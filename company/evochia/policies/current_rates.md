# Evochia Current Rates

**Policy status:** `PARTIALLY_APPROVED`
**Approved by:** `Evochia Owner`
**Effective date:** `2026-09-03`
**Approval reference:** `owner-approval-2026-09-03-phase13.2`
**Important:** approved values below are current authority within their stated scope. Historical or proposal-specific evidence must not become current rate authority without explicit owner approval. The header remains on Phase 13.2 metadata until the Phase 13.3 row-audit/state-reconciliation task.

## A. Private Chef — INTERNAL BASE RATE CARD

**State:** `APPROVED_OWNER_DECISION`.

These values operate as an **INTERNAL BASE RATE CARD**: authoritative starting points for commercial reasoning, not a public immutable tariff. Final quotation may change with staffing, menu/service complexity, location, logistics, equipment and scope.

| Service | Party size | Base service fee |
| --- | ---: | ---: |
| Breakfast Only | up to 4 | €140 |
| Breakfast Only | 5–8 | €180 |
| Breakfast Only | 9–12 | €230 |
| Half Board (2 meals/day) | up to 4 | €250/day |
| Half Board (2 meals/day) | 5–8 | €330/day |
| Half Board (2 meals/day) | 9–12 | €440/day |
| Full Board (3 meals/day) | up to 4 | €380/day |
| Full Board (3 meals/day) | 5–8 | €520/day |
| Full Board (3 meals/day) | 9–12 | €660/day |
| One-Off Private Dinner | 2 | €200–260 |
| One-Off Private Dinner | 3–6 | €280–380 |
| One-Off Private Dinner | 7–12 | €380–540 |

The service fee covers the defined chef/service work. Food/supplier cost treatment follows the quotation format and `commercial_policy.md`; it is not silently folded into these base fees.

## B. Service uplift / location rules

**State:** `APPROVED_OWNER_DECISION`.

- Yachting service uplift: `+20%`.
- Island / overnight / materially remote service uplift: `+40%`.
- The `+40%` compensates disruption, lost productive time/availability and operational complexity — **not** transport, tickets, tolls, accommodation or other actual travel costs.
- If yacht and island/remote conditions overlap, apply the **single highest applicable disruption uplift**, not both cumulatively.
- Remote Attica: base service fee + actual/quoted logistics; do not apply the island uplift automatically.

These values are unchanged by Phase 13.3. A quote-specific peak-date adjustment is governed separately by Section F and `commercial_policy.md`; it does not alter these uplift percentages.

## C. Children pricing rule

**State:** `APPROVED_OWNER_DECISION`.

`50%` treatment for **children under 12** applies only when the CLIENT pricing model is all-in or per-person menu pricing and the child portion/menu justifies the reduced price.

It does **not** apply:

- to the chef/service fee;
- as an additional discount to actual-cost/pass-through groceries or supplier purchases;
- automatically where the quoted child menu/portion is not materially reduced.

## D. Meal Prep — production-day model

**State:** `APPROVED_OWNER_DECISION`.

| Scope | Service fee |
| --- | ---: |
| Up to 2 persons | €60 / production day |
| Up to 4 persons | €85 / production day |
| Each additional person | +€20 / production day |
| Different meals / additional meal split | +€20 / production day |
| Delivery | €10 / week, independent of number of production days |

Legacy weekly arithmetic may still be derived from this model (for example 2 production days × €60 = €120 for up to 2 persons), but it is not a separate competing rate card.

**Legacy €70 additional production day rule: `RETIRED`.** It remains historical evidence only and is no longer an active rate rule.

## E. Staffing rates

Support-staff compensation, geography, plated calculation and transport rules are defined in `staffing_policy.md`. These are intentionally not inferred from the Private Chef service-fee table.

Phase 13.3 does not reopen or alter the staffing policy.

## F. Peak-date policy

**State:** `APPROVED_OWNER_DECISION`.

There is **no global peak-date surcharge** and no global peak multiplier in this rate file.

Any peak-date adjustment is quote-specific and must follow the exact evidence schema in `commercial_policy.md`:

```text
reason
amount_or_method
date_specific_basis
costs_already_covered_elsewhere
double_count_check
owner_decision/reference
```

A peak adjustment can coexist with yacht/island/remote uplift only when the documented causes are distinct. `date_specific_basis` must establish a positive date-specific scarcity/demand/availability basis; geography alone is not sufficient. `double_count_check` must prevent charging the same causal burden twice.

## G. Household-chef pricing policy and historical evidence

**State:** `APPROVED_OWNER_DECISION` for the policy boundary; historical figures remain `PROPOSAL_SPECIFIC_EVIDENCE`.

There is **no global household-chef rate card**. Household pricing is quote-specific and uses the dedicated recurring framework in `commercial_policy.md`.

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
rate_review_and_escalation
absence_or_non_use
```

Household service is a **recurring** engagement. The one-off event T-5 balance and 10/30/100 cancellation tiers **do not apply by default**.

`rate_review_and_escalation` must state both review timing/trigger and the mechanism or rule for any rate adjustment.

Historical evidence is not current tariff authority. For example, a May 2026 household-chef proposal used €6,500/month for five service days/week, €350 additional day, €40 additional hour, guest-event supplements and travel-day fees. Those values remain evidence for that specific proposal only.

## H. Historical event evidence

Event-specific fees from villa/catering proposals, including Porto Germeno examples, remain historical/client-specific evidence. They may support estimating and proposal structure but are not current global rates.

## I. Items intentionally still OPEN

The following remain genuinely unresolved and are not Phase 13.3 commercial residue:

- any service family/rate not explicitly defined above;
- any future public-facing price-list policy.

Peak-date policy and household-chef global-rate-card policy are no longer unresolved: the approved decisions are respectively **no global peak-date surcharge** and **no global household-chef rate card**.
