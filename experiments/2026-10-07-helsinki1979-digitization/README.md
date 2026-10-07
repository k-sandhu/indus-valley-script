# Package M: Helsinki 1979 digitization

**First endpoint:** 60 numbered-section rows from PDF pages 31–79, drawn from 3,460 of 11,369 detected occurrences; no sorted-section row was evaluated. In that frame the frozen pipeline has 33/60 matching counts, 23/60 exact numbers and 24/60 top-five compatible whole rows. It fails all four criteria. The corrected [report](REPORT.md) gives the per-annotator crop labels, objective audit, adjudication overlays and orientation findings.

**Repair status:** method and 80 predictions are frozen across the whole edition (28 numbered, 26 end-sorted, 26 beginning-sorted). Two independent readings, source-count adjudication and new metrics remain pending after the disk cutoff. All 11,369 original occurrences remain quarantined. The active triage subset has 9,584 rows and flags all 1,223 inverted occurrences. The original frozen files and references are unchanged.

## Main files

- [Original protocol and dated amendments](PROTOCOL.md).
- [Original 60-row metrics](evaluation/2026-10-07-frozen-v1/metrics.json), `summary`; the frame above qualifies every accuracy figure.
- [Original full coverage](runs/2026-10-07-full-v1/coverage.json): 159 attempted pages, 11,369 occurrences, 57,426 candidates.
- [Corrections and adjudication](follow-up/2026-10-07/analysis-v1/adjudication-overlay.json); [crop audit restatement](follow-up/2026-10-07/analysis-v1/crop-and-frame.json).
- [Active triage](follow-up/2026-10-07/analysis-v1/triage-queue.jsonl); [orientation flags](follow-up/2026-10-07/analysis-v1/orientation-overlay.json); [row-recall evidence](follow-up/2026-10-07/analysis-v1/row-recall-evidence.json).
- [Upright-only calibration sensitivity](follow-up/2026-10-07/analysis-v1/calibration-upright-only.json): 126 units in the original numbered-section frame, Brier 0.1262 and ten-bin error 0.1183.
- [Repaired freeze](repair/2026-10-07-v2/freeze-manifest.json), [prediction freeze](repair/2026-10-07-v2/prediction-freeze.json), [source-only locator](repair/2026-10-07-v2/blind/selection.json) and [reading conventions](repair/2026-10-07-v2/blind/CONVENTIONS.md).
- [Disk stop and exact remaining work](follow-up/2026-10-07/storage-stop-v2.json), [retrospective](RETROSPECTIVE.md), [registry proposal](registry-entry.json), [source register](sources.json) and [import contract](IMPORT_INTERFACE.md).

## Portable first evaluation

The coordinator must apply every path in [TRACK-EXCEPTIONS.txt](TRACK-EXCEPTIONS.txt), including the digit NPZ and images. The exact owned prediction copy and image hashes are in [portable-input-manifest.json](follow-up/2026-10-07/analysis-v1/portable-input-manifest.json). JSON references and frozen code are already owned. The evaluator hash is in a [dated supplement](follow-up/2026-10-07/analysis-v1/freeze-supplement.json); the original freeze manifests remain unchanged. The portable command uses only NumPy and no original PDF, GPU, model inference or local raw predictions. [requirements.txt](requirements.txt) pins NumPy 2.5.3. The original recognition replay additionally needs the acquired PDF, PyTorch and recorded environment.

Run from the repository root with a fresh output directory:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/portable_evaluate.py --out experiments/2026-10-07-helsinki1979-digitization/review/reviewer-portable-v3
```

Both local portable replays reproduce the original metrics byte-for-byte. Recompute corrections with `respond_to_review.py --out <new-owned-directory>` and the L check with `check_ledger_followup.py --out <new-owned-file>`; these need the preserved local full extraction and reviewer diagnostics. They preserve the first endpoint. `write_docs.py` now delegates to `write_followup_docs.py` for the corrected prose.

## Resume the repaired evaluation

Use the existing v2 freeze and source-only sample; do not regenerate it over the endpoint. Assign two independent readers every row and count page under the convention sheet, then a third reader the disagreements without predictions. Required final reference files are `repair/2026-10-07-v2/blind/adjudicated-reference.json` and `adjudicated-counts.json`. Preserve both initial readings and the adjudication. Only then run:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate_repair.py --out experiments/2026-10-07-helsinki1979-digitization/review/repaired-evaluation-v1
```

`prepare_repair_v2.py` created the replacement code once; it is a historical construction helper and must not be rerun over frozen files. `freeze_repair_v2.py` refuses existing freeze/prediction endpoints. A methodological repair after reference requires a separate dated freeze and new sample.

Before any operation writing more than 50 MB, check free space **inside the active process immediately before serialization**, after library/model loading. If below 1,000,000,000 bytes, stop and record unfinished work. A caller-only check proved inadequate during this run. Render source pages one at a time in memory. The repaired full run and confidence-based release are unfinished. Package L still requires a reviewed carrier concordance and occurrence-surface alignment.

## Attribution and reviewer checks

Source-derived crops, chart cards and transcription: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki; [handle](http://hdl.handle.net/10138/342677), [institutional licence](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Changes are raster cropping, card arrangement, numerical recognition and source annotation. The 1980 copied table rows and images remain local because their licence is unverified. This source licence does not assign a blanket licence to our code.

- Check ignored-asset exceptions and run portable evaluation from a checkout without local raw predictions.
- Confirm every first-endpoint hash against the preservation check, and that references still carry the original labels.
- Inspect the eleven adjudication entries and high/centered tick convention in untrimmed chart cells.
- Verify the 1,223 orientation flags, subset triage and the source-count limits on pages 62,129,130.
- Complete the two blinded readings and adjudication before opening repaired predictions for scoring.
- Confirm suffixes and occurrence segments pass L's schema while unsupported joins stay quarantined.
- Run `python tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write`.
