# Evochia Commercial Terms — Canonical Design

**Date:** 2026-09-03  
**Phase:** 13.3 — Commercial Terms Completion  
**Status:** USER-APPROVED DESIGN BASE / CANONICAL SPEC CANDIDATE  
**Decision source:** `docs/superpowers/specs/2026-09-03-evochia-commercial-terms-decisions.md`

## 1. Purpose

This specification defines the canonical Evochia commercial-terms model for booking confirmation, payment, cancellation, postponement, scope reduction, impediments, partial performance, quote validity, transport verification, legal-identity resolution, and audience-safe financial projection.

The design goal is deterministic commercial reasoning:

1. each event has one controlling operational/classification path;
2. each calculation uses one canonical definition of its inputs;
3. INTERNAL economics and CLIENT_SAFE outputs remain separate;
4. unresolved or hybrid causation fails to owner review rather than to the commercially most favorable outcome;
5. all policy files remain synchronized with the owner decision register.

This design does not replace legal review of binding contract wording.

---

# 2. Authority and derivation

The normative owner decisions for this phase live in:

`docs/superpowers/specs/2026-09-03-evochia-commercial-terms-decisions.md`

The decision register is the source of truth for the design/spec phase. This specification may organize those decisions into definitions, states, formulas and flows, but may not alter their substance.

Runtime authority remains in the Evochia policy files only after implementation.

Relevant decisions: D-001 through D-034.

---

# 3. Canonical Definitions

Definitions appear once here. Downstream sections and runtime policy files must reference them instead of redefining them.

## 3.1 `SERVICE_START`

The first scheduled service date **as defined in the quote**.

Travel, setup, shopping, prep, accommodation check-in or other operational activity does not redefine `SERVICE_START` unless the quote itself explicitly defines that activity as the start of the service.

For a multi-day booking, `SERVICE_START` is the first scheduled service date in the confirmed quote.

Decision: D-002.

## 3.2 `FIXED_CONFIRMED_BOOKING_VALUE`

The fixed monetary value confirmed at booking for the agreed service scope.

It may include fixed service, staffing, transport, equipment or other fixed lines already finalized at confirmation. It excludes variable/pass-through actual-cost items that are not fixed at confirmation.

This is the base for confirmation-payment and cancellation-tier calculations unless a specific rule explicitly narrows the base to removed scope.

## 3.3 `CONFIRMATION_DATE`

The date on which all booking-confirmation prerequisites are satisfied and Evochia can validly confirm the booking.

A still-unresolved material confirmation gate, including `TRANSPORT_UNVERIFIED`, prevents confirmation even if the quote remains otherwise valid.

## 3.4 `CONFIRMATION_PAYMENT`

If:

```text
CONFIRMATION_DATE < SERVICE_START - 5 calendar days
```

then:

```text
CONFIRMATION_PAYMENT = 30% × FIXED_CONFIRMED_BOOKING_VALUE
```

If confirmation occurs 5 or fewer calendar days before `SERVICE_START`:

```text
CONFIRMATION_PAYMENT = 100% × FIXED_CONFIRMED_BOOKING_VALUE
```

Decision: D-003.

## 3.5 `BALANCE_DUE_DATE`

For a booking confirmed with a 30% confirmation deposit:

```text
BALANCE_DUE_DATE = SERVICE_START - 5 calendar days
```

Decision: D-004.

## 3.6 `CLEARED_PAYMENT`

Payment that has been received/cleared in a form reasonably available to Evochia for operational reliance.

A transfer instruction or client statement that payment has been sent is evidence of attempted payment, not automatically `CLEARED_PAYMENT`.

## 3.7 `BANKING_CLEARING_FLOOR`

A protection against a cure deadline expiring before a normally pending bank transfer has a reasonable next banking-clearing opportunity.

The policy does not maintain its own holiday calendar; banking-day resolution is operational/current-context dependent.

## 3.8 `CURE_PERIOD`

A limited opportunity to remedy a missed balance deadline.

```text
base_cure_deadline = payment_default_notice + 48 hours
candidate_cure_deadline = later_of(base_cure_deadline, BANKING_CLEARING_FLOOR)
CURE_DEADLINE = min(candidate_cure_deadline, SERVICE_START)
```

The cure period never extends beyond `SERVICE_START`.

Decision: D-006.

## 3.9 `CANCELLATION_TIER`

Ordered first-match tier selected by calendar days remaining before `SERVICE_START` on the controlling cancellation date:

| Days before `SERVICE_START` | Retention / charge rate |
| ---: | ---: |
| 15+ | 10% |
| 6–14 | 30% |
| 0–5 | 100% |

Base for ordinary booking cancellation:

```text
FIXED_CONFIRMED_BOOKING_VALUE
```

Decision: D-008.

## 3.10 `CANCELLATION_CHARGE`

The INTERNAL calculated cancellation result under the applicable tier/regime.

It is not by itself an invoice, receivable, payment demand or authorization to pursue collection.

## 3.11 `COLLECTED_CANCELLATION_AMOUNT`

The portion of `CANCELLATION_CHARGE` satisfied from funds already collected and lawfully/contractually retainable under the applicable commercial rule.

## 3.12 `REFUND_DUE`

```text
REFUND_DUE = max(collected_amount - COLLECTED_CANCELLATION_AMOUNT, 0)
```

## 3.13 `UNCOLLECTED_CANCELLATION_BALANCE`

```text
UNCOLLECTED_CANCELLATION_BALANCE =
max(CANCELLATION_CHARGE - COLLECTED_CANCELLATION_AMOUNT, 0)
```

This value is INTERNAL by default.

It may enter a CLIENT_SAFE collection/demand workflow only after an explicit owner decision to pursue it.

Decisions: D-010, D-011.

## 3.14 `REMOVED_FIXED_VALUE`

For an approved scope reduction:

```text
REMOVED_FIXED_VALUE =
fixed value before approved change - revised fixed value
```

Cancellation-tier treatment for scope reduction applies only to `REMOVED_FIXED_VALUE`.

Decision: D-022.

## 3.15 `POSTPONEMENT_REQUEST_DATE`

The date on which the client requests a postponement that Evochia treats as a client postponement for policy purposes.

This date captures the cancellation tier used by the anti-reset and credit-expiry rules.

---

# 4. Canonical regime vocabulary

The impediment regimes are exactly:

- `EXTERNAL_PERFORMANCE_IMPEDIMENT`
- `EVOCHIA_INABILITY_TO_PERFORM`
- `CLIENT_SIDE_IMPEDIMENT`

No synonym regime vocabulary is permitted.

`OWNER_REVIEW_REQUIRED` is not a fourth commercial regime; it is the required review state when a deterministic single classification cannot be made.

`PARTIAL_PERFORMANCE` is not an impediment regime. It is a calculation modifier after classification.

Payment default is not an impediment regime.

Decisions: D-001, D-005, D-012, D-013.

---

# 5. High-level state model

```text
QUOTE_ISSUED
    |
    |-- validity expires ------------------------> QUOTE_EXPIRED
    |
    |-- confirmation gates unresolved ----------> CONFIRMATION_BLOCKED
    |       |
    |       `-- TRANSPORT_UNVERIFIED
    |
    `-- confirmation gates satisfied
            |
            v
        BOOKING_CONFIRMED
            |
            |-- confirmation >5 days before start -> 30% deposit path
            |       |
            |       `-- balance due T-5
            |               |
            |               |-- paid -> BALANCE_SETTLED
            |               `-- unpaid -> PAYMENT_DEFAULT / CURE_PENDING
            |
            |-- confirmation <=5 days before start -> 100% confirmation payment
            |
            |-- client cancellation
            |-- client postponement
            |-- approved scope reduction
            |-- performance impediment
            `-- normal performance
```

Performance impediments then classify exactly once:

```text
PERFORMANCE_EVENT
    |
    |-- EXTERNAL_PERFORMANCE_IMPEDIMENT
    |-- EVOCHIA_INABILITY_TO_PERFORM
    |-- CLIENT_SIDE_IMPEDIMENT
    `-- OWNER_REVIEW_REQUIRED
```

If any service has already been performed, `PARTIAL_PERFORMANCE` modifies the calculation after the controlling regime is known.

---

# 6. Quote validity

## 6.1 Default formula

Every quote must include an explicit `valid_until` date.

```text
valid_until = min(
    issue_date + 7 calendar days,
    SERVICE_START - 6 calendar days
)
```

Decision: D-025.

## 6.2 Overrides

A quote-specific override may shorten validity without special exception.

An extension beyond the default must state an explicit later `valid_until` date. Open-ended or implied extensions are not permitted.

Decision: D-026.

## 6.3 Validity is not confirmation readiness

A quote may still be within its validity window while confirmation remains blocked by unresolved material gates.

In particular:

```text
TRANSPORT_UNVERIFIED -> CONFIRMATION_BLOCKED
```

until transport is verified/resolved.

Decision: D-027.

---

# 7. Booking confirmation and payment

## 7.1 Confirmation prerequisites

Booking confirmation requires at minimum:

- written acceptance;
- all material confirmation gates resolved;
- required confirmation payment under D-003;
- runtime legal identity resolved where the resulting document is binding.

## 7.2 Confirmation payment

More than 5 calendar days before `SERVICE_START`:

```text
30% deposit
```

5 or fewer calendar days before `SERVICE_START`:

```text
100% at confirmation
```

## 7.3 Balance

For the 30% path:

```text
BALANCE_DUE_DATE = T-5
```

There is no separate balance stage in the <=5-day 100% confirmation path.

---

# 8. Payment default and cure

## 8.1 Payment default is operational state, not regime

If the balance is not cleared by `BALANCE_DUE_DATE`:

```text
PAYMENT_DEFAULT
    -> CURE_PENDING
```

This does not become `CLIENT_SIDE_IMPEDIMENT` merely because the payment remains unresolved.

Decision: D-005.

## 8.2 Right to cancel

Payment default gives Evochia a right to cancel according to the agreed commercial terms.

If Evochia exercises that right, the applicable ordinary cancellation tier is determined from the date the cancellation right is exercised.

No second payment-default penalty regime is created.

## 8.3 Cure deadline

```text
CURE_DEADLINE =
min(
  later_of(payment_default_notice + 48h, BANKING_CLEARING_FLOOR),
  SERVICE_START
)
```

## 8.4 Exposure boundary

While `CURE_PENDING`, Evochia is not required to increase unrecoverable exposure.

This includes no obligation to incur new material:

- ingredient/supplier commitments;
- staffing commitments;
- accommodation/travel commitments;
- equipment/rental commitments;
- preparation exposure;
- food-safety-sensitive exposure;
- credit exposure by beginning service without required cleared payment.

Already incurred/committed obligations remain recorded under their applicable commercial treatment.

Decision: D-007.

---

# 9. Ordinary cancellation

## 9.1 Tier selection

Tier selection is ordered first-match using the controlling cancellation date.

```text
15+ days -> 10%
6-14 days -> 30%
0-5 days -> 100%
```

## 9.2 Base

Ordinary cancellation charge uses:

```text
CANCELLATION_CHARGE =
CANCELLATION_TIER × FIXED_CONFIRMED_BOOKING_VALUE
```

subject to any controlling postponement/scope-reduction rule that narrows or modifies the calculation.

## 9.3 Financial outputs

Every cancellation calculation produces separate INTERNAL values:

```text
CANCELLATION_CHARGE
COLLECTED_CANCELLATION_AMOUNT
REFUND_DUE
UNCOLLECTED_CANCELLATION_BALANCE
```

## 9.4 Client projection

`UNCOLLECTED_CANCELLATION_BALANCE` is not shown by default.

CLIENT_SAFE output may show, as applicable:

- amount received;
- amount retained/applied;
- refund due;
- amount currently payable only when separately authorized for collection.

---

# 10. Scope reduction

## 10.1 Trigger

A scope reduction exists only after a written approved/revised scope.

Lower actual attendance on the service day does not by itself revise `FIXED_CONFIRMED_BOOKING_VALUE`.

Decision: D-024.

## 10.2 Removed-value calculation

```text
REMOVED_FIXED_VALUE =
fixed value before change - revised fixed value
```

The cancellation tier on the approved reduction date applies only to `REMOVED_FIXED_VALUE`.

```text
scope_reduction_charge =
applicable_tier × REMOVED_FIXED_VALUE
```

Decision: D-022.

## 10.3 Pricing methodology

The revised fixed value must use the same pricing methodology as the confirmed quote.

Requirements:

- genuinely non-scaling fixed elements remain unchanged unless explicitly revised;
- staffing triggers are recalculated from the revised scope;
- staffing is not reduced by simplistic proportional scaling;
- package/all-in methodology stays internally reconcilable to the confirmed methodology.

Decision: D-023.

## 10.4 Successive reductions

First-match selects the tier applicable to each approved reduction event.

Successive reductions may accumulate toward the applicable cancellation/retention cap.

Invariant:

```text
Each unit of fixed scope is charged at most once.
```

The implementation must track previously removed/charged fixed scope sufficiently to prevent double charging.

Decision: D-009.

---

# 11. Client postponement

## 11.1 Entitlement boundary

Client postponement is permitted once per booking.

The replacement service date must be within 6 calendar months of the **original** `SERVICE_START`.

Decision: D-015.

## 11.2 Discretionary written extension

The owner may grant an extension only by explicitly stating a new expiry date in writing.

An extension does not reset postponement history or create a new initial postponement.

Decision: D-016.

## 11.3 Credit concept

Eligible collected amounts may operate as postponement credit subject to settlement and repricing rules.

Postponement preserves eligible credit, not historical commercial pricing.

## 11.4 Repricing

The rescheduled booking is priced under current applicable rates/terms for the new date and revised scope.

Decision: D-018.

## 11.5 Anti-reset rule

Record the cancellation tier in force on `POSTPONEMENT_REQUEST_DATE`.

If the postponed booking is later cancelled:

```text
applicable_tier = max(
    tier_at_postponement_request,
    tier_at_final_cancellation
)
```

Decision: D-017.

## 11.6 Credit expiry

If the client postponement expires unused:

```text
cancellation_tier = tier_at_postponement_request
```

Decision: D-019.

## 11.7 Excess credit

After final settlement:

```text
excess_credit =
max(collected_credit - applicable_retained_or_charge_amount, 0)
```

`excess_credit` is refundable after settlement/clearing.

It is not automatically forfeited.

Decision: D-020.

## 11.8 Non-client reschedules

An `EVOCHIA_INABILITY_TO_PERFORM` reschedule or `EXTERNAL_PERFORMANCE_IMPEDIMENT` reschedule:

- does not consume the client's one postponement;
- does not start or consume the client 6-month window;
- does not activate the client anti-reset rule.

Decision: D-021.

---

# 12. Impediment classification

## 12.1 Single-classification invariant

Each material performance impediment must have one controlling classification before financial calculation.

Permitted regimes:

```text
EXTERNAL_PERFORMANCE_IMPEDIMENT
EVOCHIA_INABILITY_TO_PERFORM
CLIENT_SIDE_IMPEDIMENT
```

## 12.2 Hybrid/disputed causation

If more than one material regime is plausible and the controlling cause cannot be determined without owner judgment:

```text
OWNER_REVIEW_REQUIRED
```

The system must not select the regime that maximizes retention, minimizes refund or otherwise favors Evochia economically.

Decision: D-012.

## 12.3 Payment default exclusion

Payment default is handled only by Section 8 and must not be reclassified into the impediment matrix as an alternative path.

Decision: D-005.

---

# 13. `PARTIAL_PERFORMANCE`

## 13.1 Role

`PARTIAL_PERFORMANCE` modifies financial allocation only after a controlling regime is known.

It is not independently selected against an impediment regime.

Decision: D-013.

## 13.2 Calculation architecture

One calculation uses three allocation rules.

### Allocation Rule 1 — Unitized performed service

Where the confirmed quote contains genuine service units, use the confirmed unit basis for actually performed units.

Examples:

- dinner/day;
- production day;
- delivery;
- service session;
- event day.

### Allocation Rule 2 — Direct attributable costs

Allocate documented actual/committed costs directly to the portion/event to which they are attributable.

Examples:

- food already purchased;
- staff already performed/irrevocably committed;
- travel incurred;
- accommodation incurred;
- rentals;
- supplier cancellation fees.

Do not allocate a direct cost merely by percentage of booking completed when better attribution exists.

### Allocation Rule 3 — Shared/indivisible fixed lines

For shared fixed lines:

1. use an allocation basis already defined by the confirmed commercial model/quote;
2. otherwise use an objective deterministic allocation if one exists;
3. otherwise return `OWNER_REVIEW_REQUIRED`.

Decision: D-014.

---

# 14. Transport verification gate

`TRANSPORT_UNVERIFIED` is an independent material confirmation blocker.

A quote may be issued while transport is provisional if clearly disclosed, but booking confirmation requires material transport to be verified/resolved.

Validity and transport verification are independent dimensions:

```text
quote_valid = true
transport_verified = false
=> confirmation_allowed = false
```

Decision: D-027.

---

# 15. Peak-date and household-chef policy closure

## 15.1 Peak dates

Canonical owner decision:

```text
NO GLOBAL PEAK-DATE SURCHARGE
```

Peak-date adjustments, if any, are quote-specific only.

This is an approved decision, not an unresolved policy gap.

Decision: D-028.

## 15.2 Household chef

Canonical owner decision:

```text
NO GLOBAL HOUSEHOLD-CHEF RATE CARD
```

Household-chef pricing is quote-specific only.

Historical household-chef proposals remain proposal-specific evidence and do not become a global rate card.

Decision: D-029.

---

# 16. Legal identity — `RUNTIME_RESOLVED`

Legal identity is not hardcoded as a global client-facing company/group characterization.

## 16.1 Binding documents

Before producing a binding document, the runtime must resolve the legally correct contracting identity.

If it cannot:

```text
LEGAL_IDENTITY_UNRESOLVED
=> FAIL_CLOSED_FOR_BINDING_DOCUMENT
```

## 16.2 Client-facing language

Do not describe Evochia as a legal company/group unless that characterization is resolved and authorized for the document context.

Brand use may remain "Evochia" where appropriate without inventing legal form.

Decision: D-030.

---

# 17. Audience projection contract

## 17.1 INTERNAL

INTERNAL projection may contain:

- full cost/economic model;
- applicable regime and classification evidence;
- cancellation tier/base;
- allocation details;
- `CANCELLATION_CHARGE`;
- `COLLECTED_CANCELLATION_AMOUNT`;
- `REFUND_DUE`;
- `UNCOLLECTED_CANCELLATION_BALANCE`;
- postponement credit state;
- scope-reduction tracking;
- owner-review rationale;
- collection-decision state.

## 17.2 CLIENT_SAFE

CLIENT_SAFE projection may contain only authorized client-relevant terms and amounts, including as applicable:

- confirmed scope;
- payment schedule/status;
- applicable cancellation/postponement/scope-change term;
- amount received;
- amount retained/applied;
- refund due;
- verified transport terms;
- explicit `valid_until`;
- authorized amount currently payable.

## 17.3 Forbidden-by-default fields

At minimum:

```text
UNCOLLECTED_CANCELLATION_BALANCE
internal margin
internal supplier evidence
internal cost allocation rationale
classification uncertainty notes
```

must not leak into CLIENT_SAFE output unless an explicit downstream contract authorizes a specific field for a specific purpose.

Decision: D-031.

---

# 18. Cross-file synchronization contract

Implementation must update all stale owner-state references created by earlier Phase 13.2 partial approval.

## 18.1 `terms_policy.md`

Becomes runtime authority for:

- canonical commercial definitions;
- confirmation payment;
- balance T-5;
- payment default/cure;
- cancellation tiers;
- postponement;
- scope reduction;
- impediment vocabulary/classification;
- partial-performance interaction;
- quote validity;
- transport confirmation dependency;
- client/internal cancellation amount boundary.

## 18.2 `commercial_policy.md`

Must reference `terms_policy.md` rather than duplicate formulas.

Remove stale `OPEN` / `NEEDS_OWNER_APPROVAL` entries for:

- balance timing;
- cancellation/refundability architecture closed here;
- standard quote validity;
- peak-date global policy.

Retain only genuinely unresolved commercial items.

## 18.3 `current_rates.md`

Must record:

- no global peak-date surcharge — quote-specific only;
- no global household-chef rate card — quote-specific only;

and must not continue to label either as OPEN.

Historical household proposal values remain evidence only.

## 18.4 `company_profile.md`

Must replace stale legal-identity ambiguity with the `RUNTIME_RESOLVED` operational model.

Client-facing company/group characterization remains forbidden unless runtime-resolved and authorized.

## 18.5 `policy_state_contract.yaml`

File-level status changes only after row-level synchronization.

The existing allowed status vocabulary remains sufficient:

```text
OWNER_REVIEW_DRAFT
PARTIALLY_APPROVED
APPROVED
```

No new file-status vocabulary is introduced merely for this phase.

## 18.6 Release/routing/evals

Any release readiness, routing or eval assertions that still describe these closed decisions as OPEN must be updated in the same change set.

Decision: D-032.

---

# 19. Scenario traces

## 19.1 Standard confirmation >5 days before service

```text
SERVICE_START = 20 Sep
confirmation = 10 Sep

>5 days before start
=> confirmation payment = 30%
=> balance due = 15 Sep (T-5)
```

One path.

## 19.2 Late booking

```text
SERVICE_START = 20 Sep
confirmation = 17 Sep

<=5 days
=> 100% required at confirmation
=> no later balance stage
```

## 19.3 Payment default and banking clearing

```text
balance missed at T-5
=> PAYMENT_DEFAULT
=> CURE_PENDING
=> 48h base + banking-clearing floor
=> CURE_DEADLINE never later than SERVICE_START
```

If Evochia cancels for default, cancellation tier is selected using the date the cancellation right is exercised.

No `CLIENT_SIDE_IMPEDIMENT` path is created.

## 19.4 Ordinary cancellation at 12 days

```text
12 days before SERVICE_START
=> 6-14 tier
=> 30% × FIXED_CONFIRMED_BOOKING_VALUE
```

Then calculate collected/retained/refund/uncollected values separately.

## 19.5 Client postponement at 16 days, later cancellation at 4 days

```text
tier_at_postponement = 10%
tier_at_final_cancellation = 100%

anti-reset => max(10%, 100%) = 100%
```

## 19.6 Client postponement at 4 days, later cancellation at 30 days

```text
tier_at_postponement = 100%
tier_at_final_cancellation = 10%

anti-reset => max(100%, 10%) = 100%
```

The postponement cannot reset the cancellation exposure to a lower tier.

## 19.7 Postponement expires unused

```text
client requested postponement at 12 days
=> tier captured = 30%
credit later expires unused
=> cancellation settlement uses 30%
```

Any excess collected credit after settlement is refundable.

## 19.8 Evochia/external reschedule

```text
classification = EVOCHIA_INABILITY_TO_PERFORM
or EXTERNAL_PERFORMANCE_IMPEDIMENT
=> reschedule
```

Client postponement entitlement remains unused; client 6-month clock and anti-reset do not activate.

## 19.9 Scope reduction

```text
original fixed value = 4,000
revised fixed value = 3,000
removed_fixed_value = 1,000
reduction approved 10 days before service
=> 30% × 1,000
```

The retained €3,000 scope is not cancellation-charged.

## 19.10 Successive scope reductions

Each approved reduction selects its own tier by date and applies only to newly removed fixed scope.

Previously removed fixed scope cannot be charged again.

## 19.11 Hybrid impediment

If an external event and a material client-side act both plausibly control the inability to perform and evidence does not resolve causation:

```text
OWNER_REVIEW_REQUIRED
```

No automatic selection by financial outcome.

## 19.12 Partial performance after external impediment

```text
3 of 7 service units performed
then EXTERNAL_PERFORMANCE_IMPEDIMENT
```

Classification occurs first. Then `PARTIAL_PERFORMANCE` allocation rules determine performed units, direct costs and shared fixed lines.

---

# 20. Required tests / acceptance criteria

Implementation is incomplete unless the suite covers at least the following.

## 20.1 Confirmation/payment

1. >5-day confirmation requires 30%.
2. <=5-day confirmation requires 100%.
3. 30% path creates T-5 balance due date.
4. 100% path creates no later balance stage.
5. payment default remains operational state, not impediment regime.
6. cancellation for payment default uses tier on exercise date.
7. cure uses 48h base.
8. banking-clearing floor can extend the base cure.
9. `CURE_DEADLINE <= SERVICE_START` always.
10. cure never requires increased unrecoverable exposure.

## 20.2 Quote/confirmation gates

11. default `valid_until = min(issue_date + 7, SERVICE_START - 6)`.
12. every quote has explicit `valid_until`.
13. shorter override accepted.
14. extension requires explicit later date.
15. valid quote + `TRANSPORT_UNVERIFIED` cannot confirm.

## 20.3 Cancellation accounting

16. 15+ boundary selects 10%.
17. 6-14 boundary selects 30%.
18. 0-5 boundary selects 100%.
19. calculation separates charge / collected / refund / uncollected balance.
20. `UNCOLLECTED_CANCELLATION_BALANCE` absent from CLIENT_SAFE by default.
21. explicit collection authorization required before exposing an uncollected balance as payable.

## 20.4 Postponement

22. only one client postponement per booking.
23. replacement date bounded to 6 months from original `SERVICE_START`.
24. written owner extension uses explicit expiry and does not reset history.
25. anti-reset uses `max(tier_at_request, tier_at_final_cancellation)`.
26. expired credit uses tier at postponement request.
27. excess credit refund is calculated after settlement.
28. Evochia/external reschedule does not consume client postponement or activate anti-reset/6-month rule.
29. rescheduled booking reprices under current terms/rates.

## 20.5 Scope reduction

30. `REMOVED_FIXED_VALUE` formula correct.
31. tier applies only to removed value.
32. same confirmed pricing methodology used for revised value.
33. non-scaling elements stay fixed unless explicitly revised.
34. staffing triggers are recalculated, not proportionally scaled.
35. lower day-of attendance alone does not reduce fixed value.
36. successive reductions can accumulate.
37. each fixed-scope unit can be charged only once.

## 20.6 Impediments / partial performance

38. canonical regime vocabulary only.
39. one controlling classification per event.
40. hybrid/disputed material cause -> `OWNER_REVIEW_REQUIRED`.
41. no economically favorable auto-selection.
42. `PARTIAL_PERFORMANCE` cannot be selected as a regime.
43. unitized allocation rule covered.
44. direct attributable-cost allocation covered.
45. shared/indivisible allocation covered.
46. ambiguous shared allocation -> owner review.

## 20.7 Legal identity / export boundary

47. binding artifact fails closed when legal identity unresolved.
48. client-facing company/group characterization blocked unless runtime-resolved/authorized.
49. INTERNAL projection can contain internal-only fields.
50. CLIENT_SAFE projection blocks internal-only fields.

## 20.8 Cross-file synchronization

51. `terms_policy.md` has no stale OPEN for decisions closed here.
52. `commercial_policy.md` has no stale OPEN for balance/cancellation/validity/peak global policy.
53. `current_rates.md` records no global peak surcharge and no global household rate card as approved decisions, not OPEN.
54. `company_profile.md` reflects `RUNTIME_RESOLVED` legal identity model.
55. unrelated unresolved rows remain unresolved.
56. `policy_state_contract.yaml`, routing, release readiness and evals agree with runtime policy state.

Decision: D-034.

---

# 21. Non-goals

This phase does not:

- create a public immutable tariff;
- create a global peak-date surcharge;
- create a global household-chef rate card;
- hardcode a legal company/group identity;
- turn `UNCOLLECTED_CANCELLATION_BALANCE` into an automatic debt demand;
- classify payment default as an impediment regime;
- invent legal force-majeure wording beyond the approved operational classification model;
- replace professional legal review of binding contract language.

---

# 22. Implementation boundary

The implementation phase should change runtime policy/data/contracts/tests only after this spec is reviewed and approved.

Expected primary files include:

- `company/evochia/policies/terms_policy.md`
- `company/evochia/policies/commercial_policy.md`
- `company/evochia/policies/current_rates.md`
- `company/evochia/policies/company_profile.md`
- `company/evochia/policies/policy_state_contract.yaml`
- relevant routing/release readiness files
- Evochia policy/state/export/eval tests

Implementation must preserve unrelated approved policy decisions and unrelated OPEN rows.
