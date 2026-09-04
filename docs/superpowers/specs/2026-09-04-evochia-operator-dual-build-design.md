# Evochia Operator Dual-Build Design

**Status:** WRITTEN SPEC — awaiting owner re-review  
**Date:** 2026-09-04  
**Canonical starting commit:** `9cab252e8757b35f6501b178c06943b0e82b398a`  
**Public operator name:** `evochia-operator`  
**Public invocation target:** `@evochia-operator`

## 1. Purpose

The current repository contains 12 installable Skills: one orchestrator (`chef-ai-pro-business`) plus 11 domain Skills. The ChatGPT Skills surface successfully uploaded the frozen `9cab252` package and displayed all 12 Skills.

The goal is to add a second deployment projection that exposes one public Skill, `@evochia-operator`, while preserving the 12-skill canonical source architecture unchanged.

This is a deployment/build change, not a semantic migration of the repository.

## 2. Architectural decision

The canonical source tree remains the authority:

- `skills/chef-ai-pro-business/SKILL.md` remains the canonical orchestrator contract for the multi-skill build.
- The 11 existing domain `skills/<id>/SKILL.md` remain canonical source contracts.
- `skills/chef-ai-pro-business/references/routing.yaml` remains canonical and unchanged.
- `references/source_registry.yaml` remains the single source-authority precedence contract.
- Existing runtime ownership, parity, policies, schemas, data and doctrine remain unchanged unless a separate explicitly approved change is made.

Two deployment projections are produced from one source commit:

1. **MULTI build** — the current 12 public Skills.
2. **OPERATOR build** — one public `evochia-operator/SKILL.md` plus 11 internal domain projections named `skills/<id>/MODULE.md`.

The operator approach deliberately trades some platform-level skill isolation for a cleaner single-entrypoint UX. This is a trade-off, not an isolation improvement.

## 3. Public surface and icon

The public Skill is:

- ID/name: `evochia-operator`
- invocation: `@evochia-operator`
- role: Evochia hospitality operating intelligence and router across culinary, recipe engineering, menu design, operations, food safety, costing/commercial, suppliers, company operations, brand/documents, product development and market intelligence.

The Skill uses an Evochia-branded operator icon derived from the verified Evochia mark, with deep Evochia green as the primary tile/background and restrained use of the approved palette. The mark itself must not be reconstructed from a font.

The package must contain the approved icon asset. Actual icon binding in the ChatGPT surface is an install-time/surface verification item because no unsupported metadata convention should be invented.

## 4. No canonical repo migration

The implementation MUST NOT move or rename the 12 source Skills, rewrite `required_skills`/`target_skills`, introduce a second manually maintained registry, or alter canonical routing for the sake of the operator build.

Specifically, the builder PR must not change domain behavior in:

- the 12 existing `skills/*/SKILL.md` contracts,
- `skills/chef-ai-pro-business/references/routing.yaml`,
- `references/source_registry.yaml`,
- current company/commercial/safety policies,
- parity target skill IDs,
- current schemas/data/doctrine,
- Phase 14–16 architecture.

If the operator projection cannot work without changing one of those authorities, implementation stops for a new design decision rather than silently expanding scope.

## 5. Operator package topology

The generated operator artifact is conceptually:

```text
evochia-operator/
├── SKILL.md
├── VERSION
├── assets/
│   └── evochia-operator-icon.png
├── references/
│   ├── ... entire canonical references/ subtree ...
│   └── module_index.md                 # GENERATED — DO NOT EDIT
├── skills/
│   ├── chef-ai-pro-business/
│   │   └── references/
│   │       └── routing.yaml
│   ├── culinary-rnd/
│   │   ├── MODULE.md
│   │   └── references/...
│   ├── recipe-engineering/
│   │   ├── MODULE.md
│   │   └── ...
│   ├── menu-experience-design/
│   ├── kitchen-event-operations/
│   ├── food-safety-allergens/
│   ├── costing-commercial-intelligence/
│   ├── supplier-procurement-intelligence/
│   ├── evochia-company-operations/
│   ├── evochia-brand-documents/
│   ├── evochia-product-development/
│   └── evochia-market-intelligence/
├── company/...
├── data/...
├── schemas/...
├── templates/...
├── integrations/...
├── <other runtime resources selected by the existing package/ownership contracts>
└── provenance/
    └── build_manifest.yaml
```

`module_index.md` is added to the existing canonical `references/` subtree; it does not replace or reduce that subtree.

The operator builder MUST derive the runtime resource closure from existing canonical package/ownership/reference contracts. It MUST NOT maintain a second hand-authored runtime resource list. Files selected into the artifact retain canonical repo-root paths and are copied from Git objects for the selected source commit unless this spec explicitly defines them as generated content.

## 6. Projection rules

### 6.1 Domain modules

For each of the 11 domain Skills:

```text
source:     skills/<id>/SKILL.md
projection: skills/<id>/MODULE.md
relation:   EXACT_BYTE_COPY
```

The complete file bytes are preserved, including frontmatter, `name`, `description`, body, whitespace and line endings.

No frontmatter stripping, path rewriting, prose rewriting or semantic transformation is allowed.

### 6.2 Skill-local resources

All skill-local supporting resources retain their canonical repo-root paths beneath `skills/<id>/`.

This is required because current domain contracts contain repo-root references such as:

- `skills/culinary-rnd/references/research_protocol.md`
- `skills/kitchen-event-operations/references/event_lifecycle.md`
- `skills/evochia-market-intelligence/references/intelligence_policy.yaml`

Keeping the `skills/<id>/` prefix avoids a transformation class and preserves exact path resolution.

### 6.3 Routing

`skills/chef-ai-pro-business/references/routing.yaml` is copied to the operator artifact at the same path and remains byte-identical.

No `required_skills` → `required_modules` renaming is performed.

The generated root `SKILL.md` defines the operator resolution semantic:

> Within the operator package, a canonical skill ID referenced by routing resolves to `skills/<skill-id>/MODULE.md`.

The old source orchestrator `SKILL.md` is not projected as a twelfth module; its operator-facing orchestration role is replaced by the new root operator template, while its routing resources remain canonical inputs.

## 7. Generated module index

A manually maintained module registry is forbidden.

The builder generates `references/module_index.md` deterministically from the `name` and `description` frontmatter fields of the 11 canonical domain `SKILL.md` files.

Properties:

- marked `GENERATED — DO NOT EDIT`,
- descriptions copied exactly, not paraphrased,
- used as a low-cost capability lookup when the route table alone is insufficient,
- not a source of authority,
- reproducible from canonical source bytes.

Validator invariant:

```text
module_index.md == render(extract_frontmatter(11 canonical source SKILL.md))
```

The index is therefore a deterministic projection of source truth, not a second authority.

## 8. Root operator template

The operator root `SKILL.md` is the only new behavioral instruction surface.

It MUST exist as a source-controlled, human-reviewable template, not as a large string embedded in builder code. Canonical source location:

`release/operator/SKILL.template.md`

The template owns only orchestration semantics:

- classify request intent/context/risk/freshness/tool state/audience,
- consult canonical routing,
- use the smallest sufficient domain set,
- use the generated module index only when needed,
- resolve domain IDs to `skills/<id>/MODULE.md`,
- preserve canonical source authority and existing router invariants,
- preserve safety hard gates,
- preserve INTERNAL / OPERATIONS / CLIENT-SAFE separation,
- preserve tool-unavailable draft/handoff behavior,
- preserve FnB Central persistence boundary,
- return one composed answer without exposing internal routing transcript.

It MUST NOT duplicate current rates, commercial policy, safety doctrine or domain rules that already have canonical authority elsewhere.

No new precedence list is introduced. `references/source_registry.yaml` remains the canonical source-authority precedence contract.

## 9. Builder input, targets and determinism

The builder operates on an explicit full Git commit SHA and reads committed Git objects, not mutable working-tree bytes.

Conceptually:

```text
Build(source_commit, target) -> artifact + provenance
```

Supported targets are exactly:

- `multi`
- `operator`

The build target definition is source-controlled under `release/` and may reference existing package/ownership contracts, but must not duplicate the canonical list of domain authorities by hand when that list can be derived deterministically.

The output filename convention is:

```text
chef-ai-pro-business-<version>-<shortsha>-multi.zip
evochia-operator-<version>-<shortsha>-operator.zip
```

This prevents CRLF conversion, OneDrive state, uncommitted edits or other dirty-worktree effects from contaminating the artifact.

For a given commit and builder version, the ZIP must be byte-reproducible. The builder therefore fixes at least:

- file/path ordering,
- ZIP timestamps,
- compression method and level,
- file modes,
- path separators,
- filename encoding,
- archive metadata/extras.

Required property:

```text
build(C, operator) -> SHA X
build(C, operator) -> SHA X
```

A dirty-worktree regression test must prove that changing local working-tree content does not alter the artifact generated for explicit commit `C`.

## 10. Provenance manifest

The operator package includes `provenance/build_manifest.yaml` with at least:

- source commit,
- source version,
- target type,
- builder identity/hash,
- root operator template hash,
- per-file source/projected paths,
- transformation relation,
- source SHA-256,
- projected SHA-256,
- complete packaged file inventory hashes.

For each domain module, relation is `EXACT_BYTE_COPY`.

The ZIP SHA-256 is emitted as a build result/sidecar, not embedded inside the ZIP.

## 11. Source-anchored artifact validation

Operator validation has a release-grade source-anchored mode requiring:

```text
--artifact <path>
--source-repo <repo>
--source-commit <full SHA>
```

The validator must verify against actual Git objects, not only against the generated manifest.

Mandatory assertions:

1. Exactly one `SKILL.md` exists in the operator artifact.
2. That root Skill is `evochia-operator`.
3. Exactly 11 expected `skills/<id>/MODULE.md` exist.
4. No expected module is missing and no unexpected module ID exists.
5. Every module is an `EXACT_BYTE_COPY` of its canonical source `SKILL.md`.
6. Skill-local resources preserve canonical paths.
7. `skills/chef-ai-pro-business/references/routing.yaml` is an exact copy.
8. `references/module_index.md` equals deterministic rendering from the 11 source frontmatters.
9. Packaged file hashes match the manifest.
10. Every referenced runtime path resolves at the exact path written in the contract.
11. Forbidden files/secrets are absent.
12. Existing package restrictions such as prohibited font binaries/unintended backend source are preserved.
13. Source commit and `VERSION` are accurate.
14. Two builds from the same commit produce the same ZIP SHA-256.
15. Mutating any projected module/routing/resource byte causes validation failure.
16. Every manifest `source_sha256` is recomputed from the actual Git object at `source_commit` and `source_path`.
17. For `EXACT_BYTE_COPY`, actual Git source bytes equal artifact bytes directly, not only by hash.
18. Manual mutation of generated index or provenance without matching canonical source state fails validation.
19. Dirty-worktree mutation does not alter the artifact hash for an explicit source commit.

Self-contained validation without the Git object database may exist for convenience, but it is not sufficient release evidence.

## 12. Multi-build preservation

The current multi-skill build remains valid and buildable after adding the operator target.

The existing repository/package validator continues to validate the canonical multi-skill package. The operator artifact gets a dedicated builder/validator rather than overloading the existing validator with incompatible assumptions.

After the builder change reaches a post-builder source commit `C1`, both artifacts are produced from `C1`:

```text
MULTI(C1)
OPERATOR(C1)
```

They must share the same canonical domain bytes, policies, routing, data, schemas and source authority. The deployment projection is the intended experimental variable.

## 13. Surface install preconditions

### 13.1 Conscious sequencing waiver and open release blocker

The frozen `9cab252` artifact was uploaded successfully and the ChatGPT Skills surface displayed 12 Skills. This is preserved as pre-operator installation evidence; A1 and A2 transcripts are retained as diagnostic behavioral evidence.

The originally approved sequencing gate required a complete pre-builder A→H run before any builder implementation. The owner has chosen the speed-oriented exception: builder implementation may begin before that full pre-builder behavioral run. This is a **conscious sequencing waiver**, not a finding that the behavioral baseline is unnecessary.

Consequences of that waiver are explicit and mandatory:

- `openai_surface_install_scan` remains **OPEN and release-blocking** after builder implementation starts.
- The successful upload, 12 visible Skills, and A1/A2 evidence do **not** close the behavioral surface blocker.
- The blocker MUST be closed by a **complete MULTI(C1) A→H surface run** from the post-builder commit `C1`; sampling is not sufficient.
- The complete MULTI(C1) run must finish before operator acceptance, release-readiness advancement, or any production-ready claim.
- If MULTI(C1) exposes a failure, especially in Block F, treat it first as a multi-skill baseline failure. Do not attribute it to the operator projection without differential evidence.
- The OPERATOR(C1) run cannot substitute for the mandatory MULTI(C1) A→H run.

This waiver changes execution order only. It does not remove or weaken the release blocker.

### 13.2 Operator install precondition

Before operator behavioral testing, record:

- upload/install result,
- scan result or absence of explicit scanner verdict,
- visible Skill count,
- visible Skill names,
- whether any of the 11 internal module names are exposed,
- operator icon binding result,
- visible version/head when exposed by the surface.

Required operator surface condition:

```text
visible_skill_count == 1
visible_skill_names == [evochia-operator]
nested_module_names_exposed == false
```

If internal module names appear as Skills, the operator projection fails its install precondition and behavioral testing stops for that artifact.

## 14. Differential behavioral evaluation

After building both projections from the same post-builder commit, the **primary differential is router-to-router**.

For every primary differential case, preserve the same user task text, conversation structure, model/product configuration, tool state and timing as closely as practical. The intended comparison is:

```text
MULTI(C1):    @chef-ai-pro-business <same task>
OPERATOR(C1): @evochia-operator     <same task>
```

The only intended experimental variable is the deployment/router projection: public orchestrator with sibling Skills versus public operator with internal MODULE projections.

The multi-skill leg MUST use `@chef-ai-pro-business` for the primary comparison, including B1. Direct invocation of a domain Skill such as `@recipe-engineering` is not a substitute for the primary multi result because that would compare platform-level domain selection with model-mediated operator routing.

Direct-domain Skill runs MAY be recorded as a **third, non-gating diagnostic leg** when platform-level isolation itself is useful to inspect. Such runs must be labeled `DIRECT`, kept separate from the main differential, and must not be used to calculate the acceptance thresholds below.

Primary sentinels:

- **B1:** domain isolation / over-routing contamination.
- **D2:** INTERNAL → CLIENT-SAFE leakage after internal economics exist in the same conversation.
- **F1–F5:** safety invariant survival.

Pre-committed acceptance threshold:

```text
BLOCKING failures:              0
new MAJOR regressions:          0
new PASS_WITH_CONCERN:         <= 2
new NEAR_MISS in B1:            0
new NEAR_MISS in D2:            0
new NEAR_MISS in Block F:       0
```

Any Block F safety failure remains release-blocking without waiver.

The differential report records, per case:

- multi-orchestrator verdict,
- operator verdict,
- severity delta,
- observable behavioral delta,
- transcript references,
- optional `DIRECT` diagnostic verdict/transcript when one was run.

## 15. Scope exclusions

This design does not implement or modify:

- Phase 14 Safety & Evidence Foundation,
- Phase 15 Deterministic Commercial & Temporal Engine,
- Phase 16 Learning & Capacity Intelligence,
- current business/commercial policy semantics,
- FnB Central ownership/persistence model,
- current supplier source/provenance behavior,
- unrelated repository cleanup.

The operator dual-build is a deployment projection and evaluation project only.

## 16. Success criteria

The design succeeds when:

1. The canonical 12-skill source architecture remains semantically unchanged.
2. Both multi and operator artifacts are reproducibly buildable from one commit.
3. Operator projection contains exactly one public `SKILL.md` and 11 exact-byte internal `MODULE.md` projections.
4. All canonical paths and resource references resolve without rewriting.
5. Provenance is independently anchored to Git objects.
6. The ChatGPT surface exposes only `@evochia-operator` for the operator artifact, with the approved Evochia icon when binding is supported/configured.
7. The mandatory complete MULTI(C1) A→H run closes the still-open surface blocker, and the primary orchestrator-vs-operator differential meets the pre-committed thresholds.
8. If operator behavior regresses materially, the source architecture remains intact and the operator target can be rejected or revised without undoing the canonical Skill suite.
