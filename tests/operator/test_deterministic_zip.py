from hashlib import sha256
from zipfile import ZipFile

import pytest

from scripts.operator_support.deterministic_zip import ArchiveEntry, write_deterministic_zip


def test_same_entries_same_bytes_and_hash_regardless_of_input_order(tmp_path):
    entries = [
        ArchiveEntry("b.txt", b"B\n", 0o100644),
        ArchiveEntry("a.sh", b"#!/bin/sh\necho A\n", 0o100755),
        ArchiveEntry("nested/δοκιμή.txt", "UTF-8\n".encode("utf-8"), 0o100644),
    ]

    hash_a = write_deterministic_zip(tmp_path / "a.zip", entries)
    hash_b = write_deterministic_zip(tmp_path / "b.zip", reversed(entries))

    bytes_a = (tmp_path / "a.zip").read_bytes()
    bytes_b = (tmp_path / "b.zip").read_bytes()
    assert bytes_a == bytes_b
    assert hash_a == hash_b == sha256(bytes_a).hexdigest()


def test_archive_metadata_is_fixed_and_modes_come_from_git_style_input(tmp_path):
    path = tmp_path / "artifact.zip"
    write_deterministic_zip(
        path,
        [
            ArchiveEntry("plain.txt", b"plain\n", 0o100644),
            ArchiveEntry("tool.sh", b"#!/bin/sh\n", 0o100755),
        ],
    )

    with ZipFile(path) as archive:
        assert archive.comment == b""
        plain = archive.getinfo("plain.txt")
        tool = archive.getinfo("tool.sh")

        for info in (plain, tool):
            assert info.date_time == (1980, 1, 1, 0, 0, 0)
            assert info.create_system == 3
            assert info.extra == b""
            assert info.comment == b""

        assert plain.external_attr >> 16 == 0o100644
        assert tool.external_attr >> 16 == 0o100755


def test_non_executable_host_like_mode_is_normalized_to_git_non_executable(tmp_path):
    path = tmp_path / "artifact.zip"
    write_deterministic_zip(path, [ArchiveEntry("x.txt", b"x", 0o100664)])

    with ZipFile(path) as archive:
        assert archive.getinfo("x.txt").external_attr >> 16 == 0o100644


def test_content_change_changes_hash(tmp_path):
    hash_a = write_deterministic_zip(tmp_path / "a.zip", [ArchiveEntry("a", b"A")])
    hash_b = write_deterministic_zip(tmp_path / "b.zip", [ArchiveEntry("a", b"B")])
    assert hash_a != hash_b


def test_duplicate_archive_paths_fail_closed(tmp_path):
    with pytest.raises(ValueError, match="duplicate archive path"):
        write_deterministic_zip(
            tmp_path / "duplicate.zip",
            [ArchiveEntry("same", b"A"), ArchiveEntry("same", b"B")],
        )
