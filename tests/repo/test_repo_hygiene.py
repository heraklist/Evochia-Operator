from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_repo_hygiene import validate_tree  # noqa: E402


def reasons(tmp_path: Path) -> list[str]:
    return [violation.reason for violation in validate_tree(tmp_path)]


def test_clean_tree_passes(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("clean\n", encoding="utf-8")
    assert validate_tree(tmp_path) == []


def test_root_git_directory_is_allowed(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("local only", encoding="utf-8")
    assert validate_tree(tmp_path) == []


def test_nested_git_directory_is_rejected(tmp_path: Path) -> None:
    nested = tmp_path / "vendor" / ".git"
    nested.mkdir(parents=True)
    assert "nested .git directory" in reasons(tmp_path)


def test_themart_browser_profile_is_rejected(tmp_path: Path) -> None:
    profile = tmp_path / "providers" / "themart" / ".browser_profile_themart"
    profile.mkdir(parents=True)
    (profile / "Cookies").write_bytes(b"cookie-db")
    found = reasons(tmp_path)
    assert "browser profile directory" in found


def test_environment_and_key_files_are_rejected(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=x", encoding="utf-8")
    (tmp_path / "client.pem").write_text("private", encoding="utf-8")
    found = reasons(tmp_path)
    assert "environment/credential file" in found
    assert "private key/certificate file" in found


def test_python_venv_cache_and_output_are_rejected(tmp_path: Path) -> None:
    for relative in (".venv", "pkg/__pycache__", "output"):
        (tmp_path / relative).mkdir(parents=True)
    found = reasons(tmp_path)
    assert "python virtual environment" in found
    assert "python cache directory" in found
    assert "generated output directory" in found


def test_chromium_session_artifacts_are_rejected(tmp_path: Path) -> None:
    profile = tmp_path / "local-browser" / "Default"
    profile.mkdir(parents=True)
    for filename in ("Cookies", "Login Data", "Local State"):
        (profile / filename).write_bytes(b"sensitive")
    found = reasons(tmp_path)
    assert found.count("chromium/session artifact") == 3


def test_oversized_binary_outside_allowlist_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "random.bin"
    artifact.write_bytes(b"123456789")
    violations = validate_tree(tmp_path, max_binary_bytes=8)
    assert any(v.reason == "oversized binary outside allowlist" for v in violations)


def test_oversized_binary_in_brand_assets_is_allowed(tmp_path: Path) -> None:
    artifact = tmp_path / "company" / "evochia" / "assets" / "logo.bin"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"123456789")
    assert validate_tree(tmp_path, max_binary_bytes=8) == []


def test_env_example_is_allowed(tmp_path: Path) -> None:
    (tmp_path / ".env.example").write_text("KEY=\n", encoding="utf-8")
    assert validate_tree(tmp_path) == []
