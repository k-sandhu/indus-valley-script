# Pilot 2 results: two blind readers with clarified conventions

Recorded by the coordinator on 8 October 2026. Status: Frozen evaluation for the readings; Exploratory for the projection.

Pilot 2 ran [PILOT-2.md](../../PILOT-2.md) unchanged on PDF pages 152 and 162, which are both in the beginning-sorted section. Four column batches held 144 printed rows, and each carried three hidden controls from the v2 80-row reference. The design differed from pilot 1 in four ways:

- Both readers read blind.
- The instructions required coincident stroke pairs to stay as sets and the hatched cells 596 and 454 to be `hatched_span`.
- The charts carried the corrected v2.1 labels.
- The geometry came from package M's v3 proposals.

Eight Claude Sonnet 5.5 subagents read the batches in fresh sessions, and four more adjudicated the disputes. All twelve returns validated. The outputs are [scored-initial-v1](scored-initial-v1/metrics.json), [scored-final-v1](scored-final-v1/metrics.json) and [merge-summary-v1.json](merge-summary-v1.json). The token ledger is local at `data/raw/2026-10-08-helsinki1979-row-verification/pilot2-returns-2026-10-08-v1/coordinator-usage-final.jsonl`.

## Results beside pilot 1

| Measure | Pilot 1 (pages 53, 83, 170) | Pilot 2 (pages 152, 162) |
|---|---|---|
| Target rows | 216 | 144 |
| Reader design | Reader 1 saw proposals, Reader 2 blind | both blind |
| Readers agreed | 185 (85.6%) | 132 (91.7%, 86.0–95.2%) |
| Sent to adjudication | 31 (14.4%) | 12 (8.3%, 4.8–14.0%) |
| Controls, all fields, first pass | 16/18 per role | 10/12 per role |
| Control number, class or count errors, first pass | 0 | 1 (Reader 1 read 3549 for 3649) |
| Controls, all fields, after adjudication | 18/18 | 11/12 |
| Wrong values both readers agreed on | 0 of 18 control pairs | 0 of 12 |
| Rows whose only open values are code sets | 66 | 30 |
| Combined tokens per target row | 28,791 | 29,339 |

The convention changes removed the dispute types that dominated pilot 1. The 12 disputed items in pilot 2 concern page readings:
- six rows where one reader took the diamond for 113 and the other for 164 (the adjudicator chose 164 from its open centre);
- three printed numbers with broken or dotted digits (2086, 3649, 3286);
- two units where 28 and its underlined form 256 were confused;
- a tick read as 23 or {1, 23};
- a Y read as 443 or 126;
- a few row positions and blank gaps.

The target queue of 8.3% meets the 10% limit the protocol set before reading.

The screen still fails on its control criteria. In the first pass, Reader 1 misread one control number (3549 for 3649, on a dotted print) and Reader 2 misread one Y as 443. Each misread was caught because the other reader got it right and the row went to adjudication. After adjudication, the number, classification, count, crop, unit kind and underline are correct on all 12 controls, and the strict sequence is correct on 11. The remaining difference is a worn pair of ticks. The reference keeps {23, 25}, while the adjudicator measured the marks and chose 25. That is a set-width disagreement with an AI-produced reference, not a confident wrong code that the reference rules out. Across both pilots, no control showed a wrong value that both readers agreed on (30 control pairs).

## Time and tokens

The pilot used 4,224,785 tokens: 3,350,791 for the eight reader tasks and 873,994 for the four adjudications. Reader tasks used between 328,894 and 535,682 tokens. The readers' own start and finish times give 16 to 52 minutes per 39-row task, with a mean of 26 minutes. Three reader tasks stayed open in the harness for about 104 minutes each, long after the readers recorded finishing (at 20:52, 21:05 and 21:08 UTC). They closed together at about 22:20 UTC. The task durations therefore overstate reading time, so the time projection below uses the readers' recorded times. Adjudication took 4 to 21 minutes per batch.

The scorer's projection for 11,702 numbered occurrences in 328 columns, with two blind readers per column and one adjudication per disputed column, gives a median of 340 million combined tokens (bootstrap 95% interval 299–383 million). Its time projection uses the inflated task durations and should be read as an upper bound. From the readers' recorded times, the full run is about 285 reader-hours plus about 55 adjudication-hours, or roughly 28 hours of wall-clock time at 12 concurrent agents. The token figure is close to pilot 1's (336 million), because blind reading cost about the same per row as assisted reading.

## What remains open

Both pilots measure agreement with an earlier AI reference, and no expert has reviewed either. The controls are few (30 pairs in all), so the observed absence of agreed wrong values bounds that error rate only loosely. The 95% upper limit for an error that both readers share is about 10% of rows. Pilot 2 covered one section and no continuation lines, so the end-sorted and number-order sections enter the full run on pilot 1's evidence alone.
