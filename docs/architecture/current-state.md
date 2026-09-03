# Chef AI Pro Business vNext — Current Implementation State

**Status:** canonical implementation/release reconciliation
**Scope:** describes what is true in the implemented repository today. The original design spec and implementation plan remain historical design/plan records; when their pre-implementation wording conflicts with the implemented state below, this document controls the current-state interpretation.

## Evaluation semantics

`STATIC_CONTRACT_EVALS` validate repository contracts, schemas, routing declarations, resource reachability, leakage/security invariants and package structure. They **do not execute model/tool calls**.

`LIVE_SURFACE_BEHAVIORAL_EVALS` are a separate final-release gate executed on the installed OpenAI surface. They validate real model routing, multi-skill behavior, selected legacy/E2E scenarios and tool-unavailable degradation. A green static harness is necessary but not sufficient for final release.

## Phase 13 criticality

Phase 13 was intentionally **parallel during early implementation** because typography and owner-approved commercial policy were not prerequisites for the initial skill skeletons. At the current release stage, Phase 13 commercial owner lock is **mandatory before final commercial release**.

## Typography approval state

Phase 13.1 visual/typography owner lock: `APPROVED`.

The Evochia visual/typography system is canonical as `evochia_visual_system_v1`, effective 2026-09-03. The approved system keeps artifact-specific typography, official/digital palettes, verified logo assets and the existing fail-closed render-integrity contract. Brand voice remains a separate authority/review decision and is not implicitly approved by this visual-system lock.

## Current implementation paths

The implemented Evochia company-policy bundle lives under:

`company/evochia/policies/`

Runtime templates/schemas are governed by `release/runtime_resource_ownership.yaml`, and legacy capability-to-resource reachability is governed by `evals/legacy/resource_reachability.yaml`. The implemented repository tree is authoritative for current paths; earlier directory sketches in planning documents are illustrative/historical.

## The Mart / Phase 8B

Phase 8A contracts/security are implemented. Phase 8B exact provider-source migration remains an **OPEN final-release blocker**.

The Phase 8B execution path is now explicitly assigned to **Codex**. Codex must migrate the exact audited source bytes for the allowlisted provider artifacts and original/normalized tests. It must not reconstruct or approximate the collector/extractor from memory.

Required Phase 8B outcomes remain:
- exact `themart_capture.py` migration;
- exact `themart_extract_existing_html.py` migration;
- exact `categories.json` migration;
- normalized original provider tests;
- repository safety fence preserved;
- `.browser_profile_themart`, cookies/session state, credentials, caches, venv and unsanitized output excluded.

## Release interpretation

Repository/static candidate readiness is not production readiness. Final release remains blocked until all required release gates in `release/release_readiness.yaml` are closed, including Phase 8B, Phase 13 commercial owner lock and live OpenAI-surface installation/behavioral validation.
