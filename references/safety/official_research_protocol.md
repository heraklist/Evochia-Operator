# Official Food-Safety Research Protocol

## Purpose
This protocol controls **on-demand** food-safety research. It exists to make current legal, regulatory and scientific claims auditable without turning the skill into a background monitoring service.

**Do not use background monitoring.** Research is triggered by the user's task or by a material safety/freshness dependency. **Do not silently modify canonical doctrine** after research; a discovered conflict is surfaced for review.

## When live official research is mandatory
Research current official sources before giving a definitive answer when the task depends on:

- a current legal or sanitary requirement in Greece or the EU;
- an exact professional temperature/time requirement, cold-chain rule or holding requirement;
- a current microbiological criterion, sampling plan or process-hygiene criterion;
- an allergen labelling/information obligation or a change to the regulated allergen framework;
- whether HACCP, GHP, PRP, OPRP, CCP or documented self-control is required or how official guidance currently frames it;
- traceability, withdrawal, recall, official controls, registration/approval or competent-authority obligations;
- a current EFET/Ministry circular, inspection guide or sector-specific hygiene guide;
- a high-risk process where current scientific evidence materially changes the recommendation.

For stable classical cooking technique with no current compliance dependency, official research is optional.

## Source order by jurisdiction
For **Greece**, check applicable Greek sources first (Ministry of Health, EFET and other competent official authorities as relevant), then EUR-Lex / European Commission for directly applicable EU law and guidance. For scientific risk assessment use EFSA. Use Codex/FAO/WHO as international methodology or public-health reference where useful.

For **EU-wide** claims, EUR-Lex binding law outranks Commission guidance; EFSA supplies scientific evidence, not binding risk-management rules.

## Evidence capture
Every current claim should be representable with:

- `claim`
- `classification`: `current regulatory requirement`, `official guidance`, `scientific evidence`, or `operational best practice`
- `jurisdiction`
- `source_id`
- `authority_type`
- canonical source URL
- `retrieved_at`
- current consolidated `version` or effective date when available
- verification status

Before relying on a regulation, open the **current consolidated** version (or the current official legal act if consolidation is unavailable) and check whether later amendments, derogations or sector-specific rules matter.

## Conflict handling
1. Binding applicable law controls over guidance.
2. Greek national requirements can add context or requirements where EU law permits national measures; do not infer conflicts without checking scope.
3. Commission/EFET guidance explains implementation but is not labelled as statute unless it is actually binding law.
4. EFSA/Codex/WHO may strengthen technical reasoning but cannot silently override applicable law.
5. If two official sources appear inconsistent, state the conflict and classify the answer `NEEDS_REVIEW` until scope/date/applicability is resolved.

## Freshness failure rule
If current law, guidance, version, applicability or jurisdiction cannot be verified, do **not** provide a definitive legal limit from memory. Give the operationally conservative recommendation, label it `operational best practice` or `NEEDS_REVIEW`, and state what official verification is missing.
