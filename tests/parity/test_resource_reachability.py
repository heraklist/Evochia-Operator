from pathlib import Path
import importlib.util
import yaml

ROOT = Path(__file__).resolve().parents[2]
PARITY = ROOT / "evals/legacy/parity_matrix.yaml"
REACHABILITY = ROOT / "evals/legacy/resource_reachability.yaml"
COSTING_SKILL = ROOT / "skills/costing-commercial-intelligence/SKILL.md"
VALIDATOR = ROOT / "scripts/validate_parity_coverage.py"
EXPORT_DOCTRINE = "references/exports/excel_sheets_export_spec_v2_4.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_parity_coverage", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_contracts():
    matrix = yaml.safe_load(PARITY.read_text(encoding="utf-8"))
    reachability = yaml.safe_load(REACHABILITY.read_text(encoding="utf-8"))
    return matrix, reachability


def test_excel_export_capabilities_are_reachable_from_target_skill():
    text = COSTING_SKILL.read_text(encoding="utf-8")
    assert EXPORT_DOCTRINE in text
    assert "Excel" in text or "workbook" in text.lower()


def test_reachability_manifest_binds_excel_capabilities_to_export_doctrine():
    matrix, reachability = load_contracts()
    by_id = {item["capability_id"]: item for item in matrix["capabilities"]}
    requirements = {item["capability_id"]: item for item in reachability["requirements"]}

    for capability_id in ["excel_workbook_structure", "excel_formula_patterns"]:
        item = requirements[capability_id]
        assert item["required_resources"] == [EXPORT_DOCTRINE]
        assert item["reachable_via_skills"] == ["costing-commercial-intelligence"]
        assert "costing-commercial-intelligence" in by_id[capability_id]["target_skills"]


def test_parity_validator_checks_capability_skill_resource_reachability():
    matrix, reachability = load_contracts()
    validator = load_validator()
    issues = validator.validate_matrix(matrix, repo_root=ROOT, reachability=reachability)
    assert issues == []


def test_parity_validator_fails_when_required_resource_is_not_reachable():
    matrix, reachability = load_contracts()
    reachability["requirements"][0]["required_resources"] = [
        "references/exports/nonexistent-export-doctrine.md"
    ]

    validator = load_validator()
    issues = validator.validate_matrix(matrix, repo_root=ROOT, reachability=reachability)
    assert any(
        "excel_workbook_structure" in issue and "required resource" in issue
        for issue in issues
    )
