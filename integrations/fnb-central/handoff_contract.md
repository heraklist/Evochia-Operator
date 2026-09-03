# Chef AI ↔ FnB Central Handoff Contract

## Boundary

**FnB Central is the persistent F&B system of record.** Chef AI Pro Business is the intelligence, reasoning, creation and orchestration layer. The Skill Suite does not persist a parallel operational database and there is **no duplicate persistence** of FnB Central state inside the Skill repository.

The separate Chef AI API may transport or execute a handoff when configured, but its current mock/in-memory adapter state must not be mistaken for durable FnB Central persistence.

## Handoff object

A handoff is an explicit structured transfer of approved or review-ready data. It carries:

- `handoff_id`
- `entity_type`
- `entity_id` when one already exists
- `source_version`
- `target_system: FnB Central`
- `audience`
- `status`
- `payload`
- `assumptions`
- `source_refs`
- `requested_by`
- `idempotency_key` for a write/retry
- `created_at`

## Supported entity families

### Recipe handoff
May transfer canonical recipe data, recipe revision/draft data, yield, ingredient, allergen, production and costing hooks. Chef AI remains responsible for reasoning/creation; FnB Central owns durable recipe operational state after accepted persistence.

### Event handoff
May transfer an approved structured event brief, service requirements, menu links, staffing/equipment/procurement requirements and operational status. Chef AI does not become a persistent event database.

### Quote handoff
May transfer a quote draft, scenario, assumptions, commercial inputs and approval state. INTERNAL cost basis remains audience-controlled. A quote handoff is not equivalent to approval or client delivery unless explicitly confirmed by the relevant workflow.

### Supplier handoff
May transfer proposed or validated supplier evidence, SKU/pack/unit normalization, price snapshot provenance, confidence and review status. Extracted supplier data does not become approved master data merely because a handoff exists.

## Write semantics

A read may retrieve FnB Central/system-of-record context when the user requests or configures it. A write is always controlled:

1. Chef AI prepares the action summary and structured handoff.
2. The affected records and material assumptions are surfaced.
3. Explicit confirmation is obtained for a consequential external write.
4. The write uses an idempotency key where supported.
5. A retry may reuse the same idempotency identity; it must not create duplicate persistent records.
6. Success is claimed only from an actual target/backend response.

## Tool unavailable

If the target integration is unavailable, Chef AI may prepare a draft handoff payload or give the user a manual handoff path. It must not claim that FnB Central was updated. The Skill Suite does not persist the intended write as a substitute system of record.

## Ownership and conflict rule

When the same operational entity exists in both conversational context and FnB Central, FnB Central is authoritative for persistent current state unless the user explicitly supplies a newer approved change. Chef AI may propose a revision but does not silently overwrite persisted state.
