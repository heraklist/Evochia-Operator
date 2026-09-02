from __future__ import annotations

from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[2]

SKILLS = {
    "chef-ai-pro-business",
    "culinary-rnd",
    "recipe-engineering",
    "menu-experience-design",
    "kitchen-event-operations",
    "food-safety-allergens",
    "costing-commercial-intelligence",
    "supplier-procurement-intelligence",
    "evochia-company-operations",
    "evochia-brand-documents",
    "evochia-product-development",
    "evochia-market-intelligence",
}

REQUIRED_HEADINGS = {
    "## Purpose", "## When to Use", "## Authority and Resources", "## Responsibilities",
    "## Output Contract", "## Guardrails", "## Handoffs", "## Non-Goals",
}


def parse_frontmatter(text: str) -> dict:
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    end = text.find("\n---\n", 4)
    assert end != -1, "SKILL.md frontmatter must close with ---"
    return yaml.safe_load(text[4:end])


def test_exact_skill_suite_exists():
    skill_root = ROOT / "skills"
    found = {p.name for p in skill_root.iterdir() if p.is_dir()}
    assert found == SKILLS
    for name in SKILLS:
        assert (skill_root / name / "SKILL.md").is_file()


def test_skill_frontmatter_is_discovery_safe():
    for name in SKILLS:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        assert frontmatter["name"] == name
        description = frontmatter["description"]
        assert description.startswith("Use when ")
        assert len(description) <= 500
        assert re.fullmatch(r"[a-z0-9-]+", frontmatter["name"])
        assert "→" not in description
        assert "step 1" not in description.lower()


def test_every_skill_declares_contract_sections():
    for name in SKILLS:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        headings = set(re.findall(r"^## .+$", text, flags=re.MULTILINE))
        missing = REQUIRED_HEADINGS - headings
        assert not missing, f"{name}: missing {sorted(missing)}"


def test_orchestrator_is_not_a_monolith():
    text = (ROOT / "skills/chef-ai-pro-business/SKILL.md").read_text(encoding="utf-8")
    assert len(text.split()) < 1100
    assert "smallest sufficient" in text.lower()
    assert "INTERNAL" in text and "OPERATIONS" in text and "CLIENT-SAFE" in text
    assert "references/source_registry.yaml" in text
    for sibling in SKILLS - {"chef-ai-pro-business"}:
        assert sibling in text


def test_domain_skills_reference_shared_doctrine_instead_of_copying_it():
    expectations = {
        "culinary-rnd": "references/culinary/flavor_pairing_substitution_v2_1.md",
        "recipe-engineering": "references/operations/professional_kitchen_workflows_v2_2.md",
        "menu-experience-design": "references/culinary/owner_style_storytelling_v2_1.md",
        "kitchen-event-operations": "references/operations/professional_kitchen_workflows_v2_2.md",
        "food-safety-allergens": "references/safety/food_safety_allergens_v2_5.md",
        "costing-commercial-intelligence": "references/costing/costing_formula_engine_v2_2.md",
        "supplier-procurement-intelligence": "references/yields/supplier_yield_workflow_v3_2_2.md",
    }
    for skill, reference in expectations.items():
        text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert reference in text
