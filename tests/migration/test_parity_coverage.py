from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_parity_coverage import validate_matrix  # noqa: E402

MATRIX = ROOT / "evals" / "legacy" / "parity_matrix.yaml"

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


def load_matrix() -> dict:
    return yaml.safe_load(MATRIX.read_text(encoding="utf-8"))


def test_matrix_has_all_required_domains() -> None:
    matrix = load_matrix()
    domains = {item["domain"] for item in matrix["capabilities"]}
    assert REQUIRED_DOMAINS <= domains


def test_current_matrix_has_complete_must_preserve_coverage() -> None:
    assert validate_matrix(load_matrix()) == []


def test_validator_rejects_missing_target_skill() -> None:
    matrix = deepcopy(load_matrix())
    item = next(item for item in matrix["capabilities"] if item["must_preserve"])
    item["target_skills"] = []
    issues = validate_matrix(matrix)
    assert any("target_skills" in issue for issue in issues)


def test_validator_rejects_missing_eval_case() -> None:
    matrix = deepcopy(load_matrix())
    item = next(item for item in matrix["capabilities"] if item["must_preserve"])
    item["eval_cases"] = []
    issues = validate_matrix(matrix)
    assert any("eval_cases" in issue for issue in issues)


def test_validator_rejects_duplicate_capability_ids() -> None:
    matrix = deepcopy(load_matrix())
    matrix["capabilities"].append(deepcopy(matrix["capabilities"][0]))
    issues = validate_matrix(matrix)
    assert any("duplicate capability_id" in issue for issue in issues)


def test_every_capability_has_source_evidence() -> None:
    matrix = load_matrix()
    for item in matrix["capabilities"]:
        assert item["source_file"]
        assert item["source_section"]
        assert item["regression_test_id"]
