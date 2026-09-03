from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "integrations/chef-ai-api"
FNB = ROOT / "integrations/fnb-central/handoff_contract.md"
ORCHESTRATOR = ROOT / "skills/chef-ai-pro-business/SKILL.md"
EVALS = ROOT / "evals/integrations/integration_cases.yaml"

BACKEND_COMMIT = "74aaa31a7f5f725ad661aa3fe19f8100a36b17b7"
ROUTE_CATALOG_BLOB = "8bd2faf7cc384a90866660a79cf564d20b76c90a"

EXPECTED_READS = {
    "listIngredients", "getIngredient", "listCurrentSupplierPrices", "searchSupplierPrices",
    "searchYieldProfiles", "getIngredientAllergens", "searchRecipes", "getRecipeRevision",
    "listPricingProfiles", "getQuote", "getQuoteDrift", "getSupplierPriceIntakeJob",
    "listGoogleDriveFolderFiles", "getExportStatus", "getPosSales", "getMenuMixAnalytics",
    "getIngredientDemandForecast", "getPurchasePlan", "getCurrentInventory",
}
EXPECTED_WRITES = {
    "createSupplierPriceIntakeJob", "createProposedSupplierPrice", "bulkCreateProposedSupplierPrices",
    "createRecipeDraft", "addRecipeDraftLine", "createRecipeCostingPreview", "submitRecipeDraftForReview",
    "createCostingCardDraft", "createQuoteDraft", "createScenarioDraft", "createExportDraft",
    "exportCostingWorkbookToGoogleSheets", "exportRecipeCardToGoogleSheets", "exportPricingReportToGoogleSheets",
    "exportAllergenMatrixToGoogleSheets", "createEventDraft", "createQuoteScenario", "exportQuote",
    "importSales", "createPurchasePlanDraft", "exportPurchasePlan", "createInventoryUsagePreview",
}


def read(path: Path) -> str:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def load(path: Path):
    return yaml.safe_load(read(path))


def test_backend_contract_pins_real_separate_repo_and_declares_mock_adapter_state():
    data = load(API_DIR / "backend_contract.yaml")
    assert data["repository"] == "heraklist/chef-ai-pro-business-api"
    assert data["pinned_commit"] == BACKEND_COMMIT
    assert data["route_catalog"]["path"] == "src/router/routeCatalog.ts"
    assert data["route_catalog"]["git_blob_sha"] == ROUTE_CATALOG_BLOB
    assert data["runtime_state"] == "FUNCTIONAL_MOCK_ADAPTER"
    assert data["production_persistence"] is False
    assert data["backend_source_lives_here"] is False


def test_capability_map_covers_all_backend_routes_and_has_no_generic_execute_endpoint():
    data = load(API_DIR / "capability_map.yaml")
    reads = {x["operation_id"] for x in data["reads"]}
    writes = {x["operation_id"] for x in data["writes"]}
    assert reads == EXPECTED_READS
    assert writes == EXPECTED_WRITES
    all_ops = reads | writes
    assert not any(op.lower() in {"execute", "run", "doanything", "genericexecute"} for op in all_ops)
    assert all(item["write"] is False for item in data["reads"])
    assert all(item["write"] is True and item["sensitive"] is True for item in data["writes"])


def test_execution_policy_requires_explicit_confirmation_idempotency_and_proposal_before_writes():
    data = load(API_DIR / "execution_policy.yaml")
    assert data["reads"]["invoke_when"] == "USER_REQUESTED_OR_CONFIGURED"
    assert data["writes"]["default"] == "PROPOSE_THEN_CONFIRM"
    assert data["writes"]["required_before_execution"] == [
        "action_summary", "affected_records", "material_assumptions", "explicit_confirmation"
    ]
    assert data["writes"]["idempotency_required"] is True
    assert data["writes"]["confirmation_token_required"] is True
    assert data["writes"]["retry_policy"] == "IDEMPOTENT_RETRY_ONLY"
    assert data["tool_unavailable"]["behavior"] == "DRAFT_OR_HANDOFF_NO_FAKE_EXECUTION"


def test_auth_contract_names_environment_inputs_without_secret_values():
    data = load(API_DIR / "auth_environment.yaml")
    assert data["auth_mode_default"] == "api_key"
    assert data["api_key_header"] == "x-api-key"
    assert data["workspace_header"] == "x-workspace-id"
    assert data["actor_role_header"] == "x-actor-role"
    assert "API_KEY" in data["environment_variables"]
    serialized = read(API_DIR / "auth_environment.yaml")
    assert "sk-" not in serialized
    assert "your_key" not in serialized
    assert data["secret_storage_rule"] == "SECRET_STORE_OR_RUNTIME_ENV_ONLY"


def test_openapi_refs_are_pinned_external_contracts_not_backend_copies_of_business_logic():
    data = load(API_DIR / "openapi_refs.yaml")
    assert data["repository"] == "heraklist/chef-ai-pro-business-api"
    assert data["pinned_commit"] == BACKEND_COMMIT
    paths = {x["path"] for x in data["contracts"]}
    assert {
        "openapi/chef_ai_pro_business_full_actions_v3_2_2.yaml",
        "openapi/chef_ai_pro_business_primary_actions_v3_2_2.yaml",
        "openapi/chef_ai_pro_business_v3_0_read_only.yaml",
        "openapi/chef_ai_pro_business_v3_1_controlled_writes.yaml",
        "openapi/chef_ai_pro_business_v3_2_integrations.yaml",
    } <= paths
    assert data["backend_implementation_copied_into_skill_repo"] is False


def test_fnb_central_handoff_preserves_system_of_record_boundary_and_no_duplicate_persistence():
    text = read(FNB)
    for term in ["system of record", "recipe", "event", "quote", "supplier", "handoff", "idempotency"]:
        assert term.lower() in text.lower()
    assert "does not persist" in text.lower() or "no duplicate persistence" in text.lower()
    assert "FnB Central" in text
    assert "Chef AI" in text


def test_orchestrator_and_integration_evals_use_contracts_and_safe_tool_unavailable_behavior():
    skill = read(ORCHESTRATOR)
    assert "integrations/chef-ai-api/execution_policy.yaml" in skill
    assert "integrations/fnb-central/handoff_contract.md" in skill
    data = load(EVALS)
    ids = {c["id"] for c in data["cases"]}
    assert {"read_without_side_effect", "write_requires_confirmation", "retry_write", "tool_unavailable", "fnb_handoff"} <= ids
    write = next(c for c in data["cases"] if c["id"] == "write_requires_confirmation")
    assert write["must_not"]["execute_before_confirmation"] is True
    unavailable = next(c for c in data["cases"] if c["id"] == "tool_unavailable")
    assert unavailable["must_not"]["claim_execution_succeeded"] is True
    handoff = next(c for c in data["cases"] if c["id"] == "fnb_handoff")
    assert handoff["must_not"]["duplicate_persistent_state_in_skill"] is True
