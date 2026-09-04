from pathlib import Path
import importlib.util
import json
import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "evals/eval_manifest.yaml"
E2E = ROOT / "evals/e2e/e2e_cases.yaml"
RUNNER = ROOT / "evals/run_evals.py"
PACKAGE_POLICY = ROOT / "release/package_policy.yaml"
READINESS = ROOT / "release/release_readiness.yaml"
PACKAGE_VALIDATOR = ROOT / "scripts/validate_skill_package.py"
WORKFLOW = ROOT / ".github/workflows/verify.yml"

EXPECTED_CATEGORIES = {
    "legacy", "routing", "culinary", "safety", "costing", "supplier", "operations",
    "brand", "product-development", "market-intelligence", "integrations", "leakage/security"
}
EXPECTED_E2E = {
    "classic_recipe_to_production_recipe",
    "trend_research_to_original_recipe",
    "private_chef_enquiry_to_proposal",
    "catering_event_to_run_sheet",
    "allergen_critical_safe_block",
    "supplier_snapshot_to_ep_cost",
    "new_evochia_product_to_flyer_payload",
    "market_question_snapshot_plus_fresh_evidence",
    "tool_unavailable_safe_fallback",
    "client_safe_leakage_check",
}


def read(path: Path) -> str:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def test_eval_manifest_covers_all_required_categories_with_existing_sources():
    data = yaml.safe_load(read(MANIFEST))
    categories = {item["category"] for item in data["categories"]}
    assert categories == EXPECTED_CATEGORIES
    for item in data["categories"]:
        assert item["sources"], item["category"]
        for rel in item["sources"]:
            assert (ROOT / rel).exists(), f"missing eval source {rel}"


def test_e2e_suite_contains_all_ten_required_cross_skill_cases():
    data = yaml.safe_load(read(E2E))
    ids = {case["id"] for case in data["cases"]}
    assert EXPECTED_E2E <= ids
    for case in data["cases"]:
        assert case["required_skills"]
        assert "must" in case
        assert "must_not" in case


def test_eval_runner_is_importable_and_static_validation_passes():
    assert RUNNER.exists()
    spec = importlib.util.spec_from_file_location("run_evals", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.run_static_evals(ROOT)
    assert result["status"] == "PASS", result
    assert result["categories"] == len(EXPECTED_CATEGORIES)
    assert result["e2e_cases"] >= 10


def test_package_policy_requires_all_twelve_skills_and_excludes_sensitive_runtime_files():
    data = yaml.safe_load(read(PACKAGE_POLICY))
    assert len(data["required_skills"]) == 12
    assert "chef-ai-pro-business" in data["required_skills"]
    deny = set(data["forbidden_patterns"])
    for token in [".browser_profile_themart", ".env", "Cookies", "Login Data", "*.key", "*.pem"]:
        assert token in deny
    assert data["font_binaries_in_package"] is False
    assert data["backend_source_in_package"] is False


def test_package_validator_passes_repository_candidate_and_checks_skill_frontmatter_and_refs():
    assert PACKAGE_VALIDATOR.exists()
    spec = importlib.util.spec_from_file_location("validate_skill_package", PACKAGE_VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    issues = module.validate(ROOT)
    assert issues == [], issues


def test_release_readiness_closes_phase8b_but_keeps_surface_validation_blocking():
    data = yaml.safe_load(read(READINESS))
    assert data["candidate_version"] == "4.0.0-alpha.0"
    assert data["repository_candidate_status"] == "READY_FOR_FINAL_BLOCKERS"
    assert data["final_release_status"] == "BLOCKED"
    blockers = {item["id"]: item for item in data["blockers"]}
    assert blockers["phase8b_exact_themart_source_migration"]["status"] == "CLOSED"
    assert blockers["openai_surface_install_scan"]["status"] == "NOT_RUN"
    assert blockers["phase8b_exact_themart_source_migration"]["required_before_final_release"] is True
    assert blockers["openai_surface_install_scan"]["required_before_final_release"] is True


def test_release_readiness_does_not_claim_production_backend_and_supports_policy_state_transitions():
    data = yaml.safe_load(read(READINESS))
    assert data["backend_readiness"] == "MOCK_ADAPTER_NOT_PRODUCTION_PERSISTENCE"
    assert data["commercial_policy_readiness"] in {
        "OWNER_REVIEW_REQUIRED", "PARTIALLY_APPROVED", "APPROVED"
    }
    assert data["may_claim_production_ready"] is False


def test_ci_runs_eval_and_package_validators_after_pytest():
    text = read(WORKFLOW)
    assert "python evals/run_evals.py" in text
    assert "python scripts/validate_skill_package.py" in text
