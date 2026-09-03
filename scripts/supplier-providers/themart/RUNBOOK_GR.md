# The Mart Provider — Runbook

## Σκοπός

Ο provider συλλέγει/ανακτά supplier price evidence από The Mart για επαγγελματική χρήση του ιδιοκτήτη με **δικό του λογαριασμό**. Δεν αποτελεί αυτόματη υπηρεσία παρακολούθησης και δεν μετατρέπει extracted τιμές σε εγκεκριμένα master data.

## Εκτέλεση

Η live capture εκτελείται μόνο μετά από **ρητό αίτημα** του χρήστη. Το login παραμένει **χειροκίνητο** μέσα στο browser που ανοίγει ο provider. Ο provider δεν συλλέγει, δεν αποθηκεύει και δεν γράφει credentials στον κώδικα ή στο repository.

Το authenticated **browser profile** είναι local-only και ορίζεται από:

`THEMART_BROWSER_PROFILE_DIR`

Το profile, cookies/session databases, `.env`, caches, raw output και λοιπά authenticated artifacts δεν μπαίνουν ποτέ στο GitHub ή στο Skill package.

## Freshness

Κάθε supplier snapshot χρειάζεται `captured_at` και `freshness_state`. Αν δεν είναι διαθέσιμη live εκτέλεση, το Skill μπορεί να χρησιμοποιήσει το πιο πρόσφατο **validated snapshot**, αλλά πρέπει να δηλώνει τη φρεσκάδα του. Παλιό snapshot δεν παρουσιάζεται ως live/current χωρίς τεκμηρίωση.

## Privacy / output

- Raw HTML παραμένει local-only όταν περιέχει ευαίσθητο operational context.
- Exported `raw_capture_reference` χρησιμοποιεί sanitized filename/opaque reference και όχι πλήρες local path.
- Data-only ZIP είναι η προτιμώμενη portable έξοδος.
- Spreadsheet values προστατεύονται από formula injection (`=`, `+`, `-`, `@`, tab, CR στην αρχή).

## Recovery extractor protections

Η exact source migration πρέπει να διατηρήσει:

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

Τα `themart_capture.py` και `themart_extract_existing_html.py` θα μεταφερθούν μόνο ως exact audited source bytes. Δεν επιτρέπεται reconstruction από μνήμη ή από αυτή την περιγραφή.
