#!/usr/bin/env python3
"""Validate an Evochia Operator artifact against canonical Git source objects."""
from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path, PurePosixPath
import subprocess
import sys
from zipfile import BadZipFile, ZipFile

import yaml

try:
    from scripts.operator_support.contract_paths import extract_contract_paths
    from scripts.operator_support.contract_scope import operator_contract_paths
    from scripts.operator_support.git_source import GitSource, sha256_bytes
    from scripts.operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index
except ModuleNotFoundError:  # direct: python scripts/validate_operator_package.py
    from operator_support.contract_paths import extract_contract_paths
    from operator_support.contract_scope import operator_contract_paths
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


def _package_policy(source: GitSource, operator_policy: dict) -> dict:
    package_policy_path = operator_policy.get("source_package_policy")
    if not isinstance(package_policy_path, str) or not package_policy_path:
        raise ValueError("operator policy missing source_package_policy")
    return _load_yaml_bytes(
        source.read_bytes(package_policy_path),
        package_policy_path,
    )


def _domain_ids(package_policy: dict, operator_policy: dict) -> tuple[str, ...]:
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


def _manifest_rows(manifest: dict, issues: list[str]) -> list[dict]:
    rows = manifest.get("files", [])
    if not isinstance(rows, list):
        issues.append("manifest files must be a list")
        return []
    valid_rows: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            issues.append("manifest contains invalid file entry")
            continue
        valid_rows.append(row)
    return valid_rows


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

    for row in _manifest_rows(manifest, issues):
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


def _validate_closed_world_inventory(files: dict[str, bytes], manifest: dict, issues: list[str]) -> None:
    rows = _manifest_rows(manifest, issues)
    projected_paths = [row.get("projected_path") for row in rows if isinstance(row.get("projected_path"), str)]
    if len(projected_paths) != len(set(projected_paths)):
        issues.append("manifest contains duplicate projected_path entries")

    declared = set(projected_paths)
    actual = set(files) - {MANIFEST_PATH}
    for path in sorted(actual - declared):
        issues.append(f"artifact file absent from manifest inventory: {path}")
    for path in sorted(declared - actual):
        issues.append(f"manifest inventory file absent from artifact: {path}")


def _validate_topology(files: dict[str, bytes], domain_ids: tuple[str, ...], issues: list[str]) -> None:
    skill_paths = sorted(
        path
        for path in files
        if path == "SKILL.md" or path.endswith("/SKILL.md")
    )
    if skill_paths != ["SKILL.md"]:
        issues.append(f"operator artifact must contain exactly one root SKILL.md, found: {skill_paths}")

    expected_modules = {f"skills/{skill_id}/MODULE.md" for skill_id in domain_ids}
    actual_modules = {path for path in files if path.endswith("/MODULE.md")}
    missing = sorted(expected_modules - actual_modules)
    unexpected = sorted(actual_modules - expected_modules)
    if missing:
        issues.append(f"expected operator modules missing: {missing}")
    if unexpected:
        issues.append(f"unexpected operator modules present: {unexpected}")
    if len(actual_modules) != len(expected_modules):
        issues.append(
            f"operator module count mismatch: expected {len(expected_modules)}, found {len(actual_modules)}"
        )


def _validate_projection_paths(
    manifest: dict,
    operator_policy: dict,
    domain_ids: tuple[str, ...],
    issues: list[str],
) -> None:
    template = operator_policy.get("template")
    icon = operator_policy.get("icon") or {}
    icon_source = icon.get("source_path") if isinstance(icon, dict) else None
    icon_artifact = icon.get("artifact_path") if isinstance(icon, dict) else None

    explicit_projections: dict[str, tuple[str, str]] = {}
    if isinstance(template, str):
        explicit_projections[template] = ("SKILL.md", "TEMPLATE_EXACT_COPY")
    for skill_id in domain_ids:
        explicit_projections[f"skills/{skill_id}/SKILL.md"] = (
            f"skills/{skill_id}/MODULE.md",
            "EXACT_BYTE_COPY",
        )
    if isinstance(icon_source, str) and isinstance(icon_artifact, str):
        explicit_projections[icon_source] = (icon_artifact, "RENAMED_EXACT_BYTE_COPY")

    for row in _manifest_rows(manifest, issues):
        source_path = row.get("source_path")
        projected_path = row.get("projected_path")
        relation = row.get("relation")
        if not isinstance(source_path, str) or not source_path:
            continue
        if not isinstance(projected_path, str) or not projected_path:
            continue

        explicit = explicit_projections.get(source_path)
        if explicit is not None:
            expected_path, expected_relation = explicit
            if projected_path != expected_path or relation != expected_relation:
                issues.append(
                    f"invalid explicit projection {source_path}: expected {expected_path} ({expected_relation})"
                )
            continue

        if projected_path != source_path:
            issues.append(
                f"source-derived runtime resource moved from canonical path: {source_path} -> {projected_path}"
            )
        if relation != "EXACT_BYTE_COPY":
            issues.append(f"canonical-path source projection has unexpected relation: {projected_path}")


def _is_forbidden_path(path: str, patterns: list[str], exceptions: set[str]) -> bool:
    rel = PurePosixPath(path)
    if path in exceptions or rel.name in exceptions:
        return False
    for pattern in patterns:
        if not isinstance(pattern, str):
            continue
        if pattern.startswith("*."):
            if fnmatch.fnmatch(rel.name, pattern):
                return True
        elif pattern in rel.parts or rel.name == pattern:
            return True
    return False


def _validate_package_restrictions(files: dict[str, bytes], package_policy: dict, issues: list[str]) -> None:
    patterns = package_policy.get("forbidden_patterns", [])
    if not isinstance(patterns, list):
        patterns = []
    exceptions_raw = package_policy.get("allowed_exception_files", [])
    exceptions = set(exceptions_raw) if isinstance(exceptions_raw, list) else set()

    for path in sorted(files):
        if _is_forbidden_path(path, patterns, exceptions):
            issues.append(f"forbidden package file: {path}")

    if package_policy.get("font_binaries_in_package") is False:
        for path in sorted(files):
            if PurePosixPath(path).suffix.lower() in {".ttf", ".otf", ".woff", ".woff2"}:
                issues.append(f"font binary in operator package: {path}")

    if package_policy.get("backend_source_in_package") is False:
        for path in sorted(files):
            if path == "backend" or path.startswith("backend/"):
                issues.append(f"backend source in operator package: {path}")


def _artifact_resolves_path(files: dict[str, bytes], ref: str) -> bool:
    if ref in files:
        return True
    prefix = ref.rstrip("/") + "/"
    return any(path.startswith(prefix) for path in files)


def _validate_exact_contract_paths(files: dict[str, bytes], issues: list[str]) -> None:
    for contract_path in operator_contract_paths(files):
        try:
            text = files[contract_path].decode("utf-8")
        except UnicodeDecodeError:
            issues.append(f"contract is not UTF-8: {contract_path}")
            continue
        for ref in extract_contract_paths(text):
            if not _artifact_resolves_path(files, ref):
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
        package_policy = _package_policy(source, operator_policy)
        domain_ids = _domain_ids(package_policy, operator_policy)
    except (subprocess.CalledProcessError, UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
        return [f"canonical operator policy unavailable: {exc}"]

    manifest = _validate_manifest(files, source, issues)
    if manifest:
        _validate_closed_world_inventory(files, manifest, issues)
        _validate_projection_paths(manifest, operator_policy, domain_ids, issues)

    _validate_topology(files, domain_ids, issues)
    _validate_package_restrictions(files, package_policy, issues)

    expected_template = source.read_bytes(operator_policy["template"])
    if files.get("SKILL.md") != expected_template:
        issues.append("operator root SKILL.md differs from canonical template")
    if manifest and manifest.get("root_template_sha256") != sha256_bytes(expected_template):
        issues.append("manifest root_template_sha256 differs from canonical source template")

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
