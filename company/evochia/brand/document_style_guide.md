# Evochia Document Style Guide

**Status:** `APPROVED`
**Approved by:** Evochia Owner
**Effective date:** 2026-09-03
**Approval reference:** `owner-approval-2026-09-03-phase13.1`

## Typography authority

The typography system is intentionally artifact-specific.

- **Official logo family:** the brand guideline references **Weiss**, but the logo must be placed as approved **vector**/PNG artwork rather than retyped.
- **Current website:** Alexander for brand/headings, Bainsley for body/UI and Miama for accents. This is the current digital/site-native system.
- **Portable proposals, menus, flyers and product plans:** Cormorant Garamond for display/headings and EB Garamond for body/long-form/table text, matching the successful approved print examples and providing a portable renderer contract.
- **Operations / recipebooks:** readability, density, hierarchy and reliable print output outrank decorative styling; use the portable stack or robust serif/sans fallback as the renderer requires.

The Skill repository contains **no font binaries** (`.ttf`, `.otf`, `.woff`, `.woff2`). A renderer may reference fonts already available in its authorized runtime, but the brand package does not redistribute them.

## Palette

Official identity palette: `#024631`, `#FBF8EF`, `#C8B273`, `#DBCEA8`, `#013122`. Digital-only darker/site tokens may be used for web artifacts according to `visual_tokens.yaml`.

## Artifact patterns

### Proposals
Dark-green or controlled branded masthead; clear title/service scope; structured summary; explicit inclusions/exclusions; commercial block; terms; warm closing. Avoid hiding conditions in fine print.

### Client menus
Editorial title and occasion/mood line; clear category/course hierarchy; restrained gold; generous whitespace; dish descriptions that remain culinary rather than promotional. Allergen notes stay legible and factual.

### Product flyers
One-page hierarchy where possible: what it is → experience/flow → inclusions → practical details → CTA. Internal strategy, margin and validation notes never appear.

### Product master plans
Long-form internal document with numbered sections, decision-state tables, evidence/validation status, economics/capacity and removable confidential annexes.

### Production recipebooks
Operations-first: compact, A4-ready, repeated headers, consistent tables, clear quantities/method/holding/CCP blocks, shopping aggregation and production timeline. Brand elements remain secondary to execution clarity.

## Logo and tagline

Use curated official assets under `assets/`. Do not simulate the logo with a typeface. Generated tagline copy is **“Sophisticated taste & tailored events”**; do not reproduce the old misspelling from the original guideline artwork as live text.
