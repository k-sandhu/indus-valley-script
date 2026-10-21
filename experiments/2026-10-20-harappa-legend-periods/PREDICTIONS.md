# Frozen predictions: Harappa legend-periods shot

Written 20 October 2026 after exploring the discovery seals ([EXPLORATION.md](EXPLORATION.md)) and before any relation between a Mound F legend and its stratum was computed. The machine-readable copy registered with the bench loader is [PREDICTIONS.json](PREDICTIONS.json); this file, the scorer, the statistics modules, the protocol, the input builder and the frozen parameters are hashed as artifacts of the same freeze. Conjecture: [C-0010](../../knowledge/conjectures/C-0010-seal-legend-fixed-pattern.md). Design: [PROTOCOL.md](PROTOCOL.md).

## Population and shared definitions

The confirmation population is every Harappa seal family from Vats's Mound F with a stratum in the Lipi export, 175 families. Frames are Vats's trench cells with at least 15 seals: Trench I (37), the Granary area (37), Trench VI (33), Trenches IV and V (24), the cell without a trench name (22) and Trench III (20); the two seals of Trench A and Trench V are dropped. A seal's clock value u is the mid-rank of its stratum over the 173 seals in frames, scaled from 0 (Stratum VII, oldest) to 1 (Stratum I, latest). The early third (u < 1/3) is Strata VII to V, which the export assigns to HARP 3B-1 and 3B/C; the late third (u ≥ 2/3) is Strata II and I, assigned to 3C-3 and 3C-4. Openings and closings are read at surviving edges of single-line legends, complete one-sign legends are left out of both, and identical complete legends in one frame are merged at their median u. Every permutation null moves u among the analysed units within frames, with 9,999 draws and the observed value counted as one draw.

The frozen parameters are in [discovery-v2/frozen-parameters.json](discovery-v2/frozen-parameters.json). The closing stock is 740, 520, 090, 400, 151, 156, 527, 617, 621, 226, 892, 407, 405, 154 and 595: the union of the stock of Mackay's DK-G seals at Mohenjo-daro and the stock of the 253 Harappa seals outside the confirmation population, each defined as the signs that close at least five legends of two or more signs and stand last in at least half of their occurrences.

## Predictions

C-0010 predicts that the closing stock holds its share from the early to the late third and that no drift test finds drift. A drift test has three outcomes: "drift" when its permutation p is at most 0.05 and each of the ten units whose deletion moves the statistic most toward its null, deleted alone, leaves p at most 0.10 (2,999 draws); "no drift" when p exceeds 0.10; "inconclusive" otherwise.

| ID | Statistic | Null | Pass rule | Effect on credence |
|---|---|---|---|---|
| P1 | Closing-stock share, late third minus early third | 90% bootstrap interval within frames (9,999 resamples); two-sided permutation p within frames | Pass: interval inside (−0.25, 0.25), and still inside after each of the ten most influential single deletions (1,999 resamples each). Fail: permutation p ≤ 0.05 with an estimate of at least 0.15 in absolute value, surviving the deletion rule. Otherwise inconclusive | pass +0.05; inconclusive −0.02; fail −0.10, and a fail with Holm-adjusted p ≤ 0.05 kills |
| P2 | Closing-stock share among early-third legends | Fixed threshold | At least 0.55, also after deleting one early-third legend that closes in the stock | pass +0.02; fail −0.06 |
| P3 | Opening signs: rank analysis of variance of u across opening categories (signs opening at least five units; the rest pooled) | Permutation | No drift | no drift +0.05; inconclusive −0.03; drift −0.10 |
| P4 | Variant choice: summed between-variant statistic over Mayig classes with at least two Wells codes of three or more tokens and ten rows, minus degrees of freedom; all legends | Permutation | No drift | no drift +0.02; inconclusive −0.02; drift −0.08 |
| P5 | Length: correlation of within-frame length rank with u, complete legends | Permutation, two-sided | No drift | no drift +0.02; inconclusive −0.02; drift −0.08 |
| P6 | Sign inventory: for each sign in at least eight legends, its legend count times the squared deviation of its legends' mean u from the overall mean, summed over signs and divided by the variance of u; all legends | Permutation | No drift | no drift +0.02; inconclusive −0.02; drift −0.08 |
| P7 | Closing signs: rank analysis of variance of u across closing categories (signs closing at least five units; the rest pooled) | Permutation | No drift | no drift +0.04; inconclusive −0.03; drift −0.10 |
| PC | Positive control: correlation of u with a rectangular seal, every seal in frames | Permutation | Positive, one-sided p ≤ 0.05 | gates the gains (below) |

Leave-one-frame-out results are reported for every drift without changing its outcome.

## Joint credence rule and kill condition

All predictions share the same Mound F seals, so they move one credence. C-0010 stands at 0.40 before the read. Its credence after the read is 0.40 plus the effects of P1 to P7, held within 0.02 and 0.90. When the positive control fails, the gains of a P1 pass and of every "no drift" count at half weight, and losses count in full; P2, a level, is not gated. The card is dead, at 0.02, if P1 fails or any of P3 to P7 shows drift, with a Holm-adjusted p-value at most 0.05 over the six p-values of P1 (its permutation p) and P3 to P7. Otherwise it is strengthened if the result exceeds 0.40 and weakened if not. The largest possible result is 0.62.

## What the test can see

Power was estimated before the freeze ([power.py](power.py), [discovery-v2/power.json](discovery-v2/power.json)) on synthetic populations with Mound F's frames and strata, filled with legends and seal forms drawn from the 253 Harappa seals outside the confirmation population. Effects were planted by stratum order; then a quarter or a half of the seals in each trench exchanged strata at random, the way residual, intrusive and misassigned seals degrade a real drift. Each cell has 200 replicates (400 for no effect) with 999 permutations or resamples, so a rate carries a standard error of about 0.035.

With no planted effect the drift tests find drift in 3.5% to 5.8% of populations and "no drift" in 90% to 92%; P1 passes 56%, fails 4.3% and is inconclusive 40%; P2 passes 99%. When the closing-stock share truly differs by 0.10, 0.20 and 0.30 between the thirds, P1 passes 35%, 10.5% and 2.5% and fails 7.5%, 31% and 68%.

| Planted change | No mixing | Quarter mixed | Half mixed |
|---|---|---|---|
| Opening sign chosen by period in 15% of legends (P3) | 0.28 | 0.21 | 0.14 |
| Opening sign chosen by period in 25% of legends (P3) | 0.64 | 0.42 | 0.22 |
| Opening sign chosen by period in 35% of legends (P3) | 0.89 | 0.68 | 0.41 |
| Variant chosen by period for 25% of tokens (P4) | 0.31 | 0.23 | |
| Variant chosen by period for 50% of tokens (P4) | 0.93 | 0.73 | |
| Late third longer by 0.5 signs (P5) | 0.16 | 0.11 | |
| Late third longer by 0.8 signs (P5) | 0.38 | 0.22 | |
| Late third longer by 1.2 signs (P5) | 0.58 | 0.34 | |
| One interior sign chosen by period in 25% of legends (P6) | 0.13 | 0.15 | |
| One interior sign chosen by period in 50% of legends (P6) | 0.59 | 0.39 | |
| Closing sign chosen by period in 25% of stock-closing legends (P7) | 0.37 | 0.28 | |
| Closing sign chosen by period in 50% of stock-closing legends (P7) | 0.99 | 0.84 | |
| Rectangular seals rising from 10% to 25% (PC) | 0.39 | 0.24 | |
| Rectangular seals rising from 10% to 30% (PC) | 0.52 | 0.40 | |

Rates are the share of populations whose outcome is "drift" (or a PC pass). A change in which closing signs are used leaves the stock share unchanged, and P1 passes in 50% to 64% of those populations. The test therefore detects an opening drift of one legend in four with probability 0.64 when strata are recorded correctly and 0.42 after a quarter of the seals are displaced, a shift of half the stock-closing legends to period-specific closers almost always, and a length increase of the size CHRONOLOGY-REGION-01 measured across all Harappa faces (0.72 signs, equal-type) in about a third of populations. It misses most drifts below one legend in six, and the positive control is weak: a rise in rectangular seals like the one HARP describes is detected in fewer than half of the populations.

If Mound F repeated the discovery seals' own association (discovery seals resampled with their period ranks into Mound F's shape), the drift rates would be P3 0.67, P4 0.47, P5 0.04, P6 0.70, P7 0.36 and PC 0.77. These are upper bounds: resampling 99 seals into 173 places copies of one legend at one rank, which the tests read as an association, and on the discovery seals themselves P3 gives p = 0.56. If Mound F repeated Mackay's DK-G sequence the rates would be P3 0.12, P4 0.06, P5 0.09, P6 0.19, P7 0.08, P1 pass 0.74 and PC 0.40.

## Reliability

On the discovery seals, per-sign period means barely replicate between random halves ([discovery-v2/reliability.json](discovery-v2/reliability.json)): the split-half correlation for signs in any position is 0.11 (Spearman–Brown 0.20), a shrunken opening-sign score transfers to the other half at r = 0.19 (positive in 85% of 500 halvings), and a closing-sign score at r = −0.06. The per-sign measures are too noisy to test sign by sign, so every drift prediction is an omnibus statistic whose power is stated above.

## Not counted as confirmation

P2's level, the share of legends closing in the stock, is predictable from corpus-wide closing structure already examined ([SEAL-LEGEND-UNITS-2026-10-20](../../knowledge/registry/attempts/SEAL-LEGEND-UNITS-2026-10-20.json)); it carries a small weight and is not counted as fresh. The rise of rectangular seals in Mound F was reported by Fuls and its face-level counts by stratum were printed in this package's census before the design was fixed; the positive control confirms a known change and is not a prediction of the conjecture.
