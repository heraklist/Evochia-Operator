from pathlib import Path
import json
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/artifact_render_request.schema.json"
POLICY = ROOT / "references/artifacts/rendering_policy.md"
RECIPEBOOK = ROOT / "templates/artifacts/recipebook_contract.yaml"
CLIENT = ROOT / "templates/artifacts/client_artifact_contracts.yaml"
EVALS = ROOT / "evals/artifacts/artifact_cases.yaml"
BRAND_CONTRACT = ROOT / "company/evochia/brand/assets/render_integrity.yaml"


def read(path: Path) -> str:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def test_render_request_schema_is_valid_and_separates_canonical_content_from_renderer():
    schema = json.loads(read(SCHEMA))
    Draft202012Validator.check_schema(schema)
    text = json.dumps(schema)
    for token in [
        "artifact_type", "audience", "output_format", "canonical_content_ref",
        "brand_profile", "render_status", "brand_verification", "confidentiality",
    ]:
        assert token in text
    assert "FINAL_VERIFIED" in text
    assert "DRAFT_UNVERIFIED_BRAND_RENDER" in text


def test_rendering_policy_forbids_templates_from_owning_business_logic():
    text = read(POLICY).lower()
    assert "canonical" in text
    assert "business logic" in text
    assert "template" in text
    assert "must not" in text or "forbidden" in text
    assert "internal" in text and "client-safe" in text


def test_final_pdf_requires_verified_logo_and_embedded_fonts():
    text = read(POLICY)
    assert "FINAL_VERIFIED" in text
    assert "pdf" in text.lower()
    assert "embedded" in text.lower()
    assert "logo" in text.lower()
    assert "fail" in text.lower()
    brand = yaml.safe_load(read(BRAND_CONTRACT))
    assert brand["render_gate"]["pdf_font_embedding_required"] is True
    assert brand["resolution_policy"] == "fail_closed"


def test_docx_is_editable_source_unless_font_environment_is_verified():
    text = read(POLICY).lower()
    assert "docx" in text
    assert "editable" in text
    assert "pixel-stable" in text
    assert "verified font environment" in text


def test_recipebook_contract_is_a4_landscape_operations_first_and_uses_canonical_recipe_data():
    data = yaml.safe_load(read(RECIPEBOOK))
    assert data["artifact_type"] == "production_recipebook"
    assert data["page"]["size"] == "A4"
    assert data["page"]["orientation"] == "landscape"
    assert data["design_priority"] == "operations_first"
    assert data["canonical_inputs"] == ["recipe", "shopping_list", "production_timeline"]
    for block in ["yield", "equipment", "ingredients", "method", "holding_service", "ccp"]:
        assert block in data["required_recipe_blocks"]


def test_client_artifact_contracts_enforce_client_safe_projection_and_policy_authority():
    data = yaml.safe_load(read(CLIENT))
    assert set(data["artifacts"]) == {"proposal", "client_menu", "flyer", "product_sheet"}
    for name, contract in data["artifacts"].items():
        assert contract["audience"] == "CLIENT_SAFE"
        forbidden = set(contract["forbidden_internal_fields"])
        assert {"internal_margin", "opportunity_cost", "supplier_comparison"}.issubset(forbidden)
    proposal = data["artifacts"]["proposal"]
    assert proposal["commercial_terms_authority"] == "approved_evochia_policy_only"
    assert proposal["historical_proposal_prices_as_current_policy"] is False


def test_artifact_evals_cover_recipebook_proposal_menu_flyer_and_brand_failure():
    data = yaml.safe_load(read(EVALS))
    ids = {case["id"] for case in data["cases"]}
    required = {
        "production_recipebook_from_canonical_recipe",
        "private_chef_proposal_client_projection",
        "client_menu_no_internal_cost_leakage",
        "product_flyer_from_approved_definition",
        "pdf_brand_preflight_failure",
        "docx_unverified_font_environment",
    }
    assert required.issubset(ids)


def test_brand_failure_eval_never_silently_falls_back():
    data = yaml.safe_load(read(EVALS))
    case = next(c for c in data["cases"] if c["id"] == "pdf_brand_preflight_failure")
    assert case["expected"]["final_status"] != "FINAL_VERIFIED"
    assert case["must_not"]["silent_font_substitution"] is True
    assert case["must_not"]["synthetic_logo_reconstruction"] is True
