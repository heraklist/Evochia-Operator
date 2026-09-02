# Security Policy

Chef AI Pro Business is a private/company repository and may contain company-confidential doctrine, operating rules, commercial structures, and controlled integrations.

## Do not disclose sensitive material publicly

Do not open a public issue containing any of the following:

- API keys, credentials, tokens, cookies, or authenticated browser/session state;
- client-identifying or client-confidential information;
- private Evochia commercial data, supplier data, or internal operating documents;
- vulnerabilities that could expose private company or client information.

## Private reporting path

Report security concerns privately to the repository owner through the owner's approved private channel. **Owner action required before broader distribution:** replace this sentence with the final private security contact/process once selected.

If credentials or authenticated browser state are accidentally committed, treat them as compromised: revoke/rotate them first, then remove the material from repository history using an appropriate secure remediation process.

## Repository security gate

`scripts/validate_repo_hygiene.py` is a mandatory pre-commit/release check. It is defense in depth and does not replace secret scanning or credential rotation after exposure.
