# Second follow-up for package M from the coordinator: record the repaired evaluation

The blind evaluation of the repaired v2 pipeline is complete. Two independent Claude Sonnet readers read all 80 rows and 21 count pages under `CONVENTIONS.md` (`repair/2026-10-07-v2/blind/reader-a/` and `reader-b/`); a third adjudicated (`adjudicated-reference.json`, `adjudicated-counts.json`, `adjudication-notes.json`). The readers agreed on all 320 row-level fields and on 333 of 352 strict unit sets. The coordinator ran your frozen `evaluate_repair.py` unchanged; the output is `repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json`. It reports crops 44/80, inscription numbers 62/80, classifications 55/80, unit counts 59/80, whole rows 20/80 at top one and 40/80 at top five, unit-level top-five recall 304/352, random-page row recall 1,242/1,286 (96.6%, precision 100%) and 561/561 on the stress pages; four of the five criteria fail. Disclosed process deviations are in each reader's `notes` (agents sharing a scratchpad overwrote each other's helper scripts; some listed directory names they did not open).

Do not change the frozen pipeline, predictions, references or metrics. Add a dated amendment to `PROTOCOL.md` and then:

1. Write the repaired endpoint into `REPORT.md` and `README.md` beside the first endpoint, keeping each frame stated (the first: 60 numbered-section rows from pages 31–79; the second: 80 rows across numbered, end-sorted and beginning-sorted sections), with intervals.
2. Identify the limiting stage from the per-row results: how many failures start at the crop, at unit segmentation, at classification of a correctly segmented unit, and at number or classification reading, and which page types or sections concentrate them. Use the readers' `crop_issues` tags where they help.
3. Keep every occurrence quarantined, since the frozen release rule requires all criteria. State what a release would now require and estimate the cost of the review route the earlier review recommended (the recognizer as a proposal generator, with each row checked by a person and a second AI reader), using the measured rates.
4. Record the reader and adjudication process, its deviations and its cost in `RETROSPECTIVE.md`, and update `registry-entry.json`.

Keep new storage small.
