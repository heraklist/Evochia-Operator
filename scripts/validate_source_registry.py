#!/usr/bin/env python3
"""Validate Chef AI Pro Business source authority and supersession metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
import yaml

CURRENT_CLASSES = {"canonical_policy", "canonical_current_data"}
PRICING_AUTHORITY_USES = {"current_rates", "pricing_policy", "canonical_pricing_policy"}
CURRENT_AUTHORITIES = {"current", "canonical"}


def load_registry(path: Path | str) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _schema_issues(registry: dict[str, Any], schema_path: Path | str) -> list[str]:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [f"schema: {error.message}" for error in sorted(validator.iter_errors(registry), key=lambda e: list(e.path))]


def _find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    path: list[str] = []

    def walk(node: str) -> list[str] | None:
        if node in visiting:
            start = path.index(node)
            return path[start:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        path.append(node)
        for child in graph.get(node, []):
            cycle = walk(child)
            if cycle:
                return cycle
        path.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        cycle = walk(node)
        if cycle:
            return cycle
    return None


def validate_registry(registry: dict[str, Any], schema_path: Path | str) -> list[str]:
    issues = _schema_issues(registry, schema_path)
    sources = registry.get("sources")
    if not isinstance(sources, list):
        return issues or ["sources must be a list"]

    by_id: dict[str, dict[str, Any]] = {}
    for item in sources:
        if not isinstance(item, dict):
            continue
        sid = item.get("source_id")
        if not sid:
            continue
        if sid in by_id:
            issues.append(f"duplicate source_id: {sid}")
        else:
            by_id[sid] = item

    for sid, item in by_id.items():
        source_class = item.get("source_class")
        authority = item.get("authority")
        if source_class in CURRENT_CLASSES:
            if not item.get("owner"):
                issues.append(f"{sid}: current/canonical source requires owner")
            if not item.get("last_reviewed_at"):
                issues.append(f"{sid}: current/canonical source requires last_reviewed_at")
            if not item.get("effective_date"):
                issues.append(f"{sid}: current/canonical source requires effective_date")

        allowed = set(item.get("allowed_uses") or [])
        if source_class == "golden_example" and allowed & PRICING_AUTHORITY_USES:
            issues.append(f"{sid}: golden_example cannot be pricing authority ({sorted(allowed & PRICING_AUTHORITY_USES)})")

        if source_class == "superseded":
            if authority in CURRENT_AUTHORITIES:
                issues.append(f"{sid}: superseded source cannot be marked current/canonical")
            if not item.get("superseded_by"):
                issues.append(f"{sid}: superseded source requires superseded_by")

        for ref in (item.get("supersedes") or []) + (item.get("superseded_by") or []):
            if ref not in by_id:
                issues.append(f"{sid}: supersession reference does not exist: {ref}")

        overlap = set(item.get("supersedes") or []) & set(item.get("superseded_by") or [])
        if overlap:
            issues.append(f"{sid}: source cannot both supersede and be superseded by {sorted(overlap)}")

    for sid, item in by_id.items():
        for old in item.get("supersedes") or []:
            if old in by_id and sid not in (by_id[old].get("superseded_by") or []):
                issues.append(f"{sid}: supersedes {old} but reverse superseded_by link is missing")
        for new in item.get("superseded_by") or []:
            if new in by_id and sid not in (by_id[new].get("supersedes") or []):
                issues.append(f"{sid}: superseded_by {new} but reverse supersedes link is missing")

    graph = {sid: list(item.get("supersedes") or []) for sid, item in by_id.items()}
    cycle = _find_cycle(graph)
    if cycle:
        issues.append(f"supersession cycle: {' -> '.join(cycle)}")

    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", nargs="?", default="references/source_registry.yaml")
    parser.add_argument("--schema", default="schemas/source_registry.schema.json")
    args = parser.parse_args(argv)
    registry = load_registry(args.registry)
    issues = validate_registry(registry, args.schema)
    if issues:
        print("Source registry: FAIL", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print(f"Source registry: PASS ({len(registry['sources'])} sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
