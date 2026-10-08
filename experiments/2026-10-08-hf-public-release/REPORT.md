# Version 0.3.1 findings and validation

All **23 configurations, 3,308 rows and 1,142 images** pass local validation. V1/v2/v3 summaries, row records, bootstrap intervals and recall outputs reproduce the frozen metrics with **zero mismatches** at tolerance 1e-12. A second fresh build matches **137/137 files** and **25,292,479 bytes**. [Final validation](validation-2026-10-08-v45.json), configurations, images, benchmark_scores, review_checks and rebuild. Packaging arithmetic has Verified computation status; correction flags remain Exploratory.

## Prediction interface

The scorer accepts the public keys printed_inscription_id and classification_literal and the frozen aliases inscription_number and classification_code. Both fields must be present under either name; null values are accepted. Conflicting aliases or non-string values fail before an output is created. FIELD-DEFINITIONS.md defines the fields alongside unit confidence and section membership. [Public instructions](release/README.md#score-a-new-row-reader); [scorer](release/code/score_benchmark.py), validate_predictions.

Minimal files use only the fields listed in the card, unit confidence and ranked code sets, plus section in v2/v3. Their values come from the frozen predictions. Both key formats preserve the baseline summaries, row records and intervals. The new check runs 27 cases: nine valid files, including nullable values, and eighteen missing/conflicting/type errors. [Format test](prediction-format-2026-10-08-v41.json), documented_row_fields and cases.

| Benchmark | Correct numbers | Correct classifications | Calibration observations |
|---|---:|---:|---:|
| v1 | 23/60 | 19/60 | 140 |
| v2 | 62/80 | 55/80 | 252 |
| v3 | 71/80 | 72/80 | 315 |

The preserved reviewer script also tests both minimal key formats and rejects all eighteen malformed confidence/section/unit/row-count cases. [Reviewer rerun](review-rerun-2026-10-08-v41.json), local_card_snippets.minimal_format and failing_cases. This verifies the documented interface with baseline values; it does not evaluate a new reader.

## Reading flags and frozen evidence

Independent candidate_fields_would_change now uses the chart audit's field-specific mapping rule: join a candidate's explicit location to its original cell membership, derive reviewed labels, and flag a changed resulting set. Missing candidate-cell identities receive warnings. The flags recover **26** definite earlier independent units: v1 A six, v1 B five and v2 A fifteen. V3 derives **eight** for A and **eight** for B; its eight adjudicated flags remain unchanged. [Flag check](reading-flags-2026-10-08-v41.json), group_counts, v3_definite_units and definite_units; [P impact](../2026-10-08-chart-reference-audit/impact-v2.1.json), public_readings.unit_changes.

corrected_cell joins the union of chart_locations, chart_references and shape_only_chart_locations. V2 reader B consequently has **20** changed-cell units against the impact's strict-location **12**, and **seven** class-metadata units against **six**. The eight additional units have explicit shape-only joins; one adds the class change. [Flag check](reading-flags-2026-10-08-v41.json), v2_reader_b_additional_shape_only_units records each sample, unit and cell; [field rules](release/FIELD-DEFINITIONS.md), nested benchmark fields.

All 23 schemas and original table values match reviewed 0.3.0 after excluding only the separate reading flag columns from comparison. The 687-cell chart remains reference 2.1: eight primary codes and two classes corrected, sixteen ambiguities provisionally settled and 33 medium-confidence cells. Benchmark cards, references, predictions and locators keep their original vocabulary. Frozen strict top-five scores remain **24/60, 40/80 and 62/80**; v3 numbered/physical random-page recall remains **1,289/1,289 and 1,296/1,296**. Corrected-label rescoring remains deferred until the 18 v2 and 31 v3 unlocated identities and v3 58:0 locator conflict are reviewed. [Preservation](rebuild-comparison-2026-10-08-v42.json), table_preservation and checks; [metrics](release/benchmark/expected-metrics.json), summary and v3 recall; [chart changes](release/provenance/chart-changes.json), reference_impact and locator_conflicts.

## Public documentation and provenance

The card now puts the three benchmark frames in a table and states AI-reference provenance once. Earlier readers are Claude Sonnet, with the v2 version unrecorded; v3 readers are Claude Sonnet 5.5. It defines CISI, face, provisional family, field-block cue and the disclosed scratch/directory incidents, and gives distinct benchmark, census and metrology component descriptions. The chart review note names expert inspection priorities and publicly available cell/table witnesses. [Card](release/README.md#benchmark-frames-and-reference-provenance); [review priorities](release/docs/CHART-REVIEW.md).

CFF version 0.3.1 validates against the official 1.2.0 schema. It omits license because a list denotes alternative terms; its message directs readers to the per-component LICENSE. Owner decisions remain CC BY 4.0 edition content, CC0 project additions/data/documentation, Unlicense code and author alias k-sandhu. The three official legal texts match their saved witnesses. [CFF and rights check](review-fixes-check-2026-10-08-v41.json), cff and official_license_texts_equal; [citation](release/CITATION.cff); [full owner audit](rights-audit.json).

## Rights, privacy and reproducibility

The reviewer rerun completes **14 scripts**, with a fifteenth protected script comparing the rebuild. Outputs and scratch locations are redirected without editing the scripts; Hub loading/snippets use local substitutes. The image audit finds all 1,142 parent hashes. The whole-sequence screen tests **149 complete singleton rows** (43 v1, 62 v2 and 44 v3) against **6,878 directional sequences**; zero match. The earlier forward index has **3,506** sequences. The six-derivative run screen detects all 200 plain and 200 ambiguous planted controls and finds zero graphic-code runs. Its twelve generic integer hits are preserved agreed-unit position lists. [Reviewer rerun](review-rerun-2026-10-08-v41.json), checks, images, sequence_scan and sequence_dispositions; [base screen](validation-2026-10-08-v41.json), sequence_screen.

Prose comparisons leave zero unexplained third-party passages after location/witness review. Exact bibliography and official legal text are permitted; other matches are project readings, process notes and independently supported identifier citations. The strict privacy scan has zero hits. The broad reviewer scan additionally matches authorized public account names, a generic directory phrase in frozen reader metadata and the access label Research/archive pages; their dispositions are recorded. These screens cover saved witnesses and numbering. [Reviewer rerun](review-rerun-2026-10-08-v41.json), prose and privacy.

The release stores 1,067 PNGs embedded and 75 loose, totaling 137 files. Its rebuilt bytes are identical and the reviewed 0.3.0 archive and 57 reviewer files retain their hashes. All earlier validation files remain unchanged. [Rebuild comparison](rebuild-comparison-2026-10-08-v42.json), checks and rebuild; [changed-path inventory](created-paths-v0.3.1-2026-10-08.json).

## Hosted status and remaining decisions

The 0.3.0 review verifies private Hub commit 541766d5ea8a4c3b3ec5fcc416ee764af8763afb: 23 configurations, 3,308 rows and 136 files equal to the earlier local folder. This revision makes no Hub call. Hosted 0.3.1 remains a coordinator check after upload; the public viewer remains unchecked after the private server returned HTTP 501. Expert epigraphic review is pending. [REVIEW-0.3.0.md](REVIEW-0.3.0.md), Hosted loading and Method and scope; [owner checklist](RELEASE-CHECKLIST.md) retains the issues repository, private-store terms and final visibility decisions. No upload, repository creation, visibility change or other package edit occurred.
