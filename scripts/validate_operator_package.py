#!/usr/bin/env python3
"""Validate an Evochia Operator artifact against canonical Git source objects."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from zipfile import BadZipFile, ZipFile

import yaml

try:
    from scripts.operator_support.contract_paths import extract_contract_paths
    from scripts.operator_support.git_source import GitSource, sha256_bytes
    from scripts.operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index
except ModuleNotFoundError:  # direct: python scripts/validate_operator_package.py
    from operator_support.contract_paths import extract_contract_paths
    from operator_support.git_source import GitSource, sha256_bytes
    from operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index


MANIFEST_PATH = "provenance/build_manifest.yaml"


def _load_yaml_bytes(data: bytes, label: str) -> dict:
    loaded = yaml.safe_load(data.decode("utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"{label} must be a mapping")
    return loaded


def _zip_files(path: Path) -> dict[str, bytes]:
    with ZipFile(path) as archive:
        return {
            name: archive.read(name)
            for name in archive.namelist()
            if name and not name.endswith("/")
        }


def _domain_ids(source: GitSource, operator_policy: dict) -> tuple[str, ...]:
    package_policy_path = operator_policy.get("source_package_policy")
    if not isinstance(package_policy_path, str) or not package_policy_path:
        raise ValueError("operator policy missing source_package_policy")
    package_policy = _load_yaml_bytes(
        source.read_bytes(package_policy_path),
        package_policy_path,
    )
    required = package_policy.get("required_skills", [])
    orchestrator = operator_policy.get("orchestrator_skill")
    if not isinstance(required, list) or not isinstance(orchestrator, str):
        raise ValueError("invalid canonical skill policy")
    return tuple(skill for skill in required if isinstance(skill, str) and skill != orchestrator)


def _expected_module_index(source: GitSource, domain_ids: tuple[str, ...]) -> bytes:
    descriptors: list[ModuleDescriptor] = []
    for skill_id in domain_ids:
        meta = parse_frontmatter(source.read_bytes(f"skills/{skill_id}/SKILL.md"))
        descriptors.append(ModuleDescriptor(meta["name"], meta["description"]))
    return render_module_index(descriptors)


def _validate_manifest(files: dict[str, bytes], source: GitSource, issues: list[str]) -> dict:
    raw = files.get(MANIFEST_PATH)
    if raw is None:
        issues.append(f"missing {MANIFEST_PATH}")
        return {}
    try:
        manifest = _load_yaml_bytes(raw, MANIFEST_PATH)
    except (UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
        issues.append(f"invalid {MANIFEST_PATH}: {exc}")
        return {}

    if manifest.get("source_commit") != source.full_commit():
        issues.append("manifest source_commit does not match requested source commit")
    if manifest.get("target") != "operator":
        issues.append("manifest target is not operator")

    try:
        expected_version = source.read_bytes("VERSION").decode("utf-8").strip()
    except UnicodeDecodeError:
        expected_version = ""
    if manifest.get("source_version") != expected_version:
        issues.append("manifest source_version differs from Git source VERSION")

    for row in manifest.get("files", []):
        if not isinstance(row, dict):
            issues.append("manifest contains invalid file entry")
            continue
        projected_path = row.get("projected_path")
        if not isinstance(projected_path, str) or not projected_path:
            issues.append("manifest file entry missing projected_path")
            continue
        projected = files.get(projected_path)
        if projected is None:
            issues.append(f"manifest projected file missing: {projected_path}")
            continue
        if row.get("projected_sha256") != sha256_bytes(projected):
            issues.append(f"manifest projected hash mismatch: {projected_path}")

        source_path = row.get("source_path")
        if isinstance(source_path, str) and source_path:
            try:
                source_bytes = source.read_bytes(source_path)
            except subprocess.CalledProcessError:
                issues.append(f"manifest source path unavailable: {source_path}")
                continue
            if row.get("source_sha256") != sha256_bytes(source_bytes):
                issues.append(f"manifest source hash differs from Git source: {projected_path}")
            if row.get("relation") in {
                "EXACT_BYTE_COPY",
                "TEMPLATE_EXACT_COPY",
                "RENAMED_EXACT_BYTE_COPY",
            } and projected != source_bytes:
                issues.append(f"Git source bytes differ: {projected_path}")

    builder = manifest.get("builder") or {}
    if isinstance(builder, dict):
        builder_path = builder.get("path")
        if isinstance(builder_path, str) and builder_path:
            try:
                source_builder = source.read_bytes(builder_path)
            except subprocess.CalledProcessError:
                issues.append(f"builder source unavailable: {builder_path}")
            else:
                expected = sha256_bytes(source_builder)
                if builder.get("source_commit_sha256") != expected:
                    issues.append("builder source_commit_sha256 differs from Git source")
                if builder.get("runtime_sha256") != expected:
                    issues.append("builder runtime_sha256 differs from committed builder")

    return manifest


def _validate_exact_contract_paths(files: dict[str, bytes], issues: list[str]) -> None:
    scan_paths = [
        path
        for path in files
        if path == "SKILL.md"
        or path.endswith("/MODULE.md")
        or (path.startswith("references/") and path.endswith(".md"))
    ]
    for contract_path in sorted(scan_paths):
        try:
            text = files[contract_path].decode("utf-8")
        except UnicodeDecodeError:
            issues.append(f"contract is not UTF-8: {contract_path}")
            continue
        for ref in extract_contract_paths(text):
            # Icon source paths are validated by source blob identity and projected bytes,
            # not by artifact path resolution. They are not behavioral contract paths.
            if ref not in files:
                issues.append(f"broken referenced path {ref}")


def validate_operator_artifact(
    artifact: Path | str,
    source_repo: Path | str,
    source_commit: str,
) -> list[str]:
    issues: list[str] = []
    source = GitSource(source_repo, source_commit)

    try:
        full_commit = source.full_commit()
    except subprocess.CalledProcessError:
        return [f"source commit unavailable: {source_commit}"]

    source = GitSource(source_repo, full_commit)

    try:
        files = _zip_files(Path(artifact))
    except (OSError, BadZipFile) as exc:
        return [f"artifact unavailable or invalid ZIP: {exc}"]

    try:
        operator_policy = _load_yaml_bytes(
            source.read_bytes("release/operator/package_policy.yaml"),
            "release/operator/package_policy.yaml",
        )
        domain_ids = _domain_ids(source, operator_policy)
    except (subprocess.CalledProcessError, UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
        return [f"canonical operator policy unavailable: {exc}"]

    manifest = _validate_manifest(files, source, issues)

    expected_template = source.read_bytes(operator_policy["template"])
    if files.get("SKILL.md") != expected_template:
        issues.append("operator root SKILL.md differs from canonical template")

    routing_path = operator_policy["routing"]
    if files.get(routing_path) != source.read_bytes(routing_path):
        issues.append(f"Git source bytes differ: {routing_path}")

    for skill_id in domain_ids:
        projected_path = f"skills/{skill_id}/MODULE.md"
        source_path = f"skills/{skill_id}/SKILL.md"
        if files.get(projected_path) != source.read_bytes(source_path):
            issues.append(f"Git source bytes differ: {projected_path}")

    index_path = operator_policy["module_index_path"]
    expected_index = _expected_module_index(source, domain_ids)
    if files.get(index_path) != expected_index:
        issues.append("generated module index differs from canonical source frontmatter")
    if manifest:
        module_index = manifest.get("module_index") or {}
        if isinstance(module_index, dict):
            if module_index.get("sha256") != sha256_bytes(expected_index):
                issues.append("manifest module index hash differs from canonical source frontmatter")

    icon = operator_policy.get("icon") or {}
    if isinstance(icon, dict):
        source_path = icon.get("source_path")
        artifact_path = icon.get("artifact_path")
        expected_blob = icon.get("expected_git_blob")
        if isinstance(source_path, str) and isinstance(artifact_path, str):
            source_entries = {entry.path: entry for entry in source.entries(source_path)}
            entry = source_entries.get(source_path)
            if entry is None:
                issues.append(f"icon source unavailable: {source_path}")
            else:
                if isinstance(expected_blob, str) and entry.blob_sha != expected_blob:
                    issues.append("icon Git blob differs from operator policy pin")
                source_icon = source.read_bytes(source_path)
                if files.get(artifact_path) != source_icon:
                    issues.append("operator icon bytes differ from verified Git source blob")

    _validate_exact_contract_paths(files, issues)

    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args(argv)

    issues = validate_operator_artifact(
        artifact=Path(args.artifact),
        source_repo=Path(args.source_repo),
        source_commit=args.source_commit,
    )
    if issues:
        print("Operator package validation: FAIL", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1

    print("Operator package validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
