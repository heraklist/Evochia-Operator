# Evochia Phase 13.3 Commercial Terms Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the owner-approved Phase 13.3 Evochia commercial-terms model across canonical policies, routing, client-safe artifact contracts, evals, policy-state metadata, and release readiness without allowing stale row states or duplicate canonical authority.

**Architecture:** The repository already models Evochia commercial behavior as canonical Markdown policies plus YAML routing/artifact/eval contracts and pytest conformance tests. Do not add a new commercial calculator/runtime subsystem. First create the complete Phase 13.3 RED conformance suite, then change policy bodies, then downstream projection/routing contracts, and only after a row-level closure audit change file-level status/approval metadata.

**Tech Stack:** Python 3.12, pytest 9.x, PyYAML 6.x, jsonschema 4.x, Markdown policy files, YAML routing/eval/state contracts.

**Spec:** `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design-v2.md`

**Decision register:** `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-decisions.md`

## Global Constraints

- Implement D-001 through D-051 exactly, plus the two owner-approved implementation corrections recorded in Task 1 as D-052/D-053.
- Preserve canonical impediment names exactly: `EXTERNAL_PERFORMANCE_IMPEDIMENT`, `EVOCHIA_INABILITY_TO_PERFORM`, `CLIENT_SIDE_IMPEDIMENT`.
- Payment default remains an operational state, never an impediment regime.
- `PARTIAL_PERFORMANCE` remains a calculation modifier after classification, never a fourth regime.
- `SERVICE_START` remains the first scheduled service date **as defined in the quote**.
- Cancellation tiers remain 15+ = 10%, 6–14 = 30%, 0–5 = 100%.
- `CANCELLATION_RETENTION_CAP` applies only to affected fixed-scope retention; eligible separately treated third-party actual-cost items remain a separate ledger.
- Enforce no double recovery, no markup, actual acquisition/commitment cost, and offsets for refunds/credits/reuse/resale/insurance/recoverable assets.
- `uncollected_cancellation_balance` is INTERNAL by default and must not leak to CLIENT_SAFE outputs absent explicit owner collection authorization.
- `TRANSPORT_UNVERIFIED` blocks booking confirmation independently of quote validity.
- Legal identity is closed: sole proprietorship / `ατομική επιχείρηση`; brand `Evochia`; trade name `Evochia Food & Hospitality Group`; never characterize Evochia as a company/corporation/corporate group/group of companies.
- Household engagements use their own recurring billing/termination framework; event T-5 and 10/30/100 rules do not apply by default.
- There is no global peak-date surcharge and no global household-chef rate card.
- **Tests before policies:** Tasks 2–5 must be committed and verified RED before Task 6 modifies any file under `company/evochia/policies/`.
- **Row closure before file status:** Tasks 6–8 modify body-level rules only. File headers, `policy_state_contract.yaml`, approval references, and release readiness are reconciled only in Task 9 after explicit stale-row scanning.
- Preserve genuinely unrelated OPEN/`NEEDS_OWNER_APPROVAL` rows; do not force full approval merely to close Phase 13.3.
- Do not modify `staffing_policy.md` unless a failing Phase 13.3 test proves an actual contradiction; existing transport/uplift authority should be referenced, not duplicated.
- Do not rewrite historical proposals as policy authority.
- Full CI-equivalent verification is required before completion.

---

# 1. Repository Mapping and Change Boundaries

## Canonical design/governance

| File | Responsibility | Phase 13.3 disposition |
| --- | --- | --- |
| `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design.md` | superseded v1 candidate | mark unequivocally superseded; no canonical authority |
| `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design-v2.md` | owner-approved canonical design | apply two approved non-blocking corrections and mark owner-approved |
| `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-decisions.md` | owner-decision authority | append D-052/D-053; preserve supersession history |

## Tests created before policy edits

| File | Responsibility |
| --- | --- |
| `tests/evochia/test_phase13_3_terms_lifecycle.py` | acceptance criteria 1–36: validity, confirmation, payment, cancellation, scope reduction, postponement |
| `tests/evochia/test_phase13_3_impediment_economics.py` | criteria 37–77: threshold, classification, mitigation, regime economics, partial performance |
| `tests/evochia/test_phase13_3_projection_and_service_models.py` | criteria 78–91: peak, household, legal identity, routing, CLIENT_SAFE projection |
| `tests/evochia/test_phase13_3_cross_file_sync.py` | criteria 92–100: stale row closure, file states, readiness |
| `tests/evochia/test_phase13_2_owner_lock.py` | remove stale Phase 13.2 expectations that explicitly require now-closed rows to remain OPEN |

## Policy bodies

| File | Responsibility | Expected file status after row audit |
| --- | --- | --- |
| `company/evochia/policies/terms_policy.md` | canonical terms lifecycle + impediment economics | `PARTIALLY_APPROVED` because final legal drafting remains outside this commercial design |
| `company/evochia/policies/commercial_policy.md` | commercial invariants + peak/household boundaries | candidate for `APPROVED` after Task 9 if no unresolved row remains |
| `company/evochia/policies/current_rates.md` | rate authority; peak/household no-global-card rules | `PARTIALLY_APPROVED` because undefined service families/public-price-list policy remain unresolved |
| `company/evochia/policies/company_profile.md` | entity/brand/trade-name facts | `PARTIALLY_APPROVED` if unrelated service-taxonomy rows remain unresolved |
| `company/evochia/policies/staffing_policy.md` | staffing/transport/uplift authority | unchanged unless contradiction is proven |

## Downstream contracts

| File | Responsibility |
| --- | --- |
| `skills/chef-ai-pro-business/references/routing.yaml` | proposal routing + confirmation blockers |
| `templates/artifacts/client_artifact_contracts.yaml` | CLIENT_SAFE forbidden/internal fields |
| `references/artifacts/rendering_policy.md` | projection-before-rendering boundary |
| `evals/e2e/e2e_cases.yaml` | static end-to-end policy behavior cases |
| `evals/artifacts/artifact_cases.yaml` | client-safe artifact projection cases |

## State/release

| File | Responsibility |
| --- | --- |
| `company/evochia/policies/policy_state_contract.yaml` | file-level state/metadata after row closure |
| `release/release_readiness.yaml` | truthful Phase 13.3 closure and remaining blockers |

---

### Task 1: Normalize Canonical Design Authority and Record the Two Approved Corrections

**Files:**
- Modify: `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design.md`
- Modify: `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design-v2.md`
- Modify: `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-decisions.md`

**Interfaces:**
- Consumes: owner approval of `design-v2.md` plus the two non-blocking corrections in the approval message.
- Produces: one unambiguous canonical spec; D-052/D-053 become durable inputs for all later tests and policy changes.

- [ ] **Step 1: Mark v1 as superseded, not approved**

Replace its status metadata with:

```markdown
**Status:** `SUPERSEDED`
**Superseded by:** `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design-v2.md`
**Authority:** `NON_CANONICAL_HISTORICAL_DESIGN`
```

Remove/replace the stale phrase `USER-APPROVED DESIGN BASE / CANONICAL SPEC CANDIDATE` so no search result can present v1 as current authority.

- [ ] **Step 2: Append D-052 and D-053 without rewriting D-048/D-049 history**

Append:

```markdown
| D-052 | Supersedes the structured-field portion of D-048. A quote-specific peak-date adjustment must record exactly these canonical evidence fields: `reason`, `amount_or_method`, `date_specific_basis`, `costs_already_covered_elsewhere`, `double_count_check`, and `owner_decision/reference`. `date_specific_basis` must establish why the specific service date itself creates scarcity/demand/availability justification; geography or yacht/island disruption alone is not sufficient. `double_count_check` must verify that the same causal burden is not also recovered through yacht/island/remote uplift or another line. | 2026-09-03 | LOCKED |
| D-053 | Extends D-049. The household required field previously named `rate_review` is implemented as `rate_review_and_escalation`, and the agreement must define both when review occurs and the mechanism/rule by which a rate may change. A bare right to review with no adjustment mechanism is insufficient. | 2026-09-03 | LOCKED |
```

Update D-048 status to `SUPERSEDED IN STRUCTURED-FIELD SCHEMA BY D-052` while retaining its no-global-surcharge and causal-separation substance; update D-049 status to `LOCKED; EXTENDED BY D-053`.

- [ ] **Step 3: Apply the same correction to v2 and mark it owner-approved**

Peak structured fields in v2 must become exactly:

```text
reason
amount_or_method
date_specific_basis
costs_already_covered_elsewhere
double_count_check
owner_decision/reference
```

Household required fields must include:

```text
rate_review_and_escalation
```

instead of a bare `rate_review`.

Set v2 status to:

```markdown
**Status:** `OWNER-APPROVED CANONICAL SPEC`
```

and state that D-052/D-053 are implementation clarifications approved with the spec, not a new design-review cycle.

- [ ] **Step 4: Verify there is only one current canonical spec**

Run:

```bash
rg -n "USER-APPROVED DESIGN BASE|CANONICAL SPEC CANDIDATE|OWNER-APPROVED CANONICAL SPEC|SUPERSEDED" docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design*.md
```

Expected:
- v1 contains `SUPERSEDED` and points to v2;
- v1 does not contain the stale user-approved/canonical-candidate claim;
- v2 contains `OWNER-APPROVED CANONICAL SPEC`.

- [ ] **Step 5: Commit governance normalization**

```bash
git add docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design.md \
        docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design-v2.md \
        docs/superpowers/specs/2026-09-03-evochia-commercial-terms-decisions.md
git commit -m "docs: finalize Phase 13.3 canonical commercial authority"
```

---

### Task 2: RED — Add Quote, Payment, Cancellation, Scope and Postponement Contract Tests

**Files:**
- Create: `tests/evochia/test_phase13_3_terms_lifecycle.py`
- Modify: `tests/evochia/test_phase13_2_owner_lock.py`

**Interfaces:**
- Consumes: v2 + D-001–D-053.
- Produces: failing tests for acceptance criteria 1–36 before any policy body is modified.

- [ ] **Step 1: Create the lifecycle test file**

Use this structure:

```python
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "company/evochia/policies"
TERMS = POLICY_DIR / "terms_policy.md"
COMMERCIAL = POLICY_DIR / "commercial_policy.md"
RATES = POLICY_DIR / "current_rates.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_quote_validity_and_confirmation_payment_contract():
    terms = read(TERMS)
    required = [
        "issue_date + 7 calendar days",
        "SERVICE_START - 6 calendar days",
        "explicit `valid_until`",
        "30%",
        "100%",
        "5 or fewer",
        "BALANCE_DUE_DATE",
        "SERVICE_START - 5 calendar days",
        "TRANSPORT_UNVERIFIED",
    ]
    for token in required:
        assert token in terms
    assert "default validity is unusable" in terms.lower() or "default_valid_until < issue_date" in terms


def test_payment_default_and_cure_are_operational_not_impediment():
    terms = read(TERMS)
    assert "PAYMENT_DEFAULT" in terms
    assert "CURE_PENDING" in terms
    assert "48 hours" in terms or "48h" in terms
    assert "BANKING_CLEARING" in terms
    assert "min(" in terms and "SERVICE_START" in terms
    assert "payment default" in terms.lower() and "not" in terms.lower() and "impediment" in terms.lower()
    assert "date" in terms.lower() and "exercis" in terms.lower() and "cancellation" in terms.lower()
    assert "writing" in terms.lower() and "client" in terms.lower()


def test_cancellation_tiers_and_financial_fields_are_canonical():
    terms = read(TERMS)
    for token in ["15+", "10%", "6–14", "30%", "0–5", "100%"]:
        assert token in terms
    for field in [
        "cancellation_charge",
        "collected_cancellation_amount",
        "refund_due",
        "uncollected_cancellation_balance",
        "CANCELLATION_RETENTION_CAP",
    ]:
        assert field.lower() in terms.lower()


def test_scope_reduction_uses_removed_value_and_single_charge_invariant():
    terms = read(TERMS)
    assert "REMOVED_FIXED_VALUE" in terms
    assert "fixed value before" in terms.lower()
    assert "revised fixed value" in terms.lower()
    assert "same pricing methodology" in terms.lower()
    assert "staffing" in terms.lower() and "recalcul" in terms.lower()
    assert "lower" in terms.lower() and "attendance" in terms.lower() and "does not" in terms.lower()
    assert "each" in terms.lower() and "fixed" in terms.lower() and "charged" in terms.lower() and "once" in terms.lower()
    assert "100%" in terms and "affected fixed" in terms.lower()
    assert "third-party" in terms.lower() and "outside" in terms.lower() and "cap" in terms.lower()
    assert "double recovery" in terms.lower()


def test_client_postponement_has_one_use_six_month_window_and_anti_reset():
    terms = read(TERMS)
    required = [
        "once per booking",
        "6 calendar months",
        "original",
        "explicit new expiry",
        "max(",
        "tier_at_postponement_request",
        "tier_at_final_cancellation",
        "current",
        "excess credit",
    ]
    for token in required:
        assert token.lower() in terms.lower()
    assert "does not consume" in terms.lower() and "client" in terms.lower() and "postponement" in terms.lower()
```

- [ ] **Step 2: Encode all acceptance criteria 1–36 explicitly**

Keep one assertion path per criterion; the following mapping is mandatory:

```text
1-3   -> test_quote_validity_and_confirmation_payment_contract
4-7   -> same test (30/100/T-5/transport)
8-14  -> test_payment_default_and_cure_are_operational_not_impediment
15-19 -> test_cancellation_tiers_and_financial_fields_are_canonical
20-28 -> test_scope_reduction_uses_removed_value_and_single_charge_invariant
29-36 -> test_client_postponement_has_one_use_six_month_window_and_anti_reset
```

Add distinct assertions for:
- 15-day, 6-day and 5-day boundary tokens;
- `uncollected_cancellation_balance` CLIENT_SAFE suppression reference;
- staffing-trigger recalculation rather than proportional scaling;
- separate third-party ledger not constrained by retention cap;
- same-item double-recovery prohibition;
- expired postponement credit uses request-date tier;
- external/Evochia reschedule does not consume client postponement.

- [ ] **Step 3: Rewrite stale Phase 13.2 test expectations before policy changes**

In `tests/evochia/test_phase13_2_owner_lock.py` remove the test that requires these strings to remain OPEN:

```text
balance-payment timing
cancellation/refundability
quote validity
peak-date
household-chef global rate card
```

Replace it with a historical-boundary test:

```python
def test_phase13_2_history_does_not_require_phase13_3_rows_to_remain_open():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    terms = read(POLICY_DIR / "terms_policy.md")
    combined = "\n".join([commercial, rates, terms]).lower()
    assert "partially_approved" in combined or "partially approved" in combined
    # Phase 13.3 owns the current row-closure expectations; this historical
    # test must not force closed rows back to OPEN.
```

Also replace the all-files-Phase13.2 metadata assertion with a test that accepts the current contract as authority and checks metadata consistency rather than hardcoding `owner-approval-2026-09-03-phase13.2` for every policy.

- [ ] **Step 4: Run the lifecycle tests and verify RED**

Run:

```bash
python -m pytest -q tests/evochia/test_phase13_3_terms_lifecycle.py tests/evochia/test_phase13_2_owner_lock.py
```

Expected: new Phase 13.3 lifecycle assertions FAIL because current policy files still declare balance/cancellation/validity/peak/household rows OPEN and lack the canonical formulas/workflows. Failures must be assertion failures caused by missing Phase 13.3 policy text, not import/syntax errors.

- [ ] **Step 5: Commit RED lifecycle contract**

```bash
git add tests/evochia/test_phase13_3_terms_lifecycle.py tests/evochia/test_phase13_2_owner_lock.py
git commit -m "test: add Phase 13.3 commercial lifecycle contract"
```

---

### Task 3: RED — Add Full Impediment-Economics Contract Tests

**Files:**
- Create: `tests/evochia/test_phase13_3_impediment_economics.py`

**Interfaces:**
- Consumes: D-001, D-012–D-014, D-036–D-047, D-051.
- Produces: failing tests for acceptance criteria 37–77 before policy edits.

- [ ] **Step 1: Create the impediment-economics test file**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TERMS = ROOT / "company/evochia/policies/terms_policy.md"


def read_terms() -> str:
    return TERMS.read_text(encoding="utf-8")


def test_impediment_threshold_and_single_classification():
    text = read_terms()
    for token in [
        "EXTERNAL_PERFORMANCE_IMPEDIMENT",
        "EVOCHIA_INABILITY_TO_PERFORM",
        "CLIENT_SIDE_IMPEDIMENT",
        "OWNER_REVIEW_REQUIRED",
        "objectively verifiable",
    ]:
        assert token.lower() in text.lower()
    for excluded in ["increased cost", "fear", "preference", "lower attendance"]:
        assert excluded in text.lower()
    assert "economically" in text.lower() or "commercially" in text.lower()
    assert "favorable" in text.lower() or "favourable" in text.lower()


def test_four_workflow_outcomes_and_mitigation_cost_boundary():
    text = read_terms()
    for token in [
        "PERFORM_OR_MITIGATE",
        "REPLACEMENT_PERFORMANCE",
        "RESCHEDULE",
        "TERMINATE_AND_RECONCILE",
        "material incremental",
        "cost allocation",
    ]:
        assert token.lower() in text.lower()


def test_evochia_inability_economics():
    text = read_terms()
    section = text[text.index("EVOCHIA_INABILITY_TO_PERFORM"):]
    assert "full refund" in section.lower() or "100%" in section
    assert "unperformed" in section.lower()
    assert "10%" in section and "30%" in section and "100%" in section
    assert "do not apply" in section.lower() or "does not apply" in section.lower()
    for token in ["sunk", "margin", "opportunity cost", "client acceptance", "notify"]:
        assert token in section.lower()
    assert "consequential" in section.lower() and "not automatically" in section.lower()


def test_external_impediment_actual_exposure_and_evidence_gate():
    text = read_terms()
    for token in [
        "actual-exposure",
        "PERFORMED_SCOPE",
        "NON_RECOVERABLE_BOOKING_COST",
        "OTHER",
        "OWNER_REVIEW_REQUIRED",
        "refund",
        "credit",
        "resale",
        "reuse",
        "insurance",
    ]:
        assert token.lower() in text.lower()
    assert "force majeure fee" in text.lower()
    assert "no" in text.lower() and "markup" in text.lower()
    assert "actual acquisition" in text.lower() or "actual acquisition/commitment" in text.lower()


def test_no_double_recovery_and_separate_retention_cap():
    text = read_terms().lower()
    assert "double recovery" in text
    assert "markup" in text
    assert "cancellation_retention_cap" in text
    assert "third-party" in text
    assert "outside" in text and "cap" in text
    assert "same" in text and "item" in text and "recover" in text


def test_client_side_impediment_reuses_normal_rules_and_excludes_payment_default():
    text = read_terms().lower()
    assert "client_side_impediment" in text
    assert "cancellation" in text and "scope" in text
    assert "payment default" in text
    assert "not" in text and "route" in text


def test_partial_performance_is_modifier_with_three_allocation_rules():
    text = read_terms()
    assert "PARTIAL_PERFORMANCE" in text
    assert "not" in text.lower() and "regime" in text.lower()
    for token in ["unitized", "direct attributable", "shared", "indivisible", "OWNER_REVIEW_REQUIRED"]:
        assert token.lower() in text.lower()
```

- [ ] **Step 2: Map criteria 37–77 to explicit assertions**

Mandatory mapping:

```text
37-45 -> threshold/classification/workflow/mitigation tests
46-54 -> Evochia inability test
55-70 -> external impediment + no-double-recovery tests
71-72 -> client-side test
73-77 -> partial-performance test
```

Ensure the tests separately prove:
- replacement materially corresponds to contracted scope;
- replacement requires client acceptance;
- prompt notification at material risk, not only final failure;
- client consequential costs are not automatically reimbursed;
- `OTHER` always requires owner review;
- recoverable asset value is an offset, not loss;
- generic force-majeure fee is forbidden;
- lost margin/opportunity cost/general admin are not external client-recoverable exposure;
- external partial performance performs `performed + eligible actual exposure - recoveries`, then refund/credit.

- [ ] **Step 3: Verify RED**

```bash
python -m pytest -q tests/evochia/test_phase13_3_impediment_economics.py
```

Expected: FAIL against current `terms_policy.md`, which presently contains only a short good-faith external-disruption principle and no regime economics.

- [ ] **Step 4: Commit RED impediment contract**

```bash
git add tests/evochia/test_phase13_3_impediment_economics.py
git commit -m "test: add Phase 13.3 impediment economics contract"
```

---

### Task 4: RED — Add Peak, Household, Legal Identity and CLIENT_SAFE Projection Tests

**Files:**
- Create: `tests/evochia/test_phase13_3_projection_and_service_models.py`
- Modify later only after RED verification: none of the policy/contract files in this task.

**Interfaces:**
- Consumes: D-027, D-031, D-048–D-053.
- Produces: failing tests for acceptance criteria 78–91.

- [ ] **Step 1: Create the projection/service-model test file**

```python
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
    assert "no global peak-date surcharge" in joined.lower()
    for field in [
        "reason",
        "amount_or_method",
        "date_specific_basis",
        "costs_already_covered_elsewhere",
        "double_count_check",
        "owner_decision/reference",
    ]:
        assert field in joined
    assert "island" in joined.lower() and "yacht" in joined.lower()
    assert "distinct" in joined.lower() and "cause" in joined.lower()


def test_household_has_own_recurring_framework_and_all_required_fields():
    commercial = read(POLICY_DIR / "commercial_policy.md")
    rates = read(POLICY_DIR / "current_rates.md")
    joined = "\n".join([commercial, rates])
    assert "no global household" in joined.lower()
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
    assert "recurring" in joined.lower()
    assert "t-5" in joined.lower() and "not" in joined.lower() and "default" in joined.lower()
    assert "10/30/100" in joined or "10%/30%/100%" in joined


def test_legal_identity_is_closed_and_company_group_characterization_is_forbidden():
    profile = read(POLICY_DIR / "company_profile.md")
    lower = profile.lower()
    assert "ατομική επιχείρηση" in profile
    assert "evochia" in lower
    assert "evochia food & hospitality group" in lower
    assert "διακρι" in lower
    assert "company" in lower and "must not" in lower or "prohibited" in lower
    assert "runtime_resolved" in lower
    assert "fail" in lower and "closed" in lower


def test_routing_and_artifact_contracts_enforce_confirmation_and_client_safe_boundaries():
    routing = yaml.safe_load(read(ROUTING))
    route = next(r for r in routing["routes"] if r["route_id"] == "client_safe_proposal")
    serialized = str(route).lower()
    assert "transport" in serialized and "confirmation" in serialized
    assert "legal" in serialized and "binding" in serialized
    assert "household" in serialized
    assert "client" in serialized and "safe" in serialized

    contracts = yaml.safe_load(read(CLIENT_CONTRACTS))
    forbidden = set(contracts["artifacts"]["proposal"]["forbidden_internal_fields"])
    assert "uncollected_cancellation_balance" in forbidden
    assert "internal_margin" in forbidden
    assert "opportunity_cost" in forbidden
```

- [ ] **Step 2: Add eval-presence assertions**

Add tests requiring new eval IDs:

```text
phase13_3_payment_default_cure
phase13_3_external_impediment_reconciliation
phase13_3_evochia_inability_refund
phase13_3_client_side_impediment
phase13_3_peak_date_overlap_guard
phase13_3_household_recurring_terms
phase13_3_client_safe_uncollected_balance_guard
phase13_3_binding_identity_fail_closed
```

Assert these IDs exist across `evals/e2e/e2e_cases.yaml` and `evals/artifacts/artifact_cases.yaml` as appropriate.

- [ ] **Step 3: Verify RED**

```bash
python -m pytest -q tests/evochia/test_phase13_3_projection_and_service_models.py
```

Expected: FAIL because current policies still mark peak/household/legal identity unresolved and current proposal contract does not forbid `uncollected_cancellation_balance` explicitly.

- [ ] **Step 4: Commit RED projection/service-model contract**

```bash
git add tests/evochia/test_phase13_3_projection_and_service_models.py
git commit -m "test: add Phase 13.3 projection and service-model contract"
```

---

### Task 5: RED — Add Cross-File Row Closure, Policy-State and Release-Readiness Tests

**Files:**
- Create: `tests/evochia/test_phase13_3_cross_file_sync.py`

**Interfaces:**
- Consumes: D-032, D-034, D-051 and the explicit row-before-file-status requirement.
- Produces: failing tests for criteria 92–100.

- [ ] **Step 1: Create explicit stale-row closure tests**

```python
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
    stale_patterns = [
        "balance-payment timing",
        "cancellation/refundability windows",
        "standard quote validity",
        "peak-date pricing/surcharge policy",
        "household-chef global rate card remains open",
        "evochia food & hospitality group | `needs_owner_approval`",
    ]
    joined = "\n".join(files.values())
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


def test_file_statuses_are_derived_after_row_closure_not_before():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    assert state["policies"]["commercial_policy.md"]["status"] == "APPROVED"
    assert state["policies"]["terms_policy.md"]["status"] == "PARTIALLY_APPROVED"
    assert state["policies"]["current_rates.md"]["status"] == "PARTIALLY_APPROVED"
    assert state["policies"]["company_profile.md"]["status"] == "PARTIALLY_APPROVED"
    assert state["policies"]["staffing_policy.md"]["status"] == "PARTIALLY_APPROVED"


def test_release_readiness_closes_phase13_3_rows_without_claiming_full_release():
    readiness = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert readiness["commercial_policy_readiness"] == "PARTIALLY_APPROVED"
    assert readiness["final_release_status"] == "BLOCKED"
    assert readiness["may_claim_production_ready"] is False
    serialized = str(readiness).lower()
    assert "phase13.3" in serialized
    for stale in [
        "does not close balance timing",
        "does not close cancellation/refundability",
        "does not close standard quote validity",
        "does not close peak-date policy",
        "does not close household-chef global rate card",
    ]:
        assert stale not in serialized
```

- [ ] **Step 2: Assert row closure before metadata promotion**

Add a helper that refuses to treat a file as `APPROVED` if its text contains `OPEN` or `NEEDS_OWNER_APPROVAL`:

```python
def assert_approved_file_has_no_open_rows(name: str, status: str) -> None:
    text = read(name)
    if status == "APPROVED":
        assert "`OPEN`" not in text
        assert "NEEDS_OWNER_APPROVAL" not in text
```

Apply it to every policy entry from `policy_state_contract.yaml`.

This test is the executable form of **row closure before file status**.

- [ ] **Step 3: Verify RED**

```bash
python -m pytest -q tests/evochia/test_phase13_3_cross_file_sync.py
```

Expected: FAIL because current four files still carry stale OPEN rows and state/release metadata still describes the Phase 13.2 unresolved set.

- [ ] **Step 4: Run all new Phase 13.3 tests together and confirm no policy file has changed yet**

```bash
python -m pytest -q \
  tests/evochia/test_phase13_3_terms_lifecycle.py \
  tests/evochia/test_phase13_3_impediment_economics.py \
  tests/evochia/test_phase13_3_projection_and_service_models.py \
  tests/evochia/test_phase13_3_cross_file_sync.py

git diff -- company/evochia/policies
```

Expected:
- pytest: RED for missing Phase 13.3 implementation;
- `git diff -- company/evochia/policies`: empty.

Do not start Task 6 unless both conditions hold.

- [ ] **Step 5: Commit RED cross-file contract**

```bash
git add tests/evochia/test_phase13_3_cross_file_sync.py
git commit -m "test: add Phase 13.3 cross-file closure contract"
```

---

### Task 6: GREEN — Implement Canonical Terms Lifecycle and Regime Economics in `terms_policy.md`

**Files:**
- Modify body only: `company/evochia/policies/terms_policy.md`
- Test: `tests/evochia/test_phase13_3_terms_lifecycle.py`
- Test: `tests/evochia/test_phase13_3_impediment_economics.py`

**Interfaces:**
- Consumes: all lifecycle/regime decisions and the RED tests from Tasks 2–3.
- Produces: canonical terms authority; does **not** yet change file status/header approval metadata.

- [ ] **Step 1: Replace the stale booking/deposit and balance sections with timing-aware confirmation rules**

Required canonical content:

```text
SERVICE_START = first scheduled service date as defined in the quote

if confirmation_date > SERVICE_START - 5 calendar days:
    confirmation_payment = 30% of FIXED_CONFIRMED_BOOKING_VALUE
    BALANCE_DUE_DATE = SERVICE_START - 5 calendar days
else:
    confirmation_payment = 100% of FIXED_CONFIRMED_BOOKING_VALUE
    no separate balance stage
```

Retain written acceptance and transport/legal confirmation gates.

- [ ] **Step 2: Add quote validity and late-quote rule**

Canonical text/formula:

```text
valid_until = min(issue_date + 7 calendar days, SERVICE_START - 6 calendar days)
```

If the default gives `valid_until < issue_date`, the default is unusable and an explicit later `valid_until` override is required. Shorter overrides are allowed; longer validity must be an explicit date.

- [ ] **Step 3: Add payment-default cure state without creating a regime**

```text
PAYMENT_DEFAULT -> CURE_PENDING
base_cure_deadline = notice + 48 hours
candidate = later_of(base_cure_deadline, BANKING_CLEARING_FLOOR)
CURE_DEADLINE = min(candidate, SERVICE_START)
```

State explicitly:
- payment default is not `CLIENT_SIDE_IMPEDIMENT`;
- if Evochia exercises cancellation, tier is determined on exercise date;
- Evochia need not increase unrecoverable exposure during cure;
- if it pauses/refuses new exposure, it notifies the client promptly in writing.

- [ ] **Step 4: Add ordinary cancellation, tripartite/quad financial fields and cap definition**

```text
15+ days -> 10%
6-14 days -> 30%
0-5 days -> 100%
CANCELLATION_RETENTION_CAP = 100% of affected fixed scope
```

Define once:

```text
cancellation_charge
collected_cancellation_amount
refund_due
uncollected_cancellation_balance
```

Make `uncollected_cancellation_balance` INTERNAL by default.

- [ ] **Step 5: Add scope-reduction and cumulative-retention rules**

```text
REMOVED_FIXED_VALUE = fixed value before approved change - revised fixed value
scope_reduction_charge = tier_on_approved_reduction_date * REMOVED_FIXED_VALUE
```

Include:
- same confirmed pricing methodology;
- non-scaling fixed lines remain unchanged unless explicitly revised;
- staffing triggers recalculated, not proportionally scaled;
- written approval required;
- day-of lower attendance does not reduce fixed value by itself;
- successive reductions accumulate;
- each fixed-scope unit charged at most once;
- separate eligible third-party ledger may sit outside retention cap;
- same item cannot be recovered in both ledgers.

- [ ] **Step 6: Add full postponement state model**

Include exactly:

```text
one client postponement per booking
replacement date <= original SERVICE_START + 6 calendar months
written discretionary extension requires explicit new expiry
anti_reset_tier = max(tier_at_postponement_request, tier_at_final_cancellation)
repricing = current terms/rates for new date/scope
unused expired credit -> tier_at_postponement_request
excess collected credit after settlement -> refund
```

Evochia/external reschedules do not consume client postponement, six-month window, or anti-reset.

- [ ] **Step 7: Replace the short force-majeure section with the full impediment model**

Canonical threshold:

```text
objectively verifiable material event affecting performance
```

Not sufficient alone:

```text
increased cost
fear
preference
convenience
anticipated or actual lower attendance
```

Canonical regimes:

```text
EXTERNAL_PERFORMANCE_IMPEDIMENT
EVOCHIA_INABILITY_TO_PERFORM
CLIENT_SIDE_IMPEDIMENT
```

Hybrid/disputed/insufficient cause -> `OWNER_REVIEW_REQUIRED`.

Outcomes:

```text
PERFORM_OR_MITIGATE
REPLACEMENT_PERFORMANCE
RESCHEDULE
TERMINATE_AND_RECONCILE
```

Mitigation material incremental cost requires explicit cost-allocation agreement before commitment.

- [ ] **Step 8: Add regime economics**

For `EVOCHIA_INABILITY_TO_PERFORM`:

```text
unperformed fixed scope already collected -> 100% refund/credit
10/30/100 tiers -> not applicable to that unperformed scope
Evochia sunk costs/margin/opportunity cost -> Evochia absorbs
client independent consequential costs -> not automatically reimbursable
replacement -> materially corresponding scope + client acceptance
notification -> promptly when material risk becomes known
```

For `EXTERNAL_PERFORMANCE_IMPEDIMENT`:

```text
client allocation = PERFORMED_SCOPE + eligible NON_RECOVERABLE_BOOKING_COST
OTHER -> OWNER_REVIEW_REQUIRED
remaining collected amount -> refund/credit
```

Evidence/recovery rules:

```text
booking-specific
actually incurred or irrevocably committed
evidenced
net of refunds/credits/resale/reuse/insurance/recoverable asset value
actual acquisition/commitment cost only
no generic force-majeure fee
no markup
no margin
no opportunity cost
no generalized unsupported admin
no double recovery
```

For `CLIENT_SIDE_IMPEDIMENT`: route to ordinary cancellation/partial-cancellation/scope rules for controlling date/window; payment default remains excluded.

- [ ] **Step 9: Add `PARTIAL_PERFORMANCE` as one modifier with three allocation rules**

```text
1. unitized performed service
2. direct attributable costs
3. shared/indivisible fixed lines -> declared basis, else objective deterministic basis, else OWNER_REVIEW_REQUIRED
```

Never present it as a fourth regime.

- [ ] **Step 10: Preserve a genuinely unresolved legal-drafting row**

The commercial model is owner-approved, but final contract-law wording/legal review is outside this design. Keep a narrowly worded row such as:

```markdown
**Still unresolved / outside Phase 13.3:** final jurisdiction-specific legal drafting/review of binding contract language. This does not reopen the approved commercial economics or workflow rules above.
```

Do not keep stale OPEN rows for balance, cancellation windows, deposit treatment, quote validity, peak-date commercial policy, household global rate card, or regime economics.

- [ ] **Step 11: Run lifecycle and impediment tests**

```bash
python -m pytest -q \
  tests/evochia/test_phase13_3_terms_lifecycle.py \
  tests/evochia/test_phase13_3_impediment_economics.py
```

Expected: PASS for terms-owned assertions. Cross-file/status tests may remain RED until later tasks.

- [ ] **Step 12: Commit terms body implementation**

```bash
git add company/evochia/policies/terms_policy.md
git commit -m "feat: implement Phase 13.3 Evochia terms lifecycle"
```

---

### Task 7: GREEN — Close Commercial, Rates and Identity Rows Without Changing File Status Yet

**Files:**
- Modify body only: `company/evochia/policies/commercial_policy.md`
- Modify body only: `company/evochia/policies/current_rates.md`
- Modify body only: `company/evochia/policies/company_profile.md`
- Test: `tests/evochia/test_phase13_3_projection_and_service_models.py`
- Test: `tests/evochia/test_phase13_3_cross_file_sync.py`

**Interfaces:**
- Consumes: canonical terms authority from Task 6 plus D-045–D-053.
- Produces: row-level commercial/rate/identity closure. File headers remain unchanged until Task 9.

- [ ] **Step 1: Update `commercial_policy.md` to reference terms authority instead of duplicating formulas**

Add/retain concise invariants:

```text
no double recovery
no markup on reimbursable exposure
actual acquisition/commitment cost only
offset recoveries/reusable value
cancellation retention cap != separate eligible third-party ledger
```

Reference `terms_policy.md` for payment/cancellation/postponement/regime formulas.

Remove stale statements that balance timing, cancellation/refundability, standard quote validity, peak-date policy, household global rate card, or legal identity are still awaiting owner approval.

- [ ] **Step 2: Implement exact peak-date structured evidence schema**

Use exactly these internal fields:

```text
reason
amount_or_method
date_specific_basis
costs_already_covered_elsewhere
double_count_check
owner_decision/reference
```

Rules:
- no global peak-date surcharge;
- `date_specific_basis` must document why this specific date creates scarcity/demand/availability justification;
- geography/yacht/island disruption alone cannot be the positive peak basis;
- `double_count_check` must test peak against yacht/island/remote and other charges;
- peak and location/yacht uplift may coexist only for genuinely distinct documented causes.

- [ ] **Step 3: Implement household recurring framework in `commercial_policy.md`**

No global rate card. Every household quote/agreement requires:

```text
scope
service_days_and_hours
extra_day_and_hour_rules
guest_event_rules
food_and_pass_through_treatment
travel
billing_cycle
termination_and_notice
rate_review_and_escalation
absence_or_non_use
```

State explicitly:

```text
Household recurring framework != one-off event framework.
T-5 balance and 10/30/100 cancellation tiers do not apply by default.
```

`rate_review_and_escalation` must define both review timing and rate-adjustment mechanism.

- [ ] **Step 4: Close stale peak/household rows in `current_rates.md` while preserving evidence boundaries**

Replace household section state with:

```text
APPROVED_OWNER_DECISION: no global household-chef rate card; quote-specific only.
```

Keep historical €6,500/month etc. as `PROPOSAL_SPECIFIC_EVIDENCE`, not current rate authority.

Replace peak OPEN row with:

```text
APPROVED_OWNER_DECISION: no global peak-date surcharge; quote-specific adjustment only under commercial_policy.md evidence schema.
```

Preserve genuinely open rows:

```text
any service family/rate not explicitly defined
future public-facing price-list policy
```

- [ ] **Step 5: Close legal/entity row in `company_profile.md`**

Canonical identity table must distinguish:

```text
Legal form: individual / sole proprietorship / ατομική επιχείρηση -> APPROVED_OWNER_DECISION
Brand: Evochia -> approved
Trade name / διακριτικός τίτλος: Evochia Food & Hospitality Group -> APPROVED_OWNER_DECISION
```

Add explicit prohibition:

```text
The trade name does not create or imply a company, corporation, corporate group, or group of companies.
Client-facing text must not use those characterizations.
```

`RUNTIME_RESOLVED` resolves current binding-document particulars only; missing particulars -> fail closed.

Preserve unrelated service-taxonomy uncertainty if it genuinely remains unresolved.

- [ ] **Step 6: Run projection/service and body-level cross-file tests**

```bash
python -m pytest -q \
  tests/evochia/test_phase13_3_projection_and_service_models.py \
  tests/evochia/test_phase13_3_cross_file_sync.py
```

Expected:
- body-level stale-row assertions move toward GREEN;
- routing/artifact/eval assertions remain RED until Task 8;
- file-status assertions remain RED until Task 9.

- [ ] **Step 7: Commit row-level policy closure**

```bash
git add company/evochia/policies/commercial_policy.md \
        company/evochia/policies/current_rates.md \
        company/evochia/policies/company_profile.md
git commit -m "feat: close Phase 13.3 commercial rate and identity rows"
```

---

### Task 8: GREEN — Enforce Routing, CLIENT_SAFE Projection and Static Evals

**Files:**
- Modify: `skills/chef-ai-pro-business/references/routing.yaml`
- Modify: `templates/artifacts/client_artifact_contracts.yaml`
- Modify: `references/artifacts/rendering_policy.md`
- Modify: `evals/e2e/e2e_cases.yaml`
- Modify: `evals/artifacts/artifact_cases.yaml`
- Test: `tests/evochia/test_phase13_3_projection_and_service_models.py`
- Test: `tests/outputs/test_phase9_artifact_contracts.py`

**Interfaces:**
- Consumes: canonical policy bodies from Tasks 6–7.
- Produces: downstream execution/projection contracts that cannot bypass transport/legal/client-safe rules.

- [ ] **Step 1: Replace stale per-quote-default routing assumptions**

For `route_id: client_safe_proposal`, use canonical-default semantics with explicit service-model/quote overrides. Required routing requirements must cover:

```yaml
commercial_terms_requirements:
  - canonical_quote_validity_or_explicit_late_override
  - confirmation_payment_based_on_service_start_distance
  - t5_balance_only_on_30_percent_confirmation_path
  - canonical_cancellation_scope_postponement_terms
  - transport_verified_before_booking_confirmation
  - binding_documents_require_runtime_resolved_legal_particulars
  - household_uses_recurring_framework_not_event_defaults
  - client_safe_projection_excludes_internal_only_fields
```

Blockers must include at least:

```yaml
blockers:
  - unresolved_safety_conflict
  - unresolved_material_transport_at_confirmation
  - missing_required_binding_legal_particulars
  - ambiguous_service_model_or_material_override
```

Do not keep `quote_validity_explicit_when_no_company_default`; a company default now exists.

- [ ] **Step 2: Harden proposal forbidden fields**

In `templates/artifacts/client_artifact_contracts.yaml`, proposal `forbidden_internal_fields` must include:

```yaml
- uncollected_cancellation_balance
- internal_margin
- opportunity_cost
- supplier_comparison
- hidden_cost_basis
- internal_assumptions
- owner_review_reason
- classification_evidence
- internal_allocation_notes
```

Do not forbid valid evidenced separately chargeable third-party actual costs when the contract/policy authorizes them; the boundary is internal evidence/deliberation, not all third-party client charges.

- [ ] **Step 3: Strengthen rendering policy projection boundary**

Add explicit rule:

```text
Projection occurs before rendering. A template may not expose an INTERNAL-only commercial field merely because a client-visible label can be invented for it. `uncollected_cancellation_balance`, internal classification evidence, internal margin/opportunity cost, owner-review deliberation and internal allocation notes remain excluded unless a dedicated policy explicitly authorizes the specific field for CLIENT_SAFE use.
```

- [ ] **Step 4: Add static e2e cases**

Append cases with exact IDs:

```yaml
- id: phase13_3_payment_default_cure
  prompt: "Evochia balance missed at T-5 with a bank transfer pending over a weekend. Determine the operational state and next action."
  required_skills: [evochia-company-operations]
  optional_skills: [costing-commercial-intelligence]
  must: {payment_default_state: true, banking_clearing_floor: true, cure_capped_at_service_start: true, no_forced_new_exposure: true, client_notification: true}
  must_not: {classify_payment_default_as_client_side_impediment: true}

- id: phase13_3_external_impediment_reconciliation
  prompt: "An objectively verified external event prevents the remaining service after partial performance. Reconcile the booking."
  required_skills: [evochia-company-operations, costing-commercial-intelligence]
  optional_skills: []
  must: {external_regime: true, partial_performance_modifier: true, actual_exposure_reconciliation: true, recovery_offsets: true}
  must_not: {generic_force_majeure_fee: true, markup_recoverable_costs: true, recover_margin_or_opportunity_cost: true}

- id: phase13_3_evochia_inability_refund
  prompt: "Evochia becomes unable to perform the remaining confirmed service. Resolve the financial outcome and replacement option."
  required_skills: [evochia-company-operations]
  optional_skills: []
  must: {full_unperformed_scope_refund_or_credit: true, prompt_notification: true, replacement_requires_client_acceptance: true}
  must_not: {apply_client_cancellation_tiers_to_unperformed_scope: true, pass_evochia_sunk_costs_to_client: true}

- id: phase13_3_client_side_impediment
  prompt: "A client-side event prevents the remaining booking. Determine the applicable financial path."
  required_skills: [evochia-company-operations]
  optional_skills: [costing-commercial-intelligence]
  must: {client_side_regime: true, ordinary_window_rules: true, partial_performance_after_classification: true}
  must_not: {create_second_penalty_regime: true}

- id: phase13_3_peak_date_overlap_guard
  prompt: "Quote a peak-date island booking and determine whether both a date adjustment and island uplift may apply."
  required_skills: [evochia-company-operations, costing-commercial-intelligence]
  optional_skills: []
  must: {date_specific_basis: true, costs_already_covered_elsewhere: true, double_count_check: true, distinct_cause_required: true}
  must_not: {automatic_peak_surcharge: true, double_charge_same_cause: true}

- id: phase13_3_household_recurring_terms
  prompt: "Prepare terms for a 12-month private household chef engagement."
  required_skills: [evochia-company-operations, costing-commercial-intelligence]
  optional_skills: []
  must: {household_required_fields: true, recurring_billing_termination: true, rate_review_and_escalation: true}
  must_not: {inherit_event_t5_by_default: true, inherit_event_cancellation_tiers_by_default: true, use_global_household_rate_card: true}
```

- [ ] **Step 5: Add artifact evals for leakage and binding identity**

Append:

```yaml
- id: phase13_3_client_safe_uncollected_balance_guard
  input: internal cancellation reconciliation containing an uncollected cancellation balance with no owner collection decision
  expected:
    artifact_type: proposal
    audience: CLIENT_SAFE
    uncollected_cancellation_balance_exposed: false
  must_not:
    imply_uncollected_internal_balance_is_client_debt: true

- id: phase13_3_binding_identity_fail_closed
  input: binding Evochia client document request with unresolved required legal particulars
  expected:
    binding_document_generated: false
    identity_gate: fail_closed
  must_not:
    characterize_evochia_as_company_or_group: true
```

- [ ] **Step 6: Run routing/artifact/eval tests**

```bash
python -m pytest -q \
  tests/evochia/test_phase13_3_projection_and_service_models.py \
  tests/outputs/test_phase9_artifact_contracts.py
python evals/run_evals.py
```

Expected: PASS.

- [ ] **Step 7: Commit downstream enforcement**

```bash
git add skills/chef-ai-pro-business/references/routing.yaml \
        templates/artifacts/client_artifact_contracts.yaml \
        references/artifacts/rendering_policy.md \
        evals/e2e/e2e_cases.yaml \
        evals/artifacts/artifact_cases.yaml
git commit -m "feat: enforce Phase 13.3 commercial projection contracts"
```

---

### Task 9: GREEN — Perform Row Audit, Then Reconcile File Status and Release Readiness

**Files:**
- Modify headers only after audit: `company/evochia/policies/terms_policy.md`
- Modify headers only after audit: `company/evochia/policies/commercial_policy.md`
- Modify headers only after audit: `company/evochia/policies/current_rates.md`
- Modify headers only after audit: `company/evochia/policies/company_profile.md`
- Modify: `company/evochia/policies/policy_state_contract.yaml`
- Modify: `release/release_readiness.yaml`
- Test: `tests/evochia/test_phase13_3_cross_file_sync.py`
- Test: `tests/evochia/test_policy_state_machine.py`
- Test: `tests/evochia/test_phase13_2_owner_lock.py`

**Interfaces:**
- Consumes: fully edited row bodies and passing body-level tests.
- Produces: truthful file-level status derived from row state; truthful commercial readiness.

- [ ] **Step 1: Run the stale-row audit before changing any status**

Run:

```bash
rg -n "OPEN|NEEDS_OWNER_APPROVAL" \
  company/evochia/policies/terms_policy.md \
  company/evochia/policies/commercial_policy.md \
  company/evochia/policies/current_rates.md \
  company/evochia/policies/company_profile.md
```

Classify every match as either:

```text
A. Phase 13.3 stale row -> must be removed/closed before status work
B. genuinely unrelated unresolved row -> preserve and document
```

Expected after Tasks 6–7:
- `terms_policy.md`: only narrowly scoped final legal-drafting/review uncertainty remains;
- `commercial_policy.md`: no `OPEN` / `NEEDS_OWNER_APPROVAL` rows remain;
- `current_rates.md`: undefined service-family/rate and future public price-list policy remain open;
- `company_profile.md`: only unrelated service-taxonomy uncertainty may remain.

If a Phase 13.3 stale row is found, fix the body and rerun this audit before proceeding.

- [ ] **Step 2: Apply file-level statuses only after the audit**

Expected target:

```yaml
company_profile.md: PARTIALLY_APPROVED
commercial_policy.md: APPROVED
current_rates.md: PARTIALLY_APPROVED
staffing_policy.md: PARTIALLY_APPROVED
terms_policy.md: PARTIALLY_APPROVED
```

Do not promote a file to `APPROVED` if its body still contains an actual `OPEN` or `NEEDS_OWNER_APPROVAL` row.

- [ ] **Step 3: Update approval metadata for files materially changed by Phase 13.3**

Use:

```text
Approved by: Evochia Owner
Effective date: 2026-09-03
Approval reference: owner-approval-2026-09-03-phase13.3
```

for `terms_policy.md`, `commercial_policy.md`, `current_rates.md`, and `company_profile.md` and mirror those values in `policy_state_contract.yaml`.

Leave `staffing_policy.md` on its existing Phase 13.2 metadata if its content was not modified.

- [ ] **Step 4: Keep bundle readiness PARTIALLY_APPROVED**

Because not all required commercial policy files are fully approved:

```yaml
commercial_policy_readiness: PARTIALLY_APPROVED
```

Do not infer bundle-level `APPROVED` merely because `commercial_policy.md` itself becomes approved.

- [ ] **Step 5: Update release readiness truthfully**

Preserve:

```yaml
final_release_status: BLOCKED
may_claim_production_ready: false
```

Add a closed Phase 13.3 record, for example:

```yaml
- id: phase13_3_commercial_terms_completion
  status: CLOSED
  required_before_final_release: true
  closed_at: '2026-09-03'
  approval_reference: owner-approval-2026-09-03-phase13.3
  reason: canonical balance, cancellation, quote-validity, postponement, scope-reduction, impediment economics, peak-date, household and legal-identity rows are owner-approved and synchronized; unrelated partial-policy rows remain explicit
```

Preserve the historical Phase 13.2 closed blocker rather than rewriting it.

Replace the stale readiness note:

```text
Phase 13.2 owner approval does not close balance timing, cancellation/refundability, standard quote validity, peak-date policy or household-chef global rate card.
```

with a Phase 13.3 note stating those rows are now closed while unrelated legal drafting/service-family/taxonomy rows remain explicit.

- [ ] **Step 6: Run state/readiness tests**

```bash
python -m pytest -q \
  tests/evochia/test_phase13_3_cross_file_sync.py \
  tests/evochia/test_policy_state_machine.py \
  tests/evochia/test_phase13_2_owner_lock.py
```

Expected: PASS.

- [ ] **Step 7: Commit state/readiness reconciliation**

```bash
git add company/evochia/policies/terms_policy.md \
        company/evochia/policies/commercial_policy.md \
        company/evochia/policies/current_rates.md \
        company/evochia/policies/company_profile.md \
        company/evochia/policies/policy_state_contract.yaml \
        release/release_readiness.yaml
git commit -m "chore: reconcile Phase 13.3 policy states and readiness"
```

---

### Task 10: Full Acceptance, Doctrine and Repository Verification

**Files:**
- Modify only if a verification failure proves a real Phase 13.3 inconsistency; do not weaken tests to obtain green.

**Interfaces:**
- Consumes: Tasks 1–9.
- Produces: CI-equivalent evidence that Phase 13.3 is internally coherent and has not regressed unrelated gates.

- [ ] **Step 1: Run all Phase 13.3 tests**

```bash
python -m pytest -q \
  tests/evochia/test_phase13_3_terms_lifecycle.py \
  tests/evochia/test_phase13_3_impediment_economics.py \
  tests/evochia/test_phase13_3_projection_and_service_models.py \
  tests/evochia/test_phase13_3_cross_file_sync.py
```

Expected: PASS.

- [ ] **Step 2: Run all Evochia and output contract tests**

```bash
python -m pytest -q tests/evochia tests/outputs
```

Expected: PASS.

- [ ] **Step 3: Run the entire pytest suite**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 4: Run the static eval harness**

```bash
python evals/run_evals.py
```

Expected: PASS with all new Phase 13.3 eval IDs accepted by the harness.

- [ ] **Step 5: Run every CI repository validator**

```bash
python scripts/validate_skill_package.py
python scripts/validate_repo_hygiene.py .
python scripts/validate_parity_coverage.py
python scripts/validate_source_registry.py
python scripts/validate_doctrine_integrity.py
```

Expected: all exit 0.

- [ ] **Step 6: Run final canonical-authority and stale-row scans**

```bash
rg -n "USER-APPROVED DESIGN BASE / CANONICAL SPEC CANDIDATE" docs/superpowers/specs
rg -n "balance-payment timing|cancellation/refundability windows|standard quote validity|household-chef global rate card remains OPEN|peak-date pricing/surcharge policy" company/evochia/policies
rg -n "uncollected_cancellation_balance" templates/artifacts references/artifacts company/evochia/policies
```

Expected:
- no stale v1 canonical claim;
- no stale Phase 13.3 OPEN statements;
- `uncollected_cancellation_balance` exists in INTERNAL policy/test context and is explicitly forbidden/suppressed in CLIENT_SAFE contracts.

- [ ] **Step 7: Verify file-level status is explainable from row-level state**

Manually reconcile the Task 9 `rg` output with `policy_state_contract.yaml`:

```text
APPROVED file -> zero actual OPEN/NEEDS_OWNER_APPROVAL rows
PARTIALLY_APPROVED file -> every remaining open row is explicitly identified and unrelated to the closed Phase 13.3 decisions
```

Do not complete the phase if this explanation cannot be made deterministically.

- [ ] **Step 8: Inspect final diff for scope discipline**

```bash
git diff HEAD~9..HEAD --stat
git diff HEAD~9..HEAD -- company/evochia/policies skills/chef-ai-pro-business/references templates/artifacts references/artifacts evals tests/evochia release docs/superpowers/specs
```

Confirm:
- no unintended `staffing_policy.md` rewrite;
- no historical proposal promoted to current policy;
- no new competing regime vocabulary;
- no client-safe leakage of internal-only cancellation/economic fields;
- no unrelated release blocker was closed.

- [ ] **Step 9: Final implementation commit only if verification required fixes**

If verification required a genuine fix, commit the minimal correction with a specific message. If no files changed, do not create an empty commit.

---

# Acceptance-Criteria Coverage Matrix

| Criteria | Primary test/task |
| --- | --- |
| 1–7 | Task 2 lifecycle / Task 6 terms |
| 8–14 | Task 2 payment-cure / Task 6 terms |
| 15–28 | Task 2 cancellation/scope / Task 6 terms |
| 29–36 | Task 2 postponement / Task 6 terms |
| 37–45 | Task 3 threshold/workflow / Task 6 impediments |
| 46–54 | Task 3 Evochia inability / Task 6 impediments |
| 55–70 | Task 3 external economics / Task 6 impediments |
| 71–77 | Task 3 client-side + partial performance / Task 6 |
| 78–81 | Task 4 peak / Task 7 commercial policy |
| 82–85 | Task 4 household / Task 7 commercial + rates |
| 86–89 | Task 4 legal identity / Task 7 company profile + Task 8 routing |
| 90–91 | Task 4 CLIENT_SAFE / Task 8 artifact contracts |
| 92–98 | Task 5 stale-row sync / Tasks 7 and 9 |
| 99–100 | Task 5 state/readiness / Task 9 + Task 10 full validation |

# Explicit Non-Goals

- No general legal-contract drafting beyond recording the approved commercial operating model.
- No accounting/ERP receivable engine.
- No automatic collection of `uncollected_cancellation_balance`.
- No new global peak-date tariff.
- No global household-chef rate card.
- No change to existing +20% yacht / +40% island-overnight-remote uplift values.
- No automatic stacking of overlapping disruption/peak causes.
- No new company/group legal characterization.
- No broad policy-file `APPROVED` promotion merely because Phase 13.3 rows are closed.
- No reconstruction of historical proposal terms as current authority.

# Completion Definition

Phase 13.3 implementation is complete only when:

1. v1 is unambiguously superseded and v2 is the only current canonical spec;
2. D-052/D-053 persist the two approved implementation corrections;
3. all Phase 13.3 tests were written and observed RED before policy edits;
4. canonical policy bodies implement D-001–D-053;
5. routing/artifact/eval contracts enforce transport, identity, household and CLIENT_SAFE boundaries;
6. stale Phase 13.3 OPEN rows are closed across all four required files;
7. unrelated open rows remain explicit;
8. file-level status was assigned only after row-level audit;
9. commercial bundle readiness remains truthful (`PARTIALLY_APPROVED` unless every required policy becomes fully approved);
10. full pytest, eval harness and every CI validator pass.
