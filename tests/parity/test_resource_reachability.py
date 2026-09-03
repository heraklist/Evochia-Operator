from pathlib import Path
import importlib.util
import yaml

ROOT = Path(__file__).resolve().parents[2]
PARITY = ROOT / "evals/legacy/parity_matrix.yaml"
COSTING_SKILL = ROOT / "skills/costing-commercial-intelligence/SKILL.md"
VALIDATOR = ROOT / "scripts/validate_parity_coverage.py"
EXPORT_DOCTRINE = "references/exports/excel_sheets_export_spec_v2_4.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_parity_coverage", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_excel_export_capabilities_are_reachable_from_target_skill():
    text = COSTING_SKILL.read_text(encoding="utf-8")
    assert EXPORT_DOCTRINE in text
    assert "Excel" in text or "workbook" in text.lower()


def test_parity_validator_checks_declared_required_resources_against_target_skills():
    matrix = yaml.safe_load(PARITY.read_text(encoding="utf-8"))
    by_id = {item["capability_id"]: item for item in matrix["capabilities"]}

    for capability_id in ["excel_workbook_structure", "excel_formula_patterns"]:
        item = by_id[capability_id]
        assert item["required_resources"] == [EXPORT_DOCTRINE]
        assert "costing-commercial-intelligence" in item["target_skills"]

    validator = load_validator()
    issues = validator.validate_matrix(matrix, repo_root=ROOT)
    assert issues == []


def test_parity_validator_fails_when_required_resource_is_not_reachable_from_any_target_skill(tmp_path):
    matrix = yaml.safe_load(PARITY.read_text(encoding="utf-8"))
    item = next(x for x in matrix["capabilities"] if x["capability_id"] == "excel_workbook_structure")
    item["required_resources"] = ["references/exports/nonexistent-export-doctrine.md"]

    validator = load_validator()
    issues = validator.validate_matrix(matrix, repo_root=ROOT)
    assert any("excel_workbook_structure" in issue and "required resource" in issue for issue in issues)
