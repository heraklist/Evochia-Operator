from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / "scripts/supplier-providers/themart"
PROVENANCE = PROVIDER / "source_provenance.yaml"
VERIFY_SCRIPT = ROOT / "scripts/verify_themart_source_provenance.py"

EXPECTED_ORIGINALS = {
    "themart_capture.py": (18048, "62a14ae84897a4bc5decc673567573c22b17e9f1dd1007ad14f7e6f23cf5787d"),
    "themart_extract_existing_html.py": (20431, "5fc4a636c75c129094d3485a761890203f15aa17d37f6679be1f830968acbc33"),
    "categories.json": (1395, "8d53cb62e069aa49262dd347fa411b93499bfeec0c8a25be2ed7a7ba892c4f31"),
    "requirements.txt": (53, "47ac3b7adce44abacc2120dc99ae1f9badd024b048d6c6b21b19a8df771ee198"),
    "run_windows.bat": (256, "6ef919d3d861205e2b38d1e564b4ec8f8f89d3e076fb2f6ee1a0a74279b0e61e"),
    "README_GR.md": (3321, "7e633735a4dc81f11bb0b918c7d94e13dcf9512fa3a0b317fd4cfc6844bc258b"),
    "README_HOTFIX_GR.md": (3647, "2e107b6816cdecdbd67493ea661076e89fc62f6024555ad5225a77d151426a11"),
    "tests/test_navigation.py": (1094, "430f887de2df8be272574e809623284d0f9b82efdcfd0d90a6290e7fa7c253be"),
    "test_recovery_extractor.py": (2512, "fc782408f823b9d22c7788d47a2e39e5b3711f7ed49bd197a185452b4ff25a03"),
}

EXPECTED_DESTINATIONS = {
    "themart_capture.py": "scripts/supplier-providers/themart/themart_capture.py",
    "themart_extract_existing_html.py": "scripts/supplier-providers/themart/themart_extract_existing_html.py",
    "categories.json": "scripts/supplier-providers/themart/categories.json",
    "requirements.txt": "scripts/supplier-providers/themart/requirements.txt",
    "run_windows.bat": "scripts/supplier-providers/themart/run_windows.bat",
    "README_GR.md": "scripts/supplier-providers/themart/README_GR.md",
    "README_HOTFIX_GR.md": "scripts/supplier-providers/themart/README_HOTFIX_GR.md",
    "tests/test_navigation.py": "tests/suppliers/test_themart_navigation.py",
    "test_recovery_extractor.py": "tests/suppliers/test_themart_recovery_extractor.py",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _records() -> dict[str, dict]:
    data = yaml.safe_load(PROVENANCE.read_text(encoding="utf-8"))
    return {item["original_relative_path"]: item for item in data["files"]}


def test_provenance_manifest_records_the_pre_migration_inventory_and_destinations():
    records = _records()

    assert set(records) == set(EXPECTED_ORIGINALS)
    for relative, (byte_length, sha256) in EXPECTED_ORIGINALS.items():
        record = records[relative]
        assert record["original_byte_length"] == byte_length
        assert record["original_sha256"] == sha256
        assert record["repository_destination"] == EXPECTED_DESTINATIONS[relative]
        assert record["migration_mode"] in {"EXACT_BYTE_COPY", "DERIVED_NORMALIZED_COPY"}


def test_migrated_hashes_match_repository_bytes_and_exact_copies_fail_closed():
    records = _records()

    for relative, record in records.items():
        destination = ROOT / record["repository_destination"]
        assert destination.is_file(), f"missing migrated destination for {relative}"
        migrated_sha = _sha256(destination)
        assert destination.stat().st_size == record["migrated_byte_length"]
        assert migrated_sha == record["migrated_sha256"]
        if record["migration_mode"] == "EXACT_BYTE_COPY":
            assert migrated_sha == record["original_sha256"]
        else:
            assert migrated_sha != record["original_sha256"]
            assert record["derivation_rationale"]


def test_canonical_python_sources_are_mandatory_exact_byte_copies():
    records = _records()

    for relative in ("themart_capture.py", "themart_extract_existing_html.py"):
        record = records[relative]
        assert record["migration_mode"] == "EXACT_BYTE_COPY"
        assert record["migrated_sha256"] == EXPECTED_ORIGINALS[relative][1]


def test_provenance_verifier_passes_for_the_repository_candidate():
    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "The Mart source provenance: PASS" in result.stdout


def test_provenance_verifier_fails_closed_when_an_exact_copy_is_tampered(tmp_path):
    provider = tmp_path / "scripts/supplier-providers/themart"
    provider.mkdir(parents=True)
    destination = provider / "themart_capture.py"
    destination.write_bytes(b"tampered")
    expected_sha = hashlib.sha256(b"original").hexdigest()
    migrated_sha = hashlib.sha256(b"original").hexdigest()

    (provider / "migration_manifest.yaml").write_text(
        yaml.safe_dump({"safe_source_allowlist": ["themart_capture.py"]}),
        encoding="utf-8",
    )
    (provider / "source_provenance.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "provider": "themart",
                "files": [
                    {
                        "original_relative_path": "themart_capture.py",
                        "original_byte_length": 8,
                        "original_sha256": expected_sha,
                        "repository_destination": "scripts/supplier-providers/themart/themart_capture.py",
                        "migrated_byte_length": 8,
                        "migrated_sha256": migrated_sha,
                        "migration_mode": "EXACT_BYTE_COPY",
                        "derivation_rationale": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "The Mart source provenance: FAIL" in result.stderr
    assert "migrated SHA-256 does not match repository bytes" in result.stderr
