# Frozen predictions: Mohenjo-daro stratigraphy shot

Written 20 October 2026 after exploring Mackay's DK-G seals ([EXPLORATION.md](EXPLORATION.md)) and before any relation between Marshall's legends and depths was computed. The machine-readable copy registered with the bench loader is [PREDICTIONS.json](PREDICTIONS.json); this file, the scorer, the statistics module, the protocol, the frozen parameters and the Mayig crosswalk are hashed as artifacts of the same freeze. Conjecture: [C-0006](../../knowledge/conjectures/C-0006-closing-stock-fixed-from-lowest-levels.md). Design: [PROTOCOL.md](PROTOCOL.md).

## Population and shared definitions

The confirmation population is every Mohenjo-daro seal joined to a row of Marshall's 1931 seal table that prints a numeric depth below the modern surface. Each seal is ranked by depth within its stratum (Marshall's area with the export's section where that cell holds at least 15 seals with a depth, otherwise the rest of the area pooled; strata with fewer than five seals dropped), and u is that rank scaled from 0 at the deepest to 1 at the highest. Before reading, the strata hold 434 seals: HR-B 72, VS-A 63, C/DK-C 51, HR unspecified section 45, E/DK-E 44, HR-A 32, DK/DK-C 29, DK/DK-B 27, D 15, SD 14, B 10, VS remainder 10, L 9, HR remainder 7 and DM 6. The bottom third is u < 1/3 and the top third u ≥ 2/3. A legend is one per seal; identical complete legends in one stratum are merged at their median u. Every permutation null moves u among the analysed legends within strata, with 9,999 draws and the observed value counted as one draw.

The frozen parameters, all from Mackay's DK-G seals, are in [discovery-v2/frozen-parameters.json](discovery-v2/frozen-parameters.json). The closing stock is 740, 520, 090, 400, 151, 156, 527, 617, 621, 226, 892 and 407: the signs that close at least five DK-G legends and stand last in at least half of their occurrences. The closing formulae are the 25 final sign pairs that close at least four DK-G legends. The non-final height scores give each of 120 signs its mean DK-G height rank over legends where it stands before the last position, shrunk toward 0.5 with a weight of ten legends.

## Predictions

| ID | Statistic | Null | Pass rule | Effect on credence |
|---|---|---|---|---|
| P1 | Closing-stock share among legends of two or more signs, top third minus bottom third | 90% percentile interval from 9,999 bootstrap resamples within strata | Interval inside (−0.20, 0.20), and still inside after deleting, one at a time, each of the ten legends that move the estimate most (1,999 resamples each). Otherwise inconclusive when the estimate lies inside (−0.20, 0.20), and fail when its absolute value is 0.20 or more | pass +0.05; inconclusive −0.03; fail kills |
| P2 | Closing-stock share among bottom-third legends | Fixed threshold | At least 0.60, also after deleting one bottom-third legend that closes in the stock | pass +0.03; fail −0.10 |
| P3 | Closing-formula share, top third minus bottom third | As P1 | As P1 | pass +0.03; inconclusive −0.02; fail −0.05 |
| P4 | Rank analysis of variance of u across opening signs (signs opening at least five legends; the rest pooled) | Permutation | One-sided p ≤ 0.05; each of the ten legends whose deletion lowers the statistic most, deleted alone, leaves p ≤ 0.10 (2,999 draws) | pass +0.08; fail −0.06 |
| P5 | z(opening) − z(closing): the P4 statistic for both positions of the same legends, each standardised by its own null | Joint permutation of both positions | One-sided p ≤ 0.05 | pass +0.06; fail −0.04 |
| P6 | Variant choice: summed between-variant statistic over Mayig classes with at least two Wells codes of three or more tokens and ten rows, minus degrees of freedom; all readable legends | Permutation | One-sided p ≤ 0.05 and the P4 deletion rule | pass +0.05; fail −0.04 |
| P7 | Correlation of within-stratum length rank with u, complete legends | Permutation | Positive, one-sided p ≤ 0.05, and the P4 deletion rule | pass +0.04; fail −0.03 |
| P8 | Correlation of u with the mean DK-G score of the legend's non-final signs (long shot) | Permutation | Positive, one-sided p ≤ 0.05, and the P4 deletion rule | pass +0.05; fail −0.01 |
| P9 | Correlation of u with a rectangular seal (auxiliary) | Permutation | Positive, one-sided p ≤ 0.05, and the P4 deletion rule | none |

Leave-one-stratum-out results are reported for every drift test that passes, without changing its outcome.

## Joint credence rule and kill condition

All predictions share the same Marshall seals, so they move one credence. C-0006 stands at 0.20 before the read. Its credence after the read is 0.20 plus the effects of P1 to P8, held within 0.02 and 0.90. A drift pass in P4 to P8 counts at half weight when its Holm-adjusted p-value across those five tests exceeds 0.05. P9 has no effect. The card is dead, at 0.02, if P1 fails (the closing-stock share differs between the top and bottom thirds by 0.20 or more) or if P4, P5, P6 and P7 all fail. Otherwise it is strengthened if the result exceeds 0.20 and weakened if not.

## Power and reliability

Power was estimated before the freeze ([power.py](power.py), [discovery-v2/power.json](discovery-v2/power.json)) on synthetic populations with Marshall's strata, stratum sizes and tied depth values, filled with legends drawn from Mackay's seals. Effects were planted on the true height; then a quarter or a half of the seals in each stratum exchanged heights at random, the way residual and intrusive finds degrade a real drift. Each cell has 200 replicates (300 for no effect) with 999 permutations or resamples, so a pass rate carries a standard error of about 0.035.

With no planted effect the drift tests pass at rates 0.040 to 0.063, and the fixity tests pass at 0.91 (P1), 1.00 (P2) and 0.80 (P3). When the closing-stock share truly differs by 0.20 between top and bottom, P1 passes at 0.035 and kills at 0.57; at a true difference of 0.10 it passes at 0.46 and kills at 0.08.

| Planted drift | No mixing | Quarter mixed | Half mixed |
|---|---|---|---|
| Opening sign chosen by period in 15% of legends (P4; excess divergence 0.049 bits) | 0.56 | 0.39 | 0.16 |
| Opening sign chosen by period in 25% of legends (P4; 0.100 bits) | 0.98 | 0.80 | 0.40 |
| Opening sign chosen by period in 35% of legends (P4; 0.162 bits) | 1.00 | 0.96 | 0.67 |
| Contrast P5 at 25% | 0.92 | 0.71 | 0.32 |
| Variant chosen by period for 25% of tokens (P6) | 0.74 | 0.47 | 0.26 |
| Variant chosen by period for 50% of tokens (P6) | 1.00 | 0.99 | 0.71 |
| Top third longer by 0.3 signs (P7) | 0.31 | 0.24 | 0.12 |
| Top third longer by 0.5 signs (P7) | 0.52 | 0.40 | 0.22 |
| Top third longer by 0.8 signs (P7) | 0.85 | 0.76 | 0.45 |

The divergence column is the Jensen–Shannon divergence of opening signs between the bottom and top thirds minus its permutation mean; the Harappa 3B–3C sign-frequency comparison had an excess of 0.033 bits on a different population ([CHRONOLOGY-REGION-01](../../knowledge/registry/attempts/CHRONOLOGY-REGION-01.json)). The test therefore detects an opening drift in which one legend in four takes a period-specific opening sign with probability 0.80 even after a quarter of the seals are displaced, and misses most drifts below one legend in six.

If Marshall's areas repeat the DK-G association exactly (Mackay's seals resampled with their own heights into Marshall-shaped strata), the pass rates are P4 0.46, P5 0.19, P6 0.61, P7 0.18, P9 0.79, and P8 0.27 with scores learned on one half of DK-G and tested on the other. These rates are upper bounds, since resampling treats the noise in Mackay's association as part of the effect.

On the discovery seals, per-sign mean heights are barely reliable. Over 200 random halvings, the correlation of per-sign mean heights between halves is 0.13 for signs in any position (Spearman–Brown 0.23), 0.25 for opening signs (over the few signs with four legends in each half) and −0.06 for closing signs; a height score learned on one half predicts the other half's heights at r = 0.065 for any position, 0.025 for openings and 0.003 for closings.
