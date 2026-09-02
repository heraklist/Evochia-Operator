from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
RECIPE_SCHEMA = ROOT / "schemas" / "recipe.schema.json"
RECIPE_TEMPLATE = ROOT / "templates" / "recipes" / "production_recipe.yaml"
MENU_SCHEMA = ROOT / "schemas" / "menu_experience.schema.json"
RESEARCH_PROTOCOL = ROOT / "skills" / "culinary-rnd" / "references" / "research_protocol.md"
CULINARY_CASES = ROOT / "evals" / "culinary" / "culinary_cases.yaml"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validator(path: Path) -> Draft202012Validator:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def valid_recipe() -> dict:
    return {
        "schema_version": 1,
        "recipe_id": "rcp-beurre-blanc-001",
        "version": "1.0.0",
        "status": "draft",
        "title": "Beurre blanc",
        "description": "Professional production specification.",
        "category": "sauce",
        "cuisine": ["French"],
        "yield": {"quantity": 1000, "unit": "g", "portion_count": 10, "portion_size": {"quantity": 100, "unit": "g"}, "service_style": "plated"},
        "ingredients": [
            {"line_id": "ing-001", "name": "shallot", "quantity": 120, "unit": "g", "basis": "AP", "ap_quantity": 120, "ep_quantity": 102, "yield_pct": 85, "component": "reduction", "allergen_tags": []},
            {"line_id": "ing-002", "name": "butter", "quantity": 700, "unit": "g", "basis": "EP", "ep_quantity": 700, "component": "finish", "allergen_tags": ["milk"]},
        ],
        "allergens": ["milk"],
        "dietary_tags": ["vegetarian"],
        "equipment": ["saucepan", "fine strainer", "whisk"],
        "mise_en_place": [{"step": "Dice shallot finely", "timing": "before service"}],
        "method": [{"step_no": 1, "instruction": "Reduce wine, vinegar and shallot until nearly dry.", "time_minutes": 12, "temperature_c": 95, "sensory_cues": ["syrupy", "no raw wine aroma"]}],
        "finishing": ["Strain if required", "adjust acidity and seasoning"],
        "holding_regeneration": {"holding": "Hold warm without boiling.", "max_hold_minutes": 30, "regeneration": "Re-emulsify gently over low heat if needed."},
        "service_plating": ["Sauce immediately before pass"],
        "make_ahead_timeline": [{"offset": "T-1h", "action": "Prepare reduction base"}],
        "critical_points": [{"type": "quality", "point": "Do not boil after butter emulsification", "control": "low heat"}],
        "failure_recovery": [{"failure": "split emulsion", "likely_cause": "excess heat", "recovery": "whisk into a small amount of cool reduction", "prevention": "control heat"}],
        "scaling_notes": {"linear_scaling_safe": False, "sensitive_items": ["salt", "acid", "emulsification rate"], "process_changes": ["increase vessel surface area for large batch"]},
        "provenance": [{"source_type": "classical_reference", "title": "Classical beurre blanc technique", "role": "technique_reference"}, {"source_type": "original_synthesis", "title": "Chef AI adaptation", "role": "final_synthesis"}],
        "costing_hooks": {"costing_status": "not_costed", "ingredient_cost_basis": "unknown", "supplier_snapshot_refs": []},
    }


def valid_menu() -> dict:
    return {
        "schema_version": 1,
        "menu_id": "menu-001",
        "version": "1.0.0",
        "status": "draft",
        "title": "Summer private dinner",
        "occasion": "private dinner",
        "concept": "Mediterranean summer progression",
        "service_format": "plated",
        "dishes": [{"dish_id": "dish-1", "working_name": "tomato-course", "client_name": "Summer Tomato", "client_description": "Tomato, basil and cultured cream.", "recipe_refs": ["rcp-tomato-001"], "allergens": ["milk"], "dietary_tags": ["vegetarian"]}],
        "course_sequence": [{"course_id": "course-1", "label": "Starter", "dish_ids": ["dish-1"]}],
        "experience": {"progression_notes": ["bright opening", "controlled richness"], "service_rhythm": "steady"},
        "internal_projection": {"feasibility_state": "needs_review", "complexity_notes": ["last-minute plating"], "service_dependencies": ["cold plates"], "allergen_notes": ["milk in cultured cream"], "costing_hooks": ["dish-1"], "assumptions": ["10 guests"]},
        "client_projection": {"headline": "Summer Private Dinner", "intro": "A Mediterranean progression for a warm evening.", "course_ids": ["course-1"], "dietary_note": "Dietary requirements are confirmed before service.", "show_allergens": True},
    }


def test_phase5_artifacts_exist() -> None:
    for path in (RECIPE_SCHEMA, RECIPE_TEMPLATE, MENU_SCHEMA, RESEARCH_PROTOCOL, CULINARY_CASES):
        assert path.is_file(), path


def test_recipe_schema_is_valid_draft_2020_12() -> None:
    schema = load_json(RECIPE_SCHEMA)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_recipe_schema_accepts_professional_recipe_contract() -> None:
    errors = list(validator(RECIPE_SCHEMA).iter_errors(valid_recipe()))
    assert errors == [], [e.message for e in errors]


def test_recipe_schema_requires_ap_hook_when_basis_is_ap() -> None:
    recipe = valid_recipe()
    recipe["ingredients"][0].pop("ap_quantity")
    assert list(validator(RECIPE_SCHEMA).iter_errors(recipe))


def test_recipe_schema_requires_ep_hook_when_basis_is_ep() -> None:
    recipe = valid_recipe()
    recipe["ingredients"][1].pop("ep_quantity")
    assert list(validator(RECIPE_SCHEMA).iter_errors(recipe))


def test_recipe_schema_requires_professional_method_cues() -> None:
    recipe = valid_recipe()
    recipe["method"][0].pop("sensory_cues")
    assert list(validator(RECIPE_SCHEMA).iter_errors(recipe))


def test_recipe_template_validates_against_schema() -> None:
    errors = list(validator(RECIPE_SCHEMA).iter_errors(load_yaml(RECIPE_TEMPLATE)))
    assert errors == [], [e.message for e in errors]


def test_menu_schema_accepts_canonical_internal_and_client_projection() -> None:
    errors = list(validator(MENU_SCHEMA).iter_errors(valid_menu()))
    assert errors == [], [e.message for e in errors]


def test_client_projection_has_no_internal_commercial_fields() -> None:
    client = load_json(MENU_SCHEMA)["$defs"]["client_projection"]
    forbidden = {"margin", "internal_margin", "supplier_comparison", "opportunity_cost", "cost_basis", "hidden_assumptions"}
    assert not (set(client["properties"]) & forbidden)
    assert client.get("additionalProperties") is False


def test_research_protocol_distinguishes_expected_and_optional_web_use() -> None:
    text = RESEARCH_PROTOCOL.read_text(encoding="utf-8").lower()
    assert "expected" in text and "trend" in text
    assert "optional" in text and "classical" in text
    assert "greek" in text and "international" in text


def test_research_protocol_limits_visual_sources_to_inspiration() -> None:
    text = RESEARCH_PROTOCOL.read_text(encoding="utf-8").lower()
    assert "pinterest" in text and "visual inspiration" in text
    assert "not" in text and "safety" in text
    assert "synth" in text and "copy" in text
    assert "citation" in text or "provenance" in text


def test_culinary_eval_cases_cover_required_phase5_behaviors() -> None:
    data = load_yaml(CULINARY_CASES)
    cases = {item["case_id"]: item for item in data["cases"]}
    expected = {"CUL-ORIGINAL-CREATION", "CUL-CLASSICAL-NO-FORCED-WEB", "CUL-TREND-CURRENT-RESEARCH", "CUL-SYNTHESIS-NO-COPY", "CUL-SUBSTITUTION-BY-FUNCTION", "CUL-MENU-PROGRESSION", "CUL-CREATIVITY-BEFORE-COST"}
    assert expected <= set(cases)
    assert cases["CUL-CLASSICAL-NO-FORCED-WEB"]["web_policy"] == "optional"
    assert cases["CUL-TREND-CURRENT-RESEARCH"]["web_policy"] == "expected"
    assert cases["CUL-SYNTHESIS-NO-COPY"]["originality_required"] is True
    assert cases["CUL-CREATIVITY-BEFORE-COST"]["optimization_rule"] == "preserve_culinary_identity"
