---
name: evochia-company-operations
description: Use when an Evochia task depends on company facts, services, commercial policy, current rates, staffing rules, travel or location rules, terms, promo/agency policy, or other approved operating decisions.
---
# Evochia Company Operations

## Purpose
Apply Evochia-specific company truth and policy as an overlay on generic F&B capability without contaminating the reusable culinary/F&B core.

## When to Use
Use for Evochia enquiries, offers, service scope, staffing, rates, travel/island/yacht/overnight logic, terms, promotions, agencies, company positioning or internal operating decisions.

## Authority and Resources
Use `references/source_registry.yaml` to select current canonical Evochia sources. Company policies/current data outrank generic commercial heuristics. Historical proposals are evidence/examples, not current rate cards.

## Responsibilities
Resolve company facts and applicable policy; distinguish approved policy from draft/needs-owner-approval material; provide current service/commercial constraints to other skills; surface policy conflicts or missing owner decisions.

## Output Contract
Return the relevant approved company context plus explicit `NEEDS_REVIEW` items where policy is not yet canonical. Keep internal company policy separate from client wording.

## Guardrails
Do not manufacture rates/terms from memory, old proposals or market averages. Do not let brand voice override business rules. Do not publish confidential company economics in client-safe outputs.

## Handoffs
Supply company constraints to `costing-commercial-intelligence`, `kitchen-event-operations`, `evochia-brand-documents`, `evochia-product-development` and `evochia-market-intelligence`.

## Non-Goals
Do not own culinary creativity, food safety, visual rendering implementation or persistent CRM/event records.
