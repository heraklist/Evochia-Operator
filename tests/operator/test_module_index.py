from pathlib import Path

import pytest
import yaml

from scripts.operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index

ROOT = Path(__file__).resolve().parents[2]


def test_frontmatter_requires_name_and_description():
    raw = b"---\nname: recipe-engineering\ndescription: Exact description.\n---\n# Body\n"
    assert parse_frontmatter(raw) == {
        "name": "recipe-engineering",
        "description": "Exact description.",
    }


@pytest.mark.parametrize(
    "raw, message",
    [
        (b"# no frontmatter\n", "opening"),
        (b"---\nname: x\n", "closing"),
        (b"---\nname: x\ndescription: ''\n---\n", "description"),
        (b"---\nname: 123\ndescription: x\n---\n", "name"),
    ],
)
def test_frontmatter_fails_closed(raw, message):
    with pytest.raises(ValueError, match=message):
        parse_frontmatter(raw)


def test_render_is_sorted_and_does_not_paraphrase():
    raw = render_module_index(
        [
            ModuleDescriptor("recipe-engineering", "Exact recipe description."),
            ModuleDescriptor("culinary-rnd", "Exact culinary description."),
        ]
    )
    assert raw == (
        "<!-- GENERATED — DO NOT EDIT -->\n"
        "# Internal Capability Index\n\n"
        "- `culinary-rnd`\n"
        "  Exact culinary description.\n\n"
        "- `recipe-engineering`\n"
        "  Exact recipe description.\n"
    ).encode("utf-8")


def test_duplicate_module_names_fail_closed():
    with pytest.raises(ValueError, match="duplicate module name"):
        render_module_index(
            [
                ModuleDescriptor("same", "A"),
                ModuleDescriptor("same", "B"),
            ]
        )


def test_real_domain_skills_parse_and_render_exact_frontmatter_values():
    policy = yaml.safe_load((ROOT / "release/package_policy.yaml").read_text(encoding="utf-8"))
    domain_ids = [skill for skill in policy["required_skills"] if skill != "chef-ai-pro-business"]
    assert len(domain_ids) == 11

    descriptors = []
    source = {}
    for skill_id in domain_ids:
        meta = parse_frontmatter((ROOT / f"skills/{skill_id}/SKILL.md").read_bytes())
        assert meta["name"] == skill_id
        source[skill_id] = meta["description"]
        descriptors.append(ModuleDescriptor(meta["name"], meta["description"]))

    rendered = render_module_index(descriptors).decode("utf-8")
    for skill_id, description in source.items():
        assert f"- `{skill_id}`\n  {description}" in rendered
