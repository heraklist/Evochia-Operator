from pathlib import Path
import json
import re
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]

POLICY_DIR = ROOT / "company/evochia/policies"
BRAND_DIR = ROOT / "company/evochia/brand"
GOLDEN = ROOT / "company/evochia/golden_examples/README.md"
PRODUCT_SCHEMA = ROOT / "schemas/product_plan.schema.json"
PRODUCT_TEMPLATE = ROOT / "templates/product-plans/master_product_plan.md"
DECISIONS = ROOT / "templates/product-plans/decision_register.yaml"
PILOT = ROOT / "templates/product-plans/pilot_evidence_pack.md"
PRODUCT_EVALS = ROOT / "evals/product-development/product_cases.yaml"

POLICIES = [
    "company_profile.md",
    "commercial_policy.md",
    "current_rates.md",
    "staffing_policy.md",
    "terms_policy.md",
]

BRAND_FILES = [
    "brand_voice.md",
    "visual_identity.md",
    "visual_tokens.yaml",
    "document_style_guide.md",
    "assets/README.md",
]


def read(path: Path) -> str:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def test_owner_review_policy_bundle_exists_and_is_not_silently_canonical():
    for name in POLICIES:
        text = read(POLICY_DIR / name)
        assert "OWNER_REVIEW_DRAFT" in text
        assert "NEEDS_OWNER_APPROVAL" in text or "APPROVED" in text
    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    terms = read(POLICY_DIR / "terms_policy.md")
    assert "historical" in (commercial + rates + terms).lower()
    assert "proposal" in rates.lower()
    assert "must not" in rates.lower() or "not become" in rates.lower()


def test_rate_draft_preserves_candidate_service_models_but_labels_authority():
    text = read(POLICY_DIR / "current_rates.md")
    for token in ["Breakfast Only", "Half Board", "Full Board", "One-Off Private Dinner"]:
        assert token in text
    for value in ["140", "180", "230", "250", "330", "440", "380", "520", "660"]:
        assert value in text
    assert "CANDIDATE_FROM_OWNER_WORKING_DECISION" in text
    assert "PROPOSAL_SPECIFIC_EVIDENCE" in text
    assert "NEEDS_RECONCILIATION" in text
    assert not re.search(r"APPROVED[^\n]{0,120}€?3[,\.]?650", text, flags=re.I)


def test_commercial_and_terms_drafts_keep_vat_and_deposit_configurable_until_approval():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    terms = read(POLICY_DIR / "terms_policy.md")
    combined = commercial + "\n" + terms
    assert "VAT" in combined
    assert "current applicable" in combined.lower()
    assert "30%" in terms
    assert "NEEDS_OWNER_APPROVAL" in terms
    assert "quote validity" in terms.lower()
    assert "cancellation" in terms.lower()


def test_staffing_policy_is_contextual_not_guest_count_only():
    text = read(POLICY_DIR / "staffing_policy.md")
    for term in ["guest", "service format", "plated", "Half Board", "equipment", "travel"]:
        assert term.lower() in text.lower()
    assert "NEEDS_OWNER_APPROVAL" in text
    assert "6+" in text


def test_brand_bundle_exists_and_uses_correct_tagline():
    for name in BRAND_FILES:
        read(BRAND_DIR / name)
    voice = read(BRAND_DIR / "brand_voice.md")
    identity = read(BRAND_DIR / "visual_identity.md")
    assert "Sophisticated taste & tailored events" in voice + identity
    assert "Sofisticated taste & tailored events" not in voice + identity


def test_visual_tokens_capture_official_palette_and_artifact_specific_typography():
    tokens = yaml.safe_load(read(BRAND_DIR / "visual_tokens.yaml"))
    palette = tokens["color"]["official_identity"]
    for value in ["#024631", "#FBF8EF", "#C8B273", "#DBCEA8", "#013122"]:
        assert value in palette.values()
    typo = tokens["typography"]
    assert typo["digital_site"]["brand_heading"] == "Alexander"
    assert typo["digital_site"]["body"] == "Bainsley"
    assert typo["digital_site"]["accent"] == "Miama"
    assert typo["portable_documents"]["display"] == "Cormorant Garamond"
    assert typo["portable_documents"]["body"] == "EB Garamond"
    assert typo["logo_family_reference"] == "Weiss Font"


def test_document_style_guide_explains_typography_authority_and_no_font_binaries():
    text = read(BRAND_DIR / "document_style_guide.md")
    for term in ["Alexander", "Bainsley", "Miama", "Cormorant Garamond", "EB Garamond", "Weiss"]:
        assert term in text
    assert "vector" in text.lower()
    assert "font binaries" in text.lower()
    assets = BRAND_DIR / "assets"
    forbidden = {".ttf", ".otf", ".woff", ".woff2"}
    assert not any(p.suffix.lower() in forbidden for p in assets.rglob("*") if p.is_file())


def test_brand_asset_manifest_selects_official_vector_master_without_font_binaries():
    assets = BRAND_DIR / "assets"
    names = {p.name for p in assets.iterdir() if p.is_file()}
    assert names == {"README.md"}
    manifest = read(assets / "README.md")
    assert "ORIGINAL TRANSPARENT.svg" in manifest
    assert "official" in manifest.lower() or "approved" in manifest.lower()
    assert "do not commit font binaries" in manifest.lower()


def test_golden_registry_maps_six_output_families_and_denies_pricing_authority():
    text = read(GOLDEN)
    for token in [
        "Private Chef Proposal",
        "Catering / Corporate Proposal",
        "Client Menu",
        "Production Recipebook",
        "Interactive Dining Master Product Plan",
        "Interactive Dining Client Flyer",
    ]:
        assert token in text
    assert "does not control" in text.lower()
    assert "current rates" in text.lower()
    assert "historical" in text.lower()


def test_product_plan_schema_is_valid_and_encodes_decision_gates():
    schema = json.loads(read(PRODUCT_SCHEMA))
    Draft202012Validator.check_schema(schema)
    text = json.dumps(schema)
    for token in [
        "product_definition", "target_customers", "occasions", "positioning",
        "operating_model", "pilot", "evidence", "economics_capacity",
        "risks_governance", "client_projection", "pricing_state", "launch_state",
        "LOCKED", "UNDER_VALIDATION", "OPEN", "PENDING",
    ]:
        assert token in text


def test_product_plan_template_mirrors_golden_pattern_without_hardcoding_interactive_dining():
    text = read(PRODUCT_TEMPLATE)
    for heading in [
        "Product Definition", "Customers, Roles & Occasions", "Value Proposition & Positioning",
        "Product Architecture", "Experience Design", "Culinary System", "Operating Model",
        "Pilot & Validation", "Brand / Go-to-Market", "Economics & Capacity",
        "Commercial Packaging", "Risks & Governance", "Roadmap & Decision Gates",
        "Decision Register",
    ]:
        assert heading in text
    assert "Interactive Dining" not in text
    assert "do not lock pricing" in text.lower()


def test_decision_register_and_pilot_pack_preserve_evidence_hierarchy():
    decisions = yaml.safe_load(read(DECISIONS))
    assert decisions["allowed_states"] == ["LOCKED", "UNDER_VALIDATION", "OPEN", "PENDING"]
    pilot = read(PILOT)
    for term in ["hypothesis", "evidence", "behavior", "specific intent", "comparative preference", "general feedback", "polite praise", "actual cost", "capacity", "opportunity cost"]:
        assert term.lower() in pilot.lower()


def test_product_eval_uses_a_different_product_and_blocks_premature_launch_pricing():
    data = yaml.safe_load(read(PRODUCT_EVALS))
    assert data["cases"]
    case = data["cases"][0]
    assert "Interactive Dining" not in case["prompt"]
    expected = json.dumps(case["expected"])
    for token in ["product_definition", "target_customers", "operating_model", "pilot", "economics_capacity", "decision_states", "client_projection"]:
        assert token in expected
    assert case["must_not"]["lock_pricing_without_evidence"] is True
    assert case["must_not"]["approve_launch_without_gate"] is True


def test_evochia_skills_are_wired_to_phase7_authorities():
    company = read(ROOT / "skills/evochia-company-operations/SKILL.md")
    brand = read(ROOT / "skills/evochia-brand-documents/SKILL.md")
    product = read(ROOT / "skills/evochia-product-development/SKILL.md")
    assert "company/evochia/policies" in company
    assert "company/evochia/brand" in brand
    assert "schemas/product_plan.schema.json" in product
    assert "templates/product-plans" in product
