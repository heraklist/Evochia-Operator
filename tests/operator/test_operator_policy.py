from pathlib import Path
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "release/operator/package_policy.yaml"
EXPECTED_ICON_BLOB = "11676370669ef00c1ed6815300db240c5ce376f8"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def test_policy_references_canonical_authorities_not_a_domain_copy_list():
    data = yaml.safe_load(POLICY.read_text(encoding="utf-8"))

    assert data["schema_version"] == 1
    assert data["source_package_policy"] == "release/package_policy.yaml"
    assert data["operator_name"] == "evochia-operator"
    assert data["orchestrator_skill"] == "chef-ai-pro-business"
    assert data["template"] == "release/operator/SKILL.template.md"
    assert data["routing"] == "skills/chef-ai-pro-business/references/routing.yaml"
    assert data["module_index_path"] == "references/module_index.md"
    assert data["provenance_manifest_path"] == "provenance/build_manifest.yaml"
    assert "domain_skills" not in data


def test_policy_referenced_source_paths_exist():
    data = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    source_paths = (
        data["source_package_policy"],
        data["template"],
        data["routing"],
        data["icon"]["source_path"],
    )
    assert not [path for path in source_paths if not (ROOT / path).is_file()]


def test_icon_source_is_the_verified_git_blob():
    data = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    icon = data["icon"]

    assert icon["source_path"] == "company/evochia/brand/assets/logo-mark-42.png"
    assert icon["artifact_path"] == "assets/evochia-operator-icon.png"
    assert icon["expected_git_blob"] == EXPECTED_ICON_BLOB
    assert git("rev-parse", f"HEAD:{icon['source_path']}") == EXPECTED_ICON_BLOB
