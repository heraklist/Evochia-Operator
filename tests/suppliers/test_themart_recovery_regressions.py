from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys

from bs4 import BeautifulSoup
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / "scripts/supplier-providers/themart"
EXTRACTOR_PATH = PROVIDER / "themart_extract_existing_html.py"
ADAPTER_PATH = PROVIDER / "provider_adapter.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_dangerous_spreadsheet_prefixes_are_neutralized():
    extractor = _load(EXTRACTOR_PATH, "themart_exact_extractor_formula")

    for prefix in ("=", "+", "-", "@", "\t", "\r"):
        value = prefix + "payload"
        assert extractor.escape_spreadsheet_cell(value) == "'" + value
    assert extractor.escape_spreadsheet_cell("safe payload") == "safe payload"


def test_single_sku_card_keeps_its_own_product_url():
    extractor = _load(EXTRACTOR_PATH, "themart_exact_extractor_single_url")
    html = """
    <html><head><link rel="canonical" href="https://www.themart.gr/category.html"></head>
    <body><div class="product-card">
      <a href="/product-a.html">Product A</a>
      <span>11111</span>
      <span>Τιμή / τεμάχιο χωρίς ΦΠΑ</span><span>1,00 €</span>
    </div></body></html>
    """

    rows = extractor.extract_by_dom_cards(
        BeautifulSoup(html, "html.parser"),
        {"html_file": "page.html"},
    )

    assert len(rows) == 1
    assert rows[0]["sku"] == "11111"
    assert rows[0]["product_url"] == "https://www.themart.gr/product-a.html"


def test_multi_sku_card_leaves_product_urls_blank_instead_of_guessing():
    extractor = _load(EXTRACTOR_PATH, "themart_exact_extractor_multi_url")
    html = """
    <html><head><link rel="canonical" href="https://www.themart.gr/category.html"></head>
    <body><div class="product-card">
      <a href="/product-a.html">Product A</a>
      <span>11111</span><span>Τιμή / τεμάχιο χωρίς ΦΠΑ</span><span>1,00 €</span>
      <a href="/product-b.html">Product B</a>
      <span>22222</span><span>Τιμή / τεμάχιο χωρίς ΦΠΑ</span><span>2,00 €</span>
    </div></body></html>
    """

    rows = extractor.extract_by_dom_cards(
        BeautifulSoup(html, "html.parser"),
        {"html_file": "page.html"},
    )

    assert {row["sku"] for row in rows} == {"11111", "22222"}
    assert {row["product_url"] for row in rows} == {""}


def test_strict_mode_returns_two_when_html_exists_but_no_products_are_extracted(tmp_path):
    capture = tmp_path / "themart_capture_fixture"
    pages = capture / "pages_html"
    pages.mkdir(parents=True)
    (pages / "pantry__empty__page_001.html").write_text(
        "<html><body>No supplier product evidence</body></html>",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    result = subprocess.run(
        [sys.executable, str(EXTRACTOR_PATH), "--strict", str(capture)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2, result.stdout + result.stderr
    assert "STRICT MODE" in result.stdout


def test_recovered_export_uses_only_sanitized_html_filename(tmp_path):
    extractor = _load(EXTRACTOR_PATH, "themart_exact_extractor_privacy")
    capture = tmp_path / "private" / "themart_capture_fixture"
    pages = capture / "pages_html"
    pages.mkdir(parents=True)
    filename = "pantry__rice__page_001.html"
    (pages / filename).write_text(
        """
        <html><body>
        Product A
        11111
        Τιμή / τεμάχιο χωρίς ΦΠΑ
        1,00 €
        </body></html>
        """,
        encoding="utf-8",
    )

    try:
        extractor.main([str(capture)])
    except SystemExit as exc:
        assert exc.code in (None, 0)

    exported = pd.read_csv(capture / "indexes/products_raw_recovered.csv")
    assert exported.loc[0, "source_html_file"] == filename
    assert str(tmp_path) not in exported.to_csv(index=False)


def test_snapshot_normalization_is_independent_of_local_machine_path():
    adapter = _load(ADAPTER_PATH, "themart_adapter_determinism")
    common = {
        "captured_at": "2026-09-04T09:30:00+03:00",
        "product_name": "Product A",
        "pack_description": "1 kg",
        "unit": "kg",
        "unit_price_without_vat": "3,25 €",
        "vat_percent_guess": "13%",
    }

    first = adapter.normalize_recovered_row(
        {**common, "source_html_file": r"C:\owner-a\capture\page_001.html"},
        freshness_state="CURRENT_SNAPSHOT",
    )
    second = adapter.normalize_recovered_row(
        {**common, "source_html_file": r"D:\owner-b\other\page_001.html"},
        freshness_state="CURRENT_SNAPSHOT",
    )

    assert first == second
    assert first["raw_capture_reference"] == "page_001.html"
    assert first["source_reference"] == "page_001.html"
