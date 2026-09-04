from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "release/release_readiness.yaml"


def test_phase8b_is_closed_with_exact_source_verification_evidence():
    data = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    blocker = next(item for item in data["blockers"] if item["id"] == "phase8b_exact_themart_source_migration")
    assert blocker["status"] == "CLOSED"
    assert str(blocker["closed_at"]) == "2026-09-04"
    assert blocker["planned_executor"] == "CODEX"
    assert blocker["execution_mode"] == "EXACT_SOURCE_MIGRATION"
    assert blocker["prohibition"] == "do_not_reconstruct_collector_or_extractor_from_memory"
    assert blocker["completion_evidence"]["provenance_manifest"] == "scripts/supplier-providers/themart/source_provenance.yaml"
    assert blocker["completion_evidence"]["checksum_verifier"] == "scripts/verify_themart_source_provenance.py"
    assert blocker["completion_evidence"]["canonical_python_files_byte_identical"] is True
