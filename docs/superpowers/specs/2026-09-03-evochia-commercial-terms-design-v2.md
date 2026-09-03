# Evochia Commercial Terms — Canonical Design v2

**Date:** 2026-09-03  
**Phase:** 13.3 — Commercial Terms Completion  
**Status:** CANONICAL SPEC CANDIDATE — AWAITING OWNER REVIEW  
**Decision source:** `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-decisions.md`  
**Supersedes:** `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-design.md`

## 1. Purpose and authority

This specification defines the canonical Evochia commercial model for quotes, confirmation, payment, cancellation, postponement, scope reduction, transport verification, performance impediments, partial performance, household engagements, peak-date adjustments, legal identity and audience-safe financial projection.

The decision register is the owner-decision authority for this design phase. This spec structures D-001 through D-051 but may not change their substance. Runtime authority moves to the policy files only after implementation.

Core invariants:

1. one canonical vocabulary;
2. one controlling event/classification path;
3. classification before financial resolution;
4. payment default is an operational state, not an impediment regime;
5. `PARTIAL_PERFORMANCE` is a calculation modifier, not a regime;
6. INTERNAL and CLIENT_SAFE outputs are distinct;
7. no double recovery, no markup on reimbursable exposure;
8. owner review instead of economically favorable auto-selection;
9. stale OPEN markers must disappear everywhere once a decision is implemented.

This is a commercial operating specification, not final legal drafting.

---

# 2. Canonical Definitions

Each term is defined once here. Downstream policy files reference these definitions rather than creating synonyms or duplicate formulas.

## 2.1 `SERVICE_START`

The first scheduled service date **as defined in the quote**. Travel, shopping, setup, prep, accommodation check-in or other operational activity does not redefine it unless the quote explicitly defines that activity as the start of service. For multi-day bookings this is the first scheduled service date in the confirmed quote. [D-002]

## 2.2 `FIXED_CONFIRMED_BOOKING_VALUE`

The fixed value confirmed for the agreed booking scope. It can include finalized fixed service, staffing, transport, equipment or other fixed lines. It excludes variable/pass-through actual-cost items not fixed at confirmation.

## 2.3 `CONFIRMATION_DATE`

The date booking confirmation is completed after written acceptance, all material non-payment confirmation gates are resolved, the required confirmation payment is satisfied, and binding-document legal identity requirements are resolved.

## 2.4 `CONFIRMATION_PAYMENT`

If confirmation occurs more than 5 calendar days before `SERVICE_START`:

```text
CONFIRMATION_PAYMENT = 30% × FIXED_CONFIRMED_BOOKING_VALUE
```

If confirmation occurs 5 or fewer calendar days before `SERVICE_START`:

```text
CONFIRMATION_PAYMENT = 100% × FIXED_CONFIRMED_BOOKING_VALUE
```

[D-003]

## 2.5 `BALANCE_DUE_DATE`

For the 30% confirmation path:

```text
BALANCE_DUE_DATE = SERVICE_START - 5 calendar days
```

[D-004]

## 2.6 `CLEARED_PAYMENT`

Funds received/cleared in a form reasonably available for Evochia to rely upon operationally. Evidence that a transfer was instructed is not automatically cleared payment.

## 2.7 `BANKING_CLEARING_FLOOR`

The earliest reasonable next opportunity for a normally pending bank transfer to clear. The policy does not hard-code its own bank-holiday calendar.

## 2.8 `CURE_DEADLINE`

```text
base_cure_deadline = payment_default_notice + 48 hours
candidate_cure_deadline = later_of(base_cure_deadline, BANKING_CLEARING_FLOOR)
CURE_DEADLINE = min(candidate_cure_deadline, SERVICE_START)
```

The cure deadline never extends beyond `SERVICE_START`. [D-006]

## 2.9 `CANCELLATION_TIER`

Ordered first-match tier selected by calendar days remaining before `SERVICE_START` on the controlling cancellation date:

| Days before `SERVICE_START` | Rate |
| ---: | ---: |
| 15+ | 10% |
| 6–14 | 30% |
| 0–5 | 100% |

Ordinary cancellation base = `FIXED_CONFIRMED_BOOKING_VALUE`. [D-008]

## 2.10 `CANCELLATION_RETENTION_CAP`

The maximum cumulative cancellation/scope-reduction retention on affected fixed scope:

```text
CANCELLATION_RETENTION_CAP = 100% of affected fixed scope value
```

It does not cap separately eligible third-party actual-cost items. Every fixed-scope unit may be charged at most once. [D-009, D-047]

## 2.11 `CANCELLATION_CHARGE`

The INTERNAL calculated cancellation result under the applicable cancellation rules. It is not automatically an invoice, receivable or collection authorization.

## 2.12 `COLLECTED_CANCELLATION_AMOUNT`

The portion of `CANCELLATION_CHARGE` satisfied from already collected funds under the applicable rule.

## 2.13 `REFUND_DUE`

```text
REFUND_DUE = max(collected_amount - COLLECTED_CANCELLATION_AMOUNT - other_valid_client_allocations, 0)
```

`other_valid_client_allocations` may include separately eligible actual-cost third-party items but may never duplicate an amount already recovered through retention.

## 2.14 `UNCOLLECTED_CANCELLATION_BALANCE`

```text
UNCOLLECTED_CANCELLATION_BALANCE =
max(CANCELLATION_CHARGE - COLLECTED_CANCELLATION_AMOUNT, 0)
```

INTERNAL only by default. It enters a client collection workflow only after explicit owner decision to pursue collection. [D-010, D-011]

## 2.15 `REMOVED_FIXED_VALUE`

```text
REMOVED_FIXED_VALUE = fixed value before approved change - revised fixed value
```

Scope-reduction tier treatment applies only to this removed value. [D-022]

## 2.16 `POSTPONEMENT_REQUEST_DATE`

The date a client postponement request is accepted for policy treatment. It freezes the tier used by anti-reset and credit-expiry rules.

## 2.17 `PERFORMED_SCOPE`

Service scope actually delivered and supportable by booking/service records. It is one of the three external-impediment evidence categories. [D-042]

## 2.18 `NON_RECOVERABLE_BOOKING_COST`

A booking-specific cost that is actually incurred or irrevocably committed, supported by evidence, and not economically recoverable through refund, supplier credit, resale, reuse, insurance, transferable asset value or another recovery route. [D-042, D-045]

## 2.19 `OTHER`

Any proposed external-impediment client allocation that is neither `PERFORMED_SCOPE` nor `NON_RECOVERABLE_BOOKING_COST`. It always requires `OWNER_REVIEW_REQUIRED`. [D-042]

## 2.20 `ACTUAL_ACQUISITION_COST`

The evidenced amount actually paid or irrevocably committed for an eligible third-party item, net of rebates, refunds, credits and other recoveries. It excludes markup, replacement-value uplift, theoretical margin and generalized overhead. [D-045]

## 2.21 `RUNTIME_RESOLVED_LEGAL_IDENTITY`

The binding document's required legal particulars for the already-known entity type. Entity type itself is not unresolved: provider = individual/sole proprietorship (`ατομική επιχείρηση`); `Evochia` = brand; `Evochia Food & Hospitality Group` = approved trade name / `διακριτικός τίτλος`, not a company or corporate group. [D-050]

---

# 3. Canonical state and regime vocabulary

## 3.1 Operational states

Examples:

```text
QUOTE_ISSUED
QUOTE_EXPIRED
CONFIRMATION_BLOCKED
BOOKING_CONFIRMED
BALANCE_SETTLED
PAYMENT_DEFAULT
CURE_PENDING
CLIENT_POSTPONED
SCOPE_REVISED
```

These are not impediment regimes.

## 3.2 Performance impediment regimes

Exactly:

```text
EXTERNAL_PERFORMANCE_IMPEDIMENT
EVOCHIA_INABILITY_TO_PERFORM
CLIENT_SIDE_IMPEDIMENT
```

No synonyms. [D-001]

`OWNER_REVIEW_REQUIRED` is a review state, not a fourth regime. [D-012]

`PARTIAL_PERFORMANCE` is a calculation modifier applied after classification. [D-013]

Payment default never becomes a second `CLIENT_SIDE_IMPEDIMENT` route. [D-005]

## 3.3 Four impediment workflow outcomes

After a valid impediment is identified/classified, the operational workflow ends in one of:

```text
PERFORM_OR_MITIGATE
REPLACEMENT_PERFORMANCE
RESCHEDULE
TERMINATE_AND_RECONCILE
```

These are outcomes, not regimes. [D-037]

---

# 4. Quote validity and confirmation gates

Every quote has explicit:

```text
valid_until = min(issue_date + 7 calendar days, SERVICE_START - 6 calendar days)
```

[D-025]

A quote-specific override may shorten validity. A later expiry requires an explicit later date; never an implicit/open-ended extension. [D-026]

If the default formula yields `valid_until < issue_date`, the default is unusable; the late quote needs an explicit later `valid_until` override. This preserves the <=5-day 100% confirmation path without silently treating an already-expired default quote as valid.

Validity is independent from confirmation readiness:

```text
TRANSPORT_UNVERIFIED -> CONFIRMATION_BLOCKED
```

Material transport must be resolved before booking confirmation even if the quote is still valid. [D-027]

Binding confirmation documents also require `RUNTIME_RESOLVED_LEGAL_IDENTITY`; otherwise generation fails closed. [D-050]

---

# 5. Booking confirmation, balance and payment default

Booking confirmation requires:

- written acceptance;
- resolved material confirmation gates;
- required confirmation payment;
- binding legal particulars where applicable.

More than five days before `SERVICE_START` uses the 30% path. Five or fewer uses 100% at confirmation. [D-003]

For a 30% booking, balance is due at T-5. [D-004]

If balance is not cleared:

```text
PAYMENT_DEFAULT -> CURE_PENDING
```

Payment default is not a regime. If Evochia later exercises the cancellation right, the ordinary tier is selected from the **date that right is exercised**. [D-005]

During cure, Evochia need not increase unrecoverable exposure. If it pauses/refuses new commitments under this right, it must promptly tell the client in writing. [D-035]

Examples of exposure Evochia need not increase while unpaid:

- new supplier or ingredient commitments;
- new staffing commitments;
- accommodation/travel commitments;
- rental/equipment commitments;
- irreversible prep;
- food-safety-sensitive exposure;
- service on unsecured credit.

---

# 6. Ordinary cancellation and scope reduction

## 6.1 Ordinary cancellation

```text
CANCELLATION_CHARGE = CANCELLATION_TIER × FIXED_CONFIRMED_BOOKING_VALUE
```

Tier = 10% / 30% / 100% first-match. [D-008]

The engine produces separate INTERNAL values:

```text
cancellation_charge
collected_cancellation_amount
refund_due
uncollected_cancellation_balance
```

[D-010]

`uncollected_cancellation_balance` stays out of CLIENT_SAFE output unless owner collection is explicitly authorized. [D-011]

## 6.2 Scope reduction

Requires written revised scope. Lower day-of attendance alone does not revise fixed confirmed value. [D-024]

```text
REMOVED_FIXED_VALUE = before_fixed_value - revised_fixed_value
scope_reduction_charge = tier_on_reduction_date × REMOVED_FIXED_VALUE
```

[D-022]

The revised quote uses the same pricing methodology. Non-scaling lines stay fixed unless explicitly revised; staffing triggers are recalculated, not proportionally scaled. [D-023]

Successive reductions may accumulate. First-match chooses each event's tier; it does not prohibit accumulation. But:

```text
each fixed-scope unit charged at most once
aggregate retention <= CANCELLATION_RETENTION_CAP
```

[D-009, D-047]

## 6.3 Separate third-party cost ledger

Cancellation retention and separately eligible third-party booking costs are distinct economic ledgers. Eligible third-party actual costs can sit outside `CANCELLATION_RETENTION_CAP` when the quote/commercial model treats them separately. The same item cannot be recovered through both ledgers. [D-046]

---

# 7. Client postponement

One client postponement per booking. Replacement date within six calendar months of the **original** `SERVICE_START`. [D-015]

Owner may grant written extension only with an explicit new expiry; history is not reset. [D-016]

Rescheduled service is repriced using current applicable terms/rates and new scope; the client carries eligible credit, not historical pricing. [D-018]

Anti-reset:

```text
final_cancellation_tier = max(
  tier_at_postponement_request,
  tier_at_final_cancellation
)
```

[D-017]

Unused expired postponement credit settles at the tier that applied on `POSTPONEMENT_REQUEST_DATE`. [D-019]

Any credit beyond final valid retained/allocated amount is refunded after reconciliation. [D-020]

Evochia-caused or external rescheduling does not consume the client's postponement, six-month window or anti-reset mechanism. [D-021]

---

# 8. Impediment threshold and common workflow rules

A performance impediment requires an **objectively verifiable material event** affecting performance. [D-036]

Not enough by themselves:

- increased cost;
- fear;
- preference;
- convenience;
- anticipated lower attendance;
- actual lower attendance.

A cost increase can lead to repricing/owner decision under another policy but is not itself `EXTERNAL_PERFORMANCE_IMPEDIMENT`.

Classification must be singular. Hybrid/disputed/insufficient causation:

```text
OWNER_REVIEW_REQUIRED
```

The system must not choose the path maximizing retention or minimizing refund. [D-012]

## 8.1 Mitigation boundary

Mitigation is expected only when reasonable and proportionate. Neither party must automatically incur a material incremental cash cost or materially greater exposure. If mitigation requires such incremental cost, cost allocation must be explicitly agreed before the commitment; otherwise use another valid outcome. [D-038]

## 8.2 Common economic invariants

For every regime:

```text
NO_DOUBLE_RECOVERY
NO_MARKUP_ON_REIMBURSABLE_EXPOSURE
ACTUAL_ACQUISITION_COST_ONLY
OFFSET_ALL_RECOVERIES
```

A refund, credit, insurance payment, supplier refund, resale, reuse or reusable asset value offsets client allocation. [D-045]

No generic `force majeure fee`. [D-043]

---

# 9. `EVOCHIA_INABILITY_TO_PERFORM`

## 9.1 Classification

Used when Evochia is the controlling cause of inability to deliver the contracted performance.

## 9.2 Financial resolution

Cancellation tiers **do not apply** to unperformed scope.

```text
client_refund_or_credit = 100% of unperformed fixed scope already collected
```

Evochia bears:

- its own sunk costs;
- lost margin;
- opportunity cost;
- its own non-recoverable internal/third-party commitments unless another separately agreed client-owned item applies independently.

These are not shifted to the client because Evochia cannot perform. [D-039]

Performed scope, if any, is resolved through `PARTIAL_PERFORMANCE` before calculating the unperformed refund. [D-013, D-014]

## 9.3 Client consequential costs

The client's independent third-party/consequential costs are not automatically reimbursable by Evochia. Any goodwill compensation is owner-discretionary and must be explicit. [D-040]

## 9.4 Replacement

`REPLACEMENT_PERFORMANCE` is permitted only if the proposed replacement materially corresponds to contracted scope and the client accepts it. The client cannot be unilaterally substituted into a materially different service. [D-040]

## 9.5 Notification

Evochia must notify the client promptly when a material risk of inability to perform becomes known, not only after failure is certain. [D-040]

## 9.6 Available workflow outcomes

```text
PERFORM_OR_MITIGATE
REPLACEMENT_PERFORMANCE (client acceptance required)
RESCHEDULE
TERMINATE_AND_RECONCILE
```

---

# 10. `EXTERNAL_PERFORMANCE_IMPEDIMENT`

## 10.1 Classification

Used only for objectively verifiable material events outside the reasonable control of both parties that actually impede performance. Fear/preference/attendance/cost increase alone do not qualify. [D-036]

## 10.2 Financial model: actual-exposure reconciliation

The 10/30/100 cancellation tiers do **not** govern this regime.

Client allocation is limited to:

```text
PERFORMED_SCOPE
+ eligible NON_RECOVERABLE_BOOKING_COST
```

Then remaining collected funds are refunded/credited. [D-041]

Evochia absorbs:

- lost margin;
- opportunity cost;
- theoretical profit;
- generalized administration;
- unsupported estimates.

The client bears its own independent/consequential costs unless separately agreed. [D-041, D-043]

## 10.3 Evidence gate

Every proposed client allocation must classify as exactly one of:

```text
PERFORMED_SCOPE
NON_RECOVERABLE_BOOKING_COST
OTHER
```

`OTHER -> OWNER_REVIEW_REQUIRED`. [D-042]

For `NON_RECOVERABLE_BOOKING_COST`, require:

- booking-specific nexus;
- actually incurred or irrevocably committed;
- documentary evidence;
- no duplicate recovery;
- net of supplier refunds/credits;
- net of resale/reuse/insurance value;
- actual acquisition/commitment cost only.

Recoverable/reusable assets are not loss merely because purchased for the booking. [D-042, D-043, D-045]

## 10.4 No force-majeure markup

Forbidden client allocations include:

- generic force-majeure percentage;
- profit markup on third-party cost;
- replacement-price uplift over actual cost;
- margin;
- opportunity cost;
- generalized overhead/admin;
- an asset cost where the asset remains economically usable/recoverable.

[D-043, D-045]

## 10.5 Partial performance

If some service was delivered before the external impediment:

1. classify `EXTERNAL_PERFORMANCE_IMPEDIMENT`;
2. apply `PARTIAL_PERFORMANCE` to performed scope/cost allocation;
3. add only valid non-recoverable booking costs;
4. offset all recoveries;
5. settle/refund the remainder.

## 10.6 Available workflow outcomes

```text
PERFORM_OR_MITIGATE
REPLACEMENT_PERFORMANCE (if genuinely equivalent and agreed)
RESCHEDULE
TERMINATE_AND_RECONCILE
```

External reschedule does not consume the client postponement mechanism. [D-021]

---

# 11. `CLIENT_SIDE_IMPEDIMENT`

A client-side performance impediment does not create a bespoke penalty model. Apply the normal cancellation / partial-cancellation / scope-reduction rules for the controlling date/window. [D-044]

If performance has begun, classify first, then apply `PARTIAL_PERFORMANCE` to the performed component and the ordinary client-side cancellation logic to the unperformed/removed component as applicable. [D-013, D-014, D-044]

Payment default is expressly excluded from this route; it remains Section 5's operational state and exercise-date cancellation path. [D-005]

---

# 12. `PARTIAL_PERFORMANCE`

`PARTIAL_PERFORMANCE` is one calculation modifier with three allocation rules. [D-013, D-014]

## Rule 1 — Unitized performed service

Where the contract has genuine units (service session, dinner/day, production day, delivery):

```text
performed_value = contracted_unit_value × actually_performed_units
```

## Rule 2 — Direct attributable costs

Direct costs are allocated by documentary attribution to the performed/affected portion, not by arbitrary booking-completion percentage when better attribution exists.

## Rule 3 — Shared/indivisible fixed lines

Use, in order:

1. allocation basis already defined in the confirmed quote/commercial model;
2. objective deterministic allocation if one exists;
3. otherwise `OWNER_REVIEW_REQUIRED`.

The modifier never changes the controlling regime.

---

# 13. Peak-date quote-specific adjustment

There is **no global peak-date surcharge**. [D-048]

Any quote-specific peak adjustment requires structured INTERNAL fields:

```text
peak_date_context
adjustment_reason
adjustment_method_or_amount
owner_approval
client_disclosure
causal_overlap_check
```

Peak adjustment and yacht/island/remote disruption uplift may coexist only if their documented causes are genuinely distinct. The same availability/disruption cause cannot be charged twice under different labels. [D-048]

This means "peak date" is not a generic multiplier and cannot silently stack because a date is also on an island/yacht.

---

# 14. Household-chef framework

There is **no global household-chef rate card**. Household pricing is quote-specific. [D-049]

Every household quote/agreement must define:

```text
scope
service_days_and_hours
extra_day_and_hour_rules
guest_event_rules
food_and_pass_through_treatment
travel
billing_cycle
termination_and_notice
rate_review
absence_or_non_use
```

Household service is a recurring engagement model and has its **own billing/termination framework**. One-off event deposit, T-5 balance and 10/30/100 cancellation logic do not apply by default. [D-049]

Historical household proposals remain evidence/examples only, not a current global tariff.

---

# 15. Legal identity and binding documents

Closed identity facts: [D-050]

```text
Provider entity type: individual / sole proprietorship (ατομική επιχείρηση)
Brand: Evochia
Trade name / διακριτικός τίτλος: Evochia Food & Hospitality Group
```

The trade name is not evidence of a separate company, corporation, corporate group or group of companies.

`RUNTIME_RESOLVED` resolves required binding-document particulars (e.g. the correct current legal identifiers/details needed for that artifact), **not** whether Evochia is a company.

Binding document:

```text
required legal particulars unavailable -> FAIL CLOSED
```

Client-facing language must never characterize Evochia as:

- a company;
- a corporation;
- a corporate group;
- a group of companies.

This prohibition is not unlockable by later inference from the trade name. A future actual legal-entity change would require a new explicit owner decision superseding D-050.

---

# 16. INTERNAL vs CLIENT_SAFE projection contract

## 16.1 INTERNAL may contain

- controlling state/regime;
- classification evidence;
- `OWNER_REVIEW_REQUIRED` reason;
- fixed confirmed value;
- cancellation tier and retention cap;
- cancellation charge;
- collected cancellation amount;
- refund due;
- uncollected cancellation balance;
- performed-scope allocation;
- third-party actual-cost evidence;
- refunds/credits/reuse offsets;
- mitigation alternatives/costs;
- collection decision;
- peak causal-overlap record;
- legal-identity resolution state.

## 16.2 CLIENT_SAFE may contain

Only amounts/terms authorized for client disclosure, e.g.:

- service/quote terms;
- applicable cancellation or reconciliation basis;
- amount received;
- amount retained/applied;
- evidenced separately chargeable third-party actual costs where contractually applicable;
- refund/credit due;
- currently payable amount only if validly authorized.

Forbidden by default:

```text
uncollected_cancellation_balance
internal margin/opportunity cost
owner-review deliberation
internal allocation notes
unsupported third-party estimates
```

[D-011, D-031, D-045]

---

# 17. Scenario traces

## S1 — Normal early confirmation

Confirmation >5 days before service -> 30% deposit -> balance T-5 -> cleared -> `BALANCE_SETTLED` -> performance.

## S2 — Late confirmation

Confirmation <=5 days -> explicit valid quote override if default validity unusable -> all gates including transport/legal identity resolved -> 100% at confirmation -> no balance stage.

## S3 — Weekend/bank clearing cure

Balance missed -> `PAYMENT_DEFAULT` -> cure = later of 48h/banking floor but never after `SERVICE_START`; Evochia can pause new exposure and tells client in writing.

## S4 — Payment default cancelled by Evochia

No impediment classification. Cancellation tier selected by date Evochia exercises cancellation right.

## S5 — Ordinary client cancellation with insufficient collected funds

Calculate tier charge, collected amount, refund and uncollected balance separately. Uncollected balance remains INTERNAL unless owner elects collection.

## S6 — Two scope reductions

Each reduction calculates removed fixed value and its own first-match tier. Previous removed units are excluded from second charge. Aggregate retention cannot exceed affected fixed scope value. Separately eligible third-party cost ledger remains outside that cap with no double recovery.

## S7 — Client postpones then cancels

One postponement; new date within six months of original start; repricing current terms; final tier = max(request-date tier, final-cancellation tier); excess credit refunded.

## S8 — Evochia cannot perform before service

`EVOCHIA_INABILITY_TO_PERFORM` -> cancellation tiers ignored -> full refund/credit of collected unperformed fixed scope; Evochia absorbs own sunk cost/margin/opportunity cost. Equivalent replacement requires client acceptance. Prompt notification once material risk known.

## S9 — Evochia inability after partial performance

Classify Evochia inability -> apply `PARTIAL_PERFORMANCE` to delivered units -> refund 100% of remaining unperformed fixed scope collected; no 10/30/100 on remainder.

## S10 — External event before service

Objectively verifiable external material event -> `EXTERNAL_PERFORMANCE_IMPEDIMENT` -> actual-exposure reconciliation. Valid client allocation only evidenced non-recoverable booking cost; reusable/refundable assets offset. No generic fee, margin or markup.

## S11 — External event after partial performance

Classify external -> `PARTIAL_PERFORMANCE` for performed scope -> add eligible non-recoverable booking costs -> offset supplier credits/reusable value -> refund remainder.

## S12 — Fear / preference / lower attendance

No objectively verifiable performance impediment -> not external. Use normal client change/cancellation/scope rules if client elects change.

## S13 — Hybrid cause

Two plausible material regimes and no deterministic controlling cause -> `OWNER_REVIEW_REQUIRED`; no commercially favorable auto-selection.

## S14 — Mitigation materially increases cost

Valid impediment exists; proposed workaround requires material incremental cash cost -> no automatic obligation to incur -> explicit cost-allocation agreement or choose another workflow outcome.

## S15 — Peak-date + island

Quote proposes peak adjustment and island uplift -> causal-overlap check required. If both reflect same disruption/availability burden, double charge prohibited; if distinct documented causes, both may be explicitly quoted.

## S16 — Household engagement

Monthly recurring household engagement -> own quote-specific scope/rate/billing/termination/absence framework -> does not inherit one-off event T-5/cancellation tiers automatically.

## S17 — Binding artifact legal identity

Entity type known as sole proprietorship, but required current binding particulars unavailable -> fail closed. Trade name never licenses wording such as "Evochia company/group".

---

# 18. Cross-file implementation contract

Implementation must reconcile at least:

## `terms_policy.md`

Canonical runtime authority for definitions and terms lifecycle, including confirmation/payment, cancellation, postponement, scope reduction, three regimes, partial performance, common recovery rules, transport gate and external-disruption treatment.

## `commercial_policy.md`

References the terms authority; removes stale OPEN statements for closed decisions; encodes no-double-recovery/no-markup, peak causal separation and household recurring-framework boundary without duplicating all formulas.

## `current_rates.md`

Peak-date = approved **no global surcharge, quote-specific only**. Household = approved **no global rate card, quote-specific only**. Historical values remain evidence.

## `company_profile.md`

Legal identity = sole proprietorship; brand/trade-name distinction; remove stale unresolved company/group implication. No corporate/group characterization.

## `policy_state_contract.yaml`

Update file/row approval states consistently after actual policy implementation; do not let file-level approval promote unrelated unresolved rows.

## Routing/artifact contracts

Enforce `TRANSPORT_UNVERIFIED` confirmation block, legal-identity fail-closed, CLIENT_SAFE suppression of internal fields and material unresolved-term gates.

## Release readiness

Remove obsolete Phase 13.2 notes once all corresponding policy/test changes are actually merged; preserve unrelated blockers.

[D-032]

---

# 19. Acceptance tests

At minimum, implementation must prove:

### Quote / confirmation / payment
1. 7-day/default validity formula.
2. `SERVICE_START - 6` validity ceiling.
3. late-default-validity requires explicit later date.
4. >5-day confirmation = 30%.
5. <=5-day confirmation = 100%.
6. T-5 balance only on 30% path.
7. transport unresolved blocks confirmation independently of validity.
8. payment default remains operational state.
9. exercise-date tiering after payment default.
10. 48-hour cure.
11. banking-clearing floor.
12. cure never beyond `SERVICE_START`.
13. no forced new exposure during cure.
14. pause/refusal of exposure is communicated to client.

### Cancellation / scope / postponement
15. tier boundary at 15 days.
16. tier boundary at 6 days.
17. tier boundary at 5 days.
18. three/four financial fields remain separate.
19. uncollected balance suppressed from CLIENT_SAFE.
20. removed-value-only tiering.
21. same pricing methodology on reduction.
22. staffing trigger recalculation.
23. lower attendance alone does not reduce fixed value.
24. successive reductions accumulate.
25. each fixed unit charged once.
26. retention <= 100% affected fixed scope.
27. separate eligible third-party costs are not constrained by retention cap.
28. no same-item retention + third-party double recovery.
29. one client postponement.
30. six-month window from original start.
31. extension requires explicit expiry.
32. anti-reset max rule.
33. current-term repricing.
34. expired credit uses request-date tier.
35. excess credit refund.
36. non-client reschedule does not consume client postponement.

### Impediment threshold/workflow
37. objectively verifiable material event required.
38. increased cost alone rejected as external impediment.
39. fear/preferences rejected as external impediment.
40. reduced attendance rejected as external impediment.
41. exactly one controlling regime.
42. hybrid cause -> owner review.
43. no favorable-regime auto-selection.
44. workflow outcome is one of four permitted outcomes.
45. material incremental mitigation cost requires explicit allocation agreement.

### Evochia inability
46. full refund/credit of collected unperformed fixed scope.
47. cancellation tiers not applied to Evochia-caused unperformed scope.
48. Evochia sunk costs not passed through.
49. margin/opportunity cost not passed through.
50. client consequential costs not automatically reimbursed.
51. replacement materially corresponds to scope.
52. replacement requires client acceptance.
53. prompt notification on known material risk.
54. partial-performance modifier correctly separates delivered/unperformed scope.

### External impediment
55. uses actual-exposure reconciliation, not 10/30/100 tiers.
56. performed scope accepted as evidence category.
57. valid non-recoverable booking cost accepted with evidence.
58. `OTHER` -> owner review.
59. supplier refund offsets exposure.
60. reusable/resellable asset value offsets exposure.
61. insurance/other recovery offsets exposure.
62. no generic force-majeure fee.
63. no markup.
64. actual acquisition cost only.
65. no opportunity-cost recovery.
66. no margin recovery.
67. no generalized unsupported admin recovery.
68. no double recovery.
69. client consequential costs remain client-side absent agreement.
70. partial external performance reconciles performed + eligible exposure then refund.

### Client-side impediment / partial performance
71. client-side impediment routes to normal cancellation/change rules.
72. payment default excluded from client-side impediment route.
73. `PARTIAL_PERFORMANCE` cannot be selected as regime.
74. unitized allocation.
75. direct attributable-cost allocation.
76. shared fixed allocation uses declared/objective basis.
77. ambiguous shared allocation -> owner review.

### Peak / household / legal / export
78. no global peak surcharge.
79. all peak structured fields required when adjustment used.
80. peak/yacht/island causal-overlap check.
81. same causal burden cannot be charged twice.
82. no global household rate card.
83. all ten household framework fields required.
84. household uses recurring billing/termination framework.
85. event cancellation/payment rules not inherited by default.
86. entity type fixed as sole proprietorship.
87. brand vs trade name represented distinctly.
88. company/corporate/group characterization prohibited.
89. binding artifact fails closed when required legal particulars unresolved.
90. CLIENT_SAFE suppresses internal-only amounts/evidence.
91. explicit owner collection required before exposing uncollected cancellation balance.

### Cross-file sync
92. stale balance OPEN removed where closed.
93. stale cancellation/refundability OPEN removed where closed.
94. stale quote-validity OPEN removed where closed.
95. stale peak-date OPEN removed and replaced with approved no-global-surcharge rule.
96. stale household-rate-card OPEN removed and replaced with approved no-global-card rule.
97. stale company/group identity uncertainty removed.
98. unrelated genuinely unresolved rows remain unresolved.
99. policy-state contract matches runtime files.
100. release-readiness notes match implemented Phase 13.3 state.

[D-034, D-051]

---

# 20. Completion criterion

Phase 13.3 is not complete merely because this spec exists. Completion requires:

1. owner approval of this v2 spec;
2. an implementation plan derived from this v2 spec and D-001–D-051;
3. TDD implementation of runtime policies/contracts/tests;
4. cross-file stale-OPEN reconciliation;
5. green validation/release gates;
6. no policy implementation that silently departs from the decision register.
