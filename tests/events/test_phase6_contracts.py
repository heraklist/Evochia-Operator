from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
BRIEF = ROOT / "schemas" / "event_brief.schema.json"
ECON = ROOT / "schemas" / "event_economics.schema.json"
TEMPLATES = [
    ROOT / "templates" / "operations" / "event_brief.md",
    ROOT / "templates" / "operations" / "production_plan.md",
    ROOT / "templates" / "operations" / "shopping_plan.md",
    ROOT / "templates" / "operations" / "packing_loading.md",
    ROOT / "templates" / "operations" / "run_sheet.md",
    ROOT / "templates" / "operations" / "close_out.md",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(path: Path, data: dict):
    schema = load(path)
    Draft202012Validator.check_schema(schema)
    return list(Draft202012Validator(schema).iter_errors(data))


def sample_brief() -> dict:
    return {
        "schema_version": 1,
        "event_id": "evt-001",
        "status": "draft",
        "client": {"name": "Private Client", "contact_ref": None},
        "occasion": "private dinner",
        "date_time": {"date": "2026-09-20", "service_time": "20:30", "timezone": "Europe/Athens"},
        "location": {"venue": "Private villa", "city": "Athens", "country": "GR"},
        "pax": {"total": 12, "adults": 10, "children": 2},
        "service_style": "plated",
        "kitchen_equipment": {"kitchen_available": True, "known_equipment": ["oven"], "missing_or_unknown": ["plate warmer"]},
        "dietary_allergen_constraints": [{"type": "allergen", "value": "nuts", "severity_or_note": "severe allergy"}],
        "budget_price_context": {"currency": "EUR", "budget_total": 1200, "price_context": "client budget"},
        "travel_accommodation": {"travel_required": False, "accommodation_required": False, "notes": None},
        "staffing": {"chef_count": 1, "assistant_count": 1, "service_count": 1, "stewarding_count": 0, "notes": None},
        "known_facts": ["12 guests"],
        "unknowns": ["plate warmer availability"],
        "assumptions": ["service starts at 20:30"],
        "decision_state": "needs_review",
    }


def sample_economics() -> dict:
    return {
        "schema_version": 1,
        "scenario_id": "econ-001",
        "currency": "EUR",
        "food_cost": 240,
        "labour": {"chef_founder": 300, "assistants": 120, "service": 100, "stewarding": 0, "shopping_prep_time": 80},
        "travel": {"transport": 20, "tolls": 0, "ferry": 0, "parking": 10},
        "accommodation_overnight": 0,
        "equipment_rental": 0,
        "consumables_packaging": 25,
        "overhead": {"variable": 30, "fixed_allocation": 40},
        "cash_cost": 565,
        "economic_cost": 965,
        "opportunity_cost": 100,
        "vat": {"rate_pct": 24, "basis": "client_fee", "amount": 290.32},
        "client_fee": 1500,
        "contribution": 935,
        "gross_profit": 535,
        "margin_pct": 35.67,
        "minimum_viable_price": 1100,
        "assumptions": ["labour treated as economic cost"],
    }


def test_phase6_artifacts_exist():
    assert BRIEF.is_file() and ECON.is_file()
    assert all(p.is_file() for p in TEMPLATES)


def test_event_brief_schema_accepts_contract():
    assert validate(BRIEF, sample_brief()) == []


def test_event_brief_requires_decision_state_and_unknowns():
    data = sample_brief(); data.pop("decision_state"); data.pop("unknowns")
    assert validate(BRIEF, data)


def test_event_economics_schema_accepts_cash_and_economic_cost():
    assert validate(ECON, sample_economics()) == []


def test_event_economics_requires_founder_labour_and_minimum_viable_price():
    data = sample_economics(); data["labour"].pop("chef_founder"); data.pop("minimum_viable_price")
    assert validate(ECON, data)


def test_templates_expose_audience_and_assumption_boundaries():
    joined = "\n".join(p.read_text(encoding="utf-8") for p in TEMPLATES).lower()
    assert "internal" in joined and "operations" in joined and "client-safe" in joined and "assumption" in joined


def test_client_safe_template_contract_forbids_internal_leakage():
    text = TEMPLATES[0].read_text(encoding="utf-8").lower()
    for term in ["internal margin", "supplier comparison", "opportunity cost", "hidden assumptions"]:
        assert term in text
    assert "must not appear" in text or "do not expose" in text
