# The Mart Recovery Extractor v5

Διορθωμένη έκδοση μετά το audit του v3.

## Τι διορθώνει

- Spreadsheet formula injection protection: πεδία που αρχίζουν με `=`, `+`, `-`, `@`, tab ή carriage return γίνονται ασφαλή για Excel/LibreOffice.
- `find_page_url()` δεν παίρνει πλέον τυχαίο URL από body text ως fallback.
- Το `raw_card_text` σε multi-SKU block περιορίζεται καλύτερα στο τρέχον προϊόν.
- Multi-SKU bug: το δεύτερο προϊόν δεν παίρνει πλέον τις τιμές του προηγούμενου.
- Product URL safety: αν ένα DOM block περιέχει πολλά SKU, το `product_url` μένει κενό αντί να μπει λάθος link.
- Local path privacy: στο CSV/XLSX γράφεται μόνο το όνομα του HTML αρχείου, όχι `C:\Users\...`.
- Το default ZIP είναι πλέον data-only και δεν περιλαμβάνει raw saved HTML.
- Δεν περιέχει `__pycache__`.
- Κρατά τις διορθώσεις του v2:
  - compile-safe raw docstring
  - τιμές τύπου `1 €`
  - σταθερό schema/headers
  - product name πριν από SKU
  - `requirements.txt`

## Αρχεία

- `themart_extract_existing_html.py`
- `requirements.txt`
- `README_HOTFIX_GR.md`
- `test_recovery_extractor.py`

## Πού το βάζεις

Βάλε τα αρχεία:

```text
themart_extract_existing_html.py
requirements.txt
```

μέσα στον φάκελο:

```text
Desktop\themart_capture_tool
```

## Πώς το τρέχεις

Άνοιξε terminal στον φάκελο `Desktop\themart_capture_tool` και τρέξε:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
python themart_extract_existing_html.py "C:\Users\<USERNAME>\Desktop\themart_capture_tool\output\themart_capture_20260628_110215"
```

Αν είσαι ήδη μέσα στο `Desktop\themart_capture_tool`, μπορείς και απλά:

```bat
python themart_extract_existing_html.py
```

## Τι θα δημιουργήσει

```text
output\themart_capture_YYYYMMDD_HHMMSS\indexes\products_raw_recovered.csv
output\themart_capture_YYYYMMDD_HHMMSS\indexes\products_raw_recovered.xlsx
output\themart_capture_YYYYMMDD_HHMMSS\indexes\extraction_diagnostics.csv
output\themart_capture_YYYYMMDD_HHMMSS_recovered_indexes_only.zip
```

## Strict mode για έλεγχο

Προαιρετικά, μπορείς να βάλεις `--strict` ώστε το script να επιστρέψει exit code `2` όταν βρει HTML files αλλά εξάγει 0 προϊόντα:

```bat
python themart_extract_existing_html.py --strict "C:\Users\<USERNAME>\Desktop\themart_capture_tool\output\themart_capture_20260628_110215"
```

Χρήσιμο για automation ή όταν θέλεις να ξέρεις άμεσα ότι η εξαγωγή απέτυχε.

## Αν χρειάζεσαι και τα raw HTML μέσα σε ZIP

Default δεν τα βάζει στο ZIP για privacy. Αν τα χρειάζεσαι ρητά, τρέξε:

```bat
python themart_extract_existing_html.py --include-html-zip "C:\Users\<USERNAME>\Desktop\themart_capture_tool\output\themart_capture_20260628_110215"
```

Θα δημιουργήσει επιπλέον:

```text
themart_capture_YYYYMMDD_HHMMSS_with_recovered_excel_AND_HTML.zip
```

## Σημαντικό

Δεν κάνει login και δεν ξανακατεβάζει σελίδες. Δουλεύει μόνο πάνω στα HTML που έχουν ήδη αποθηκευτεί.
