from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "company/evochia/policies"
BRAND_VOICE = ROOT / "company/evochia/brand/brand_voice.md"
ROUTING = ROOT / "skills/chef-ai-pro-business/references/routing.yaml"
REGISTRY = ROOT / "references/source_registry.yaml"
READINESS = ROOT / "release/release_readiness.yaml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase13_2_policy_bundle_keeps_explicit_state_and_approval_boundaries():
    contract = yaml.safe_load(read(POLICY_DIR / "policy_state_contract.yaml"))
    for name, item in contract["policies"].items():
        text = read(POLICY_DIR / name)
        assert item["status"] in {"OWNER_REVIEW_DRAFT", "PARTIALLY_APPROVED", "APPROVED"}
        assert f"**Policy status:** `{item['status']}`" in text
        if item["status"] in {"PARTIALLY_APPROVED", "APPROVED"}:
            assert item["approved_by"] == "Evochia Owner"
            assert item["effective_date"]
            assert item["approval_reference"]
        else:
            assert item["approved_by"] is None


def test_brand_voice_preserves_internal_constraint_and_single_authority_transition():
    text = read(BRAND_VOICE)
    assert "Internal positioning constraint" in text
    assert "restaurant-at-home" in text

    registry = yaml.safe_load(read(REGISTRY))
    matches = [s for s in registry["sources"] if s["source_id"] == "evochia_brand_voice"]
    assert len(matches) == 1
    source = matches[0]
    if "**Status:** `APPROVED`" in text:
        assert source["path_or_external_ref"] == "company/evochia/brand/brand_voice.md"
        assert "archive:files(1)/Evochia_Company_Brain_ChatGPT/Evochia_Brand_Voice.md" in source.get("notes", "")
    else:
        assert source["path_or_external_ref"] == "archive:files(1)/Evochia_Company_Brain_ChatGPT/Evochia_Brand_Voice.md"


def test_commercial_content_preserves_internal_client_separation_and_base_rates():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    assert "INTERNAL costing architecture != CLIENT quotation format" in commercial
    assert "INTERNAL BASE RATE CARD" in rates
    for value in ["€140", "€180", "€230", "€250", "€330", "€440", "€380", "€520", "€660"]:
        assert value in rates
    assert "€70 additional production day" in rates
    assert "RETIRED_ON_OWNER_APPROVAL" in rates or "`RETIRED`" in rates


def test_staffing_contains_exact_plated_and_transport_rules():
    staffing = read(POLICY_DIR / "staffing_policy.md")
    assert "within Attica / outside Attica" in staffing
    assert "6+ guests OR plated service" in staffing
    assert "Half Board under 6" in staffing
    assert "Full Board under 6" in staffing
    assert "MANDATORY_REVIEW_TRIGGER" in staffing
    assert "((base_rate * 11 + 99) // 100) * 10" in staffing
    assert "binary floating-point" in staffing
    assert "€100 / €140 / €200 / €220 / €250" in staffing
    assert "TRANSPORT_UNVERIFIED" in staffing
    assert "OWNER_APPROVED_PROMO_SUBSIDY" in staffing
    assert "Stay model" in staffing
    assert "Commute model" in staffing


def test_outside_attica_half_board_uses_existing_minimum_staff_rate_and_day_floor():
    staffing = read(POLICY_DIR / "staffing_policy.md")
    assert "Outside Attica — Half Board | €180/person/day | €180 minimum" in staffing
    assert "day-floor" in staffing.lower()
    assert "not priced per meal" in staffing.lower()
    assert "Dinner-only and Half Board" in staffing
    assert "Full Board starts at €200" in staffing
    assert "Outside Attica Half Board support-day rate" not in staffing


def test_terms_and_routing_allow_provisional_quote_but_gate_final_acceptance():
    terms = read(POLICY_DIR / "terms_policy.md")
    routing = yaml.safe_load(read(ROUTING))
    assert "TRANSPORT_UNVERIFIED" in terms
    assert "before final acceptance" in terms
    assert "written acceptance" in terms
    assert "CONFIRMATION_PAYMENT" in terms

    route = next(r for r in routing["routes"] if r["route_id"] == "client_safe_proposal")
    assert route["commercial_terms_policy"] in {
        "per_quote_explicit_material_terms",
        "canonical_evochia_terms_with_explicit_overrides",
    }
    assert "unresolved_safety_conflict" in route["blockers"]
    assert "unapproved_material_commercial_terms" not in route["blockers"]


def test_release_readiness_tracks_current_policy_state_without_claiming_production_ready():
    readiness = yaml.safe_load(read(READINESS))
    assert readiness["commercial_policy_readiness"] in {
        "OWNER_REVIEW_REQUIRED", "PARTIALLY_APPROVED", "APPROVED"
    }
    assert readiness["final_release_status"] == "BLOCKED"
    assert readiness["may_claim_production_ready"] is False
