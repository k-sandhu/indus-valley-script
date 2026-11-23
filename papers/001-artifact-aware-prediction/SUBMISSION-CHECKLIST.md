# Preprint and submission checklist for Paper 001

Date: 23 November 2026. Companion to [manuscript.md](manuscript.md), [methods.md](methods.md), [claim-evidence-map.md](claim-evidence-map.md) and the original 2 October 2026 [submission-gaps.md](submission-gaps.md).

## Completed scientific repairs since 2 October 2026

- [x] **Full-corpus transitive alias isolation (Split 2, Q-0010 / Issue #19):** Rebuilt transitive components across all 5,680 observed faces (`data/normalized/lipi_observed_faces.jsonl`), eliminating all 755 cross-fold alias-linked queries (9.43%) across both outer and inner folds ([REPORT.md](../../experiments/2026-11-22-restoration-leak-free/REPORT.md), [summary.json](../../experiments/2026-11-22-restoration-leak-free/results-v1/summary.json)).
- [x] **Near-variant-clean sensitivity refit (Split 3):** Merged all 876 Levenshtein-1 pairs and 295 `F-0010` base-shape pairs on top of Split 2 (964 components), eliminating all outer and inner alias, one-edit and base-family leakage and refitting all six models from scratch with nested three-fold inner selection.
- [x] **Modified Kneser–Ney comparison and priority positioning:** Evaluated finite-vocabulary interpolated bidirectional modified Kneser–Ney (`MKN`) and graphic-base-family pooling (`MKN-GF`, `MKN-GF-SB`) under the shared protocol, and credited Rao et al. (2009) and Yadav et al. (2010) explicitly for prior Markov restoration, modified Kneser–Ney smoothing and deduplication.
- [x] **Paired component-bootstrap uncertainty and independent replay:** Computed 10,000-draw paired component-bootstrap intervals within and across Splits 1–3 (`seed = 20261122`) and passed standalone verification in [verification-v1.json](../../experiments/2026-11-22-restoration-leak-free/verification-v1.json) (`0.0` Split 1 reproduction diff, `8.88e-16` max recomputation diff across 18 cells, `6.66e-16` brute-force replay diff across 45 queries and 270 evaluations, zero leakage violations).
- [x] **Preservation of frozen 2 October 2026 endpoints:** Kept all original 2 October 2026 results (`C01`–`C19`, `MARKOV-01` through `MARKOV-05`, `numeric-review.json`) intact and clearly separated from the dated 22 November 2026 refit (`C20`–`C29`).

## Reproduction steps

Recorded environment: Python 3.13.5, NumPy 2.2.6 and the Python standard library (no PyTorch required for the exact classical and graphic-family ladder; PyTorch 2.14.1+cu126 was used in the 6 October neural package). Run all commands from the repository root after confirming the required local inputs exist under `data/normalized/` and `data/raw/`.

### 1. Verify pinned input digests

Confirm SHA-256 digests before running any check:

- `data/normalized/lipi_clean_rtl_singleline.jsonl`: `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`
- `data/normalized/lipi_observed_faces.jsonl`: `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`
- `experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv`: `c2d55fb56e25b8d7f630f2680f9b85b9122cfa15b8718e08fa5b72c11f509f7d`
- `experiments/2026-11-22-restoration-leak-free/PROTOCOL.md`: `b4c0a1d4c3147d5f012463f78dd0ed1392963752b147e06fdd52d59143a9c3f6`
- `experiments/2026-11-22-restoration-leak-free/results-v1/summary.json`: `d97eaa3af73d60a1c952db517d9f51bf24b125e13f57a84e90e7cbc96954b9ee`

### 2. Replay verification without overwriting frozen outputs

```powershell
# Original 2 October 2026 structural integrity tests and read-only numeric claim audit
python src/methods/verify_methods.py
python papers/001-artifact-aware-prediction/verify_numeric_claims.py

# Independent verification of the 22 November 2026 Split 1-3 refit
python experiments/2026-11-22-restoration-leak-free/code/verify.py

# Prose check over Paper 001
python tools/review_prose.py --path papers/001-artifact-aware-prediction --no-write
```

### 3. Full fresh refit from scratch

`experiments/2026-11-22-restoration-leak-free/code/run_refit.py` refuses to run if `results-v1/summary.json` already exists, protecting the frozen endpoint. To perform an independent clean-room refit, copy `experiments/2026-11-22-restoration-leak-free/code/` into a new dated directory `experiments/YYYY-MM-DD-restoration-repro/code/`, point `RAW` to a fresh local directory under `data/raw/YYYY-MM-DD-restoration-repro/`, run `run_refit.py` and `verify.py`, and compare the resulting summary JSON against `d97eaa3a...`. For fresh runs of the 2 October 2026 shuffled-corpus references and matched-law gap sensitivity, use the commands in [methods.md](methods.md) with a fresh dated output path.

## Local-only data and redistribution boundaries

Follow [REDISTRIBUTION.md](../../knowledge/provenance/REDISTRIBUTION.md) and [LOCAL_STORAGE.md](../../LOCAL_STORAGE.md) before assembling any public preprint supplement or repository release bundle:

| Asset class | Repository status | Preprint / public release handling |
|---|---|---|
| Paper 001 prose, methods, claim map, checklist, protocols, analysis scripts, `summary.json`, `verification-v1.json`, `numeric-review.json` | Tracked in Git | Safe to include in the public preprint supplement (project code under Unlicense; project text and aggregates under CC0 1.0, per [REUSE.md](../../REUSE.md)). |
| `data/normalized/lipi_clean_rtl_singleline.jsonl` and `data/normalized/lipi_observed_faces.jsonl` | Local-only (`D:\projects\indus_valley_script`) | **Do not redistribute** until reuse rights for the upstream Lipi export are resolved. Publish pinned acquisition steps, normalization scripts (`research/corpus/normalize_lipi.py`) and SHA-256 digests instead. |
| Per-query slot audits and prediction JSONLs (`results/restoration/*slot_audit*.jsonl`, `data/raw/2026-11-22-restoration-leak-free/predictions/`, `folds/`) | Local-only | **Do not redistribute**, because per-slot targets and record sequences can reconstruct the unresolved-rights input corpus. |
| Mayig corpus source and crosswalk (`data/normalized/mayig_wells_class_crosswalk.json`) | Bulk data local-only; MIT-licensed upstream | Preserve the Michael Carlson (2024) MIT notice and cite the pinned upstream repository; trace any CISI photographs separately. |
| Third-party PDFs, scans, CISI photographs, Sproat XML and derived nonlinguistic JSONLs | Local-only | **Do not redistribute** unverified-rights PDFs or photographs; include Apache 2.0 notices and `flatten_manifest.json` if packaging Sproat-derived controls. |

## Remaining human review items before submission

### Epigraphic and archaeological review

- [ ] **Photographic transcription audit:** An independent Indus epigraphist inspects a pre-declared stratified sample of faces across sites, object types, compound-sign divisions, reading-direction assignments and disputed signs, producing a source-linked adjudication table and transcription uncertainty bounds.
- [ ] **Crosswalk and allograph review:** Epigraphic review of the Mayig-to-Wells class crosswalk (checking the 5 unmapped and 7 unsupported faces plus candidate-set overlaps) and of the `F-0010` 77-class base-shape table (`sign_components_v1.tsv`), noting that both `F-0010` coders were instances of one AI model working in Wells code order.
- [ ] **Prospective post-catalogue evaluation:** Acquire and transcribe newly published CISI 3.1 and post-catalogue inscriptions, verify zero full-corpus alias and near-variant overlap with the Lipi training set, and score frozen Split 2 and Split 3 recipes prospectively without retuning.

### Statistical and computational review

- [ ] **Neural refit on Splits 2 and 3:** On a PyTorch-enabled workstation, refit the 6 October GRU, transformer, conditioned neural and log-ensemble models from scratch on Split 2 (1,361 components) and Split 3 (964 components) so neural and exact classical rankings can be compared directly under zero alias and zero near-variant leakage.
- [ ] **External statistical check:** Independent statistician reviews the conditional component-bootstrap assumptions (conditioning on fitted models and fixed corpus population), the uniqueness-conditioned rejection sampler (`1,000` accepted of `6,569` proposals), and the coarser-partition cross-split bootstrap design.
- [ ] **Independent clean-room reproduction:** A contributor outside the original fitting session reproduces the 2 October and 22 November summaries from pinned inputs and signs a dated reproduction log.

### Editorial and submission packaging

- [ ] **Authors, affiliations and disclosures:** Assign human authors, affiliations, contribution roles, acknowledgements and explicit AI-assistance disclosure.
- [ ] **Reference verification:** Verify title-page bibliographic details for every entry in Section 9 (`R1`–`R11`), especially older printed proceedings (`R3`, `R5`, `R9`).
- [ ] **Figures and venue formatting:** Generate tracked publication figures from the verified aggregates (predictive gain, Split 1–3 known-slot accuracy vs. log loss and ECE, and known-slot vs. unknown-count gap contrast) and format for the chosen preprint server or journal.
