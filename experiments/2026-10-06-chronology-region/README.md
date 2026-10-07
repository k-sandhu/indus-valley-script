# Package D1: chronology, region and external inscriptions

This package analyzed all **5,680 local faces** and searched primary chronological, regional and external-text precedents. The input has **18,067 known tokens**, **1,879 unreadable slots** and **4,695 physical families**. The [report](REPORT.md) answers the three questions with exact populations, source locations and uncertainty limits.

The unambiguous Harappa 3B–3C comparison has adjusted frequency divergence **0.19048 bits**, family-reference Holm **p = 0.044**, and text-closure **p = 0.068** on a smaller population. Four of six regional family-reference comparisons pass Holm .05; one passes under text closure as well. **Zero of 24 time and 314 regional sign tests** passes BH .05. The exact type/length external comparison retains **7 of 42 external objects**, with adjusted surprisal excess **0.65090 bits per sign** [**−0.37986, 1.85719**]. [Tests](main-2026-10-07-v1/permutation_tests.json), [sign tests](main-2026-10-07-v1/sign_tests.csv), [external endpoint](main-2026-10-07-v1/external_models.json).

Regional adjusted other-minus-within losses are **0.63860**, **0.27428** and **−1.06756 bits per sign** for Inter-Riverine, Lower Indus and Gujarat/Kutch. Equal training-component budgets change these to **0.26346**, **0.18223** and **−0.03030**. [Prediction results](main-2026-10-07-v1/regional_models.json), `adjusted.losses.type_excess/size_excess`. Region is determined by site, so a region effect conditional on fixed site is unidentifiable in this input.

## Protocols and preserved endpoints

- [PROTOCOL.md](PROTOCOL.md) and [PRECOMPUTATION_CLARIFICATION.md](PRECOMPUTATION_CLARIFICATION.md) precede outcome computation. The protocol was recorded under the October 6 task date; acquisition and computation continued after midnight on October 7.
- [main-2026-10-07-v1/](main-2026-10-07-v1/) contains the **Frozen evaluation** aggregates. Its counting, group exclusions and selected predictions passed **Verified computation** checks. Main execution took **375.22 seconds** on the recorded environment.
- [AMENDMENT-2026-10-07.md](AMENDMENT-2026-10-07.md) specifies the **Exploratory** bootstrap support repair and descriptive additions. [exploratory-2026-10-07-v1/](exploratory-2026-10-07-v1/) preserves those results separately. Some original site-balanced intervals had only 1–3 valid replicates; use the amendment when interpreting supplemental intervals.
- [mapping-notes.json](mapping-notes.json) preserves the open/questioned HARP date boundaries and the export-specific geographic scope.
- [sources.json](sources.json) records exact bibliographies, opened versus snippet-only scope, failed searches and failed downloads. Six PDFs and two useful HTML pages were downloaded; two downloads returned HTTP 403.
- [RETROSPECTIVE.md](RETROSPECTIVE.md), [registry-entry.json](registry-entry.json) and [FILES_CREATED.json](FILES_CREATED.json) provide the work record, proposed registry entry and complete path inventory. Shared repository files were not edited.

## Reproduce from the repository root

The local-only input `data/normalized/lipi_observed_faces.jsonl` must be present, with SHA256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`. It is the repository's observational Lipi export; no proposed decipherment fields enter the analysis. Required reuse code is `src/methods/conditional_structure.py`, SHA256 `ed150239452339a04ef35f04b5814a236d9bd3ad0b64702e66a0230760de0ca8`. [environment.json](environment.json) records Python and package versions. No package installation was needed.

Use fresh endpoint names. The scripts refuse an existing output directory or verification file. Default seeds and the 499 bootstrap/permutation budgets must be retained to reproduce the saved random schedule.

```powershell
python -B experiments/2026-10-06-chronology-region/analyze.py --run reviewer-2026-10-07-v1
python -B experiments/2026-10-06-chronology-region/verify.py --run reviewer-2026-10-07-v1 --output reviewer-verification-v1.json
python -B experiments/2026-10-06-chronology-region/supplement.py --main reviewer-2026-10-07-v1 --run reviewer-exploratory-2026-10-07-v1
python -B experiments/2026-10-06-chronology-region/verify_supplement.py --main reviewer-2026-10-07-v1 --supplement reviewer-exploratory-2026-10-07-v1 --output reviewer-supplement-verification-v1.json
python -B experiments/2026-10-06-chronology-region/check_catalogue_join.py --check source-join-check.json
python tools/review_prose.py --path experiments/2026-10-06-chronology-region --no-write
```

Optional literature reacquisition also requires a fresh name:

```powershell
python -B experiments/2026-10-06-chronology-region/acquire_sources.py --run reviewer-sources-2026-10-07-v1
```

Downloaded source bytes can change upstream. The saved local acquisition manifest records retrieval dates, response status, byte counts, SHA256, PDF page counts and extracted-text paths. All source payloads, full record memberships, comparator memberships and per-sign predictions remain under `data/raw/2026-10-06-chronology-region/`; temporary/configuration locations are set beneath that path. The scripts create no CI/CD or recurring automation.

## Output guide

| Files | Contents |
|---|---|
| `*_strata.csv`, `*_sign_counts.csv`, `*_positions.csv`, `*_lengths.csv` | Exact region/type, site/type and Harappa label/type counts; unreadable and clear-record denominators |
| `period_mapping.json`, `region_mapping.json`, `audit.json` | Mapping, input/code/protocol hashes, component sizes and population accounting |
| `time_comparisons.json`, `region_comparisons.json` | Raw, common-support, adjusted effects and intervals; clear/unique-text sensitivities |
| `permutation_tests.json`, `sign_tests.csv` | Whole-component reference results, expanded-margin checks, Holm and BH corrections |
| `rarefaction.json`, `interval_sensitivity.json` | Equal-token sampling budgets and interval-allocation envelopes |
| `harappa_attestation_bounds.csv`, `harappa_component_presence.csv` | Readable first/last observed bounds, presence intervals and zero-count detection limits |
| `regional_models.json`, `external_models.json` | Cross-region and matched external predictive scores, novelty and exact training/test counts |
| Supplement `*_intervals.json`, `model_intervals.json` | Cell-preserving post-outcome uncertainty estimates with status retained |
| Supplement `attestation_by_type.csv`, `presence_by_type.csv`, `sequence_summary.json` | Type-specific attestation and descriptive sequence statistics |
| Supplement `external_coverage.csv`, `external_literature_check.csv`, `unpaired_external_scores.csv` | External selection, site-level source leads and unsupported-type diagnostics |
| Supplement `actual_fold_counts.json` | Actual slot/clear-token counts rather than the original allocator's proxy |
| `source-join-check.json` | Exact CISI-base join counts for the two HARP contextual cautions |

## Checks for the reviewer

Repeat the full runs with fresh names and compare numerical fields, ignoring runtime and path/name fields. Sample the HARP chronology at printed xlv/Table 1, Suga's methods at printed 32–34, Rao's Table 2 at PDF page 5, and Parpola's external-find discussion at author-proof PDF pages 4–6. Inspect why circular seals lack matches, and authenticate selected external rows against original plates before assigning them to a non-canonical class.

The existing [main verification](verification-2026-10-07-v1.json) checked 23 divergence effects, 104 regional and 14 external prediction calculations, three count tables and ten source payload hashes. [Supplement verification](verification-supplement-2026-10-07-v1.json) checked unchanged effects, model means, fold totals, coverage and sampled type-presence counts. Independent replay of all resampling draws, interval coverage calibration, full paywalled sources and object-level archaeological validation remain outstanding.
