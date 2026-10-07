# Helsinki 1979 digitization: corrected first endpoint and repair status

The first pipeline failed all four reliability criteria. Its **60-row evaluation covers only numbered-section targets from PDF pages 31–79, drawn from 3,460 of the 11,369 detected occurrences; no sorted-section row was evaluated**. In that frame it has 33 matching unit counts, 23 exact numbers and 24 compatible whole rows within five templates. These original outcomes and references remain unchanged. The [Sonnet review](REVIEW.md) confirmed all 43 checked headline numbers and diagnosed page geometry as the main limitation.

The repair now has a frozen method and 80-row sample across all three sections. Its two independent readings, source-count reference, adjudication and evaluation remain unfinished after the disk cutoff was triggered. No repaired accuracy is reported and no row has been released from quarantine. [Stop record](follow-up/2026-10-07/storage-stop-v2.json).

## First endpoint: numbered-section frame only

Every figure in this table uses the original 60 numbered-section rows from PDF 31–79 (detected frame 3,460/11,369; zero sorted-section targets). The code metrics compare the original AI reference labels, including the errors subsequently found by review.

| Original outcome in that frame | Result |
|---|---|
| Annotator crop acceptance | 23/60 (38.3%; 95% CI 27.1–51.0%) |
| Drawing-unit count agreement | 33/60 (55.0%; 95% CI 42.5–66.9%) |
| Exact inscription number, with suffix | 23/60 (38.3%; 95% CI 27.1–51.0%) |
| Exact classification, with blank positions | 19/60 (31.7%; 95% CI 21.3–44.2%) |
| Compatible whole row, top one | 13/60 (21.7%; 95% CI 13.1–33.6%) |
| Compatible whole row, top five | 24/60 (40.0%; 95% CI 28.6–52.6%) |
| Exact sequence on singleton-reference rows | 10/52 (19.2%; 95% CI 10.8–31.9%) |

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

Twenty pages have fewer than 72 detections. Their numbers and counts are in [row-recall-evidence.json](follow-up/2026-10-07/analysis-v1/row-recall-evidence.json), `short_pages`. The review counted 36 printed rows in page 62 column 0, where the first pipeline found 21: count coverage 21/36 (58.3%; Wilson 95% CI 42.2–72.9%). This is a count comparison, not a corpus-wide matched-row recall estimate. Pages 129–130 print five to eight columns; the first method searched two. Fewer than 72 detections can also reflect a partial page, so it does not establish a missing-row count by itself. An independent true-row denominator remains unfinished.

The active [triage queue](follow-up/2026-10-07/analysis-v1/triage-queue.jsonl) contains 9,584 rows, leaving 1,785 outside triage. Priorities contain 1,352 orientation/column/recall cases, 4,324 clipping/fragment cases, 723 field/order cases and 3,185 remaining repeat-disagreement cases. It uses native edge crossings of at least one point, narrow number-edge units, unresolved fields, unmatched ink, numbering violations and candidate disagreements between unverified number groups. It omits the universal boundary/classification flag and the old confidence cutoff that queued every row. **All 11,369 remain quarantined**, including rows outside triage. [Summary](follow-up/2026-10-07/analysis-v1/triage-summary.json), `reason_counts` and `priorities`.

## Repair development, freezing and unfinished evaluation

The review measured mean field drift of +7.4 PDF points on even pages and −3.2 on odd pages, with offsets from −11 to +18. It found the correct code among five proposals for all 198 size-consistent units examined; its resolution tests found no benefit from increasing the working render above two pixels per point. The native scan is 601 dpi bilevel. These are conditional, post-outcome diagnoses. Its offset/orientation rerun on the old numbered-section 60-row frame yielded 44 matching counts, 40 numbers and 35 top-five whole rows, compared with the frozen 33, 23 and 24. It supplies development evidence and no fresh accuracy estimate.

The new layout localizes field coordinates from OCR word boxes without trusting their digit strings, checks compact multi-column pages through print projections and internal whitespace, and uses source-header content for upright orientation. It detects vertical field bands and intervening glyph whitespace without fixing row counts. On development pages the detector found 72 rows on pages 30, 62, 100 and 145, eight columns/288 rows on 129 and six columns/201 rows on 130. These are detector outputs, pending independent source counts. The known page-30 development reference gives 17/20 matching counts, 19/20 numbers, 6/20 top-one and 12/20 top-five whole rows. [Development output](follow-up/2026-10-07/development-recognition-v1.json).

The first repair candidate's unlabelled frame exposed false field columns from glyph-like OCR. It was superseded before any independent reading, with all artifacts preserved in `repair/2026-10-07-v1/`. The replacement adds a 35-point margin-neighbourhood restriction on ordinary two-column page types; compact printed columns remain detected separately. Its [freeze](repair/2026-10-07-v2/freeze-manifest.json) at 2026-10-07T16:54:51.431467+00:00 includes layout, sampling and evaluator hashes plus the unchanged original recognizer, digits, chart and calibration. Its [prediction freeze](repair/2026-10-07-v2/prediction-freeze.json) at 2026-10-07T16:58:06.116694+00:00 precedes every new reference: none exists.

| Evaluation component | First endpoint | Repaired endpoint |
|---|---|---|
| Frame | 60 numbered-section rows, PDF 31–79; 3,460/11,369 detected rows; no sorted target | 80 rows: 28 numbered, 26 end-sorted, 26 beginning-sorted; eligible denominators 3,596 / 3,228 / 3,496 |
| Independent readings | One primary reader per row; six convenience repeats | Two readings per row and source-only adjudication required; not started |
| Counts / numbers / top-five whole rows | 33/60 / 23/60 / 24/60 in the stated first frame | Pending |
| Row recall | No overall true-row denominator | 18 seeded pages plus stress pages 62,129,130 prepared; source count pending |
| Calibration | Original and upright-only sensitivity above | Pending |
| Quarantine | All 11,369 occurrences | No release allowed before evaluation and the frozen rule |

The 80-row sample uses seed 2026100780, excludes development pages and the old 60 targets, and includes both sorted sections. The prepared count frame has 21 pages. Two readers must independently annotate all rows and visually count/match every source column; a third source-only reader adjudicates before scoring. The [convention sheet](repair/2026-10-07-v2/blind/CONVENTIONS.md) preserves vertical tick position and editorial distinctions. Thresholds remain 90% crop/number accuracy, 95% count agreement and 80% top-five whole rows, with a new 95% random-page row-recall criterion. The frozen release rule further requires singleton codes, numeric-witness agreement, no unresolved geometry/auxiliaries, minimum unit confidence 0.90 and confidence product 0.90. It permits transcription eligibility only; a carrier import still needs reviewed identity and surface alignment.

Disk checks are in [storage-preframe-check-v2.json](follow-up/2026-10-07/storage-preframe-check-v2.json) and [storage-stop-v2.json](follow-up/2026-10-07/storage-stop-v2.json). Free space fell to 917,327,872 bytes and then 256,331,776 while the helper was active. The 60,522,244-byte frame had already been written by the failed gate check; the helper completed before interruption. This exposed a missing in-process pre-write gate. The completed artifacts are retained; no further evaluation or full run was started. Space recovered after the helper exited. This does not erase the recorded cutoff failure.

## Portable evidence and Package L

The unchanged evaluator can now read the exact frozen predictions from an owned portable input root. The existing digit NPZ, all 60 source crops and nine chart sheets are listed with hashes in [portable-input-manifest.json](follow-up/2026-10-07/analysis-v1/portable-input-manifest.json) and [TRACK-EXCEPTIONS.txt](TRACK-EXCEPTIONS.txt). Tracking exceptions still require coordinator integration. The [retrospective freeze supplement](follow-up/2026-10-07/analysis-v1/freeze-supplement.json) records the evaluator hash without backdating it. The portable rerun is byte-identical to the original metrics: SHA256 `5cd4b8df754a4284b8bdb7e333f9b2b860cdb377b1f47698533e613c0fcc8c06`.

Package L's available [contract](../2026-10-07-object-ledger/HELSINKI-INTERFACE.md) and review-response amendment are now implemented by `import_helsinki1979_v2.py`. Its requested `IMPORT_INTERFACE.md` is absent. A read-only check exercised 63 existing provisional occurrences, including three letter-suffixed strings: all schema checks passed, zero were accepted and all 63 were quarantined without identity/surface concordances. [Interface check](follow-up/2026-10-07/ledger-interface-v2.json). No Package L file or ledger was changed. The four inspected 1980 Finnish-to-Mahadevan pairs remain local and supply no verified CISI/carrier join.
