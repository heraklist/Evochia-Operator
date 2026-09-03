from pathlib import Path
import importlib.util
import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "release/runtime_resource_ownership.yaml"
VALIDATOR = ROOT / "scripts/validate_skill_package.py"

EXPECTED_ROOTS = {
    "templates/operations/": "kitchen-event-operations",
    "templates/safety/": "food-safety-allergens",
    "templates/product-plans/": "evochia-product-development",
    "templates/artifacts/": "evochia-brand-documents",
}

EXPECTED_EXACT = {
    "schemas/event_brief.schema.json": "kitchen-event-operations",
    "schemas/event_economics.schema.json": "kitchen-event-operations",
    "schemas/haccp_plan.schema.json": "food-safety-allergens",
    "schemas/safety_evidence.schema.json": "food-safety-allergens",
    "schemas/product_plan.schema.json": "evochia-product-development",
    "schemas/artifact_render_request.schema.json": "evochia-brand-documents",
    "references/artifacts/rendering_policy.md": "evochia-brand-documents",
}


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skill_package", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runtime_resource_manifest_declares_expected_owners():
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    roots = {item["path"]: item["owner_skill"] for item in data["resource_roots"]}
    exact = {item["path"]: item["owner_skill"] for item in data["exact_resources"]}
    assert EXPECTED_ROOTS.items() <= roots.items()
    assert EXPECTED_EXACT.items() <= exact.items()


def test_owner_skills_explicitly_reference_their_runtime_resource_roots():
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    for section in ["resource_roots", "exact_resources"]:
        for item in data[section]:
            skill = ROOT / "skills" / item["owner_skill"] / "SKILL.md"
            assert skill.exists()
            text = skill.read_text(encoding="utf-8")
            assert item["reference_token"] in text, (item["path"], item["owner_skill"])


def test_package_validator_includes_runtime_resource_ownership_gate():
    validator = load_validator()
    issues = validator.validate(ROOT)
    assert not [issue for issue in issues if "runtime resource" in issue or "resource owner" in issue]


def test_package_validator_detects_unreachable_declared_resource(tmp_path):
    validator = load_validator()
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    data["exact_resources"].append({
        "path": "schemas/event_brief.schema.json",
        "owner_skill": "culinary-rnd",
        "reference_token": "schemas/event_brief.schema.json",
    })
    issues = validator.validate_runtime_resource_ownership(ROOT, data)
    assert any("resource owner" in issue and "culinary-rnd" in issue for issue in issues)
