# Evochia Company Profile

**Policy status:** `PARTIALLY_APPROVED`
**Approved by:** `Evochia Owner`
**Effective date:** `2026-09-03`
**Approval reference:** `owner-approval-2026-09-03-phase13.3`
**Purpose:** canonical current company context with explicit row-level approval boundaries.

## Rule-state vocabulary

- `APPROVED_EXISTING_CONTEXT` — established and approved current company context.
- `APPROVED_OWNER_DECISION` — explicitly approved by the owner in the current policy lock.
- `PROPOSAL_SPECIFIC_EVIDENCE` — true for a specific proposal/booking, not automatically general policy.
- `NEEDS_OWNER_APPROVAL` — unresolved before canonical use.

## Identity and positioning

| Field | Current value | State |
| --- | --- | --- |
| Legal form / provider entity type | Individual / sole proprietorship (`ατομική επιχείρηση`) | `APPROVED_OWNER_DECISION` |
| Brand | Evochia | `APPROVED_EXISTING_CONTEXT` |
| Trade name / διακριτικός τίτλος | Evochia Food & Hospitality Group | `APPROVED_OWNER_DECISION` |
| Business model | Chef-led hospitality: Private Chef + Catering / event food service | `APPROVED_EXISTING_CONTEXT` |
| Positioning | Premium, personal, editorial, chef-led hospitality | `APPROVED_EXISTING_CONTEXT` |
| Geography | Greece-wide service capability, with Athens/Attica as operational base/context | `APPROVED_EXISTING_CONTEXT` |
| Brand architecture | Branded-house approach under Evochia | `APPROVED_EXISTING_CONTEXT` |

The legal/entity facts are closed. `Evochia Food & Hospitality Group` is an approved trade name / **διακριτικός τίτλος** of the sole proprietorship. It is **not** a statement that a separate company, corporation, corporate group or group of companies exists.

Client-facing text **must not** characterize Evochia as a company, corporation, corporate group or group of companies. The trade name never unlocks those descriptions by inference.

The detailed client-facing positioning language is governed by the approved `company/evochia/brand/brand_voice.md`. The internal “restaurant-at-home” constraint belongs to Brand Voice governance and is not a default client-facing phrase.

## `RUNTIME_RESOLVED` legal particulars

`RUNTIME_RESOLVED` applies to the current legal particulars required for a specific binding document; it does **not** mean entity type is unresolved.

Examples of runtime particulars can include the legally required current provider identifiers/details for the artifact and jurisdiction.

Binding-document rule:

```text
required binding legal particulars unavailable
-> FAIL CLOSED
-> do not generate/authorize the binding artifact as complete
```

The fail-closed gate cannot be bypassed by substituting the brand or trade name for missing required legal particulars.

## Current service families

- Event Catering — including wedding/corporate contexts where appropriate.
- Private Chef — home, villa, yacht/island and Athens/Greece contexts.
- Bespoke menus and chef-led dining experiences.
- Product/experience formats developed through the Evochia product-development process.

Pop-up/festival directions remain opportunity areas unless separately approved as live commercial products.

## Operating principles

1. Sell professional hospitality/service rather than hiding labour and commercial value inside ingredient margin.
2. Preserve the distinction between INTERNAL economics and CLIENT quotation/presentation.
3. Keep service scope, food/supplier costs, staffing, travel, accommodation, rentals/equipment and VAT transparent at the appropriate audience level.
4. Use current approved company policy over generic F&B pricing heuristics when `company=evochia`.
5. Food safety and allergen authority always outrank brand or commercial preferences.
6. Preserve the legal distinction between sole proprietorship, brand and trade name in every binding/client-facing projection.

## File-level partial approval does not approve unresolved rows

`PARTIALLY_APPROVED` does **not** silently promote every row in this document. A row explicitly marked `NEEDS_OWNER_APPROVAL` remains unresolved until its own explicit owner decision is recorded.

The Phase 13.3 legal identity row is **not** unresolved: legal form, brand and trade name are approved as stated above.

## Remaining approval gap

`NEEDS_OWNER_APPROVAL` remains only for genuinely unrelated **service-taxonomy** questions or future profile fields that have not received an explicit owner decision.

Those service-taxonomy questions do not reopen legal form, brand/trade-name identity, rates, staffing or commercial terms. Dedicated policy files govern those domains under their own row-level states.
