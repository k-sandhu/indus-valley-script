# Review of package M, v3 work (8 October 2026)

Scope: the v3 crop rebuild, its development results on the reused v2 rows, the freeze, the fresh blind packet, the full-edition proposals, the coordinator's blind evaluation and the endpoint record (`repair/2026-10-08-v3/`, `repair/2026-10-08-endpoint-record-v1/` and the updated README, REPORT, PROTOCOL, RETROSPECTIVE and registry entry). The earlier `REVIEW.md` is unchanged.

## Verdict

The v3 results stand. The evaluator replay is byte-identical to the coordinator's `metrics.json`, the record scripts regenerate the diagnosis files byte-for-byte, and every headline count and interval recomputes from the per-row records. The full-edition inventory (11,769 records, 11,702 numbered occurrences, 67 continuations, 54,384 unit windows, 5 unresolved, all quarantined) matches an independent pass over the 106 MB JSONL. The freeze and prediction-freeze timestamps precede the first reader start by 77 minutes (14:11:23Z and 14:13:49Z against 15:28:00Z), and the packet and code hashes are unchanged. The development results on the 80 v2 rows are labelled Exploratory throughout and do not appear in the evaluation columns.

The limiting-stage analysis also holds, and I could test it directly. I re-ran the frozen segmentation and recognizer in memory on the six crop-stage rows whose failing windows I could not otherwise attribute (21, 44, 48, 55, 58, 66) with the lower box edge trimmed by 0.5 to 1.5 pt. All six became top-five compatible, while nine failing rows outside the crop stage (31, 14, 41, 60, 65, 68, 3, 35, 70) and row 32 did not. Neighbour ink of 0.4 to 1.3 pt at the lower edge changes the unit count in rows 58 and 66 and the unit identity in the other four.

Two problems remain. The documents never say that the whole reference was produced by Claude Sonnet 5.5 readers and a Claude adjudicator with no human check. And the top-five criterion, which fails by two rows, depends on two adjudicated empty strict sets (rows 35 and 70) and on the strict-versus-shape-only convention; the frozen metrics hold a shape-only top five of 65/80 that the documents omit. The release conclusion does not depend on either point, because the count criterion (72/80 against 76) and the number criterion (71/80 against 72) fail on pipeline errors that no reading choice changes.

## Checked claims

| Claim | Evidence | Result | Note |
|---|---|---|---|
| Freeze 2026-10-08T14:11:23Z, prediction freeze 14:13:49Z, readers started 15:28:00Z to 15:29:59Z, adjudicator 16:04:23Z | `freeze-manifest.json`, `prediction-freeze.json`, reader `started_utc`, file mtimes | Confirmed | Embedded timestamps and mtimes agree. The commit that first records the freeze (`0445bad`) is dated 15:33:31Z, after the readers started, so Git alone does not anchor the order (M5). |
| Hash chain intact | 12 code hashes, 195 packet hashes, predictions, selection, count detections; `evaluator_sha256` in metrics equals the freeze entry | Confirmed | `verify_crop_v3.py` and my own comparison. |
| Model, digits, chart snapshot, calibration, `pipeline.py`, `evaluate.py` unchanged from v2 | v3 and v2 `freeze-manifest.json` | Confirmed | Identical SHA256 for all seven. v3 changed crop, layout and unit-window code only. |
| Selection reproduces from seed | `frame.json`, seed 2026100880, count seed 2026100891 | Confirmed | Pools 572/2,004/2,004, the 80 targets and the 18 random count pages regenerate exactly. The frame records the freeze hash. |
| Headline: crop 71, number 71, classification 72, count 72, top-one 38, top-five 62, exact 28/54 | `metrics.json` `rows`, recomputed in `review-v3/recomputed-v3-claims.json` | Confirmed | |
| All 22 Wilson intervals in the README table, and 62/77 | Own implementation | Confirmed | |
| Thresholds 72/72/76/64 and gaps 1/1/4/2 | `negative_result_criteria`, `diagnosis.json` | Confirmed | |
| Unit recall 293/366 and 338/366; positional 263/315 and 301/315; Brier 0.1117; ECE 0.1153; 43/43 correct in the 0.9 bin | `metrics.json` | Confirmed | Stored bootstrap intervals reproduce in the replay. |
| Random-page numbered 1,289/1,289, physical 1,296/1,296, stress 561/561; 1,850 numbered and 1,857 physical lines on 21 pages and 52 columns; 7 continuations on pages 35, 47, 127, 172, 175 | Reader count files, `adjudicated-counts.json` | Confirmed | The two readers agree on every page. |
| Readers agree on 80/80 numbers, classifications, counts and line membership; 79/80 crops; 357/369 strict sets; the adjudicator emptied one strict set both readers filled (35:2) | Reader files, recomputed | Confirmed | Row 21 is the one crop disagreement. |
| 18 top-five failures: 8 crop, 6 count, 4 count-consistent (3, 31, 35, 70); 42 top-one failures: 9/6/27; 65 accepted-crop equal-count rows with 247/282 and 278/282; the four resolved misses all in row 31 | Recomputed from `metrics.json` | Confirmed | |
| Limiting stages 8 crop, 7 segmentation/underline, 3 unresolved, 0 graphic-proposal misses | `unit-window-audit.json`, overlays, counterfactual | Confirmed | Row 31 and the six count failures match the overlays. The crop-stage rows were not window-inspected by the package; my trim probe supports their crop attribution (M1). Rows 76 and 77 (cut drawings) were not probed. |
| Wrong numbers 9, classifications 8, either 15; section, page, margin-side and parity tables | Recomputed | Confirmed | Crop-rejected pages 68, 112, 115, 135, 148, 161 (neighbour ink) and 84, 172, 174 (cuts). |
| Development on the 80 v2 rows: 71 counts, 69 numbers, 67 classifications, 33 top-one, 60 top-five, 327/352, 1,847/1,847 | `repair/2026-10-08-development-record-v1/diagnosis.json` | Confirmed | Crop acceptance is explicitly not reported for development rows. |
| Full inventory 11,769 / 11,702 / 67 / 54,384 / 5 unresolved / 159 pages / 106,190,599 bytes; all quarantined, none released | Streamed `proposals.jsonl` | Confirmed | No duplicate keys; schema validation passes; the 80 sample rows equal their full-run records. |
| Chart cells: 5 reference units (3 at 20:4:1, 2 at 21:6:1) and 10 top-five proposal units (3, 6, 0, 1) | `diagnosis.json` `chart_label_audit`; recomputed from reference locations and `template_key` | Confirmed | The ten units are distinct. Six reference units carry the card-label remark in their own note; the sixth is row 58. Among 263 top-one code matches, one is cross-cell (row 8 unit 4, coincident cards 205), unrelated to the four cells. |
| Row 58 unit 0 locator: reference 21:7:5, notes 20:4:1 | Atlas cells `p20_c4_r1` and `p21_c7_r5`, `exact_058.png` (`review-v3/row58_locator_check.png`) | Confirmed | The unit is two overlapping circles with corner ticks, which is 21:7:5 (printed 350/506). Cell 20:4:1 is a branched stem (printed 86/508). The card-label remark in row 58's note belongs to the cell of rows 31 and 32. |
| First and v2 comparator numbers and intervals | `evaluation/2026-10-07-frozen-v1/metrics.json`, v2 `metrics.json` | Confirmed | |
| Package N figures (216 rows, 185/216 agreed, 16/18 controls per role, 336.4 M tokens, 346.0 agent-hours) | N `PILOT-RESULTS.md`, `coordinator-cost-projection-v1.json` | Confirmed | |
| Ledger total 2,486,666 tokens and 11,108.273 s | `coordinator-task-ledger.jsonl` | Confirmed | |
| "Row 31's seven shifted unit windows" (README) | `unit-window-audit.json`, my overlay | Discrepancy | The audit and the overlay show windows 3 to 6 shifted; windows 0 to 2 are well placed. |
| Top-five criterion fails at 62/80 | The frozen evaluator tests `strict_top5` | Confirmed, sensitive | See M2. |

## Reproduction log

All commands ran from the repository root with `C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe`. Outputs went to `experiments/2026-10-07-helsinki1979-digitization/review-v3/`. The byte comparisons are in `review-v3/replay-hashes.json`; I deleted the bulky duplicate outputs after hashing them.

| Command | Result |
|---|---|
| `evaluate_crop_v3.py --out review-v3/v3-evaluation-repeat` | Exit 0. `metrics.json` SHA256 `60315317de3e9e967ad7b5182079aeb02fcb2a1fe1a7560115638fab38971b77`, identical to the coordinator's file and to `evaluator-replay/metrics.json`. |
| `verify_crop_v3.py --out review-v3/verify-crop-v3-repeat.json` | 31 of 32 checks pass in 48 s. The failing check, `no_fresh_reference_or_reader_files`, is a freeze-time check and fails by construction now that `blind/` holds reader and adjudication files. The original run (`repair/2026-10-08-record-v1/verification.json`, 11:18 EDT, before the readers) passed 32 of 32. |
| `record_v3_endpoint.py --out review-v3/v3-endpoint-record-repeat` | Exit 0 in 1.8 s. `diagnosis.json`, `reader-process-cost.json`, `chart-locator-inspection.json` and `preservation-check.json` (520 files) are byte-identical to the committed copies. |
| `verify_v3_endpoint_record.py --out review-v3/v3-record-check-repeat.json` | 26 of 26 checks pass. |
| `review-v3/recompute_v3_claims.py` | Independent recomputation of the table above and the sensitivity figures in M2. Output `recomputed-v3-claims.json`. |
| `review-v3/render_overlays.py` | Source-page overlays of the frozen unit windows for 19 rows (`review-v3/overlays/`). |
| `review-v3/counterfactual_bottom_edge.py` | Exploratory probe described in M1. Outputs `counterfactual-bottom-edge.json` (rows 21, 44, 48, 55, 58, 66) and `counterfactual-bottom-edge-control.json` (14 other rows). 41 s and 54 s on the CUDA environment. |
| `tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write` | 15 files scanned, no flags. |
| `git status --porcelain` | Only the three untracked prompt files, `2026-10-08-chart-reference-audit/`, `2026-10-08-site-map-and-overview/` and my `review-v3/`. No tracked file is modified. |

The two evaluation replays and the record replay ran on the CPU; none runs inference. The counterfactual loads the frozen classifier and templates.

## Spot checks of the limiting-stage analysis

I viewed each row below on the original PDF at 8 times scale with the frozen windows drawn on it (`review-v3/overlays/`), and the three development rows in the v3h development renders. Observations of small marks are one reviewer's reading and post hoc.

| Row | What the overlay shows | Agrees with the package |
|---|---|---|
| Development 27, 53, 76 (v2 indices) | 27: the box takes in neighbour field ink at left and cuts the last hatched patch. 53: the last classification digit enters the left edge. 76: the last hatched patch lies outside the right edge. | Yes. Fresh rows 76 and 77 repeat the final-patch and field-overlap defect, which the freeze documents as still present. |
| 31 | Windows 0 to 2 fit. Windows 3 to 6 start inside the previous drawing and cut the U, two fish and the underline slots. | Yes, for windows 3 to 6. |
| 14, 60, 65 | A window encloses only a speck far left of the drawings (two specks in 65). | Yes. |
| 32 | Eight windows over seven drawings; the last encloses a detached underline dash. | Yes. |
| 41 | The eight-tick group is split across three windows. | Yes. |
| 68 | Window 6 holds the curved sign and the ruled compound. | Yes. |
| 3 | One complete window around the oval with a slashed inner oval, no underline. | Yes. Card 160 is in the top five and in the shape-only set. |
| 35, 70 | An isolated high tick, no underline, in one window. The top five is [1, 23, 764, 8, 14] in both. | Yes. The strict set is empty; the shape-only set [1, 23, 258] intersects the top five. |
| 21, 55 | Clean windows apart from a 0.4 to 0.5 pt tip of the next row's ink at the lower edge. Row 21 misses card 25 (the tick pair); row 55 misses card 179 (the fish with a bar). | The probe in M1 restores both rows, so the crop attribution holds. |
| 58, 66 | Five windows for six drawings in 58 (the single stroke and the hook share a window); seven for six in 66 (the four-tick group is split). | The probe in M1 restores both counts, so the lower-edge ink is the cause. |
| 44, 48 | Window bottoms include the tops of the next row's signs; row 48 misses four of five units in the top five. | Restored at a 1.5 pt trim. |
| 76, 77 | The last hatched patch (and in 77 its underline) is cut by the box and overlapped by the field box. | Yes; not probed. |
| 30 | The box starts right of the first fish's left corner ticks. The top five still contains 520. | Yes. |

## Method findings

M1. The stage partition and the lower-edge probe. The amendment fixes the order of checks (rejected crop, then unequal count, then candidate miss on a correct window), and the documents call the result earliest observed failure stages. The window audit inspects only rows that pass the crop check, so the eight crop-stage rows carry no unit-level inspection in the package. To test whether the crop rejection explains their failures, I re-ran `crop_v3.segment_units` and the unchanged recognizer on each row with the bottom of the glyph box moved up by 0.5, 1.0 or 1.5 pt, after confirming that the untrimmed box reproduces the frozen top-one codes on all 20 rows tried. The smallest trim that gives a strict top-five compatible row is 0.5 pt for row 21 (strip 0.4 pt), 1.0 pt for row 55 (0.5 pt), 1.5 pt for rows 44, 48 and 66 (1.3, 1.3, 1.1 pt), and 0.5 pt for row 58 (0.8 pt), where the unit count also changes from 5 to 6. Row 66 changes from 7 to 6 units at 0.5 pt. None of the other failing rows tried (31, 14, 41, 60, 65, 68, 3, 35, 70) gains compatibility at any trim, and row 32 loses one window but stays incompatible. The mechanism is the column projection that splits units: a few pixels of neighbour ink at the lower edge fill the gaps between a stroke and a hook (58) or inside a tick group (66) and alter the matched windows elsewhere. The trim sizes were chosen after seeing outcomes and the probe is a sensitivity check, not a repair or a rescoring: in the control set a passing row (5) became incompatible at a 1.0 pt trim, so a fixed trim is not a safe general rule. Rows 76 and 77, where drawings are cut, were not probed. One consequence for the documents: the 0.4 pt strip on which row 21's crop rejection rests (reader A accepted it) is enough to change the pipeline's output on that row, so the rejected label is consistent with the behaviour of the code.

M2. Criteria that depend on reading choices. The top-five criterion fails by two rows, and rows 35 and 70 fail only because the strict set for an isolated high tick is empty. For 35:2 both readers had {23} and the adjudicator emptied the set; for 70:4 reader A had an empty set, reader B had {23}, and the adjudicator chose A. With {23} accepted in both, the strict top five would be 64/80 (80.0%), which meets the threshold. The frozen metrics also hold a shape-only top five of 65/80 (81.3%; Wilson 71.3 to 88.3%). The README and REPORT give the fully resolved sensitivity (62/77) but not these two. The evaluator's `strict_top5` is the pre-declared rule and was used for both earlier endpoints, so the reported verdict is correct. The release conclusion does not depend on these rows: count (4 rows short) and number (1 row short, with seven of the nine errors single-digit substitutions such as 8452 read as 0452 by the unchanged digit templates) fail regardless. The crop criterion (1 row short) hinges on row 21, which M1 shows to be a real pipeline failure.

M3. Reference provenance. The reference comes from two Claude Sonnet 5.5 readers and a third Claude adjudicator working from the same conventions and chart cards. The readers agreed on every number, classification and count, and on 357 of 369 strict sets, which partly reflects shared habits. The count reference is built from pixel scripts that locate the field block and a 19.75 pt line pitch, the same cues the pipeline uses, so the 1,289/1,289 recall shows agreement between two implementations of one rule more than independent discovery. Only `RETROSPECTIVE.md` and `sources.json` name the readers; the README, REPORT and registry outcome report "correct" counts without saying correct against an AI reference.

M4. Sampling frame. The numbered-section sample is 28 rows from the eight eligible pages (28, 39, 48, 53, 54, 64, 68, 77), up to six rows per page; each sorted section uses 18 of its 28 pages. Wilson and row-bootstrap intervals treat rows as independent, so intervals for the numbered section and for pooled rates understate page-level variation. Eight of the 18 "fresh" count pages (32, 35, 46, 47, 58, 98, 163, 171) carried first-endpoint or v2 recognition targets; they are fresh against the previous count pages only. No sampled target has a continuation line, so the 67 continuations in the inventory are checked only through the seven on the count pages.

M5. Timing evidence. Embedded `created_utc`, file mtimes and the hash chain place the freeze 77 minutes before the readers. The freeze files were first committed in `0445bad` at 15:33:31Z, after the readers started, and the reader prompt was written at 15:29:19Z. A commit made before launching readers would give an anchor that does not rest on file timestamps and the readers' self-reported start times.

M6. Reader exposure. Reader B's count task listed the directory above `blind/`, which printed the names `predictions.json`, `frame.json` and `count-page-detections.json`; the reader reports opening none. The adjudicator saw the ledger file name. The package records both as declarations. No reader's `files_opened` list contains a prediction or frame file, and `selection.json` holds geometry only.

## Scope and rights

No document claims decipherment, a sound or a meaning; codes are chart labels. The 1979 edition's record at the Helsinki research portal gives the title, authors Kimmo Koskenniemi and Asko Parpola, year 1979, Research Reports 1, Department of Asian and African Studies, ISBN 951-45-1627-3, and licence CC BY 4.0. The CC BY 4.0 deed requires credit, a licence link and an indication of changes; the README and conventions give all three. The persistent handle redirects (HTTP 302) to `helda.helsinki.fi`, whose page returned a bot-check error to my fetch, so I could not open the HELDA record; the local provenance JSON records the earlier browser download, and the PDF's SHA256 matches the freeze. The portal lists 179 pages and the local PDF has 180, as the provenance record notes (179 book pages). Tracked source crops and the 21 full count pages are CC BY derivatives listed in `TRACK-EXCEPTIONS.txt`. The 106 MB proposal file is local and named in `HOST-FILES.txt`. The v3 work depends on the 1979 edition, the licence deed and internal records only; the 1980 documentation entry is a v1 dependency.

## Writing

The prose scan is clean and the README opens with the result. Passages to fix: missing spaces in README line 31 ("pages(PDF 22–180)"), REPORT line 52 ("47,127,172"), REPORT line 95 ("195.0,390.1 or 975.2", "one, two orfive minutes"), REPORT line 99 ("rows,327/352") and RETROSPECTIVE lines 80 and 82 ("(320 fields),357/369", "counts:1,850", "pt(maximum"). The opening paragraph of RETROSPECTIVE still describes the readers as future work; the completed section further down supersedes it and should be marked. Several sentences warn against over-reading a number ("not counterfactual accuracy gains", "not promises", "confer no release status") where one methods statement would do. `sources.json` stores en dashes as mojibake (for example "printed 15â€“17") in the 1979 entry's `source_locations`.

## Required fixes, ranked

1. State the reference provenance next to the headline numbers in README, REPORT and the registry outcome: two Claude Sonnet 5.5 readers and a Claude adjudicator, no human reading, shared conventions, and a count reference built from the field-block cue.
2. Add the reading-choice sensitivity to REPORT and README: strict top five 64/80 if 35:2 and 70:4 were {23}, shape-only top five 65/80 (81.3%; 71.3 to 88.3%), and a sentence that the count and number criteria fail independently of those rows.
3. Correct "row 31's seven shifted unit windows" in the README to windows 3 to 6.
4. Repair the missing-space defects listed under Writing and mark the first RETROSPECTIVE paragraph as superseded.

## Optional improvements

1. Record the lower-edge mechanism in REPORT: a 0.4 to 1.3 pt strip of neighbour ink changes unit counts and codes through the column projection, which couples the crop and segmentation stages. The probe in `review-v3/` is one way to document it.
2. Add a page-clustered bootstrap, or a sentence on the eight-page numbered frame, to the interval tables, and say that 8 of the 18 count pages carried earlier recognition targets.
3. Commit the freeze before launching readers in later runs.
4. Note in the diagnosis that seven of nine number errors are single-digit substitutions, and that rows 14, 60, 65 and the last window of row 32 are specks or dash fragments, which are candidates for the next layout fix.
5. Fix the mojibake in `sources.json`. Add a short attribution note beside `page-count-source/`. Replace "immutable" for `OPTION-B-INTERFACE.md`, which the record commit amended (26 added lines and a whole-file line-ending change); the proposal file hash is what stays fixed.
6. The shared registry entry `HELSINKI1979-DIGITIZATION-01` still shows the first and v2 outcomes; the coordinator should integrate `registry-entry.json`.
