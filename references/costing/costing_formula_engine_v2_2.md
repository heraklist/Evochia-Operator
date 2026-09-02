# Chef AI Pro Business — Costing Formula Engine v2.2

## Purpose
Define the formula-first costing system for professional F&B recipe costing. It is app-agnostic and can be used in ChatGPT Projects, Excel, Google Sheets, Airtable, a database, API backend or custom app.

## Core Logic
```text
Definitions → Variables → Formulas → Assumptions → Calculation → Output → Commercial Verdict
```

## Net Cost Basis
All internal costing uses net cost excluding recoverable VAT.

VAT layers:
1. Input VAT: removed from supplier prices when recoverable.
2. Output VAT: applied to final selling price for display/quote/invoice output.

Use net values for food cost %, gross margin, contribution margin and break-even. Show gross prices when customer-facing VAT display is needed. VAT rates must be configurable and verified.

## Canonical Units

| Dimension | Base unit |
|---|---|
| Mass | g |
| Volume | mL |
| Count | pc |
| Time | min |
| Currency | EUR |

## Variables

| Symbol | Definition |
|---|---|
| Q_AP | As Purchased quantity |
| Q_EP | Edible/Effective Portion quantity |
| y_i | yield factor for stage i |
| y_total | total yield |
| C_pack_gross | supplier pack price including VAT if applicable |
| C_pack_net | supplier pack price excluding recoverable VAT |
| Q_pack_base | pack quantity in canonical unit |
| c_AP | AP unit cost |
| c_EP | EP unit cost |
| ρ | density g/mL |
| ω | average piece weight g/pc |
| C_line | recipe line cost |
| C_batch | batch cost |
| Q_saleable | saleable output |
| c_portion | cost per portion |
| P_net | net selling price |
| P_gross | gross selling price |
| FC% | food cost percentage |
| GM% | gross margin percentage |
| MU% | markup percentage |
| V | unit variable cost |
| F | fixed cost |
| CM | contribution margin |

## VAT Formulas

If supplier price includes recoverable VAT:
```text
C_pack_net = C_pack_gross / (1 + VAT_in)
```

If supplier price excludes VAT:
```text
C_pack_net = C_pack_gross
```

Final gross selling price:
```text
P_gross = P_net × (1 + VAT_out)
```

If VAT status is unknown, mark `needs_review`.

## Unit Conversion

Same dimension:
```text
Q_base = Q_input × factor_to_base
```

Pack expansion:
```text
Q_pack_base = inner_count × inner_qty × factor_to_base
```

AP unit cost:
```text
c_AP = C_pack_net / Q_pack_base
```

Volume to mass:
```text
Q_g = Q_mL × ρ
```

Mass to volume:
```text
Q_mL = Q_g / ρ
```

Pieces to mass:
```text
Q_g = pcs × ω
```

Rules:
- Do not convert mass↔volume without density.
- Do not convert pc↔mass without average piece weight.
- Do not assume 1 mL = 1 g except for explicit water-like conventions.
- Store density and piece weight per ingredient and source.

## AP / EP Yield Engine

Single-stage:
```text
Yield % = Q_EP / Q_AP
Waste % = 1 - Yield %
```

EP quantity from AP:
```text
Q_EP = Q_AP × y_total
```

AP required:
```text
Q_AP_required = Q_EP_target / y_total
```

EP unit cost:
```text
c_EP = c_AP / y_total
```

Multi-stage:
```text
y_total = y_1 × y_2 × y_3 × ... × y_n
w_total = 1 - y_total
```

Typical:
```text
trim yield × cook yield × service yield
```

Dry-to-cooked gain can be greater than 1.00 for rice, pasta, legumes and similar items.

## Recipe Line Cost

If usage is EP:
```text
C_line = Q_EP_target × c_EP
```

Equivalent:
```text
C_line = (Q_EP_target / y_total) × c_AP
```

If usage is AP:
```text
C_line = Q_AP_used × c_AP
```

Every recipe line declares AP/EP basis, unit, conversion path, supplier price source, yield profile, allergen status and confidence/missing-data flags.

## Batch Cost

```text
C_batch =
Σ ingredient lines
+ Σ sub-recipe lines
+ packaging batch
+ variable labor batch
+ variable overhead batch
```

## Portion Cost
```text
c_portion = C_batch / saleable_portions
```

## Sub-Recipe Cost
```text
c_subrecipe_unit = C_subrecipe_batch / Q_subrecipe_saleable_output
C_subrecipe_line = Q_subrecipe_used × c_subrecipe_unit
```

Rules:
- Sub-recipes must reference specific revisions.
- No recipe may reference itself directly or indirectly.
- Recursively explode recipe trees to ingredient-level cost when needed.

## Packaging, Labor, Overhead

Packaging:
```text
C_packaging_line = packaging_units × c_packaging_unit_net
```

Variable labor:
```text
C_labor_batch = (minutes_batch / 60) × hourly_rate
C_labor_portion = C_labor_batch / saleable_portions
```

Variable overhead:
```text
C_overhead_batch = energy_rate_per_hour × cooking_hours
C_overhead_portion = C_overhead_batch / saleable_portions
```

Define basis explicitly.

## Cost Basis
Allowed cost bases:
- food only
- food + packaging
- food + packaging + variable labor
- full variable cost

Never compare food-only cost to contribution-margin formulas without stating the basis.

## Pricing Formulas

Food cost:
```text
Food Cost % = Cost Basis / P_net
P_net = Cost Basis / Target Food Cost %
```

Gross margin:
```text
GM% = (P_net - Cost Basis) / P_net
P_net = Cost Basis / (1 - Target GM%)
```

Markup:
```text
MU% = (P_net - Cost Basis) / Cost Basis
P_net = Cost Basis × (1 + MU%)
```

Conversion:
```text
GM% = Markup% / (1 + Markup%)
Markup% = GM% / (1 - GM%)
```

## Default Pricing Tiers

| Tier | Food Cost Target | Use |
|---|---:|---|
| Budget | 35% | Competitive / minimum acceptable |
| Balanced | 30% | Recommended default |
| Premium | 25% | High-service / private chef / premium |

Targets are configurable.

## Reliability Status
Use:
- Reliable
- Mostly reliable with minor assumptions
- Incomplete costing
- Unreliable due to missing yield
- Unreliable due to missing supplier price
- Unreliable due to missing VAT/pack/unit
- Unreliable due to missing density/piece weight
- Allergen data incomplete
- Needs review before commercial quote

## Commercial Verdict
Use:
Commercially viable, Tight margin, Needs repricing, Incomplete costing, Unreliable due to missing yield/price, Below cost / not viable, Allergen conflict / do not serve, High quote drift / reapproval required.
