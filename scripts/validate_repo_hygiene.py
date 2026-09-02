#!/usr/bin/env python3
"""Fail closed on repository artifacts that must never enter Chef AI source control."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import os
import subprocess
import sys

DEFAULT_MAX_BINARY_BYTES = 25 * 1024 * 1024

FORBIDDEN_DIR_REASONS = {
    ".browser_profile_themart": "browser profile directory",
    ".venv": "python virtual environment",
    "venv": "python virtual environment",
    "__pycache__": "python cache directory",
    ".pytest_cache": "python cache directory",
    "output": "generated output directory",
}

SENSITIVE_CHROMIUM_FILES = {
    "Cookies",
    "Cookies-journal",
    "Login Data",
    "Login Data-journal",
    "Web Data",
    "Web Data-journal",
    "History",
    "History-journal",
    "Local State",
    "Network Persistent State",
    "Trust Tokens",
}

EXPLICIT_CREDENTIAL_NAMES = {
    "credentials.json",
}

PRIVATE_KEY_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
BINARY_SUFFIXES = {
    ".bin",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".xlsx",
    ".xls",
    ".docx",
    ".zip",
    ".gz",
    ".tar",
}

LARGE_BINARY_ALLOWLIST_PREFIXES = (
    Path("company/evochia/assets"),
    Path("data"),
)


@dataclass(frozen=True, order=True)
class Violation:
    path: str
    reason: str


def _is_under(path: Path, prefix: Path) -> bool:
    try:
        path.relative_to(prefix)
        return True
    except ValueError:
        return False


def _is_probably_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True
    try:
        sample = path.read_bytes()[:8192]
    except OSError:
        return False
    if b"\x00" in sample:
        return True
    try:
        sample.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True


def _file_violation(relative: Path, absolute: Path, max_binary_bytes: int) -> list[Violation]:
    found: list[Violation] = []
    name = relative.name
    lower = name.lower()

    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        found.append(Violation(str(relative), "environment/credential file"))

    if absolute.suffix.lower() in PRIVATE_KEY_SUFFIXES:
        found.append(Violation(str(relative), "private key/certificate file"))

    if lower in EXPLICIT_CREDENTIAL_NAMES or lower.startswith("client_secret") or lower.startswith("service_account"):
        found.append(Violation(str(relative), "environment/credential file"))

    if name in SENSITIVE_CHROMIUM_FILES:
        found.append(Violation(str(relative), "chromium/session artifact"))

    try:
        size = absolute.stat().st_size
    except OSError:
        size = 0
    allowed_large = any(_is_under(relative, prefix) for prefix in LARGE_BINARY_ALLOWLIST_PREFIXES)
    if size > max_binary_bytes and not allowed_large and _is_probably_binary(absolute):
        found.append(Violation(str(relative), "oversized binary outside allowlist"))

    return found


def _git_candidate_files(root_path: Path) -> list[Path] | None:
    """Return tracked + non-ignored untracked files when root is a real git worktree."""
    try:
        check = subprocess.run(
            ["git", "-C", str(root_path), "rev-parse", "--is-inside-work-tree"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if check.returncode != 0 or check.stdout.strip() != "true":
        return None

    candidates: set[Path] = set()
    for args in (
        ["ls-files", "-z"],
        ["ls-files", "--others", "--exclude-standard", "-z"],
    ):
        proc = subprocess.run(
            ["git", "-C", str(root_path), *args],
            check=False,
            capture_output=True,
        )
        if proc.returncode != 0:
            return None
        for raw in proc.stdout.split(b"\x00"):
            if raw:
                candidates.add(Path(raw.decode("utf-8", errors="surrogateescape")))
    return sorted(candidates)


def _directory_violations(relative: Path) -> list[Violation]:
    found: list[Violation] = []
    parts = relative.parts
    for index, dirname in enumerate(parts[:-1]):
        rel_dir = Path(*parts[: index + 1])
        if dirname == ".git":
            found.append(Violation(str(rel_dir), "nested .git directory"))
        elif dirname.startswith(".browser_profile") or dirname in {"chromium-profile", "chrome-profile"}:
            found.append(Violation(str(rel_dir), "browser profile directory"))
        else:
            reason = FORBIDDEN_DIR_REASONS.get(dirname)
            if reason:
                found.append(Violation(str(rel_dir), reason))
    return found


def _nested_git_directories(root_path: Path) -> list[Violation]:
    found: list[Violation] = []
    for current, dirnames, _filenames in os.walk(root_path):
        current_path = Path(current)
        relative_current = current_path.relative_to(root_path)
        if relative_current == Path(".") and ".git" in dirnames:
            dirnames.remove(".git")
        if ".git" in dirnames:
            rel = relative_current / ".git"
            found.append(Violation(str(rel), "nested .git directory"))
            dirnames.remove(".git")
    return found


def validate_tree(root: Path | str, *, max_binary_bytes: int = DEFAULT_MAX_BINARY_BYTES) -> list[Violation]:
    root_path = Path(root).resolve()
    violations: list[Violation] = []

    candidates = _git_candidate_files(root_path)
    if candidates is not None:
        violations.extend(_nested_git_directories(root_path))
        for relative in candidates:
            absolute = root_path / relative
            if not absolute.is_file():
                continue
            violations.extend(_directory_violations(relative))
            violations.extend(_file_violation(relative, absolute, max_binary_bytes))
        return sorted(set(violations))

    for current, dirnames, filenames in os.walk(root_path):
        current_path = Path(current)
        relative_current = current_path.relative_to(root_path)

        if relative_current == Path(".") and ".git" in dirnames:
            dirnames.remove(".git")

        kept_dirs: list[str] = []
        for dirname in dirnames:
            rel = relative_current / dirname
            if dirname == ".git":
                violations.append(Violation(str(rel), "nested .git directory"))
                continue
            if dirname.startswith(".browser_profile") or dirname in {"chromium-profile", "chrome-profile"}:
                violations.append(Violation(str(rel), "browser profile directory"))
                continue
            reason = FORBIDDEN_DIR_REASONS.get(dirname)
            if reason:
                violations.append(Violation(str(rel), reason))
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in filenames:
            rel = relative_current / filename
            violations.extend(_file_violation(rel, current_path / filename, max_binary_bytes))

    return sorted(set(violations))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    parser.add_argument(
        "--max-binary-mb",
        type=float,
        default=DEFAULT_MAX_BINARY_BYTES / (1024 * 1024),
        help="maximum binary size outside allowlisted asset/data paths (default: 25 MiB)",
    )
    args = parser.parse_args(argv)
    max_bytes = int(args.max_binary_mb * 1024 * 1024)
    violations = validate_tree(Path(args.root), max_binary_bytes=max_bytes)
    if not violations:
        print("Repository hygiene: PASS")
        return 0
    print("Repository hygiene: FAIL", file=sys.stderr)
    for item in violations:
        print(f"- {item.path}: {item.reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
