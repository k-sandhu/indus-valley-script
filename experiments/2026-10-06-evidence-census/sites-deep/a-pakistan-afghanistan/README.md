# Pakistan and Afghanistan site census

The revised exploratory census contains **37 label rows** and **36 site entities** after joining the catalogue aliases Gharo Bhiro and Nuhato. Every row has at least 3 distinct new live queries and an opened source. The merged ledgers contain 375 search or inspection records and 669 source records, including historical leads and unsuccessful access. The revision added 247 live search runs. See [site-rows.json](site-rows.json), [site-rows.csv](site-rows.csv), [searches.json](searches.json) and [sources.json](sources.json).

Final excavation monographs are identified for 8 sites and final exploration publications for 5. A full final-report scan was inspected for 1 site, Chanhu-daro. Reports for 5 further rows have unresolved final or comprehensive status. No dated inscription discovery was established after a verified latest site-specific CISI cutoff. These publication and later-find bases are explained in [REPORT.md](REPORT.md).

Mahadevan 1977 pages 6–7 provide a matched historical total of **2,596 included inscribed objects across seven sites**. Their local rows contain **4,732 faces, 3,805 object families and 3,565 distinct CISI identifiers**. The historical and current inventories differ in date and selection. Across all 31 matched local labels, the coordinator aggregate sums to **4,837 faces, 3,908 families and 3,637 identifiers**. See [site-count-comparison.json](site-count-comparison.json), [aggregate.json](aggregate.json) and each row’s `local_corpus`.

## Reproduce

From the repository root, run:

```powershell
python experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/make_discovery_row.py
python experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/build_revision.py
python experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/write_revision_reports.py
python experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/repair_active_text.py
python tools/review_prose.py --path experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan --no-write
python experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/inventory_outputs.py
```

`build_revision.py` reads the revision files and the existing local coverage aggregate. It makes no network requests. The CSV has one row per label; nested fields are UTF-8 JSON strings in CSV cells. The first-pass assembler `build_site_rows.py` is retained as a superseded record and must not be used to regenerate the revised census. Acquisition commands are in [acquire_common_sources.py](acquire_common_sources.py) and [inspect_common_pdf.py](inspect_common_pdf.py); dependencies used were requests, PyMuPDF, pypdf and the local Tesseract executable. No installation was performed. Regional helper code is preserved under [research-code](research-code/README.md).

## Preserved evidence and access

All 25 original files were copied byte for byte into [first-pass](first-pass/) before revision. [preservation.json](preservation.json) gives archive hashes. [PROTOCOL.md](PROTOCOL.md) records the dated amendments. [RETROSPECTIVE.md](RETROSPECTIVE.md) records corrections, reuse and failures. New source PDFs, HTML, OCR and page images remain under this package’s local raw directory. Public downloads did not establish image redistribution rights.

New nearby labels and their inclusion trails are recorded in the `discovery` fields and [discovery-candidates.json](discovery-candidates.json). The full list of created or changed paths is [created-paths.json](created-paths.json). Mechanical reference, query and CSV checks are in [revision-audit.json](revision-audit.json); these do not verify archaeological interpretations.
