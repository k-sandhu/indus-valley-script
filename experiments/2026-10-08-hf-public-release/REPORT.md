# Version 0.3.0 findings and validation

All **23 configurations and 3,308 rows** load locally, and every one of **1,142 PNGs** matches its parent. The scorer reproduces all three frozen endpoints with zero numerical or structural differences at tolerance 1e-12, including v3 numbered and physical-line recall. [Final validation](validation-2026-10-08-v38.json), configurations, images, source_checks and benchmark_scores. Status: Verified computation for packaging and arithmetic; chart annotations and later interpretation remain Exploratory.

## Chart changes and preserved vocabulary

The chart uses [P's current reference 2.1](../2026-10-08-chart-reference-audit/chart-reference-v2.1.json). Eight primary codes and two upper classes change, and 16 earlier lower-code ambiguities are provisionally settled. Thirty-six records change numeric fields; 33 cells have medium and 654 high qualitative confidence. The second AI reader inspected 63 cells blind and checked the whole chart with pixels. It did not independently eye-read every cell, and no expert reviewed the labels. [Chart provenance](release/provenance/chart-changes.json), comparison_summary and changes; [chart table](release/data/chart_reference.parquet), previous_* and change_note.

Every earlier v1/v2 reference, prediction and locator field is preserved after resolving portable provenance labels back to its witness. The 91-file 0.2.0 archive retains its hashes. V3 uses M's frozen predictions and adjudicated reference without label remapping. [Rebuild comparison](rebuild-comparison-2026-10-08-v37.json), checks.v1_frozen_payloads_preserved, checks.v2_frozen_payloads_preserved and checks.v0_2_0_archive_preserved.

Unit flags match P's sample/unit joins. Direct candidate changes occur in 11/0/8 reference units in v1/v2/v3; unlocated affected identities occur in 0/18/31. Linked changed records, including class/confidence updates, touch 23/12/21 units. V3 preserves one locator conflict, 58:0. [Rebuild comparison](rebuild-comparison-2026-10-08-v37.json), details.*_chart_flags; [P impact](../2026-10-08-chart-reference-audit/impact-v2.1.json), M_references and M_v3_reported_location_conflicts. P asks for identity review before a mapped sensitivity; this release defers it and retains the original benchmark cards. The corrected chart is a separate vocabulary version.

## Frozen frames and AI-reference provenance

V1 evaluates 60 numbered-section occurrences on PDF 31–79 from 3,460 detections. V2 evaluates 80 numbered/end-sorted/beginning-sorted rows, 28/26/26, from pools 3,596/3,228/3,496. V3 evaluates 80 fresh rows with those quotas from pools 572/2,004/2,004 on 8/28/28 eligible pages, excluding previous target pages and ten development pages. These are separate samples; their differences do not estimate a paired repair effect. [Public card](release/README.md), Benchmark frames and reference provenance; [v3 selection](release/benchmark/v3-selection.json), denominators, eligible_pages and excluded_pages.

Two Claude Sonnet 5.5 readers and a Claude adjudicator produced the repair references from shared conventions/cards, with no human check. V3 readers agree on 80/80 numbers, classifications, counts and line memberships and 357/369 strict unit sets. Count references use pixel scripts with the field-block cue also used by the pipeline and a line-pitch cross-check. Row intervals do not capture page clustering; v3's numbered stratum spans eight pages. [M review](../2026-10-07-helsinki1979-digitization/REVIEW-V3.md), M3–M4; [reader metadata](release/benchmark/reader-metadata.json); [v3 notes](release/benchmark/v3-adjudication-notes.json), agreement_summary and counts_comparison.

| Frozen outcome | v1 | v2 | v3 |
|---|---:|---:|---:|
| Crops | 23/60 | 44/80 | 71/80 |
| Counts | 33/60 | 59/80 | 72/80 |
| Numbers | 23/60 | 62/80 | 71/80 |
| Classifications | 19/60 | 55/80 | 72/80 |
| Strict top one | 13/60 | 20/80 | 38/80 |
| Strict top five | 24/60 | 40/80 | 62/80 |
| Aligned strict top-five units | 224/267 | 304/352 | 338/366 |

[Expected metrics](release/benchmark/expected-metrics.json), v1/v2/v3.summary. V3 numbered random-page recall is 1,289/1,289 and physical-line recall 1,296/1,296; both stress-page recalls are 561/561. The 21 pages total 1,850 numbered occurrences and 1,857 physical lines. The 18 random pages are fresh relative to earlier count pages; eight carried earlier recognition targets. Stress pages are reused. [Expected metrics](release/benchmark/expected-metrics.json), v3.source_row_recall and physical_line_recall; [count table](release/data/benchmark_count_pages_v3.parquet), reference_json.

V3 falls short of crop/number/count/top-five thresholds 72/72/76/64 by 1/1/4/2 rows. Only ≥95% random-page numbered recall passes. Strict top five is 62/80; its fully resolved subset is 62/77 and shape-only is 65/80. Accepting code 23 for strict units 35:2 and 70:4 gives 64/80 in the separate Exploratory sensitivity; count and number still fail. [Sensitivity](release/benchmark/v3-reading-choice-sensitivity.json), altered_units and summary; [independent check](rebuild-comparison-2026-10-08-v37.json), checks.reading_choice_sensitivity. Full-edition proposals remain excluded.

## Rights, privacy and replay

The owner's licence/author decisions remain: CC BY 4.0 edition content, CC0 project additions/data/documentation, Unlicense code and k-sandhu without affiliation. Official licence texts match their preserved downloads; CFF validates against the official 1.2.0 schema. The museum table retains 49 independent identifier pairs and excludes 19 Lipi-only joins. [Checks](review-fixes-check-2026-10-08-v35.json), cff and official_license_texts_equal; [full owner audit](rights-audit.json); [public exclusions](release/EXCLUSIONS.md).

The whole-sequence screen tests **149 singleton reference rows with at least two units**, including 105 older and 44 v3 rows, against 6,878 sequences in both directions; zero match. The earlier basis has 3,506 distinct forward sequences. The six-derivative scan finds zero graphic-code runs of at least three positions. Twelve generic integer hits are agreed-unit index lists in six v3 records, repeated in the reference/adjudication tables. All 200 plain and 200 ambiguous planted controls are detected. Available-witness prose screens leave zero unexplained third-party matches. [Final validation](validation-2026-10-08-v38.json), sequence_screen and review_checks; [review disposition](review-rerun-2026-10-08-v35.json), sequence_dispositions and prose. The screens cover saved sources/numbering; recoded copying and unsaved prose are outside their reach.

Privacy has zero hits. Eight malformed v2/v3 prediction files fail loudly; two passing files have zero mismatches, finite intervals and calibration counts 252/315. All ten applicable reviewer scripts complete and retain their original hashes. Raw image materialization supports legacy checks; rights/privacy scans read the actual release. [Input checks](review-fixes-check-2026-10-08-v35.json), privacy and prediction_cases; [review rerun](review-rerun-2026-10-08-v35.json), checks and adaptations.

The release has **136 files, 25,287,707 bytes, 1,067 embedded and 75 loose PNGs**. A fresh build matches **136/136 files**, including manifests. [Fresh validation](rebuild-validation-2026-10-08-v37.json); [comparison](rebuild-comparison-2026-10-08-v37.json), rebuild. Owner records, full audits and raw overlap witnesses remain outside the upload folder.

Hosted 0.3.0 loading awaits the coordinator's private-preview update. The coordinator reports all 19 configurations/images loading for 0.2.0. The issues repository, private-store Hub terms and final visibility remain decisions in [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md). No upload, repository creation or visibility change occurred.
