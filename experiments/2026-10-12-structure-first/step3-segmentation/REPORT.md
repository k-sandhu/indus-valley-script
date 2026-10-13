# Step 3: catalogued line divisions fall between recurring units; alternation cannot be tested at this scale

Where the catalogue marks a line division in an inscription, each line tends to recur elsewhere as a unit, and windows crossing the division do not. The segmenter chosen in step 5, run without line information, places a boundary at nearly every catalogued division. The Kober-style search for stems with alternating endings cannot discriminate at this corpus size: the Indus rate lies inside every comparison range, and step 5 shows the statistic does not separate readable scripts even on their true words. Endpoints: [run-linebreaks-2026-10-12-v3](run-linebreaks-2026-10-12-v3/summary.json) and [run-alternation-2026-10-12](run-alternation-2026-10-12/summary.json). Earlier line-break runs and their corrections are described in the [first](AMENDMENT-linebreaks-2026-10-12.md) and [second](AMENDMENT-linebreaks-v3-2026-10-12.md) amendments; the segmenter agreement and the stronger controls were computed in the [review](../review/REVIEW.md).

## Line divisions

Of 118 faces with a catalogued division ('/' in the visual code), 40 contain unknown or damaged signs, 6 have no line or crossing window of at least two signs and 3 are boustrophedon, leaving 69, of which 61 are square seals. Each line is read right to left. A line counts as found when it occurs as a contiguous part of a clean single-line text from another object. The controls are windows of the same lengths that cross the division, built under each line order.

| Comparison | Lines found | Crossing windows found | Lines higher | Crossings higher | Ties | Sign test p |
|---|---:|---:|---:|---:|---:|---:|
| Both line orders pooled | 23.7% | 8.4% | 25 | 3 | 41 | 0.00003 |
| Better line order per face (conservative) | 23.7% | 12.8% | 23 | 4 | 42 | 0.0003 |

Rates are per-face means; pooled over windows, 25.2% of lines and 6.0% of crossing windows are found. The decision rests on the 27–28 faces that are not tied. In the review's post-outcome controls the result survives counting identical faces once (22 against 4, p = 0.0005), dropping faces with a line of stroke numerals only (17 against 2, p = 0.0007), and moving the division to every other position of the same joined text, which lowers the mean line-minus-crossing difference from 0.186 to 0.029 (p = 0.0001). Six decided faces are Chanhu-daro seals with a separate line of strokes, where the catalogue's division may mark a group set apart in the seal field rather than wrapped text.

**Segmenter agreement (protocol output, computed in review).** Run on the clean texts plus the 72 joined multi-line faces, the Dirichlet-process segmenter places a boundary at 76 of 76 divisions in one line order and 74 of 76 in the other, against 37% of other positions in the same texts. Greedy n-gram matching reaches 73 and 67 of 76 against 49% elsewhere; branching entropy 29 and 44 against 37%. These are recall figures: a division shows where a boundary must fall, not where one cannot.

Whether earlier work used line divisions as segmentation evidence was not checked here; Parpola (1994) and Wells' publications should be consulted before any priority is claimed.

## Segmentation and alternation

The Dirichlet-process segmenter divides the 1,859 distinct texts into 6,137 units of mean length 1.39 signs (741 unit types, 70 of three signs or more). Its commonest multi-sign units are 861–002 (109), 817–002 (93) and 820–002 (66), then 760–740, 176–740, 740–400 and 032–220. Such recurrent pairs are described in Mahadevan's 1977 concordance and in Koskenniemi's 1981 segmentation, and Yadav and colleagues (2010) segmented the corpus into frequent n-grams; the segmenter recovers known structure.

From these units only 68 stems can be formed, of which 2 alternate (0.029). Comparison words subsampled to the same unit-length profile give 0.046 for Ur III seal legends (95% range 0.015–0.095), 0.012 for Sumerian lines (0–0.045), 0.019 for Akkadian letters (0–0.061) and 0.031 for Egyptian sentences (0–0.062). The IVS value lies inside all four ranges. Whole texts give 0.024; branching-entropy segments 0.055; greedy segments 0.081. All alternation figures are descriptive under the step 5 rule.

## What the result decides

The protocol gave no per-hypothesis prediction for the line-division test, so it is descriptive for the ledger. It does constrain how future segmentation work should proceed: catalogued divisions are the only boundary evidence internal to the corpus, the Dirichlet-process segmenter recovers them, and a larger sample from multi-line tablets and from sign spacing measured on photographs would allow segmentation to be trained and checked against them. The alternation statistic decides nothing at this scale.
