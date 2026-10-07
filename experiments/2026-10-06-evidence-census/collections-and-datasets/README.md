# Collections and datasets census

The focused pass on 7 October 2026 documents **114 inscription-confirmed original records**: New Delhi 76, Kolkata 18, British Museum 6, Penn 5, Louvre 4 and Met 5. **108 records were retrieved directly with HTTP 200; six British Museum witnesses came through the search provider while direct requests were blocked.** These are bounded minima. Complete inscription inventories remain unmeasured. [Results and bases](REPORT.md), [summary](focused-summary.json).

**61/114 inspected originals (53.51%)** join to 61 corpus families and 67 faces. Of 80 records with usable identifier keys, 61 match (76.25%). The [full audit](paired-full-audit.csv) retains every confirmed pair; the [30-object sample](paired-sample-audit.csv) is selected deterministically. Marshall's 1931 table resolves Hr 5635 / HR 5635345 as field number HR 5635 followed by plate number 345. [Join methods and disagreements](REPORT.md#identifier-audit).

The Museums of India union contains **4,007 record IDs** across seven terms. All 156 result pages and 158 candidate object pages were captured. Accession deduplication gives 94 confirmed originals, ten plaster copies and 44 candidates with unconfirmed inscriptions. Penn's complete Indus Script filter contains 34 records: five originals and 29 plaster impressions. [Candidate counts](portal-candidate-counts.csv), [counts per term](portal-term-counts.csv).

## Outputs and reproduction

The [collection register](collection-register.json) and [CSV](collection-register.csv) retain 37 rows. The [dataset register](dataset-register.json) retains 15 entries. The [field matrix](metadata-field-matrix.csv) has 52 rows; [focused field counts](focused-field-counts.csv) give record denominators. The [query log](focused-query-log.csv) records exact URLs, dates, HTTP outcomes, counts and raw-body locators for 417 direct attempts. [Sources](sources.json) distinguish direct access from provider text and failures.

Run from the repository root with Python and beautifulsoup4 available:

```powershell
python experiments/2026-10-06-evidence-census/collections-and-datasets/focused_rerun.py
```

This command recomputes the focused registers and audits from existing local witnesses without network requests. It needs the ignored raw directory and data/normalized/lipi_observed_faces.jsonl. focused_fetch.py captures a new named URL without replacing an existing response. focused_enumerate.py reuses captured portal pages. Earlier scripts and [the previous snapshot](history/2026-10-07-depth-pass/) remain available; earlier register builders would restore earlier outcomes.

The pass reused the 2 October landscape, existing Lipi CSV/export and complete CISI Volume 1 scan. Acquired pages, three Met photograph witnesses, PDFs, OCR, source rows and paired values remain under data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/. [Protocol](PROTOCOL.md), [retrospective](RETROSPECTIVE.md), [registry proposal](registry-entry.json).

Remaining work includes full inscription counts for BM, MFA, ASI site museums and Karachi, and wider inscription adjudication beyond the portal and Met candidate frames. The report gives failed routes, rights conditions and reviewer checks beside the affected results. [Changed-path manifest](CHANGES.json).
