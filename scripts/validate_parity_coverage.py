#!/usr/bin/env python3
"""Validate the v3.2.2 → vNext legacy parity contract and required runtime reachability."""

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

DEFAULT_MATRIX = "evals/legacy/parity_matrix.yaml"
DEFAULT_REACHABILITY = "evals/legacy/resource_reachability.yaml"


def _validate_reachability(
    matrix: dict[str, Any],
    reachability: dict[str, Any] | None,
    repo_root: Path,
) -> list[str]:
    if not reachability:
        return []

    issues: list[str] = []
    capabilities = {
        item.get("capability_id"): item
        for item in matrix.get("capabilities", [])
        if isinstance(item, dict) and item.get("capability_id")
    }

    seen: set[str] = set()
    for index, requirement in enumerate(reachability.get("requirements", [])):
        if not isinstance(requirement, dict):
            issues.append(f"reachability[{index}] must be a mapping")
            continue

        cid = requirement.get("capability_id")
        label = cid or f"reachability[{index}]"
        if not cid:
            issues.append(f"{label}: missing capability_id")
            continue
        if cid in seen:
            issues.append(f"{label}: duplicate reachability declaration")
        seen.add(cid)

        capability = capabilities.get(cid)
        if capability is None:
            issues.append(f"{label}: reachability capability not present in parity matrix")
            continue

        resources = requirement.get("required_resources")
        skills = requirement.get("reachable_via_skills")
        if not isinstance(resources, list) or not resources:
            issues.append(f"{label}: required_resources must be a non-empty list")
            continue
        if not isinstance(skills, list) or not skills:
            issues.append(f"{label}: reachable_via_skills must be a non-empty list")
            continue

        target_skills = set(capability.get("target_skills") or [])
        undeclared = sorted(set(skills) - target_skills)
        if undeclared:
            issues.append(f"{label}: reachability skills not declared as target_skills {undeclared}")

        skill_texts: dict[str, str] = {}
        for skill in skills:
            skill_file = repo_root / "skills" / skill / "SKILL.md"
            if not skill_file.exists():
                issues.append(f"{label}: target skill file missing {skill_file.relative_to(repo_root)}")
                continue
            skill_texts[skill] = skill_file.read_text(encoding="utf-8")

        for resource in resources:
            resource_path = repo_root / resource
            if not resource_path.exists():
                issues.append(f"{label}: required resource missing {resource}")
                continue
            if not any(resource in text for text in skill_texts.values()):
                issues.append(
                    f"{label}: required resource {resource} is not reachable from declared target skills"
                )

    return issues


def validate_matrix(
    matrix: dict[str, Any],
    repo_root: Path | None = None,
    reachability: dict[str, Any] | None = None,
) -> list[str]:
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

    if repo_root is not None:
        issues.extend(_validate_reachability(matrix, reachability, Path(repo_root)))

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="repository root (preferred) or explicit parity matrix YAML path",
    )
    parser.add_argument("--reachability", default=DEFAULT_REACHABILITY)
    args = parser.parse_args(argv)

    supplied = Path(args.path)
    if supplied.is_dir():
        repo_root = supplied.resolve()
        matrix_path = repo_root / DEFAULT_MATRIX
    else:
        matrix_path = supplied.resolve()
        repo_root = Path.cwd().resolve()

    reachability_path = Path(args.reachability)
    if not reachability_path.is_absolute():
        reachability_path = repo_root / reachability_path

    matrix = yaml.safe_load(matrix_path.read_text(encoding="utf-8"))
    reachability = (
        yaml.safe_load(reachability_path.read_text(encoding="utf-8"))
        if reachability_path.exists()
        else None
    )
    issues = validate_matrix(matrix, repo_root=repo_root, reachability=reachability)
    if issues:
        print("Legacy parity coverage: FAIL", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print(f"Legacy parity coverage: PASS ({len(matrix['capabilities'])} capabilities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
