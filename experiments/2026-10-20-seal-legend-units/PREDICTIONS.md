# Prospective predictions: closing formulas on seals no analysis has read

Frozen on 20 October 2026, before any legend of either fresh pool was read. The hashes of this file, of [predictions.json](predictions.json) (pass bounds for every pool size and the power tables), of the scorer [score_prospective.py](score_prospective.py) with the code it imports, of [RULES-v2.md](RULES-v2.md) and of the version 2 inventory and closing stock are listed in [PREDICTIONS.sha256](PREDICTIONS.sha256). The scorer refuses to run if any of them has changed and logs every read in `prospective-access.jsonl`. A later change to a prediction is a dated amendment in a new package; the frozen outcome stays as this package's result.

## The claim

An Indus seal legend is a variable opening joined to a closing formula drawn from a shared stock of about fifty formulae, most of them one or two signs and many ending in the jar sign 740. When a scribe had to break a legend across two lines, the break came after the closing formula, and the second line held a short group of one to three signs. Credence 0.6.

The stock is the version 2 closing stock of this package: 49 formulae (13 of one sign, 27 of two and 9 of three) that a segmenter trained on the catalogue's line divisions found after the strongest boundary of seal legends in at least three unrelated groups of objects ([AMENDMENT-1.md](AMENDMENT-1.md)). A legend's closing formula is found by Rule 1 of [RULES-v2.md](RULES-v2.md), the longest final stretch of one to four signs that is in the stock, and its opening is what precedes it. These are the units that section 2 of the [working model](../../knowledge/WORKING-MODEL.md) reads as a personal name and a title; the predictions below test the structure, not those meanings.

## Pools and populations

The predictions are scored separately on two pools. The first is the absent seal numbers of the CISI 3.1 range: 244 Mohenjo-daro and Harappa numbers that lie between present seals or tablets are missing from the Lipi export ([absent-numbers.csv](../2026-10-13-cisi3-range-coverage/run-2026-10-13/absent-numbers.csv)), 84 of them between seals, and they become readable when CISI 3.1 is acquired (question [Q-1008](../../knowledge/questions/Q-1008-acquire-cisi-3-1.md)). The second is inscribed seals published after the catalogues closed (question [Q-1026](../../knowledge/questions/Q-1026-post-catalogue-finds.md)). A legend already transcribed in the Lipi export, or in any file this package read, is not fresh and is left out.

The single-line population of each pool is every seal face (object type `SEAL*`) whose legend is on one line, is complete, has no unreadable or damaged sign and has at least three signs, with identical legends within the pool counted once. Legends identical to a known text count and are reported. The divided population is every such seal face whose legend is on two lines; the main line is the longer one, or the first in reading order when both are equally long. Expected sizes: about 50 single-line legends in the CISI 3.1 pool (60% of the present CISI 3.1 seal faces meet the rule) and one or two divided ones; for the post-catalogue pool no count exists, and power is given at 20 and 50. Recurrence is always looked up in the build corpus B of this package, the corpus on which the calibration was made.

## Predictions

Expected values come from the 171 legends of the held set H, which played no part in building the inventory, and the bounds are predictive intervals from those counts at the pool's actual size. Power is the probability of passing under the stated rate, from 20,000 to 40,000 simulated pools.

**P1. Most fresh legends close with a formula from the stock.** Statistic: the share of single-line legends with a stock closing. In H it is 0.760 (130 of 171); with the signs of each H legend shuffled into a random order it is 0.207. Pass: the share is at least the lower 2.5% predictive bound for the pool's size (0.62 at 50 legends, 0.55 at 20, 0.64 at 80). Kill: in a pool of at least 20 legends, the share is at or below the 97.5% quantile of the shuffled rate (0.32 at 50 legends, 0.40 at 20).

| Pool size | Lower bound | Pass if the rate is H's | if 0.15 lower | if 0.25 lower | if signs are shuffled |
|---:|---:|---:|---:|---:|---:|
| 20 | 0.55 | 0.99 | 0.79 | 0.45 | 0.001 |
| 50 | 0.62 | 0.99 | 0.50 | 0.08 | 0.000 |
| 80 | 0.64 | 0.99 | 0.35 | 0.02 | 0.000 |

**P2. Endings recur more than beginnings.** For each single-line legend we ask whether its final two signs end any text of B and whether its first two signs begin any text of B. In H the final pair is known for 0.789 and the initial pair for 0.602; 54 legends have only the ending known and 22 only the beginning (one-sided exact McNemar p = 0.0002). Null: endings and beginnings recur equally. Pass: more legends have only the ending known than only the beginning, with one-sided exact McNemar p < 0.05. Power at H's rates is 0.57 for 50 legends, 0.22 for 20 and 0.78 for 80; with half H's asymmetry it is 0.20 at 50; under the null the pass rate is 0.03.

**P3. Openings are new.** Among single-line legends with a stock closing and an opening of at least two signs, the share whose whole opening occurs as a stretch of some text of B. In H it is 0.171 (21 of 123). Pass: the share is at most the upper 97.5% predictive bound for the number of openings scored (0.33 for the 36 openings expected from 50 legends, 0.43 for 14). If openings were formulae drawn from a small set like the closings, about nine in ten would be known; the pass rate under that alternative is 0.00 at every expected size, and 0.39 if the true share were 0.20 higher than H's at 50 legends.

**P4. Scribes broke the line after the closing formula (long shot).** Statistic: the share of divided legends whose main line, read alone, ends in a stock closing. On the 58 distinct divided seal legends of the known corpus it is 0.62 (36), against 0.22 when the division is moved to each other position of the same legend; those divisions trained the segmenter, so this value is in-sample. Null: the division falls at a position unrelated to the closing, with each face's chance computed in the same way. Pass, once at least three divided legends are scored over both pools: the share is at least 0.5 and the one-sided binomial p against the mean chance is below 0.05. With three faces all three must qualify (power 0.25 at the known rate), with six faces four (power 0.60), with ten faces five (power 0.88). The pools are expected to hold too few divided legends for a decisive test.

## Joint credence rule and kill condition

The predictions share legends, so their effects are combined pool by pool. For a pool of at least 20 single-line legends, the credence of the claim (0.6) changes by: P1 pass +0.05, fail −0.10; P2 pass +0.03, a difference in the predicted direction without significance 0, a difference of zero or in the other direction −0.10; P3 pass +0.03, fail −0.05, in which case the claim's "variable opening" is restated as a formulaic opening. A pool's total change lies between −0.20 and +0.10, and a pool of fewer than 20 legends moves the credence by half as much. P4, scored once over both pools, adds +0.05 if it passes and −0.05 if it fails on six or more legends. Section 2 of the working model (credence 0.45) moves by half of each change to this claim.

The claim is dead if P1's kill condition is met in any pool of at least 20 legends: fresh legends that close with a stock formula no more often than shuffled ones would show that the stock describes the known corpus and nothing else.

## Statistic families

Scoring spends two families on the fresh pools, recorded for the ledger `bench/spent.json` in [spent-entry.json](spent-entry.json): `seal_legend_closing_structure` (P1 to P3) and `line_division_unit_boundary` (P4). The known corpus is spent for both families by this package: every clean text trained the segmenter or built the inventory, the held set H was read once to calibrate these predictions, and the known divided faces were read for training, cross-validation and P4's in-sample value.
