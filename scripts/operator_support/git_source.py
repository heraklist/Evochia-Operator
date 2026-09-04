from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class GitEntry:
    path: str
    mode: int
    blob_sha: str


def sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


class GitSource:
    """Read repository state from committed Git objects, never working-tree bytes."""

    def __init__(self, repo: Path | str, commit: str):
        self.repo = Path(repo).resolve()
        self.commit = commit

    def _run(self, *args: str, text: bool = False):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=text,
        )

    def full_commit(self) -> str:
        return self._run("rev-parse", f"{self.commit}^{{commit}}", text=True).stdout.strip()

    def entries(self, prefix: str | None = None) -> tuple[GitEntry, ...]:
        args = ["ls-tree", "-r", "-z", self.full_commit()]
        if prefix:
            args += ["--", prefix]
        raw = self._run(*args).stdout
        entries: list[GitEntry] = []
        for record in raw.split(b"\0"):
            if not record:
                continue
            meta, path = record.split(b"\t", 1)
            mode, kind, blob_sha = meta.decode("ascii").split()
            if kind != "blob":
                continue
            entries.append(
                GitEntry(
                    path=path.decode("utf-8"),
                    mode=int(mode, 8),
                    blob_sha=blob_sha,
                )
            )
        return tuple(sorted(entries, key=lambda item: item.path))

    def read_bytes(self, path: str) -> bytes:
        return self._run("show", f"{self.full_commit()}:{path}").stdout
