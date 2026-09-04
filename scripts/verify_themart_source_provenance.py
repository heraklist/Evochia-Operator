#!/usr/bin/env python3
"""Fail closed unless migrated The Mart files match their provenance manifest."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys

import yaml


ALLOWED_MODES = {"EXACT_BYTE_COPY", "DERIVED_NORMALIZED_COPY"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_relative(value: object, label: str, issues: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        issues.append(f"{label}: missing relative path")
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        issues.append(f"{label}: path must be repository-relative")
        return None
    return path


def validate(root: Path | str) -> list[str]:
    root_path = Path(root).resolve()
    provider = root_path / "scripts/supplier-providers/themart"
    provenance_path = provider / "source_provenance.yaml"
    migration_path = provider / "migration_manifest.yaml"
    issues: list[str] = []

    if not provenance_path.is_file():
        return ["missing scripts/supplier-providers/themart/source_provenance.yaml"]
    if not migration_path.is_file():
        return ["missing scripts/supplier-providers/themart/migration_manifest.yaml"]

    provenance = yaml.safe_load(provenance_path.read_text(encoding="utf-8")) or {}
    migration = yaml.safe_load(migration_path.read_text(encoding="utf-8")) or {}
    records = provenance.get("files")
    if not isinstance(records, list) or not records:
        return ["source_provenance.yaml: files must be a non-empty list"]

    allowlist = migration.get("safe_source_allowlist")
    if not isinstance(allowlist, list) or not allowlist:
        issues.append("migration_manifest.yaml: safe_source_allowlist must be a non-empty list")
        allowlist = []

    seen_originals: set[str] = set()
    seen_destinations: set[str] = set()

    for index, record in enumerate(records):
        label = f"files[{index}]"
        if not isinstance(record, dict):
            issues.append(f"{label}: record must be a mapping")
            continue

        original = _safe_relative(record.get("original_relative_path"), f"{label}.original_relative_path", issues)
        destination = _safe_relative(record.get("repository_destination"), f"{label}.repository_destination", issues)
        original_name = original.as_posix() if original else None
        destination_name = destination.as_posix() if destination else None

        if original_name:
            if original_name in seen_originals:
                issues.append(f"{label}: duplicate original path {original_name}")
            seen_originals.add(original_name)
        if destination_name:
            if destination_name in seen_destinations:
                issues.append(f"{label}: duplicate repository destination {destination_name}")
            seen_destinations.add(destination_name)

        mode = record.get("migration_mode")
        if mode not in ALLOWED_MODES:
            issues.append(f"{label}: invalid migration mode {mode!r}")

        original_sha = record.get("original_sha256")
        migrated_sha = record.get("migrated_sha256")
        if not isinstance(original_sha, str) or not SHA256_RE.fullmatch(original_sha):
            issues.append(f"{label}: invalid original SHA-256")
        if not isinstance(migrated_sha, str) or not SHA256_RE.fullmatch(migrated_sha):
            issues.append(f"{label}: invalid migrated SHA-256")

        for field in ("original_byte_length", "migrated_byte_length"):
            value = record.get(field)
            if not isinstance(value, int) or value < 0:
                issues.append(f"{label}: {field} must be a non-negative integer")

        if destination:
            absolute = (root_path / destination).resolve()
            try:
                absolute.relative_to(root_path)
            except ValueError:
                issues.append(f"{label}: destination resolves outside repository")
            else:
                if not absolute.is_file():
                    issues.append(f"{label}: migrated destination is missing")
                else:
                    actual_length = absolute.stat().st_size
                    actual_sha = _sha256(absolute)
                    if actual_length != record.get("migrated_byte_length"):
                        issues.append(f"{label}: migrated byte length does not match repository bytes")
                    if actual_sha != migrated_sha:
                        issues.append(f"{label}: migrated SHA-256 does not match repository bytes")

        if mode == "EXACT_BYTE_COPY" and original_sha != migrated_sha:
            issues.append(f"{label}: exact copy original and migrated SHA-256 differ")
        if mode == "DERIVED_NORMALIZED_COPY":
            if original_sha == migrated_sha:
                issues.append(f"{label}: derived copy must not be byte-identical")
            rationale = record.get("derivation_rationale")
            if not isinstance(rationale, list) or not rationale or not all(isinstance(item, str) and item for item in rationale):
                issues.append(f"{label}: derived copy requires explicit derivation rationale")

    if set(allowlist) != seen_originals:
        missing = sorted(set(allowlist) - seen_originals)
        extra = sorted(seen_originals - set(allowlist))
        if missing:
            issues.append(f"provenance manifest missing allowlisted originals: {', '.join(missing)}")
        if extra:
            issues.append(f"provenance manifest contains non-allowlisted originals: {', '.join(extra)}")

    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    issues = validate(args.repo_root)
    if issues:
        print("The Mart source provenance: FAIL", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("The Mart source provenance: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
