# Evochia Brand Assets

**Status:** `RENDER_INTEGRITY_CONTRACT`

The Skill repository must be able to produce a branded result that is **correct or explicitly fails**. Silent logo reconstruction, unverified replacements and silent font substitution are forbidden.

## Materialized asset in this repository

- `logo-mark-42.png` — byte-identical production Evochia mark copied from `heraklist/evochia_site` commit `8168999e22ef5ca000dfe5c4be53e6e084c9db6f`, source path `assets/logo-42.png`, Git blob SHA `11676370669ef00c1ed6815300db240c5ce376f8`.

This file is sufficient for small UI/preview use. It is **not** the print-resolution source.

## Pinned production sources for higher-resolution rendering

The renderer may materialize these exact assets into a temporary render cache only after verifying their Git blob identity:

- `assets/logo-84.png` → `25e4e8643a9fbec55213901181bde4ffcb5b2b3c`
- `assets/logo-280.png` → `59f8a5e406b77abc45fe5938b154f5e73f9e86af`

If the exact required asset cannot be retrieved and verified, the renderer must fail the final-brand gate rather than substitute another logo.

## Owner-supplied identity pack

Authoritative source evidence: `EVOCHIA-LOGO-GUIDLINES.zip`.

Recorded canonical paths:

- `EVOCHIA-LOGO/EVOCHIA/SVG/ORIGINAL TRANSPARENT.svg`
- `EVOCHIA-LOGO/EVOCHIA/SVG/ORIGINAL.svg`
- `EVOCHIA-LOGO/EVOCHIA/SVG/GREYSCALE TRANSPARENT.svg`
- `EVOCHIA-LOGO/EVOCHIA/PNG LOGO FILE 1850x1063/ORIGINAL-TRANSPARENT.png`

The supplied full lockup contains the source-artwork spelling **“Sofisticated taste & tailored events”**. Preserve the source asset unchanged as evidence, but do not use that lockup as the default for newly generated artifacts. Generated brand copy uses **“Sophisticated taste & tailored events”**.

A corrected full lockup may become the default only after explicit owner approval plus visual/checksum verification.

## Font rule

Font binaries are not duplicated into this Skill repository. `render_integrity.yaml` pins exact authorized font sources and identities. Renderers use temporary materialization and a fail-closed preflight. A missing or mismatched font is a render failure, not permission to fall back silently.
