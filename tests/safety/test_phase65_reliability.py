from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "references/safety/official_sources.yaml"
PROTOCOL = ROOT / "references/safety/official_research_protocol.md"
HACCP = ROOT / "references/safety/haccp_operational_framework.md"
HYGIENE = ROOT / "references/safety/hygiene_prerequisite_programs.md"
EVIDENCE_SCHEMA = ROOT / "schemas/safety_evidence.schema.json"
HACCP_SCHEMA = ROOT / "schemas/haccp_plan.schema.json"
SKILL = ROOT / "skills/food-safety-allergens/SKILL.md"
EVALS = ROOT / "evals/safety/safety_cases.yaml"
TEMPLATES = [
    ROOT / "templates/safety/haccp_plan.yaml",
    ROOT / "templates/safety/temperature_monitoring_log.md",
    ROOT / "templates/safety/cleaning_sanitation_schedule.md",
    ROOT / "templates/safety/receiving_traceability_check.md",
    ROOT / "templates/safety/corrective_action_log.md",
    ROOT / "templates/safety/allergen_service_matrix.md",
    ROOT / "templates/safety/staff_hygiene_brief.md",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase65_artifacts_exist():
    for path in [SOURCES, PROTOCOL, HACCP, HYGIENE, EVIDENCE_SCHEMA, HACCP_SCHEMA, SKILL, EVALS, *TEMPLATES]:
        assert path.is_file(), path


def test_official_source_registry_is_on_demand_and_has_required_authorities():
    data = yaml.safe_load(SOURCES.read_text(encoding="utf-8"))
    assert data["update_mode"] == "on_demand_only"
    assert data["background_monitoring"] is False
    ids = {item["source_id"] for item in data["sources"]}
    required = {
        "eu_reg_852_2004",
        "eu_commission_fsms_notice_2022_c355_01",
        "eu_reg_1169_2011",
        "eu_reg_2073_2005",
        "eu_reg_178_2002",
        "eu_reg_2017_625",
        "efet_haccp_guidance",
        "greek_health_47829_2017",
        "efsa_scientific_advice",
        "codex_cxc_1_1969",
        "who_five_keys",
    }
    assert required <= ids
    for item in data["sources"]:
        assert item["canonical_url"].startswith("https://")
        assert item["jurisdiction"]
        assert item["authority_type"] in {"binding_law", "official_guidance", "scientific_authority", "international_standard", "public_health_guidance"}
        assert item["live_reverify"] is True


def test_research_protocol_requires_freshness_and_claim_classification():
    text = PROTOCOL.read_text(encoding="utf-8").lower()
    for phrase in [
        "current regulatory requirement",
        "official guidance",
        "scientific evidence",
        "operational best practice",
        "jurisdiction",
        "version",
        "retrieved_at",
        "current consolidated",
        "do not use background monitoring",
        "do not silently modify canonical doctrine",
    ]:
        assert phrase in text
    for trigger in ["temperature", "microbiological", "allergen", "haccp", "sanitary", "traceability", "recall"]:
        assert trigger in text


def test_evidence_schema_requires_source_date_jurisdiction_and_classification():
    schema = load_json(EVIDENCE_SCHEMA)
    Draft202012Validator.check_schema(schema)
    valid = {
        "schema_version": 1,
        "claim": "Food businesses must maintain HACCP-based procedures.",
        "classification": "current_regulatory_requirement",
        "jurisdiction": "EU",
        "source_id": "eu_reg_852_2004",
        "authority_type": "binding_law",
        "canonical_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:32004R0852",
        "retrieved_at": "2026-09-02",
        "version_or_effective_date": "2021-03-24",
        "verification_status": "verified_official_source",
    }
    validator = Draft202012Validator(schema)
    assert list(validator.iter_errors(valid)) == []
    invalid = dict(valid); invalid.pop("retrieved_at"); invalid.pop("jurisdiction")
    assert list(validator.iter_errors(invalid))


def test_haccp_framework_covers_hazard_analysis_and_control_classes():
    text = HACCP.read_text(encoding="utf-8").lower()
    for term in [
        "biological", "chemical", "physical", "allergen", "flow diagram",
        "ghp", "prp", "oprp", "ccp", "critical limit", "monitoring",
        "corrective action", "validation", "verification", "records",
    ]:
        assert term in text
    assert "not every control" in text and "ccp" in text


def test_hygiene_prerequisites_cover_operational_programs():
    text = HYGIENE.read_text(encoding="utf-8").lower()
    for term in [
        "cleaning", "sanitation", "personal hygiene", "water", "waste", "pest",
        "maintenance", "temperature", "cold chain", "allergen", "cross-contact",
        "supplier", "receiving", "traceability", "recall", "food safety culture", "training",
    ]:
        assert term in text


def test_haccp_plan_schema_requires_evidence_hazards_controls_and_approval():
    schema = load_json(HACCP_SCHEMA)
    Draft202012Validator.check_schema(schema)
    required = set(schema["required"])
    for key in ["scope", "process_steps", "hazard_analysis", "control_plan", "source_evidence", "verification", "approval_status"]:
        assert key in required


def test_templates_have_monitoring_corrective_action_and_human_review_boundaries():
    joined = "\n".join(p.read_text(encoding="utf-8") for p in TEMPLATES).lower()
    for term in ["monitor", "corrective action", "responsible", "date", "human review", "source"]:
        assert term in joined
    assert "allergen" in joined and "temperature" in joined and "traceability" in joined


def test_food_safety_skill_is_upgraded_to_haccp_hygiene_and_official_research():
    text = SKILL.read_text(encoding="utf-8")
    lower = text.lower()
    for ref in [
        "references/safety/official_sources.yaml",
        "references/safety/official_research_protocol.md",
        "references/safety/haccp_operational_framework.md",
        "references/safety/hygiene_prerequisite_programs.md",
    ]:
        assert ref in text
    assert "HACCP" in text and "GHP" in text
    assert "on-demand" in lower
    assert "current regulatory requirement" in lower
    assert "operational best practice" in lower
    assert "background monitoring" in lower


def test_safety_evals_cover_current_greek_eu_and_haccp_pressure_cases():
    data = yaml.safe_load(EVALS.read_text(encoding="utf-8"))
    cases = {c["case_id"]: c for c in data["cases"]}
    for cid in ["SAFETY-CURRENT-GR", "SAFETY-HACCP-OFFSITE", "SAFETY-ALLERGEN-HARD-BLOCK", "SAFETY-MICRO-CRITERIA"]:
        assert cid in cases
    assert cases["SAFETY-CURRENT-GR"]["research_required"] is True
    assert "EFET" in cases["SAFETY-CURRENT-GR"]["official_source_priority"]
    assert cases["SAFETY-HACCP-OFFSITE"]["human_review_required"] is True


def test_orchestrator_routes_haccp_hygiene_and_current_sanitary_work_to_safety_gate():
    routing = yaml.safe_load((ROOT / "skills/chef-ai-pro-business/references/routing.yaml").read_text(encoding="utf-8"))
    route = next(item for item in routing["routes"] if item["route_id"] == "safety_critical")
    intent = route["intent"].lower()
    assert "haccp" in intent and "hygiene" in intent and "sanitary" in intent
    assert route["required_skills"] == ["food-safety-allergens"]
    assert route["hard_gate"] == "safety"
    assert route["research_policy"] == "on_demand_official_when_current_claim"
