from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "company/evochia/policies"
TERMS = POLICY_DIR / "terms_policy.md"


def read_terms() -> str:
    return TERMS.read_text(encoding="utf-8")


def lower_terms() -> str:
    return read_terms().lower()


def test_quote_validity_formula_and_late_quote_override_are_canonical():
    text = read_terms()
    lower = text.lower()
    assert "SERVICE_START" in text
    assert "as defined in the quote" in lower
    assert "issue_date + 7 calendar days" in text
    assert "SERVICE_START - 6 calendar days" in text
    assert "explicit `valid_until`" in text or "explicit valid_until" in lower
    assert "default_valid_until < issue_date" in text or "default validity is unusable" in lower
    assert "explicit later" in lower


def test_confirmation_payment_paths_are_time_banded():
    text = read_terms()
    lower = text.lower()
    assert "FIXED_CONFIRMED_BOOKING_VALUE" in text
    assert "30%" in text
    assert "100%" in text
    assert "more than 5" in lower
    assert "5 or fewer" in lower
    assert "confirmation" in lower


def test_t5_balance_applies_only_to_30_percent_path():
    text = read_terms()
    lower = text.lower()
    assert "BALANCE_DUE_DATE" in text
    assert "SERVICE_START - 5 calendar days" in text
    assert "30%" in text
    assert "no separate balance" in lower or "no later balance" in lower


def test_transport_gate_is_independent_from_quote_validity():
    text = read_terms()
    lower = text.lower()
    assert "TRANSPORT_UNVERIFIED" in text
    assert "confirmation" in lower and "block" in lower
    assert "valid" in lower and "independent" in lower


def test_payment_default_is_operational_state_not_impediment():
    text = read_terms()
    lower = text.lower()
    assert "PAYMENT_DEFAULT" in text
    assert "CURE_PENDING" in text
    assert "payment default" in lower
    assert "not" in lower and "impediment" in lower
    assert "CLIENT_SIDE_IMPEDIMENT" in text


def test_payment_default_cancellation_uses_exercise_date_tier():
    lower = lower_terms()
    assert "exercise" in lower
    assert "date" in lower
    assert "cancellation" in lower
    assert "tier" in lower
    assert "payment-default" not in lower or "penalty" in lower or "no second" in lower


def test_cure_uses_48_hours_banking_floor_and_service_start_cap():
    text = read_terms()
    assert "48 hours" in text or "48h" in text
    assert "BANKING_CLEARING_FLOOR" in text
    assert "later_of" in text
    assert "min(" in text
    assert "SERVICE_START" in text


def test_cure_does_not_force_new_exposure_and_requires_client_notification():
    lower = lower_terms()
    for token in [
        "supplier",
        "staffing",
        "travel",
        "accommodation",
        "equipment",
        "food-safety",
    ]:
        assert token in lower
    assert "does not require evochia to increase unrecoverable exposure" in lower
    assert "writing" in lower
    assert "client" in lower


def test_cancellation_tier_boundaries_are_exact():
    text = read_terms()
    assert "15+" in text and "10%" in text
    assert ("6–14" in text or "6-14" in text) and "30%" in text
    assert ("0–5" in text or "0-5" in text) and "100%" in text
    assert "first-match" in text.lower()


def test_cancellation_financial_fields_remain_separate():
    lower = lower_terms()
    for field in [
        "cancellation_charge",
        "collected_cancellation_amount",
        "refund_due",
        "uncollected_cancellation_balance",
    ]:
        assert field in lower
    assert "internal" in lower


def test_uncollected_cancellation_balance_is_not_client_safe_by_default():
    lower = lower_terms()
    assert "uncollected_cancellation_balance" in lower
    assert "client_safe" in lower
    assert "owner" in lower and "collection" in lower
    assert "not" in lower or "only" in lower


def test_scope_reduction_uses_removed_fixed_value_only():
    text = read_terms()
    lower = text.lower()
    assert "REMOVED_FIXED_VALUE" in text
    assert "fixed value before" in lower
    assert "revised fixed value" in lower
    assert "only" in lower and "removed" in lower


def test_scope_reduction_preserves_pricing_method_and_recalculates_staffing():
    lower = lower_terms()
    assert "same pricing methodology" in lower
    assert "non-scaling" in lower
    assert "staffing" in lower and "recalcul" in lower
    assert "proportional" in lower


def test_lower_day_of_attendance_does_not_reduce_fixed_value():
    lower = lower_terms()
    assert "attendance" in lower
    assert "does not" in lower or "does not by itself" in lower
    assert "fixed" in lower


def test_successive_scope_reductions_accumulate_without_double_charge():
    text = read_terms()
    lower = text.lower()
    assert "successive" in lower and "accumul" in lower
    assert "CANCELLATION_RETENTION_CAP" in text
    assert "100%" in text and "affected fixed" in lower
    assert "charged" in lower and "once" in lower


def test_third_party_ledger_is_outside_retention_cap_but_cannot_double_recover():
    lower = lower_terms()
    assert "third-party" in lower
    assert "separate" in lower and "ledger" in lower
    assert "outside" in lower and "cap" in lower
    assert "double recovery" in lower or "same item" in lower


def test_client_postponement_is_once_with_six_month_original_start_window():
    lower = lower_terms()
    assert "once per booking" in lower
    assert "6 calendar months" in lower or "six calendar months" in lower
    assert "original" in lower and "service_start" in lower


def test_postponement_extension_requires_explicit_expiry_without_reset():
    lower = lower_terms()
    assert "explicit" in lower and "expiry" in lower
    assert "does not reset" in lower or "history" in lower


def test_postponement_anti_reset_uses_max_of_request_and_final_tiers():
    text = read_terms()
    assert "max(" in text
    assert "tier_at_postponement_request" in text
    assert "tier_at_final_cancellation" in text


def test_postponed_booking_is_repriced_under_current_terms():
    lower = lower_terms()
    assert "current" in lower and "terms" in lower
    assert "reprice" in lower or "repric" in lower
    assert "credit" in lower
    assert "historical" in lower or "old pricing" in lower


def test_expired_postponement_credit_uses_request_date_tier():
    lower = lower_terms()
    assert "expire" in lower
    assert "postponement" in lower
    assert "request" in lower
    assert "tier" in lower


def test_excess_postponement_credit_is_refunded():
    lower = lower_terms()
    assert "excess" in lower and "credit" in lower
    assert "refund" in lower


def test_external_or_evochia_reschedule_does_not_consume_client_postponement():
    text = read_terms()
    lower = text.lower()
    assert "EXTERNAL_PERFORMANCE_IMPEDIMENT" in text
    assert "EVOCHIA_INABILITY_TO_PERFORM" in text
    assert "does not consume" in lower
    assert "client" in lower and "postponement" in lower
