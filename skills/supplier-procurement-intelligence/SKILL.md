---
name: supplier-procurement-intelligence
description: Use when supplier prices, pack normalization, product comparability, yield-sensitive purchasing, The Mart refreshes, price freshness, procurement planning, or supplier evidence are needed.
---
# Supplier Procurement Intelligence

## Purpose
Convert supplier evidence into comparable, reviewable procurement intelligence without inventing prices or silently promoting extracted data to approved master records.

## When to Use
Use for supplier files, The Mart capture/snapshot, price comparisons, pack/unit/VAT normalization, ingredient matching, yield-adjusted EP cost or purchase-plan evidence.

## Authority and Resources
Read `references/yields/supplier_yield_workflow_v3_2_2.md` and `data/yields/fnb_basic_ingredient_yields_v1.csv`. Normalize provider output against `schemas/supplier_price_snapshot.schema.json`. For The Mart, enforce `scripts/supplier-providers/themart/provider_contract.yaml` and use only `scripts/supplier-providers/themart/provider_adapter.py capture`; never invoke the exact historical scripts or `run_windows.bat` directly. Accept spreadsheet output only after the adapter's fail-closed recovery and formula scan; read the provider runbook before local execution. Verify migrated bytes with `scripts/verify_themart_source_provenance.py`. The Mart provider is tool implementation, not business truth.

## Responsibilities
Preserve raw evidence separately; normalize pack/unit/VAT/date; classify exact/comparable/similar/not-comparable; track price/match confidence and freshness; choose yield hierarchy; compute AP/EP comparable cost; surface stale/unknown data and pack rounding needs.

## Output Contract
Return normalized comparison/procurement evidence with supplier, raw item, pack, net/AP cost, EP cost where relevant, source/date/confidence, freshness and needs-review status. Extracted supplier rows are evidence, not automatically approved master data.

## Guardrails
Never invent missing price, pack size, tax status or supplier identity. Never auto-approve extracted supplier data. Authenticated browser profiles, cookies, credentials and raw output remain local-only and outside the repository. The Mart authenticated profile is supplied only through `THEMART_BROWSER_PROFILE_DIR`; optional output configuration uses `THEMART_OUTPUT_DIR`. A live The Mart refresh requires an **explicit user request** and available local/tool execution; background monitoring is disabled. Otherwise use the latest validated snapshot when available and label freshness.

## Handoffs
Send approved/current costs to `costing-commercial-intelligence`; recipe quantities to `recipe-engineering`; event purchasing context to `kitchen-event-operations`.

## Non-Goals
Do not define Evochia service pricing, brand voice, client proposal terms or persistent inventory state. Do not reconstruct or approximate The Mart collector/extractor code when exact audited source bytes are unavailable.
