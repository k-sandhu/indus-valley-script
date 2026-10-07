# Package M: Helsinki 1979 digitization

Both frozen endpoints fail their release criteria. **First frame: 60 numbered-section rows, PDF31–79**, sampled from 3,460/11,369 detected occurrences; no sorted-section row was evaluated. **Repaired frame: 80 rows across numbered, end-sorted and beginning-sorted sections (28/26/26)**, excluding development pages and the old targets. The reference and sampling differences make the comparison descriptive.

| Outcome, 95% interval | First: 60 numbered rows, PDF31–79 | Repaired: 80 rows, three sections |
|---|---|---|
| Crop acceptance | 23/60 (38.3%; 27.1–51.0%) | 44/80 (55.0%; 44.1–65.4%) |
| Drawing-unit count | 33/60 (55.0%; 42.5–66.9%) | 59/80 (73.8%; 63.2–82.1%) |
| Inscription number, including suffix | 23/60 (38.3%; 27.1–51.0%) | 62/80 (77.5%; 67.2–85.3%) |
| Five-position classification | 19/60 (31.7%; 21.3–44.2%) | 55/80 (68.8%; 57.9–77.8%) |
| Compatible whole row, top one | 13/60 (21.7%; 13.1–33.6%) | 20/80 (25.0%; 16.8–35.5%) |
| Compatible whole row, top five | 24/60 (40.0%; 28.6–52.6%) | 40/80 (50.0%; 39.3–60.7%) |
| Exact sequence, singleton-reference subset | 10/52 (19.2%; 10.8–31.9%) | 19/66 (28.8%; 19.3–40.6%) |

Intervals are the stored 95% Wilson intervals. The [report](REPORT.md) gives unit recall and calibration, source-count intervals and the stage diagnosis. Original frozen code, predictions, references and metrics are unchanged.

The repaired count evaluation finds **1,242/1,286 random-page rows (96.6%; pooled 95% interval 95.4–97.4%; page-bootstrap 90.5–100.0%)**, with **1,242/1,242 precision (100%; pooled interval 99.7–100.0%)**, across 18 pages. Stress pages 62,129,130 yield **561/561 recall and precision (100%; 99.3–100.0%)**. Only the row-recall criterion passes; four fail. [Metrics](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), `source_row_recall`, `negative_result_criteria`.

Of 40 top-five whole-row failures in the repaired 80-row frame, 34 first fail crops, three unit counts, two underline-window association and one graphic proposal classification after source/window inspection. Number reading also fails in 18/80 and classification reading in 25/80. All **11,369** provisional occurrences stay quarantined, including the 1,785 outside the 9,584-row triage queue. A release needs a newly validated automatic rule or a separately validated human-plus-AI review route and adjudication; object imports additionally need identity/surface concordances.

## Main files and review workload

- [Protocol and dated recording amendment](PROTOCOL.md), [findings](REPORT.md), [process and cost](RETROSPECTIVE.md), [registry proposal](registry-entry.json), [source register](sources.json), [import contract](IMPORT_INTERFACE.md).
- [Frozen repaired metrics](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), [freeze](repair/2026-10-07-v2/freeze-manifest.json), [prediction freeze](repair/2026-10-07-v2/prediction-freeze.json).
- [Reader A](repair/2026-10-07-v2/blind/reader-a/rows-part1.json), [reader B](repair/2026-10-07-v2/blind/reader-b/rows-part1.json), their part-2/count files in the same folders, [adjudicated rows](repair/2026-10-07-v2/blind/adjudicated-reference.json), [counts](repair/2026-10-07-v2/blind/adjudicated-counts.json), [decision notes](repair/2026-10-07-v2/blind/adjudication-notes.json).
- [Machine-readable diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), [unit-window audit](follow-up/2026-10-07/endpoint-record-v1/unit-window-audit.json), [workload](follow-up/2026-10-07/endpoint-record-v1/review-workload.json), [preservation hashes](follow-up/2026-10-07/endpoint-record-v1/preservation-check.json).
- [Original coverage](runs/2026-10-07-full-v1/coverage.json), [triage](follow-up/2026-10-07/analysis-v1/triage-queue.jsonl), [orientation overlay](follow-up/2026-10-07/analysis-v1/orientation-overlay.json), [first-reference adjudication overlay](follow-up/2026-10-07/analysis-v1/adjudication-overlay.json).

Reviewing 11,369 provisional occurrences requires at least that many human checks and independent AI checks. At assumed human times of one/two/five minutes per row, the human pass takes 189.5/379.0/947.4 hours, excluding adjudication and missing-row recovery. The recorded AI task timing projects 272.6 summed task hours for one pass. Reader disagreements project about 2,132 adjudication rows from 15/80 measured rows; a human/AI rate is unmeasured. Monetary cost is unknown without usage/billing records. These are Exploratory planning estimates with distinct source/task frames, detailed in `review-workload.json`.

## Portable first evaluation

The coordinator must apply every path in [TRACK-EXCEPTIONS.txt](TRACK-EXCEPTIONS.txt), including the digit NPZ and images. The exact owned prediction copy and image hashes are in [portable-input-manifest.json](follow-up/2026-10-07/analysis-v1/portable-input-manifest.json). JSON references and frozen code are already owned. The evaluator hash is in a [dated supplement](follow-up/2026-10-07/analysis-v1/freeze-supplement.json); the original freeze manifests remain unchanged. The portable command uses only NumPy and no original PDF, GPU, model inference or local raw predictions. [requirements.txt](requirements.txt) pins NumPy 2.5.3. The original recognition replay additionally needs the acquired PDF, PyTorch and recorded environment.

Run from the repository root with a fresh output directory:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/portable_evaluate.py --out experiments/2026-10-07-helsinki1979-digitization/review/reviewer-portable-v3
```

Both local portable replays reproduce the original metrics byte-for-byte. Recompute corrections with `respond_to_review.py --out <new-owned-directory>` and the L check with `check_ledger_followup.py --out <new-owned-file>`; these need the preserved local full extraction and reviewer diagnostics. They preserve the first endpoint. `write_docs.py` now delegates to `write_followup_docs.py` for the corrected prose.

## Reproduce the repaired record

Run from the repository root, with fresh output paths:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/record_repaired_endpoint.py --out experiments/2026-10-07-helsinki1979-digitization/review/repaired-record-repeat
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/audit_repaired_unit_windows.py --out experiments/2026-10-07-helsinki1979-digitization/review/unit-window-repeat.json
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate_repair.py --out experiments/2026-10-07-helsinki1979-digitization/review/repaired-evaluation-repeat
```

The recorder uses the standard library; the frozen evaluator needs NumPy and the retained reference, prediction and frame inputs. Unit-window observations are a post-outcome visual audit encoded in the audit script; rerunning it verifies inputs/calculations and does not replace source inspection. `write_docs.py` and `write_followup_docs.py` now delegate to `write_repaired_endpoint_docs.py`, which reads the preserved pre-record prose and current aggregates.

Do not rerun the construction/sampling helpers over either frozen endpoint. A future large-write gate must run inside the active process after library/model loading. Stop below 1,000,000,000 bytes free before writes over 50 MB. No full repaired extraction or release was run in this recording task. The prior disk-stop artifact remains historical evidence.

## Attribution and reviewer checks

Source-derived crops, chart cards and transcription: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki; [handle](http://hdl.handle.net/10138/342677), [institutional licence](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Changes are raster cropping, card arrangement, numerical recognition and source annotation. The 1980 copied table rows and images remain local because their licence is unverified. This source licence does not assign a blanket licence to our code.

- Rerun the frozen evaluator into a new directory and compare the complete metrics, ignoring no outcome fields.
- Verify both endpoint hashes, all six initial reader files and adjudication; inspect the disclosed scratchpad/directory-list deviations in reader notes.
- Reproduce the stage partitions; visually inspect exact rows 3,25,50,52,58,72 against the frozen unit windows.
- Check page 66/112 recall misses and the 52 source column counts, including continuation exclusions.
- Verify workload arithmetic and supply missing billing/adjudicator-time records before reporting money or total project effort.
- Confirm zero releases and preserve L's concordance requirements.
- Run `python tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write`.
