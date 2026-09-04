from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import yaml


@dataclass(frozen=True)
class ModuleDescriptor:
    name: str
    description: str


def parse_frontmatter(data: bytes) -> dict[str, str]:
    """Parse required Skill frontmatter from canonical UTF-8 bytes.

    The operator index is a generated projection of canonical source values.
    Missing fences, malformed YAML, empty values, or non-string name/description
    fields fail closed rather than producing a partial capability index.
    """
    text = data.decode("utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter fence")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("missing closing frontmatter fence")

    loaded = yaml.safe_load(text[4:end]) or {}
    if not isinstance(loaded, dict):
        raise ValueError("frontmatter must be a mapping")

    result: dict[str, str] = {}
    for field in ("name", "description"):
        value = loaded.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"frontmatter {field} must be a non-empty string")
        result[field] = value
    return result


def render_module_index(modules: Iterable[ModuleDescriptor]) -> bytes:
    """Render a deterministic capability index without paraphrasing descriptions."""
    ordered = sorted(modules, key=lambda item: item.name)
    names = [item.name for item in ordered]
    if len(names) != len(set(names)):
        raise ValueError("duplicate module name")

    lines = [
        "<!-- GENERATED — DO NOT EDIT -->",
        "# Internal Capability Index",
        "",
    ]
    for index, module in enumerate(ordered):
        if not module.name.strip() or not module.description.strip():
            raise ValueError("module name and description must be non-empty")
        lines.append(f"- `{module.name}`")
        lines.append(f"  {module.description}")
        if index != len(ordered) - 1:
            lines.append("")
    return ("\n".join(lines) + "\n").encode("utf-8")
