# Chef AI Pro Business — Supplier and Yield Workflow v3.2.2

## Purpose
Defines supplier price file handling, canonical ingredient matching and yield profile selection.

## Core Doctrine
```text
Raw supplier files
→ document classification
→ raw extraction
→ field normalization
→ ingredient matching
→ AP unit cost
→ yield profile selection
→ EP unit cost
→ supplier comparison
→ validation
→ proposed candidate / needs_review / human-approved master
```

Never compare raw supplier prices before normalization.

## Accepted Source Formats
XLS/XLSX, CSV, XML, digital PDF, scanned PDF, screenshots/images, handwritten notes, TXT, email/pasted text, catalogues, invoices, quotes and user-entered prices.

Reliability varies. Low-confidence sources must be reviewed.

## File Inventory Fields
source_file_id, source_file_name, folder_path, file_type, detected_supplier, document_type, document_date, processed_at, extraction_status, extraction_confidence, notes.

## Supplier Detection Priority
1. explicit supplier field
2. invoice/catalogue header
3. VAT/tax ID
4. logo/trading name
5. email sender or metadata
6. folder name
7. file name
8. user clarification

If supplier cannot be detected:
```text
supplier = UNKNOWN_SUPPLIER
status = needs_review
```

## Raw Item Extraction
Preserve raw values exactly. Extract:
raw_item_name, raw_category, raw_brand, raw_sku, raw_pack_description, raw_qty, raw_uom, raw_price, raw_currency, raw_vat_status, raw_vat_rate, raw_discount, raw_date, line_notes.

Raw values are evidence. Normalized fields are separate.

## Normalized Supplier Price Schema
supplier_price_id, supplier_id, supplier_name, supplier_sku, canonical_ingredient_id, canonical_ingredient_name, raw_item_name, brand, category, cut_or_form, quality_grade, pack_description, inner_count, inner_qty, inner_uom, pack_qty_base, base_uom, gross_pack_price_eur, price_includes_vat, vat_rate, net_pack_price_eur, ap_unit_cost_base, effective_from, effective_to, source_type, source_file_name, source_ref, match_confidence, price_confidence, validation_status, reviewed_by, reviewed_on, notes.

## Normalization Formulas
Net price when VAT is included and recoverable:
```text
net_pack_price_eur = gross_pack_price_eur / (1 + vat_rate)
```

If VAT excluded:
```text
net_pack_price_eur = gross_pack_price_eur
```

If VAT unknown:
```text
validation_status = needs_review
```

Pack quantity:
```text
pack_qty_base = inner_count × inner_qty × unit_to_base_factor
```

AP unit cost:
```text
ap_unit_cost_base = net_pack_price_eur / pack_qty_base
```

Discount logic depends on whether discount applies before or after VAT. If unclear, flag.

## Ingredient Matching
Use raw item name, category, SKU, brand, pack size, unit, cut/form, fresh/frozen state, origin/quality, Greek/English aliases, previous approved matches and user corrections.

## Match Levels
- Exact equivalent: same ingredient, form, cut, state
- Comparable: small spec differences, approved as comparable
- Similar not equivalent: same family, different usable form
- Not comparable: different costing object

Only exact equivalent or approved comparable items should be compared directly.

## Do Not Merge Automatically
Never automatically merge whole fish with fillet, skin-on with skin-off, bone-in with boneless, fresh with frozen when yield/quality differs, raw with cooked/prepared product, dry rice with cooked rice, shell-on with peeled, retail pack with horeca bulk pack when economics differ.

## Confidence Scoring

Price confidence:
- High: structured invoice/catalogue with clear item, unit, pack, price, VAT/date
- Medium: mostly clear PDF/image/table with some inferred fields
- Low: screenshot, handwriting, unclear VAT/pack, OCR risk, ambiguous item

Match confidence:
- High: approved alias/SKU or exact name + pack/form/category match
- Medium: good semantic match with one minor missing field
- Low: same general ingredient family but uncertain form/cut/pack

## High-Confidence Proposed Candidate Rule
The GPT must never auto-approve supplier prices into the approved master.

It may classify a normalized row as a **high-confidence proposed candidate** only if:
```text
price_confidence = High
AND match_confidence = High
AND VAT status is known
AND pack size is known
AND effective date is known or accepted
```

Result:
```text
validation_status = proposed
review_status = human_review_required
```

Otherwise:
```text
validation_status = needs_review
```

Human/backend approval is required before any supplier price becomes approved/current. This applies even when extraction and matching confidence are high.

## Supplier Comparison Output
Show canonical item, supplier, raw item, pack, net pack price, AP unit cost, EP unit cost, VAT, source, date, confidence and notes.

Sort by exact equivalence, approved/current prices, lowest AP unit cost, higher confidence and newest effective date. Show similar-but-not-equivalent items separately.

## Yield Profile Selection
Respect ingredient, variety/species, cut/form, process state, stage type, supplier-specific flag, internal test flag, confidence, seasonality, region and last reviewed date.

Examples:
- tomato whole raw ≠ tomato concassé
- whole fish ≠ fillet skin-on
- fillet skin-on ≠ fillet skin-off
- chicken breast bone-in ≠ boneless skinless breast
- dry rice ≠ cooked rice

## Yield Source Hierarchy
1. Internal kitchen test / measured yield
2. Supplier-specific measured yield
3. Official/public yield references
4. Food composition/measure databases
5. Operational benchmark seed
6. Conservative assumption, clearly labeled

Measured internal values override seed defaults.

## Internal Kitchen Test Protocol
Record AP weight, trimmed usable EP weight, cooked weight, served/plated weight, waste reason, supplier, batch/date, operator and photo/reference note.

Calculate:
```text
Trim Yield = raw usable EP / AP weight
Cook Yield = cooked usable / raw usable EP
Service Yield = served usable / cooked usable
Final Yield = Trim × Cook × Service
```

## Cost Reliability Flags
Flag missing supplier price, VAT status, pack size, density, piece weight, yield, low-confidence match, low-confidence price, high-cost ingredient with estimated yield, unknown allergen status, ambiguous raw item, stale source and non-comparable supplier items.
