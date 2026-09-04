#!/usr/bin/env python3
"""Build deterministic Chef AI package artifacts from committed Git objects."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

try:
    from scripts.operator_support.deterministic_zip import ArchiveEntry, write_deterministic_zip
    from scripts.operator_support.git_source import GitSource
except ModuleNotFoundError:  # direct: python scripts/build_skill_package.py
    from operator_support.deterministic_zip import ArchiveEntry, write_deterministic_zip
    from operator_support.git_source import GitSource


@dataclass(frozen=True)
class BuildResult:
    artifact_path: Path
    sha256: str
    source_commit: str
    source_version: str
    target: str


def _build_multi(source: GitSource, output_dir: Path) -> BuildResult:
    full_commit = source.full_commit()
    source = GitSource(source.repo, full_commit)
    version = source.read_bytes("VERSION").decode("utf-8").strip()

    entries = tuple(
        ArchiveEntry(
            path=entry.path,
            data=source.read_bytes(entry.path),
            mode=entry.mode,
        )
        for entry in source.entries()
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / f"chef-ai-pro-business-{version}-{full_commit[:7]}-multi.zip"
    digest = write_deterministic_zip(artifact, entries)
    return BuildResult(
        artifact_path=artifact,
        sha256=digest,
        source_commit=full_commit,
        source_version=version,
        target="multi",
    )


def build_package(
    *,
    target: str,
    source_repo: Path | str,
    source_commit: str,
    output_dir: Path | str,
) -> BuildResult:
    source = GitSource(source_repo, source_commit)
    destination = Path(output_dir)
    if target == "multi":
        return _build_multi(source, destination)
    raise ValueError(f"unsupported build target: {target}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=("multi", "operator"))
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)

    try:
        result = build_package(
            target=args.target,
            source_repo=Path(args.source_repo),
            source_commit=args.source_commit,
            output_dir=Path(args.output_dir),
        )
    except Exception as exc:
        print(f"Package build: FAIL\n- {exc}", file=sys.stderr)
        return 1

    print(f"Package build: PASS\n{result.artifact_path}\nSHA256 {result.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
