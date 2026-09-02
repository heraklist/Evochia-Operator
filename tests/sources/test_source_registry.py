from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_source_registry import load_registry, validate_registry  # noqa: E402

REGISTRY = ROOT / "references" / "source_registry.yaml"
SCHEMA = ROOT / "schemas" / "source_registry.schema.json"


def registry() -> dict:
    return load_registry(REGISTRY)


def test_current_registry_is_valid() -> None:
    assert validate_registry(registry(), SCHEMA) == []


def test_registry_contains_expected_canonical_and_superseded_sources() -> None:
    by_id = {item["source_id"]: item for item in registry()["sources"]}
    assert by_id["evochia_ci_v33"]["source_class"] == "canonical_current_data"
    assert by_id["evochia_ci_v20"]["source_class"] == "superseded"
    assert by_id["evochia_ci_v10"]["source_class"] == "superseded"
    assert by_id["evochia_ci_v20"]["superseded_by"] == ["evochia_ci_v33"]
    assert by_id["evochia_ci_v10"]["superseded_by"] == ["evochia_ci_v33"]


def test_sample_proposal_is_not_current_rate_policy() -> None:
    by_id = {item["source_id"]: item for item in registry()["sources"]}
    proposal = by_id["evochia_sample_private_chef_proposal"]
    assert proposal["source_class"] == "golden_example"
    assert "current_rates" in proposal["forbidden_uses"]
    assert "pricing_policy" in proposal["forbidden_uses"]


def test_validator_rejects_duplicate_source_ids() -> None:
    data = deepcopy(registry())
    data["sources"].append(deepcopy(data["sources"][0]))
    assert any("duplicate source_id" in issue for issue in validate_registry(data, SCHEMA))


def test_validator_rejects_supersession_cycle() -> None:
    data = deepcopy(registry())
    by_id = {item["source_id"]: item for item in data["sources"]}
    by_id["evochia_ci_v33"]["supersedes"] = ["evochia_ci_v20"]
    by_id["evochia_ci_v20"]["superseded_by"] = ["evochia_ci_v33"]
    by_id["evochia_ci_v20"]["supersedes"] = ["evochia_ci_v33"]
    by_id["evochia_ci_v33"]["superseded_by"] = ["evochia_ci_v20"]
    assert any("supersession cycle" in issue for issue in validate_registry(data, SCHEMA))


def test_validator_rejects_current_source_without_review_metadata() -> None:
    data = deepcopy(registry())
    item = next(x for x in data["sources"] if x["source_class"] == "canonical_current_data")
    item["last_reviewed_at"] = None
    assert any("last_reviewed_at" in issue for issue in validate_registry(data, SCHEMA))


def test_validator_rejects_golden_example_as_pricing_authority() -> None:
    data = deepcopy(registry())
    item = next(x for x in data["sources"] if x["source_class"] == "golden_example")
    item["allowed_uses"].append("current_rates")
    assert any("golden_example" in issue and "pricing" in issue for issue in validate_registry(data, SCHEMA))


def test_validator_rejects_superseded_source_marked_current() -> None:
    data = deepcopy(registry())
    item = next(x for x in data["sources"] if x["source_class"] == "superseded")
    item["authority"] = "current"
    assert any("superseded" in issue and "current" in issue for issue in validate_registry(data, SCHEMA))
