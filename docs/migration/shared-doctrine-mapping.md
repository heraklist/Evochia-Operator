# Phase 3 — Shared Doctrine Migration Map

**Migration mode:** lossless copy first; skill-specific refactoring happens only after integrity is locked.

| Legacy source | vNext shared target | Role |
|---|---|---|
| `06_flavor_pairing_substitution_system_v2_1.md` | `references/culinary/flavor_pairing_substitution_v2_1.md` | flavor architecture, pairing, substitution doctrine |
| `07_menu_storytelling_owner_style_v2_1.md` | `references/culinary/owner_style_storytelling_v2_1.md` | owner culinary style and storytelling |
| `08_professional_kitchen_workflows_v2_2.md` | `references/operations/professional_kitchen_workflows_v2_2.md` | production/service/scaling doctrine |
| `04_output_router_and_templates_v2_1.md` | `references/operations/output_router_templates_v2_1.md` | legacy output behavior reference |
| `05_safety_allergen_rules_v2_5.md` | `references/safety/food_safety_allergens_v2_5.md` | safety/allergen gate doctrine |
| `09_costing_formula_engine_v2_2.md` | `references/costing/costing_formula_engine_v2_2.md` | deterministic costing/AP-EP/VAT formulas |
| `10_supplier_yield_workflow_v3_2_2.md` | `references/yields/supplier_yield_workflow_v3_2_2.md` | supplier normalization and yield hierarchy |
| `11_what_if_pricing_profitability_v2_2.md` | `references/costing/what_if_profitability_v2_2.md` | scenarios, profitability, quote drift |
| `12_excel_sheets_export_spec_v2_4.md` | `references/exports/excel_sheets_export_spec_v2_4.md` | spreadsheet/export formula doctrine |
| `04_FNB_Allergen_Master_v1.csv` | `data/allergens/fnb_allergen_master_v1.csv` | allergen reference data |
| `04_FNB_Basic_Ingredient_Yields_v1.csv` | `data/yields/fnb_basic_ingredient_yields_v1.csv` | fallback yield reference data |

`references/doctrine_manifest.yaml` records SHA-256 and byte size for every migrated artifact. `scripts/validate_doctrine_integrity.py` fails if any lossless copy changes before an explicit reviewed migration replaces it.

## Release-critical semantic probes

The Phase 3 tests explicitly preserve:
- non-linear scaling safeguards for salt/acid/spices/yeast/gelatin/thickeners/leavening;
- heat-transfer, evaporation, cooling and plating-speed considerations;
- no allergen-free/safe guarantee and separation of cross-contact from confirmed presence;
- net costing excluding recoverable VAT;
- AP/EP equations and yield-adjusted cost;
- supplier raw evidence kept separate from normalized records and no auto-approval;
- what-if scenarios never mutating the approved baseline.
