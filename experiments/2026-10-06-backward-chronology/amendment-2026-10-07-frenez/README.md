# Frenez chronology amendment, 7 October 2026

The early record is better documented after this follow-up, while the longest internal gap remains **1300–700 BCE, 600 years**, for A/B evidence with high or moderate calendar strength. The amended inventory has **54 rows, 44 source records, 17 attributed continuity claims and 33 century bins**. It adds five dated assemblages and **193 reported sherds/specimens with exact counts**. These totals and the unchanged gaps are in [run-01/summary.json](run-01/summary.json), fields `inventory_rows`, `dated_additive_rows_in_window` and `gaps`, and [comparison-01/comparison.json](comparison-01/comparison.json), fields `added_distinct_reported_exact_objects` and `unchanged_gap_series`.

The 12 appended rows cover Mehrgarh/Nausharo marks and firing contexts, Rehman Dheri sherds and its disputed rectangular object, Harappa pottery/seals/sealing, and western contact examples. [REPORT.md](REPORT.md) gives the source findings. The full amended [JSON](evidence-table.json) and [CSV](evidence-table.csv) retain all 42 original rows unchanged. [Added rows](added-rows.json), [dating details](dating-details.json), [eight lecture claims](lecture-claim-audit.json) and [five contact case records](contact-items.json) provide the specimen and claim audits. The contact selection contains four illustrated seals and a separate abstract-only cohort of three Bahrain tokens.

All **477 pre-existing Package E files** remain byte-for-byte unchanged. The [baseline check](comparison-01/baseline-verification.json) records their hashes. Documentary assessments are Exploratory; coverage arithmetic is Verified computation; [test designs](TEST-DESIGNS.md) are Proposed. No new specimen-to-radiocarbon association received grade A.

## Reuse and access

Reused the parent protocol, row/source/claim records, run 03 and coverage code, the October 2 South India witnesses, and the [external phonetic-anchor audit](../../../research/literature/external_phonetic_anchor_audit.md). Correctly identified local Gadd, Possehl, Frenez chapter and CV witnesses were read again without changing them. New acquisitions and OCR remain under `data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/`. [sources.json](sources.json) distinguishes opened publications, caption/abstract/catalogue access, search snippets and cited but unopened originals. [search-log.json](search-log.json) records the initial 21 search batches; the subsequent `web-22.json` bibliography check is preserved in the local raw directory and final path manifest. Quivron's complete 1980 paper was recovered through 12 public page images after its direct PDF returned 403.

The original Quivron 1997 chapter, original firing-batch registers, a direct Harappa sealing-to-carbon-sample join and the final forthcoming hybrid-seal paper remain unrecovered. Rehman Dheri catalogue 54 has conflicting layer/phase assignments. These issues have separate fields in the evidence and lecture audits.

## Reproduction from the repository root

Use fresh output names for every run. The builder, coverage and comparison scripts use Python's standard library. Acquisition additionally uses `requests`, Beautiful Soup, PyMuPDF and optional Tesseract. No installation is needed in the current environment.

```powershell
python experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/build_amendment.py --output experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/reviewer-inputs-01
python experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/analyze_coverage.py --output experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/reviewer-run-01
python experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/compare_coverage.py --run experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/run-01 --reproduction experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/reviewer-run-01 --output experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/reviewer-comparison-01
python experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/make_audits.py --output experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/reviewer-audits-01
python tools/review_prose.py --path experiments/2026-10-06-backward-chronology --no-write
```

The builder's regenerated evidence, sources, claims and CSV should match the files here. `make_audits.py` also rescans the raw search directory, so its search log includes queries acquired after `audits-01`. It does not change coverage inputs. `acquire_sources.py` preserves download/processing witnesses under new identifiers; `recover_persee.py` refuses to replace an existing recovered-page directory. Temporary library locations are under the local raw directory.

The completed [reproduction check](comparison-01/comparison.json), field `reproduction`, compares all six coverage output files byte-for-byte. [run verification](run-01/verification.json) checks 38 local source hashes, 54 CSV/JSON rows and seven estimator fixtures. [Century coverage](comparison-01/COVERAGE.md) and [coverage deltas](comparison-01/coverage-deltas.csv) show the new counts. The proposed [registry entry](registry-entry.json) is ready for coordinator review. The [final path manifest](final-manifest.json) enumerates every new owned and local raw path; shared files were not edited.
