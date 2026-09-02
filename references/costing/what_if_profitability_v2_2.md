# Chef AI Pro Business — What-If, Pricing and Profitability v2.2

## Purpose
Defines scenario logic, event profitability, quote drift, contribution margin, break-even and pricing simulations.

## Core Scenario Doctrine
A what-if scenario must never overwrite baseline data.

Correct:
```text
Baseline data + scenario overrides = scenario result
```

Every scenario declares baseline version, scenario name, as-of date, changed assumptions, unchanged assumptions, affected items/events and result delta versus baseline.

## Core Variables
P = net selling price per unit  
Q = quantity / portions / guests sold  
V = unit variable cost  
F = fixed cost  
C_food = food cost per unit  
C_pack = packaging cost per unit  
C_labor_var = variable labor per unit  
C_overhead_var = variable overhead per unit  
VAT_out = output VAT rate  
FC_target = target food cost %  
GM_target = target gross margin %  
MU_target = target markup %  
y_total = total yield  
inflation_factor = cost increase/decrease factor  
discount = discount rate or amount  
mix_i = menu mix share

## Cost Stack
```text
C_food_unit = Σ ingredient and sub-recipe cost per unit
C_pack_unit = packaging cost per unit
C_labor_var_unit = variable labor per unit
C_overhead_var_unit = variable overhead per unit
V = C_food_unit + C_pack_unit + C_labor_var_unit + C_overhead_var_unit + C_channel_unit
```

Define cost basis explicitly: food only, food + packaging, full variable basis.

## Revenue and Profit
```text
Revenue_net = P × Q
Revenue_gross = Revenue_net × (1 + VAT_out)
Gross Profit = (P - CostBasis_unit) × Q
CM_unit = P - V
CM_total = (P - V) × Q
CM_ratio = (P - V) / P
Operating Profit = (P - V) × Q - F
```

## Break-Even
```text
BreakEvenUnits = F / (P - V)
```

Valid only when P > V. If P <= V, state that break-even cannot be achieved through volume alone.

```text
BreakEvenRevenue = F / CM_ratio
MarginOfSafetyUnits = Q - BreakEvenUnits
MarginOfSafety% = (Q - BreakEvenUnits) / Q
Required P = V + (F / Q) + TargetProfit_per_guest
Required P = V + ((F + TargetProfit_total) / Q)
```

## Pricing Scenarios
```text
P = CostBasis / FC_target
P = CostBasis / (1 - GM_target)
P = CostBasis × (1 + MU_target)
P_discounted = P × (1 - discount%)
CM_unit_discounted = P_discounted - V
Profit_delta = (P_discounted - P) × Q
Minimum_P = V + Required_CM_unit
Minimum_P = V + (F / Q)
```

## Ingredient Inflation
```text
New Ingredient Cost = Baseline Ingredient Cost × (1 + inflation%)
C_recipe_new = C_recipe_baseline - C_line_old + C_line_new
RecipeDrift% ≈ Σ(Share_i_baseline × Drift_i%)
```

## Yield Sensitivity
```text
c_EP = c_AP / y_total
c_EP_new = c_AP / y_new
Yield Cost Drift% = (c_EP_new - c_EP_old) / c_EP_old
Q_AP_required_new = Q_EP_target / y_new
```

## Portion Simulation
```text
New Line Cost = Old Line Cost × (New Portion Qty / Old Portion Qty)
C_portion_new = Σ New Line Costs + Packaging + Labor + Overhead
GM_new = (P - C_portion_new) / P
FC_new = C_food_new / P
```

## Event Profitability
```text
Revenue_event = P_per_guest × Guest_Count
VariableCost_event = V_per_guest × Guest_Count
TotalCost_event = VariableCost_event + FixedEventCosts
Profit_event = Revenue_event - TotalCost_event
Event GM% = Profit_event / Revenue_event
FixedCost_per_guest = FixedEventCosts / Guest_Count
```

Small private chef/catering events can be unprofitable even when food cost looks healthy.

## Quote Drift
```text
CostDrift€ = C_current - C_baseline
CostDrift% = (C_current - C_baseline) / C_baseline
ProfitDrift€ = -CostDrift€
```

Thresholds:
| Drift | Status | Action |
|---:|---|---|
| 0–3% | Fresh | No action |
| 3–7% | Aging | Review |
| 7–12% | Stale | Reprice recommended |
| >12% | High risk | Reapproval required |

## Menu Mix
```text
CM_i = P_i - V_i
WeightedCM = Σ(mix_i × CM_i)
BreakEvenUnits_total = F / WeightedCM
Σ mix_i = 1
```

## Output Verdicts
Use: Commercially viable, Tight margin, Needs repricing, Reprice recommended, High quote drift / reapproval required, Break-even impossible through volume alone, Reduce portion or raise price, Change supplier/product form, Add minimum charge/guest minimum, Separate labor/service fee, Redesign menu.
