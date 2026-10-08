# Printed numbers on the 1979 chart

The proposed v2 reference changes eight primary codes and one upper class among 687 chart cells. It resolves all 16 retained lower-code ambiguities, producing 21 changed numeric row records and 687 distinct lower codes. The classes span 1–401 without a decrease or missing class. These are the final values of [comparison.json](comparison.json), `summary`, and [chart-reference-v2.json](chart-reference-v2.json), `rows`. The readings remain Exploratory because one AI reader performed the audit and the larger-crop reinspection. The worn 333 at `p21_c4_r22` has medium confidence; the other 686 cells have high qualitative confidence.

## Primary corrections and visible evidence

Pages are one-based PDF page numbers; columns and rows are zero-based. Every entry below links through its cell identifier to [cell-observations.json](cell-observations.json), `rows[*].cell`, with `source_image`, `review_image` and `visible_evidence`. [comparison.json](comparison.json), `changes[*]`, preserves old and new values. The chart comes from Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki, [institutional source](http://hdl.handle.net/10138/342677), PDF pages 20–21. [sources.json](sources.json) records access and rights provenance.

| Cell | Printed class | Old primary | Proposed code | Observation supporting the reading |
|---|---:|---:|---:|---|
| p20_c4_r1 | 86 | 506 | 508 | Final digit has two lobes and a detached upper-right ink fragment; its shape differs from the hooked 6 in class 86 above. Drawing is an underlined branching stem. |
| p20_c4_r21 | 98 | 465 | 486 | Middle digit has two lobes; final digit has a curved upper hook and lower loop. Drawing is the underlined six-bar comb, adjacent to the class-98 plain comb labelled 51. |
| p21_c0_r21 | 214 | 360 | 380 | Middle digit has two rounded lobes, with a worn right contour. Drawing has two adjacent arches. |
| p21_c0_r29 | 218 | 579 | 679 | Initial digit has a curved upper hook and lower loop. Drawing is the star form. |
| p21_c5_r34 | 326 | 205 | 206 | Final digit has the hooked upper stroke of 6. The flagged U has two short interior ticks. |
| p21_c6_r1 | 327 | 206 | 208 | Final digit has two lobes. The flagged U has three short interior ticks. |
| p21_c6_r9 | 331 | 385 | 386 | Final digit has an upper hook and lower loop. The U has one fork-ended and one comb-ended arm. |
| p21_c6_r31 | 345 | 285 | 286 | Final digit has an upper hook and lower loop, unlike the flat-topped 5 in class 345 directly above. Drawing has an arched top, hanging loops and central stem. |

At `p21_c5_r15`, the printed upper number is 316 and the original reference records 315. The final digit has the rounded hook and lower loop of 6. The adjacent class order is 315, 316, 316, 316. The lower code 197 is unchanged; the drawing is a U with a central hanging loop. See the cell's `visible_evidence` and `comparison.changes[*].fields.rank`.

The one-, two- and three-interior-tick U forms print class/code pairs 325/205 (`p21_c5_r32`), 326/206 (`p21_c5_r34`) and 327/208 (`p21_c6_r1`). This supports the coordinator's reported two-tick and three-tick corrections. The comb's 486 also agrees with N's adjudicator observations. Both propositions were checked against this audit's rendered pixels; N's inscription readings supply no chart-number evidence here. See [sources.json](sources.json), `N-chart-observations`, and the three cells' observation records.

## Retained ambiguities

All old lower-code candidate sets are reduced to one provisional printed code. The last column summarizes digit features from `cell-observations.rows[*].visible_evidence`; [comparison.json](comparison.json), `old_ambiguity_decisions`, gives the exact old primary, alternatives and new set for all 16 cells.

| Cell | Old primary plus alternatives | Proposed code | Digit or drawing check |
|---|---|---:|---|
| p20_c4_r21 | 465, 485, 486 | 486 | Hooked final 6; six-bar comb with underline. 465 and 485 visibly label other drawings. |
| p20_c7_r22 | 784, 764 | 784 | Middle 8 has two lobes; underlined short-tick group, class 151. |
| p21_c0_r1 | 698, 598 | 698 | Curved initial 6 differs from flat-topped 5 on `p21_c9_r17` (598); underlined branching stroke, class 203. |
| p21_c0_r18 | 260, 250 | 260 | Middle 6 has upper hook and lower loop; curved drawing, class 211. |
| p21_c0_r29 | 579, 679 | 679 | Hooked initial 6; star, class 218. |
| p21_c3_r2 | 65, 55 | 65 | Initial hook differs from the second digit's flat top; rectangle with interior ticks, class 270. |
| p21_c3_r4 | 68, 58 | 68 | Initial 6 has hook and loop; final 8 has two lobes; rectangle with internal horizontal strokes, class 270. |
| p21_c4_r6 | 436, 435 | 436 | Hooked final 6; capped frame with upper hatching, class 290. |
| p21_c4_r22 | 333, 533 | 333 | Surviving diagonals and lower bowls fit 3; first digit lacks the left stem of 5. Ink loss limits confidence to medium. |
| p21_c5_r34 | 205, 206, 208 | 206 | Hooked final 6; two interior ticks, class 326. |
| p21_c6_r9 | 385, 386 | 386 | Hooked final 6; fork/comb-ended U, class 331. |
| p21_c6_r17 | 364, 354 | 364 | Hooked middle 6; two fork-ended U arms and crossbar, class 333. |
| p21_c7_r6 | 496, 495 | 496 | Hooked final 6; overlapping ovals with a branching extension, class 351. |
| p21_c8_r5 | 671, 571 | 671 | Curved initial hook matches the 6 of nearby 691 and differs from the flat-topped 5 of 579. Underlined circle with triangular projection, class 370. |
| p21_c8_r16 | 63, 53 | 63 | Hooked initial 6; four-compartment square with interior ticks, class 378. |
| p21_c9_r5 | 677, 577 | 677 | Hooked initial 6; diamond with notch and branching projection, class 390. |

Six old primary codes label two cells: 385, 465, 579, 506, 360 and 205. Their pairs show different drawings: figure / fork-comb U, figure / comb, bracketed oval / star, branching stem / overlapping ovals, opposed comb / adjacent arches, and one-tick / two-tick U. The eight primary corrections remove these collisions. Zero codes are shared by two final cells (`comparison.summary.duplicate_codes`). Unique labels corroborate the digit readings; they did not determine the values. Alternatives that duplicate another cell are separately documented in the evidence notes, including 354, 495 and 53.

## New v3 hypotheses and the audit's own correction

Package M's `card_label_observations` proposes 508 at `20:4:1`, 208 at `21:6:1`, 350 at `20:4:13` and 286 at `21:6:31`. This audit supports the first, second and fourth. At `p20_c4_r13`, the middle lower digit has the upper hook and lower loop of 6. The digit-band comparison with the flat-topped middle 5 of `p21_c1_r19` (350) supports 360. See [the local 24x comparison](../../data/raw/2026-10-08-chart-reference-audit/digits-24x/sheet-00.png) and that cell's reinspection record. Its opposed-comb drawing differs from the class-234 drawing labelled 350. The conflicting 350 report should receive independent visual review.

M's composite-label observation also suggests 598 at `21:0:1` and 671 at `21:8:5`. This audit reads 698 at the former and 671 at the latter. The initial digits are compared with nearby printed examples in [sheet-08.png](../../data/raw/2026-10-08-chart-reference-audit/digits-24x/sheet-08.png) and [sheet-16.png](../../data/raw/2026-10-08-chart-reference-audit/digits-24x/sheet-16.png). The saved same-reader reinspection had incorrectly chosen 571 at the latter. Final continuation review corrected it to 671 and preserved the earlier exploratory outputs under local `continuation-history/`. The first-pass observations remain unchanged.

## Method and scope

[PROTOCOL.md](PROTOCOL.md) preceded the new readings. Full pages were rendered at 6 pixels per point, and every cell at 8. Forty sheets displayed the printed class, drawing and lower code with cell identities; old numeric readings were absent from the sheets. [visual-readings.json](visual-readings.json), `columns`, stores every first-pass pair. The first pass differed from the original at 21 lower codes and two classes, including errors made by this audit reader. A rule selecting mismatches, old ambiguities, difficult-digit notes and repeated first-pass codes selected 56 cells. Follow-up inspection of the added v3 hypothesis produced 57 distinct reinspected cells. Full-cell reinspection used 16x renders; difficult comparisons also used 24x digit bands. No OCR or PDF text layer supplied values.

Enlargement exposes the scan's surviving ink and cannot restore it. Confidence is an uncalibrated visual judgement. The same reader performed the initial reading, saw the comparisons and made the follow-up decisions, so the counts do not establish independent accuracy. The complete evidence is in `cell-observations.rows`, and the first pass and later changes remain separate. This package audits this edition's printed numbering; it provides no sound or meaning assignments.

The v2 file retains all original row fields and auxiliary flags, adds `change_log` to the 21 numerically changed rows, and records audit provenance at the top level. Its row `source` strings identify the fresh audit throughout; the count of 21 concerns numeric fields and confidence, rather than that provenance update. The original PDF, atlas metadata and numeric reference retain their initial hashes. Consumer hashes are in [consumer-input-integrity.json](consumer-input-integrity.json), `inputs` and `unchanged`; mechanical coverage and replay checks are in [verification.json](verification.json), `checks`.

## Consumer impact

The joins use explicit chart locations intersected with the old candidate code membership. Each joined cell contributes its v2 label. This preserves alternatives between different drawings while removing alternative digit readings within a cell. A candidate without a matching location is retained and reported in `potential_mappings`, including its possible old-cell identities. Those flags identify review work; they are not claims that the candidate must change. Separate `shape_only_chart_locations` fields are used where supplied. [impact.py](impact.py) implements the joins and [impact.json](impact.json) records every locator and delta.

| Reference | Rows / units | Directly changed rows / units | Strict changed units | Shape-only changed units | Units with unlocated affected candidates |
|---|---:|---:|---:|---:|---:|
| M v1 and release v1 | 60 / 267 | 8 / 11 | 1 | 11 | 0 |
| M v2 adjudicated and release v2 | 80 / 352 | 0 / 0 | 0 | 0 | 18 |
| M v3 adjudicated | 80 / 369 | 7 / 8 | 8 | 8 | 31 |

The v1 strict change is sample 36, unit 1, 506 to 508. Its shape-only set also changes. Other v1 changes reduce comb, tick-group and worn-digit alternatives. Exact units are in `impact.M_references.v1.unit_changes`; samples are 1, 5, 7, 8, 23, 32, 36 and 39. The eight direct v3 sample/unit pairs are 15/0 (comb to 486), 31/0, 32/0 and 32/2 (506 to 508), 39/4 (58/68 to 68), 51/2 (435/436 to 436), 60/6 and 67/4 (206 to 208). M's card-label note also names 58/0 as using `20:4:1`, while the stored adjudicated reference points to `21:7:5`, whose 506 is unchanged. This conflict requires graphic identity review before mapping that unit; it is recorded in `impact.M_v3_reported_location_conflicts`. No units in the note use `20:4:13` or `21:6:31`.

The 21 affected template records are listed in `impact.M_templates`, with indices, fields, snapshot path and sheet paths. `development/templates.json` changes code sets in 20 records and rank/rank-candidate metadata in one. M's `pipeline.py`, `templates()` and `Recognizer.alternatives()`, derive label payloads from the reference while retaining cell keys. M's v1 sheets show codes and rank; its repair position cards show codes and cell identity. Consequently 20 v3 card code strips change; the class-only correction has no rank strip on a position card. The 21 locations occupy eight original v1 sheets and nine sheets in each repair packet. These paths are listed individually without editing them.

For N, `impact.N_charts` records 105 cell placements in five deliveries: v1 and v2 reader-1/reader-2, and the adjudicator pilot. All 45 inspected sheet files are byte-identical to M's v2 position sheets. Twenty code strips per delivery therefore carry affected labels, or 100 placements altogether. The remaining five placements correspond to the class-only correction. The copying step is visible in N's `generate_packets.py`, lines 132–146; its original-PDF chart images preserve the printed numbers independently of the card strips.

The release's `chart_reference.parquet` changes 21 rows. Exact row indices, `cell_id` and affected fields are in `impact.public_chart_reference_changes`. Its v1/v2 `benchmark_rows` tables embed the references and predictions in JSON columns. The reference changes match the M rows above. Stored predictions would change 65 alternatives in 41 units across 33 v1 rows, and 88 alternatives in 56 units across 42 v2 rows. Of these, 60 and 83 alternatives change code sets; five in each version change rank metadata. The top alternative changes in five v1 units and ten v2 units. Every `sample_index`, unit and alternative index is in `impact.public_predictions`; confidence values and graphic scores remain the frozen values.

`benchmark_readings.parquet` also carries candidate labels. Its v1 A/B primary readings change six/five units; v2 reader A changes 15 units. V2 reader B has zero direct changes or unlocated affected candidates, while adjudicator C's 18 flagged units match the adjudicated reference above. `impact.public_readings` gives the exact group, source field and unit records, including groups with no direct changes. The 42 affected-location entries for release chart cards occupy 17 sheet files; their `code_strip_changes` and `rank_strip_changes` fields distinguish displayed changes from metadata-only placement checks.

The scorer compares candidate code sets from `reference_json` and `prediction_json`. A versioned remapping can affect strict and shape-only top-one/top-five compatibility, exact-sequence matches, calibration outcomes, bootstrap intervals and the top-five acceptance criterion. The code changes identify 32 v1 and 42 v2 expected row records to recheck; their sample indices are in `impact.scorer_expectations.expected_row_records_to_review`. Exact field families are in `fields_requiring_new_versioned_run`. New metric values have not been computed. The direct public-reference joins change no strict-set cardinalities, so their reference ambiguous-unit and unique-reference-row counts remain constant. Crop, count, classification-literal, inscription-number and source-row-recall values use other evidence and retain their current definitions.

## Consumer uptake and remaining checks

M should preserve its frozen chart snapshot and card-labelled references, then create a new pipeline snapshot after independent digit review. Keep cell keys and template order stable and version the emitted code sets and rank metadata. A separately dated sensitivity run can map stored alternatives by `template_key`; first resolve the unlocated reference candidates and keep their graphic-reading uncertainty separate from digit-label uncertainty. Its report should state the old and new vocabulary and reuse the frozen graphic predictions.

N should create a new packet version with revised code strips and a chart-correction notice. Preserve completed returns under their original vocabulary; map only identifiable cells in a new merge or sensitivity output. O should version its release, rebuild the chart table, card images and affected benchmark JSON payloads, and freeze new scorer expectations after a documented mapped run. Update release manifests and hashes together. Printed source-cell crops already carry the source digits and need no alteration for the reference correction.

Independent review remains needed for the digit decisions and for the 18 v2 / 31 v3 unlocated-candidate units. Prioritize the medium-confidence 333 and the conflicting 360/350 and 698/598 observations, plus this audit's corrected 671 decision. Repeat the deterministic joins, compare the source hashes, inspect all changed and old-ambiguous cells, and sample unchanged cells from each page. The full consumer locators are preserved so that review can resolve these points without editing frozen outputs.
