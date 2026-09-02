# Chef AI Pro Business vNext — Implementation Plan

**Date:** 2026-09-02  
**Design source:** `docs/superpowers/specs/2026-09-02-chef-ai-pro-business-vnext-design.md`  
**Canonical repository:** `heraklist/chef_ai_pro_business`  
**Backend repository:** `heraklist/chef-ai-pro-business-api`  
**Status:** Implementation plan candidate — execute only after owner review  

## 0. Delivery Contract

Build Chef AI Pro Business vNext as a private/company modular skill suite that preserves Chef AI Pro Business v3.2.2 behavior while adding Operator, culinary web R&D, Evochia company/brand/product-development overlays, supplier-price intelligence, branded outputs, and controlled tool integrations.

Implementation is complete only when:

1. legacy parity tests pass;
2. new vNext capability tests pass;
3. no secrets/browser profiles are committed;
4. source authority and supersession are machine-readable;
5. INTERNAL / OPERATIONS / CLIENT-SAFE boundaries are tested;
6. the packaged skill suite passes installation/scan validation on the target OpenAI surface;
7. tool-unavailable paths degrade safely;
8. no persistent FnB Central state is duplicated inside the skill.

## 1. Execution Principles

- Small slices over broad rewrites.
- Tests/evals before or alongside behavior migration.
- Preserve legacy semantics first; refactor second.
- Deterministic calculations remain formula/script driven where possible.
- Company policy overrides generic heuristics only when explicitly in Evochia context.
- External web research is evidence/inspiration, not silent canonical truth.
- No OpenAI API key is required for Phases 0–7.
- API keys/secrets never enter source control, fixtures, docs, screenshots, or chat transcripts.

---

# Phase 0 — Repository Foundation + Security Fence

## Task 0.1 — Bootstrap repository metadata

**Create:**
- `README.md`
- `CHANGELOG.md`
- `VERSION`
- `.gitignore`
- `.gitattributes`
- `SECURITY.md`
- `docs/architecture/README.md`

**Requirements:**
- VERSION starts at `4.0.0-alpha.0` (vNext architecture generation; not claiming production readiness).
- README states private/company scope, canonical repo, backend separation, and no-secret policy.
- SECURITY.md explicitly prohibits public disclosure of client/company-sensitive material and provides a private reporting path placeholder for owner completion.

## Task 0.2 — Add hard repository exclusions

`.gitignore` MUST exclude at minimum:

```gitignore
.env
.env.*
!.env.example
*.pem
*.key
*.p12
.browser_profile_themart/
**/.browser_profile_themart/
.venv/
**/.venv/
__pycache__/
**/__pycache__/
output/
**/output/
*.log
.DS_Store
Thumbs.db
```

Add explicit deny patterns for likely secret/session artifacts from Chromium profiles.

## Task 0.3 — Add repository hygiene validator

**Create:** `scripts/validate_repo_hygiene.py`

Validator fails if tracked/candidate tree contains:
- browser profile directories;
- `.env` or common credential files;
- cookies/session databases;
- Python caches/venvs;
- nested `.git` directories;
- files above an agreed binary-size threshold outside allowlisted `company/evochia/assets` or `data/` paths.

**Test:** `tests/repo/test_repo_hygiene.py`

**Acceptance:**
```bash
python -m pytest tests/repo/test_repo_hygiene.py -q
python scripts/validate_repo_hygiene.py .
```
Both pass on the clean repository and fail on injected forbidden fixtures.

---

# Phase 1 — Definitive Legacy Capability Inventory

## Task 1.1 — Inventory all v3.2.2 source behavior

**Input:** existing `chef_ai_pro_business_v3_2_2_final_install_api_package`.

**Create:** `docs/migration/legacy-capability-inventory.md`

For every legacy behavior record:
- capability id;
- source file;
- source heading/section;
- current behavior;
- target vNext skill;
- preserve / upgrade / split / merge / retire status;
- regression test id;
- notes on changed authority.

## Task 1.2 — Build machine-readable parity matrix

**Create:** `evals/legacy/parity_matrix.yaml`

Minimum domains:
- culinary answers/troubleshooting;
- recipe creation;
- recipe specification;
- pairing/flavor architecture;
- substitution/reformulation;
- menu development;
- storytelling/owner style;
- professional kitchen workflow;
- scaling/holding/consistency;
- safety/allergens;
- AP/EP/yields;
- supplier normalization;
- pricing/VAT/margin;
- what-if;
- quote drift;
- exports;
- API invocation/approval behavior.

## Task 1.3 — Parity coverage validator

**Create:** `scripts/validate_parity_coverage.py`

Fail when a `must_preserve` legacy capability has no target skill or eval case.

**Test:** `tests/migration/test_parity_coverage.py`

---

# Phase 2 — Source Registry + Supersession Model

## Task 2.1 — Define registry schema

**Create:**
- `schemas/source_registry.schema.json`
- `references/source_registry.yaml`

Required fields:
- `source_id`
- `title`
- `path_or_external_ref`
- `source_class`
- `authority`
- `scope`
- `allowed_uses`
- `forbidden_uses`
- `freshness_type`
- `effective_date`
- `last_reviewed_at`
- `supersedes`
- `superseded_by`
- `confidentiality`
- `owner`

Allowed source classes:
- `canonical_policy`
- `canonical_current_data`
- `domain_doctrine`
- `reference`
- `golden_example`
- `historical_evidence`
- `superseded`

## Task 2.2 — Register initial authorities

Register at minimum:
- legacy Chef AI core instructions/doctrine;
- recipe/costing/yield/allergen references;
- Evochia Company Brain current files;
- Evochia Brand Voice;
- owner culinary style;
- official logo guidelines/assets;
- approved proposal/menu samples;
- Colette production recipebook;
- Interactive Dining Master Plan + flyer;
- CI v33 as current canonical CI data;
- older CI versions as superseded;
- The Mart provider code as tool implementation, not business truth;
- historical proposal prices as `historical_evidence`, never current rates.

## Task 2.3 — Registry validator

**Create:** `scripts/validate_source_registry.py`

Checks:
- unique source ids;
- no supersession cycles;
- every canonical current source has owner + review metadata;
- golden examples cannot be marked canonical pricing policy;
- superseded files cannot be selected as current.

**Tests:** `tests/sources/test_source_registry.py`

---

# Phase 3 — Shared Doctrine Migration

## Task 3.1 — Migrate culinary doctrine

**Create/curate under:** `references/culinary/`

Preserve and normalize:
- flavor/pairing logic;
- substitutions/reformulation;
- professional kitchen workflow;
- owner culinary/presentation style;
- menu storytelling doctrine.

Do not duplicate the same doctrine in multiple `SKILL.md` files.

## Task 3.2 — Migrate deterministic F&B doctrine

**Create/curate under:**
- `references/costing/`
- `references/yields/`
- `references/safety/`
- `references/operations/`

Formula-first material remains source-of-truth for math.

## Task 3.3 — Doctrine integrity tests

**Create:** `evals/legacy/doctrine_cases.yaml`

Golden cases must detect regressions such as:
- blind scaling of salt/acid/gelatin/leavening;
- AP/EP inversion;
- recoverable VAT included incorrectly in internal net cost;
- invented supplier prices;
- allergen-free guarantee language.

---

# Phase 4 — Skill Skeletons + Routing Contracts

## Task 4.1 — Create the 12 skill directories

**Create:**

```text
skills/chef-ai-pro-business/
skills/culinary-rnd/
skills/recipe-engineering/
skills/menu-experience-design/
skills/kitchen-event-operations/
skills/food-safety-allergens/
skills/costing-commercial-intelligence/
skills/supplier-procurement-intelligence/
skills/evochia-company-operations/
skills/evochia-brand-documents/
skills/evochia-product-development/
skills/evochia-market-intelligence/
```

Each contains `SKILL.md` with concise:
- purpose;
- triggers;
- inputs;
- authority/resources;
- responsibilities;
- output contract;
- guardrails;
- handoff conditions;
- non-goals.

## Task 4.2 — Build orchestrator routing table

**Create:** `skills/chef-ai-pro-business/references/routing.yaml`

Routing dimensions:
- job intent;
- context (generic F&B vs Evochia);
- risk;
- freshness need;
- tool availability;
- output audience;
- required skills;
- optional skills;
- blockers/approval gates.

## Task 4.3 — Routing evals

**Create:** `evals/routing/routing_cases.yaml`

Cases include:
- quick recipe question → no unnecessary commercial/company modules;
- new trend concept → culinary-rnd + recipe/menu as needed;
- Evochia private-chef enquiry → company + operations + commercial + brand;
- allergen-critical event → safety gate mandatory;
- competitor request → market-intelligence without culinary stack;
- supplier refresh → supplier-intelligence explicit tool path;
- new product concept → product-development + relevant supporting skills.

---

# Phase 5 — Recipe / Menu / Culinary R&D Upgrade

## Task 5.1 — Canonical recipe schema

**Create:**
- `schemas/recipe.schema.json`
- `templates/recipes/production_recipe.yaml`

Fields support:
- id/version/status;
- title/description/category/cuisine;
- yield/portion/service style;
- ingredient lines with AP/EP hooks;
- allergens/dietary tags;
- equipment;
- mise en place;
- detailed method;
- temperature/time/sensory cues;
- finishing;
- holding/regeneration;
- service/plating;
- make-ahead timeline;
- critical quality/safety points;
- failure recovery;
- scaling notes;
- source/inspiration provenance;
- costing hooks.

## Task 5.2 — Culinary research protocol

**Create:** `skills/culinary-rnd/references/research_protocol.md`

Define:
- when web search is expected vs optional;
- Greek + international source coverage;
- culinary/professional/restaurant/trend/visual source roles;
- Pinterest/visual research as inspiration, not safety/recipe authority;
- synthesis/originality rule;
- citation/provenance behavior for research briefs.

## Task 5.3 — Menu/experience schema

**Create:** `schemas/menu_experience.schema.json`

Support internal and client projections from one canonical menu object.

## Task 5.4 — Culinary evals

**Create:** `evals/culinary/`

Test:
- original recipe development;
- classical recipe without forced web dependency;
- trend request with current research;
- Pinterest/visual source labeled as inspiration;
- technical validation after creative ideation;
- client menu projection does not expose internal costing.

---

# Phase 6 — Event Operator + Commercial Intelligence

## Task 6.1 — Canonical event brief schema

**Create:** `schemas/event_brief.schema.json`

Fields include:
- occasion;
- date/location;
- pax/adults/children;
- budget/range;
- culinary direction;
- dietary/allergen requirements;
- service format;
- kitchen/venue constraints;
- staffing;
- equipment;
- transport/accommodation;
- known/unknown fields;
- assumptions;
- approval state.

## Task 6.2 — Event operating flow

**Create:** `skills/kitchen-event-operations/references/event_lifecycle.md`

Lifecycle:
```text
lead/enquiry
→ structured brief
→ feasibility
→ menu
→ recipes
→ production/staff/equipment
→ procurement
→ event economics
→ client proposal
→ prep/packing/run sheet
→ service
→ close-out
→ actual vs estimated
→ approved learning
```

## Task 6.3 — Event economics schema

**Create:** `schemas/event_economics.schema.json`

Support:
- food;
- chef/founder labour;
- assistants/service/stewarding;
- prep/shopping time;
- travel/ferry/flight/parking;
- accommodation/overnight;
- equipment/rental;
- overhead;
- VAT;
- cash cost;
- economic cost;
- contribution/gross profit;
- margin;
- opportunity-cost notes.

## Task 6.4 — Audience boundary tests

**Create:** `tests/outputs/test_audience_boundaries.py`

Fail if CLIENT-SAFE output contains internal cost basis/margin, supplier comparison or internal strategic notes.

---

# Phase 7 — Evochia Company / Brand / Product Development

## Task 7.1 — Build company canonical draft files

**Create as NEEDS_OWNER_APPROVAL initially:**
- `company/evochia/business/company_profile.md`
- `company/evochia/commercial/commercial_policy.md`
- `company/evochia/commercial/current_rates.md`
- `company/evochia/commercial/staffing_policy.md`
- `company/evochia/commercial/terms_policy.md`

Do not mark rates/terms canonical until owner approval.

## Task 7.2 — Brand system

**Create:**
- `company/evochia/brand/brand_voice.md`
- `company/evochia/brand/visual_identity.md`
- `company/evochia/brand/visual_tokens.yaml`
- `company/evochia/brand/document_style_guide.md`
- `company/evochia/brand/assets/`

Typography remains a focused decision produced from site + official guidelines + approved documents. Do not commit font binaries.

## Task 7.3 — Golden output registry

**Create:** `company/evochia/golden_examples/README.md`

Map sample roles:
- private-chef proposal;
- catering/corporate proposal;
- client menu;
- production recipebook;
- Interactive Dining master product plan;
- Interactive Dining client flyer.

Record what each sample controls (structure/tone/layout) and what it does NOT control (e.g. historical prices).

## Task 7.4 — Product-development schema + template

**Create:**
- `schemas/product_plan.schema.json`
- `templates/product-plans/master_product_plan.md`
- `templates/product-plans/decision_register.yaml`
- `templates/product-plans/pilot_evidence_pack.md`

Flow mirrors the approved Interactive Dining pattern without hardcoding its content.

## Task 7.5 — Product-development eval

Input: a different hypothetical Evochia product idea.
Expected:
- product definition;
- target occasions/customers;
- positioning;
- operating model;
- pilot hypothesis/evidence plan;
- economics/capacity questions;
- decision states;
- client-facing projection;
- no premature launch/pricing claims.

---

# Phase 8 — The Mart Provider Migration

## Task 8.1 — Extract safe provider subset

From `themart_capture.zip`, migrate only:
- `themart_capture.py`
- `themart_extract_existing_html.py`
- `categories.json`
- `requirements.txt`
- `run_windows.bat` if still useful;
- `README_GR.md` distilled to provider runbook;
- `README_HOTFIX_GR.md` distilled into known-issues/history;
- `tests/test_navigation.py` after cache removal;
- `test_recovery_extractor.py` normalized under tests.

**Target:** `scripts/supplier-providers/themart/`

Explicitly exclude `.browser_profile_themart`, caches, venv, output, nested git and credentials.

## Task 8.2 — Provider interface contract

**Create:** `schemas/supplier_price_snapshot.schema.json`

Normalized provider result includes:
- provider;
- captured_at;
- product/SKU;
- product name;
- pack/unit;
- gross/net price where known;
- VAT status/rate where known;
- unit price;
- source URL/reference;
- evidence state;
- confidence;
- parsing warnings;
- raw capture reference (local only where sensitive).

## Task 8.3 — Local-only profile configuration

Provider accepts a configurable local profile path from environment/config, never a hardcoded committed browser profile.

Example local variable name:
`THEMART_BROWSER_PROFILE_DIR`

Document it in `.env.example` without any secret value.

## Task 8.4 — Provider regression tests

Must preserve existing recovery protections:
- no cross-product price bleeding;
- correct URL/product association;
- spreadsheet formula-injection safety;
- local path/privacy sanitization;
- strict failure state for ambiguous extraction;
- deterministic fixture normalization.

---

# Phase 9 — Artifact Contracts and Renderers

## Task 9.1 — Separate canonical data from renderer

No PDF/DOCX/XLSX template contains business logic that is absent from canonical schemas.

## Task 9.2 — Recipebook renderer contract

Define A4 production recipebook requirements from the approved Colette sample:
- A4 print-ready;
- compact/readable;
- professional recipe blocks;
- shopping list aggregation;
- production timeline;
- consistent pagination/header/footer;
- brand-aware but operations-first.

## Task 9.3 — Proposal/menu/flyer renderer contracts

Define artifact-specific:
- structure;
- audience;
- brand voice;
- visual tokens;
- allowed commercial data;
- required terms;
- confidentiality rules;
- internal-to-client projection rules.

## Task 9.4 — Artifact golden tests

Test structured outputs first; visual rendering comparison follows once typography is locked.

---

# Phase 10 — Market Intelligence / CI / SEO Integration

## Task 10.1 — Register CI v33

Treat latest approved v33 workbook as `canonical_current_data` for current competitive intelligence; historical CI versions remain superseded evidence.

## Task 10.2 — Market intelligence routing

CI/SEO/growth modules are optional and must not load for ordinary recipe/event operations.

## Task 10.3 — Freshness and evidence rules

Current claims requiring fresh public evidence trigger web research; the workbook remains company intelligence context, not proof that the external market has not changed.

---

# Phase 11 — API / Integration Contracts

**No OpenAI API key required before this phase unless an earlier test explicitly needs an OpenAI API call.**

## Task 11.1 — Import backend contracts only

**Create:** `integrations/chef-ai-api/`

Store:
- API capability map;
- OpenAPI contract references/copies as appropriate;
- auth/environment documentation;
- draft/proposed/approval semantics.

Backend source stays in `heraklist/chef-ai-pro-business-api`.

## Task 11.2 — Explicit side-effect policy

Reads may be invoked when the user requests/configures them.
Writes require:
1. proposed action summary;
2. affected records;
3. material assumptions;
4. explicit confirmation;
5. idempotency/retry behavior where available.

## Task 11.3 — FnB Central handoff contract

**Create:** `integrations/fnb-central/handoff_contract.md`

Define structured handoffs for recipe/event/quote/supplier data without creating duplicate persistence in the skill repo.

---

# Phase 12 — Evaluation Harness + Release Candidate

## Task 12.1 — Eval runner

**Create:** `evals/run_evals.py` or equivalent lightweight harness suitable for local/Codex validation.

Categories:
- legacy;
- routing;
- culinary;
- safety;
- costing;
- supplier;
- operations;
- brand;
- product-development;
- market-intelligence;
- integrations;
- leakage/security.

## Task 12.2 — Cross-skill end-to-end cases

Minimum E2E cases:
1. classic recipe → production recipe;
2. trend research → original dish → recipe;
3. private chef enquiry → menu → costing → proposal;
4. catering event → production/shopping/run sheet;
5. allergen-critical request → safe block/alternative;
6. supplier snapshot → normalized EP cost;
7. new Evochia product → pilot plan → client flyer payload;
8. market/competitor question → CI + fresh web evidence;
9. tool unavailable → safe fallback;
10. client-safe output leakage check.

## Task 12.3 — Package validator

Validate:
- every skill has valid required metadata/structure for current OpenAI Skill format;
- referenced resource paths exist;
- no forbidden files packaged;
- no broken source-registry refs;
- package size within target limits;
- private/confidential assets are intentionally included.

## Task 12.4 — OpenAI surface validation

On eligible target workspace:
- upload/install candidate;
- review scan result;
- run smoke tests;
- run selected parity/E2E tests;
- verify one-or-more skill routing behavior;
- record version and evidence.

---

# Phase 13 — Typography + Commercial Policy Lock (Parallel Owner Review Track)

These are deliberate owner-approved tracks, not prerequisites for early skill skeleton work.

## Task 13.1 — Typography audit

Audit:
- current evochia.gr;
- official logo guidelines;
- current proposals;
- menus;
- Interactive Dining plan/flyer;
- production recipebook.

Deliver:
- display typography;
- document heading typography;
- body typography;
- Greek/Latin compatibility;
- PDF-safe fallbacks;
- artifact-class rules.

No font binaries are committed merely for convenience.

## Task 13.2 — Commercial policy review

Owner approves/revises:
- current rates;
- service fee model;
- food/supplier cost treatment;
- VAT wording;
- staffing thresholds;
- travel/islands/yachts;
- overnight/accommodation;
- equipment;
- children;
- promo/agency rules;
- deposit/payment/cancellation/validity terms;
- profitability/economic-cost rules.

Only approved values move from `NEEDS_OWNER_APPROVAL` to canonical policy.

---

# Recommended Commit / PR Sequence

1. `chore: bootstrap vnext repository and security fence`
2. `docs: add legacy capability inventory and parity matrix`
3. `feat: add source registry and validators`
4. `refactor: migrate shared culinary fnb and safety doctrine`
5. `feat: add orchestrator and skill skeletons`
6. `feat: add recipe menu and culinary rnd contracts`
7. `feat: add event operator and commercial contracts`
8. `feat: add evochia company brand and product development layers`
9. `feat: migrate safe themart provider subset`
10. `feat: add artifact contracts and golden output mapping`
11. `feat: add market intelligence routing`
12. `feat: add api and fnb central handoff contracts`
13. `test: complete legacy vnext and e2e evaluation harness`
14. `release: package private skill suite v4 alpha candidate`

Each commit/PR must keep the repository validation suite green.

---

# First Executable Slice After Plan Approval

Start only with **Phase 0 + Phase 1**:

1. initialize/clone `heraklist/chef_ai_pro_business` in an isolated worktree;
2. add repo foundation/security fence;
3. add the approved design spec and this implementation plan;
4. build definitive v3.2.2 capability inventory;
5. create parity matrix + validator/tests;
6. run hygiene + parity-coverage tests;
7. review results before migrating behavior.

**Do not build sub-skills yet in the first slice.**

This gives a measurable baseline proving exactly what must survive before the monolith is decomposed.

---

# Definition of Done for v4 Alpha Candidate

A v4 alpha candidate exists only when:

```text
approved architecture
→ clean repo/security fence
→ complete legacy inventory
→ complete source registry
→ shared doctrine migrated
→ 12 skill contracts implemented
→ recipe/menu/operator/company/product layers wired
→ safe The Mart provider integrated
→ artifact contracts defined
→ API/FnB handoffs documented
→ legacy parity green
→ vNext evals green
→ leakage/security checks green
→ OpenAI skill package validates/installs
→ owner-approved release evidence recorded
```

No single passing demo is sufficient evidence of migration success.
