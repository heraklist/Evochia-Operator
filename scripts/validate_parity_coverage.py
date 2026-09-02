#!/usr/bin/env python3
"""Validate the v3.2.2 → vNext legacy parity contract."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys
from typing import Any

import yaml

ALLOWED_TARGET_SKILLS = {
    "chef-ai-pro-business",
    "culinary-rnd",
    "recipe-engineering",
    "menu-experience-design",
    "kitchen-event-operations",
    "food-safety-allergens",
    "costing-commercial-intelligence",
    "supplier-procurement-intelligence",
    "evochia-company-operations",
    "evochia-brand-documents",
    "evochia-product-development",
    "evochia-market-intelligence",
}

ALLOWED_MIGRATION_STATUS = {"preserve", "upgrade", "split", "merge", "retire"}

REQUIRED_DOMAINS = {
    "culinary_answers_troubleshooting",
    "recipe_creation",
    "recipe_specification",
    "pairing_flavor_architecture",
    "substitution_reformulation",
    "menu_development",
    "storytelling_owner_style",
    "professional_kitchen_workflow",
    "scaling_holding_consistency",
    "safety_allergens",
    "ap_ep_yields",
    "supplier_normalization",
    "pricing_vat_margin",
    "what_if",
    "quote_drift",
    "exports",
    "api_invocation_approval",
}


def validate_matrix(matrix: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    capabilities = matrix.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        return ["capabilities must be a non-empty list"]

    seen: set[str] = set()
    domains: set[str] = set()
    for index, item in enumerate(capabilities):
        if not isinstance(item, dict):
            issues.append(f"capabilities[{index}] must be a mapping")
            continue
        cid = item.get("capability_id")
        label = cid or f"capabilities[{index}]"
        if not cid:
            issues.append(f"{label}: missing capability_id")
        elif cid in seen:
            issues.append(f"{label}: duplicate capability_id")
        else:
            seen.add(cid)

        domain = item.get("domain")
        if domain:
            domains.add(domain)
        else:
            issues.append(f"{label}: missing domain")

        for key in ("source_file", "source_section", "current_behavior", "regression_test_id"):
            if not item.get(key):
                issues.append(f"{label}: missing {key}")

        status = item.get("migration_status")
        if status not in ALLOWED_MIGRATION_STATUS:
            issues.append(f"{label}: invalid migration_status {status!r}")

        targets = item.get("target_skills")
        if item.get("must_preserve") and (not isinstance(targets, list) or not targets):
            issues.append(f"{label}: must_preserve requires target_skills")
        elif isinstance(targets, list):
            unknown = sorted(set(targets) - ALLOWED_TARGET_SKILLS)
            if unknown:
                issues.append(f"{label}: unknown target_skills {unknown}")

        eval_cases = item.get("eval_cases")
        if item.get("must_preserve") and (not isinstance(eval_cases, list) or not eval_cases):
            issues.append(f"{label}: must_preserve requires eval_cases")

        if item.get("must_preserve") and status == "retire":
            issues.append(f"{label}: must_preserve capability cannot be retired")

    missing_domains = sorted(REQUIRED_DOMAINS - domains)
    if missing_domains:
        issues.append(f"missing required domains: {missing_domains}")

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "matrix",
        nargs="?",
        default="evals/legacy/parity_matrix.yaml",
        help="parity matrix YAML path",
    )
    args = parser.parse_args(argv)
    path = Path(args.matrix)
    matrix = yaml.safe_load(path.read_text(encoding="utf-8"))
    issues = validate_matrix(matrix)
    if issues:
        print("Legacy parity coverage: FAIL", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print(f"Legacy parity coverage: PASS ({len(matrix['capabilities'])} capabilities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
