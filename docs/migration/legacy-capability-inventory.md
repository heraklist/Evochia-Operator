# Chef AI Pro Business v3.2.2 — Legacy Capability Inventory

**Migration target:** Chef AI Pro Business vNext `4.0.0-alpha.0`  
**Source package:** `chef_ai_pro_business_v3_2_2_final_install_api_package`  
**Purpose:** human-readable index for the Phase 1 migration parity contract. The complete per-capability source evidence, target skills, migration status, regression ids and eval cases are authoritative in `evals/legacy/parity_matrix.yaml`.

## Status vocabulary

- **preserve** — semantics must remain materially unchanged.
- **upgrade** — legacy behavior remains, but vNext adds depth, better routing, stronger authority or new tool/output support.
- **split / merge / retire** — reserved for explicitly reviewed migrations; no must-preserve behavior is retired in this Phase 1 baseline.

## Coverage summary

- Legacy behavior records: **92**
- Must preserve: **92**
- Domains: **20**
- Every must-preserve record has source evidence, target skill(s), regression test id and legacy eval case(s) in the machine-readable parity matrix.

## Domain coverage

| Domain | Capability records |
|---|---:|
| AP/EP and yields | 6 |
| API invocation / approval / security | 19 |
| Culinary answers and troubleshooting | 2 |
| Exports / workbook behavior | 3 |
| Menu development | 2 |
| Pairing and flavor architecture | 3 |
| Pricing / VAT / margin | 8 |
| Professional kitchen workflow | 5 |
| Quality gates | 2 |
| Quote drift | 1 |
| Recipe creation | 1 |
| Recipe specification | 2 |
| Routing | 3 |
| Safety and allergens | 10 |
| Scaling / holding / consistency | 3 |
| Source authority | 2 |
| Storytelling / owner style | 4 |
| Substitution / reformulation | 2 |
| Supplier normalization | 8 |
| What-if / profitability scenarios | 6 |
| **Total** | **92** |

## Representative non-negotiable legacy behaviors

The full list is in `evals/legacy/parity_matrix.yaml`. The following are representative release-critical examples:

- smallest-sufficient routing and material follow-up questions only;
- assumptions never presented as facts;
- original recipe creation and professional recipe specification;
- flavor architecture, menu progression and substitution by functional role;
- menu storytelling and owner culinary style without invented provenance/awards/suppliers;
- practical mise en place, prep timelines, staff briefing and event risk checks;
- non-linear batch scaling and holding-quality planning;
- EU/Greece 14-allergen propagation, cross-contact controls and no allergen-free guarantees;
- AP/EP separation, multiplicative yields, hydration yields above 100%, and missing-yield warnings;
- formula-first costing, configurable VAT, margin/markup/food-cost calculations and commercial verdicts;
- supplier raw-evidence preservation, normalization before comparison and no invented supplier prices;
- scenario calculations that never overwrite approved baselines;
- quote-drift reapproval logic;
- deterministic workbook/export formula patterns;
- explicit API/tool triggering, read-only-first behavior, confirmation before consequential writes, draft/proposed defaults, idempotency, RBAC, audit logging, data minimization and safe non-leaky errors;
- final quality and production-gate checks before release-critical output.

## Authority changes already approved for vNext

1. Generic legacy pricing tiers remain fallback knowledge, but approved Evochia commercial policy will outrank them in Evochia context.
2. Legacy source-priority logic is preserved and will be expanded by the Phase 2 machine-readable Source Registry.
3. Historical proposal/sample prices are evidence/examples, not current company pricing policy.
4. Web research becomes an explicit R&D/evidence source; it may not silently override safety, approved company policy, deterministic formula logic or approved current data.
5. API/integration behavior remains explicit/configured and approval-gated; tool availability is never fabricated.

## Phase 1 acceptance rule

No must-preserve capability may proceed into refactoring without at least one target vNext skill and one regression/eval case. `scripts/validate_parity_coverage.py` enforces this contract against the complete 92-record matrix.
