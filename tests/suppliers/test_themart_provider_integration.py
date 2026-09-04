from __future__ import annotations

import ast
import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / "scripts/supplier-providers/themart"
ADAPTER = PROVIDER / "provider_adapter.py"
CAPTURE = PROVIDER / "themart_capture.py"
SCHEMA = ROOT / "schemas/supplier_price_snapshot.schema.json"


def _load_adapter():
    assert ADAPTER.is_file(), "missing repository compatibility adapter"
    spec = importlib.util.spec_from_file_location("themart_provider_adapter", ADAPTER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runtime_paths_require_an_explicit_local_profile_outside_the_repository(tmp_path):
    adapter = _load_adapter()

    with pytest.raises(adapter.ProviderConfigurationError, match="THEMART_BROWSER_PROFILE_DIR"):
        adapter.resolve_runtime_paths(ROOT, {})

    with pytest.raises(adapter.ProviderConfigurationError, match="outside the repository"):
        adapter.resolve_runtime_paths(
            ROOT,
            {"THEMART_BROWSER_PROFILE_DIR": str(ROOT / "local-profile")},
        )

    profile = tmp_path / "profile"
    paths = adapter.resolve_runtime_paths(
        ROOT,
        {"THEMART_BROWSER_PROFILE_DIR": str(profile)},
    )
    assert paths.browser_profile == profile.resolve()
    assert paths.output_root == (tmp_path / "themart_capture_output").resolve()


def test_runtime_paths_allow_an_explicit_local_output_outside_the_repository(tmp_path):
    adapter = _load_adapter()
    profile = tmp_path / "profile"
    output = tmp_path / "snapshots"

    paths = adapter.resolve_runtime_paths(
        ROOT,
        {
            "THEMART_BROWSER_PROFILE_DIR": str(profile),
            "THEMART_OUTPUT_DIR": str(output),
        },
    )

    assert paths.browser_profile == profile.resolve()
    assert paths.output_root == output.resolve()


def test_capture_module_receives_only_resolved_external_runtime_paths(tmp_path):
    adapter = _load_adapter()
    paths = adapter.resolve_runtime_paths(
        ROOT,
        {"THEMART_BROWSER_PROFILE_DIR": str(tmp_path / "profile")},
    )

    class CaptureModule:
        USER_DATA_DIR = None
        OUT_ROOT = None

    capture_module = CaptureModule()
    adapter.configure_capture_module(capture_module, paths)

    assert capture_module.USER_DATA_DIR == paths.browser_profile
    assert capture_module.OUT_ROOT == paths.output_root / ".themart_capture_staging"


def test_prepare_capture_module_configures_the_exact_source_without_launching_browser(tmp_path):
    adapter = _load_adapter()

    capture_module, paths = adapter.prepare_capture_module(
        ROOT,
        {"THEMART_BROWSER_PROFILE_DIR": str(tmp_path / "profile")},
    )

    assert Path(capture_module.__file__).resolve() == CAPTURE.resolve()
    assert capture_module.USER_DATA_DIR == paths.browser_profile
    assert capture_module.OUT_ROOT == paths.output_root / ".themart_capture_staging"


def test_complete_recovered_row_normalizes_to_the_existing_snapshot_schema():
    adapter = _load_adapter()
    row = {
        "supplier": "The Mart",
        "captured_at": "2026-09-04T09:30:00+03:00",
        "root_category": "Παντοπωλείο",
        "category_name": "Ρύζι",
        "page_num": "2",
        "sku": "12345",
        "product_code": "SKU-12345",
        "product_name": "Ρύζι επαγγελματικό",
        "pack_description": "10 kg",
        "unit": "kg",
        "unit_price_without_vat": "2,50 €",
        "unit_price_with_vat": "2,825 €",
        "product_price_without_vat": "25,00 €",
        "product_price_with_vat": "28,25 €",
        "vat_percent_guess": "13.00%",
        "category_url": "https://www.themart.gr/pantry/rice.html",
        "product_url": "https://www.themart.gr/product/rice.html",
        "source_html_file": r"C:\Users\owner\private\pantry__rice__page_002.html",
    }

    record = adapter.normalize_recovered_row(row, freshness_state="CURRENT_SNAPSHOT")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(record)

    assert record == {
        "provider": "themart",
        "captured_at": "2026-09-04T09:30:00+03:00",
        "root_category": "Παντοπωλείο",
        "category_name": "Ρύζι",
        "page_num": 2,
        "sku": "12345",
        "product_code": "SKU-12345",
        "product_name": "Ρύζι επαγγελματικό",
        "pack": "10 kg",
        "unit": "kg",
        "price_net": 25.0,
        "price_gross": 28.25,
        "vat_rate": 0.13,
        "vat_status": "INFERRED",
        "unit_price": 2.5,
        "unit_price_basis": "NET",
        "source_reference": "https://www.themart.gr/product/rice.html",
        "product_url": "https://www.themart.gr/product/rice.html",
        "category_url": "https://www.themart.gr/pantry/rice.html",
        "evidence_state": "NORMALIZED",
        "confidence": "HIGH",
        "freshness_state": "CURRENT_SNAPSHOT",
        "parsing_warnings": [],
        "raw_capture_reference": "pantry__rice__page_002.html",
    }


@pytest.mark.parametrize(
    "local_source_path",
    [
        r"C:\Users\owner\private\page_001.html",
        r"D:\different-owner\capture\page_001.html",
        "/home/owner/private/page_001.html",
        r"mixed\private/path/page_001.html",
    ],
)
def test_normalized_local_source_reference_is_platform_independent_basename(local_source_path):
    adapter = _load_adapter()
    record = adapter.normalize_recovered_row(
        {
            "captured_at": "2026-09-04T09:30:00+03:00",
            "product_name": "Product A",
            "source_html_file": local_source_path,
        },
        freshness_state="CURRENT_SNAPSHOT",
    )

    assert record["raw_capture_reference"] == "page_001.html"
    assert record["source_reference"] == "page_001.html"


def test_incomplete_row_stays_evidence_needs_review_without_inventing_values():
    adapter = _load_adapter()
    row = {
        "captured_at": "2026-09-04T09:30:00+03:00",
        "product_name": "Ambiguous product",
        "unit": "",
        "all_prices_detected": "9,99 €",
        "source_html_file": "page.html",
    }

    record = adapter.normalize_recovered_row(row, freshness_state="UNKNOWN")

    assert record["evidence_state"] == "NEEDS_REVIEW"
    assert record["confidence"] == "LOW"
    assert record["unit"] == "UNKNOWN"
    assert record["vat_status"] == "UNKNOWN"
    assert record["price_net"] is None
    assert record["price_gross"] is None
    assert record["unit_price"] is None
    assert "unit_missing" in record["parsing_warnings"]
    assert "pack_missing" in record["parsing_warnings"]
    assert "price_fields_missing" in record["parsing_warnings"]
    assert "vat_status_unknown" in record["parsing_warnings"]
    assert "APPROVED" not in record["evidence_state"]


def test_normalizer_rejects_missing_product_identity_instead_of_inventing_it():
    adapter = _load_adapter()

    with pytest.raises(ValueError, match="product_name"):
        adapter.normalize_recovered_row(
            {"captured_at": "2026-09-04T09:30:00+03:00", "unit": "kg"},
            freshness_state="STALE",
        )


def test_recovered_csv_normalizes_to_jsonl_without_local_path_leakage(tmp_path):
    adapter = _load_adapter()
    source = tmp_path / "products_raw_recovered.csv"
    destination = tmp_path / "supplier_snapshot.jsonl"
    fieldnames = [
        "captured_at",
        "product_name",
        "pack_description",
        "unit",
        "unit_price_without_vat",
        "vat_percent_guess",
        "product_url",
        "source_html_file",
    ]
    with source.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "captured_at": "2026-09-04T09:30:00+03:00",
                "product_name": "Product A",
                "pack_description": "1 kg",
                "unit": "kg",
                "unit_price_without_vat": "3,25 €",
                "vat_percent_guess": "13%",
                "product_url": "https://www.themart.gr/product-a.html",
                "source_html_file": r"C:\private\capture\page_001.html",
            }
        )

    count = adapter.normalize_recovered_csv(
        source,
        destination,
        freshness_state="CURRENT_SNAPSHOT",
    )
    records = [json.loads(line) for line in destination.read_text(encoding="utf-8").splitlines()]

    assert count == 1
    assert records[0]["raw_capture_reference"] == "page_001.html"
    assert "C:\\private" not in destination.read_text(encoding="utf-8")
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(records[0])


def test_cli_normalizes_recovered_csv_without_live_capture(tmp_path):
    source = tmp_path / "products.csv"
    destination = tmp_path / "snapshot.jsonl"
    source.write_text(
        "captured_at,product_name,pack_description,unit,unit_price_without_vat,vat_percent_guess,source_html_file\n"
        '2026-09-04T09:30:00+03:00,Product A,1 kg,kg,"3,25 €",13%,page.html\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ADAPTER),
            "normalize",
            str(source),
            str(destination),
            "--freshness-state",
            "CURRENT_SNAPSHOT",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert destination.is_file()
    assert "Normalized supplier evidence rows: 1" in result.stdout


def test_cli_prepare_only_validates_configuration_without_creating_runtime_state(tmp_path):
    profile = tmp_path / "profile"
    env = os.environ.copy()
    env["THEMART_BROWSER_PROFILE_DIR"] = str(profile)

    result = subprocess.run(
        [sys.executable, str(ADAPTER), "capture", "--prepare-only"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "The Mart live capture configuration: READY" in result.stdout
    assert not profile.exists()
    assert not (tmp_path / "themart_capture_output").exists()


def test_exact_capture_preserves_manual_login_and_foreground_only_boundary():
    tree = ast.parse(CAPTURE.read_text(encoding="utf-8"))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert any(isinstance(call.func, ast.Name) and call.func.id == "input" for call in calls)
    assert any(
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "launch_persistent_context"
        and any(keyword.arg == "headless" and isinstance(keyword.value, ast.Constant) and keyword.value.value is False for keyword in call.keywords)
        for call in calls
    )
    assert not imported_names.intersection({"schedule", "apscheduler", "celery"})
