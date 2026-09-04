from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

import yaml

from scripts.operator_support.contract_paths import extract_contract_paths
from scripts.operator_support.git_source import GitSource, sha256_bytes
from scripts.operator_support.module_index import ModuleDescriptor, parse_frontmatter, render_module_index

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "scripts/build_skill_package.py"
VALIDATOR = ROOT / "scripts/validate_operator_package.py"
MANIFEST_PATH = "provenance/build_manifest.yaml"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def clone_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "source"
    subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(repo)],
        check=True,
        capture_output=True,
    )
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    return repo, git(repo, "rev-parse", "HEAD")


def operator_command(repo: Path, commit: str, output_dir: Path) -> subprocess.CompletedProcess[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--target",
            "operator",
            "--source-repo",
            str(repo),
            "--source-commit",
            commit,
            "--output-dir",
            str(output_dir),
        ],
        text=True,
        capture_output=True,
    )


def run_operator_builder(repo: Path, commit: str, output_dir: Path) -> Path:
    result = operator_command(repo, commit, output_dir)
    assert result.returncode == 0, result.stderr or result.stdout
    matches = list(output_dir.glob("evochia-operator-*-operator.zip"))
    assert len(matches) == 1
    return matches[0]


def archive_files(artifact: Path) -> dict[str, bytes]:
    with ZipFile(artifact) as archive:
        return {
            name: archive.read(name)
            for name in archive.namelist()
            if name and not name.endswith("/")
        }


def source_policy(source: GitSource) -> tuple[dict, dict, tuple[str, ...]]:
    package_policy = yaml.safe_load(source.read_bytes("release/package_policy.yaml"))
    operator_policy = yaml.safe_load(source.read_bytes("release/operator/package_policy.yaml"))
    domains = tuple(
        skill
        for skill in package_policy["required_skills"]
        if skill != operator_policy["orchestrator_skill"]
    )
    return package_policy, operator_policy, domains


def expected_index(source: GitSource, domains: tuple[str, ...]) -> bytes:
    descriptors = []
    for skill_id in domains:
        meta = parse_frontmatter(source.read_bytes(f"skills/{skill_id}/SKILL.md"))
        descriptors.append(ModuleDescriptor(meta["name"], meta["description"]))
    return render_module_index(descriptors)


def normalized_mode(mode: int) -> int:
    return 0o100755 if mode & 0o111 else 0o100644


def test_operator_projects_canonical_domains_references_index_and_verified_icon(tmp_path):
    repo, commit = clone_repo(tmp_path)
    source = GitSource(repo, commit)
    _, operator_policy, domains = source_policy(source)
    assert len(domains) == 11

    artifact = run_operator_builder(repo, commit, tmp_path / "out")
    version = source.read_bytes("VERSION").decode("utf-8").strip()
    assert artifact.name == f"evochia-operator-{version}-{commit[:7]}-operator.zip"

    files = archive_files(artifact)
    assert files["SKILL.md"] == source.read_bytes(operator_policy["template"])
    module_paths = sorted(path for path in files if path.startswith("skills/") and path.endswith("/MODULE.md"))
    assert module_paths == sorted(f"skills/{skill}/MODULE.md" for skill in domains)
    assert not [path for path in files if path.startswith("skills/") and path.endswith("/SKILL.md")]

    for skill_id in domains:
        assert files[f"skills/{skill_id}/MODULE.md"] == source.read_bytes(f"skills/{skill_id}/SKILL.md")
        for entry in source.entries(f"skills/{skill_id}/"):
            if entry.path.endswith("/SKILL.md"):
                continue
            assert files[entry.path] == source.read_bytes(entry.path)

    routing = operator_policy["routing"]
    assert files[routing] == source.read_bytes(routing)

    for entry in source.entries("references/"):
        assert files[entry.path] == source.read_bytes(entry.path)

    index_path = operator_policy["module_index_path"]
    assert files[index_path] == expected_index(source, domains)

    icon = operator_policy["icon"]
    assert icon["source_path"] not in files
    assert files[icon["artifact_path"]] == source.read_bytes(icon["source_path"])
    icon_entry = next(entry for entry in source.entries(icon["source_path"]) if entry.path == icon["source_path"])
    assert icon_entry.blob_sha == icon["expected_git_blob"]

    # Packaged brand evidence is documentation, not a repo-path authority. Its
    # recorded paths live inside an external owner-supplied ZIP and must not be
    # resolved as repository runtime paths.
    brand_readme = "company/evochia/brand/assets/README.md"
    assert files[brand_readme] == source.read_bytes(brand_readme)
    assert "EVOCHIA-LOGO/EVOCHIA/SVG/ORIGINAL.svg" not in files

    assert "scripts/build_skill_package.py" not in files
    assert not [path for path in files if path.startswith("tests/")]
    assert not [path for path in files if path.startswith("release/")]


def test_operator_closure_includes_owned_roots_exact_resources_and_preserves_git_modes(tmp_path):
    repo, commit = clone_repo(tmp_path)
    source = GitSource(repo, commit)
    _, operator_policy, _ = source_policy(source)
    ownership = yaml.safe_load(source.read_bytes("release/runtime_resource_ownership.yaml"))
    artifact = run_operator_builder(repo, commit, tmp_path / "out")
    files = archive_files(artifact)

    with ZipFile(artifact) as archive:
        source_entries = {entry.path: entry for entry in source.entries()}

        for item in ownership["resource_roots"]:
            root = item["path"].rstrip("/")
            entries = source.entries(root + "/")
            assert entries, root
            for entry in entries:
                assert files[entry.path] == source.read_bytes(entry.path)

        for item in ownership["exact_resources"]:
            path = item["path"].rstrip("/")
            assert files[path] == source.read_bytes(path)

        manifest = yaml.safe_load(files[MANIFEST_PATH])
        for row in manifest["files"]:
            source_path = row.get("source_path")
            projected_path = row["projected_path"]
            if not source_path or source_path not in source_entries:
                continue
            assert archive.getinfo(projected_path).external_attr >> 16 == normalized_mode(source_entries[source_path].mode)

    icon_source = operator_policy["icon"]["source_path"]
    contract_paths = ["SKILL.md"] + sorted(
        path for path in files if path.startswith("skills/") and path.endswith("/MODULE.md")
    )
    for path in contract_paths:
        text = files[path].decode("utf-8")
        for ref in extract_contract_paths(text):
            if ref == icon_source:
                continue
            if ref in files:
                continue
            prefix = ref.rstrip("/") + "/"
            assert any(name.startswith(prefix) for name in files), f"unresolved exact contract path: {ref}"


def test_operator_build_and_generated_index_ignore_dirty_skill_worktree_edit(tmp_path):
    repo, commit = clone_repo(tmp_path)
    clean = run_operator_builder(repo, commit, tmp_path / "clean")
    clean_files = archive_files(clean)

    skill = repo / "skills/recipe-engineering/SKILL.md"
    skill.write_bytes(skill.read_bytes() + b"\nDIRTY WORKTREE DESCRIPTION OVERRIDE\n")

    dirty = run_operator_builder(repo, commit, tmp_path / "dirty")
    dirty_files = archive_files(dirty)

    assert clean.read_bytes() == dirty.read_bytes()
    assert clean_files["references/module_index.md"] == dirty_files["references/module_index.md"]
    assert clean_files["skills/recipe-engineering/MODULE.md"] == dirty_files["skills/recipe-engineering/MODULE.md"]


def test_operator_manifest_is_source_anchored_sorted_and_hash_complete(tmp_path):
    repo, commit = clone_repo(tmp_path)
    source = GitSource(repo, commit)
    _, operator_policy, _ = source_policy(source)
    artifact = run_operator_builder(repo, commit, tmp_path / "out")
    files = archive_files(artifact)
    manifest = yaml.safe_load(files[MANIFEST_PATH])

    assert manifest["source_commit"] == commit
    assert manifest["source_version"] == source.read_bytes("VERSION").decode("utf-8").strip()
    assert manifest["target"] == "operator"
    assert manifest["root_template_sha256"] == sha256_bytes(source.read_bytes(operator_policy["template"]))
    assert manifest["module_index"]["sha256"] == sha256_bytes(files[operator_policy["module_index_path"]])

    builder_source = source.read_bytes("scripts/build_skill_package.py")
    assert manifest["builder"]["path"] == "scripts/build_skill_package.py"
    assert manifest["builder"]["source_commit_sha256"] == sha256_bytes(builder_source)
    assert manifest["builder"]["runtime_sha256"] == sha256(BUILDER.read_bytes()).hexdigest()

    rows = manifest["files"]
    assert [row["projected_path"] for row in rows] == sorted(row["projected_path"] for row in rows)
    assert {row["projected_path"] for row in rows} == set(files) - {MANIFEST_PATH}

    for row in rows:
        projected = files[row["projected_path"]]
        assert row["projected_sha256"] == sha256_bytes(projected)
        source_path = row.get("source_path")
        if source_path:
            source_bytes = source.read_bytes(source_path)
            assert row["source_sha256"] == sha256_bytes(source_bytes)
            if row["relation"] in {"EXACT_BYTE_COPY", "TEMPLATE_EXACT_COPY", "RENAMED_EXACT_BYTE_COPY"}:
                assert projected == source_bytes


def test_operator_closure_does_not_follow_backticked_paths_from_included_documentation(tmp_path):
    repo, _ = clone_repo(tmp_path)
    skill = repo / "skills/recipe-engineering/SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8") + "\nUse `company/operator-fixture/level1.md`.\n",
        encoding="utf-8",
    )
    level1 = repo / "company/operator-fixture/level1.md"
    level1.parent.mkdir(parents=True, exist_ok=True)
    level1.write_text("# Evidence\nRecorded external path `external-pack/level2.txt`.\n", encoding="utf-8")
    external = repo / "external-pack/level2.txt"
    external.parent.mkdir(parents=True, exist_ok=True)
    external.write_text("external evidence\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "add documentation authority fixture")
    commit = git(repo, "rev-parse", "HEAD")

    artifact = run_operator_builder(repo, commit, tmp_path / "out")
    files = archive_files(artifact)

    assert files["company/operator-fixture/level1.md"] == GitSource(repo, commit).read_bytes("company/operator-fixture/level1.md")
    assert "external-pack/level2.txt" not in files


def test_operator_build_fails_closed_when_backticked_runtime_path_is_missing(tmp_path):
    repo, _ = clone_repo(tmp_path)
    skill = repo / "skills/recipe-engineering/SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8") + "\nUse `company/operator-fixture/missing.md`.\n",
        encoding="utf-8",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-m", "add missing closure fixture")
    commit = git(repo, "rev-parse", "HEAD")

    result = operator_command(repo, commit, tmp_path / "out")

    assert result.returncode == 1
    assert "missing referenced runtime path: company/operator-fixture/missing.md" in result.stderr
    assert not list((tmp_path / "out").glob("*.zip"))


def test_real_operator_artifact_passes_source_anchored_validator(tmp_path):
    repo, commit = clone_repo(tmp_path)
    artifact = run_operator_builder(repo, commit, tmp_path / "out")

    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--artifact",
            str(artifact),
            "--source-repo",
            str(repo),
            "--source-commit",
            commit,
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Operator package validation: PASS" in result.stdout
