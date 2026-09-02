# Chef AI Pro Business

Chef AI Pro Business vNext is the private/company skill-suite source repository for a modular F&B Operating Copilot. It preserves the approved Chef AI Pro Business v3.2.2 behavior while evolving it into an orchestrated set of focused skills for culinary R&D, professional recipes, menus, event operations, costing, procurement, Evochia company policy, branded documents, product development, and market intelligence.

## Repository role

- **Canonical skill-suite repository:** `heraklist/chef_ai_pro_business`
- **Separate execution backend:** `heraklist/chef-ai-pro-business-api`
- **Persistent F&B operating system:** FnB Central remains a separate product/system of record.
- **Current version:** see [`VERSION`](VERSION). `4.0.0-alpha.0` denotes the vNext architecture generation and does **not** claim production readiness.

## Security boundary

This repository must never contain API keys, credentials, `.env` secrets, authenticated browser profiles, cookies/session databases, local virtual environments, generated local output, or other machine/session state. The Mart authentication remains local-only and is not part of the distributable skill suite.

Run the repository hygiene gate before committing:

```bash
python scripts/validate_repo_hygiene.py .
python -m pytest tests/repo/test_repo_hygiene.py -q
```

## Implementation status

The approved architecture and implementation plan live under `docs/superpowers/`. Implementation proceeds in small verified phases. Legacy parity is a release requirement: a successful install alone is not sufficient.
