#!/usr/bin/env python3
"""Validate the repository as a private Chef AI Pro Business skill-package candidate."""
from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path
import re
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "release/package_policy.yaml"
OWNERSHIP_PATH = ROOT / "release/runtime_resource_ownership.yaml"
GENERATED_CACHE_PARTS = {"__pycache__", ".pytest_cache"}


def _frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    return yaml.safe_load(text[4:end]) or {}


def _path_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for token in re.findall(r"`([^`]+)`", text):
        token = token.strip()
        if "/" not in token:
            continue
        if token.startswith(("http://", "https://")):
            continue
        if any(ch in token for ch in "*{}<>|"):
            continue
        if " " in token:
            continue
        refs.add(token.rstrip(".,;:"))
    return refs


def _is_forbidden(rel: Path, patterns: list[str], exceptions: set[str]) -> bool:
    posix = rel.as_posix()
    if posix in exceptions or rel.name in exceptions:
        return False
    for pattern in patterns:
        if pattern.startswith("*."):
            if fnmatch.fnmatch(rel.name, pattern):
                return True
        elif pattern in rel.parts or rel.name == pattern:
            return True
    return False


def _candidate_files(root: Path):
    """Yield files that can actually be part of the package candidate.

    In a Git working tree, tracked files are the source of truth. In a materialized
    non-Git package, scan the filesystem but ignore test/runtime cache directories.
    """
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            for raw in result.stdout.split(b"\0"):
                if not raw:
                    continue
                rel = Path(raw.decode("utf-8"))
                path = root / rel
                if path.is_file():
                    yield path
            return

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if ".git" in rel.parts or GENERATED_CACHE_PARTS & set(rel.parts):
            continue
        yield path


def validate_runtime_resource_ownership(root: Path | str, data: dict) -> list[str]:
    root = Path(root).resolve()
    issues: list[str] = []
    seen_paths: set[str] = set()

    for section, expect_dir in (("resource_roots", True), ("exact_resources", False)):
        for item in data.get(section, []):
            path = item.get("path")
            owner = item.get("owner_skill")
            token = item.get("reference_token")
            label = path or f"{section}:<missing-path>"
            if not path or not owner or not token:
                issues.append(f"runtime resource {label}: incomplete ownership declaration")
                continue
            if path in seen_paths:
                issues.append(f"runtime resource {path}: duplicate ownership declaration")
            seen_paths.add(path)

            resource = root / path
            if not resource.exists():
                issues.append(f"runtime resource missing: {path}")
                continue
            if expect_dir and not resource.is_dir():
                issues.append(f"runtime resource root is not a directory: {path}")
            if not expect_dir and not resource.is_file():
                issues.append(f"runtime resource is not a file: {path}")

            skill_file = root / "skills" / owner / "SKILL.md"
            if not skill_file.exists():
                issues.append(f"resource owner {owner}: missing SKILL.md for {path}")
                continue
            skill_text = skill_file.read_text(encoding="utf-8")
            if token not in skill_text:
                issues.append(f"resource owner {owner}: {path} is not reachable via token {token}")

    for path in data.get("non_runtime_tooling", []):
        if not (root / path).exists():
            issues.append(f"non-runtime tooling resource missing: {path}")

    return issues


def validate(root: Path | str = ROOT) -> list[str]:
    root = Path(root).resolve()
    issues: list[str] = []
    policy_path = root / "release/package_policy.yaml"
    if not policy_path.exists():
        return ["missing release/package_policy.yaml"]
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}

    skills_dir = root / "skills"
    for skill_name in policy.get("required_skills", []):
        skill_dir = skills_dir / skill_name
        skill_file = skill_dir / policy.get("required_skill_file", "SKILL.md")
        if not skill_file.exists():
            issues.append(f"missing skill file: {skill_file.relative_to(root)}")
            continue
        text = skill_file.read_text(encoding="utf-8")
        meta = _frontmatter(text)
        for field in policy.get("required_frontmatter_fields", []):
            if not meta.get(field):
                issues.append(f"{skill_name}: missing frontmatter {field}")
        if meta.get("name") != skill_name:
            issues.append(f"{skill_name}: frontmatter name mismatch")

        for ref in _path_refs(text):
            candidates = [root / ref, skill_dir / ref]
            if not any(path.exists() for path in candidates):
                issues.append(f"{skill_name}: broken referenced path {ref}")

    ownership_path = root / "release/runtime_resource_ownership.yaml"
    if not ownership_path.exists():
        issues.append("missing release/runtime_resource_ownership.yaml")
    else:
        ownership = yaml.safe_load(ownership_path.read_text(encoding="utf-8")) or {}
        issues.extend(validate_runtime_resource_ownership(root, ownership))

    patterns = policy.get("forbidden_patterns", [])
    exceptions = set(policy.get("allowed_exception_files", []))
    candidate_files = list(_candidate_files(root))
    total_bytes = 0
    for path in candidate_files:
        rel = path.relative_to(root)
        if _is_forbidden(rel, patterns, exceptions):
            issues.append(f"forbidden package file: {rel.as_posix()}")
        try:
            total_bytes += path.stat().st_size
        except OSError:
            issues.append(f"cannot stat package file: {rel.as_posix()}")

    limit = int(policy.get("max_repository_candidate_bytes", 0) or 0)
    if limit and total_bytes > limit:
        issues.append(f"package candidate size {total_bytes} exceeds {limit}")

    registry = root / "references/source_registry.yaml"
    if not registry.exists():
        issues.append("missing references/source_registry.yaml")
    else:
        data = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
        ids = [item.get("source_id") for item in data.get("sources", [])]
        if not ids or len(ids) != len(set(ids)):
            issues.append("source registry ids missing or duplicated")

    if policy.get("font_binaries_in_package") is False:
        for path in candidate_files:
            if path.suffix.lower() in {".ttf", ".otf", ".woff", ".woff2"}:
                issues.append(f"font binary in package: {path.relative_to(root).as_posix()}")

    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", nargs="?", default=str(ROOT))
    args = parser.parse_args(argv)
    issues = validate(args.repo_root)
    if issues:
        print("Skill package validation: FAIL", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("Skill package validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
