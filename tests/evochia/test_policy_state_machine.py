from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "company/evochia/policies"
CONTRACT = POLICY_DIR / "policy_state_contract.yaml"
READINESS = ROOT / "release/release_readiness.yaml"

ALLOWED = {"OWNER_REVIEW_DRAFT", "PARTIALLY_APPROVED", "APPROVED"}
EXPECTED_CLASSES = {
    "company_profile.md": "canonical_current_data",
    "current_rates.md": "canonical_current_data",
    "commercial_policy.md": "canonical_policy",
    "staffing_policy.md": "canonical_policy",
    "terms_policy.md": "canonical_policy",
}


def extract_status(text: str) -> str:
    match = re.search(r"Policy status:\*\*\s*`?([A-Z_]+)`?", text)
    assert match, "missing explicit Policy status"
    return match.group(1)


def test_policy_state_contract_has_transition_safe_vocabulary_and_authority_classes():
    data = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    assert set(data["allowed_statuses"]) == ALLOWED
    assert data["approval_metadata_required"] == ["approved_by", "effective_date", "approval_reference"]
    classes = {name: item["source_class_when_approved"] for name, item in data["policies"].items()}
    assert classes == EXPECTED_CLASSES


def test_policy_manifest_status_matches_each_policy_document_and_approved_requires_metadata():
    data = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    for name, item in data["policies"].items():
        status = item["status"]
        assert status in ALLOWED
        text = (POLICY_DIR / name).read_text(encoding="utf-8")
        assert extract_status(text) == status
        if status == "APPROVED":
            for field in data["approval_metadata_required"]:
                assert item.get(field), f"{name}: approved policy missing {field}"


def test_release_readiness_vocabulary_can_represent_fully_approved_commercial_policy():
    readiness = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert readiness["commercial_policy_readiness"] in {
        "OWNER_REVIEW_REQUIRED", "PARTIALLY_APPROVED", "APPROVED"
    }
