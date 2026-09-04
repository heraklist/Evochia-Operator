from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile

from scripts.operator_support.git_source import GitSource

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "scripts/build_skill_package.py"
CANONICAL_VALIDATOR = ROOT / "scripts/validate_skill_package.py"
CANONICAL_VALIDATOR_BLOB = "1d94966ba4677255fd4d02c594ff4f514e946a37"


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
    commit = git(repo, "rev-parse", "HEAD")
    return repo, commit


def run_multi_builder(repo: Path, commit: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--target",
            "multi",
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
    assert result.returncode == 0, result.stderr or result.stdout

    matches = list(output_dir.glob("chef-ai-pro-business-*-multi.zip"))
    assert len(matches) == 1
    return matches[0]


def test_multi_build_is_reproducible_and_uses_commit_derived_filename(tmp_path):
    repo, commit = clone_repo(tmp_path)
    version = GitSource(repo, commit).read_bytes("VERSION").decode("utf-8").strip()

    artifact_a = run_multi_builder(repo, commit, tmp_path / "out-a")
    artifact_b = run_multi_builder(repo, commit, tmp_path / "out-b")

    expected_name = f"chef-ai-pro-business-{version}-{commit[:7]}-multi.zip"
    assert artifact_a.name == artifact_b.name == expected_name
    assert artifact_a.read_bytes() == artifact_b.read_bytes()
    assert sha256(artifact_a.read_bytes()).hexdigest() == sha256(artifact_b.read_bytes()).hexdigest()


def test_multi_build_materializes_exact_committed_tree_and_git_modes(tmp_path):
    repo, commit = clone_repo(tmp_path)
    source = GitSource(repo, commit)
    artifact = run_multi_builder(repo, commit, tmp_path / "out")
    expected_entries = {entry.path: entry for entry in source.entries()}

    with ZipFile(artifact) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        assert names == sorted(expected_entries)
        assert len([name for name in names if name.startswith("skills/") and name.endswith("/SKILL.md")]) == 12
        assert not [name for name in names if name.endswith("/MODULE.md")]
        assert archive.read("VERSION") == source.read_bytes("VERSION")

        for path, entry in expected_entries.items():
            assert archive.read(path) == source.read_bytes(path)
            expected_mode = 0o100755 if entry.mode & 0o111 else 0o100644
            assert archive.getinfo(path).external_attr >> 16 == expected_mode


def test_multi_build_ignores_dirty_tracked_and_untracked_worktree_state(tmp_path):
    repo, commit = clone_repo(tmp_path)
    clean = run_multi_builder(repo, commit, tmp_path / "clean")

    tracked = repo / "data/allergens/fnb_allergen_master_v1.csv"
    assert tracked.is_file()
    tracked.write_bytes(tracked.read_bytes() + b"\r\nDIRTY-WORKTREE-ONLY\r\n")
    (repo / "untracked-build-noise.txt").write_text("untracked\n", encoding="utf-8")

    dirty = run_multi_builder(repo, commit, tmp_path / "dirty")

    assert clean.read_bytes() == dirty.read_bytes()


def test_multi_artifact_passes_existing_canonical_validator_without_changes(tmp_path):
    repo, commit = clone_repo(tmp_path)
    validator_blob = git(repo, "rev-parse", f"{commit}:scripts/validate_skill_package.py")
    assert validator_blob == CANONICAL_VALIDATOR_BLOB

    artifact = run_multi_builder(repo, commit, tmp_path / "out")
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    shutil.unpack_archive(str(artifact), str(extracted), format="zip")

    result = subprocess.run(
        [sys.executable, str(CANONICAL_VALIDATOR), str(extracted)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Skill package validation: PASS" in result.stdout
