---
name: recipe-engineering
description: Use when a dish idea or existing recipe must become a reliable professional recipe, scalable production specification, troubleshooting plan, or structured recipe output.
---
# Recipe Engineering

## Purpose
Turn culinary intent into an executable professional recipe while preserving creativity, metric precision, scaling safeguards, service quality and costing hooks.

## When to Use
Use for recipe creation, professional recipe specifications, scaling, reformulation, production instructions, yield/portion structure, holding/regeneration, failure recovery or troubleshooting.

## Authority and Resources
Read `references/operations/professional_kitchen_workflows_v2_2.md`, `references/culinary/flavor_pairing_substitution_v2_1.md`, and the safety/costing references when relevant.

## Responsibilities
Specify yield, portions, equipment, ingredients, AP/EP basis where material, mise en place, detailed method, time/temperature/sensory cues, finishing, holding, regeneration, service/plating, make-ahead sequence, critical quality points, failure recovery, allergens and scaling notes. Keep nonlinear ingredients/processes under review when batch size changes.

## Output Contract
Produce either a concise recipe or professional production spec according to user need. Metric units are default. Separate assumptions from known values. When data is intended for artifacts, structure it so one canonical recipe can drive A4 recipebook, XLSX, shopping and prep outputs later.

## Guardrails
Do not blindly multiply salt, acid, spice, yeast, gelatin, thickeners or leavening. Do not invent supplier prices or measured yields. Do not claim allergen-free status. Do not replace sensory/quality cues with timer-only instructions when professional execution needs both.

## Handoffs
Use `food-safety-allergens` for safety-critical validation, `costing-commercial-intelligence` for costing, `supplier-procurement-intelligence` for purchasing evidence and `kitchen-event-operations` for multi-recipe production/service coordination.

## Non-Goals
Do not own company pricing policy, branded proposal language, competitive intelligence or persistent recipe storage.
