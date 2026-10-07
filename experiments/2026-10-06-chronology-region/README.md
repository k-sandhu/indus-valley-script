# Package D1: chronology, region and external inscriptions

**Follow-up of 7 October:** the caption-led assays are complete and labelled **Exploratory, post-launch amendment**. Harappa 3C has **4.59846 more rarefied object types** than 3B at 115 families per period. The early inventory has **18 signs**, but its type-and-length-adjusted difference from later texts is **+0.12019 signs**, interval **[−1.43545, 4.16580]**. External Wells 090/091 raw enrichment occurs entirely on circular seals, which have no supported matched endpoint. [Added findings and reproduction commands](#caption-led-follow-up-of-7-october); [report](REPORT.md#caption-led-post-launch-analyses-recorded-7-october-2026).

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

## Caption-led follow-up of 7 October

The [dated protocol](POST-LAUNCH-PROTOCOL-2026-10-07.md) preceded this computation. It follows the coordinator's [caption check](../2026-10-06-research-program/frenez-talk-check.md). The original endpoints, scripts and source manifest are preserved. Copies of the four earlier documents and their baseline hashes are in [post-launch-document-baseline-2026-10-07-v1/](post-launch-document-baseline-2026-10-07-v1/). Every new path and the four document updates are enumerated in [FILES_POST_LAUNCH_2026-10-07.json](FILES_POST_LAUNCH_2026-10-07.json).

The graphic references support Wells **090** for the simple human and **091** for paired humans; **093/097** are declared alternatives. In all 42 external faces, 090 occurs **7/149 known tokens (4.69799%)**, versus **184/17,792 (1.03417%)** in core regions; 091 occurs **5/149 (3.35570%)**, versus **22/17,792 (0.12365%)**. All 12 external target tokens are on circular seals. Only **7 external faces, 30 tokens**, have supported exact type/length matches, and these contain neither target. Their equal-type excesses are **−0.28739** and **−0.01228 percentage points**; grouped enrichment Holm p-values are **1.000**. This selected comparison leaves circular-seal enrichment unresolved. [Identifications](post-launch-2026-10-07-v1/sign_identifications.json), `identifications`; [counts](post-launch-2026-10-07-v1/external_target_counts.csv); [matched effects](post-launch-2026-10-07-v1/external_frequency.json), `results`; [selection](post-launch-coverage-2026-10-07-v1/external_selection_counts.csv).

Period 3B has **115 families and 5 object types**; 3C has **444 and 14**. At 115 families each, expected richness is **5 versus 9.59846**, difference **4.59846 [3.19136, 6.14341]**, Holm **p=.0145**. Expected Shannon diversity rises **0.90105 bits [0.67707, 1.14435]**, Holm **p=.001**. All **200** sampled admissible-date allocations retain positive rarefied differences. The date bin is **2200–1900 BCE**, so these data cannot locate a change specifically at 2100 BCE. [Counts](post-launch-2026-10-07-v1/media_period_summary.csv); [effects](post-launch-2026-10-07-v1/media_comparison.json), `effects`; [allocations](post-launch-2026-10-07-v1/media_interval_allocations.csv).

Unambiguous Periods 2/3A contain **31 readable families, 37 known tokens and 18 signs**. Samples of 31 later families average **63.01051 signs**, but also **128.97599 known tokens**. Exact type/observed-length support retains **27 early and 12 later pottery families**, sampled at a common total budget of **12**. Their expected inventories are **10.12019 versus 10.00000**, difference **+0.12019 [−1.43545, 4.16580]**, Holm **p=.5335**. This export provides no adjusted evidence for a restricted early repertoire on that support. [Early results](post-launch-2026-10-07-v1/early_inventory.json), `raw_family_reference`, `adjusted.type_length`; [cell denominators](post-launch-coverage-2026-10-07-v1/early_adjusted_denominators.csv).

The added run took **51.10 seconds**. It uses the original analyzer and Paper 002 component approach; it fits no new sequence model. [New sources](sources-post-launch.json) distinguish opened texts from bibliographic leads, including Vidale's direct external-sign precedent and Kenoyer's published media chronology. Four PDFs downloaded successfully; one scan lacked extractable text. Earlier Parpola 1983/1986/1994 and Kenoyer–Meadow 2008 full chapters remain unchecked. Lecture-slide IDs and individual external-find classifications also remain unverified.

Run from the repository root with fresh names. The saved original D1 endpoint must remain present for the prespecified seven-object sensitivity. Required packages are those already recorded in [environment.json](environment.json).

```powershell
python -B experiments/2026-10-06-chronology-region/post_launch.py --run reviewer-post-launch-2026-10-07-v1
python -B experiments/2026-10-06-chronology-region/verify_post_launch.py --run reviewer-post-launch-2026-10-07-v1 --output reviewer-post-launch-verification-v1.json --coverage reviewer-post-launch-coverage-2026-10-07-v1
python -B experiments/2026-10-06-chronology-region/acquire_post_launch_sources.py --run reviewer-post-launch-sources-2026-10-07-v1
python -B experiments/2026-10-06-chronology-region/finalize_post_launch.py --verification reviewer-post-launch-verification-v1.json --output reviewer-post-launch-final-checks-v1.json --inventory reviewer-post-launch-files-v1.json
python tools/review_prose.py --path experiments/2026-10-06-chronology-region --no-write
```

[Follow-up verification](verification-post-launch-2026-10-07-v1.json) rebuilt **1,921 Harappa families**, checked **44 rarefaction curve rows** using combinations, tested **20 constructed subset cases**, and checked saved p-values/corrections and principal interval quantiles. Its **395,653 assertions** mostly check admissible family-date assignments; they are not independent archaeological confirmations. It verified **81 immutable prior files** and four document snapshots. Repeat the complete random schedule in fresh directories, inspect atlas rows 26/31 at zero-based page index 20, sample Vidale Figure 5 and Kenoyer Tables 1–2, and check the external circular-seal losses and early pottery support. [Final preservation/source checks](final-checks-post-launch-2026-10-07-v1.json) record the end-of-work audit.
