#!/usr/bin/env python3
"""Build deterministic Chef AI package artifacts from committed Git objects."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable

import yaml

try:
    from scripts.operator_support.contract_paths import extract_contract_paths
    from scripts.operator_support.deterministic_zip import ArchiveEntry, write_deterministic_zip
    from scripts.operator_support.git_source import GitEntry, GitSource, sha256_bytes
    from scripts.operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index
except ModuleNotFoundError:  # direct: python scripts/build_skill_package.py
    from operator_support.contract_paths import extract_contract_paths
    from operator_support.deterministic_zip import ArchiveEntry, write_deterministic_zip
    from operator_support.git_source import GitEntry, GitSource, sha256_bytes
    from operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index


BUILDER_PATH = "scripts/build_skill_package.py"
MANIFEST_RELATION_GENERATED = "GENERATED_FRONTMATTER_INDEX"


@dataclass(frozen=True)
class BuildResult:
    artifact_path: Path
    sha256: str
    source_commit: str
    source_version: str
    target: str


@dataclass(frozen=True)
class Projection:
    projected_path: str
    data: bytes
    mode: int
    relation: str
    source_path: str | None = None
    source_sha256: str | None = None


def _yaml_mapping(data: bytes, label: str) -> dict:
    loaded = yaml.safe_load(data.decode("utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"{label} must be a mapping")
    return loaded


def _entry_map(source: GitSource) -> dict[str, GitEntry]:
    return {entry.path: entry for entry in source.entries()}


def _add_source_projection(
    projections: dict[str, Projection],
    source: GitSource,
    entries: dict[str, GitEntry],
    *,
    source_path: str,
    projected_path: str | None = None,
    relation: str = "EXACT_BYTE_COPY",
) -> None:
    projected_path = projected_path or source_path
    entry = entries.get(source_path)
    if entry is None:
        raise ValueError(f"missing source path: {source_path}")
    data = source.read_bytes(source_path)
    candidate = Projection(
        projected_path=projected_path,
        data=data,
        mode=entry.mode,
        relation=relation,
        source_path=source_path,
        source_sha256=sha256_bytes(data),
    )
    existing = projections.get(projected_path)
    if existing is not None and existing != candidate:
        raise ValueError(f"conflicting projection: {projected_path}")
    projections[projected_path] = candidate


def _add_source_tree(
    projections: dict[str, Projection],
    source: GitSource,
    entries: dict[str, GitEntry],
    prefix: str,
    *,
    skip_paths: set[str] | None = None,
) -> None:
    skip_paths = skip_paths or set()
    normalized = prefix.rstrip("/") + "/"
    matches = [entry for entry in entries.values() if entry.path.startswith(normalized)]
    if not matches:
        raise ValueError(f"missing source directory: {prefix.rstrip('/')}")
    for entry in sorted(matches, key=lambda item: item.path):
        if entry.path in skip_paths:
            continue
        _add_source_projection(
            projections,
            source,
            entries,
            source_path=entry.path,
        )


def _resolve_runtime_reference(
    ref: str,
    *,
    projections: dict[str, Projection],
    source: GitSource,
    entries: dict[str, GitEntry],
    excluded_source_paths: set[str],
) -> tuple[str, ...]:
    """Materialize one exact backticked runtime path from committed Git objects.

    The extractor intentionally normalizes a trailing slash away. Exact blobs win;
    otherwise the path is treated as a directory root and all committed blobs below
    that prefix are included. Paths already materialized/generated require no source
    lookup. non_runtime_tooling and the remapped icon source remain excluded.
    """
    if ref in projections:
        return ()
    if ref in excluded_source_paths:
        return ()

    if ref in entries:
        _add_source_projection(projections, source, entries, source_path=ref)
        return (ref,)

    prefix = ref.rstrip("/") + "/"
    matches = tuple(
        entry.path
        for entry in sorted(entries.values(), key=lambda item: item.path)
        if entry.path.startswith(prefix) and entry.path not in excluded_source_paths
    )
    if not matches:
        raise ValueError(f"missing referenced runtime path: {ref}")
    for source_path in matches:
        _add_source_projection(projections, source, entries, source_path=source_path)
    return matches


def _expand_markdown_closure(
    projections: dict[str, Projection],
    *,
    source: GitSource,
    entries: dict[str, GitEntry],
    excluded_source_paths: set[str],
) -> None:
    """Follow backticked repository paths to a fixed point with cycle detection."""
    scanned_paths: set[str] = set()
    visited_refs: set[str] = set()

    while True:
        pending = [
            projection
            for path, projection in sorted(projections.items())
            if path not in scanned_paths
            and (path == "SKILL.md" or path.endswith("/MODULE.md") or path.endswith(".md"))
        ]
        if not pending:
            return

        for projection in pending:
            scanned_paths.add(projection.projected_path)
            try:
                text = projection.data.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(f"runtime Markdown is not UTF-8: {projection.projected_path}") from exc

            for ref in extract_contract_paths(text):
                if ref in visited_refs:
                    continue
                visited_refs.add(ref)
                _resolve_runtime_reference(
                    ref,
                    projections=projections,
                    source=source,
                    entries=entries,
                    excluded_source_paths=excluded_source_paths,
                )


def _manifest_row(projection: Projection) -> dict:
    return {
        "projected_path": projection.projected_path,
        "relation": projection.relation,
        "source_path": projection.source_path,
        "source_sha256": projection.source_sha256,
        "projected_sha256": sha256_bytes(projection.data),
    }


def _build_multi(source: GitSource, output_dir: Path) -> BuildResult:
    full_commit = source.full_commit()
    source = GitSource(source.repo, full_commit)
    version = source.read_bytes("VERSION").decode("utf-8").strip()

    entries = tuple(
        ArchiveEntry(
            path=entry.path,
            data=source.read_bytes(entry.path),
            mode=entry.mode,
        )
        for entry in source.entries()
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / f"chef-ai-pro-business-{version}-{full_commit[:7]}-multi.zip"
    digest = write_deterministic_zip(artifact, entries)
    return BuildResult(
        artifact_path=artifact,
        sha256=digest,
        source_commit=full_commit,
        source_version=version,
        target="multi",
    )


def _build_operator(source: GitSource, output_dir: Path) -> BuildResult:
    full_commit = source.full_commit()
    source = GitSource(source.repo, full_commit)
    entries = _entry_map(source)
    version = source.read_bytes("VERSION").decode("utf-8").strip()

    package_policy = _yaml_mapping(
        source.read_bytes("release/package_policy.yaml"),
        "release/package_policy.yaml",
    )
    operator_policy = _yaml_mapping(
        source.read_bytes("release/operator/package_policy.yaml"),
        "release/operator/package_policy.yaml",
    )
    ownership = _yaml_mapping(
        source.read_bytes("release/runtime_resource_ownership.yaml"),
        "release/runtime_resource_ownership.yaml",
    )

    orchestrator = operator_policy.get("orchestrator_skill")
    required_skills = package_policy.get("required_skills")
    if not isinstance(orchestrator, str) or not isinstance(required_skills, list):
        raise ValueError("invalid canonical skill policy")
    domains = tuple(
        skill
        for skill in required_skills
        if isinstance(skill, str) and skill != orchestrator
    )
    if len(domains) != 11 or len(set(domains)) != 11:
        raise ValueError(f"operator requires exactly 11 unique domain skills, got {len(domains)}")

    icon = operator_policy.get("icon") or {}
    if not isinstance(icon, dict):
        raise ValueError("invalid operator icon policy")
    icon_source = icon.get("source_path")
    icon_artifact = icon.get("artifact_path")
    expected_icon_blob = icon.get("expected_git_blob")
    if not all(isinstance(value, str) and value for value in (icon_source, icon_artifact, expected_icon_blob)):
        raise ValueError("incomplete operator icon policy")
    icon_entry = entries.get(icon_source)
    if icon_entry is None or icon_entry.blob_sha != expected_icon_blob:
        raise ValueError("operator icon Git blob differs from policy pin")

    excluded_source_paths = {
        path.rstrip("/")
        for path in ownership.get("non_runtime_tooling", [])
        if isinstance(path, str) and path
    }
    excluded_source_paths.add(icon_source)

    projections: dict[str, Projection] = {}

    template_path = operator_policy.get("template")
    routing_path = operator_policy.get("routing")
    module_index_path = operator_policy.get("module_index_path")
    if not all(isinstance(value, str) and value for value in (template_path, routing_path, module_index_path)):
        raise ValueError("incomplete operator projection policy")

    _add_source_projection(
        projections,
        source,
        entries,
        source_path=template_path,
        projected_path="SKILL.md",
        relation="TEMPLATE_EXACT_COPY",
    )
    _add_source_projection(projections, source, entries, source_path="VERSION")

    # Entire canonical references subtree is an exact runtime projection.
    _add_source_tree(
        projections,
        source,
        entries,
        "references/",
        skip_paths=excluded_source_paths,
    )

    # Each domain remains a governed source Skill, projected as MODULE.md with all
    # skill-local resources preserved at their canonical repository paths.
    descriptors: list[ModuleDescriptor] = []
    for skill_id in domains:
        skill_source = f"skills/{skill_id}/SKILL.md"
        skill_projected = f"skills/{skill_id}/MODULE.md"
        _add_source_projection(
            projections,
            source,
            entries,
            source_path=skill_source,
            projected_path=skill_projected,
        )
        meta = parse_frontmatter(source.read_bytes(skill_source))
        if meta["name"] != skill_id:
            raise ValueError(f"domain frontmatter name mismatch: {skill_id}")
        descriptors.append(ModuleDescriptor(meta["name"], meta["description"]))

        prefix = f"skills/{skill_id}/"
        for entry in sorted(entries.values(), key=lambda item: item.path):
            if entry.path.startswith(prefix) and entry.path != skill_source:
                _add_source_projection(
                    projections,
                    source,
                    entries,
                    source_path=entry.path,
                )

    # The nested orchestrator contributes only the canonical routing contract.
    _add_source_projection(projections, source, entries, source_path=routing_path)

    module_index = render_module_index(descriptors)
    projections[module_index_path] = Projection(
        projected_path=module_index_path,
        data=module_index,
        mode=0o100644,
        relation=MANIFEST_RELATION_GENERATED,
    )

    # Explicit runtime ownership is a seed, not a second registry. non_runtime_tooling
    # is deliberately omitted from the artifact.
    for item in ownership.get("resource_roots", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ValueError("invalid runtime resource root declaration")
        root = item["path"].rstrip("/")
        _add_source_tree(
            projections,
            source,
            entries,
            root + "/",
            skip_paths=excluded_source_paths,
        )

    for item in ownership.get("exact_resources", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ValueError("invalid exact runtime resource declaration")
        path = item["path"].rstrip("/")
        if path in excluded_source_paths:
            raise ValueError(f"runtime resource conflicts with non-runtime exclusion: {path}")
        _add_source_projection(projections, source, entries, source_path=path)

    # Contract references are resolved strictly from committed Git objects to a
    # fixed point. This is intentionally backtick-only, matching contract_paths.py.
    _expand_markdown_closure(
        projections,
        source=source,
        entries=entries,
        excluded_source_paths=excluded_source_paths,
    )

    # The brand mark is the sole explicit source-path remap.
    _add_source_projection(
        projections,
        source,
        entries,
        source_path=icon_source,
        projected_path=icon_artifact,
        relation="RENAMED_EXACT_BYTE_COPY",
    )

    runtime_builder = Path(__file__).resolve().read_bytes()
    source_builder = source.read_bytes(BUILDER_PATH)
    manifest = {
        "schema_version": 1,
        "source_commit": full_commit,
        "source_version": version,
        "target": "operator",
        "builder": {
            "path": BUILDER_PATH,
            "runtime_sha256": sha256_bytes(runtime_builder),
            "source_commit_sha256": sha256_bytes(source_builder),
        },
        "root_template_sha256": sha256_bytes(source.read_bytes(template_path)),
        "module_index": {
            "path": module_index_path,
            "generation_method": "frontmatter-name-description-v1",
            "sha256": sha256_bytes(module_index),
        },
        "files": [
            _manifest_row(projections[path])
            for path in sorted(projections)
        ],
    }
    manifest_path = operator_policy.get("provenance_manifest_path")
    if not isinstance(manifest_path, str) or not manifest_path:
        raise ValueError("missing provenance manifest path")
    manifest_bytes = yaml.safe_dump(
        manifest,
        sort_keys=True,
        allow_unicode=True,
    ).encode("utf-8")

    archive_entries: list[ArchiveEntry] = [
        ArchiveEntry(
            path=projection.projected_path,
            data=projection.data,
            mode=projection.mode,
        )
        for projection in projections.values()
    ]
    archive_entries.append(
        ArchiveEntry(
            path=manifest_path,
            data=manifest_bytes,
            mode=0o100644,
        )
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / f"evochia-operator-{version}-{full_commit[:7]}-operator.zip"
    digest = write_deterministic_zip(artifact, archive_entries)
    return BuildResult(
        artifact_path=artifact,
        sha256=digest,
        source_commit=full_commit,
        source_version=version,
        target="operator",
    )


def build_package(
    *,
    target: str,
    source_repo: Path | str,
    source_commit: str,
    output_dir: Path | str,
) -> BuildResult:
    source = GitSource(source_repo, source_commit)
    destination = Path(output_dir)
    if target == "multi":
        return _build_multi(source, destination)
    if target == "operator":
        return _build_operator(source, destination)
    raise ValueError(f"unsupported build target: {target}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=("multi", "operator"))
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)

    try:
        result = build_package(
            target=args.target,
            source_repo=Path(args.source_repo),
            source_commit=args.source_commit,
            output_dir=Path(args.output_dir),
        )
    except Exception as exc:
        print(f"Package build: FAIL\n- {exc}", file=sys.stderr)
        return 1

    print(f"Package build: PASS\n{result.artifact_path}\nSHA256 {result.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
