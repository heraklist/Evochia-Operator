# Artifact Rendering Policy

## Canonical data first

Every artifact is rendered from an approved **canonical structured object** or explicit projection of one. A visual template **must not own business logic** that is absent from the canonical schemas. Pricing, allergens, service scope, calculations and decision state are resolved before rendering.

## Audience boundary

Rendering preserves the information boundary of the source projection:

- `INTERNAL` may contain economics, assumptions, supplier evidence and strategic notes.
- `OPERATIONS` may contain production, staffing, equipment, allergen and service instructions.
- `CLIENT_SAFE` contains only approved client-facing content.

A template must not transform INTERNAL fields into CLIENT-SAFE content by hiding labels or changing wording. Projection happens before rendering.

## Brand preflight

For Evochia artifacts use `company/evochia/brand/assets/render_integrity.yaml`.

`FINAL_VERIFIED` requires the renderer to verify the exact required logo identity and required font identities. The render gate is fail-closed: missing or mismatched brand assets cause failure rather than synthetic logo reconstruction or silent font substitution.

If the preflight is incomplete, the output can only be `DRAFT_UNVERIFIED_BRAND_RENDER` (or an unbranded draft when explicitly requested).

## PDF

A final PDF is the canonical fixed-layout branded deliverable. `FINAL_VERIFIED` PDF requires:

1. verified logo asset;
2. verified required fonts;
3. required fonts **embedded** in the PDF;
4. final page-size/orientation checks;
5. no overflow/clipping and no unintended fallback font;
6. audience/confidentiality checks.

If any requirement fails, final rendering must fail.

## DOCX

DOCX is primarily an **editable source**. It may name the correct fonts, but Word/other consumers can substitute fonts when the local environment lacks them. Therefore do not claim a DOCX is pixel-stable or a canonical fixed-layout representation unless the **verified font environment** used to open/render it is known.

When a DOCX is supplied alongside a PDF, the verified PDF is the visual reference.

## XLSX

XLSX is a structured operational/commercial view, not the authority for recipe/costing business logic. Formulas may implement explicitly approved deterministic calculations, but canonical field meaning remains in schemas/doctrine. Spreadsheet injection protections apply to external/supplier text.

## Golden rendering

Golden examples control artifact-specific structure, tone and layout patterns within their registered authority. They do not control current prices or company policy.
