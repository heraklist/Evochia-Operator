from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "company/evochia/policies"
BRAND_VOICE = ROOT / "company/evochia/brand/brand_voice.md"
REGISTRY = ROOT / "references/source_registry.yaml"
READINESS = ROOT / "release/release_readiness.yaml"

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


def test_commercial_policy_bundle_uses_policy_state_contract_as_current_authority():
    contract = yaml.safe_load(read(POLICY_DIR / "policy_state_contract.yaml"))
    for name in POLICIES:
        item = contract["policies"][name]
        assert item["status"] in {"OWNER_REVIEW_DRAFT", "PARTIALLY_APPROVED", "APPROVED"}
        if item["status"] in {"PARTIALLY_APPROVED", "APPROVED"}:
            assert item["approved_by"] == "Evochia Owner"
            assert str(item["effective_date"]) == EFFECTIVE_DATE
            assert item["approval_reference"]

        text = read(POLICY_DIR / name)
        assert f"**Policy status:** `{item['status']}`" in text
        if item["status"] in {"PARTIALLY_APPROVED", "APPROVED"}:
            assert "**Approved by:** `Evochia Owner`" in text
            assert f"**Effective date:** `{EFFECTIVE_DATE}`" in text
            assert f"**Approval reference:** `{item['approval_reference']}`" in text


def test_brand_voice_is_owner_approved_and_existing_registry_authority_is_redirected():
    voice = read(BRAND_VOICE)
    assert "**Status:** `APPROVED`" in voice
    assert "**Approved by:** `Evochia Owner`" in voice
    assert f"**Effective date:** `{EFFECTIVE_DATE}`" in voice
    assert "**Approval reference:** `owner-approval-2026-09-03-phase13.2`" in voice

    registry = yaml.safe_load(read(REGISTRY))
    matches = [s for s in registry["sources"] if s["source_id"] == "evochia_brand_voice"]
    assert len(matches) == 1
    source = matches[0]
    assert source["path_or_external_ref"] == "company/evochia/brand/brand_voice.md"
    assert source["source_class"] == "canonical_policy"
    assert source["authority"] == "canonical"
    assert str(source["effective_date"]) == EFFECTIVE_DATE
    assert "archive:files(1)/Evochia_Company_Brain_ChatGPT/Evochia_Brand_Voice.md" in source.get("notes", "")


def test_phase13_2_release_record_stays_closed_while_release_remains_blocked():
    readiness = yaml.safe_load(read(READINESS))
    assert readiness["final_release_status"] == "BLOCKED"
    assert readiness["may_claim_production_ready"] is False
    blocker = next(b for b in readiness["blockers"] if b["id"] == "phase13_commercial_policy_owner_lock")
    assert blocker["status"] == "CLOSED"
    assert any(
        b["id"] == "phase8b_exact_themart_source_migration" and b["status"] == "OPEN"
        for b in readiness["blockers"]
    )


def test_phase13_2_history_does_not_require_phase13_3_rows_to_remain_open():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    terms = read(POLICY_DIR / "terms_policy.md")
    combined = "\n".join([commercial, rates, terms]).lower()
    assert "policy status" in combined
    # Phase 13.3 owns the current row-closure expectations. This historical
    # test intentionally does not force balance/cancellation/validity/peak/
    # household rows back to OPEN.


def test_full_board_under_six_is_now_an_approved_review_trigger_not_pending_proposal():
    staffing = read(POLICY_DIR / "staffing_policy.md")
    assert "Full Board under 6:** `MANDATORY_REVIEW_TRIGGER`, not automatic assistant" in staffing
    assert not re.search(
        r"Full Board under 6[^\n]{0,180}awaiting explicit owner approval",
        staffing,
        flags=re.I,
    )
