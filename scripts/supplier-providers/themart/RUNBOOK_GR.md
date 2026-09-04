# The Mart Provider — Runbook

## Σκοπός

Ο provider συλλέγει/ανακτά supplier price evidence από The Mart για επαγγελματική χρήση του ιδιοκτήτη με **δικό του λογαριασμό**. Δεν αποτελεί αυτόματη υπηρεσία παρακολούθησης και δεν μετατρέπει extracted τιμές σε εγκεκριμένα master data.

## Εκτέλεση

Η live capture εκτελείται μόνο μετά από **ρητό αίτημα** του χρήστη. Το login παραμένει **χειροκίνητο** μέσα στο browser που ανοίγει ο provider. Ο provider δεν συλλέγει, δεν αποθηκεύει και δεν γράφει credentials στον κώδικα ή στο repository.

Το authenticated **browser profile** είναι local-only και ορίζεται από:

`THEMART_BROWSER_PROFILE_DIR`

Προαιρετικά, το local-only output root ορίζεται από `THEMART_OUTPUT_DIR`. Αν μείνει κενό, ο compatibility adapter χρησιμοποιεί φάκελο `themart_capture_output` δίπλα στο browser profile. Και τα δύο paths πρέπει να είναι absolute και εκτός repository.

Το profile, cookies/session databases, `.env`, caches, raw output και λοιπά authenticated artifacts δεν μπαίνουν ποτέ στο GitHub ή στο Skill package.

### Repository-safe εκτέλεση

Τα canonical `themart_capture.py` και `themart_extract_existing_html.py` παραμένουν exact audited source bytes. Μην εκτελείς το historical `run_windows.bat` μέσα από repository checkout, επειδή διατηρεί το αρχικό relative profile/output behavior μόνο ως provenance evidence.

Εγκατάστησε τις provider dependencies σε virtual environment **εκτός repository**:

```text
python -m pip install -r scripts/supplier-providers/themart/requirements-runtime.txt
python -m playwright install chromium
```

Έλεγξε τη local-only configuration χωρίς browser ή δημιουργία runtime state:

```text
python scripts/supplier-providers/themart/provider_adapter.py capture --prepare-only
```

Μόνο μετά από ρητό αίτημα για live refresh, εκτέλεσε foreground capture:

```text
python scripts/supplier-providers/themart/provider_adapter.py capture
```

Το browser παραμένει ορατό και το login γίνεται χειροκίνητα. Ο adapter εφαρμόζει τα external paths στα globals του exact module χωρίς να τροποποιεί τα canonical source bytes.

### Supported output boundary

Η παραπάνω εντολή adapter είναι η μοναδική supported live-capture διαδρομή του provider. Η απευθείας εκτέλεση των historical `themart_capture.py`, `themart_extract_existing_html.py` ή `run_windows.bat` δεν αποτελεί supported provider execution/output και δεν πρέπει να χρησιμοποιείται από το `supplier-procurement-intelligence` Skill ή από wrapper/CLI.

Η supported διαδρομή είναι fail-closed:

1. Το exact capture γράφει προσωρινά στο local-only `.themart_capture_staging`.
2. Ο adapter εκτελεί υποχρεωτικά το exact recovery hardening.
3. Ελέγχει κάθε cell των `products_raw_recovered.csv`, `products_raw_recovered.xlsx` και `extraction_diagnostics.csv` για leading `=`, `+`, `-`, `@`, tab ή CR.
4. Δημιουργεί το normalized `supplier_snapshot.jsonl` και δημοσιεύει μόνο το hardened capture directory και το `*_recovered_indexes_only.zip`.
5. Διαγράφει πριν από publication τα historical `products_raw.csv`, `products_raw.xlsx`, `captured_pages.csv`, `capture_summary.txt` και το raw full-capture ZIP.

Αν recovery, formula scan ή destination validation αποτύχει, δεν δημοσιεύεται supported output και η εντολή αποτυγχάνει. Δεν υπάρχει CLI flag ή wrapper option που να παρακάμπτει αυτό το boundary. Τυχόν staging artifacts αποτυχημένης εκτέλεσης είναι unsupported diagnostic state και η επόμενη εκτέλεση αρνείται να συνεχίσει μέχρι να γίνει ελεγχόμενο local cleanup.

## Freshness

Κάθε supplier snapshot χρειάζεται `captured_at` και `freshness_state`. Αν δεν είναι διαθέσιμη live εκτέλεση, το Skill μπορεί να χρησιμοποιήσει το πιο πρόσφατο **validated snapshot**, αλλά πρέπει να δηλώνει τη φρεσκάδα του. Παλιό snapshot δεν παρουσιάζεται ως live/current χωρίς τεκμηρίωση.

Για ήδη validated historical recovery input, η ξεχωριστή normalization εντολή είναι:

```text
python scripts/supplier-providers/themart/provider_adapter.py normalize <products_raw_recovered.csv> <supplier_snapshot.jsonl> --freshness-state CURRENT_SNAPSHOT
```

Χρησιμοποίησε `STALE` ή `UNKNOWN` όταν αυτό ανταποκρίνεται στην πραγματική κατάσταση. Το JSONL περιέχει supplier evidence· δεν αποτελεί approved master data.

## Privacy / output

- Raw HTML παραμένει local-only όταν περιέχει ευαίσθητο operational context.
- Exported `raw_capture_reference` χρησιμοποιεί sanitized filename/opaque reference και όχι πλήρες local path.
- Data-only ZIP είναι η προτιμώμενη portable έξοδος.
- Spreadsheet values προστατεύονται από formula injection (`=`, `+`, `-`, `@`, tab, CR στην αρχή).
- Τα raw historical spreadsheets διατηρούνται byte-for-byte μόνο ως source limitation/provenance behavior. Δεν είναι supported production output και δεν περνούν το publication boundary.

## Recovery extractor protections

Η exact source migration διατηρεί:

- isolation τιμής ανά προϊόν/SKU,
- σωστή association προϊόντος ↔ URL,
- καμία αυθαίρετη body-level URL fallback,
- blank product URL όταν multi-SKU block δεν επιτρέπει ασφαλή αντιστοίχιση,
- local-path sanitization,
- strict failure όταν υπάρχει HTML αλλά εξάγονται μηδέν προϊόντα,
- deterministic normalization σε fixtures.

## Background behavior

**Background monitoring: disabled.** Δεν γίνεται αυτόματο login, scheduled capture ή περιοδικό scraping. Refresh γίνεται μόνο με explicit execution request.

## Phase 8B note

Τα `themart_capture.py` και `themart_extract_existing_html.py` έχουν μεταφερθεί ως exact audited source bytes. Το `source_provenance.yaml` και το `scripts/verify_themart_source_provenance.py` είναι το fail-closed checksum gate. Δεν επιτρέπεται reconstruction, formatting ή inline refactor των canonical files.

Το `requirements-runtime.txt` είναι companion runtime artifact και όχι μέρος των original exact bytes. Το pin `playwright==1.49.1` αντιστοιχεί στην έκδοση που βρέθηκε στο owner-local virtual environment του αρχικού `themart_capture_tool` με Python 3.12.13. Το exact source εισάγει `playwright.async_api` και το audited owner-local environment εκθέτει επιτυχώς αυτό το API. Το audit evidence καταγράφεται στο `dependency_evidence.yaml`; repository scan δεν βρήκε δεύτερη ή conflicting Playwright version declaration.
