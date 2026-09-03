# Evochia Commercial Policy

**Policy status:** `PARTIALLY_APPROVED`
**Approved by:** `Evochia Owner`
**Effective date:** `2026-09-03`
**Approval reference:** `owner-approval-2026-09-03-phase13.2`

The Phase 13.3 commercial body below is owner-approved. File-level status and approval metadata remain on the Phase 13.2 header until the dedicated row-audit/state-reconciliation task. Canonical booking lifecycle formulas and impediment economics live in `terms_policy.md`; this file owns the higher-level commercial architecture, rate-boundary rules and service-model governance.

## 1. Core commercial model

**Approved rule — `APPROVED_OWNER_DECISION`:** Evochia sells professional hospitality/service. Food or ingredient cost is not the mechanism used to hide chef labour, operating cost or commercial value.

Where the service model uses pass-through purchasing, groceries, ingredients and third-party supplier purchases are evidenced at actual acquisition/commitment cost. Other quotation formats remain valid when explicitly chosen for the client/service.

### INTERNAL costing architecture != CLIENT quotation format

INTERNAL economics remain granular even when the client sees a packaged price. Internal evaluation models, where applicable:

`food + founder/chef labour + assistants/service + prep/shopping + travel + accommodation + equipment + consumables + overhead + opportunity cost`

The CLIENT quotation may legitimately be presented as:

- all-in price;
- per-person price;
- package price;
- fixed service fee plus pass-through costs;
- another explicitly defined commercial projection.

A client-facing package never erases the underlying INTERNAL cost/economic model. Conversely, the INTERNAL ledger does not require every cost component to appear as a separate client line.

## 2. Cost, recovery and fee boundaries

- Founder/chef labour is never zero in INTERNAL economic analysis.
- Additional staff, equipment/rentals, travel, accommodation and unusual logistics are modelled explicitly even when the client sees a consolidated fee.
- Food/grocery/third-party supplier treatment must be stated clearly for each quote or service family.
- Promotions, agency arrangements and deliberate subsidies must not erase the INTERNAL economic result.
- A client charge below a verified INTERNAL cost floor requires an explicit owner-approved exception where a dedicated policy defines such a floor.
- Historical proposal prices remain evidence only and never silently become current policy.

Commercial recovery invariants, with formulas governed by `terms_policy.md`:

```text
NO_DOUBLE_RECOVERY
NO_MARKUP_ON_REIMBURSABLE_EXPOSURE
ACTUAL_ACQUISITION_OR_COMMITMENT_COST_ONLY
OFFSET_ALL_RECOVERIES
```

A refund, supplier credit, insurance payment, resale, reuse or recoverable asset value must reduce the amount allocated as client-recoverable exposure.

`CANCELLATION_RETENTION_CAP` applies to affected fixed-scope cancellation/scope-reduction retention only. Separately eligible third-party actual-cost items use a distinct ledger and can sit outside that cap when the confirmed commercial model treats them separately. The same economic item may never be recovered through both ledgers.

## 3. Service uplifts and actual logistics

**Approved rules — `APPROVED_OWNER_DECISION`:**

- Yachting service uplift: `+20%`.
- Island / overnight / materially remote service uplift: `+40%`.
- These uplifts compensate disruption, lost productive time/availability and operational complexity. They do **not** replace actual transport, tickets, tolls, accommodation or other third-party travel costs.
- When more than one disruption uplift applies to the same service context (for example yacht + island), apply the **single highest applicable uplift**; do not stack overlapping disruption uplifts.
- Remote Attica is handled as base service fee plus actual/quoted logistics rather than automatically receiving the island uplift.

The approved uplift values above are not changed by Phase 13.3.

## 4. Peak-date quote-specific adjustment

**Approved rule — `APPROVED_OWNER_DECISION`: there is no global peak-date surcharge.**

A peak-date adjustment is quote-specific only and requires exactly these INTERNAL evidence fields:

```text
reason
amount_or_method
date_specific_basis
costs_already_covered_elsewhere
double_count_check
owner_decision/reference
```

Field semantics:

- `reason` — the commercial reason for considering a peak adjustment.
- `amount_or_method` — the explicit amount or deterministic method proposed.
- `date_specific_basis` — the positive evidence for why the **specific service date** creates scarcity, demand or availability pressure. Geography, island status, yacht context or remoteness alone is not sufficient positive peak evidence.
- `costs_already_covered_elsewhere` — identifies operational burden/cost already recovered through another service uplift or quote line.
- `double_count_check` — proves that the same causal burden is not recovered again under the peak adjustment.
- `owner_decision/reference` — records explicit owner approval/reference for the quote-specific adjustment.

### Peak versus yacht/island/remote causal overlap

A quote-specific peak adjustment may coexist with yacht/island/remote disruption uplift only when their documented **causes are genuinely distinct**.

Examples:

- a date-specific scarcity/demand burden and a separately evidenced island logistics/disruption burden can coexist;
- the same availability loss or disruption burden cannot be charged twice merely by labelling one line “peak” and another “island/yacht”.

The `date_specific_basis` establishes the positive date case; `double_count_check` establishes non-overlap. Both are required.

## 5. VAT / tax presentation

**Approved rule — `APPROVED_OWNER_DECISION`:** do not hardcode a universal VAT rate from historical proposals. Apply the **current applicable** tax treatment for the actual service, date, entity and jurisdiction. Client outputs state whether relevant prices are net/gross and VAT included/excluded where material.

Tax-sensitive claims require current verification when material.

## 6. Service-specific pricing

Approved Private Chef and Meal Prep pricing lives in `current_rates.md`.

The Private Chef table operates as an **INTERNAL BASE RATE CARD**: an authoritative starting point for reasoning, not a public immutable tariff. Staffing, complexity, location, logistics and scope may change the final quote.

Household-chef service is deliberately excluded from a global rate card and follows Section 8.

## 7. Event quote governance

Canonical event/private-chef lifecycle defaults are governed by `terms_policy.md`, including:

- explicit quote validity and permitted override handling;
- confirmation payment based on distance from `SERVICE_START`;
- T-5 balance only on the 30% confirmation path;
- ordinary cancellation tiers;
- scope reduction and postponement;
- transport confirmation gate;
- impediment classifications/economics;
- INTERNAL versus CLIENT_SAFE financial projection.

Each quote still states material scope and presentation choices, including:

- service scope and guest/service assumptions;
- what is included/excluded;
- quotation format (all-in / per-person / package / service + pass-through);
- food/supplier-cost treatment;
- staffing and logistics assumptions;
- VAT/tax presentation;
- explicit quote-specific overrides where the canonical policy permits them;
- material change/repricing triggers.

A missing or ambiguous material quote-specific fact can block confirmation, but an approved canonical default must not be represented as unresolved merely because older proposals used different wording.

## 8. Household-chef recurring framework

**Approved rule — `APPROVED_OWNER_DECISION`: there is no global household-chef rate card.** Household pricing is quote-specific.

Every household quote/agreement must explicitly define all ten fields:

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

### Field requirements

- `scope` — household members, meals, kitchen-management work and exclusions.
- `service_days_and_hours` — weekly rhythm and working-hour boundary.
- `extra_day_and_hour_rules` — how approved additional days/hours are priced.
- `guest_event_rules` — treatment of guest meals, formal dinners and event-like service.
- `food_and_pass_through_treatment` — ingredients, supplier purchases and reimbursement/prepayment treatment.
- `travel` — local/domestic/international travel terms where applicable.
- `billing_cycle` — recurring invoice/payment cadence.
- `termination_and_notice` — trial, term, termination and notice structure.
- `rate_review_and_escalation` — both the review timing/trigger **and the mechanism or rule by which the rate may change**. A bare right to review with no adjustment/escalation mechanism is insufficient.
- `absence_or_non_use` — what happens when the household does not use scheduled service or is absent.

Household service is a **recurring** engagement model with its own billing/termination framework. One-off event T-5 balance and 10/30/100 cancellation tiers **do not apply by default** to household collaboration.

Historical household proposals remain `PROPOSAL_SPECIFIC_EVIDENCE`; they can inform structure but never become a global current tariff.

## 9. Legal identity dependency

The legal/entity facts themselves are governed by `company_profile.md`. Commercial documents must use the sole-proprietorship/brand/trade-name distinction from that file.

`RUNTIME_RESOLVED` resolves the current legal particulars required for a binding artifact, not the entity type. Binding commercial documents fail closed when required current particulars are unavailable.

The trade name `Evochia Food & Hospitality Group` does not authorize company/corporate/group characterization.

## 10. CLIENT_SAFE commercial projection

CLIENT_SAFE projection follows `terms_policy.md` and artifact contracts.

Permitted where relevant and authorized:

- confirmed service scope;
- explicit validity/payment terms;
- applicable cancellation/reconciliation basis;
- amount received;
- amount retained/applied;
- refund/credit due;
- separately eligible evidenced third-party actual costs when contractually applicable;
- a payable amount only when collection is validly authorized.

Forbidden by default:

- internal margin/opportunity cost;
- hidden cost basis;
- owner-review rationale;
- classification evidence;
- internal allocation notes;
- `UNCOLLECTED_CANCELLATION_BALANCE` absent explicit owner collection authorization.

## 11. Authority boundary

`terms_policy.md` is the canonical authority for lifecycle formulas and regime economics. `current_rates.md` is the current rate authority. `staffing_policy.md` remains the approved staffing/transport authority and is not reopened by Phase 13.3.

This commercial policy body contains no unresolved Phase 13.3 commercial row. Any future change to a locked rule requires a new explicit owner decision rather than inference from historical proposals.
