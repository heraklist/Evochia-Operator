---
name: food-safety-allergens
description: Use when food safety, allergens, cross-contact, raw or undercooked foods, holding, leftovers, preservation, high-risk guests, or service-critical dietary claims materially affect the task.
---
# Food Safety Allergens

## Purpose
Provide the mandatory safety/allergen gate. Safety authority outranks creativity, margin, convenience and presentation.

## When to Use
Use for the EU/Greece 14 allergens, severe allergy/celiac concerns, cross-contact, raw animal foods, sous vide, fermentation/canning, hot/cold holding, leftovers, vulnerable guests or any client-facing safety claim.

## Authority and Resources
Read `references/safety/food_safety_allergens_v2_5.md` and `data/allergens/fnb_allergen_master_v1.csv`. Current official guidance should be sought when exact current regulatory/temperature guidance is material.

## Responsibilities
Propagate ingredient/sub-recipe/recipe/menu allergens; distinguish contains, may-contain, cross-contact, exempt and unknown; identify hard conflicts; specify operational controls and review status; state what remains unverified.

## Output Contract
Return a risk summary, conservative recommendation, practical controls, avoid-list, verification boundary and safer alternative when useful. For service-critical cases, provide OPERATIONS allergen notes/matrix suitable for trained human review.

## Guardrails
Never guarantee safe, allergen-free, gluten-free, nut-free or medically suitable food. Unknown is not safe. Supplier/item changes require re-check. Severe-allergy client outputs require trained human verification.

## Handoffs
Return hard-blocks to the orchestrator. Coordinate with `recipe-engineering`, `menu-experience-design` and `kitchen-event-operations` for redesign and operational controls.

## Non-Goals
Do not provide medical diagnosis, replace HACCP/local law/training, set commercial rates or use brand language to soften a material warning.
