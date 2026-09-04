from pathlib import Path

from scripts.operator_support.contract_paths import extract_contract_paths

ROOT = Path(__file__).resolve().parents[2]


def test_extracts_exact_repo_paths_without_rewriting():
    text = """
`skills/culinary-rnd/references/research_protocol.md`
`skills/kitchen-event-operations/references/event_lifecycle.md`
`skills/evochia-market-intelligence/references/intelligence_policy.yaml`
`references/operations/output_router_templates_v2_1.md`
"""
    assert extract_contract_paths(text) == (
        "references/operations/output_router_templates_v2_1.md",
        "skills/culinary-rnd/references/research_protocol.md",
        "skills/evochia-market-intelligence/references/intelligence_policy.yaml",
        "skills/kitchen-event-operations/references/event_lifecycle.md",
    )


def test_rejects_non_repository_tokens():
    text = "`https://x/a/b` `templates/*/x.md` `skills/<skill-id>/MODULE.md` `../secret/x` `/absolute/x` `plain-token`"
    assert extract_contract_paths(text) == ()


def test_real_bug_paths_are_present_in_current_contracts():
    cases = {
        "skills/culinary-rnd/SKILL.md": "skills/culinary-rnd/references/research_protocol.md",
        "skills/kitchen-event-operations/SKILL.md": "skills/kitchen-event-operations/references/event_lifecycle.md",
        "skills/evochia-market-intelligence/SKILL.md": "skills/evochia-market-intelligence/references/intelligence_policy.yaml",
    }
    for contract, expected in cases.items():
        refs = extract_contract_paths((ROOT / contract).read_text(encoding="utf-8"))
        assert expected in refs
