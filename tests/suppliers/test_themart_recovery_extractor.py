#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from pathlib import Path
import sys


PROVIDER = Path(__file__).resolve().parents[2] / "scripts/supplier-providers/themart"
sys.path.insert(0, str(PROVIDER))

from themart_extract_existing_html import (
    extract_by_text_fallback,
    parse_product_block,
    PRODUCT_COLUMNS,
    EURO_RE,
)

def test_integer_price_and_name_before_sku():
    meta = {"root_category": "Παντοπωλείο", "category_name": "Test", "page_num": 1, "html_file": "test.html"}
    text = """
    Product A
    11111
    Τιμή / τεμάχιο χωρίς ΦΠΑ
    1 €
    Τιμή / τεμάχιο με ΦΠΑ
    1,24 €
    """
    rows = parse_product_block(text, meta)
    assert len(rows) == 1
    assert rows[0]["sku"] == "11111"
    assert rows[0]["product_name"] == "Product A"
    assert rows[0]["unit_price_without_vat"] == "1 €"

def test_multi_sku_prices_do_not_bleed():
    meta = {"root_category": "Παντοπωλείο", "category_name": "Test", "page_num": 1, "html_file": "test.html"}
    text = """
    Product A
    11111
    Τιμή / τεμάχιο χωρίς ΦΠΑ
    1 €
    Τιμή / τεμάχιο με ΦΠΑ
    1,24 €

    Product B
    22222
    Τιμή / τεμάχιο χωρίς ΦΠΑ
    2 €
    Τιμή / τεμάχιο με ΦΠΑ
    2,48 €
    """
    rows = parse_product_block(text, meta)
    assert len(rows) == 2
    assert rows[0]["sku"] == "11111"
    assert rows[0]["unit_price_without_vat"] == "1 €"
    assert rows[1]["sku"] == "22222"
    assert rows[1]["unit_price_without_vat"] == "2 €"
    assert rows[1]["unit_price_with_vat"] == "2,48 €"

def test_static_columns_exist_for_empty_export():
    assert "product_name" in PRODUCT_COLUMNS
    assert EURO_RE.search("1 €")


def test_spreadsheet_formula_escape():
    from themart_extract_existing_html import escape_spreadsheet_cell
    assert escape_spreadsheet_cell("=HYPERLINK(\"x\")") == "'=HYPERLINK(\"x\")"
    assert escape_spreadsheet_cell("+1") == "'+1"
    assert escape_spreadsheet_cell("-1") == "'-1"
    assert escape_spreadsheet_cell("@cmd") == "'@cmd"
    assert escape_spreadsheet_cell("normal") == "normal"

def test_no_body_url_fallback():
    from themart_extract_existing_html import find_page_url
    html = "<html><body>https://example.com/product</body></html>"
    assert find_page_url(BeautifulSoup(html, "html.parser")) == ""


def test_strict_arg_parse():
    from themart_extract_existing_html import parse_args
    args = parse_args(["--strict", "some_capture_dir"])
    assert args.strict is True
    assert args.capture_dir == "some_capture_dir"
