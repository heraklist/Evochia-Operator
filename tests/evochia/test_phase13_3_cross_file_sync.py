from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "company/evochia/policies"
STATE = POLICY_DIR / "policy_state_contract.yaml"
READINESS = ROOT / "release/release_readiness.yaml"


def read(name: str) -> str:
    return (POLICY_DIR / name).read_text(encoding="utf-8")


def test_closed_phase13_3_rows_are_not_stale_open_anywhere():
    files = {
        name: read(name).lower()
        for name in ["terms_policy.md", "commercial_policy.md", "current_rates.md", "company_profile.md"]
    }
    joined = "\n".join(files.values())
    stale_patterns = [
        "balance-payment timing",
        "cancellation/refundability windows",
        "standard quote validity",
        "peak-date pricing/surcharge policy",
        "household-chef global rate card remains open",
        "evochia food & hospitality group | `needs_owner_approval`",
    ]
    for pattern in stale_patterns:
        assert pattern not in joined


def test_unrelated_open_rows_are_preserved():
    terms = read("terms_policy.md").lower()
    rates = read("current_rates.md").lower()
    profile = read("company_profile.md").lower()
    assert "legal" in terms and ("open" in terms or "review" in terms)
    assert "service family" in rates and "open" in rates
    assert "public-facing price-list" in rates and "open" in rates
    assert "service-taxonomy" in profile or "service taxonomy" in profile


def test_file_statuses_follow_row_closure_targets():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    assert state["policies"]["commercial_policy.md"]["status"] == "APPROVED"
    assert state["policies"]["terms_policy.md"]["status"] == "PARTIALLY_APPROVED"
    assert state["policies"]["current_rates.md"]["status"] == "PARTIALLY_APPROVED"
    assert state["policies"]["company_profile.md"]["status"] == "PARTIALLY_APPROVED"
    assert state["policies"]["staffing_policy.md"]["status"] == "PARTIALLY_APPROVED"


def test_approved_files_have_no_actual_open_rows():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    for name, item in state["policies"].items():
        if item["status"] == "APPROVED":
            text = read(name)
            assert "`OPEN`" not in text
            assert "NEEDS_OWNER_APPROVAL" not in text


def test_phase13_3_changed_policy_metadata_uses_phase13_3_approval_reference():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    for name in ["terms_policy.md", "commercial_policy.md", "current_rates.md", "company_profile.md"]:
        item = state["policies"][name]
        assert item["approved_by"] == "Evochia Owner"
        assert str(item["effective_date"]) == "2026-09-03"
        assert item["approval_reference"] == "owner-approval-2026-09-03-phase13.3"
        text = read(name)
        assert "**Approval reference:** `owner-approval-2026-09-03-phase13.3`" in text


def test_staffing_policy_remains_on_phase13_2_authority_when_unchanged():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    staffing = state["policies"]["staffing_policy.md"]
    assert staffing["status"] == "PARTIALLY_APPROVED"
    assert staffing["approval_reference"] == "owner-approval-2026-09-03-phase13.2"


def test_release_readiness_closes_phase13_3_without_claiming_full_release():
    readiness = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert readiness["commercial_policy_readiness"] == "PARTIALLY_APPROVED"
    assert readiness["final_release_status"] == "BLOCKED"
    assert readiness["may_claim_production_ready"] is False
    serialized = str(readiness).lower()
    assert "phase13.3" in serialized
    assert "phase13_3_commercial_terms_completion" in serialized
    assert "phase8b_exact_themart_source_migration" in serialized
    assert "openai_surface_install_scan" in serialized


def test_release_readiness_does_not_retain_phase13_2_stale_commercial_residue_note():
    readiness = READINESS.read_text(encoding="utf-8").lower()
    stale_fragments = [
        "does not close balance timing",
        "does not close cancellation/refundability",
        "does not close standard quote validity",
        "does not close peak-date policy",
        "does not close household-chef global rate card",
    ]
    for fragment in stale_fragments:
        assert fragment not in readiness
