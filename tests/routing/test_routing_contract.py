from __future__ import annotations
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[2]
ROUTING = ROOT / "skills/chef-ai-pro-business/references/routing.yaml"
CASES = ROOT / "evals/routing/routing_cases.yaml"
EXPECTED_SKILLS = {
    "chef-ai-pro-business", "culinary-rnd", "recipe-engineering", "menu-experience-design",
    "kitchen-event-operations", "food-safety-allergens", "costing-commercial-intelligence",
    "supplier-procurement-intelligence", "evochia-company-operations", "evochia-brand-documents",
    "evochia-product-development", "evochia-market-intelligence",
}

def load(path): return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_routing_contract_exists_and_only_uses_known_skills():
    data=load(ROUTING)
    assert data["schema_version"] == 1
    assert data["default_policy"]["selection"] == "smallest_sufficient"
    assert data["authority_source"] == "references/source_registry.yaml"
    assert data["audiences"] == ["INTERNAL", "OPERATIONS", "CLIENT-SAFE"]
    assert set(data["skills"]) == EXPECTED_SKILLS
    for route in data["routes"]:
        assert set(route["required_skills"]) <= EXPECTED_SKILLS
        assert set(route.get("optional_skills", [])) <= EXPECTED_SKILLS

def test_release_critical_routing_cases_are_declared():
    ids={c["case_id"] for c in load(CASES)["cases"]}
    assert {"ROUTE-QUICK-RECIPE","ROUTE-CULINARY-TREND","ROUTE-EVOCHIA-PRIVATE-CHEF","ROUTE-ALLERGEN-CRITICAL","ROUTE-COMPETITOR","ROUTE-SUPPLIER-REFRESH","ROUTE-NEW-PRODUCT","ROUTE-CLIENT-SAFE-PROPOSAL"} <= ids

def test_quick_recipe_does_not_load_company_or_commercial_stack():
    case={c["case_id"]:c for c in load(CASES)["cases"]}["ROUTE-QUICK-RECIPE"]
    assert case["expected_required"] == ["recipe-engineering"]
    assert "evochia-company-operations" in case["must_not_require"]
    assert "costing-commercial-intelligence" in case["must_not_require"]

def test_allergen_critical_always_requires_safety_gate():
    case={c["case_id"]:c for c in load(CASES)["cases"]}["ROUTE-ALLERGEN-CRITICAL"]
    assert "food-safety-allergens" in case["expected_required"]
    assert case["hard_gate"] == "safety"

def test_evochia_private_chef_uses_company_ops_commercial_and_brand():
    req=set({c["case_id"]:c for c in load(CASES)["cases"]}["ROUTE-EVOCHIA-PRIVATE-CHEF"]["expected_required"])
    assert {"evochia-company-operations","kitchen-event-operations","costing-commercial-intelligence","evochia-brand-documents"} <= req

def test_competitor_lookup_does_not_load_culinary_stack():
    case={c["case_id"]:c for c in load(CASES)["cases"]}["ROUTE-COMPETITOR"]
    assert case["expected_required"] == ["evochia-market-intelligence"]
    assert "culinary-rnd" in case["must_not_require"]

def test_supplier_refresh_is_explicit_tool_path():
    case={c["case_id"]:c for c in load(CASES)["cases"]}["ROUTE-SUPPLIER-REFRESH"]
    assert case["expected_required"] == ["supplier-procurement-intelligence"]
    assert case["tool_policy"] == "explicit_user_request"

def test_new_product_routes_to_product_development():
    case={c["case_id"]:c for c in load(CASES)["cases"]}["ROUTE-NEW-PRODUCT"]
    assert "evochia-product-development" in case["expected_required"]
