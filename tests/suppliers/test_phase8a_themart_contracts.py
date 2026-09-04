from pathlib import Path
import json
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / "scripts/supplier-providers/themart"
SCHEMA = ROOT / "schemas/supplier_price_snapshot.schema.json"
ENV_EXAMPLE = ROOT / ".env.example"
SKILL = ROOT / "skills/supplier-procurement-intelligence/SKILL.md"
RUNTIME_REQUIREMENTS = PROVIDER / "requirements-runtime.txt"


def read(path: Path) -> str:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def test_supplier_snapshot_schema_is_valid_and_carries_provenance_freshness_and_warnings():
    schema = json.loads(read(SCHEMA))
    Draft202012Validator.check_schema(schema)
    text = json.dumps(schema)
    for token in [
        "provider", "captured_at", "sku", "product_name", "pack", "unit",
        "price_net", "price_gross", "vat_rate", "vat_status", "unit_price",
        "source_reference", "evidence_state", "confidence", "parsing_warnings",
        "raw_capture_reference", "freshness_state",
    ]:
        assert token in text
    assert "APPROVED" not in schema.get("properties", {}).get("evidence_state", {}).get("enum", [])


def test_migration_manifest_uses_explicit_allowlist_and_denies_sensitive_archive_content():
    manifest = yaml.safe_load(read(PROVIDER / "migration_manifest.yaml"))
    allow = set(manifest["safe_source_allowlist"])
    assert "themart_capture.py" in allow
    assert "themart_extract_existing_html.py" in allow
    assert "categories.json" in allow
    denied = "\n".join(manifest["deny_patterns"]).lower()
    for token in [".browser_profile_themart", "cookies", ".venv", "__pycache__", "output", ".git"]:
        assert token in denied
    assert manifest["exact_source_migration_state"] == "MIGRATED_EXACT_SOURCE_VERIFIED"
    assert manifest["provenance_manifest"] == "scripts/supplier-providers/themart/source_provenance.yaml"
    assert manifest["reconstruction_from_memory_forbidden"] is True


def test_provider_contract_is_explicit_on_demand_and_local_profile_only():
    contract = yaml.safe_load(read(PROVIDER / "provider_contract.yaml"))
    assert contract["execution_mode"] == "explicit_user_request_only"
    assert contract["background_monitoring"] is False
    assert contract["browser_profile"]["environment_variable"] == "THEMART_BROWSER_PROFILE_DIR"
    assert contract["browser_profile"]["repository_storage"] == "forbidden"
    assert contract["credentials"]["collection_by_provider"] is False
    assert contract["credentials"]["repository_storage"] == "forbidden"
    assert contract["output_root"]["environment_variable"] == "THEMART_OUTPUT_DIR"
    assert contract["output_root"]["repository_storage"] == "forbidden"


def test_env_example_names_profile_variable_without_real_secret_or_path():
    text = read(ENV_EXAMPLE)
    assert "THEMART_BROWSER_PROFILE_DIR=" in text
    line = next(line for line in text.splitlines() if line.startswith("THEMART_BROWSER_PROFILE_DIR="))
    assert line == "THEMART_BROWSER_PROFILE_DIR="
    output_line = next(line for line in text.splitlines() if line.startswith("THEMART_OUTPUT_DIR="))
    assert output_line == "THEMART_OUTPUT_DIR="
    assert "password" not in text.lower()
    assert "cookie" not in text.lower()


def test_runtime_requirements_preserve_original_pins_and_add_audited_playwright_dependency():
    text = read(RUNTIME_REQUIREMENTS)
    assert text.splitlines() == ["-r requirements.txt", "playwright==1.49.1"]


def test_runbook_preserves_manual_login_privacy_and_snapshot_fallback():
    text = read(PROVIDER / "RUNBOOK_GR.md").lower()
    for term in ["χειροκίνη", "δικό του λογαριασμό", "δεν αποθηκεύ", "browser profile", "ρητό αίτημα", "validated snapshot"]:
        assert term in text
    assert "background" in text


def test_recovery_regression_contract_preserves_known_protections():
    data = yaml.safe_load(read(PROVIDER / "recovery_regressions.yaml"))
    ids = {case["id"] for case in data["cases"]}
    required = {
        "no_cross_product_price_bleed",
        "correct_product_url_association",
        "spreadsheet_formula_injection_protection",
        "local_path_privacy_sanitization",
        "strict_zero_extraction_failure",
        "deterministic_fixture_normalization",
        "multi_sku_product_url_not_guessed",
    }
    assert required.issubset(ids)


def test_category_scope_records_all_twelve_audited_root_categories():
    data = yaml.safe_load(read(PROVIDER / "category_scope.yaml"))
    categories = data["root_categories"]
    assert len(categories) == 12
    joined = " ".join(item["label"].lower() for item in categories)
    for term in ["fruit", "fish", "dairy", "butcher", "frozen", "bakery", "plant", "soft drinks", "wine"]:
        assert term in joined


def test_supplier_skill_is_wired_to_provider_contract_and_snapshot_schema():
    text = read(SKILL)
    assert "scripts/supplier-providers/themart/provider_contract.yaml" in text
    assert "schemas/supplier_price_snapshot.schema.json" in text
    assert "THEMART_BROWSER_PROFILE_DIR" in text
    assert "scripts/supplier-providers/themart/provider_adapter.py" in text
    assert "scripts/verify_themart_source_provenance.py" in text
    assert "explicit user request" in text.lower()
