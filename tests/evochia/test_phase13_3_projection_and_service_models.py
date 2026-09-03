from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "company/evochia/policies"
ROUTING = ROOT / "skills/chef-ai-pro-business/references/routing.yaml"
CLIENT_CONTRACTS = ROOT / "templates/artifacts/client_artifact_contracts.yaml"
ARTIFACT_EVALS = ROOT / "evals/artifacts/artifact_cases.yaml"
E2E = ROOT / "evals/e2e/e2e_cases.yaml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_peak_date_is_quote_specific_with_exact_evidence_schema():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    joined = "\n".join([commercial, rates])
    lower = joined.lower()
    assert "no global peak-date surcharge" in lower
    for field in [
        "reason",
        "amount_or_method",
        "date_specific_basis",
        "costs_already_covered_elsewhere",
        "double_count_check",
        "owner_decision/reference",
    ]:
        assert field in joined
    assert "island" in lower and "yacht" in lower
    assert "distinct" in lower and "cause" in lower
    assert "specific" in lower and "date" in lower


def test_household_has_own_recurring_framework_and_all_required_fields():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    joined = "\n".join([commercial, rates])
    lower = joined.lower()
    assert "no global household" in lower
    for field in [
        "scope",
        "service_days_and_hours",
        "extra_day_and_hour_rules",
        "guest_event_rules",
        "food_and_pass_through_treatment",
        "travel",
        "billing_cycle",
        "termination_and_notice",
        "rate_review_and_escalation",
        "absence_or_non_use",
    ]:
        assert field in joined
    assert "recurring" in lower
    assert "t-5" in lower and "not" in lower and "default" in lower
    assert "10/30/100" in joined or "10%/30%/100%" in joined
    assert "mechanism" in lower or "adjustment" in lower


def test_legal_identity_is_closed_and_company_group_characterization_is_forbidden():
    profile = read(POLICY_DIR / "company_profile.md")
    lower = profile.lower()
    assert "ατομική επιχείρηση" in profile
    assert "evochia" in lower
    assert "evochia food & hospitality group" in lower
    assert "διακρι" in lower
    assert "runtime_resolved" in lower
    assert "fail" in lower and "closed" in lower
    assert "company" in lower
    assert "must not" in lower or "prohibited" in lower or "never" in lower


def test_routing_enforces_transport_legal_household_and_client_safe_boundaries():
    routing = yaml.safe_load(read(ROUTING))
    route = next(r for r in routing["routes"] if r["route_id"] == "client_safe_proposal")
    serialized = str(route).lower()
    assert "transport" in serialized and "confirmation" in serialized
    assert "legal" in serialized and "binding" in serialized
    assert "household" in serialized
    assert "client" in serialized and "safe" in serialized
    assert "canonical" in serialized


def test_proposal_artifact_contract_forbids_internal_commercial_fields():
    contracts = yaml.safe_load(read(CLIENT_CONTRACTS))
    proposal = contracts["artifacts"]["proposal"]
    forbidden = set(proposal["forbidden_internal_fields"])
    assert {
        "uncollected_cancellation_balance",
        "internal_margin",
        "opportunity_cost",
        "supplier_comparison",
        "owner_review_reason",
        "classification_evidence",
        "internal_allocation_notes",
    }.issubset(forbidden)


def test_phase13_3_e2e_eval_cases_exist():
    data = yaml.safe_load(read(E2E))
    ids = {case["id"] for case in data["cases"]}
    assert {
        "phase13_3_payment_default_cure",
        "phase13_3_external_impediment_reconciliation",
        "phase13_3_evochia_inability_refund",
        "phase13_3_client_side_impediment",
        "phase13_3_peak_date_overlap_guard",
        "phase13_3_household_recurring_terms",
    }.issubset(ids)


def test_phase13_3_artifact_eval_cases_exist():
    data = yaml.safe_load(read(ARTIFACT_EVALS))
    ids = {case["id"] for case in data["cases"]}
    assert {
        "phase13_3_client_safe_uncollected_balance_guard",
        "phase13_3_binding_identity_fail_closed",
    }.issubset(ids)
