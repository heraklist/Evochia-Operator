from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "company/evochia/policies"
BRAND_VOICE = ROOT / "company/evochia/brand/brand_voice.md"
REGISTRY = ROOT / "references/source_registry.yaml"
READINESS = ROOT / "release/release_readiness.yaml"

APPROVAL_REF = "owner-approval-2026-09-03-phase13.2"
EFFECTIVE_DATE = "2026-09-03"
POLICIES = [
    "company_profile.md",
    "commercial_policy.md",
    "current_rates.md",
    "staffing_policy.md",
    "terms_policy.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_commercial_policy_bundle_is_partially_approved_with_owner_metadata():
    contract = yaml.safe_load(read(POLICY_DIR / "policy_state_contract.yaml"))
    for name in POLICIES:
        item = contract["policies"][name]
        assert item["status"] == "PARTIALLY_APPROVED"
        assert item["approved_by"] == "Evochia Owner"
        assert str(item["effective_date"]) == EFFECTIVE_DATE
        assert item["approval_reference"] == APPROVAL_REF

        text = read(POLICY_DIR / name)
        assert "**Policy status:** `PARTIALLY_APPROVED`" in text
        assert "**Approved by:** `Evochia Owner`" in text
        assert f"**Effective date:** `{EFFECTIVE_DATE}`" in text
        assert f"**Approval reference:** `{APPROVAL_REF}`" in text


def test_brand_voice_is_owner_approved_and_existing_registry_authority_is_redirected():
    voice = read(BRAND_VOICE)
    assert "**Status:** `APPROVED`" in voice
    assert "**Approved by:** `Evochia Owner`" in voice
    assert f"**Effective date:** `{EFFECTIVE_DATE}`" in voice
    assert f"**Approval reference:** `{APPROVAL_REF}`" in voice

    registry = yaml.safe_load(read(REGISTRY))
    matches = [s for s in registry["sources"] if s["source_id"] == "evochia_brand_voice"]
    assert len(matches) == 1
    source = matches[0]
    assert source["path_or_external_ref"] == "company/evochia/brand/brand_voice.md"
    assert source["source_class"] == "canonical_policy"
    assert source["authority"] == "canonical"
    assert str(source["effective_date"]) == EFFECTIVE_DATE
    assert "archive:files(1)/Evochia_Company_Brain_ChatGPT/Evochia_Brand_Voice.md" in source.get("notes", "")


def test_phase13_release_blocker_is_closed_but_release_remains_blocked_for_other_gates():
    readiness = yaml.safe_load(read(READINESS))
    assert readiness["commercial_policy_readiness"] == "PARTIALLY_APPROVED"
    assert readiness["final_release_status"] == "BLOCKED"
    assert readiness["may_claim_production_ready"] is False
    blocker = next(b for b in readiness["blockers"] if b["id"] == "phase13_commercial_policy_owner_lock")
    assert blocker["status"] == "CLOSED"
    assert any(b["id"] == "phase8b_exact_themart_source_migration" and b["status"] == "OPEN" for b in readiness["blockers"])


def test_explicitly_open_commercial_items_remain_open_after_owner_lock():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    terms = read(POLICY_DIR / "terms_policy.md")
    combined = "\n".join([commercial, rates, terms]).lower()
    for phrase in [
        "balance-payment timing",
        "cancellation/refundability",
        "quote validity",
        "peak-date",
        "household-chef global rate card",
    ]:
        assert phrase in combined
    assert "open" in combined


def test_full_board_under_six_is_now_an_approved_review_trigger_not_pending_proposal():
    staffing = read(POLICY_DIR / "staffing_policy.md")
    assert "Full Board under 6:** `MANDATORY_REVIEW_TRIGGER`, not automatic assistant" in staffing
    assert not re.search(r"Full Board under 6[^\n]{0,180}awaiting explicit owner approval", staffing, flags=re.I)
