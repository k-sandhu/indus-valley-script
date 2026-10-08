# Helsinki 1979: the completed v3 crop evaluation

V3 fails four of five frozen release criteria. In **80 fresh rows across the numbered, end-sorted and beginning-sorted sections (28/26/26), excluding both earlier samples by page**, it accepts 71 crops, reads 71 numbers and 72 classifications, matches 72 counts, and yields 38 top-one and 62 top-five compatible whole rows. Random-page numbered recall passes at 1,289/1,289. Cropping and unit segmentation still limit the proposals; every occurrence remains quarantined. [Frozen metrics](repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json), `summary`, `negative_result_criteria`; [diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json), `criterion_row_gaps`, `incompatible_whole_row_partitions`.

## Three frozen endpoints and their frames

| Outcome, Wilson 95% interval | First: 60 numbered rows, PDF 31–79 | V2: 80 rows, three sections | V3: 80 fresh rows, three sections |
|---|---|---|---|
| Crop acceptance | 23/60 (38.3%; 27.1–51.0%) | 44/80 (55.0%; 44.1–65.4%) | 71/80 (88.8%; 80.0–94.0%) |
| Drawing-unit count | 33/60 (55.0%; 42.5–66.9%) | 59/80 (73.8%; 63.2–82.1%) | 72/80 (90.0%; 81.5–94.8%) |
| Literal inscription number | 23/60 (38.3%; 27.1–51.0%) | 62/80 (77.5%; 67.2–85.3%) | 71/80 (88.8%; 80.0–94.0%) |
| Five-position classification | 19/60 (31.7%; 21.3–44.2%) | 55/80 (68.8%; 57.9–77.8%) | 72/80 (90.0%; 81.5–94.8%) |
| Whole row, top one | 13/60 (21.7%; 13.1–33.6%) | 20/80 (25.0%; 16.8–35.5%) | 38/80 (47.5%; 36.9–58.3%) |
| Whole row, top five | 24/60 (40.0%; 28.6–52.6%) | 40/80 (50.0%; 39.3–60.7%) | 62/80 (77.5%; 67.2–85.3%) |
| Exact singleton-reference sequence | 10/52 (19.2%; 10.8–31.9%) | 19/66 (28.8%; 19.3–40.6%) | 28/54 (51.9%; 38.9–64.6%) |

The first endpoint contains **60 numbered-section rows from PDF 31–79**, drawn from 3,460 of the original 11,369 detections, with no sorted-section target. V2 contains **80 rows across three sections (28/26/26)** with eligible pools 3,596/3,228/3,496. V3 contains **80 fresh rows across those sections (28/26/26)** from pools 572/2,004/2,004 on 8/28/28 eligible pages. V3 excludes every page carrying any first-60 or v2-80 target and the original ten development pages. The row comparisons have different source frames and references; they do not estimate a paired crop-repair effect or a section-weighted edition rate. [First metrics](evaluation/2026-10-07-frozen-v1/metrics.json), `summary`; [v2 metrics](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), `frame`, `summary`; [v3 selection](repair/2026-10-08-v3/blind/selection.json), `denominators`, `eligible_pages`, `excluded_pages`.

The first crop figure preserves its original annotator labels, including C's permissive judgments; the separate objective audit and later reference corrections remain in the [preserved earlier report](repair/2026-10-08-endpoint-record-v1/documentation-snapshot.json). Exact-sequence denominators retain only singleton-reference rows: 52, 66, 54. V3 has 369 reference units and 374 proposals; 28 units retain multiple strict candidates and three have empty strict sets. Those three rows remain in the 80-row whole-sequence denominator. The fully resolved-reference sensitivity is 62/77 top-five rows (80.5%; 70.3–87.8%), while the frozen criterion uses 62/80. [V3 metrics](repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json), `summary.reference_*`, `summary.strict_top5`.

| V3 frozen criterion, all 80 rows unless stated | Observed | Minimum passing numerator | Additional passing rows needed |
|---|---|---|---|
| Crop ≥90% | 71/80 | 72/80 | 1 |
| Number ≥90% | 71/80 | 72/80 | 1 |
| Count ≥95% | 72/80 | 76/80 | 4 |
| Top-five whole rows ≥80% | 62/80 | 64/80 | 2 |
| Random-page numbered recall ≥95% | 1289/1289 | 1225/1289 | 0 |

The criterion gaps count passing rows required at the frozen point thresholds; they are not promises that repairing that many rows would validate a future method. The classification field and top-one sequence have reported scores but no separate global threshold. All four failures keep the global release gate closed. [Diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json), `criterion_row_gaps`.

## Unit recall and confidence calibration

| Outcome, stored row-bootstrap 95% interval | First: same 60 numbered rows | V2: same 80 three-section rows | V3: same 80 fresh three-section rows |
|---|---|---|---|
| Aligned strict top-one recall | 199/267 (74.5%; 66.3–81.7%) | 249/352 (70.7%; 64.2–76.8%) | 293/366 (80.1%; 73.6–86.2%) |
| Aligned strict top-five recall | 224/267 (83.9%; 76.0–90.6%) | 304/352 (86.4%; 81.1–91.2%) | 338/366 (92.3%; 87.8–96.4%) |
| Equal-count positional top one | 103/140 (73.6%; 58.4–85.3%) | 174/252 (69.0%; 61.0–76.2%) | 263/315 (83.5%; 77.0–88.9%) |
| Equal-count positional top five | 118/140 (84.3%; 68.7–95.7%) | 217/252 (86.1%; 79.2–92.1%) | 301/315 (95.6%; 91.6–98.8%) |
| Brier score | 0.1488 (0.107–0.197) | 0.1925 (0.158–0.231) | 0.1117 (0.095–0.131) |
| Ten-bin calibration error | 0.1056 (0.080–0.185) | 0.0755 (0.047–0.147) | 0.1153 (0.090–0.151) |

Aligned recall counts resolved strict units: the three v3 empty sets leave 366 of 369 units in that denominator. Extra proposals do not reduce aligned recall; their effects enter count and whole-row scores. Positional scores and calibration are conditional on equal counts and resolved strict positions (315 v3 units). V3 kept the original confidence coefficients and performed no refit. Its 43 units in the ≥0.9 confidence bin all match top one, within this conditional sample; that bin provides no row-release authorization. The stored v3 intervals use 2,000 row resamples within sections, seed 2026100881. [Three metric files](evaluation/2026-10-07-frozen-v1/metrics.json), [v2](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), [v3](repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json), `summary`, `row_bootstrap_95`, `bootstrap`.

## Source-row and physical-line recall

| Independent count frame | V2 recall / precision, pooled Wilson 95% | V3 recall / precision, pooled Wilson 95% |
|---|---|---|
| 18 random pages, six per section | 1,242/1,286 (96.6%; 95.4–97.4%) / 1,242/1,242 (100%; 99.7–100%) | 1,289/1,289 for both (100%; 99.7–100%) |
| Stress pages 62, 129, 130 | 561/561 for both (100%; 99.3–100%) | 561/561 for both (100%; 99.3–100%) |
| Random-page physical lines, including unnumbered lines | Not a frozen v2 metric | 1,296/1,296 for both (100%; 99.7–100%) |

V3's 18 random pages are fresh relative to the previous count-page set. Its seven extra physical lines occur on pages 35, 47,127,172 and 175. Both readers agree on 1,850 numbered rows and 1,857 physical lines across all 21 pages and 52 columns; the stress pages contain no extra physical lines. Random-page bootstrap recall/precision intervals are 100–100% for v3, compared with 90.5–100% numbered recall for v2. A sampled zero-miss result does not establish complete edition coverage. The compact stress pages 129–130 remain development pages excluded from recognition sampling; this count test measures discovery, not sign recognition on those pages. Continuation parents in the count reference remain probable assignments to the numbered line above, supported by position rather than a printed link. [V3 metrics](repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json), `source_row_recall`, `physical_line_recall`; [adjudication](repair/2026-10-08-v3/blind/adjudication-notes.json), `counts_comparison`; [reader B counts](repair/2026-10-08-v3/blind/reader-b/counts.json), `notes`.

## Limiting stages, compared with v2

Of v3's **18 incompatible top-five rows**, eight fail the crop check, six have unequal counts despite an accepted crop, and four have accepted crops and equal counts. The four are row 31 with four resolved unit misses and rows 3, 35, 70 with one empty strict-reference set each. Inspecting row 31 shows that the seven windows cut the U and adjacent fish drawings and assign overlapping underline slots. The refined diagnostic partition is therefore **8 crop, 7 segmentation/underline association, 3 unresolved strict-reference rows and 0 resolved graphic-proposal misses on inspected correct windows**. V2's corresponding inspected partition was **34 crop, 5 segmentation/underline association and 1 graphic-proposal miss** among 40 top-five failures. These are earliest observed failure stages, not counterfactual accuracy gains. [V3 diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json), `incompatible_whole_row_partitions`, `unresolved_strict_units`; [window audit](repair/2026-10-08-endpoint-record-v1/unit-window-audit.json), `refined_top5_counts`, `observations`; [v2 audit](follow-up/2026-10-07/endpoint-record-v1/unit-window-audit.json), `refined_top5_incompatible_rows`.

The six accepted-crop count failures are concrete: row 14 promotes a speck to a unit; row 32 emits an extra underline fragment and cuts a compound window; row 41 splits one tick group into three; rows 60 and 65 promote remote specks; row 68 merges two adjacent drawings. The seven inspected resolved segmentation failures include row 31's equal-count window shifts. The 65 accepted-crop, equal-count rows have 247/282 strict resolved positional matches at top one and 278/282 at top five. All four resolved top-five misses lie in row 31. Equal counts remain a proxy for the other rows' boundaries; this inspection covers failed top-five cases, not every unit. Top-one whole-row failures partition into 9 crop, 6 count and 27 count-consistent candidate failures; the last group includes the same three unresolved rows and row 31. [Diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json), `count_consistent_accepted_crop_proxy`, `accepted_crop_equal_count_top5_misses`; [audit](repair/2026-10-08-endpoint-record-v1/unit-window-audit.json), `observations`.

The nine rejected crops comprise six with neighbour-row ink (21, 44, 48, 55, 58, 66) and three with cut drawings (30, 76, 77). Row 77 also loses an own underline; rows 76 and 77 have field boxes overlapping the final drawing. Row 30 retains a compatible top-five sequence despite its rejected crop. V2's overlapping tags named omitted own underlines in 18 rows, neighbour ink in 13, number ink in 13 and cut ink in 4. V3's residual crop problem concentrates at the lower row edge and the field boundary. The original reader strings are retained unchanged alongside these post-outcome tag families. [Diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json), `crop_issues`, per-row `adjudicated_crop_issues`; [audit](repair/2026-10-08-endpoint-record-v1/unit-window-audit.json), `crop_tag_families`; [v2 diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), `crop_issues`.

Number reading fails in 9/80 rows and classification-field reading in 8/80, with 15/80 having at least one wrong field. Seven wrong numbers (22, 35, 40, 43, 52, 69, 73) and four wrong classifications (17, 25, 34, 57) remain within accepted-crop, equal-count rows. Those eleven rows are disjoint. V2 had 18 wrong numbers, 25 wrong classifications and 30 rows with either wrong field; its accepted-crop, equal-count subset retained three wrong numbers and seven wrong classifications. Field errors are separate from drawing-code classification. [Diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json), `subsets`; [v2 diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), `subsets`.

| V3 section, frame size | Crop failures | Count failures | Top-five row failures | Number failures | Classification-field failures |
|---|---|---|---|---|---|
| Numbered, 28 | 1 | 1 | 3 | 1 | 2 |
| End-sorted, 26 | 3 | 2 | 6 | 4 | 2 |
| Beginning-sorted, 26 | 5 | 5 | 9 | 4 | 4 |

Beginning-sorted rows contribute half the top-five failures and five of the eight count failures. Neighbour ink occurs on PDF 68, 112, 115, 135, 148, 161; drawing cuts occur on 84, 172, 174. Page 87 contributes both the equal-count underline/window failure (31) and a count failure (32). End-sorted fields lie on the left (3/26 rejected crops); the other sections use the right (6/54). Even pages have 6/44 rejected crops and odd pages 3/36. These small groups do not isolate a parity or margin-side cause. V2 had similar crop/top-five failures across its three sections (13/12/11 and 14/13/13), whereas v3's remaining failures cluster more in its sorted-section sample. No compact multi-column recognition row was evaluated. [Diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json), `by_section`, `by_page`, `by_margin_side`, `by_page_parity`; [v2 diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), corresponding fields.

## Chart labels and future correction

| Chart cell | Frozen card label / observed printed code | Reference units by exact cell key | Top-one / any top-five proposal units |
|---|---|---|---|
| 20:4:1 | 506 / 508 | 3 (31:0, 32:0, 32:2) | 2 / 3 |
| 21:6:1 | 206 / 208 | 2 (60:6, 67:4) | 2 / 6 |
| 20:4:13 | 360 / 350 | 0 | 0 / 0 |
| 21:6:31 | 285 / 286 | 0 | 0 / 1 |

The first two differences affect reference units and predictions in this sample; the fourth appears only as a non-top-one proposal (row 46 unit 1, rank 4). This endpoint scores the shared card vocabulary, so the printed-label differences do not change its frozen codes or metrics. The adjudication notes additionally locate row 58 unit 0 at 20:4:1, while the reference locates it at 21:7:5, another card labelled 506. The table uses exact reference keys and preserves that conflicting prose locator separately. It is unsafe to replace every occurrence of 506 or 206 globally because different cells share those codes. [Adjudication notes](repair/2026-10-08-v3/blind/adjudication-notes.json), `card_label_observations`; [diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json), `chart_label_audit`, `chart_location_witness_disagreement`.

Post-outcome source inspection supports the reference's row 58 locator: its first drawing is two overlapping circles with corner ticks, matching 21:7:5; 20:4:1 is a branched stem. This local observation preserves both witnesses and makes no new reference. [Locator inspection](repair/2026-10-08-endpoint-record-v1/chart-locator-inspection.json), `observation`, `source_hashes`.

[Package P](../2026-10-08-chart-reference-audit/PROTOCOL.md) owns the full chart audit. A future pipeline should take its reviewed, cell-keyed snapshot and explicit old-to-new mapping as new inputs, regenerate candidate-code labels and blind chart cards, retain unresolved and duplicate-code cases, and check confidence calibration under the new labels. Freeze those changes and their evaluator before a fresh source reference. Preserve this endpoint for comparison; a separate cell-remapping sensitivity can measure label effects but cannot replace its metrics. Package N's verification reference must declare its chart version and independently confirm the row 58 cell identity before using that cell-specific mapping.

## Quarantine and package N handoff

All **11,769 v3 physical-line proposals (11,702 numbered occurrences and 67 continuations) remain quarantined; zero are released**, as do the 11,369 original occurrences. The full JSONL has 54,384 unit windows, five unresolved empty windows, and 159 source pages. Its 106,190,599-byte payload stays local; [HOST-FILES.txt](HOST-FILES.txt) lists it for coordinator backup. No full inference was repeated while recording this endpoint. [Full summary](repair/2026-10-08-v3/full-summary.json), `rows`, `numbered_occurrences`, `continuation_lines`, `units`, `nonfinite_units_unresolved`, `released_rows`.

An automatic route requires a separately frozen repair and fresh blind test passing all five global criteria, then complete geometry, resolved continuation/editorial state, singleton top-one codes, independent numeric-witness agreement, minimum unit confidence 0.90 and confidence product 0.90 for each eligible row. The chart correction also needs an explicit version and label validation. High confidence cannot bypass a failed global gate. The authorized option-B route uses the v3 inventory as proposals, with complete source-column coverage, reviewed line membership and missing-line recovery; its separately validated acceptance rule and human/expert source check remain required. [Freeze](repair/2026-10-08-v3/freeze-manifest.json), `release_rule`; [proposal contract](OPTION-B-INTERFACE.md); [schema](option-b-schema.json).

[Package N's pilot](../2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md) used v2 proposals on 216 target rows: readers agreed on 185/216 (85.6%; Wilson 80.3–89.7%), and 31 went to adjudication. Each role passed 16/18 all-field hidden controls (88.9%; 67.2–96.9%), below its 95% screening threshold; adjudication matched all 18. It recommends clarified coincident-pair/unit-kind conventions, package P's reviewed chart and a second pilot with v3 before a full run. Seeing proposals saved no reader time in that pilot. Package M supplies immutable source coordinates, physical-line keys, suffix-preserving numbers, candidate sets, confidence and source/freeze hashes through the [option-B interface](OPTION-B-INTERFACE.md); N creates its own reviewed records under its [input contract](../2026-10-08-helsinki1979-row-verification/INPUT_CONTRACT.md). The original proposals and endpoint stay unchanged.

N's measured planning projection for two AI roles plus adjudication on 11,702 numbered occurrences is 336.4 million task tokens (bootstrap 95% 302.2–366.1 million) and 346.0 summed agent-hours (276.1–462.3), before an unmeasured human/expert pass. Task tokens include cached context and are not a price. The pilot is three pages, so those planning intervals do not measure full-edition verification accuracy. A person checking every numbered occurrence would add 195.0,390.1 or 975.2 hours at assumed one, two orfive minutes per row, plus continuation, source-coverage and ledger work; human throughput has not been observed. [N projection](../2026-10-08-helsinki1979-row-verification/pilot/coordinator-cost-projection-v1.json), `full_run`; [cost record](repair/2026-10-08-endpoint-record-v1/reader-process-cost.json), `package_n_pilot`. L still requires independently reviewed carrier/surface concordances and imports none here.

## Development, provenance and reproduction

V3 reused all 80 v2 targets and 352 units, and 21 old count pages, to select its crop method before freezing. Development scores were 71 counts, 69 numbers, 67 classifications, 33 top-one and 60 top-five rows,327/352 aligned top-five units, and 1,847/1,847 numbered recall. These Exploratory development results remain in the [development diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json); they are separate from the fresh endpoint above. The old classifier, digits, chart and calibration were reused unchanged. The [freeze](repair/2026-10-08-v3/freeze-manifest.json) and [prediction freeze](repair/2026-10-08-v3/prediction-freeze.json) precede all new readings. The complete reader/adjudication process and deviations are recorded in [RETROSPECTIVE.md](RETROSPECTIVE.md) and [reader cost](repair/2026-10-08-endpoint-record-v1/reader-process-cost.json).

The new record reuses `record_repaired_endpoint.py`'s Wilson and diagnostic functions, the v2 diagnosis and window audit, the frozen scorer and all supplied reader witnesses. Reproduction commands are in [README.md](README.md). Source attribution: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), University of Helsinki, [handle](http://hdl.handle.net/10138/342677), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); raster cropping and annotations are modifications. No new source download, literature search, chart correction or ledger import was performed.
