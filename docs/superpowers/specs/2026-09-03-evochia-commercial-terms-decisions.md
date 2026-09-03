# Evochia Commercial Terms — Decision Register

**Date:** 2026-09-03  
**Status:** LOCKED INPUT FOR CANONICAL SPEC  
**Owner:** Evochia Owner  
**Purpose:** One-line-per-decision source of truth for the Phase 13.3 commercial-terms spec. The canonical spec must be derived from this register, not reconstructed from conversation memory.

## Decision discipline

- Each decision has a stable ID.
- A later change must supersede an earlier decision explicitly; it must not silently rewrite history.
- The canonical spec may add structure and definitions, but may not change the substance of a LOCKED decision.
- Runtime policy files remain the operational authority only after implementation; this register is the owner-decision authority for the design/spec phase.

## Locked decisions

| ID | Decision | Date | Status |
| --- | --- | --- | --- |
| D-001 | Canonical impediment regimes are exactly `EXTERNAL_PERFORMANCE_IMPEDIMENT`, `EVOCHIA_INABILITY_TO_PERFORM`, and `CLIENT_SIDE_IMPEDIMENT`; do not introduce synonym regime names. | 2026-09-03 | LOCKED |
| D-002 | `SERVICE_START` means the first scheduled service date **as defined in the quote**; travel, setup, shopping or other operational activity does not redefine it unless the quote itself defines that activity as service start. | 2026-09-03 | LOCKED |
| D-003 | Booking confirmation payment rule: when confirmation occurs more than 5 calendar days before `SERVICE_START`, 30% of the fixed confirmed booking value is due as deposit; when confirmation occurs 5 or fewer calendar days before `SERVICE_START`, 100% is due at confirmation. | 2026-09-03 | LOCKED |
| D-004 | Default balance due date for a booking that used a 30% confirmation deposit is `SERVICE_START - 5 calendar days` (`T-5`). | 2026-09-03 | LOCKED |
| D-005 | Missing the balance deadline creates an operational payment-default state, not an impediment regime. It creates a right to cancel; if Evochia exercises that right, the ordinary cancellation tier is determined by the date the cancellation right is exercised. | 2026-09-03 | LOCKED |
| D-006 | Payment-default cure uses a 48-hour base period plus a banking-clearing floor where needed; the final cure deadline can never extend beyond `SERVICE_START`. | 2026-09-03 | LOCKED |
| D-007 | A cure period extends the client's opportunity to cure only; it never obliges Evochia to increase unrecoverable financial, operational or food-safety exposure while waiting. | 2026-09-03 | LOCKED |
| D-008 | Cancellation tiers are ordered first-match rules based on days before `SERVICE_START`, using the fixed confirmed booking value as the base: 15+ days = 10%; 6–14 days = 30%; 0–5 days = 100%. | 2026-09-03 | LOCKED |
| D-009 | First-match semantics select the applicable cancellation tier; they do **not** prohibit cumulative effects from successive scope reductions. Successive reductions accumulate toward the applicable cap, with the invariant that each unit of fixed scope is charged no more than once. | 2026-09-03 | LOCKED |
| D-010 | Cancellation accounting must distinguish `cancellation_charge`, `collected_cancellation_amount`, `refund_due`, and `uncollected_cancellation_balance`; these values must never be collapsed into a single client debt concept. | 2026-09-03 | LOCKED |
| D-011 | `uncollected_cancellation_balance` is INTERNAL by default and must not appear in CLIENT_SAFE outputs unless the owner separately decides to pursue collection. | 2026-09-03 | LOCKED |
| D-012 | Impediments use a single-classification rule. If causation is hybrid, disputed or insufficiently evidenced such that more than one material regime is plausible, classification is `OWNER_REVIEW_REQUIRED`; the system must never auto-select the economically most favorable regime. | 2026-09-03 | LOCKED |
| D-013 | `PARTIAL_PERFORMANCE` is not a fourth impediment regime. It is a calculation modifier applied only after the event has been classified into the controlling regime. | 2026-09-03 | LOCKED |
| D-014 | `PARTIAL_PERFORMANCE` uses one calculation with three allocation rules: unitized performed service, direct attributable costs, and shared/indivisible fixed lines; ambiguous shared-line allocation requires `OWNER_REVIEW_REQUIRED`. | 2026-09-03 | LOCKED |
| D-015 | Client postponement is permitted once per booking. The replacement service date must fall within 6 calendar months of the **original** `SERVICE_START`. | 2026-09-03 | LOCKED |
| D-016 | The owner may grant a discretionary written postponement extension only by stating an explicit new expiry date; an extension does not reset the original postponement history. | 2026-09-03 | LOCKED |
| D-017 | Client-postponement anti-reset rule: if the postponed booking is later cancelled, use `max(cancellation tier at postponement request, cancellation tier at final cancellation)`. | 2026-09-03 | LOCKED |
| D-018 | A postponed booking is repriced under the current applicable terms/rates for the new date and scope; postponement preserves eligible credit, not historical pricing. | 2026-09-03 | LOCKED |
| D-019 | If client postponement credit expires unused, treat the booking as cancelled using the cancellation tier that applied on the date the postponement was requested. | 2026-09-03 | LOCKED |
| D-020 | After final settlement of a postponed/cancelled booking, any collected credit exceeding the applicable retained/charge amount is refundable; excess credit is not forfeited by default. | 2026-09-03 | LOCKED |
| D-021 | An Evochia-caused reschedule or an `EXTERNAL_PERFORMANCE_IMPEDIMENT` reschedule does not consume the client's one postponement, does not start or consume the client 6-month postponement window, and does not trigger the client-postponement anti-reset rule. | 2026-09-03 | LOCKED |
| D-022 | Scope reduction uses `removed_fixed_value = fixed value before change - revised fixed value`; the applicable cancellation tier is applied only to `removed_fixed_value`, not to the retained scope. | 2026-09-03 | LOCKED |
| D-023 | Scope reduction must use the same pricing methodology as the confirmed quote. Non-scaling fixed elements remain unchanged unless explicitly revised, and staffing triggers are recalculated rather than proportionally scaled. | 2026-09-03 | LOCKED |
| D-024 | Scope reduction requires written approval/revision. Lower actual attendance on the service day does not by itself reduce the fixed confirmed booking value. | 2026-09-03 | LOCKED |
| D-025 | Default quote validity is 7 calendar days. Every quote must carry an explicit `valid_until` date calculated as `min(issue_date + 7 calendar days, SERVICE_START - 6 calendar days)`. | 2026-09-03 | LOCKED |
| D-026 | A quote-specific validity override may shorten validity freely; extending validity requires an explicit later date rather than an implied/open-ended extension. | 2026-09-03 | LOCKED |
| D-027 | `TRANSPORT_UNVERIFIED` is an independent booking-confirmation gate: material transport must be verified/resolved before booking confirmation regardless of whether the quote is still within its validity period. | 2026-09-03 | LOCKED |
| D-028 | Peak-date policy is `APPROVED_OWNER_DECISION`: there is **no global peak-date surcharge**. Any peak-date pricing adjustment is quote-specific only. | 2026-09-03 | LOCKED |
| D-029 | Household-chef policy is `APPROVED_OWNER_DECISION`: there is **no global household-chef rate card**. Household-chef pricing is quote-specific only; historical proposals remain proposal-specific evidence. | 2026-09-03 | LOCKED |
| D-030 | Legal identity uses a `RUNTIME_RESOLVED` model. Binding documents fail closed unless the legally correct runtime identity is resolved. Client-facing documents must not describe Evochia as a company/group unless that legal characterization is actually resolved and authorized. | 2026-09-03 | LOCKED |
| D-031 | INTERNAL and CLIENT_SAFE projections are separate contracts. INTERNAL may include full economics, classification evidence, allocation detail and uncollected balances; CLIENT_SAFE includes only authorized client terms/amounts and must not leak internal-only fields. | 2026-09-03 | LOCKED |
| D-032 | After implementation, stale `OPEN` / `NEEDS_OWNER_APPROVAL` markers must be removed everywhere for decisions closed by this register, including `terms_policy.md`, `commercial_policy.md`, `current_rates.md`, and `company_profile.md`; unrelated unresolved items remain open. | 2026-09-03 | LOCKED |
| D-033 | Canonical definitions must define each commercial term once. Downstream policy sections/files reference those definitions instead of creating parallel vocabulary or duplicate formulas. | 2026-09-03 | LOCKED |
| D-034 | The design/spec and implementation tests must include at minimum: cancellation-tier boundaries, payment-default exercise-date tiering, banking-clearing cure cap, no-new-exposure during cure, anti-reset, excess-credit refund, removed-value tiering, cumulative scope-reduction single-charge invariant, single impediment classification, hybrid cause owner review, partial-performance allocations, transport confirmation gate, legal-identity fail-closed behavior, CLIENT_SAFE export boundary, and stale-OPEN cross-file synchronization. | 2026-09-03 | LOCKED |
