---
name: evochia-market-intelligence
description: Use when Evochia needs competitor, partnership, SEO, market, growth, positioning, or current external intelligence rather than culinary or event-production work.
---
# Evochia Market Intelligence

## Purpose
Provide optional company intelligence without loading the culinary stack when the job is competitor, SEO, growth or market analysis.

## When to Use
Use for competitor research, CI dataset questions, positioning comparisons, partner discovery, SEO/current market signals, growth opportunities or market validation.

## Authority and Resources
Use `references/source_registry.yaml` to resolve source authority and the current CI dataset. The current machine-readable registry selects `evochia_ci_v33`; v20/v10 are superseded historical evidence. Use `skills/evochia-market-intelligence/references/intelligence_policy.yaml` for CI/SEO methodology, evidence, freshness, entity governance and version-pointer resolution. Structure market briefs with `schemas/market_intelligence_brief.schema.json`.

The canonical CI research protocol controls research method. Any time-bound sentence inside that protocol naming a then-current workbook does not override the Source Registry's current-data selection.

## Responsibilities
Retrieve relevant current internal CI; preserve company-level deduplication and relationship classes; distinguish Research Priority, Competitive Threat and Partner / Opportunity; identify freshness gaps; research external evidence for mutable current claims; distinguish facts, external evidence, estimates, assumptions and inference; compare positioning; and surface actionable implications for Evochia.

For a newly discovered competitor or partner candidate, create a dated archive finding first. Promotion to canonical requires evidence validation, deduplication and archive-before-change.

## SEO Rules
The CI workbook is a competitor benchmark, not the primary source for Evochia's own analytics. GA4 and Google Search Console remain the primary own-data layer when connected/available. Do not invent monthly search volume, CPC, keyword difficulty, follower growth, hashtag reach or rankings. Missing unsupported numeric metrics are `Not estimated`. Search Console integration remains deferred until explicitly activated by a later approved integration decision.

## Freshness
Treat v33 as a company intelligence snapshot, not proof that the external market is unchanged. Claims such as current prices, active services, rankings, ratings/review counts, social metrics, page status and partnership/service claims require fresh public evidence when current truth matters. Fresh research does not silently mutate the canonical workbook.

## Output Contract
Return evidence-led intelligence with claim/evidence class, source reference, research date, freshness state, confidence, comparison/prioritization, uncertainties, residual risk and recommended next action. Use `INTERNAL`, `OPERATIONS` or `CLIENT-SAFE` audience boundaries as applicable. INTERNAL strategic conclusions stay internal unless explicitly prepared for external use.

## Guardrails
Do not treat CI snapshots as proof that the external market is unchanged. Do not use competitor pricing as Evochia policy. Do not inflate direct competitor counts with aliases, venues, sub-brands or weak directory-only signals. Missing enrichment is not automatically a competitive weakness. Do not claim 100% national market coverage. Do not route ordinary recipe/menu/event-production work here merely because competitors are mentioned incidentally.

Collect business-facing public information only. Do not collect follower lists, unrelated personal data or perform unauthorized bulk social scraping.

## Handoffs
Use `evochia-product-development` for product decisions, `evochia-company-operations` for policy constraints and `evochia-brand-documents` for approved outward-facing positioning.

## Non-Goals
Do not create recipes, event production plans, supplier cost masters or final company rates.
