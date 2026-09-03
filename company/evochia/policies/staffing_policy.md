# Evochia Staffing Policy

**Policy status:** `OWNER_REVIEW_DRAFT`
**Current authority:** prepared owner-review candidate only; no threshold, rate or transport rule below is canonical until explicit owner approval.

## 1. Principle

Staffing is a feasibility, safety and service-quality decision. Guest count is a hard trigger in defined cases, but **service format**, menu complexity, plated synchronization, meal frequency, dietary splits, kitchen/equipment constraints, setup/pack-down, stewarding, travel and venue conditions can require more support than the minimum rule.

The current prepared rate card uses one support-staff category (kitchen assistant / service support) **per person per day**. Future separation into distinct kitchen/service/stewarding roles and rate cards remains open unless explicitly approved later.

## 2. Mandatory and review triggers

**Prepared rule — `CANDIDATE_FROM_OWNER_WORKING_DECISION`:**

- **6+ guests OR plated service:** at least one assistant/support person is mandatory.
- **Plated service:** always requires assistant/support regardless of guest count.
- **Half Board under 6:** `MANDATORY_REVIEW_TRIGGER`, not automatic assistant. Review menu complexity, meal turnaround, dietary splits, kitchen constraints, prep/reset load and cleanup.
- **Full Board under 6:** `MANDATORY_REVIEW_TRIGGER` is a prepared proposal awaiting explicit owner approval; it is not an automatic assistant requirement in this draft.
- Operational constraints may require additional labour even below the normal guest threshold.
- Additional staffing above the minimum remains workload/role based; no universal waiter/stewarding ratio is approved here.

## 3. Prepared support-staff base rates

All values are labour compensation only. Accommodation, tickets and special travel costs are separate.

| Geography / service context | Default base | Prepared range / rule |
| --- | ---: | --- |
| Within Attica | €90/person/day | €90–120; default = minimum |
| Outside Attica — dinner only | €180/person/day | €180 minimum; higher amount quote-specific where justified |
| Outside Attica — Half Board | €180/person/day | €180 minimum; higher amount quote-specific where justified |
| Outside Attica — Full Board | €200/person/day | €200–220; default = minimum |

### Geography vocabulary

Use **within Attica / outside Attica** consistently for this staff rate card. Athens remains an operational-base description, not the geographic boundary of the rate policy.

## 4. Plated-rate calculation

The prepared plated rule is **not** represented as a final flat “+10%” rate because rounding changes the realized uplift.

For integer-euro base rates:

```text
plated_rate = ((base_rate * 11 + 99) // 100) * 10
```

Equivalent rule: calculate `base_rate × 11 / 10`, then round **up** to the smallest multiple of €10 that is greater than or equal to the calculated amount. If the calculated amount is already an exact multiple of €10, it remains unchanged.

Do **not** implement this calculation with binary floating-point arithmetic. For future cent-level support, use decimal/fixed-point arithmetic.

Prepared reference results:

| Base rate | Calculated before rounding | Final plated rate |
| ---: | ---: | ---: |
| €90 | €99 | €100 |
| €120 | €132 | €140 |
| €180 | €198 | €200 |
| €200 | €220 | €220 |
| €220 | €242 | €250 |

Reference sequence: **€100 / €140 / €200 / €220 / €250**.

Because of the round-up rule, the realized uplift across these current reference points is approximately 10%–16.7%. The implementation must follow the formula, not validate the rounded result as an exact 10% uplift.

## 5. Structured staff-line requirement

A staff amount is never sufficient as its own identifier. INTERNAL/OPERATIONS records must carry at least:

- `role_category`;
- `geography`;
- `service_type`;
- `plated`;
- `base_rate`;
- `final_rate`;
- `staff_count`;
- `days`.

When a staff charge is shown as a separate CLIENT-SAFE line, the description must retain enough context to avoid ambiguity (for example geography + service context + plated/non-plated), rather than showing only “assistant €200”.

## 6. Transport architecture

### 6.1 INTERNAL transport evidence

INTERNAL transport cost must use current route, fuel and toll evidence whenever tooling/research is available.

- Route/distance: current route evidence.
- Fuel price: dated `EXTERNAL_EVIDENCE`.
- Tolls/fees: current evidence where material.
- Vehicle parameters: collected through a runtime mini-interview; do not hardcode a permanent vehicle/fuel profile because vehicles and fuel types can change.
- If required live verification is unavailable, do not invent an INTERNAL cost: mark the verification state `NEEDS_REVIEW`.
- Driving time is **not** a separate client transport line, but it is not zero internally; account for time/opportunity cost in INTERNAL economics.

### 6.2 CLIENT transport charge

Client transport is a fixed commercial line **per journey/vehicle, not per person**.

Prepared working reference: **€150 indicative minimum for assignments up to 100 km each way**, explicitly editable by quote and not a universal distance tariff.

Assistants travelling in the same vehicle do not create an additional transport charge. Ferry/air tickets and other person-specific tickets are separate actual/quoted lines.

### 6.3 Verified-cost floor

When INTERNAL transport has been verified, the client fixed transport charge must not be lower than the verified INTERNAL transport cost unless there is an explicit `OWNER_APPROVED_PROMO_SUBSIDY` decision.

This floor is a commercial safety rule; it does not require the client-facing line to expose the internal calculation.

### 6.4 Offline/provisional fallback

When INTERNAL transport verification is unavailable, a proposal may use the prepared indicative minimum where applicable and must mark the transport line **`TRANSPORT_UNVERIFIED`**.

`TRANSPORT_UNVERIFIED` means provisional, not final. The quote must state that transport is subject to verification/repricing. Verification must occur **before final acceptance / booking confirmation**. Once verified, the verified-cost floor applies before the client can finally accept the booking.

Do not convert an underpriced provisional line into `OWNER_APPROVED_PROMO_SUBSIDY` automatically after acceptance. Any subsidy exception must be explicit and prior to final confirmation.

## 7. Multi-day transport models

For multi-day assignments, use one of two mutually exclusive models; do not charge both accommodation and repeated daily commute for the same period unless a materially different arrangement is explicitly documented.

### Stay model

- base/booking transport once for the assignment;
- accommodation as a separate line;
- tickets/third-party travel costs as applicable;
- no routine daily commute charge for the stay period.

### Commute model

- base/booking transport logic;
- additional daily commute costs as defined in the quote;
- no accommodation charge for the same period.

## 8. Uplift boundary

Yacht/island/remote service uplifts belong to commercial service pricing and compensate disruption/availability/complexity. They do **not** replace or duplicate the transport, ticket or accommodation lines defined here.

## 9. Items intentionally still open

- distinct kitchen vs service vs stewarding role rates if/when the unified support category is split;
- universal service/stewarding ratios;
- agency-provided staff treatment where materially different;
- any role-specific overtime/additional-hour policy not already defined in a separate approved service agreement.
