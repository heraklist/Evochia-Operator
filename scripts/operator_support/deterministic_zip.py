from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

_FIXED_TIME = (1980, 1, 1, 0, 0, 0)
_REGULAR_FILE = 0o100000


@dataclass(frozen=True)
class ArchiveEntry:
    path: str
    data: bytes
    mode: int = 0o100644


def _normalized_git_mode(mode: int) -> int:
    """Normalize a Git blob mode to the only two executable states Git preserves."""
    return 0o100755 if mode & 0o111 else 0o100644


def write_deterministic_zip(path: Path | str, entries: Iterable[ArchiveEntry]) -> str:
    """Write a byte-reproducible ZIP from in-memory entries and return its SHA-256.

    Entry permissions come from Git-style blob modes supplied by the caller, never
    from the host filesystem. Metadata that could vary by host or wall-clock time
    is fixed explicitly.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    ordered = tuple(sorted(entries, key=lambda item: item.path))
    if len({entry.path for entry in ordered}) != len(ordered):
        raise ValueError("duplicate archive path")

    with ZipFile(
        destination,
        "w",
        compression=ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        archive.comment = b""
        for entry in ordered:
            info = ZipInfo(entry.path, date_time=_FIXED_TIME)
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.compress_type = ZIP_DEFLATED
            info.internal_attr = 0
            info.external_attr = _normalized_git_mode(entry.mode) << 16
            info.extra = b""
            info.comment = b""
            archive.writestr(
                info,
                entry.data,
                compress_type=ZIP_DEFLATED,
                compresslevel=9,
            )

    return sha256(destination.read_bytes()).hexdigest()
