# Chef AI Pro Business — Excel / Google Sheets Export Spec v2.4

## Purpose
Define how to design Excel/Google Sheets workbooks for supplier prices, recipe costing, what-if simulations and professional reporting. Use only when the user asks for Excel, Google Sheets, workbook, formula export, template, costing card or dashboard.

## Workbook Principles
1. Separate input from calculation from output.
2. Use structured tables.
3. Use canonical units.
4. Keep supplier prices effective-dated.
5. Mark all assumptions.
6. Do not overwrite historical prices.
7. Audit missing data.

## Recommended Sheets
README, UOM, Ingredients, Suppliers, Supplier_Items, Supplier_Prices, Density, Yield_Rules, Allergens, Ingredient_Allergens, Recipes, Recipe_Lines, Pricing_Profiles, VAT_Profiles, Scenarios, Scenario_Overrides, Calc_Ingredient_Costs, Calc_Recipe_Costs, Out_Recipe_Card, Out_Pricing, Out_What_If, Out_Shopping_List, Out_Allergen_Matrix, Out_Dashboard, Validation_Errors.

## Table Names
tblUOM, tblIngredients, tblSuppliers, tblSupplierItems, tblSupplierPrices, tblDensity, tblYields, tblAllergens, tblIngredientAllergens, tblRecipes, tblRecipeLines, tblPricingProfiles, tblVATProfiles, tblScenarios, tblScenarioOverrides.

## Core Fields

### tblUOM
uom_code, dimension, to_base_factor, base_uom, active.

### tblIngredients
ingredient_id, ingredient_name_el, ingredient_name_en, category, base_uom, default_yield_profile_id, preferred_supplier_item_id, active, notes.

### tblSupplierItems
supplier_item_id, supplier_id, ingredient_id, sku, brand, pack_description, inner_count, inner_qty, inner_uom, price_includes_vat, vat_in, preferred_flag, pack_qty_base.

### tblSupplierPrices
supplier_price_id, supplier_item_id, effective_from, effective_to, gross_pack_price_eur, discount_pct, source_type, source_ref, verified_on, net_pack_price_eur, pack_qty_base, ap_unit_cost_base.

### tblDensity
ingredient_id, density_g_per_ml, avg_piece_g, source, verified_on, notes.

### tblYields
yield_profile_id, ingredient_id, process_code, stage_no, yield_factor, loss_pct, source, effective_from, notes.

### tblRecipes
recipe_id, recipe_revision_id, recipe_name, recipe_type, status, valid_from, saleable_qty, saleable_uom, portion_size, portion_uom, approved_by, notes.

### tblRecipeLines
recipe_revision_id, line_no, line_type, ingredient_id, subrecipe_revision_id, usage_qty, usage_uom, quantity_basis, yield_profile_id, notes, usage_qty_base, yield_total, line_cost_eur.

## Core Formula Patterns

Net pack cost:
```excel
=IF([@price_includes_vat],[@gross_pack_price_eur]/(1+[@vat_in]),[@gross_pack_price_eur])
```

Pack quantity:
```excel
=[@inner_count]*[@inner_qty]*XLOOKUP([@inner_uom],tblUOM[uom_code],tblUOM[to_base_factor])
```

AP unit cost:
```excel
=[@net_pack_price_eur]/[@pack_qty_base]
```

Total yield:
```excel
=PRODUCT(FILTER(tblYields[yield_factor],tblYields[yield_profile_id]=[@yield_profile_id]))
```

EP unit cost:
```excel
=[@ap_unit_cost_base]/[@yield_total]
```

Usage quantity:
```excel
=[@usage_qty]*XLOOKUP([@usage_uom],tblUOM[uom_code],tblUOM[to_base_factor])
```

Ingredient line cost, AP/EP aware:
```excel
=IF([@quantity_basis]="EP",
   [@usage_qty_base]*XLOOKUP([@ingredient_id],Calc_Ingredient_Costs[ingredient_id],Calc_Ingredient_Costs[ep_unit_cost_base]),
   [@usage_qty_base]*XLOOKUP([@ingredient_id],Calc_Ingredient_Costs[ingredient_id],Calc_Ingredient_Costs[ap_unit_cost_base])
)
```

Sub-recipe line cost:
```excel
=[@usage_qty_base]*XLOOKUP([@subrecipe_revision_id],Calc_Recipe_Costs[recipe_revision_id],Calc_Recipe_Costs[saleable_unit_cost_base])
```

Recipe batch cost:
```excel
=SUMIFS(tblRecipeLines[line_cost_eur],tblRecipeLines[recipe_revision_id],[@recipe_revision_id])
```

Saleable unit cost:
```excel
=[@batch_cost_eur]/[@saleable_qty_base]
```

Food cost:
```excel
=[@food_cost_eur]/[@sell_price_net_eur]
```

Gross margin:
```excel
=([@sell_price_net_eur]-[@cost_basis_eur]) / [@sell_price_net_eur]
```

Markup:
```excel
=([@sell_price_net_eur]-[@cost_basis_eur]) / [@cost_basis_eur]
```

Gross price with VAT:
```excel
=[@sell_price_net_eur]*(1+[@vat_out])
```

Quote drift:
```excel
=([@current_cost_eur]-[@baseline_cost_eur]) / [@baseline_cost_eur]
```

Break-even units:
```excel
=[@fixed_cost_eur]/([@sell_price_net_eur]-[@variable_cost_unit_eur])
```

## Validation Errors
Missing supplier price, missing yield, missing density, missing piece weight, invalid yield, invalid VAT, recipe cycle risk, missing allergen status, price below cost, margin below target, quote drift high, supplier price needs review, stale source.

## Export Views
Recipe card, costing summary, pricing recommendation, allergen matrix, shopping list with pack rounding, supplier comparison, quote drift report, event profitability report, dashboard.

## Google Sheets Sync Notes
When using API/integration, write to named tabs and preserve IDs. Do not overwrite approved rows unless user confirms and backend allows it. Supplier prices should be appended as new effective-dated rows, not overwritten.
