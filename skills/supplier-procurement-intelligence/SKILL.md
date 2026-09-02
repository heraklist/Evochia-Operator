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
Read `references/yields/supplier_yield_workflow_v3_2_2.md` and `data/yields/fnb_basic_ingredient_yields_v1.csv`. The Mart provider is tool implementation, not business truth.

## Responsibilities
Preserve raw evidence separately; normalize pack/unit/VAT/date; classify exact/comparable/similar/not-comparable; track price/match confidence; choose yield hierarchy; compute AP/EP comparable cost; surface stale/unknown data and pack rounding needs.

## Output Contract
Return normalized comparison/procurement evidence with supplier, raw item, pack, net/AP cost, EP cost where relevant, source/date/confidence and needs-review status.

## Guardrails
Never invent missing price, pack size, tax status or supplier identity. Never auto-approve extracted supplier data. Authenticated browser profiles, cookies and credentials remain local-only. A live The Mart refresh requires explicit user request and available local/tool execution; otherwise use the latest validated snapshot and label freshness.

## Handoffs
Send approved/current costs to `costing-commercial-intelligence`; recipe quantities to `recipe-engineering`; event purchasing context to `kitchen-event-operations`.

## Non-Goals
Do not define Evochia service pricing, brand voice, client proposal terms or persistent inventory state.
