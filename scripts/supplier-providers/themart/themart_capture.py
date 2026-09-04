#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The Mart Capture Tool
- Manual login by user
- Captures category/subcategory HTML pages
- Extracts best-effort product rows into CSV/XLSX
- Creates final ZIP of captured output

No credentials are requested or stored by this script.
"""

import asyncio
import csv
import json
import math
import re
import shutil
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


ROOT = Path(__file__).resolve().parent
OUT_ROOT = ROOT / "output"
USER_DATA_DIR = ROOT / ".browser_profile_themart"
CATEGORIES_FILE = ROOT / "categories.json"

PAGE_DELAY_SECONDS = 1.3
NAV_TIMEOUT_MS = 60000
MAX_RECURSION_DEPTH = 4
PRODUCTS_PER_PAGE = 60

COMMON_NON_CATEGORY_TEXTS = {
    "σύνδεση", "εγγραφή", "συχνές ερωτήσεις", "καταστήματα", "επικοινωνία",
    "λίστες", "αρχική", "προϊόντα", "μετάβαση στη λίστα προϊόντων",
    "καθαρισμός", "εφαρμογή", "δείτε τα όλα", "όλες οι κατηγορίες",
    "περισσότερες κατηγορίες", "λιγότερες κατηγορίες",
}


def safe_filename(text: str, max_len: int = 120) -> str:
    text = (text or "").strip()
    text = re.sub(r"[^\w\u0370-\u03FF\-\.\s]+", "_", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "_", text)
    text = text.strip("._-")
    return (text[:max_len] or "page")


def with_query_params(url: str, **params) -> str:
    parsed = urlparse(url)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for k, v in params.items():
        if v is None:
            q.pop(k, None)
        else:
            q[k] = str(v)
    return urlunparse(parsed._replace(query=urlencode(q)))


def root_base_path(root_url: str) -> str:
    path = urlparse(root_url).path
    if path.endswith(".html"):
        path = path[:-5]
    return path.rstrip("/")


def same_domain(url: str) -> bool:
    try:
        return urlparse(url).netloc in ("www.themart.gr", "themart.gr")
    except Exception:
        return False


def is_probable_category_url(abs_url: str, root_url: str) -> bool:
    if not same_domain(abs_url):
        return False
    parsed = urlparse(abs_url)
    path = parsed.path
    if not path.endswith(".html"):
        return False
    # Exclude query-heavy URLs, account/login, product compare, etc.
    if any(bad in path for bad in ["/customer/", "/checkout/", "/wishlist/", "/catalogsearch/"]):
        return False
    base = root_base_path(root_url)
    # Root category itself or nested category paths only.
    return path == base + ".html" or path.startswith(base + "/")


def unique_preserve(seq):
    seen = set()
    out = []
    for x in seq:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def extract_total_products(text: str) -> int:
    # Examples: "391 προϊόντα", "67 προϊόντα"
    m = re.search(r"(\d{1,6})\s+προϊόν", text, re.IGNORECASE)
    return int(m.group(1)) if m else 0


def normalize_lines(text: str):
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def extract_products_from_html(html: str, root_category: str, category_name: str, category_url: str, page_num: int):
    soup = BeautifulSoup(html, "html.parser")
    products = []

    # Magento/Luma-like product cards.
    cards = soup.select("li.product-item, div.product-item-info")
    if not cards:
        # Fallback: try elements that include product-item-link.
        link_parents = []
        for a in soup.select("a.product-item-link"):
            parent = a
            for _ in range(5):
                if parent and parent.name not in ("body", "html"):
                    if parent.get("class") and any("product" in c for c in parent.get("class", [])):
                        break
                    parent = parent.parent
            if parent:
                link_parents.append(parent)
        cards = link_parents

    for card in cards:
        raw_text = card.get_text("\n", strip=True)
        lines = normalize_lines(raw_text)

        # Product name.
        name_el = card.select_one("a.product-item-link")
        name = name_el.get_text(" ", strip=True) if name_el else ""
        href = urljoin(category_url, name_el.get("href")) if name_el and name_el.get("href") else ""

        if not name:
            # Fallback: choose first line that is not just SKU/label/price.
            for ln in lines:
                low = ln.lower()
                if re.fullmatch(r"\d{5,8}", ln):
                    continue
                if "τιμή" in low or "φπα" in low or "συνδεθείτε" in low or "όφελος" in low:
                    continue
                if re.search(r"[Α-Ωα-ωA-Za-z]", ln):
                    name = ln
                    break

        # SKU/product code: The Mart often shows a numeric code near card top.
        sku = ""
        for ln in lines:
            if re.fullmatch(r"\d{5,8}", ln):
                sku = ln
                break

        price_texts = []
        for el in card.select(".price"):
            price = el.get_text(" ", strip=True)
            if price:
                price_texts.append(price)
        # Fallback regex prices if .price selector not present.
        if not price_texts:
            price_texts = re.findall(r"\d{1,4}(?:[.,]\d{2})\s*€", raw_text)

        price_texts = unique_preserve(price_texts)

        # Best-effort extraction of labelled prices from raw text.
        unit_without_vat = ""
        unit_with_vat = ""
        product_with_vat = ""
        product_without_vat = ""

        joined = "\n".join(lines)
        patterns = [
            ("unit_without_vat", r"Τιμή\s*/\s*[^\\n]+χωρίς\s+ΦΠΑ\s*\n\s*(\d{1,4}(?:[.,]\d{2})\s*€)"),
            ("unit_with_vat", r"Τιμή\s*/\s*[^\\n]+με\s+ΦΠΑ\s*\n\s*(\d{1,4}(?:[.,]\d{2})\s*€)"),
            ("product_with_vat", r"Προϊόν\s+με\s+ΦΠΑ\s*\n\s*(\d{1,4}(?:[.,]\d{2})\s*€)"),
        ]
        for key, pattern in patterns:
            mm = re.search(pattern, joined, re.IGNORECASE)
            if mm:
                if key == "unit_without_vat":
                    unit_without_vat = mm.group(1)
                elif key == "unit_with_vat":
                    unit_with_vat = mm.group(1)
                elif key == "product_with_vat":
                    product_with_vat = mm.group(1)

        # Some cards show final net price as "X χωρίς ΦΠΑ".
        m_net = re.search(r"(\d{1,4}(?:[.,]\d{2})\s*€)\s+χωρίς\s+ΦΠΑ", raw_text, re.IGNORECASE)
        if m_net:
            product_without_vat = m_net.group(1)

        if name or sku or price_texts:
            products.append({
                "root_category": root_category,
                "category_name": category_name,
                "category_url": category_url,
                "page_num": page_num,
                "sku": sku,
                "product_name": name,
                "product_url": href,
                "unit_price_without_vat": unit_without_vat,
                "unit_price_with_vat": unit_with_vat,
                "product_price_without_vat": product_without_vat,
                "product_price_with_vat": product_with_vat,
                "all_prices_detected": " | ".join(price_texts),
                "raw_card_text": raw_text[:3000],
                "captured_at": datetime.now().isoformat(timespec="seconds"),
            })

    # Deduplicate per SKU/name/url/page.
    seen = set()
    deduped = []
    for p in products:
        key = (p.get("sku"), p.get("product_name"), p.get("product_url"), p.get("category_url"), p.get("page_num"))
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped


async def get_page_text(page) -> str:
    try:
        return await page.locator("body").inner_text(timeout=10000)
    except Exception:
        return ""


async def discover_subcategory_links(page, current_url: str, root_url: str):
    anchors = await page.evaluate("""() => Array.from(document.querySelectorAll('a[href]')).map(a => ({
        text: (a.innerText || a.textContent || '').trim(),
        href: a.href
    }))""")
    links = []
    for a in anchors:
        text = re.sub(r"\s+", " ", (a.get("text") or "").strip())
        href = a.get("href") or ""
        if not text:
            continue
        if text.lower() in COMMON_NON_CATEGORY_TEXTS:
            continue
        if not is_probable_category_url(href, root_url):
            continue
        # Avoid adding the current URL repeatedly.
        if urlparse(href)._replace(query="", fragment="").geturl() == urlparse(current_url)._replace(query="", fragment="").geturl():
            continue
        links.append((text, urlparse(href)._replace(query="", fragment="").geturl()))

    # Deduplicate by URL.
    out = []
    seen = set()
    for text, href in links:
        if href not in seen:
            seen.add(href)
            out.append({"name": text, "url": href})
    return out


async def wait_for_loaded(page):
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT_MS)
    except PlaywrightTimeoutError:
        pass
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except PlaywrightTimeoutError:
        pass


async def navigate_with_retry(page, url: str, retries: int = 3):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
            await wait_for_loaded(page)
            return
        except Exception as exc:
            last_error = exc
            if "interrupted by another navigation" not in str(exc) or attempt == retries:
                raise
            await wait_for_loaded(page)
            await page.wait_for_timeout(1500)
    raise last_error


async def capture_category(page, root_category, category_name, category_url, root_url, html_dir):
    rows = []
    page_records = []

    first_url = with_query_params(category_url, product_list_limit=PRODUCTS_PER_PAGE, p=1)
    print(f"\n[CAPTURE] {root_category} > {category_name}")
    print(f"          {first_url}")

    await navigate_with_retry(page, first_url)
    await page.wait_for_timeout(int(PAGE_DELAY_SECONDS * 1000))

    text = await get_page_text(page)
    total_products = extract_total_products(text)
    pages = max(1, math.ceil(total_products / PRODUCTS_PER_PAGE)) if total_products else 1

    # Cap very high accidental loops, but allow large categories.
    pages = min(pages, 100)

    # Discover subcategories from the first page.
    subcats = await discover_subcategory_links(page, category_url, root_url)

    for pnum in range(1, pages + 1):
        url = with_query_params(category_url, product_list_limit=PRODUCTS_PER_PAGE, p=pnum)
        if pnum > 1:
            await navigate_with_retry(page, url)
            await page.wait_for_timeout(int(PAGE_DELAY_SECONDS * 1000))

        html = await page.content()
        title = ""
        try:
            title = await page.title()
        except Exception:
            title = category_name

        fn = f"{safe_filename(root_category)}__{safe_filename(category_name)}__page_{pnum:03d}.html"
        fpath = html_dir / fn
        fpath.write_text(html, encoding="utf-8")

        extracted = extract_products_from_html(html, root_category, category_name, url, pnum)
        rows.extend(extracted)

        page_records.append({
            "root_category": root_category,
            "category_name": category_name,
            "url": url,
            "page_num": pnum,
            "total_products_reported": total_products,
            "pages_reported": pages,
            "html_file": str(fpath.relative_to(html_dir.parent)),
            "title": title,
            "captured_at": datetime.now().isoformat(timespec="seconds"),
        })

        print(f"          page {pnum}/{pages}: {len(extracted)} product rows")

    return rows, page_records, subcats


async def main():
    OUT_ROOT.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUT_ROOT / f"themart_capture_{stamp}"
    html_dir = out_dir / "pages_html"
    index_dir = out_dir / "indexes"
    html_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

    with CATEGORIES_FILE.open("r", encoding="utf-8") as f:
        root_categories = json.load(f)

    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1440, "height": 1200},
            accept_downloads=True,
        )
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(NAV_TIMEOUT_MS)

        print("\nΆνοιξε ο browser.")
        print("1) Κάνε σύνδεση στο https://www.themart.gr/")
        print("2) Βεβαιώσου ότι βλέπεις τιμές προϊόντων.")
        print("3) Γύρνα εδώ και πάτα ENTER για να ξεκινήσει το capture.\n")

        await navigate_with_retry(page, "https://www.themart.gr/customer/account/login/")
        input("Πάτα ENTER αφού ολοκληρώσεις τη σύνδεση και βλέπεις τιμές... ")
        await wait_for_loaded(page)
        await page.wait_for_timeout(3000)

        all_rows = []
        all_pages = []
        visited_categories = set()
        queue = []

        for cat in root_categories:
            queue.append({
                "root_category": cat["name"],
                "name": cat["name"],
                "url": cat["url"],
                "root_url": cat["url"],
                "depth": 0,
            })

        while queue:
            item = queue.pop(0)
            clean_url = urlparse(item["url"])._replace(query="", fragment="").geturl()
            key = (item["root_category"], clean_url)
            if key in visited_categories:
                continue
            visited_categories.add(key)

            try:
                rows, pages, subcats = await capture_category(
                    page=page,
                    root_category=item["root_category"],
                    category_name=item["name"],
                    category_url=clean_url,
                    root_url=item["root_url"],
                    html_dir=html_dir,
                )
                all_rows.extend(rows)
                all_pages.extend(pages)

                if item["depth"] < MAX_RECURSION_DEPTH:
                    for s in subcats:
                        skey = (item["root_category"], urlparse(s["url"])._replace(query="", fragment="").geturl())
                        if skey not in visited_categories:
                            queue.append({
                                "root_category": item["root_category"],
                                "name": s["name"],
                                "url": s["url"],
                                "root_url": item["root_url"],
                                "depth": item["depth"] + 1,
                            })
            except Exception as exc:
                print(f"[WARN] Failed category: {item['root_category']} > {item['name']} | {clean_url}")
                print(f"       {type(exc).__name__}: {exc}")
                all_pages.append({
                    "root_category": item["root_category"],
                    "category_name": item["name"],
                    "url": clean_url,
                    "page_num": "",
                    "total_products_reported": "",
                    "pages_reported": "",
                    "html_file": "",
                    "title": "",
                    "captured_at": datetime.now().isoformat(timespec="seconds"),
                    "error": f"{type(exc).__name__}: {exc}",
                })

        await context.close()

    products_csv = index_dir / "products_raw.csv"
    products_xlsx = index_dir / "products_raw.xlsx"
    pages_csv = index_dir / "captured_pages.csv"

    df_products = pd.DataFrame(all_rows)
    df_pages = pd.DataFrame(all_pages)

    df_products.to_csv(products_csv, index=False, encoding="utf-8-sig")
    df_pages.to_csv(pages_csv, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(products_xlsx, engine="openpyxl") as writer:
        df_products.to_excel(writer, sheet_name="products_raw", index=False)
        df_pages.to_excel(writer, sheet_name="captured_pages", index=False)

    summary = [
        f"The Mart capture completed: {datetime.now().isoformat(timespec='seconds')}",
        f"Captured category/page records: {len(all_pages)}",
        f"Extracted product rows: {len(all_rows)}",
        "",
        "Files:",
        f"- {products_csv.relative_to(out_dir)}",
        f"- {products_xlsx.relative_to(out_dir)}",
        f"- {pages_csv.relative_to(out_dir)}",
        "- pages_html/*.html",
        "",
        "Note: This is raw extraction from logged-in HTML. Review price columns before using for costing.",
    ]
    (out_dir / "capture_summary.txt").write_text("\n".join(summary), encoding="utf-8")

    zip_path = OUT_ROOT / f"{out_dir.name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", root_dir=out_dir)

    print("\nDONE")
    print(f"Output folder: {out_dir}")
    print(f"Result ZIP:    {zip_path}")
    print(f"Product rows:  {len(all_rows)}")


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        print("Python 3.9+ is required.")
        raise SystemExit(1)
    asyncio.run(main())
