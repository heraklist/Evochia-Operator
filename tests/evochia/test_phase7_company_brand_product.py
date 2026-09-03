from pathlib import Path
import hashlib
import json
import re
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]

POLICY_DIR = ROOT / "company/evochia/policies"
POLICY_STATE = POLICY_DIR / "policy_state_contract.yaml"
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


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    framed = f"blob {len(payload)}\0".encode("ascii") + payload
    return hashlib.sha1(framed).hexdigest()


def policy_contract() -> dict:
    return yaml.safe_load(read(POLICY_STATE))


def policy_status(name: str) -> str:
    text = read(POLICY_DIR / name)
    match = re.search(r"Policy status:\*\*\s*`?([A-Z_]+)`?", text)
    assert match, f"{name}: missing explicit Policy status"
    return match.group(1)


def test_policy_bundle_has_explicit_valid_states_and_preserves_historical_boundaries():
    contract = policy_contract()
    allowed = set(contract["allowed_statuses"])
    for name in POLICIES:
        assert policy_status(name) in allowed
        assert contract["policies"][name]["status"] == policy_status(name)

    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    terms = read(POLICY_DIR / "terms_policy.md")
    assert "historical" in (commercial + rates + terms).lower()
    assert "proposal" in rates.lower()
    assert "must not" in rates.lower() or "not become" in rates.lower()


def test_rate_policy_preserves_service_families_and_never_promotes_historical_evidence_silently():
    text = read(POLICY_DIR / "current_rates.md")
    status = policy_status("current_rates.md")
    for token in ["Breakfast Only", "Half Board", "Full Board", "One-Off Private Dinner"]:
        assert token in text
    assert "PROPOSAL_SPECIFIC_EVIDENCE" in text
    assert not re.search(r"APPROVED[^\n]{0,120}€?3[,\.]?650", text, flags=re.I)
    if status != "APPROVED":
        assert "CANDIDATE_FROM_OWNER_WORKING_DECISION" in text
        assert "NEEDS_RECONCILIATION" in text or "RETIRED_ON_OWNER_APPROVAL" in text


def test_commercial_and_terms_keep_vat_quote_validity_and_cancellation_explicit():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    terms = read(POLICY_DIR / "terms_policy.md")
    combined = commercial + "\n" + terms
    assert "VAT" in combined
    assert "current applicable" in combined.lower()
    assert "quote validity" in terms.lower()
    assert "cancellation" in terms.lower()
    if policy_status("terms_policy.md") != "APPROVED":
        assert "30%" in terms
        assert "NEEDS_OWNER_APPROVAL" in terms


def test_staffing_policy_is_contextual_not_guest_count_only():
    text = read(POLICY_DIR / "staffing_policy.md")
    for term in ["guest", "service format", "plated", "Half Board", "equipment", "travel"]:
        assert term.lower() in text.lower()
    if policy_status("staffing_policy.md") != "APPROVED":
        assert "NEEDS_OWNER_APPROVAL" in text
        assert "6+" in text


def test_brand_bundle_uses_canonical_generated_tagline_and_documents_source_typo_safely():
    for name in BRAND_FILES:
        read(BRAND_DIR / name)
    voice = read(BRAND_DIR / "brand_voice.md")
    identity = read(BRAND_DIR / "visual_identity.md")
    assert "Sophisticated taste & tailored events" in voice + identity
    assert "Sofisticated taste & tailored events" not in voice
    if "Sofisticated taste & tailored events" in identity:
        low = identity.lower()
        assert "source evidence" in low
        assert "not the default" in low


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


def test_brand_assets_are_materialized_or_pinned_and_fail_closed():
    assets = BRAND_DIR / "assets"
    names = {p.name for p in assets.iterdir() if p.is_file()}
    assert {"README.md", "render_integrity.yaml", "logo-mark-42.png"}.issubset(names)

    mark = assets / "logo-mark-42.png"
    assert mark.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert git_blob_sha(mark) == "11676370669ef00c1ed6815300db240c5ce376f8"

    contract = yaml.safe_load(read(assets / "render_integrity.yaml"))
    assert contract["resolution_policy"] == "fail_closed"
    assert contract["final_artifact_requires_verified_assets"] is True
    assert contract["logo"]["active_default"]["source_commit"] == "8168999e22ef5ca000dfe5c4be53e6e084c9db6f"
    assert contract["logo"]["active_default"]["assets"]["ui_raster_mark_1x"]["git_blob_sha"] == "11676370669ef00c1ed6815300db240c5ce376f8"
    gate = contract["render_gate"]
    assert gate["missing_logo"] == "fail"
    assert gate["missing_required_font"] == "fail"
    assert gate["silent_font_substitution"] == "forbidden"
    assert gate["pdf_font_embedding_required"] is True

    manifest = read(assets / "README.md")
    assert "ORIGINAL TRANSPARENT.svg" in manifest
    assert "do not use that lockup as the default" in manifest.lower()


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
