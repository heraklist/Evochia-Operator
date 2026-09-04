#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
The Mart Recovery Extractor v5

Reads already captured HTML files from The Mart Capture Tool and creates:
- indexes/products_raw_recovered.csv
- indexes/products_raw_recovered.xlsx
- indexes/extraction_diagnostics.csv
- data-only ZIP by default

Usage:
  python themart_extract_existing_html.py
or:
  python themart_extract_existing_html.py "C:\Users\<USERNAME>\Desktop\themart_capture_tool\output\themart_capture_YYYYMMDD_HHMMSS"

Optional:
  python themart_extract_existing_html.py --include-html-zip "C:\...\themart_capture_YYYYMMDD_HHMMSS"

This script does NOT login and does NOT download pages. It only parses existing .html files.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup


PRODUCT_COLUMNS = [
    "supplier",
    "captured_at",
    "root_category",
    "category_name",
    "page_num",
    "sku",
    "product_code",
    "product_name",
    "unit",
    "unit_price_without_vat",
    "unit_price_with_vat",
    "product_price_without_vat",
    "product_price_with_vat",
    "vat_percent_guess",
    "all_prices_detected",
    "category_url",
    "product_url",
    "source_html_file",
    "raw_card_text",
]

DIAGNOSTIC_COLUMNS = [
    "html_file",
    "root_category",
    "category_name",
    "page_num",
    "rows_extracted",
    "method",
    "has_vat_text",
    "has_price_text",
    "status",
    "error",
]

SKU_RE = re.compile(r"^\s*([A-ZΑ-Ω]?\d{4,9})\s*$")
EURO_RE = re.compile(r"\d{1,5}(?:[.,]\d{1,2})?\s*€")
URL_RE = re.compile(r"https?://[^\s\"']+")

DANGEROUS_SPREADSHEET_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def escape_spreadsheet_cell(value):
    """
    Prevent spreadsheet formula injection when opening CSV/XLSX exports.
    Any string beginning with =, +, -, @, tab, or carriage return is prefixed with apostrophe.
    """
    if isinstance(value, str) and value.startswith(DANGEROUS_SPREADSHEET_PREFIXES):
        return "'" + value
    return value


def sanitize_dataframe_for_spreadsheet(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df.map(escape_spreadsheet_cell)

BAD_NAME_PARTS = {
    "προσθήκη",
    "σύνδεση",
    "εγγραφή",
    "φίλτρα",
    "χαρακτηριστικά",
    "τιμή",
    "προβολή",
    "προϊόντα",
    "κορυφαίες",
    "σε λίστα",
    "χωρίς φπα",
    "με φπα",
    "φπα",
    "διαθέσιμο",
    "μη διαθέσιμο",
    "ποσότητα",
    "τεμάχιο",
    "κιλό",
    "λίτρο",
    "pce",
}

CATEGORY_HINTS = {
    "οπωροπωλείο",
    "ιχθυοπωλείο",
    "γάλατα",
    "τυριά",
    "κρεοπωλείο",
    "κατεψυγμένα",
    "παντοπωλείο",
    "αρτοσκευάσματα",
    "πρωινό",
    "κάβα",
}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def lines_from_text(text: str) -> list[str]:
    return [clean(x) for x in (text or "").splitlines() if clean(x)]


def is_sku(line: str) -> bool:
    return bool(SKU_RE.match(line or ""))


def price_to_float(value: str) -> float | None:
    if not value:
        return None
    m = EURO_RE.search(value)
    if not m:
        return None
    raw = m.group(0).replace("€", "").strip().replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def format_vat_guess(net: str, gross: str) -> str:
    n = price_to_float(net)
    g = price_to_float(gross)
    if not n or not g or n <= 0 or g <= n:
        return ""
    vat = round((g / n - 1) * 100)
    if vat in {6, 13, 24}:
        return str(vat)
    return ""


def price_after_label(lines: list[str], must_include: list[str], must_not_include: list[str] | None = None) -> tuple[str, str]:
    must_not_include = must_not_include or []
    for i, line in enumerate(lines):
        low = line.lower()
        if all(x.lower() in low for x in must_include) and not any(x.lower() in low for x in must_not_include):
            m = EURO_RE.search(line)
            if m:
                return m.group(0), line

            for j in range(i + 1, min(i + 5, len(lines))):
                candidate = lines[j]
                candidate_low = candidate.lower()

                # Stop if the next price section has already started.
                if j > i + 1 and (
                    "τιμή /" in candidate_low
                    or "προϊόν με φπα" in candidate_low
                    or "προϊόν χωρίς φπα" in candidate_low
                ):
                    break

                m = EURO_RE.search(candidate)
                if m:
                    return m.group(0), line
    return "", ""


def unit_from_label(label: str) -> str:
    # Examples: "Τιμή / κιλό χωρίς ΦΠΑ", "Τιμή / PCE με ΦΠΑ"
    m = re.search(r"Τιμή\s*/\s*(.+?)\s+(?:χωρίς|με)\s+ΦΠΑ", label or "", re.I)
    if not m:
        return ""
    return clean(m.group(1))


def looks_like_bad_name(line: str) -> bool:
    low = (line or "").lower()
    if not line or len(line) < 2:
        return True
    if EURO_RE.search(line) or is_sku(line):
        return True
    if any(part in low for part in BAD_NAME_PARTS):
        return True
    if low in CATEGORY_HINTS:
        return True
    return False


def guess_product_name_with_index(lines: list[str], sku_index: int) -> tuple[str, int | None]:
    """
    Prefer product names near the SKU. Handles both common orders:
    - SKU before product name
    - product name before SKU
    """
    # 1) Look after SKU first.
    for idx, line in enumerate(lines[sku_index + 1: min(sku_index + 8, len(lines))], start=sku_index + 1):
        low = line.lower()
        if "τιμή /" in low or "προϊόν με" in low or "προϊόν χωρίς" in low:
            break
        if not looks_like_bad_name(line):
            return clean(line), idx

    # 2) Look before SKU for sites/cards that show title first.
    start = max(0, sku_index - 8)
    for idx in range(sku_index - 1, start - 1, -1):
        line = lines[idx]
        low = line.lower()
        if "τιμή /" in low or "προϊόν με" in low or "προϊόν χωρίς" in low:
            break
        if not looks_like_bad_name(line):
            return clean(line), idx

    return "", None


def guess_product_name(lines: list[str], sku_index: int) -> str:
    return guess_product_name_with_index(lines, sku_index)[0]


def product_context_lines(lines: list[str], sku_index: int, end: int, name_index: int | None) -> list[str]:
    """
    Keep raw debug context limited to the current product.
    If the product name is before SKU, begin at the name. Otherwise begin at SKU.
    """
    if name_index is not None and name_index < sku_index:
        return lines[name_index:end]
    return lines[sku_index:end]


def parse_product_block(block_text: str, meta: dict, page_url: str = "", product_url: str = "") -> list[dict]:
    lines = lines_from_text(block_text)
    rows = []

    sku_indexes = [(i, SKU_RE.match(line).group(1)) for i, line in enumerate(lines) if SKU_RE.match(line)]
    if not sku_indexes:
        return rows

    for idx, (i, sku) in enumerate(sku_indexes):
        end = sku_indexes[idx + 1][0] if idx + 1 < len(sku_indexes) else min(i + 55, len(lines))

        price_chunk = lines[i:end]
        price_text = "\n".join(price_chunk)

        # Require price/VAT context to avoid category/menu codes.
        if "ΦΠΑ" not in price_text and not EURO_RE.search(price_text):
            continue

        name, name_index = guess_product_name_with_index(lines, i)
        if not name:
            continue

        context_text = "\n".join(product_context_lines(lines, i, end, name_index))

        unit_price_without_vat, unit_without_label = price_after_label(price_chunk, ["Τιμή", "χωρίς ΦΠΑ"])
        unit_price_with_vat, unit_with_label = price_after_label(price_chunk, ["Τιμή", "με ΦΠΑ"])
        product_price_without_vat, product_without_label = price_after_label(price_chunk, ["Προϊόν", "χωρίς ΦΠΑ"])
        product_price_with_vat, product_with_label = price_after_label(price_chunk, ["Προϊόν", "με ΦΠΑ"])

        all_prices = list(dict.fromkeys(EURO_RE.findall(price_text)))
        unit = unit_from_label(unit_without_label or unit_with_label)
        vat_guess = format_vat_guess(product_price_without_vat or unit_price_without_vat, product_price_with_vat or unit_price_with_vat)

        rows.append({
            "supplier": "The Mart",
            "captured_at": datetime.now().isoformat(timespec="seconds"),
            "root_category": meta.get("root_category", ""),
            "category_name": meta.get("category_name", ""),
            "page_num": meta.get("page_num", ""),
            "sku": sku,
            "product_code": sku,
            "product_name": name,
            "unit": unit,
            "unit_price_without_vat": unit_price_without_vat,
            "unit_price_with_vat": unit_price_with_vat,
            "product_price_without_vat": product_price_without_vat,
            "product_price_with_vat": product_price_with_vat,
            "vat_percent_guess": vat_guess,
            "all_prices_detected": " | ".join(all_prices),
            "category_url": page_url,
            "product_url": product_url,
            "source_html_file": meta.get("html_file", ""),
            "raw_card_text": context_text[:3000],
        })
    return rows


def parse_meta_from_filename(path: Path) -> dict:
    stem = path.stem
    parts = stem.split("__")
    root_category = parts[0] if len(parts) >= 1 else ""
    category_name = parts[1] if len(parts) >= 2 else ""
    page_num = ""
    m = re.search(r"page[_\s-]*(\d+)", stem, re.I)
    if m:
        page_num = int(m.group(1))
    return {
        "root_category": root_category.replace("_", " "),
        "category_name": category_name.replace("_", " "),
        "page_num": page_num,
        "html_file": path.name,  # Avoid local path leakage in CSV/XLSX exports.
    }


def find_page_url(soup: BeautifulSoup) -> str:
    canonical = soup.select_one('link[rel="canonical"]')
    if canonical and canonical.get("href"):
        return canonical["href"]
    og = soup.select_one('meta[property="og:url"]')
    if og and og.get("content"):
        return og["content"]
    # Do not fallback to arbitrary URLs from body text; those may be product/account URLs.
    return ""


def extract_by_dom_cards(soup: BeautifulSoup, meta: dict) -> list[dict]:
    page_url = find_page_url(soup)
    rows = []
    seen_card_keys = set()

    # Look for SKU text nodes, then climb to a plausible card ancestor.
    for node in soup.find_all(string=True):
        txt = clean(str(node))
        if not SKU_RE.match(txt):
            continue

        chosen = None
        for parent in getattr(node, "parents", []):
            if not getattr(parent, "get_text", None):
                continue
            parent_text = parent.get_text("\n", strip=True)
            if ("ΦΠΑ" in parent_text or "Τιμή /" in parent_text or EURO_RE.search(parent_text)) and len(parent_text) < 6000:
                sku_count = len([ln for ln in lines_from_text(parent_text) if is_sku(ln)])
                if sku_count <= 4:
                    chosen = parent
                    break

        if chosen is None:
            continue

        card_text = chosen.get_text("\n", strip=True)
        sku_count_in_card = len([ln for ln in lines_from_text(card_text) if is_sku(ln)])

        card_key = (txt, card_text[:500])
        if card_key in seen_card_keys:
            continue
        seen_card_keys.add(card_key)

        # If the card contains multiple SKUs, do not assign the first href to all rows.
        # Blank URL is safer than wrong URL for pricing data.
        link = ""
        if sku_count_in_card == 1:
            a = chosen.select_one("a[href]")
            if a and a.get("href"):
                link = urljoin(page_url, a.get("href"))

        rows.extend(parse_product_block(card_text, meta, page_url=page_url, product_url=link))

    return rows


def extract_by_text_fallback(soup: BeautifulSoup, meta: dict) -> list[dict]:
    page_url = find_page_url(soup)
    body = soup.body.get_text("\n", strip=True) if soup.body else soup.get_text("\n", strip=True)
    return parse_product_block(body, meta, page_url=page_url, product_url="")


def dedupe(rows: list[dict]) -> list[dict]:
    out = []
    seen = set()
    for r in rows:
        key = (
            r.get("sku", ""),
            r.get("product_name", ""),
            r.get("unit_price_without_vat", ""),
            r.get("unit_price_with_vat", ""),
            r.get("product_price_without_vat", ""),
            r.get("product_price_with_vat", ""),
            r.get("source_html_file", ""),
        )
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def find_capture_dir() -> Path:
    cwd = Path.cwd()
    candidates = []
    for p in [cwd, cwd / "output"]:
        if p.exists():
            candidates += [x for x in p.glob("themart_capture_*") if x.is_dir()]
    if not candidates:
        raise SystemExit("Δεν βρέθηκε φάκελος themart_capture_*. Δώσε path ως όρισμα στο script.")
    candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return candidates[0]


def read_html(path: Path) -> str:
    # Prefer explicit utf-8. Replacement is safer than ignore because it preserves length and signals corruption.
    return path.read_text(encoding="utf-8", errors="replace")


def create_data_only_zip(capture_dir: Path, files: list[Path]) -> Path:
    zip_target = capture_dir.parent / f"{capture_dir.name}_recovered_indexes_only.zip"
    if zip_target.exists():
        zip_target.unlink()

    with zipfile.ZipFile(zip_target, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for file_path in files:
            if file_path.exists():
                z.write(file_path, file_path.relative_to(capture_dir))
    return zip_target


def create_full_zip(capture_dir: Path) -> Path:
    zip_target = capture_dir.parent / f"{capture_dir.name}_with_recovered_excel_AND_HTML.zip"
    if zip_target.exists():
        zip_target.unlink()
    shutil.make_archive(str(zip_target.with_suffix("")), "zip", root_dir=capture_dir)
    return zip_target


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract products/prices from existing The Mart saved HTML.")
    parser.add_argument(
        "capture_dir",
        nargs="?",
        help="Path to output/themart_capture_YYYYMMDD_HHMMSS. If omitted, the newest local capture folder is used.",
    )
    parser.add_argument(
        "--include-html-zip",
        action="store_true",
        help="Also create a full ZIP including raw saved HTML. Default ZIP contains only recovered indexes/summary.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 2 if HTML files were scanned but zero product rows were extracted.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    capture_dir = Path(args.capture_dir).expanduser().resolve() if args.capture_dir else find_capture_dir()
    pages_dir = capture_dir / "pages_html"
    if not pages_dir.exists():
        raise SystemExit(f"Δεν βρέθηκε pages_html εδώ: {pages_dir}")

    index_dir = capture_dir / "indexes"
    index_dir.mkdir(exist_ok=True)

    html_files = sorted(pages_dir.glob("*.html"))
    all_rows: list[dict] = []
    diagnostics: list[dict] = []

    for path in html_files:
        meta = parse_meta_from_filename(path)
        try:
            html = read_html(path)
            soup = BeautifulSoup(html, "html.parser")
            full_text = soup.get_text(" ", strip=True)

            rows = extract_by_dom_cards(soup, meta)
            method = "dom_cards"

            if not rows:
                rows = extract_by_text_fallback(soup, meta)
                method = "text_fallback"

            rows = dedupe(rows)
            all_rows.extend(rows)

            diagnostics.append({
                "html_file": path.name,
                "root_category": meta.get("root_category", ""),
                "category_name": meta.get("category_name", ""),
                "page_num": meta.get("page_num", ""),
                "rows_extracted": len(rows),
                "method": method,
                "has_vat_text": "ΦΠΑ" in full_text,
                "has_price_text": bool(EURO_RE.search(full_text)),
                "status": "ok" if rows else "no_rows",
                "error": "",
            })
            print(f"{len(rows):4d} rows | {path.name}")
        except Exception as exc:
            diagnostics.append({
                "html_file": path.name,
                "root_category": meta.get("root_category", ""),
                "category_name": meta.get("category_name", ""),
                "page_num": meta.get("page_num", ""),
                "rows_extracted": 0,
                "method": "",
                "has_vat_text": "",
                "has_price_text": "",
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
            })
            print(f"ERR  | {path.name} | {exc}")

    all_rows = dedupe(all_rows)

    products_csv = index_dir / "products_raw_recovered.csv"
    products_xlsx = index_dir / "products_raw_recovered.xlsx"
    diagnostics_csv = index_dir / "extraction_diagnostics.csv"

    df = pd.DataFrame(all_rows, columns=PRODUCT_COLUMNS)
    diag = pd.DataFrame(diagnostics, columns=DIAGNOSTIC_COLUMNS)

    df_export = sanitize_dataframe_for_spreadsheet(df)
    diag_export = sanitize_dataframe_for_spreadsheet(diag)

    df_export.to_csv(products_csv, index=False, encoding="utf-8-sig")
    diag_export.to_csv(diagnostics_csv, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(products_xlsx, engine="openpyxl") as writer:
        df_export.to_excel(writer, sheet_name="products_raw_recovered", index=False)
        diag_export.to_excel(writer, sheet_name="diagnostics", index=False)

    summary = capture_dir / "recovery_extraction_summary.txt"
    summary.write_text(
        "\n".join([
            f"Recovery extraction completed: {datetime.now().isoformat(timespec='seconds')}",
            f"Capture folder: {capture_dir.name}",
            f"HTML files scanned: {len(html_files)}",
            f"Product rows extracted: {len(all_rows)}",
            f"CSV: indexes/{products_csv.name}",
            f"XLSX: indexes/{products_xlsx.name}",
            f"Diagnostics: indexes/{diagnostics_csv.name}",
            "",
            "Diagnostics status values:",
            "- ok: product rows extracted",
            "- no_rows: file parsed but no product rows found",
            "- error: file could not be parsed",
            "",
            "Privacy note:",
            "The default recovery ZIP contains only sanitized recovered indexes and summary files, not raw saved HTML.",
            "Use --include-html-zip only if you explicitly need a full archive with HTML.",
        ]),
        encoding="utf-8",
    )

    data_zip = create_data_only_zip(capture_dir, [products_csv, products_xlsx, diagnostics_csv, summary])

    full_zip = None
    if args.include_html_zip:
        full_zip = create_full_zip(capture_dir)

    print("\nDONE RECOVERY")
    print(f"HTML files scanned:      {len(html_files)}")
    print(f"Product rows extracted:  {len(all_rows)}")
    print(f"CSV:                     {products_csv}")
    print(f"XLSX:                    {products_xlsx}")
    print(f"Diagnostics:             {diagnostics_csv}")
    print(f"Data-only ZIP:           {data_zip}")
    if full_zip:
        print(f"Full ZIP with HTML:      {full_zip}")

    if args.strict and html_files and len(all_rows) == 0:
        print("STRICT MODE: HTML files were scanned, but zero product rows were extracted.")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
