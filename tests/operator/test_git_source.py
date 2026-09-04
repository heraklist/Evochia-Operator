from pathlib import Path
import subprocess

from scripts.operator_support.git_source import GitSource, sha256_bytes


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def make_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    (repo / "contract.md").write_bytes(b"canonical\n")
    (repo / "nested").mkdir()
    (repo / "nested/resource.txt").write_bytes(b"resource\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture")
    return repo, git(repo, "rev-parse", "HEAD")


def test_reads_committed_blob_not_dirty_worktree(tmp_path):
    repo, commit = make_repo(tmp_path)
    source = GitSource(repo, commit)

    (repo / "contract.md").write_bytes(b"dirty\r\n")

    assert source.read_bytes("contract.md") == b"canonical\n"


def test_full_commit_and_blob_identity_match_git_objects(tmp_path):
    repo, commit = make_repo(tmp_path)
    source = GitSource(repo, commit[:8])

    assert source.full_commit() == commit
    entry = next(item for item in source.entries() if item.path == "contract.md")
    assert entry.blob_sha == git(repo, "rev-parse", f"{commit}:contract.md")
    assert sha256_bytes(source.read_bytes("contract.md")) == sha256_bytes(b"canonical\n")


def test_entries_are_from_committed_tree_and_support_exact_prefix(tmp_path):
    repo, commit = make_repo(tmp_path)
    source = GitSource(repo, commit)

    (repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")
    (repo / "nested/resource.txt").write_bytes(b"dirty resource\n")

    assert [item.path for item in source.entries()] == [
        "contract.md",
        "nested/resource.txt",
    ]
    assert [item.path for item in source.entries("nested/")] == [
        "nested/resource.txt",
    ]
    assert source.read_bytes("nested/resource.txt") == b"resource\n"
