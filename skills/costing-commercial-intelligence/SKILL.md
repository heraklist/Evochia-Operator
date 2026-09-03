---
name: costing-commercial-intelligence
description: Use when the task requires AP/EP or recipe costing, yields, VAT, pricing, margin, markup, event economics, profitability, what-if analysis, quote drift, break-even, commercial viability, or Excel/Google Sheets costing workbook design/export.
---
# Costing Commercial Intelligence

## Purpose
Provide deterministic F&B costing and commercial analysis while preserving the approved baseline and applying Evochia policy only when that company context is active.

## When to Use
Use for recipe/event costing, pricing, margin/markup, VAT, labour/overhead, scenario comparison, quote drift, break-even, viability decisions, or Excel/Google Sheets costing workbook and formula-export structure.

## Authority and Resources
Read `references/costing/costing_formula_engine_v2_2.md` and `references/costing/what_if_profitability_v2_2.md`. When the requested output is Excel, Google Sheets, a workbook, formula export, costing card or dashboard, also read `references/exports/excel_sheets_export_spec_v2_4.md`. Use approved current company policy above generic pricing heuristics in Evochia context.

## Responsibilities
Normalize cost basis; calculate AP/EP and yields; include relevant food, packaging, labour, staff, transport, accommodation, equipment and overhead; separate cash cost from economic cost; calculate net/gross price, FC%, GM%, markup, contribution and break-even; preserve scenario isolation. For spreadsheet outputs, separate input/calculation/output layers and preserve the canonical workbook/formula patterns rather than inventing an unrelated sheet structure.

## Output Contract
Show definitions/formulas where material, assumptions/missing data, reliability status, result and commercial verdict. For spreadsheet requests, produce an Excel/Google Sheets export plan or workbook-ready structure consistent with the export doctrine. INTERNAL output may contain margin/opportunity-cost detail; CLIENT-SAFE output must not.

## Guardrails
Recoverable input VAT is excluded from internal net cost. VAT rates are configurable/current-data questions, not universal constants. Never invent supplier prices/yields. What-if scenarios never overwrite approved baselines. Generic food-cost targets do not override approved Evochia service-fee policy. Do not imply Google Sheets access or persistence merely because a workbook structure is produced.

## Handoffs
Use `supplier-procurement-intelligence` for current supplier evidence, `kitchen-event-operations` for event resources, and `evochia-company-operations` for current company commercial policy.

## Non-Goals
Do not approve master prices, issue invoices, persist records or infer current Evochia rates from historical proposals.
