from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TERMS = ROOT / "company/evochia/policies/terms_policy.md"


def read_terms() -> str:
    return TERMS.read_text(encoding="utf-8")


def test_impediment_threshold_requires_objectively_verifiable_material_event():
    text = read_terms()
    lower = text.lower()
    for token in [
        "EXTERNAL_PERFORMANCE_IMPEDIMENT",
        "EVOCHIA_INABILITY_TO_PERFORM",
        "CLIENT_SIDE_IMPEDIMENT",
        "OWNER_REVIEW_REQUIRED",
    ]:
        assert token in text
    assert "objectively verifiable" in lower
    assert "material event" in lower


def test_cost_fear_preference_and_attendance_are_not_external_by_themselves():
    lower = read_terms().lower()
    for token in ["increased cost", "fear", "preference", "lower attendance"]:
        assert token in lower
    assert "not" in lower and "external" in lower


def test_single_classification_and_hybrid_owner_review_rule():
    lower = read_terms().lower()
    assert "single" in lower and "classification" in lower
    assert "hybrid" in lower or "disputed" in lower
    assert "owner_review_required" in lower
    assert "favorable" in lower or "favourable" in lower


def test_four_workflow_outcomes_are_exact_and_not_regimes():
    text = read_terms()
    for token in [
        "PERFORM_OR_MITIGATE",
        "REPLACEMENT_PERFORMANCE",
        "RESCHEDULE",
        "TERMINATE_AND_RECONCILE",
    ]:
        assert token in text
    assert "outcome" in text.lower()


def test_mitigation_material_incremental_cost_needs_explicit_allocation_agreement():
    lower = read_terms().lower()
    assert "mitigation" in lower
    assert "material incremental" in lower
    assert "cost allocation" in lower
    assert "explicit" in lower and "agreement" in lower


def test_evochia_inability_refunds_unperformed_scope_without_cancellation_tiers():
    text = read_terms()
    lower = text.lower()
    assert "EVOCHIA_INABILITY_TO_PERFORM" in text
    assert "unperformed" in lower
    assert "full refund" in lower or "100%" in text
    assert "10%" in text and "30%" in text and "100%" in text
    assert "do not apply" in lower or "does not apply" in lower


def test_evochia_inability_absorbs_own_sunk_margin_and_opportunity_cost():
    lower = read_terms().lower()
    assert "sunk" in lower
    assert "margin" in lower
    assert "opportunity cost" in lower
    assert "absorb" in lower or "bears" in lower
    assert "not" in lower and "client" in lower


def test_evochia_inability_client_consequential_costs_are_not_automatic():
    lower = read_terms().lower()
    assert "consequential" in lower
    assert "not automatically" in lower
    assert "owner" in lower and ("discretion" in lower or "goodwill" in lower)


def test_replacement_corresponds_to_scope_and_requires_client_acceptance():
    lower = read_terms().lower()
    assert "replacement" in lower
    assert "materially correspond" in lower
    assert "client acceptance" in lower or "client accepts" in lower


def test_evochia_inability_requires_prompt_risk_notification():
    lower = read_terms().lower()
    assert "notify" in lower or "notification" in lower
    assert "prompt" in lower
    assert "material risk" in lower
    assert "known" in lower or "becomes known" in lower


def test_external_impediment_uses_actual_exposure_not_cancellation_tiers():
    text = read_terms()
    lower = text.lower()
    assert "EXTERNAL_PERFORMANCE_IMPEDIMENT" in text
    assert "actual-exposure" in lower or "actual exposure" in lower
    assert "10/30/100" in text or ("10%" in text and "30%" in text and "100%" in text)
    assert "do not" in lower or "does not" in lower


def test_external_evidence_categories_are_exact_with_other_owner_review():
    text = read_terms()
    for token in ["PERFORMED_SCOPE", "NON_RECOVERABLE_BOOKING_COST", "OTHER", "OWNER_REVIEW_REQUIRED"]:
        assert token in text
    assert "exact" in text.lower() or "exactly" in text.lower()


def test_non_recoverable_booking_cost_requires_evidence_and_booking_nexus():
    lower = read_terms().lower()
    assert "booking-specific" in lower
    assert "actually incurred" in lower or "irrevocably committed" in lower
    assert "evidence" in lower or "document" in lower


def test_external_reconciliation_offsets_every_recovery_route():
    lower = read_terms().lower()
    for token in ["supplier refund", "credit", "resale", "reuse", "insurance"]:
        assert token in lower
    assert "offset" in lower
    assert "recoverable" in lower and "asset" in lower


def test_external_reconciliation_forbids_generic_fee_markup_margin_and_opportunity_cost():
    lower = read_terms().lower()
    assert "force majeure fee" in lower
    assert "markup" in lower
    assert "margin" in lower
    assert "opportunity cost" in lower
    assert "generalized" in lower or "unsupported" in lower
    assert "forbidden" in lower or "no " in lower or "cannot" in lower


def test_actual_acquisition_or_commitment_cost_is_only_recovery_basis():
    lower = read_terms().lower()
    assert "actual acquisition" in lower or "actual acquisition/commitment" in lower
    assert "replacement-price" in lower or "replacement price" in lower
    assert "markup" in lower


def test_no_double_recovery_and_retention_cap_third_party_separation():
    lower = read_terms().lower()
    assert "double recovery" in lower
    assert "cancellation_retention_cap" in lower
    assert "third-party" in lower
    assert "outside" in lower and "cap" in lower
    assert "same" in lower and "item" in lower


def test_external_partial_performance_reconciles_performed_plus_eligible_exposure_then_refund():
    lower = read_terms().lower()
    assert "partial_performance" in lower
    assert "performed_scope" in lower
    assert "non_recoverable_booking_cost" in lower
    assert "offset" in lower
    assert "refund" in lower or "credit" in lower


def test_client_side_impediment_reuses_ordinary_window_rules():
    text = read_terms()
    lower = text.lower()
    assert "CLIENT_SIDE_IMPEDIMENT" in text
    assert "ordinary" in lower
    assert "cancellation" in lower
    assert "scope" in lower
    assert "controlling" in lower and ("date" in lower or "window" in lower)


def test_payment_default_is_excluded_from_client_side_impediment_route():
    text = read_terms()
    lower = text.lower()
    assert "PAYMENT_DEFAULT" in text or "payment default" in lower
    assert "CLIENT_SIDE_IMPEDIMENT" in text
    assert "excluded" in lower or "not" in lower


def test_partial_performance_is_modifier_not_regime():
    text = read_terms()
    lower = text.lower()
    assert "PARTIAL_PERFORMANCE" in text
    assert "modifier" in lower
    assert "not" in lower and "regime" in lower


def test_partial_performance_has_three_allocation_rules():
    text = read_terms()
    lower = text.lower()
    assert "unitized" in lower
    assert "direct attributable" in lower
    assert "shared" in lower and "indivisible" in lower
    assert "OWNER_REVIEW_REQUIRED" in text
    assert "objective" in lower
