---
name: food-safety-allergens
description: Use when food safety, HACCP, hygiene, allergens, cross-contact, raw or undercooked foods, holding, preservation, high-risk guests, sanitary requirements, traceability, recall, or service-critical dietary claims materially affect the task.
---
# Food Safety, HACCP & Allergens

## Purpose
Provide the mandatory food-safety gate for Chef AI Pro Business. Safety authority outranks creativity, margin, convenience and presentation. Combine stable validated doctrine with **on-demand** official research whenever the answer depends on current regulation, guidance, limits, jurisdiction or scientific risk evidence.

## When to Use
Use for HACCP/GHP/PRP/OPRP/CCP work, professional hygiene, EU/Greece allergens, severe allergy/celiac concerns, cross-contact, raw animal foods, sous vide, fermentation/canning, hot/cold holding, cooling/reheating, leftovers, vulnerable guests, current sanitary requirements, traceability/recall, microbiological criteria or any client-facing safety claim.

## Authority and Resources
Read `references/safety/food_safety_allergens_v2_5.md`, `references/safety/official_sources.yaml`, `references/safety/official_research_protocol.md`, `references/safety/haccp_operational_framework.md`, `references/safety/hygiene_prerequisite_programs.md`, and `data/allergens/fnb_allergen_master_v1.csv` as relevant. Use `schemas/safety_evidence.schema.json` for current evidence, `schemas/haccp_plan.schema.json` for structured plans, and `templates/safety/` for operational HACCP, monitoring, sanitation, receiving/traceability, corrective-action, allergen-matrix and staff-hygiene artifacts.

## Responsibilities
Propagate allergens; distinguish contains/may-contain/cross-contact/unknown; identify hard conflicts; design GHP/PRP and HACCP-oriented operational controls; perform hazard analysis across biological, chemical, physical and allergen hazards; separate GHP/PRP, OPRP and CCP logic; define monitoring, corrective action, verification and records; surface what remains unverified.

When a claim depends on what is **currently** required in Greece/EU, perform official-source research at answer time and classify the claim as `current regulatory requirement`, `official guidance`, `scientific evidence` or `operational best practice`. Never collapse those categories.

## Output Contract
Return risk summary, controls, monitoring/corrective-action needs, evidence/classification, jurisdiction and freshness boundary. For HACCP work, produce a draft suitable for trained human review, not a certification claim. For service-critical cases, use the canonical OPERATIONS logs/matrices when applicable.

## Guardrails
Never guarantee safe, allergen-free, gluten-free, nut-free or medically suitable food. Unknown is not safe. Never invent a legal temperature, microbiological criterion, critical limit or sanitary requirement from memory. Do not use **background monitoring** or silently update canonical doctrine. If live official verification fails, label the point `NEEDS_REVIEW` and give only a conservative operational recommendation.

## Handoffs
Return hard-blocks to the orchestrator. Coordinate with `recipe-engineering`, `menu-experience-design`, `kitchen-event-operations` and `supplier-procurement-intelligence` for redesign, execution controls, supplier evidence and traceability.

## Non-Goals
Do not provide medical diagnosis, certify HACCP compliance, replace competent authorities/local law/training, set commercial rates, or use brand language to soften a material warning.
