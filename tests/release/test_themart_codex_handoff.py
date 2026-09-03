from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "release/release_readiness.yaml"


def test_phase8b_is_open_but_explicitly_planned_for_codex_execution():
    data = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    blocker = next(item for item in data["blockers"] if item["id"] == "phase8b_exact_themart_source_migration")
    assert blocker["status"] == "OPEN"
    assert blocker["planned_executor"] == "CODEX"
    assert blocker["execution_mode"] == "EXACT_SOURCE_MIGRATION"
    assert blocker["prohibition"] == "do_not_reconstruct_collector_or_extractor_from_memory"
