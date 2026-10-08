# Cropping v3: development and prepared blind endpoint, 8 October 2026

V3 produces **11,769 physical-line proposals, 11,702 numbered occurrences, 67 continuation lines and 54,384 proposed unit windows (5 unresolved) across 159 pages (PDF22–180)**, with zero releases. Its new blind endpoint is prepared, and its accuracy awaits coordinator readings. The method was selected on all 80 v2 rows and the 21 existing count pages. [Full summary](repair/2026-10-08-v3/full-summary.json), `rows`, `numbered_occurrences`, `continuation_lines`, `units`, `pages`; [freeze](repair/2026-10-08-v3/freeze-manifest.json); [selection](repair/2026-10-08-v3/blind/selection.json).

## Development findings and scope

| Outcome, descriptive 95% Wilson interval | First frozen: 60 numbered rows, PDF31–79 | V2 frozen: 80 rows, 28/26/26 sections | V3 development: same 80 v2 targets |
|---|---|---|---|
| Matching unit count | 33/60 (55.0%; 42.5–66.9%) | 59/80 (73.8%; 63.2–82.1%) | 71/80 (88.8%; 80.0–94.0%) |
| Literal inscription number | 23/60 (38.3%; 27.1–51.0%) | 62/80 (77.5%; 67.2–85.3%) | 69/80 (86.2%; 77.0–92.1%) |
| Five-position classification | 19/60 (31.7%; 21.3–44.2%) | 55/80 (68.8%; 57.9–77.8%) | 67/80 (83.8%; 74.2–90.3%) |
| Compatible whole row, top one | 13/60 (21.7%; 13.1–33.6%) | 20/80 (25.0%; 16.8–35.5%) | 33/80 (41.2%; 31.1–52.2%) |
| Compatible whole row, top five | 24/60 (40.0%; 28.6–52.6%) | 40/80 (50.0%; 39.3–60.7%) | 60/80 (75.0%; 64.5–83.2%) |
| Crop acceptance | 23/60 (38.3%; 27.1–51.0%) | 44/80 (55.0%; 44.1–65.4%) | No new independent crop labels |

The first endpoint's 60-row frame covers the numbered section on PDF31–79 and no sorted row. V2's 80-row frame covers all three sections (28/26/26), and those same 80 targets and 352 units are reused for v3 development. The old predictions, references and metrics are preserved. Parameter selection prevents interpreting the v3 development intervals as held-out accuracy.

V3 aligned strict unit recall is 280/352 at top one and 327/352 at top five. On matching-count rows, the same-position figures are 244/305 and 286/305. Calibration uses those 305 aligned positions: Brier 0.124876, ECE10 0.110060. It reuses the original coefficients without fitting on these rows. These development bins and bootstrap intervals are in [diagnosis.json](repair/2026-10-08-development-record-v1/diagnosis.json), `development_summary`, `development_intervals`. Fresh v3 calibration remains unmeasured.

The 21 reused page counts yield 1,847/1,847 numbered recall and precision (Wilson 99.8–100.0%). That recovers the v2 omissions on pages 66 and 112 and retains 288 numbered rows on the eight-column page 129 and 201 on the compact page 130. The reference also records ten unnumbered continuations on these pages. V3 locates all 10 and agrees with all 10 preceding-numbered-row links (Wilson 72.2–100.0% for each measure); its 1,857 physical detections equal the old source count. This is development corroboration on the reused pages. [Continuation check](repair/2026-10-08-development-record-v1/continuation-check.json), `continuation_recall`, `continuation_precision`, `preceding_numbered_parent_agreement`, `physical_lines_detected`; [development file](repair/2026-10-08-development-v3h/development.json), `development_count_pages`, `pages`.

## Diagnosis and crop changes

The earlier 80-row endpoint rejected 36 crops; 34 of those are among the 40 top-five whole-row failures. The 34-row target set is therefore a failure-stage subset. Both full reader tag lists and their exact source locations are retained in [diagnosis.json](repair/2026-10-08-development-record-v1/diagnosis.json), `v2_rejected_crops`, `v2_top5_failure_starts_at_crop`, `crop_issue_observations`. The text-search families overlap and are a way to locate observations, not independent error labels.

The field detector pairs print components and refines its horizontal band from repeated classification lines. It rejects components cut by the field-search boundary, masks every column's field and clamps row padding. Glyph components define each row's ink bounds; dashed underline components belong to the preceding drawing body. Unanchored tall components create explicit continuation lines without imposing a pitch or row count. Compact columns use the inherited print-column detector. Body segmentation removes underline groups temporarily, retains loss-rectangle strokes and separates short ticks next to tall units; matching restores each whole underline slot. The original CNN, template costs, code candidates and calibration are unchanged. [Implementation](crop_v3.py); [frozen parameters](repair/2026-10-08-v3/freeze-manifest.json), `parameters`, `inherited_column_parameters`, `code_hashes`.

All five previously diagnosed unit-window failures (rows 3,25,50,52,58) now have matching counts and compatible top-five rows in development. Row72 retains a top-five graphic-code miss under the unchanged recognizer and chart labels. Known source/window defects remain on development rows 27 (field/next-row ink and incomplete final patch),53 (classification digit at the glyph edge),76 (final patch clipped by the field boundary). Their source contexts are local in `data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-v3/2026-10-08-development-v3h/row_027.png`, `row_053.png`, `row_076.png`; the observations are recorded in [development inspection](repair/2026-10-08-development-record-v1/visual-inspection.json). Independent crop acceptance on v3 boxes awaits the fresh source readers.

Development top-five compatible rows are 25/28 numbered,18/26 end-sorted,17/26 beginning-sorted. Count agreement is26/28,23/26,22/26. Field and graphic errors therefore remain after the principal crop repairs. These selected development strata supply no edition-level error census. [Diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json), `development_by_section`.

## Fresh reference and verification handoff

The method froze at 2026-10-08T14:11:23.905485+00:00 and predictions at 2026-10-08T14:13:49.280280+00:00. The fresh selection has 80 numbered targets drawn from 572/2,004/2,004 section pools on 8/28/28 eligible pages. Page exclusions contain every earlier evaluation target page and the original ten development pages. Source-only exact/context images, 12 chart cards and21 count pages are frozen with hashes. All selected targets happen to have no detected continuation, so the physical-line count test and complete source pass supply the planned continuation check. [Selection](repair/2026-10-08-v3/blind/selection.json); [prediction freeze](repair/2026-10-08-v3/prediction-freeze.json), `packet_hashes`; [conventions](repair/2026-10-08-v3/blind/CONVENTIONS.md).

Two source-only readers and a third adjudicator are required. No new reference or metrics were created here. The frozen evaluator reports the old metrics and both numbered/physical-line recall, with pooled and bootstrap intervals. It retains the original five criteria and prevents a pass on an incompletely scored crop/number/count frame. Every full proposal remains quarantined for the separate human-plus-independent-AI verification package. Its [contract](OPTION-B-INTERFACE.md) requires complete source-page coverage and explicit continuation review. Large output is listed in [HOST-FILES.txt](HOST-FILES.txt) for coordinator backup. L's carrier/surface concordance remains separate.

## Earlier frozen endpoints, preserved record

# Helsinki 1979 digitization: two failed frozen endpoints

The repaired pipeline fails four of five frozen reliability criteria. In its **80-row frame across numbered, end-sorted and beginning-sorted sections (28/26/26)**, it has 44 accepted crops, 59 matching counts, 62 exact numbers, 55 exact classifications and 40 top-five compatible whole rows. Random-page row recall passes at 1,242/1,286; crop and unit-window handling remain the main limits. All occurrences remain quarantined. [Frozen repaired metrics](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), `summary`, `source_row_recall`, `negative_result_criteria`.

The first endpoint remains unchanged: **60 numbered-section rows on PDF pages 31–79**, 33 matching counts, 23 exact numbers and 24 top-five whole rows. Its references, review corrections and separate sensitivities remain preserved below. The coordinator subsequently completed the repaired source readings, adjudication and unchanged evaluator after this package's recorded disk stop. Diagnostic partitions and workload projections are Exploratory.

## Both frozen endpoints

The first endpoint samples **60 numbered-section rows on PDF pages 31–79**, drawn from 3,460 of 11,369 first-run detections; it has no sorted-section target. The second samples **80 occurrences across numbered, end-sorted and beginning-sorted sections (28/26/26)**, excluding development pages and the old targets, with eligible denominators 3,596/3,228/3,496. Section quotas do not weight these headline rates to the full edition. The references also differ: one primary reading per first-endpoint row, then two independent readings and source-only adjudication for every repaired row. The comparison describes two frames; it does not estimate a paired treatment effect.

| Outcome, 95% interval | First: 60 numbered rows, PDF31–79 | Repaired: 80 rows, three sections |
|---|---|---|
| Crop acceptance | 23/60 (38.3%; 27.1–51.0%) | 44/80 (55.0%; 44.1–65.4%) |
| Drawing-unit count | 33/60 (55.0%; 42.5–66.9%) | 59/80 (73.8%; 63.2–82.1%) |
| Inscription number, including suffix | 23/60 (38.3%; 27.1–51.0%) | 62/80 (77.5%; 67.2–85.3%) |
| Five-position classification | 19/60 (31.7%; 21.3–44.2%) | 55/80 (68.8%; 57.9–77.8%) |
| Compatible whole row, top one | 13/60 (21.7%; 13.1–33.6%) | 20/80 (25.0%; 16.8–35.5%) |
| Compatible whole row, top five | 24/60 (40.0%; 28.6–52.6%) | 40/80 (50.0%; 39.3–60.7%) |
| Exact sequence, singleton-reference subset | 10/52 (19.2%; 10.8–31.9%) | 19/66 (28.8%; 19.3–40.6%) |

Row proportions use the stored Wilson intervals. The original crop acceptance includes annotator C's permissive labels; the objective audit below is separate. The exact-sequence row restricts each frame to singleton references. The repaired sample contains 352 reference drawings and 377 proposals, with 15 ambiguous reference units and none unresolved. Candidate compatibility accepts intersection with a reference set and does not authenticate a unique code. Exact evidence: [first metrics](evaluation/2026-10-07-frozen-v1/metrics.json), `summary`; [repaired metrics](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), `summary` and `frame`.

| Unit/calibration outcome, 95% interval | First: same 60-row frame | Repaired: same 80-row frame |
|---|---|---|
| Aligned top-one recall | 199/267 (74.5%; 66.3–81.7%) | 249/352 (70.7%; 64.2–76.8%) |
| Aligned top-five recall | 224/267 (83.9%; 76.0–90.6%) | 304/352 (86.4%; 81.1–91.2%) |
| Equal-count top-one positional accuracy | 103/140 (73.6%; 58.4–85.3%) | 174/252 (69.0%; 61.0–76.2%) |
| Equal-count top-five positional accuracy | 118/140 (84.3%; 68.7–95.7%) | 217/252 (86.1%; 79.2–92.1%) |
| Brier score | 0.1488 (0.107–0.197) | 0.1925 (0.158–0.231) |
| Ten-bin calibration error | 0.1056 (0.080–0.185) | 0.0755 (0.047–0.147) |

Aligned recall omits a penalty for extra proposals; whole-row scores include their count/order effects. Calibration and positional scores use only equal-count rows: 140 units originally and 252 after repair. The intervals above are the stored row bootstraps (2,000 draws; repaired resampling within sections, seed 2026100781). Five templates can propose more than five codes through ambiguous chart labels. All fields and interval arrays are in the two metric files, `summary` and `row_bootstrap_95`.

The repaired source-count frame has 18 random pages and three prespecified stress pages, separate from the 80-row recognition frame:

| Source-count frame | Recall, pooled Wilson 95% interval | Precision, pooled Wilson 95% interval |
|---|---|---|
| 18 random pages, six per section | 1242/1286 (96.6%; 95.4–97.4%) | 1242/1242 (100.0%; 99.7–100.0%) |
| Stress pages 62,129,130 | 561/561 (100.0%; 99.3–100.0%) | 561/561 (100.0%; 99.3–100.0%) |

The random-page bootstrap interval for recall is **90.5–100.0%**, wider than the pooled row interval because misses cluster by page. Page 66 loses five rows in its second column (31/36 detected); page 112 finds 18/36 and 15/36 in its two columns, losing 39 rows. Those two pages account for all 44 misses. The remaining 16 random pages have complete matched coverage. Matching uses source column bounds and a 9-point anchor tolerance. The source counts include 1,847 numbered occurrences in 52 columns and exclude ten unnumbered continuation lines; counting every physical line would give 1,857. Pages 129–130 were development pages excluded from the recognition sample, so their 288/288 and 201/201 recall results do not evaluate their glyph recognition. [Metrics](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), `source_row_recall`; [count reference](repair/2026-10-07-v2/blind/adjudicated-counts.json), `total_rows`, `total_columns`, `total_physical_lines`.

The frozen criteria use point rates: crop ≥90%, number ≥90%, count ≥95%, top-five whole rows ≥80%, and random-page recall ≥95%. Only recall passes. Four criteria fail, so the pipeline status is **Failed** and every occurrence remains quarantined. [Criteria](repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), `negative_result_criteria`.

## First-endpoint reference and extraction details

Exact fields are [metrics.json](evaluation/2026-10-07-frozen-v1/metrics.json), `summary`. The same 60-row frame contains 267 reference drawings (229 glyphs and 38 editorial units) against 288 proposals. Aligned compatible recall is 199/267 at top one and 224/267 at top five; candidate-set edits total 95 and 71. Equal-count same-position accuracy is 103/140 and 118/140 on 33 rows. The stored row-bootstrap intervals are `row_bootstrap_95`. Aligned recall does not penalize extra proposals; whole-row compatibility requires equal counts and ordered candidate intersections. Five templates can carry more than five codes when the chart has an ambiguous lower label: the mean is 5.208 codes and maximum eight in this sample.

The crop labels need a narrower interpretation. A accepted 4/20 boxes and B 3/20, together 7/40; C accepted 16/20. Nine of C's accepted boxes fail the review's edge/fragment tests even with a 1 PDF-point crossing tolerance; eleven fail with no tolerance. The post-outcome objective audit passes 14/60 boxes without tolerance (95% CI 14.4–35.4%) and 21/60 with a 1-point tolerance (24.2–47.6%). Those are additional Exploratory observations in the same numbered-section frame, and do not replace the frozen 23/60. See [crop-and-frame.json](follow-up/2026-10-07/analysis-v1/crop-and-frame.json), `per_annotator`, and [review crop audit](review/reviewer-check/diagnosis/crop-audit-summary.json), `variants`.

Source OCR strings were exposed in 22 original locators. Excluding those rows gives 13/38 exact numbers (95% CI 21.2–50.1%) within the same numbered-section frame. Glyph predictions and proposed counts were withheld from the annotators. The review independently reread 30 rows and matched all 30 for count, number and classification. Its rereading was post-outcome; it audits the reference rather than supplies a new blind estimate.

## Reference adjudication and calibration

The following **zero-based unit positions** are review adjudications, recorded on 7 October 2026. Frozen references have not been edited. Sources are [unit-adjudication.json](review/reviewer-check/unit-adjudication.json), [tick-position-check.json](review/reviewer-check/diagnosis/tick-position-check.json) and the review's source images. The [overlay](follow-up/2026-10-07/analysis-v1/adjudication-overlay.json) stores the original and adjudicated code sets.

| Sample | Unit | Original set | Adjudicated set | Source observation |
|---|---|---|---|---|
| 10 | 4 | [17] | [19] | four ticks over three |
| 35 | 2 | [599] | [597] | narrow unmarked hatched patch |
| 35 | 8 | [106] | [13] | narrow underlined hatched patch |
| 24 | 5 | [2] | [25] | pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2 |
| 25 | 0 | [2] | [25] | pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2 |
| 30 | 3 | [2] | [25] | pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2 |
| 31 | 2 | [2] | [25] | pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2 |
| 34 | 3 | [2] | [25] | pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2 |
| 51 | 1 | [2] | [25] | pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2 |
| 52 | 4 | [2] | [25] | pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2 |
| 59 | 6 | [2] | [25] | pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2 |

The chart places code 25's two short strokes high in its sign box and code 2's pair near the middle. Tight chart crops removed this distinguishing position. The repair's source-reading cards retain the original cell position. The narrow/wide hatched variants and uncertainty underlines also need separate labels. The review found the repeat reader correct on both previously reported candidate-set disagreements.

The six repeats were fixed convenience indices 5, 13, 30, 35, 42 and 51, two in each 20-row primary group. No RNG or probability-selection rule was recorded. The original protocol calls them prespecified before annotation; its paragraph-level timing cannot be independently isolated. Their count/number/classification agreement of 6/6, candidate agreement of 4/6 and four crop disagreements describe those six rows only.

Calibration uses the original references and coefficients. In the original numbered-section 60-row frame, 140 same-position units in equal-count rows give Brier score 0.1488 (row-bootstrap 95% CI 0.107–0.197) and ten-bin error 0.1056 (0.080–0.185). Excluding all three inverted selected rows leaves 57 sampled rows and 126 scored units: Brier 0.1262 (0.096–0.164) and ten-bin error 0.1183 (0.074–0.179). This sensitivity is Exploratory, uses 2,000 row-bootstrap draws with seed 2026100707, applies no adjudications and refits no model. [Calibration output](follow-up/2026-10-07/analysis-v1/calibration-upright-only.json), `calibration` and `ci95`. These quantities are conditional on matching counts and do not qualify clipped rows or object identity. The [original figure](figures/validation.png) still plots the original 60-row numbered-section endpoint, not this sensitivity or the repaired sample.

## Full first extraction and row-recall evidence

The full first run attempted PDF 22–180: 159 pages, 11,369 detected occurrences, 57,426 unit proposals, 10,425 recognized number strings and three unmatched units. Section totals are 4,036 numbered, 3,743 end-sorted and 3,590 beginning-sorted occurrences; the sorted sections contain 64.5% of that extraction and had no original evaluated row. [Coverage](runs/2026-10-07-full-v1/coverage.json), `counts` and `pages`.

**All 17 pages rotated by the heuristic are upright in the source.** Their 1,223 inverted occurrences are flagged `orientation_unreliable` in the separate [orientation overlay](follow-up/2026-10-07/analysis-v1/orientation-overlay.json). The original payload has not been changed. The affected sorted-section proportions are 575/3,743 (15.4%) and 576/3,590 (16.0%); 72 numbered-section rows are also affected. The review verified 13 page orientations from header content and four by viewing.

Twenty pages have fewer than 72 detections. Their numbers and counts are in [row-recall-evidence.json](follow-up/2026-10-07/analysis-v1/row-recall-evidence.json), `short_pages`. The review counted 36 printed rows in page 62 column 0, where the first pipeline found 21: count coverage 21/36 (58.3%; Wilson 95% CI 42.2–72.9%). This is a count comparison, not a corpus-wide matched-row recall estimate. Pages 129–130 print five to eight columns; the first method searched two. Fewer than 72 detections can also reflect a partial page, so it does not establish a missing-row count by itself. The first endpoint still has no edition-wide source denominator; the repaired 21-page count reference above now supplies a separate sampled denominator.

The active [triage queue](follow-up/2026-10-07/analysis-v1/triage-queue.jsonl) contains 9,584 rows, leaving 1,785 outside triage. Priorities contain 1,352 orientation/column/recall cases, 4,324 clipping/fragment cases, 723 field/order cases and 3,185 remaining repeat-disagreement cases. It uses native edge crossings of at least one point, narrow number-edge units, unresolved fields, unmatched ink, numbering violations and candidate disagreements between unverified number groups. It omits the universal boundary/classification flag and the old confidence cutoff that queued every row. **All 11,369 remain quarantined**, including rows outside triage. [Summary](follow-up/2026-10-07/analysis-v1/triage-summary.json), `reason_counts` and `priorities`.

## Repair development and freeze chronology

The review measured mean field drift of +7.4 PDF points on even pages and −3.2 on odd pages, with offsets from −11 to +18. It found the correct code among five proposals for all 198 size-consistent units examined; its resolution tests found no benefit from increasing the working render above two pixels per point. The native scan is 601 dpi bilevel. These are conditional, post-outcome diagnoses. Its offset/orientation rerun on the old numbered-section 60-row frame yielded 44 matching counts, 40 numbers and 35 top-five whole rows, compared with the frozen 33, 23 and 24. It supplies development evidence and no fresh accuracy estimate.

The new layout localizes field coordinates from OCR word boxes without trusting their digit strings, checks compact multi-column pages through print projections and internal whitespace, and uses source-header content for upright orientation. It detects vertical field bands and intervening glyph whitespace without fixing row counts. On development pages the detector found 72 rows on pages 30, 62, 100 and 145, eight columns/288 rows on 129 and six columns/201 rows on 130. The subsequent source-count reference confirms the 72, 288 and 201 printed occurrences on stress pages 62,129,130; pages 30,100,145 remain development detector observations. The known page-30 development reference gives 17/20 matching counts, 19/20 numbers, 6/20 top-one and 12/20 top-five whole rows. [Development output](follow-up/2026-10-07/development-recognition-v1.json).

The first repair candidate's unlabelled frame exposed false field columns from glyph-like OCR. It was superseded before any independent reading, with all artifacts preserved in `repair/2026-10-07-v1/`. The replacement adds a 35-point margin-neighbourhood restriction on ordinary two-column page types; compact printed columns remain detected separately. Its [freeze](repair/2026-10-07-v2/freeze-manifest.json) at 2026-10-07T16:54:51.431467+00:00 includes layout, sampling and evaluator hashes plus the unchanged original recognizer, digits, chart and calibration. Its [prediction freeze](repair/2026-10-07-v2/prediction-freeze.json) at 2026-10-07T16:58:06.116694+00:00 precedes the completed independent readings and adjudication supplied by the coordinator.

## Limiting stages: Exploratory diagnosis of the 80-row endpoint

Row geometry and editorial-unit handling limit this endpoint. Of **40 incompatible top-five rows**, 34 first fail the crop check, three have unequal unit counts despite an accepted crop (indices 3,50,52), and three have candidate misses despite accepted crops and matching counts (25,58,72). For **60 incompatible top-one rows**, the corresponding partition is 35 crop, three count and 22 count-consistent candidate failures. These partitions use the earliest failed observable check; they do not attribute a counterfactual gain from repairing that check. [Diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), `incompatible_whole_row_partitions` and per-row `metric_fields`.

Across all 80 rows, 36 crops are rejected, including two with compatible top-five sequences. Eighteen of the 21 count failures occur inside rejected crops; three are additional segmentation failures in accepted crops. The adjudicated tags name omitted own underlines in 18 rows, neighbour ink in 13, number-field ink in 13 and cut target ink in four. Tags overlap. The loss rectangle is split into two units in row 3; a dash fragment becomes an extra tick in row 50; the high tick is absorbed into the following diamond window in row 52. [Source tags](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), `crop_issues`, and [unit-window inspection](follow-up/2026-10-07/endpoint-record-v1/unit-window-audit.json), `count_failure_rows`.

The 41 accepted-crop, equal-count rows contain 166 units. Strict positional matches are 134/166 at top one and 161/166 at top five; shape-only matches are 152/166 and 165/166. Equal counts are a segmentation proxy, so these are conditional observations. Inspection of all five residual strict top-five unit misses finds four underlined units in rows 25 and 58: their 5–9-point unit windows truncate part of the approximately 14-point underline, and the corresponding plain graphic is proposed. The remaining miss is row 72 unit 1, a complete figure whose code 244 lies outside the five proposals. Thus the inspected top-five failures have repair targets of **34 row crops, five rows with unit segmentation/underline association defects, and one row with a graphic proposal miss**. This inspection was made after predictions were visible and does not validate every other unit boundary. [Audit](follow-up/2026-10-07/endpoint-record-v1/unit-window-audit.json), `units`, `refined_top5_incompatible_rows`; [source conventions](repair/2026-10-07-v2/blind/reader-b/rows-part1.json), `notes` on dashed sign slots.

Number reading fails in 18/80 rows and classification-field reading in 25/80; 30/80 have at least one bad field. These overlap crop and unit errors. Among the 41 accepted-crop, matching-count rows, three still have wrong numbers (12,40,68) and seven wrong classifications (16,18,31,32,34,37,66). Those ten rows are disjoint. Glyph classification and the five-position classification field are separate outcomes. [Diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), `subsets`.

| Section in the 80-row frame | Crop failures | Count failures | Top-five row failures | Number failures | Classification-field failures |
|---|---|---|---|---|---|
| Numbered (28) | 13 | 7 | 14 | 5 | 8 |
| End-sorted (26) | 12 | 7 | 13 | 8 | 12 |
| Beginning-sorted (26) | 11 | 7 | 13 | 5 | 5 |

Crop and whole-row failure rates are similar across the three sections. Field reading is worse in the end-sorted sample, where numbers/classifications sit to the left. The numbered and beginning-sorted fields sit to the right. Odd pages have 21/43 rejected crops and even pages 15/37; these small section/parity groups do not isolate a parity effect. Pages 41,105,165 and173 each have two sampled crop failures, but only two targets per page. The multi-column pages 129–130 have no evaluated recognition row. [Diagnosis](follow-up/2026-10-07/endpoint-record-v1/diagnosis.json), `by_section`, `by_margin_side`, `by_page_parity`, `by_page` and `count_page_failures`.

## Quarantine, release requirements and review cost

**All 11,369 original occurrences remain quarantined; zero are released.** The original 9,584-row triage queue prioritizes work and does not certify its other 1,785 rows. The repaired sample failed four global criteria, so high confidence cannot release an individual row under the frozen rule. An automatic route would need a separate layout/editorial-unit repair, a new method freeze and fresh blind evaluation passing all five criteria. Each eligible row would still require resolved orientation and complete geometry, singleton codes, independent numeric-witness agreement, no unresolved editorial/boundary ambiguity, minimum unit confidence 0.90 and confidence product 0.90. Preserve variants and losses; the count reference excludes unnumbered continuations, so a complete transcription must explicitly attach those source lines to their numbered occurrence. L import additionally requires reviewed carrier identity and occurrence-surface alignment. [Frozen rule](repair/2026-10-07-v2/freeze-manifest.json), `release_rule`; [import contract](IMPORT_INTERFACE.md).

A review route uses the recognizer to propose codes and requires a complete human source check plus a second independent AI reading for each occurrence, followed by adjudication and a separately specified, validated acceptance rule. That means at least **11,369 human readings and 11,369 AI readings**, before recovering missing rows or checking complete line/side coverage. Applying the repaired 80-row rates to that provisional occurrence count projects about **5,116 crop corrections**, **2,984 count corrections**, **8,527 top-one sequence corrections**, **5,685 rows with a top-five proposal miss**, **2,558 number corrections** and **3,553 classification corrections**. Corrections overlap and cannot be added. Crop and top-five planning ranges from the sample Wilson intervals are 3,931–6,353 and 4,468–6,901 respectively. The frames/section weights differ and these projections estimate work under stated assumptions, not an edition error census. [Workload](follow-up/2026-10-07/endpoint-record-v1/review-workload.json), `projections` and `extrapolation_note`.

The two AI readings disagree on strict sets in 15/80 rows (19/352 units), projecting about **2,132 adjudication rows** (sample-based range 1,331–3,258). Human/AI disagreement has not been measured. The four 40-row task records sum to 13,810 elapsed seconds for 160 readings: 86.3 seconds per reading and about **272.6 summed task hours** for one AI pass through 11,369 rows. Six reading tasks including page counts sum to 16,037 seconds; their recorded wall span is 5,679 seconds because tasks overlap. These include tool latency and source inspection, and some start times are approximate. They are not human throughput measurements. At assumed human check times of one, two or five minutes per row, the human pass needs **189.5, 379.0 or 947.4 hours**, plus source recovery, adjudication, continuation checking and ledger joins. Adjudicator elapsed time, token usage and billed dollars are absent from the supplied records; monetary cost remains unknown. [Workload](follow-up/2026-10-07/endpoint-record-v1/review-workload.json), `observed_reader_task_timing`, `human_scenarios` and cost-null fields.

## Portable evidence and Package L

The unchanged evaluator can now read the exact frozen predictions from an owned portable input root. The existing digit NPZ, all 60 source crops and nine chart sheets are listed with hashes in [portable-input-manifest.json](follow-up/2026-10-07/analysis-v1/portable-input-manifest.json) and [TRACK-EXCEPTIONS.txt](TRACK-EXCEPTIONS.txt). Tracking exceptions still require coordinator integration. The [retrospective freeze supplement](follow-up/2026-10-07/analysis-v1/freeze-supplement.json) records the evaluator hash without backdating it. The portable rerun is byte-identical to the original metrics: SHA256 `5cd4b8df754a4284b8bdb7e333f9b2b860cdb377b1f47698533e613c0fcc8c06`.

Package L's available [contract](../2026-10-07-object-ledger/HELSINKI-INTERFACE.md) and review-response amendment are now implemented by `import_helsinki1979_v2.py`. Its requested `IMPORT_INTERFACE.md` is absent. A read-only check exercised 63 existing provisional occurrences, including three letter-suffixed strings: all schema checks passed, zero were accepted and all 63 were quarantined without identity/surface concordances. [Interface check](follow-up/2026-10-07/ledger-interface-v2.json). No Package L file or ledger was changed. The four inspected 1980 Finnish-to-Mahadevan pairs remain local and supply no verified CISI/carrier join.
