# Evochia Visual Identity

**Status:** `OWNER_REVIEW_DRAFT`
**Authority model:** official logo guideline → logo/palette; current site → digital typography/current web tokens; approved documents → portable print/document system.

## Official identity palette

- Primary green `#024631`
- Warm off-white `#FBF8EF`
- Gold `#C8B273`
- Secondary beige `#DBCEA8`
- Deep green `#013122`

The current website also uses a darker digital family (`#0A1F15`, `#0F2E1F`, `#143A28`) and a site gold family around `#C4A265`. These are digital implementation tokens, not replacements for the official logo palette.

## Logo

Use actual approved/verified Evochia artwork. Do not reconstruct the logo or wordmark from a font. The guideline names **Weiss Font** as the logo-family reference; this does not make Weiss the default document body font.

The active rendering contract is `company/evochia/brand/assets/render_integrity.yaml`. A final branded artifact is valid only when the required logo asset resolves to the pinned identity. Missing/mismatched assets cause a render failure rather than silent substitution.

The owner-supplied full lockup is retained as source evidence but is not the default for new artifacts because its embedded tagline artwork contains the spelling `Sofisticated taste & tailored events`. Generated brand copy uses the canonical wording **“Sophisticated taste & tailored events”** until a corrected full lockup is explicitly approved.

## Typography decision

### Digital / site-native identity

Current evochia.gr implementation is the authority for the active website typography:
- **Alexander** — brand and major headings
- **Bainsley** — body/UI
- **Miama** — controlled accent/signature use
- Georgia/serif fallback is used in specific page-hero situations

### Portable generated documents

For proposals, menus, flyers and long-form printable client documents, use the proven portable editorial stack from approved documents:
- **Cormorant Garamond** — display/headings
- **EB Garamond** — body, tables and long-form text

This is intentionally artifact-specific. Font source identities are pinned in `render_integrity.yaml`; font binaries are materialized temporarily by the renderer rather than duplicated in the Skill repository.

## Final-render rule

- Missing required font → fail final branded render.
- Font identity mismatch → fail final branded render.
- Silent font substitution → forbidden.
- Final PDF → required fonts must be embedded and verified.
- DOCX → editable source; do not claim pixel-stable/canonical appearance unless the consuming font environment is verified.
- Any output produced without verified brand assets/fonts must be labelled `DRAFT_UNVERIFIED_BRAND_RENDER`.

## Visual character

Quiet, warm, editorial, structured, with generous whitespace, deep green anchors, restrained gold rules/highlights, warm neutral paper/backgrounds and clear information hierarchy. Operations documents prioritize density/readability over decorative luxury.
