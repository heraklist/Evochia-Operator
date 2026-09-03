# Evochia Company Profile

**Policy status:** `OWNER_REVIEW_DRAFT`
**Purpose:** consolidate current company context and explicit approval boundaries before any promotion to canonical current data.

## Rule-state vocabulary

- `APPROVED_EXISTING_CONTEXT` — already established in current company knowledge/site context.
- `CANDIDATE_FROM_OWNER_WORKING_DECISION` — working business decision prepared for explicit owner review.
- `PROPOSAL_SPECIFIC_EVIDENCE` — true for a specific proposal/booking, not automatically general policy.
- `NEEDS_OWNER_APPROVAL` — unresolved before canonical use.

## Identity and positioning

| Field | Working value | State |
| --- | --- | --- |
| Brand | Evochia | `APPROVED_EXISTING_CONTEXT` |
| Business model | Chef-led hospitality: Private Chef + Catering / event food service | `APPROVED_EXISTING_CONTEXT` |
| Positioning | Premium, personal, editorial, chef-led hospitality | `APPROVED_EXISTING_CONTEXT` |
| Geography | Greece-wide service capability, with Athens/Attica as operational base/context | `APPROVED_EXISTING_CONTEXT` |
| Brand architecture | Branded-house approach under Evochia | `APPROVED_EXISTING_CONTEXT` |
| Working umbrella descriptor | Evochia Food & Hospitality Group | `NEEDS_OWNER_APPROVAL` for legal/commercial use |

The detailed client-facing positioning language is governed by `company/evochia/brand/brand_voice.md`. The internal “restaurant-at-home” constraint belongs to Brand Voice governance and is not a default client-facing phrase.

## Current service families

- Event Catering — including wedding/corporate contexts where appropriate.
- Private Chef — home, villa, yacht/island and Athens/Greece contexts.
- Bespoke menus and chef-led dining experiences.
- Product/experience formats developed through the Evochia product-development process.

Pop-up/festival directions are opportunity areas unless separately approved as live commercial products.

## Operating principles

1. Sell professional hospitality/service rather than hiding labour and commercial value inside ingredient margin.
2. Preserve the distinction between INTERNAL economics and CLIENT quotation/presentation.
3. Keep service scope, food/supplier costs, staffing, travel, accommodation, rentals/equipment and VAT transparent at the appropriate audience level.
4. Use current approved company policy over generic F&B pricing heuristics when `company=evochia`.
5. Food safety and allergen authority always outrank brand or commercial preferences.

## File-level approval does not approve unresolved rows

A future file status of `PARTIALLY_APPROVED` does **not** silently promote every field in this document. Any field that remains `NEEDS_OWNER_APPROVAL` retains that state until its own explicit owner decision is recorded.

In particular, legal entity naming and the working umbrella descriptor **Evochia Food & Hospitality Group** remain unresolved unless separately approved. No file-level status transition may be interpreted as legal-name approval.

## Approval gap

Final legal/entity naming, unresolved service-taxonomy questions, peak-date policy and any other row explicitly marked `NEEDS_OWNER_APPROVAL` remain open until separate owner approval. Rates, staffing and commercial terms are governed by their dedicated policy files and their own state metadata.
