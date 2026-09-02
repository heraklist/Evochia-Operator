# Chef AI Pro Business vNext — Skill Suite Architecture Design

**Date:** 2026-09-02  
**Status:** Design candidate for owner review — implementation locked until approval  
**Canonical repository:** `heraklist/chef_ai_pro_business`  
**Separate execution backend:** `heraklist/chef-ai-pro-business-api`

## 1. Product Definition

Chef AI Pro Business vNext is a private/company F&B Operating Copilot and skill suite. It preserves the validated capabilities and behavior of Chef AI Pro Business v3.2.2 while adding modular orchestration, culinary R&D, event operations, Evochia company policy, branded documents, product development, market intelligence, and controlled tool execution.

It is not a monolithic prompt and it is not a second FnB Central database/application.

### Core role

```text
Culinary creator + professional recipe engineer
+ F&B costing/commercial intelligence
+ event/private-chef operator
+ Evochia company/brand copilot
+ product-development copilot
+ controlled research/tool orchestrator
```

## 2. Migration Contract — Non-Negotiable Legacy Parity

The vNext build MUST preserve the legacy v3.2.2 capability set unless explicitly superseded by an approved company policy or safer/higher-authority rule.

### Legacy capabilities that must remain

- Quick culinary answers and culinary troubleshooting
- Original recipe creation
- Professional recipe specifications
- Flavor architecture and pairing logic
- Ingredient substitutions and reformulation by functional role
- Menu and tasting-menu development
- Private dinner / event menu creation
- Menu storytelling and owner culinary style
- Professional kitchen workflows
- Mise en place, prep and service planning
- Batch scaling with non-linear scaling safeguards
- Holding-quality planning and consistency controls
- EU/Greece allergen review and propagation
- Food-safety priority over creativity/margin
- AP/EP costing and multi-stage yields
- Supplier-price normalization and comparison
- Pricing, margin, markup and configurable VAT logic
- What-if scenarios without baseline overwrite
- Quote drift and reapproval logic
- Excel/Sheets export structures
- Draft/proposed/needs-review states
- Human approval gates for consequential records and final commercial outputs
- API/integration workflows only when explicitly requested/configured
- Evaluation/regression behavior

### Migration acceptance rule

A new architecture is not accepted because the skill installs. It is accepted only when legacy parity tests and new vNext capability tests pass.

## 3. Product Principles

1. **Creativity before optimization.** Commercial validation refines an idea; it must not erase culinary identity.
2. **Dinner/service outcome before interaction or novelty.** Experiential features may not compromise the core culinary/service result.
3. **Facts, assumptions, estimates and approvals stay distinct.**
4. **Source authority is explicit.** Uploaded files do not all have equal authority.
5. **Safety can block downstream recommendations.**
6. **Internal, operations and client-safe outputs are separate information boundaries.**
7. **Tools extend the intelligence; they do not define it.**
8. **Web research supplies signals and evidence; Chef AI performs original synthesis and technical validation.**
9. **Human approval remains required for consequential commercial/master-data actions.**
10. **FnB Central remains the persistent structured operating system; Chef AI remains the intelligence/orchestration layer.**

## 4. High-Level Runtime Architecture

```text
USER REQUEST
    ↓
MAIN ORCHESTRATOR
    ↓
Job + Context + Risk + Audience classification
    ↓
Relevant sub-skills only
    ↓
Relevant authoritative references/data only
    ↓
Optional research/tools when the job requires them
    ↓
Safety / policy / commercial / quality gates
    ↓
INTERNAL | OPERATIONS | CLIENT-SAFE output
    ↓
Draft | artifact | explicit tool handoff/action
```

## 5. Final Proposed Skill Suite

The suite uses one primary orchestrator plus focused sibling skills. Shared references, templates, data and scripts are not automatically separate skills.

### 5.1 `chef-ai-pro-business`

**Role:** main orchestrator and routing contract.  
**Triggers:** any Chef AI Pro Business request.  
**Responsibilities:** identify the job, choose sub-skills, load only relevant authority, track assumptions/confidence, enforce output boundary, request tool use when necessary, and combine results.

### 5.2 `culinary-rnd`

**Role:** creativity, culinary concept development, trend/inspiration research and original synthesis.  
**Triggers:** new ideas, trends, contemporary concepts, new dishes, plating, cuisine exploration, novel event concepts.  
**Research:** Greek and international web, culinary publications, chefs/restaurants, visual sources such as Pinterest where publicly accessible, and other relevant public trend evidence.  
**Guardrail:** research material is inspiration/reference, not an automatically trusted recipe or safety authority.

### 5.3 `recipe-engineering`

**Role:** convert an idea/dish into a technically executable professional recipe.  
**Outputs:** canonical structured recipe, single recipe card, scalable production spec, A4 production recipebook data, shopping/prep hooks.  
**Required depth when professional:** yield, portions, equipment, ingredients, AP/EP where relevant, mise en place, detailed method, temperature/time/sensory cues, finishing, holding, service, make-ahead, critical points, failure recovery, allergens and scaling notes.

### 5.4 `menu-experience-design`

**Role:** menu architecture and guest experience.  
**Responsibilities:** occasion, progression, balance, course structure, dietary alternatives, culinary narrative, plating/service complexity and experience flow.  
**Client projection:** applies Evochia brand style only when the output is client-facing.

### 5.5 `kitchen-event-operations`

**Role:** operator layer for private chef, catering and event execution.  
**Responsibilities:** event intake, structured brief, feasibility, staffing, equipment, production, timeline, shopping requirements, packing/loading, run sheet, service flow, close-out and actual-vs-estimated learning hooks.

### 5.6 `food-safety-allergens`

**Role:** safety gate.  
**Authority:** outranks creativity, commercial optimization and brand presentation.  
**Responsibilities:** EU/Greece allergens, cross-contact distinction, unknown-status handling, high-risk service/holding issues, allergen matrices and service notes.  
**Rule:** no guarantee of allergen-free status; trained human review is required for client/service-critical allergen output.

### 5.7 `costing-commercial-intelligence`

**Role:** deterministic F&B costing and commercial reasoning.  
**Responsibilities:** AP/EP, yields, recipe/sub-recipe cost, event economics, labour/staff/travel/equipment/overhead, VAT, price/margin/markup, minimum viable price, what-if, quote drift, profitability and opportunity-cost analysis.  
**Company overlay:** Evochia commercial policy overrides generic default pricing heuristics when operating in Evochia context.

### 5.8 `supplier-procurement-intelligence`

**Role:** supplier price evidence, normalization, freshness and purchasing intelligence.  
**Responsibilities:** raw evidence preservation, pack/VAT/unit normalization, price confidence, yield-sensitive EP cost, price snapshots, purchase-plan inputs and provider adapters.  
**Provider 1:** The Mart local collector.

### 5.9 `evochia-company-operations`

**Role:** canonical company context and operational/commercial policy overlay.  
**Responsibilities:** company facts, services, service boundaries, staffing policy, pricing/rates, travel/island/yacht rules, terms, promo/agency rules and other approved company policies.  
**Rule:** company facts/policies are not inferred from historical proposal prices.

### 5.10 `evochia-brand-documents`

**Role:** transform approved internal content into Evochia client-facing communication and branded artifacts.  
**Responsibilities:** brand voice, EL/EN adaptation, menu language, proposal language, flyers/product sheets, visual tokens and document-style rules.  
**Golden examples:** current private-chef proposal, catering proposal, menu samples, Interactive Dining flyer, production recipebook.

### 5.11 `evochia-product-development`

**Role:** create and validate new Evochia products from opportunity to pilot/commercial packaging.  
**Golden model:** Interactive Dining Master Business & Product Plan.  
**Workflow:** opportunity → product definition → customer/occasion → value proposition → architecture → experience → culinary system → operating model → pilot → evidence/validation → brand/GTM → economics/capacity → commercial packaging → risk/governance → decision gates.  
**Decision states:** LOCKED / UNDER VALIDATION / OPEN / PENDING (localized in working language).

### 5.12 `evochia-market-intelligence`

**Role:** optional peripheral company intelligence.  
**Modules:** competitive intelligence, SEO intelligence and growth/market opportunity analysis.  
**Canonical current CI dataset:** latest approved v33 workbook; older versions remain historical/superseded.

## 6. Shared Resources — Not Separate Skills by Default

```text
references/
  culinary/
  costing/
  safety/
  operations/
  company/evochia/
  research/
templates/
  recipes/
  menus/
  proposals/
  product-plans/
  flyers/
  operations/
schemas/
  recipe/
  event/
  costing/
  quote/
  supplier/
data/
  yields/
  allergens/
  ci/
scripts/
  supplier-providers/
  validators/
evals/
```

## 7. Source Registry and Authority Model

Every significant source receives metadata for authority, scope, freshness, supersession and allowed uses.

### Source classes

- `canonical_policy`
- `canonical_current_data`
- `domain_doctrine`
- `reference`
- `golden_example`
- `historical_evidence`
- `superseded`

### Runtime precedence

1. Safety/allergen authority
2. Current explicit user instruction for the present task
3. Canonical Evochia company policy
4. Approved current/live operational data
5. Deterministic costing/yield engines
6. Chef AI professional domain doctrine
7. Current external research/evidence
8. Owner creative/style preferences
9. Golden examples and historical evidence
10. General model knowledge

### Required semantics

A historical proposal may influence proposal structure and style but must not silently become a current rate card.  
A Brand Voice file may control tone but not override food safety or current commercial policy.  
The Mart price data may supply supplier evidence but not company service pricing policy.  
Current CI data may inform market intelligence but not recipe costing.  
External web evidence may inform current research but cannot silently replace approved company policy.

## 8. Decision and Assumption Ledger

Serious recipes, events, costings, proposals, product plans and strategic recommendations should classify important inputs and conclusions as one of:

- `FACT`
- `APPROVED_DATA`
- `EXTERNAL_EVIDENCE`
- `ESTIMATE`
- `ASSUMPTION`
- `NEEDS_REVIEW`
- `APPROVED_DECISION`

Product-development workflows additionally track:

- `LOCKED`
- `UNDER_VALIDATION`
- `OPEN`
- `PENDING`

## 9. Tool and Research Model

### 9.1 Web culinary R&D

Automatic/expected when the user requests trends, novelty, research, current ideas, contemporary concepts or visual inspiration. Optional for classical/well-defined recipes.

Research roles:

- official/safety sources → safety/factual authority
- professional culinary sources → technique reference
- restaurant/chef evidence → contemporary execution/positioning signal
- trend publications → trend signal
- Pinterest/visual/social sources → visual inspiration signal

The system must synthesize rather than copy source recipes or presentation verbatim.

### 9.2 The Mart local collector

The existing `themart_capture_tool` is migrated as a provider implementation, not rewritten from scratch.

Repository-safe assets may include:

- `themart_capture.py`
- `themart_extract_existing_html.py`
- `categories.json`
- `requirements.txt`
- relevant tests/runbook

Never commit or package:

- `.browser_profile_themart/`
- credentials/cookies/tokens
- `.venv/`
- `__pycache__/`
- raw local `output/` snapshots unless explicitly sanitized and selected as fixtures
- nested `.git/`

The authenticated browser profile remains local-only and configurable by path.

Execution rule: refreshing/capturing supplier prices is an explicit user-requested local/tool action. The skill may use the latest validated snapshot when live refresh is unavailable.

### 9.3 Chef AI API

The API remains a separate backend. The skill repo contains contracts/integration references, not the backend implementation.

API calls remain explicit-process driven. Consequential writes require summary + explicit confirmation and should default to draft/proposed/needs-review states.

### 9.4 Artifact generation

Canonical structured objects should drive multiple views rather than duplicating business logic across PDFs/XLSX/docs.

Example:

```text
canonical recipe object
  → chat recipe
  → A4 production recipe
  → recipebook
  → XLSX production workbook
  → shopping list
  → prep timeline
```

## 10. Output Information Boundaries

### INTERNAL
May include cost basis, margin, opportunity cost, assumptions, risks, supplier evidence and strategic notes.

### OPERATIONS
May include production quantities, prep, staffing, equipment, allergens, run sheet and service notes.

### CLIENT-SAFE
Contains only approved client-facing information: concept/menu, service scope, fee/terms, dietary wording and Evochia brand communication. Internal margins, supplier comparison logic and hidden strategic notes must not leak.

## 11. Evochia Brand and Document System

### Existing authorities

- Official logo/identity guideline pack for logo, mark and official palette
- Evochia Brand Voice for language/tone
- Current site and approved documents for typography/document-system evidence
- Golden proposal/menu/flyer/recipebook examples for artifact-specific layout patterns

### Typography

Not locked in this design version. It will be resolved by a dedicated visual audit across:

1. current evochia.gr implementation
2. official logo guidelines
3. current approved proposals
4. menu samples
5. Interactive Dining plan/flyer
6. production recipebook

The result may intentionally be a typography system by artifact class rather than one font for every use.

### Brand assets

Canonical SVG/PNG logo assets are stored as assets; font files are not required merely to reproduce vectorized logo artwork.

## 12. Golden Output Families

### Professional Recipe / Production Recipebook

Golden sample: Colette production recipebook.  
Target: printable A4 production use; structured recipe content; dense but readable; recipe data shared with shopping/production outputs.

### Client Menu

Golden samples: Evochia menu PDFs.  
Target: culinary concept, clear dish identity, atmospheric but restrained storytelling, client-safe dietary presentation.

### Private Chef / Catering Proposal

Golden samples: approved Evochia proposal PDFs/docs.  
Target: service-specific proposal structure, clear commercial terms, correct scope, Evochia voice and client-safe pricing presentation.

### Product Master Plan + Flyer

Golden sample: Interactive Dining Master Business & Product Plan + client flyer.  
Target relationship:

```text
internal master product plan
  → approved product definition
  → client product sheet/flyer
  → enquiry-specific menu
  → proposal
```

Internal annexes and commercially sensitive details are removable for external distribution.

## 13. FnB Central Boundary

### Chef AI Pro Business owns

- reasoning
- creative development
- research
- recommendations
- structured drafts
- scenario analysis
- orchestration
- document/content generation
- tool handoff decisions

### FnB Central owns when available

- persistent structured operational records
- canonical database state
- event/client/recipe/supplier persistence
- inventory/stock movements where implemented
- operational history
- reports based on stored records

### Rule

Do not build a second persistent FnB Central inside the skill. Use structured handoff/sync contracts when FnB Central becomes available.

## 14. Security and Privacy Boundaries

- No browser profiles, credentials, session cookies, secrets or API keys in the repo.
- Company-confidential master plans and internal economics are private/company resources.
- Client-facing outputs must not expose internal appendices, hidden margin, supplier evidence or internal risk notes.
- External research must not silently become canonical company truth.
- Consequential external writes remain confirmation-gated.

## 15. Evaluation Strategy

### 15.1 Legacy parity suite

Must include representative tests for:

- original recipe creation
- professional recipe spec
- non-linear batch scaling
- substitution/reformulation
- menu creation and storytelling
- kitchen/event execution planning
- food safety/allergen handling
- AP/EP/yield costing
- supplier normalization
- pricing/VAT/margin
- what-if baseline preservation
- quote drift
- Excel/export structure
- API explicit-invocation/confirmation behavior

### 15.2 New vNext suite

Must include:

- current web culinary R&D → original synthesis
- visual inspiration source correctly labeled
- Evochia company-policy override of generic pricing defaults
- event intake → operations → economics → client proposal
- The Mart snapshot normalization/freshness handling
- A4 recipebook structured output contract
- internal vs client-safe leakage test
- Interactive Dining-style product-development flow
- product decision-state tracking
- CI v33 selected over superseded CI versions
- tool-unavailable graceful fallback

### 15.3 Cross-skill contract tests

Important flows must test handoffs, not only isolated skill behavior.

## 16. Repository Shape

```text
chef_ai_pro_business/
├── README.md
├── CHANGELOG.md
├── VERSION
├── .gitignore
├── docs/
│   └── superpowers/specs/
├── skills/
│   ├── chef-ai-pro-business/
│   ├── culinary-rnd/
│   ├── recipe-engineering/
│   ├── menu-experience-design/
│   ├── kitchen-event-operations/
│   ├── food-safety-allergens/
│   ├── costing-commercial-intelligence/
│   ├── supplier-procurement-intelligence/
│   ├── evochia-company-operations/
│   ├── evochia-brand-documents/
│   ├── evochia-product-development/
│   └── evochia-market-intelligence/
├── references/
├── company/evochia/
├── templates/
├── schemas/
├── data/
├── scripts/
├── integrations/
└── evals/
```

Each real skill directory will contain a `SKILL.md` plus only the supporting resources/scripts it needs. Large or changing data should remain shared/reference data rather than bloating skill instructions.

## 17. Implementation Sequence After Design Approval

1. Build definitive capability inventory from v3.2.2 and all approved vNext additions.
2. Build source registry and supersession map.
3. Create repo foundation and security exclusions.
4. Migrate legacy doctrine into shared references.
5. Build orchestrator and sub-skills incrementally.
6. Add Evochia company/brand/product-development overlays.
7. Migrate The Mart provider safely.
8. Add structured schemas and golden output templates.
9. Build legacy parity + new capability evals.
10. Integrate explicit API contracts/handoffs.
11. Package and validate private/company skill suite.

## 18. Deferred / Not Yet Locked

The following are intentionally deferred to focused follow-up decisions and are not blockers for this architecture review:

- final Evochia typography system
- consolidated current Evochia rate card
- final commercial terms policy
- final staffing policy
- future persistent supplier-price backend implementation
- future FnB Central integration transport
- wider supplier provider adapters beyond The Mart

These will be authored from existing evidence and then owner-approved; they are not expected as pre-existing source files.

## 19. Design Acceptance Criteria

This architecture is ready for implementation planning when the owner confirms that:

1. Legacy v3.2.2 capabilities are correctly represented and must remain.
2. The 12-skill suite has the right boundaries.
3. Evochia is an overlay/company intelligence layer without destroying generic F&B capability.
4. Creativity and web R&D remain first-class.
5. The Mart stays a local controlled provider with no browser profile committed.
6. Interactive Dining is the golden product-development pattern, not a hardcoded one-off product.
7. Client outputs follow Evochia samples/brand while internal data remains protected.
8. FnB Central is the persistent system and Chef AI is the intelligence/operator layer.
9. API/tool side effects remain explicit and confirmation-gated.
10. Typography and final business policies are intentionally resolved in later focused specs.
