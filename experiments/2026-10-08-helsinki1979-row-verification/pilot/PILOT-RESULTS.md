# Pilot results: two readers and an adjudicator on three pages

Recorded by the coordinator on 8 October 2026. Status: Frozen evaluation for the readings; Exploratory for the projection.

The pilot ran the workflow in [PILOT.md](../PILOT.md) on PDF pages 53, 83 and 170 of Koskenniemi and Parpola's *Corpus of Texts in the Indus Script* (1979), one page from each section, using package M's v2 proposals. Six column batches held 216 printed rows. Each batch also carried three hidden control rows from the v2 80-row adjudicated reference. Twelve Claude Sonnet 5.5 subagents read the batches: Reader 1 corrected the proposals, and Reader 2 read blind. Five further Sonnet subagents settled the disputes. Every agent ran in a fresh session with its own delivery root and helper folder. All 12 reader returns and 5 adjudicator returns passed `validate_return.py`. The scorer outputs are [scored-initial-v1](scored-initial-v1/metrics.json) and [scored-final-v1](scored-final-v1/metrics.json), and the merge summary is [merge-summary-v1.json](merge-summary-v1.json). The raw returns, packets and merged records stay local under `data/raw/2026-10-08-helsinki1979-row-verification/`.

## Accuracy on the hidden controls

Each role read 18 control rows without knowing which they were. Both roles read the inscription number, classification, unit count and crop judgment correctly on all 18. On the full strict code sequence, Reader 1 scored 17 of 18 and Reader 2 16 of 18. With unit kinds and underlines included, each role had all fields right on 16 of 18 rows (88.9%, Wilson 95% interval 67.2–96.9%), which fails the screening threshold of 95% set in the protocol. The four misses were these:

| Role | Control | Reader | Reference |
|---|---|---|---|
| Reader 1 | v2 sample 27 | kept the first narrow hatched patch as {597, 598} | 598 |
| Reader 1 | v2 sample 50 | labelled the hatched cells 454 and 596 as `sign` | `hatched_span` |
| Reader 2 | v2 sample 65 | narrowed the underlined double stroke to 769 | {543, 769} |
| Reader 2 | v2 sample 17 | kept the underlined comb as {465, 485, 486} | 486 |

None of the misses is a confidently wrong number, classification or count. Two are wider candidate sets than the reference, one is a unit-kind label and one narrows a pair of codes that the chart draws identically. No pair of readers agreed on a wrong control value. All four rows went to adjudication, and the adjudicators' final readings match the reference in every field, so the merged output is correct on all 18 controls. These controls measure agreement with an earlier AI-produced reference that no expert has reviewed.

## Agreement and adjudication

The readers agreed on 185 of 216 target rows (85.6%, 95% interval 80.3–89.7%). The other 31 (14.4%; page bootstrap 8.3–25.0%) went to adjudication, in five of the six columns. An item can carry more than one dispute, and most came from a few conventions rather than from difficult page reading:

- 17 of the 18 disputed items in page 83, column 1, concerned whether to keep a pair of stroke codes that the chart draws identically (8/764, 9/765, 10/766, 543/769). The adjudicator kept the pair every time.
- 7 items on pages 53 and 170 differed on whether the hatched ring cells 596 and 454 are `sign` or `hatched_span`. The adjudicators chose `hatched_span`.
- At least 5 items involved the chart labels 205/206/208 and 465/485/486, and 6 involved the 597/598 spacing rule.
- The rest were readings of the page: a bow-tie read as 235 or 593 in two rows, a Y read as 443 or 126, the 58/68 rectangle, and one difference in a row's vertical position.

The adjudicators found that the project's chart reference mislabels the three-tick U. The printed chart gives class 327 with code 208 (`output/chart_atlas/cells/p21_c6_r1.png`), but the reference records 206 with high confidence. The two-tick cell above it, class 326 (`p21_c5_r34.png`), is recorded as 205 with alternatives 206 and 208. The coordinator confirmed the printed digits on the crops. Package P (`experiments/2026-10-08-chart-reference-audit/`) re-reads all 687 chart codes and measures which references and release tables depend on them.

## Merged output

All 216 rows have a final reading: 144 were agreed, 6 were settled to unique codes by adjudication, and 66 keep at least one candidate set. Every one of those 66 rows is complete in its number, classification, unit count and crop judgment, and its only open values are code sets. Of the 72 open sets, 63 are stroke pairs the chart prints identically (9/765 in 34 units, 8/764 in 13, 10/766 in 7, 543/769 in 6, 501/768 in 3), 8 are 597/598 hatching positions and 1 is the 58/68 rectangle. The merge stages 150 fully resolved rows for the ledger and imports none; package L still needs a reviewed object and surface concordance.

## Time and token use

The coordinator recorded each agent's token total and task duration from the Claude Code task notifications in [coordinator-task-ledger-v1.jsonl](coordinator-task-ledger-v1.jsonl). These totals combine input, cached context re-reads and output, so they are not a price. A reader task of 39 rows used 349,502 to 462,740 tokens (mean 409,235) and took 17 to 75 minutes (mean 27). Reader 1, who saw the proposals, was no faster than the blind Reader 2. Reader 1 corrected several proposals, including printed numbers (3190 to 3199, 3166 to 3188, 1100 to 1102) and missed underlines. Adjudication used 1,308,140 tokens for 35 rows in five tasks (mean 14 minutes per task). The pilot as a whole used 6,218,955 tokens, or 28,791 per target row.

[coordinator-cost-projection-v1.json](coordinator-cost-projection-v1.json) projects the full edition from these measurements, using v3's 11,702 numbered occurrences in 328 printed columns. It assumes one reading task per column for each role and one adjudication task for every column with a dispute. The median projection is 336 million tokens (bootstrap 95% interval 302–366 million) and 346 agent-hours (276–462). That is about 29 hours of wall-clock time with 12 agents running at once, or 14 hours with 24, if rate limits allow that concurrency.

## Changes before a full run

The disputes suggest four changes, each to be confirmed on a second small pilot before the full run starts:
- State in the reader instructions that coincident stroke pairs always stay as sets and that 596 and 454 are `hatched_span`.
- Correct the chart labels that package P confirms.
- Use the v3 proposals.
- Consider running Reader 1 blind as well, since seeing the proposals saved no time and two blind readings are more independent.

The first two changes do not touch the page readings or the 597/598 spacing cases. Those account for 6 to 9 of the 31 items, depending on how overlapping disputes are counted, or about 3–4% of rows. That share is an estimate from the dispute types; a second pilot would measure it.

## Process notes

Several readers listed folder names outside their own role, including other batches' return files and other agents' helper folders. They reported this, and none opened those files. One reader saw inscription 3245 printed as an example on chart page 16 before reading that row. Reader 2 on page 170, column 1, reported 1,566 seconds in its return while the task ran for 4,504 seconds; the projection uses task durations. Package M's v3 blind sample, prepared after this pilot was drawn, includes one row on page 53. The two sets of readers were separate agents and neither saw the other's output.
