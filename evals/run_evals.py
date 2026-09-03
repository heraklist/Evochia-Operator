#!/usr/bin/env python3
"""Static evaluation harness for Chef AI Pro Business vNext contracts.

This runner validates the machine-readable eval inventory and cross-skill E2E
case structure. It intentionally does not pretend to execute model/tool calls;
live surface smoke tests remain a separate release gate.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import yaml

REQUIRED_CATEGORIES = {
    "legacy", "routing", "culinary", "safety", "costing", "supplier", "operations",
    "brand", "product-development", "market-intelligence", "integrations", "leakage/security",
}


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run_static_evals(root: Path) -> dict:
    issues: list[str] = []
    manifest_path = root / "evals/eval_manifest.yaml"
    e2e_path = root / "evals/e2e/e2e_cases.yaml"

    if not manifest_path.exists():
        return {"status": "FAIL", "categories": 0, "e2e_cases": 0, "issues": ["missing eval manifest"]}
    if not e2e_path.exists():
        return {"status": "FAIL", "categories": 0, "e2e_cases": 0, "issues": ["missing E2E cases"]}

    manifest = _load_yaml(manifest_path) or {}
    category_items = manifest.get("categories", [])
    names = [item.get("category") for item in category_items]
    if len(names) != len(set(names)):
        issues.append("duplicate eval category")
    missing_categories = REQUIRED_CATEGORIES - set(names)
    extra_categories = set(names) - REQUIRED_CATEGORIES
    if missing_categories:
        issues.append(f"missing categories: {sorted(missing_categories)}")
    if extra_categories:
        issues.append(f"unexpected categories: {sorted(extra_categories)}")

    for item in category_items:
        category = item.get("category", "<unknown>")
        sources = item.get("sources") or []
        if not sources:
            issues.append(f"{category}: no sources")
        for rel in sources:
            if not (root / rel).exists():
                issues.append(f"{category}: missing source {rel}")

    e2e = _load_yaml(e2e_path) or {}
    cases = e2e.get("cases", [])
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        issues.append("duplicate E2E case id")
    for case in cases:
        cid = case.get("id", "<unknown>")
        if not case.get("required_skills"):
            issues.append(f"{cid}: required_skills missing")
        if "must" not in case or "must_not" not in case:
            issues.append(f"{cid}: must/must_not contract missing")

    return {
        "status": "PASS" if not issues else "FAIL",
        "categories": len(category_items),
        "e2e_cases": len(cases),
        "issues": issues,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = run_static_evals(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
