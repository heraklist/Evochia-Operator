from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "release/operator/SKILL.template.md"


def frontmatter(text: str) -> dict:
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4:end]) or {}


def test_operator_template_is_router_not_policy_monolith():
    text = TEMPLATE.read_text(encoding="utf-8")
    meta = frontmatter(text)
    assert meta["name"] == "evochia-operator"
    assert meta["description"]
    assert "smallest sufficient" in text.lower()
    assert "skills/<skill-id>/MODULE.md" in text
    assert "skills/chef-ai-pro-business/references/routing.yaml" in text
    assert "references/module_index.md" in text
    assert "references/source_registry.yaml" in text
    assert "food-safety-allergens" in text
    assert all(token in text for token in ("INTERNAL", "OPERATIONS", "CLIENT-SAFE"))
    assert "DRAFT_OR_HANDOFF_NO_FAKE_EXECUTION" in text
    assert "FnB Central" in text
    assert "system of record" in text.lower()
    assert "routing transcript" in text.lower()


def test_operator_template_does_not_duplicate_rate_policy():
    text = TEMPLATE.read_text(encoding="utf-8")
    forbidden = ["15+", "6–14", "0–5", "+20%", "+40%", "6500", "6,500"]
    assert not [token for token in forbidden if token in text]
