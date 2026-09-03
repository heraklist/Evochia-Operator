# Evochia Terms Policy

**Policy status:** `PARTIALLY_APPROVED`
**Approved by:** `Evochia Owner`
**Effective date:** `2026-09-03`
**Approval reference:** `owner-approval-2026-09-03-phase13.3`

This file is the canonical runtime authority for Evochia booking lifecycle and impediment economics. Historical booking terms remain evidence only and do not override the approved rules below.

## 1. Canonical definitions

### `SERVICE_START`

`SERVICE_START` is the first scheduled service date **as defined in the quote**. Travel, shopping, setup, preparation, accommodation check-in or another operational activity does not redefine `SERVICE_START` unless the quote itself explicitly defines that activity as service start.

### `FIXED_CONFIRMED_BOOKING_VALUE`

The fixed monetary value confirmed for the agreed booking scope. It may include finalized fixed service, staffing, transport, equipment or other fixed lines. It excludes variable/pass-through actual-cost items that are not fixed at confirmation.

### `CONFIRMATION_DATE`

The date booking confirmation completes after written acceptance, all material non-payment confirmation gates are resolved, the required confirmation payment is satisfied, and binding-document legal particulars are available where required.

### `CLEARED_PAYMENT`

Funds received/cleared in a form reasonably available for Evochia to rely upon operationally. A transfer instruction or client statement that payment has been sent is evidence of attempted payment, not automatically `CLEARED_PAYMENT`.

### `BANKING_CLEARING_FLOOR`

The earliest reasonable next opportunity for a normally pending bank transfer to clear. The policy does not hard-code its own bank-holiday calendar.

### `CANCELLATION_TIER`

An ordered first-match tier based on calendar days remaining before `SERVICE_START` on the controlling cancellation date.

### `CANCELLATION_RETENTION_CAP`

```text
CANCELLATION_RETENTION_CAP = 100% of affected fixed scope value
```

It constrains cumulative cancellation/scope-reduction retention only. Separately eligible third-party actual-cost items may sit outside this cap when the quote/commercial model treats them separately, subject to the no-double-recovery and no-markup rules below.

### Cancellation accounting fields

Every cancellation calculation keeps these values separate:

```text
CANCELLATION_CHARGE
COLLECTED_CANCELLATION_AMOUNT
REFUND_DUE
UNCOLLECTED_CANCELLATION_BALANCE
```

Canonical formulas:

```text
REFUND_DUE = max(
    collected_amount - COLLECTED_CANCELLATION_AMOUNT - other_valid_client_allocations,
    0
)

UNCOLLECTED_CANCELLATION_BALANCE =
max(CANCELLATION_CHARGE - COLLECTED_CANCELLATION_AMOUNT, 0)
```

`other_valid_client_allocations` can include separately eligible actual-cost third-party items but may never duplicate an amount already recovered through cancellation retention.

`UNCOLLECTED_CANCELLATION_BALANCE` is INTERNAL by default. It is not automatically an invoice, receivable, debt demand or CLIENT_SAFE field. It may enter a client collection workflow only after an explicit owner decision to pursue collection.

### `REMOVED_FIXED_VALUE`

```text
REMOVED_FIXED_VALUE =
fixed value before approved change - revised fixed value
```

### `POSTPONEMENT_REQUEST_DATE`

The date on which a client postponement request is accepted for policy treatment. It freezes the cancellation tier used by the anti-reset and expiry rules.

### External-impediment evidence categories

The evidence categories are exactly:

```text
PERFORMED_SCOPE
NON_RECOVERABLE_BOOKING_COST
OTHER
```

`PERFORMED_SCOPE` means service actually delivered and supportable by booking/service records.

A `NON_RECOVERABLE_BOOKING_COST` must be booking-specific, actually incurred or irrevocably committed, evidenced, and net of refunds, credits, resale, reuse, insurance or recoverable/reusable asset value.

`OTHER` always requires `OWNER_REVIEW_REQUIRED` before any client allocation.

## 2. Quote validity

Every quote must carry an explicit `valid_until` date.

Default formula:

```text
valid_until = min(
    issue_date + 7 calendar days,
    SERVICE_START - 6 calendar days
)
```

A quote-specific override may shorten validity freely. Extending validity requires an explicit later `valid_until` date; validity is never open-ended or implied.

Late-quote interaction:

```text
if default_valid_until < issue_date:
    default validity is unusable
    -> explicit later valid_until override required
```

The formula is not silently clamped. This preserves the late-booking path while preventing an already-expired default from being treated as valid.

Quote validity and booking-confirmation readiness are independent. A quote may be valid while confirmation is blocked by another material gate.

## 3. Booking confirmation and confirmation payment

Booking confirmation requires:

- written acceptance;
- all material confirmation gates resolved;
- the applicable confirmation payment cleared;
- required legal particulars resolved for binding documents.

If confirmation occurs **more than 5 calendar days** before `SERVICE_START`:

```text
CONFIRMATION_PAYMENT = 30% × FIXED_CONFIRMED_BOOKING_VALUE
BALANCE_DUE_DATE = SERVICE_START - 5 calendar days
```

If confirmation occurs **5 or fewer calendar days** before `SERVICE_START`:

```text
CONFIRMATION_PAYMENT = 100% × FIXED_CONFIRMED_BOOKING_VALUE
```

There is **no separate balance stage** on the 100% late-confirmation path.

## 4. Balance payment, `PAYMENT_DEFAULT` and cure

For the 30% path only:

```text
BALANCE_DUE_DATE = SERVICE_START - 5 calendar days
```

If the balance is not cleared by that deadline:

```text
PAYMENT_DEFAULT -> CURE_PENDING
```

Payment default is an operational state, **not an impediment regime** and not `CLIENT_SIDE_IMPEDIMENT`.

Payment default gives Evochia a right to cancel under the ordinary cancellation model. If Evochia exercises that right, the ordinary cancellation tier is selected from the **date the cancellation right is exercised**. There is no second payment-default penalty or separate penalty regime.

Cure deadline:

```text
base_cure_deadline = payment_default_notice + 48 hours
candidate_cure_deadline = later_of(base_cure_deadline, BANKING_CLEARING_FLOOR)
CURE_DEADLINE = min(candidate_cure_deadline, SERVICE_START)
```

The cure period never extends beyond `SERVICE_START`.

### Exposure boundary during cure

Cure extends the client's opportunity to remedy payment default. It does not require Evochia to increase unrecoverable exposure while payment remains unresolved. Evochia may pause/refuse new material commitments including:

- supplier or ingredient commitments;
- staffing commitments;
- travel commitments;
- accommodation commitments;
- equipment/rental commitments;
- irreversible preparation;
- food-safety-sensitive exposure;
- beginning service on unsecured credit.

Already incurred/committed obligations remain recorded under their applicable treatment.

If Evochia exercises this right to pause/refuse new exposure during cure, Evochia must communicate that decision promptly to the client **in writing**, so operational non-action is not ambiguous.

## 5. Ordinary client cancellation

Cancellation tiers are ordered first-match rules:

| Calendar days before `SERVICE_START` | Tier |
| ---: | ---: |
| 15+ | 10% |
| 6–14 | 30% |
| 0–5 | 100% |

For ordinary full-booking cancellation:

```text
CANCELLATION_CHARGE =
CANCELLATION_TIER × FIXED_CONFIRMED_BOOKING_VALUE
```

The selected tier determines the fixed-scope cancellation retention/charge. It does not merge the separate cancellation accounting fields into one debt concept.

CLIENT_SAFE output may show authorized amounts such as amount received, amount retained/applied and `REFUND_DUE`. `UNCOLLECTED_CANCELLATION_BALANCE` remains INTERNAL unless the owner explicitly authorizes collection.

## 6. Third-party costs, retention cap and recovery invariants

Cancellation retention and separately eligible third-party booking costs use a **separate ledger**.

Eligible third-party actual costs can sit **outside** `CANCELLATION_RETENTION_CAP` when the quote/commercial model treats those costs separately from fixed service scope.

Common invariants:

```text
NO_DOUBLE_RECOVERY
NO_MARKUP_ON_REIMBURSABLE_EXPOSURE
ACTUAL_ACQUISITION_OR_COMMITMENT_COST_ONLY
OFFSET_ALL_RECOVERIES
```

Therefore:

- the same item cannot be recovered once through fixed-scope retention and again as a third-party cost;
- a cost already refunded, credited, resold, reused, insured or otherwise recouped must be offset;
- reimbursable exposure uses evidenced actual acquisition/commitment cost, not replacement-price markup or a percentage uplift;
- recoverable/reusable assets are not treated as loss merely because they were originally obtained for the booking.

## 7. Scope reduction / partial cancellation

A scope reduction exists only after written approval/revision. Lower actual attendance on the service day **does not by itself** reduce `FIXED_CONFIRMED_BOOKING_VALUE`.

Calculation:

```text
REMOVED_FIXED_VALUE =
fixed value before approved change - revised fixed value

scope_reduction_charge =
applicable cancellation tier on approved reduction date × REMOVED_FIXED_VALUE
```

The cancellation tier applies **only to removed fixed value**, never retained scope.

The revised fixed value must use the **same pricing methodology** as the confirmed quote.

Requirements:

- genuinely non-scaling fixed elements remain unchanged unless explicitly revised;
- staffing triggers are recalculated from the revised scope rather than reduced by simplistic proportional scaling;
- package/all-in methodology remains reconcilable to the confirmed methodology.

### Successive reductions

Successive scope reductions may **accumulate** under the tier applicable to each approved reduction date.

Invariants:

```text
each unit of fixed scope is charged at most once
aggregate fixed-scope retention <= CANCELLATION_RETENTION_CAP
```

Previously removed/charged fixed scope must be excluded from later removal calculations. Separate eligible third-party costs remain outside the fixed-scope cap but are still subject to no double recovery.

## 8. Client postponement

Client postponement is permitted **once per booking**.

The replacement date must fall within **6 calendar months** of the **original `SERVICE_START`**.

A discretionary extension is allowed only in writing with an **explicit new expiry date**. An extension does not reset postponement history.

Postponement preserves eligible credit, not historical/old pricing. The rescheduled booking is **repriced under current terms/rates** for the new date and scope.

### Anti-reset

```text
applicable_tier = max(
    tier_at_postponement_request,
    tier_at_final_cancellation
)
```

If postponement credit expires unused:

```text
applicable_tier = tier_at_postponement_request
```

After final reconciliation, **excess credit is refunded** rather than forfeited by default.

### Non-client reschedules

A reschedule caused by `EVOCHIA_INABILITY_TO_PERFORM` or `EXTERNAL_PERFORMANCE_IMPEDIMENT` **does not consume** the client's one postponement, does not start/consume the client six-month window, and does not activate the client anti-reset rule.

## 9. Impediment threshold and classification

A performance impediment requires an **objectively verifiable material event** affecting performance.

The following are **not external impediments by themselves**:

- increased cost;
- fear;
- preference;
- convenience;
- anticipated lower attendance;
- actual lower attendance.

A price/cost increase can require repricing or another owner decision, but increased cost alone is not `EXTERNAL_PERFORMANCE_IMPEDIMENT`.

Canonical regimes are exactly:

```text
EXTERNAL_PERFORMANCE_IMPEDIMENT
EVOCHIA_INABILITY_TO_PERFORM
CLIENT_SIDE_IMPEDIMENT
```

Each valid event receives a **single classification** before financial resolution.

If causation is hybrid, disputed or insufficiently evidenced such that multiple material regimes remain plausible:

```text
OWNER_REVIEW_REQUIRED
```

`OWNER_REVIEW_REQUIRED` is a review state, not a fourth regime. The system must never auto-select the economically/commercially favorable regime.

## 10. Common impediment workflow

After classification, the operational workflow ends in one of exactly four outcome classes:

```text
PERFORM_OR_MITIGATE
REPLACEMENT_PERFORMANCE
RESCHEDULE
TERMINATE_AND_RECONCILE
```

These are workflow **outcomes**, not regimes.

### Mitigation boundary

Mitigation is required only when reasonable and proportionate. Neither party is automatically required to incur a **material incremental** cash cost or materially greater operational exposure to mitigate.

If a mitigation path requires material incremental cost, **explicit agreement on cost allocation** is required before commitment. Without that agreement, select another valid workflow outcome.

## 11. `EVOCHIA_INABILITY_TO_PERFORM`

This regime applies when Evochia is the controlling cause of inability to deliver the contracted performance.

### Financial resolution

For collected unperformed fixed scope:

```text
client_refund_or_credit = 100% of unperformed fixed scope already collected
```

The ordinary 10% / 30% / 100% cancellation tiers **do not apply** to Evochia-caused unperformed scope.

Evochia **bears / absorbs** its own:

- sunk costs;
- lost margin;
- opportunity cost;
- non-recoverable internal commitments;
- non-recoverable third-party commitments that belong to Evochia's own performance responsibility, unless a separately agreed client-owned item applies independently.

Those amounts are not passed through merely because Evochia cannot perform.

### Client consequential costs

Independent third-party/consequential costs incurred by the client are **not automatically** reimbursable by Evochia. Any goodwill compensation is owner-discretionary and explicit.

### Replacement

`REPLACEMENT_PERFORMANCE` is permitted only when the replacement **materially corresponds** to the contracted scope and requires **client acceptance**. A materially different service cannot be imposed unilaterally.

### Notification

Evochia must **promptly notify** the client when a **material risk** of inability to perform becomes known, rather than waiting until failure is certain.

## 12. `EXTERNAL_PERFORMANCE_IMPEDIMENT`

This regime applies only to an objectively verifiable material event outside the reasonable control of both parties that actually impedes performance.

### Actual-exposure reconciliation

The ordinary 10/30/100 cancellation tiers **do not govern** this regime.

Client allocation is limited to:

```text
PERFORMED_SCOPE
+ eligible NON_RECOVERABLE_BOOKING_COST
```

Remaining collected funds are refunded/credited after reconciliation.

Evochia absorbs:

- lost margin;
- opportunity cost;
- theoretical profit;
- generalized administration/overhead;
- unsupported estimates.

The client bears its own independent/consequential costs unless separately agreed.

### Evidence gate

Each proposed client allocation must be exactly one of:

```text
PERFORMED_SCOPE
NON_RECOVERABLE_BOOKING_COST
OTHER
```

`OTHER -> OWNER_REVIEW_REQUIRED`.

A `NON_RECOVERABLE_BOOKING_COST` requires:

- booking-specific nexus;
- actually incurred or irrevocably committed exposure;
- documentary evidence;
- actual acquisition/commitment cost;
- offset of supplier refund or credit;
- offset of resale value;
- offset of reuse value;
- offset of insurance or another recovery route;
- offset of recoverable/reusable asset value.

There is **no generic force majeure fee** or external-impediment percentage.

Forbidden client-recoverable exposure includes:

- markup;
- replacement-price uplift above actual acquisition/commitment cost;
- margin;
- opportunity cost;
- theoretical profit;
- generalized unsupported administration;
- the unreduced cost of an asset that remains economically recoverable/reusable.

The no-double-recovery rule applies across performed scope, cancellation retention, third-party lines, supplier recoveries and all other recovery channels.

## 13. `CLIENT_SIDE_IMPEDIMENT`

`CLIENT_SIDE_IMPEDIMENT` does not create a second or bespoke penalty model.

Apply the **ordinary cancellation / partial-cancellation / scope-reduction rules** using the controlling date/window. If performance has already begun, apply `PARTIAL_PERFORMANCE` after classification to separate what was performed from the unperformed/removed client-side scope.

`PAYMENT_DEFAULT` is expressly **excluded** from this route. Payment default remains the operational state in Section 4 and, if Evochia exercises cancellation, uses the ordinary exercise-date cancellation tier.

## 14. `PARTIAL_PERFORMANCE`

`PARTIAL_PERFORMANCE` is a calculation **modifier**, **not a regime**. It is applied only after the controlling impediment regime is known.

One modifier uses three allocation rules:

### Rule 1 — Unitized performed service

For genuine contracted units such as a dinner/day, service session, production day or delivery:

```text
performed_value = contracted_unit_value × actually_performed_units
```

### Rule 2 — Direct attributable costs

Direct attributable costs are allocated by documentary attribution to the performed/affected portion rather than by arbitrary completion percentage where better attribution exists.

### Rule 3 — Shared / indivisible fixed lines

Use, in order:

1. the allocation basis declared in the confirmed quote/commercial model;
2. an objective deterministic allocation basis if one exists;
3. otherwise `OWNER_REVIEW_REQUIRED`.

Ambiguous shared/indivisible allocation never invents a favorable percentage.

### Regime-specific partial-performance settlement

For an external event:

```text
classify EXTERNAL_PERFORMANCE_IMPEDIMENT
-> allocate PERFORMED_SCOPE
-> add eligible NON_RECOVERABLE_BOOKING_COST
-> offset all recoveries
-> refund/credit remaining collected amount
```

For Evochia inability, performed scope is reconciled first and 100% of the remaining collected unperformed fixed scope is refunded/credited.

For client-side impediment, performed scope is reconciled first and ordinary cancellation/change logic applies to the remaining affected scope.

## 15. Ingredients, supplier costs and pass-through treatment

When groceries/ingredients/third-party purchases are pass-through, they remain separate actual-cost items supported by receipts/expense evidence. If Evochia advances purchases, reimbursement/prepayment treatment must be explicit in the quote/service agreement.

An all-in/per-person/package quotation can present costs differently to the client, but INTERNAL costing remains granular under `commercial_policy.md`.

This general pass-through rule does not override the regime-specific recovery rules in Sections 11–14.

## 16. VAT / taxes

Use the **current applicable** VAT/tax treatment for the specific service/date/entity/jurisdiction and state whether quoted figures are net/gross and VAT included/excluded where material.

A historical 24% calculation is not a universal rule.

## 17. Travel, accommodation, staff and equipment

Inclusions/exclusions must be explicit. Extra staffing, special equipment/rentals, travel/ferry/tolls/parking, accommodation and third-party styling/services are separate unless specifically included in the chosen quotation format.

Service uplifts for yacht/island/remote disruption do not silently replace actual transport/ticket/accommodation lines.

## 18. `TRANSPORT_UNVERIFIED` confirmation gate

A transport line marked `TRANSPORT_UNVERIFIED` is provisional and cannot be treated as a final verified transport commitment.

The transport gate is **independent from quote validity**:

```text
quote valid + TRANSPORT_UNVERIFIED
-> CONFIRMATION_BLOCKED
```

Verification must occur before final acceptance / booking confirmation.

After verification:

- the final client transport line follows the verified-cost floor in `staffing_policy.md`;
- a charge below verified INTERNAL transport cost requires explicit `OWNER_APPROVED_PROMO_SUBSIDY`;
- an unverified low estimate never becomes a retroactive subsidy automatically.

A client may review a provisional proposal while transport is unresolved, but the booking cannot be confirmed until the material transport term is resolved.

## 19. Multi-day travel model

Where material, the quote identifies the Stay model or Commute model from `staffing_policy.md`. They are mutually exclusive for the same service period unless an exceptional mixed arrangement is explicitly described and economically justified.

## 20. CLIENT_SAFE projection boundary

INTERNAL may contain:

- full economics;
- classification evidence;
- owner-review rationale;
- allocation notes;
- `UNCOLLECTED_CANCELLATION_BALANCE`;
- third-party evidence and recovery offsets;
- internal mitigation analysis.

CLIENT_SAFE may contain only authorized client terms and amounts, including where applicable:

- confirmed scope;
- quote validity;
- payment schedule/status;
- applicable cancellation/reconciliation basis;
- amount received;
- amount retained/applied;
- verified separately chargeable third-party actual costs where contractually applicable;
- refund/credit due;
- an amount payable only when a valid collection decision exists.

CLIENT_SAFE must not expose `UNCOLLECTED_CANCELLATION_BALANCE` merely because it exists internally. Owner collection authorization is required before any collection/demand projection.

## 21. Per-quote overrides and service-model boundaries

Canonical defaults apply unless the approved policy expressly permits an explicit quote-specific override.

A quote-specific override must be explicit; it cannot silently contradict an approved mandatory safety, identity, recovery or confirmation gate.

Household recurring engagements are governed by the dedicated household framework in `commercial_policy.md` / `current_rates.md`; their recurring billing/termination structure does not inherit one-off event T-5 or cancellation tiers by default.

## 22. Intentionally unresolved outside Phase 13.3

`NEEDS_OWNER_APPROVAL` remains only for **final jurisdiction-specific legal drafting/review of binding contract language** (including final clause wording), not for the commercial economics or workflow rules above.

This narrow legal-drafting review does **not** reopen:

- confirmation-payment timing;
- balance timing;
- cancellation windows or refund calculations;
- quote-validity default;
- postponement/scope-reduction rules;
- impediment classifications or economics;
- no-double-recovery/no-markup rules;
- transport confirmation gate.
