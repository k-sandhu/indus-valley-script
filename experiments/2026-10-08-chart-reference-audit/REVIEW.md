# Review of package P: audit of the 1979 sign-chart reference

Reviewer: Claude (an AI model), 8 October 2026. The readings below are a second AI reading of the printed chart, made blind to the package's values, and are not an expert certification.

## Verdict

The main results stand. I read 63 cells independently (the 23 cells named in the brief and 40 drawn with seed 20261008) before opening the package's readings. After a check on the native pixels, my class numbers and codes agree with `chart-reference-v2.json` on all 63 cells, including all 16 old ambiguities and all eight primary-code changes. A pixel-template sweep of all 687 cells found no code that disagrees with v2 and one class number that does: `p20_c3_r33` prints class 86, and both v2 and the original reference record 85. Every count in the README and REPORT that I recomputed from `comparison.json`, `impact.json` and `chart-reference-v2.json` is correct (50 of 50), and `audit.py compare`, `impact.py` and `verify.py` rerun to byte-identical outputs. The most important problem is the evidential basis of the "high" label. The audit's first pass misread 5, 6 and 8 in 15 of its 21 code differences, only 57 cells were reinspected, and the other 630 carry "high" on one reading. My own eye pass made the same 5/6 mistakes at five cells. The class error at `p20_c3_r33` sits in one of those 630 cells, and the confidence labels should be lowered where the decision rests on a 5/6/8 shape test.

## Independent reading

**Cell list.** `review/cell-selection.json` (rebuilt by `review/select_cells.py --check`): the 21 IDs in `comparison.json` `changes`, which include all 16 cells with `alternatives` in the original, plus `p20_c4_r13` and `p20_c3_r16`, giving 23 core cells; 40 further cells drawn with `random.Random(20261008).sample` from the other 664.

**Reading.** I rendered each cell from the PDF (10x full cell, 20x label area), read class number and code by eye, and wrote `review/independent-readings.json` before opening `cell-observations.json`, `visual-readings.json`, `chart-reference-v2.json` or `comparison.json` beyond the IDs. The embedded page image is a 1-bit raster of 4880 by 7010 pixels (about 8.3 pixels per point), so renders above 8x add no information. After the eye pass I segmented the label digits on the native pixels and compared each digit with mean templates built from the clear digits of other cells (`review/pixel_check.py`, `review/shape_features.py`). The eye pass was already written when I did this; the file records both the eye-pass code and the final code.

**Results.**

| Group | Cells | Final code equals v2 | Final class equals v2 | Final code equals original |
|---|---:|---:|---:|---:|
| Core | 23 | 23 | 23 | 15 |
| Random | 40 | 40 | 40 | 40 |

The eight core cells where my code differs from the original are exactly the audit's eight primary changes. Confidence in my own readings was high for 37 cells, medium-high for 16, medium for 9 and low-medium for 1 (`p21_c6_r1`).

| Cell | Original | v2 | My eye pass | My final | Shape evidence |
|---|---|---|---|---|---|
| `p20_c4_r13` | 360 | 360 | 350 | 360 (medium) | Middle digit: top stroke 52% of digit width, empty top-left corner, left stroke continues below the bowl junction; template 6 0.907, 5 0.485; 7 of 7 nearest neighbours are 6s. The lower left of the bowl is broken, which makes it look like a 5. 350 is carried by `p21_c1_r19`, whose middle digit has a flat bar. |
| `p21_c0_r21` | 360 | 380 | 380 | 380 (medium-high) | Middle digit 8 with the upper-right fleck; template 8 0.864, 6 0.572. |
| `p21_c4_r22` | 333 / 533 | 333 | 333 | 333 (medium) | Worn print. Each digit has a lower bowl open to the left, an upper-right diagonal fragment and no left stem, so a 5 is unlikely. Template scores are low (best matches 0.42, 0.54, 0.72, each a 3). |
| `p20_c3_r16` | 368 | 368 | 368 | 368 (medium) | Middle digit is a 6 (template 0.891 against 5 0.443). |
| `p20_c4_r1` | 506 | 508 | 508 | 508 (medium-high) | Last digit 8 with the upper-right fleck; template 8 0.904, 6 0.684. 506 is carried by `p21_c7_r5`. |
| `p21_c6_r31` | 285 | 286 | 286 | 286 (medium-high) | Rounded top, 54% width; template 6 0.949, 5 0.584. The 5 of class 345 above it has a bar 85% wide. |
| `p21_c6_r1` | 206 | 208 | 208 | 208 (low-medium, later medium) | Template 8 0.839, 6 0.685. The digit has no fleck at its upper right, as 6s do not, but its waist is narrow like an 8's. A later nearest-neighbour check over 939 digits puts it among the 8s (7 of 7; mean similarity of the ten closest 8s 0.879, 6s 0.750). |
| `p21_c5_r34` | 205 / 206 / 208 | 206 | 205 | 206 (medium-high) | Rounded top, 48% width; template 6 0.946, 5 0.599. 205 is carried by `p21_c5_r32`. |
| `p21_c0_r1` | 698 / 598 | 698 | 598 | 698 (medium) | First digit: top stroke 54%, empty corner; template 6 0.891, 5 0.463. 598 is carried by `p21_c9_r17`. |
| `p21_c8_r5` | 671 / 571 | 671 | 671 | 671 (medium-high) | First digit: top stroke 46%; template 6 0.921, 5 0.557. The last digit is a 1 printed with a detached dot. |
| `p21_c0_r29` | 579 | 679 | 679 | 679 (medium-high) | Template 6 0.945, 5 0.599. |
| `p20_c4_r21` | 465 / 485 / 486 | 486 | 486 | 486 (high) | Clear. |
| `p21_c6_r9` | 385 | 386 | 386 | 386 (medium) | Middle digit is a broken 8 (template 0.848); last digit a 6 (0.949). |
| `p21_c5_r15` class | 315 | 316 | 316 | 316 (high) | The 1 is printed with a detached dot. |

The figure `review/disputed-digits.png` shows the contested digits beside clear 5, 6 and 8 examples (binarised crops of the Koskenniemi and Parpola 1979 chart pages, CC BY 4.0, cropped and enlarged 5x).

## Disagreements and which reading the print supports

My final readings disagree with v2 on no code and no class in the 63 cells. The disagreements that exist are of three kinds.

1. **My eye pass against v2, five cells.** I read `p20_c4_r13` as 350, `p21_c0_r1` as 598, `p21_c0_r18` as 250, `p21_c3_r4` as 58 and `p21_c5_r34` as 205. In each the middle or leading digit has a gap at the lower left of its bowl. Re-inspection on native pixels separates the typeface's two forms: a 5 has a flat top bar 73-96% of the digit width (28 clear examples) with a squared top-left corner, and a 6 has a rounded top 41-60% wide (28 clear examples) with an empty corner and a left stroke that continues below the bowl junction. All five digits have the 6 outline. The print therefore supports v2 and the original in `p20_c4_r13` (360), and the v3 adjudicator's 350 for that cell most likely repeats the same misperception, which my eye pass also made. The reading stays at medium confidence because the bowl is open, and an expert check of that digit is warranted.
2. **My readings against the original reference, eight cells.** These are the audit's eight primary changes. The print supports the v2 value in each. `p21_c6_r1` (208 against 206) is the least certain, for the reasons in the table.
3. **Whole-chart sweep against v2, one cell.** `p20_c3_r33`, class number. The second digit has the rounded top and continuing left stroke of a 6 (template 6 0.945, 5 0.580; 7 of 7 nearest neighbours are 6s, best similarity 0.96). The cell above, `p20_c3_r32`, prints a flat-topped 5 in class 85, and the cells below (`p20_c3_r34`, `p20_c4_r0`) print 86. The class order stays nondecreasing and complete either way, so the audit's order and coverage checks could not catch this. I rate the 86 reading medium-high.

## Whole-chart pixel sweep

`review/pixel_check.py` classifies every digit of the class number and code of all 687 cells with templates built from the digits of my high and medium-high cells that the pixel check left unchanged. It produced no code that differs from v2 after inspection of its mismatches. The automated output disagrees with v2 in 6 codes and 9 class numbers over 12 cells; `review/pixel-check-mismatch-resolution.json` records each. Nine are segmentation artifacts (neighbouring ink merged, digits cut at the label-region edge) where a hand-set window read or the 10x render confirms v2. Two are not settled by pixels: the worn middle digit of the code of `p21_c7_r21` (eye reads 734) and the faint first class digit of `p21_c4_r21` (300, consistent with its neighbours). One is the `p20_c3_r33` class.

`review/knn_check.py` labels each of the 939 digits that v2 gives as 5, 6 or 8 (class numbers and codes, 368 fives, 289 sixes, 282 eights) by its seven most similar digits in other cells. The labels agree for 938 of 939; the exception is the same `p20_c3_r33` class digit. This is a consistency check of v2 with itself rather than an independent label source, so it detects isolated misreads but not a shared error across many cells.

Codes in my pixel readings are unique after the artifact cells are set aside, matching v2's 687 distinct codes. The class sequence shows four apparent decreases that are all segmentation artifacts.

## Checked claims

| Claim | Evidence path | Result | Note |
|---|---|---|---|
| 8 primary-code changes, 1 class change, 21 changed rows | `comparison.json` `summary` | confirmed | 21 rows have a `change_log` in v2. |
| 16 old ambiguities resolved, none remain | `comparison.json`, `chart-reference-v2.json` | confirmed | 12 kept the old primary code and 4 moved to an old alternative (`p20_c4_r21`, `p21_c0_r29`, `p21_c5_r34`, `p21_c6_r9`). All 16 match my readings. |
| 687 distinct codes; classes 1-401 nondecreasing | v2 `rows` | confirmed | One class number is probably wrong (`p20_c3_r33`). |
| First pass differed from the original in 21 codes and 2 classes | `visual-readings.json` against the original | confirmed | 15 of the 21 code differences were later reverted to the original value; 6 became final changes. Two final changes (`p20_c4_r1`, `p21_c6_r31`) were absent from the first pass and appeared only after the v3 hints. |
| 57 cells reinspected | `cell-observations.json` `reinspected` | confirmed | 630 cells were not reinspected. |
| Six old primary codes label two cells each | original `rows` | confirmed | 205, 360, 385, 465, 506, 579. |
| 333 is the only medium-confidence cell; the other 686 are high | v2 `numeric_confidence` | confirmed as recorded | The label overstates the 5/6/8 decisions, see fixes. |
| Impact counts in README and REPORT | `impact.json` | confirmed | 50 of 50 figures recomputed with `review/check_numbers.py` (`review/number-check.json`): v1 8 rows / 11 units, v2 0 / 0 with 18 unlocated, v3 7 / 8 with 31 unlocated, 21 template records (20 code sets, 1 rank), 105 N placements of which 100 change a code strip, 21 release chart rows, 65 / 88 prediction alternatives (60 / 83 code sets), 32 / 42 scorer rows to recheck. |
| v3 location conflict (sample 58 unit 0: `20:4:1` reported, `21:7:5` stored) | `impact.json` `M_v3_reported_location_conflicts` | confirmed | |
| Three spot-checked joins (v1 sample 36 unit 1; v3 60/6 and 39/4 and 15/0) | M reference files | confirmed | Locations and codes match the stored references. |
| Original reference and atlas unchanged | SHA-256, `git status`, `git diff --stat` | confirmed | `09cc3116...` and `3ef9b48b...` match `sources.json`; no tracked file is modified. |
| Prose scan zero flags | `tools/review_prose.py` | confirmed | See Writing. |

## Reproduction log

I ran patched copies of the scripts in the raw temporary folder so that no package file was rewritten; the copies were deleted at the end.

- `audit.py compare`: 0.2 s. `chart-reference-v2.json`, `cell-observations.json` and `comparison.json` are byte-identical to the package files.
- `impact.py`: 2.3 s. `impact.json` is byte-identical, and the three extracted public-release JSON files in the raw directory are byte-identical. `consumer-input-integrity.json` differs only in the two path names of the copied inputs; the other 116 pinned hashes are equal and `unchanged` is true.
- `verify.py`: 4.1 s. 22 of 22 checks pass, with the same check names as `verification.json`.
- Not rerun: `audit.py render`, `audit.py review` and `extra-crops.py`, which would overwrite the package's raw renders. My pixel check reads the PDF directly and uses only the package's `render-manifest.json` for cell rectangles.
- `review/pixel_check.py`, `compare_readings.py`, `check_numbers.py`, `knn_check.py` and `shape_features.py` rerun cleanly from the repository root (about 20 s in total).

## Sources

`sources.json` lists five sources, all opened and none snippet-only. The Helsinki research portal record confirms the title *Corpus of Texts in the Indus Script*, authors Kimmo Koskenniemi and Asko Parpola, 1979, Research Reports vol. 1 of the Department of Asian and African Studies, University of Helsinki, licence CC BY 4.0, file `indus_corpus_1979.pdf` (16.2 MB). The handle URL `http://hdl.handle.net/10138/342677` redirects to `helda.helsinki.fi`, which returned an anti-bot access page to me, so the helda record text is unverified. The local PDF has the recorded SHA-256 `7bfc35f2...` and 180 pages (16,935,355 bytes, 16.15 MiB). The reference and atlas hashes in `sources.json` match the files. The v3 `card_label_observations` entries match the package's description of them (508 at `20:4:1`, 208 at `21:6:1`, 350 at `20:4:13`, 286 at `21:6:31`, composite labels including 598 at `21:0:1` and 571/671 at `21:8:5`). The N adjudicator's return states 327/208, 326/206 and "98 486" as the package reports, and the package disclosed its one over-broad filter over N's returns. `knowledge/provenance/REDISTRIBUTION.md` keeps the original PDF local and allows selected tracked crops with attribution; the package places no source pixels in its owned directory, and `impact.json` contains locators and labels only, with no inscription text.

## Method and scope

`PROTOCOL.md` was created at 12:00:20, before `audit.py` (12:00:53), the first render (12:01:04) and the first-pass file (created 12:02:47, last written 12:37:01). It was edited at 13:16:43, and the amendments are dated and label the affected outputs exploratory. The repository has one commit for the package, so the protocol's original text cannot be recovered from history. The first-pass readings are frozen and their hash is checked by `verify.py`. The preliminary 571 decision was preserved under `continuation-history/` before correction to 671, and I confirm 671.

The design reinspects cells where the first pass differs from the original, where old ambiguities, notes or duplicates exist. A cell where the audit reader and the original reader share a misreading is never reinspected, and the class at `p20_c3_r33` is such a cell. The audit's first pass also missed two real code errors that it found only after the v3 hints. The REPORT says that the first pass contained the reader's own errors, but it does not give their number (15 of 21), does not say that 630 cells were read once, and does not say that two final corrections came from the v3 hints rather than from the first pass.

No claim of decipherment, sound or meaning appears. The cell evidence describes drawings with words such as "anthropomorphic" and "figure" to tell them apart; these are descriptive labels and nothing rests on them. I did not find resampling, bootstrap or novelty claims in the package. Limitations sit beside the claims in the REPORT's method section.

## Writing

`tools/review_prose.py --path experiments/2026-10-08-chart-reference-audit --no-write` reported zero flags on the four package Markdown files. By reading, the prose is concrete and the headline findings come first. Two passages are unclear. README paragraph 1 says "The resulting code list ... covers every class from 1 to 401", where the classes, not the codes, span 1-401. REPORT "Method and scope" says "the count of 21 concerns numeric fields and confidence, rather than that provenance update", which does not say that all 687 rows received a new `source` string. About eight "rather than" constructions occur across the three longer files; they are few enough not to need editing.

## Boundaries

`git status --porcelain` shows only `experiments/2026-10-08-chart-reference-audit/review/` (mine, with this file) and `experiments/2026-10-08-site-map-and-overview/`, which belongs to another contributor. The temporary folder `data/raw/2026-10-08-chart-reference-audit/reviewer-tmp/` was deleted. No file of the package, the original reference or `output/chart_atlas/` was changed.

## Required fixes, ranked

1. Correct the class of `p20_c3_r33` from 85 to 86 in a dated v2 amendment (or v2.1) with a `change_log`, then rerun `impact.py`: it adds one template record, one release `chart_reference` row, and any stored alternatives whose `template_key` is `20:3:33`. The order and coverage checks remain true. Ask an expert to confirm that digit with the five 5/6 cells in the next item.
2. Lower `numeric_confidence` to "medium" for the cells whose value depends on separating a 6 with a broken bowl from a 5, or a broken 8 from a 6 (`p20_c4_r13`, `p21_c0_r1`, `p21_c0_r18`, `p21_c3_r4`, `p21_c5_r34`, `p21_c6_r1` at least), and state in the README and REPORT that 15 of the first pass's 21 code differences were reader errors and that 630 cells were read once. The labels are copied into the public release's `chart_reference`, so the current "high" travels with them.
3. Reword the two unclear sentences named under Writing.

## Optional improvements

- Keep the contested alternative in `alternatives` (350 for `p20_c4_r13`, 206 for `p21_c6_r1`, 598 for `p21_c0_r1`) until an expert confirms the digit, so consumers see the open question.
- Add the native-pixel template sweep, or an equivalent, to the package's checks. It covers the 630 unreinspected cells that no second reader has seen, and it found the one error that the audit's design could not.
- Note in the REPORT that the page raster is about 8.3 pixels per point, so the 16x and 24x crops are interpolated and the digit evidence comes from the same pixels as the 8x crops.
- Resolve `p21_c7_r21` (worn middle digit of 734) and `p21_c4_r21` (faint first class digit, 300) from a better source or an expert.
