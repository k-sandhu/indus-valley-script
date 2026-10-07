# Review of package M: digitizing the CC BY 1979 Helsinki corpus

Reviewer: Claude (Sonnet 5.5), 7 October 2026. Package produced by GPT-6.1-Sol. All reviewer outputs are in `review/reviewer-check/`. The directory `review/2026-10-07-v1/` belongs to the package (its priority queue) and was not touched.

## Verdict

The main results stand: the frozen evaluation fails all four criteria, and nothing I found changes that. The evaluator and the 60-row recomputation reproduce exactly, the six freeze hashes match, the code, manifest, selection and predictions all predate the first reference file, and 43 headline numbers in the README and REPORT agree with the saved outputs, the main counts recomputed from the references and predictions. My reading of 30 rows from 5x renders (360 dpi equivalent) of the 600 dpi scan matches the reference on unit count, printed number and classification in all 30, including every disputed row (samples 14–16, 24, 29, 30, 35 and crop decisions 5, 13, 42, 51). Of 46 unit-level disagreements between the reference and the pipeline's top-one code, the reference is right in 33, the pipeline in 3, neither in 1, and 9 cannot be decided. Two reported figures need restating. The crop figure (23/60) mixes annotators A and B, who accepted 7 of 40 boxes, with annotator C, who accepted 16 of 20, 9 of which contain ink from the printed number, a neighbouring row or a drawing clipped by 1 pt or more; an edge test that ignores the labels passes 14 of 60 boxes (21 with a 1 pt tolerance). The 60-row estimate also covers only the numbered section (3,460 of the 11,369 extracted rows). The failure is page geometry: 32 of the 36 rows that fail top-five compatibility fail first at the crop or number-field boundary and 3 sit on a mis-rotated page. The printed number field lies +7.4 pt (even PDF pages) or −3.2 pt (odd pages) from the pipeline's fixed window, and all 17 pages the orientation heuristic rotated by 180 degrees are upright. Moving the window by the offset measured from the PDF's OCR layer, with upright pages and everything else frozen, raises count agreement from 33/60 to 44/60 and strict top-five whole rows from 24/60 to 35/60 (exploratory). The most important problem for the repository is that the frozen evidence cannot be re-audited from a clean clone: `development/digits.npz`, the frozen predictions file and the 60 annotated crops are git-ignored, so the freeze check, `evaluate.py` and `verify.py` fail without them.

## How this review was done

Reproduction used the package's own scripts with outputs redirected into `review/reviewer-check/`. All other analysis ran after the predictions and references were available; it diagnoses the frozen outcome, leaves it unchanged and is labelled Exploratory. My readings audit the reference against the images and are not blind. I viewed rows at 5x, unit galleries at 6x and single digit fields at 14x, and compared drawings with the chart atlas cells in `output/chart_atlas/`. The edge test has six parts, run on the native 600 dpi page image or the frozen unit lists: (1) an ink component of 40 pixels or more crosses the margin-side box edge; (2) the pipeline emitted a narrow unit (14 pt or less) at the number edge that no reference unit matches; (3) such a unit sits at the top or bottom strip edge; (4) ink crosses the top or bottom edge; (5) a reference unit is lost without an extra unit; (6) the page was rotated by the heuristic. I applied it with no tolerance and with crossings under 1 pt ignored (parts 1 and 4). Intervals are Wilson 95% unless stated. Effort figures in the recommendation are my estimates for one developer or annotator; the measured rates are this package's run times and its annotators' wall-clock times.

## Checked claims

| Claim | Evidence | Result | Note |
|---|---|---|---|
| Code, chart, model, digit classifier, calibration and PDF hashes equal the freeze manifest | `freeze-manifest.json`; `sha256sum` of each file | confirmed | `pipeline.py` edddcbd0…, `chart-snapshot.json` 09cc3116…, `classifier.pt` fd541c3c…, `digits.npz` 6720bdc1…, `calibration.json` dfc4a801…, PDF 7bfc35f2…. `selection.json` hash equals `prediction-freeze.json`; manifest hash equals `selection.json` field `frozen_manifest_sha256`. |
| Freeze precedes selection, predictions and references | file creation and write times | confirmed | `pipeline.py` last written 10:10:01, manifest 10:10:06, selection 10:10:15, predictions and `prediction-freeze.json` 10:20:35, first annotator work files 10:25:08 (B), 10:25:31 (A), 10:29:29 (C), references 10:31:48 (C), 10:35:29 (B), 10:43:00 (A). Reference `created_utc` fields agree. |
| References made without predictions | `chronology` and `blinding` fields; times above | consistent, unverifiable | Self-reported by each annotator; no access log exists. See the coupling through the chart sheets below. |
| Seeded selection of 60 rows from 3,460 | `selection-replication.json` | confirmed | Layout code rebuilt the 3,460-row frame and `random.Random(20261007).sample` returned the same 60 keys. |
| 23/60 crops, 33/60 counts, 23/60 numbers, 19/60 classifications, 13/60 top one, 24/60 top five, 10/52 unique sequences | `evaluation/2026-10-07-frozen-v1/metrics.json`; `numbers-check.json` | confirmed | Recomputed from references and predictions, not from the summary fields. The crop label count is accurate; its meaning is qualified below. |
| 288 predicted against 267 reference units (229 glyph, 38 editorial); 8 two-candidate units; 52 singleton rows | references, predictions | confirmed | |
| Wilson intervals, bootstrap intervals, aligned recall 199 and 224 of 267, edits 95 and 71, same-position 103 and 118 of 140, shape-only 15 and 25, mean width 5.208 | `metrics.json` | confirmed | 43 of 43 checks in `numbers-check.json`. |
| Brier 0.1488 and ten-bin error 0.1056 | `metrics.json` | confirmed | The 140 units include 14 units from rotated rows 15 and 16, all wrong. Without them: Brier 0.1262, error 0.1183, accuracy 0.817, mean confidence 0.748. |
| 13/38 numbers after excluding the 22 OCR-exposed rows | `metrics.json` exploratory block | confirmed | The pipeline reads 10 of 22 exposed rows correctly, so exposure does not favour it. |
| Six repeats: counts, numbers, classifications 6/6; identical candidate sets 4/6; crop judgments disagree on 4 | `evaluation/annotation-comparison-v1.json` | confirmed | My adjudication of all six is below. |
| Full run: 11,369 rows, 57,426 units, 159 pages, 10,425 numbers read, 3 unmatched; sections 4,036 / 3,743 / 3,590; 52.1 min | `coverage.json`; recount of `occurrences.jsonl` | confirmed | Payload SHA equals `coverage.json` and `hf-hosting-manifest.json`. |
| 17 pages rotated 180 degrees "need source review" | `coverage.json`; page images and OCR headers | discrepancy | All 17 are upright (13 by the OCR header word near the top, 4 by viewing). The rotation is wrong on 1,223 rows (10.8%). |
| "All pages yielded detected rows" | `coverage.json` | confirmed, incomplete | 20 pages have other than 72 rows. Page 62 column 0 prints 36 rows and the run found 21. Pages 129 and 130 print five to eight columns and yield 71 and 72 rows. |
| Review queue separates 946, 9,712 and 711 rows | `review/2026-10-07-v1/summary.json` | confirmed | The three classes sum to 11,369, so every row is queued. |
| All 11,369 staged rows quarantined; 0 of 60 accepted by Package L's importer | `integration/`; `ledger-import.jsonl` | confirmed | Every row has `disposition: quarantine`. |
| Page-30 development 17/20, 6/20, 12/20; calibration fit 81 positions, 61 correct; earlier pilots 14/20, 2/20, 5/20 and 18/20, 6/20, 16/20 | development files; `research/methods/results/` | confirmed | |
| Two large files backed up to the private dataset | `experiments/2026-10-06-research-program/hf-hosting-manifest.json` | confirmed locally | Local SHA-256 and sizes equal the manifest; the remote copy is not checkable without credentials. |
| CC BY 4.0 attribution recorded | `README.md`, `sources.json`, `rights` object in every staged row | confirmed | Rows of `occurrences.jsonl` carry only `licence: CC BY 4.0`; attribution sits in the README and the staged rows. |

## Reproduction log

| Command (from the repository root) | Result |
|---|---|
| `evaluate.py --out review/reviewer-check/evaluation-recompute` | 1 s. `metrics.json` SHA-256 5cd4b8df… is byte-identical to the frozen and `recompute-v1` files. |
| `rerun_frozen_sample.py --predictions-out data/raw/…/reviewer-sample-v3.json --audit-out review/reviewer-check/sample-rerun-reviewer.json` | 49 s on the CUDA device. 60 of 60 rows reproduce number, classification, strip box, orientation, unit boundaries and top-five template keys; largest confidence difference 0.0. |
| `verify.py --out review/reviewer-check/verify-reviewer.json` | 25 of 25 checks true; recorded storage 423.2 MB against the 500 MB limit (175 MB of it installed dependencies). |
| `pipeline.py full` | Not rerun (52 minutes, about 100 MB). I recounted rows, units, numbers, unmatched units and pages from `occurrences.jsonl` and checked its hash instead. |
| `tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write` | 0 flags on the package's 8 Markdown files and on this review. Manual findings are in the writing section. |

The scripts behind the other numbers in this review are in `review/reviewer-check/scripts/` and run from the repository root.

## Source checks

Only three sources are cited in `sources.json`; I checked all three, and none is marked snippet-only.

| Source | What I opened | Result |
|---|---|---|
| Koskenniemi and Parpola, *Corpus of Texts in the Indus Script*, 1979 | Research portal entry; local PDF pp. 1, 2, 16–18 | Title, authors, year, Research Reports vol. 1, Department of Asian and African Studies, ISBN 951-45-1627-3, 179 pages, CC BY all match. The local file is 16,935,355 bytes, 180 PDF pages, SHA-256 as recorded. Pages 16–18 define rank and code numbers and the auxiliary signs as cited; p. 18 names the CalComp plotter. The handle `hdl.handle.net/10138/342677` redirects to `helda.helsinki.fi`, which returned an anti-bot challenge page, so the handle page itself is unverified. PDF page 1 carries the same HELDA citation and handle. |
| Koskenniemi and Parpola, *Documentation and Duplicates of the Texts in the Indus Script*, 1980 | Local PDF; the `tuhat.helsinki.fi` URL in `sources.json`; PDF pp. 24, 26, 27 | The URL serves a file with the same SHA-256 (0ced4102…) and size (8,143,483 bytes) as the local copy: 98 pages, Research Reports No. 2, ISBN 951-45-2149-8. §2.1 is on PDF 24, the §2.2 title on 26 and §2.2.1 "Finnish to Mahadevan" on 27. The OCR layer reads 0002 = 3230 and the image reads 3234, as the package states. The fetch tool stored the PDF; I deleted that copy. |
| Creative Commons, Attribution 4.0 International | Licence deed | The attribution and "indicate if you modified" conditions match the package's modification notice. |

## Freeze and reference independence

The freeze is sound. Two parts of the protocol cannot be dated separately: the comparison plan for repeated readings and the later disclosure paragraph. `PROTOCOL.md` was last written at 10:26:01, after annotation began, and Git holds one committed version. The annotator notes say each read the protocol before release, which fits the plan paragraph predating annotation. `evaluate.py` was created at 10:14:49 and last written at 10:27:44, before any reference existed, but `prediction-freeze.json` does not record its hash.

Three features of the reference design limit what its labels can show.

- **Chart sheets without vertical position.** The sheets given to annotators (`blind/chart_sheets/`) were drawn by `pipeline.make_chart_sheets` from tight-cropped templates. Chart codes 2 and 25 are the same two short strokes at different heights: code 25 at the top of the sign box (1.2 px below the tallest drawing's top), code 2 near its middle (14.2 px). Annotator A recorded 25 for three units; annotators B and C recorded 2 for eight units. In all eleven the strokes sit at the top of the line (ten seen on 5x renders, sample 18 by measurement); the measured offset is 0–2 px for samples 0, 18, 24, 25, 31, 51 and 59 (`diagnosis/tick-position-check.json`), and the 8 and 7 px measured for samples 34 and 52 come from neighbouring-row ink at the strip top. The pipeline also has no position feature and ranks 2 first, so the eight units agree with it for the same reason.
- **Locator geometry and OCR strings.** `selection.json` carried the source PDF's OCR strings for 22 rows, and its context boxes follow the pipeline's geometry, so rows with right-shifted fields reached annotators with truncated number fields (rows 24, 25 and 29 needed a wider render). I read those three numbers (2429, 2559, 2892) from wide renders and they match the reference.
- **Repeated rows.** The six repeated rows (5, 13, 30, 35, 42, 51) have no stated selection rule, and five of the six have count mismatches in the pipeline output. The 6/6 and 4/6 agreement figures describe these rows only.

The 60-row sample contains six rows from page 78 (57 of the 3,460 frame rows, so 1.0 expected; probability of six or more 0.0004). The draw replicates from the seed, so this is a chance concentration, but page 78 is the best-performing page: without it, counts agree on 27 of 54 rows and strict top-five whole rows on 20 of 54.

## Independent readings of the disputed rows

| Sample | Package flag | My reading of the source | Right |
|---|---|---|---|
| 14, 15, 16 | page 37 crops inverted | Page 37 is upright in the PDF. Reference counts 4, 8, 6, numbers 1582, 1562, 1541 and classifications `62 99`, `69 98`, `11 40` match what I read. The pipeline's 8, 8, 6 units and numbers 6609, 8659, 0111 come from reading the strips upside down. | reference |
| 24 | 9 against 8 units; number None | Nine drawings, 2429, `11 40`. The ninth drawing begins 6 pt beyond the box edge; the number field starts 21 pt right of the fixed window. | reference |
| 29 | 4 against 3 units | Four drawings (underlined U, three hatched patches), 2892, `11 90`; the fourth lies beyond the box. | reference |
| 30 | 6 against 5 units; candidate sets differ | Six drawings. The pipeline merged the second arrow with the tick pair (gap 7.4 pt, below its 9.5 pt join limit). The ticks sit at the line top, chart code 25; B recorded 2 and A's repeat recorded 25. | reference on count; repeat on code |
| 35 | 9 against 10 units; two set differences | Nine drawings. The first and last hatched patches are narrow (about 6.5 pt, chart codes 597 and 13); B recorded the wide codes 599 and 106, A's repeat 597 and 13. The pipeline's tenth unit is the leading digit. | reference on count; repeat on codes |
| 5 | crop False (A), True (C) | The box ends at 254 pt and the leading 1 of 1251 begins at 251.7 pt, so it is in the box. | A |
| 13 | False (A), True (C) | The bar stack ends 2 pt beyond the box edge. | A |
| 42 | True (C), False (B) | The leading 4 of 4112 lies wholly inside the box and the pipeline emitted a unit for it. | B |
| 51 | True (C), False (B) | A 0.4 pt sliver of the leading 6 is inside the box and the pipeline emitted a unit for it. | B, marginally |

The stricter annotator is right in all four crop disputes. The remaining 19 rows I read (0, 4, 20, 25, 31, 33, 34, 36, 37, 39, 40, 41, 43, 44, 49, 50, 52, 57, 59) agree with the reference on counts, numbers and classification strings; at 5x I misread one classification digit in sample 34, and a 14x zoom confirmed the reference (`52647`). Counts and numbers for each row are in `independent-rereads.json`.

At unit level I looked at all 46 aligned pairs (excluding page 37) whose top-one set misses the strict reference set, comparing the source unit at 6x with the chart cells for the reference code and the pipeline's top two (`unit-adjudication.json`). The reference is right in 33 pairs. The pipeline is right in 3 because the reference has the wrong code: sample 10 unit 4 (four ticks over three is code 19, the reference has 17), sample 25 unit 0 (ticks at the line top, code 25, reference 2) and sample 35 unit 2 (narrow patch 597, reference 599). In a fourth pair (sample 35 unit 8) both are wrong: the reference has the wide code 106 and the pipeline the unmarked 597, while the printed patch is narrow and underlined, code 13. Nine pairs I could not decide, mostly code pairs that look the same in the chart cells (8 and 764, 133 and 394). Correcting those four pairs and the other seven tick units (samples 24, 30, 31, 34, 51, 52, 59) moves the aligned top-one count from 198 to 195 of 244 and whole-row top one from 13 to 11; whole-row top five stays at 24.

## Why the pipeline failed

The four stages are not independent, so the table gives the first stage at which a failing row goes wrong and the number of rows each stage touches.

| Stage | Rows where it fails first (of 36 failing strict top five) | Rows it touches |
|---|---|---|
| Page orientation | 3 | 3 |
| Crop or number-field geometry | 32 | 32 |
| Unit segmentation (merge or split) | 0 | 3 |
| Glyph classification or reference convention | 1 | 11 |

The 27 rows with a wrong unit count split into 18 with a number-field fragment inside the glyph strip, 3 where the strip clips or loses the last drawing (24, 29, 33), 3 with ink from the neighbouring row's underline at the strip top (34, 49, 50), 2 merges (30, 43) and 1 rotated page. A fragment is the leading digit of the printed number: a unit 1 to 19 pixels wide at the strip's number-side edge, read as a small chart sign (the single stroke 764 or 1 most often); the calibrated confidence of 17 of the 18 fragments is 0.42–0.68. Of the 37 wrong numbers, 34 occur in rows that fail an objective edge or rotation test, and 38 of 41 wrong classification strings do; the three exceptions for numbers are rows 2, 40 and 44, a leading digit lost or read as 1. Vertical row boundaries are mostly sound: an ink component crosses the top or bottom box edge in only 1.7% and 2.3% of the 11,369 rows, and 139 of 159 pages return 72 rows.

**Page geometry.** The source OCR layer gives the left edge of 4-digit words for 72 page-columns in the numbered section (`ocr-field-drift.json`). Their offset from the pipeline's fixed field position ranges from −11.2 to +18.5 pt, against a field window 24 pt wide. Even PDF pages average +7.4 pt (SD 5.6, 22 pages) and odd pages −3.2 pt (SD 3.1, 20 pages), so the window is wrong in opposite directions on the two page types; the development page 30 sits at +5.0 and +2.8 pt. In the sample, rows on even pages agree on count in 21 of 27 and rows on odd pages in 12 of 33 (Fisher exact p = 0.002); exact numbers 16/27 against 7/33 (p = 0.004); strict top five 15/27 against 9/33 (p = 0.035). These parity comparisons were chosen after seeing the results. Within the 38 non-rotated rows that have an offset estimate:

| Offset of the field from the fixed window | Rows | Counts right | Numbers right | Classifications right |
|---|---|---|---|---|
| within ±1.5 pt | 10 | 8 | 8 | 8 |
| more than 1.5 pt left (leading digits inside the strip) | 13 | 1 | 0 | 0 |
| more than 1.5 pt right (last drawing clipped, digits outside the field) | 15 | 12 | 8 | 5 |

The pipeline's own page score shows the same pattern without any reference: `anchor_score` counts the number bands the field window found, and 13 pages (914 rows) have fewer than 36 of about 72, including pages 44, 46, 48, 50, 52, 54, 56 and 60, all even. On the full run, an ink component crosses the margin-side box edge in 3,537 of the 11,369 rows (31.1%) on pages left unrotated, by more than 1 pt in 22.5% of all rows and more than 2 pt in 14.5%. Together with the 10.8% of rows on rotated pages, 41.9% (4,760) of the provisional rows have a clipped margin edge or an inverted page.

**Orientation.** The score for "right margin, upright" and for its mirror "left margin, rotated 180°" is nearly equal on a page of two symmetric columns: on page 37 the scores were 69 and 70, and the larger won. The 17 rotated pages hold 72 numbered-section rows, 575 end-sorted rows and 576 beginning-sorted rows, so the 3 rotated rows in the 60-row sample (5%) understate the full run (10.8%, and 15–16% in the two sorted sections).

**Row recall.** The frame is built from detected rows, so omissions are invisible to the sample. Of the 20 pages with fewer than 72 rows I checked four against the page images: page 62 is 15 rows short (column 0 prints 36 and the run found 21), page 66 is 9 short and page 78 about 5 short, while page 180 is the short last page. Pages 129 and 130 (printed 128 and 129) fall within the printed pp. 127–129 that page 180's note gives as the list of single-auxiliary-sign texts; they hold five to eight columns of short entries, and the two-column reading yields 71 and 72 rows for them, roughly 300 fewer than the pages print (a visual estimate from thumbnails).

**Recognition.** Among the 198 aligned units whose crop size is within 10% of the correct chart template, the frozen matcher has the correct code first in 182 (91.9%) and within the top five in all 198. Across the 244 aligned units of the 57 non-rotated rows, top-one accuracy is 81.1% and top-five 91.0% (at rank level 84.8% and 94.3%); by unit type top one is 169 of 195 for plain glyphs, 4 of 16 for underlined units and 25 of 33 for unmarked editorial patches. Of the 46 top-one disagreements, 23 follow from the crop: the dashed underline lies outside the box for 10 units whose chart code includes it, the box edge clips 7, 3 are merged units, 1 is a split, 1 is margin leakage and 1 is neighbouring-row ink. A further 19 are classification proper: 12 fine inner-mark variants (fish 177, 178, 179; triangle 103, 104), 6 position-dependent pairs and 1 hatched patch with a sign inside. The last 4 are reference errors.

**Resolution.** All pages but the cover are 1-bit PNGs of 4,880 × 7,010 pixels at 601 dpi (8.34 px/pt). The sampled units have median height 123 px and width 70 px, with strokes about 4 px thick. The pipeline renders at 2 px/pt, which gives 30 × 17 px units and strokes near 1 px, a 4.2-fold linear reduction. Scan resolution does not limit recognition. I reran the frozen matching method on the frozen unit boxes at other render scales (`resolution-and-matcher-tests.json`):

| Render scale (px/pt) | 1 | 2 (frozen) | 3 | 4 | 6 | 8.34 (native) |
|---|---|---|---|---|---|---|
| Top one of 244 aligned units | 58 | 198 | 189 | 189 | 171 | 165 |
| Top five of 244 | 132 | 222 | 216 | 214 | 183 | 179 |

The matcher peaks at the scale it was developed at. At 4 px/pt it gains 10 units and loses 19, so more pixels alone do not help. A parameter-free cross-correlation matcher on the same units scores 182 and 208 at 2 px/pt and does no better on size-consistent crops (174 of 198 against 182 of 198), so the residual 8% is a matter of variant conventions and position, which a new scan would not touch. The 1979 text (PDF p. 18) says the signs were drawn by a CalComp plotter from one stroke font; a registration-based match against exact templates is therefore a sound basis once crops are right.

**Comparison with the fresh-20 pilot.**

| Run | Rows | Counts right | Strict top-one rows | Strict top-five rows | Edits per reference unit, top one and five |
|---|---|---|---|---|---|
| Fresh-20, frozen (fixed pitch, page 30) | 20 | 14 (48–86%) | 2 (3–30%) | 5 (11–47%) | 0.72, 0.63 |
| Fresh-20, post-reference crop repair | 20 | 18 | 6 | 16 | 0.25, 0.06 |
| New pipeline, development (page 30) | 20 | 17 | 6 | 12 | 0.27, 0.14 |
| New pipeline, frozen test (33 pages) | 60 | 33 (43–67%) | 13 (13–34%) | 24 (29–53%) | 0.36, 0.27 |
| Same rows, offset and orientation repaired (exploratory) | 60 | 44 | 22 | 35 | not computed |

The edit rate per unit halved against the original pilot, while whole-row proportions overlap within their intervals. On its development page the new pipeline matches the repaired-crop diagnostic at top one and falls short at top five; on fresh pages its top-five edit rate doubles. The earlier pilot drew every row from one page, so neither it nor the development page measures layout generalization.

## Recommended next approach

Repair the layout stage first, keep the recognizer as a proposal generator, then verify every row by human checking with a second AI reader to expose disagreements (approaches A, E and C below, in that order). The evidence is above: 32 of 36 failing rows fail at the geometry, the recognizer's top five contains the right code for every size-consistent unit, the matcher does not improve with scale or with a different scoring rule, and moving the field window with upright orientation recovered 11 count matches, 17 numbers and 11 top-five rows with no other edit. The test moved the window for the 39 rows that have an OCR-based offset estimate; on those rows counts rise from 21 to 34 of 39, numbers from 16 to 33, classifications from 13 to 31 and top-five rows from 16 to 27 (`shift-oracle-test.json`). The 21 rows without an estimate did not improve (counts 12 to 10, numbers 7 to 7). The test used the same rows that motivated it, so it shows feasibility and gives no new accuracy estimate.

| Approach | What the evidence says | Estimated effort | Main risk |
|---|---|---|---|
| A. Repair layout, freeze, retest | Orientation: set upright after a header check (13 of the 17 rotated pages are confirmed upright by the OCR header word, the other 4 by viewing). Field edges per page and column from the OCR word boxes with an ink-projection fallback and a parity prior. Strip ends at the field edge minus a margin and reaches below the underline dashes. Reject slivers at the number edge. A column detector for pages 129–130. | 6–8 working days for one developer, including a new frozen sample of at least 100 rows read by two annotators under one written convention sheet. Full run 52 min; 60-row rerun 49 s. | Even and odd pages vary within type (SD 5.6 and 3.1 pt); page types not yet seen; the protocol thresholds (95% counts, 90% numbers) may stay out of reach without verification. |
| B. Better unit segmentation | Segmentation proper explains 3 of 36 failing rows (merges at gaps of 7–11 pt, the double hatched patch 762 split in two). | 2–3 days after A, with chart composites as a lexicon. | Little measurable gain until A is done. |
| C. VLM reading against the chart with human checking | The reference is such a reading. It matches my reading on 30 of 30 rows and on 33 of the 37 decidable unit disagreements. In the six repeats the three candidate-set differences among 26 units are all convention errors of the first reader. | About 1–2 days for a harness with position-aware chart cards. The package's annotators needed 0.5–0.9 min per row (10–18 min per 20 rows), so 11,369 rows is about 95–170 agent-hours, parallelizable; token volume was not recorded. | Convention drift (ticks 2 and 25, narrow and wide hatched patches, underline codes) unless a sheet pins them; fine inner-mark variants. |
| D. Higher-resolution scan | The PDF is 601 dpi bilevel; the matcher does not use it above 2 px/pt. | Not recommended. | |
| E. Manual annotation under a written protocol | Needed for any reliable claim. With proposals from A: assume 2 s to confirm a correct first candidate (92% of clean units), 8 s to choose among five, 8 s per row for count, number, classification and orientation, and 20 s extra on the 20% of rows still defective after repair: about 80 hours per pass. | About 150–200 hours with a second pass and adjudication. Unaided coding at 15–25 s per unit is 300–460 hours for one pass. | Annotator conventions; needs the convention sheet from C. |

Approach B is worth doing only if the retest after A still shows merged or split units in more than a few percent of rows; D can be dropped. Four further steps need no new method.

- Numbering order. In the numbered section the reference numbers increase strictly in page, column and row order (0 violations in 59 consecutive pairs), so the order can repair numbers on pages 22–78. The package found 490 non-increasing pairs among the recognized values.
- Cross-section agreement. Each text appears up to three times (numbered, end-sorted, beginning-sorted). The package's repeated-number groups agree exactly at top one in 372 of 2,616 cases, which gives a reference-free accuracy monitor as the geometry improves.
- Triage. Rank rows by objective signals (page `anchor_score`, edge crossing, narrow edge unit, rotation, numbering violation, cross-section disagreement) in place of the confidence threshold that currently queues every row.
- Cross-check lead. The object-ledger amendment names CISI 1 p. 365's Finnish Concordance column as a bridge for the unfinished cross-check; I did not open it.

## Quarantine, rights and attribution

Quarantine holds. All 11,369 staged rows have `disposition: quarantine` and `review_status: automatic_provisional_requires_review`; the object ledger's `ledger-public.json` contains no 1979 transcription (0 matches for the edition string); no `with-helsinki` build or import output exists; no other tracked file cites the extraction's totals; and the package text calls the output provisional and the corpus unfinished throughout. The 1979 attribution (authors, title, year, publisher, handle, licence, modifications) is in the README, `sources.json` and the `rights` object of every staged row. The 1980 edition's copied rows and renders stay local, and the one tracked trace is a single number pair in `concordance-search.json`. This matches `knowledge/provenance/REDISTRIBUTION.md`.

## Writing

`review_prose.py` reports no flags. Reading the text, I found these passages unclear or dense. The README's "Files and source attribution" paragraph packs twelve links into 79 words and the "Reviewer checks" paragraph is a task list written as prose; both read better as lists. The PROTOCOL amendment dated before selection combines about a dozen separate decisions in one 195-word paragraph. Several sentences are too compressed to parse on first reading: "Initial references remain unchanged" (README), "Strict top one happened to have singleton labels in every prediction" and "Top five means five image templates with retained numeric ambiguity, yielding a mean 5.208 codes" (REPORT), and "Our new code/prose have no separately assigned blanket licence" (README). The README results paragraph gives "crop judgments disagree on four" without the base of six. The caveat words "provisional" and "quarantine" appear about 17 times across the five main documents, which is acceptable. The REPORT states the evaluation frame (pages 31–79) in the method section, away from the results table where it qualifies every figure.

## Boundaries

`git status --porcelain` shows two untracked paths from this review, `experiments/2026-10-07-helsinki1979-digitization/REVIEW.md` and `experiments/2026-10-07-helsinki1979-digitization/review/reviewer-check/`; no tracked package file changed. The other changed paths belong to the object-ledger package, which was being revised in parallel while this review ran (a modified `experiments/2026-10-07-object-ledger/PROTOCOL.md` and new untracked scripts, an amendment and output directories under that package). I ran no command that changes history and left no `__pycache__` in the package. The only local raw file I kept is `data/raw/2026-10-07-helsinki1979-digitization/reviewer-sample-v3.json` (the recomputed predictions, 1 MB); the page renders, the 1980 crop and other temporary files were deleted.

## Required fixes, ranked

1. Make the frozen evidence recoverable. Track or host with hashes `development/digits.npz` (12.9 KB), `data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json` (1.07 MB), the 60 `blind/row_*.png` crops and `blind/chart_sheets/*.png`. `file-manifest.jsonl` records their hashes, so a restored copy can be checked, but neither Git nor `hf-hosting-manifest.json` holds the files. The 1979 crops are CC BY and `REDISTRIBUTION.md` allows selected crops with attribution. Until then `check_freeze`, `evaluate.py`, `rerun_frozen_sample.py` and `verify.py` fail on a clean clone.
2. Restate the crop figure. Give the per-annotator counts (4/20, 3/20, 16/20), say that 9 of annotator C's 16 acceptances contain ink from the printed number, a neighbouring row or a drawing clipped by 1 pt or more (11 with no tolerance), and add the objective result (14 of 60 boxes pass the edge tests, 21 with a 1 pt tolerance; removing rows with defects the annotators themselves noted leaves 12 and 14). Keep 23/60 as the frozen value.
3. Put the evaluation frame beside every headline figure in the README and the REPORT results section: pages 31–79, 3,460 of 11,369 detected rows, no sorted-section row evaluated, and the sorted sections hold 64.5% of the extraction and 15–16% of their rows on mis-rotated pages.
4. Replace "those values need source review" with the finding that all 17 rotated pages are upright, and mark their 1,223 rows (`orientation_unreliable`) in the queue.
5. Record row-recall evidence: the 20 pages with fewer than 72 rows, page 62 column 0 and pages 129–130.
6. Add a dated adjudication note, leaving the frozen references unedited, that lists the reference errors found (sample 10 unit 4, sample 35 units 2 and 8, and the tick units of samples 24, 25, 30, 31, 34, 51, 52 and 59), the tick convention, and that the repeat readings were right on both candidate-set disagreements.
7. Record the evaluator hash with the prediction freeze, or note that `evaluate.py` was last written at 10:27:44, during annotation and before any reference.

## Optional improvements

- Report rank-level accuracy and edits per reference unit next to code-level results, for comparison with the earlier pilot.
- Report the calibration figures without the rotated-row units, and note that spurious fragment units carry confidence 0.42–0.68, all below the 0.75 review threshold.
- Put a CC BY attribution sidecar beside `occurrences.jsonl` and `ledger-import.jsonl`, whose rows carry only the licence name or the staging fields.
- Direct the README's rerun commands to `review/` or a dated folder, so reviewers need not write into `evaluation/` and `verification/`.
- Split the long README and PROTOCOL paragraphs into lists and rewrite the unclear sentences above.
- State the rule for choosing the six repeated rows.

## Files written by this review

`REVIEW.md`; under `review/reviewer-check/`: `evaluation-recompute/metrics.json`, `sample-rerun-reviewer.json`, `verify-reviewer.json`, `logs/`, `numbers-check.json`, `selection-replication.json`, `independent-rereads.json`, `unit-adjudication.json`; `diagnosis/` with `diagnosis.json`, `stage-attribution.json`, `crop-audit-summary.json`, `boundary-cut-sample60.json`, `boundary-cut-full.json`, `full-run-summary.json`, `ocr-field-drift.json`, `scan-resolution.json`, `tick-position-check.json`, `gallery-top1-index.json`, `resolution-and-matcher-tests.json`, `shift-oracle-test.json` and `raw-unit-results/`; and the scripts that produced them in `scripts/`. Total about 2.5 MB.
