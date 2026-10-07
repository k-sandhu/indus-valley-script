# Package E: backward chronology

This package assembled **42 evidence rows**, reviewed **18 sources**, and recorded **11 attributed continuity/origin claims** for roughly 3500–200 BCE. Nineteen rows have a selected calendar interval within the window. No recovered source supplies a dated diagnostic chain from late Indus signs to early historic writing. The full evidence record remains **Exploratory**; the coverage arithmetic and integrity checks are **Verified computation**.

The century analysis has **33 bins**. All published A+B brackets leave two one-century gaps. Restricting those links to high/moderate calendar strength leaves a longest internal gap of **600 years in whole bins, 1300–700 BCE**. The difference depends mainly on weak older absolute chronologies, particularly Rangpur. See [REPORT.md](REPORT.md) for the complete century table and source-specific limitations, and [summary.json](run-2026-10-07-03/summary.json), `gaps`, for the computed intervals.

The original Rangpur report counts **222 marked sherds**. Lal's rounded percentages are reproduced as **47/53 = 88.68%** and **47/55 = 85.45%**, using his combined Harappan/Chalcolithic comparator. Porunthal supplies **two inscribed ringstands** and uncalibrated rice determinations, **Beta-302854: 2440±30 BP** and **Beta-305904: 2400±30 BP**; no calibrated interval was reconstructed from those ages. Source rows and exact locations are in [evidence-table.json](evidence-table.json), with a [CSV copy](evidence-table.csv). Additional legacy laboratory records are keyed to those rows in [dating-details.json](dating-details.json).

[PROTOCOL.md](PROTOCOL.md) records inclusion rules and the pre-computation dating-strength refinement. [sources.json](sources.json) gives exact citations, access status and local witness hashes. [continuity-claims.json](continuity-claims.json) identifies the intermediates and missing evidence for each argument. [TEST-DESIGNS.md](TEST-DESIGNS.md) proposes four falsifiable tests and states which inputs exist locally. [RETROSPECTIVE.md](RETROSPECTIVE.md) records acquisition failures, repairs and remaining work.

## Reproduction

From the repository root, run the standard-library coverage script into a fresh directory:

```powershell
python experiments/2026-10-06-backward-chronology/analyze_coverage.py --output experiments/2026-10-06-backward-chronology/reviewer-run-NEW
```

The output directory must not already exist. The script checks CSV/JSON correspondence, source/claim references, **16 source hashes**, date selection, and **7 boundary/count fixtures**, then writes `coverage.json`, `coverage.csv`, `summary.json`, `dating-audit.json`, `regional-gaps.json` and `verification.json`. [Run 03](run-2026-10-07-03/summary.json) uses the final documentary revision. [Run 01](run-2026-10-07-01/summary.json) and its [original inputs](inputs-preserved-2026-10-07-01/evidence-table.json) are preserved. Each run's repeat produced all six files byte-for-byte; the final evidence rebuild reproduced all three input files. See [reproduction-check-03.json](reproduction-check-03.json).

The post-outcome source audit corrected one image-access flag, added unselected dating/laboratory metadata, and aligned the Ashokan reign envelope with Salomon's reported 272–232 BCE. The final count is **27 rows with verified images**, reduced from 28; every century-coverage value and gap length is unchanged. [revision-audit-03.json](revision-audit-03.json) verifies the preserved original input hashes and lists the changed fields.

To regenerate the curated table in another fresh owned directory:

```powershell
python experiments/2026-10-06-backward-chronology/build_evidence.py --output experiments/2026-10-06-backward-chronology/reviewer-evidence-NEW
```

`acquire_sources.py` preserves downloads, extraction and optional OCR/rendering in the local raw directory. Acquisition needs `requests`, `beautifulsoup4`, `PyMuPDF`, and Tesseract for OCR; those were already available. Coverage needs no additional packages. All temporary settings are directed to the owned raw `tmp` directory.

## Review targets and unresolved work

Repeat the two commands above and compare the files with the preserved inputs/endpoint. Sample Lal p. 21, Rao p. 130, Sali pp. 207–211 and 504–506, and Tamil Volume I pp. 74, 167 and 227. Check that conventional, corrected, calibrated and midpoint dates stay separate, that site counts are excluded from object totals, and that pooled catalogues are excluded from additive coverage.

The largest acquisition gaps are OCP/Copper Hoard marked inventories, joined PGW/NBPW examples, full Anuradhapura sample tables, Porunthal calibration outputs, and Tamil Nadu specimen-to-layer-to-sample joins. Adjacent Aramaic material is retained as an acquisition target; the primary Bactrian collection pages failed to open. [retrieval-audit.json](retrieval-audit.json) records **23 direct URL attempts, 9 failed/blocked downloads, 3 web failures or wrong targets**, and **17 response witnesses**. Earlier queries are preserved by topic rather than exact strings; the first search response was not retained. This limits exact search replication.

All third-party payloads, extracted pages, OCR, renders and web response witnesses remain in `data/raw/2026-10-06-backward-chronology/`. Earlier South India witnesses and reviewed results were reused without rerunning the failed/superseded stroke path. [file-manifest-final.json](file-manifest-final.json) lists every created package/raw file. [registry-entry.json](registry-entry.json) is a proposed entry; shared repository files were not edited.
