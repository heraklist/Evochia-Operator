# Architecture Index

Chef AI Pro Business vNext is implemented from the approved design and implementation plan:

- `../superpowers/specs/2026-09-02-chef-ai-pro-business-vnext-design.md`
- `../superpowers/plans/2026-09-02-chef-ai-pro-business-vnext-implementation.md`

Core architectural boundaries:

1. one primary orchestrator plus focused sibling skills;
2. shared doctrine/resources are not duplicated across skill instructions;
3. source authority and supersession are explicit and machine-readable;
4. safety outranks creativity, commercial optimization, and presentation;
5. INTERNAL / OPERATIONS / CLIENT-SAFE outputs are distinct boundaries;
6. Chef AI is intelligence/orchestration, while FnB Central remains persistent structured operating state;
7. the separate `chef-ai-pro-business-api` backend remains an execution/integration layer;
8. authenticated browser profiles and credentials are local-only and never distributable assets.
