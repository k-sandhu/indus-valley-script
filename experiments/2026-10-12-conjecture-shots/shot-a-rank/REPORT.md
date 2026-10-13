# Shot A: an upper grade of Indus seal written in face size and closing sign

13 October 2026. Frozen confirmation result of the two-stage shot described in [README.md](README.md); predictions in [PREDICTIONS.md](PREDICTIONS.md), outcome in [confirmation/results.json](confirmation/results.json).

## Result

On the confirmation half, seals whose legend ends in sign 001, 595, 679 or 820 are larger than seals of the same type, site class and text length. The 11 such seals have a mean residual of +0.346 in log face area, against −0.007 for the other 571, a difference of 0.353 (face area × 1.42) with p = 0.021 under a permutation of last signs within type × site × length cells (P4, `P4.difference`, `P4.p_one_sided`). Last signs as a whole carry size information beyond type, site and length: the between-sign sum of squares of residual size is 1.81 times its null mean, p = 0.0074 (P1a).

The other four scored predictions failed. The frozen grade order of the 28-sign closing lexicon correlates with confirmation size at r = 0.117 but does not clear rearrangements of the same scores among signs of similar frequency (p = 0.060, P1b). Closing signs do not explain more size than opening signs (P1c, p = 0.32). Seals with identical legends are not significantly closer in size than matched seals (P2, p = 0.10). The site prediction reversed: closing formulae, not opening signs, are the site-specific end of the legend on this half (P3, p = 0.98). The auxiliary prediction that unicorn seals coded `Bull1:W` are larger passed (P5, p = 0.0001).

The kill condition, P4 and P1a both failing, was not met. Under the frozen credence rules the conjecture [C-0001](../../../knowledge/conjectures/C-0001-rank-written-twice.md) moves from 0.12 to 0.21, status strengthened. An independent recomputation with separate code and a different random generator agreed on P1a, P4 and the kill decision ([verification.json](verification.json)).

| ID | Prediction | Statistic on the confirmation half | p | Result |
|---|---|---|---:|---|
| P1a | Last signs carry size beyond type, site and length | Between-sign ratio 1.81 (29 signs with at least 3 seals, 502 seals) | 0.0074 | pass |
| P1b | The frozen grade order of last signs reappears | r = 0.117 over 481 scored seals; rearrangement mean 0.022, SD 0.060, z = 1.56 | 0.060 | fail |
| P1c | Last signs explain more size than first signs | Ratios 1.81 and 1.66, difference 0.15 | 0.32 | fail |
| P2 | Identical legends are closer in size than matched seals | 23 legends, 61 usable pairs: mean absolute difference in log area 0.445 against 0.512 | 0.10 | fail |
| P3 | First signs are more site-specific than closing formulae | z(MI) −0.16 for first signs, 2.72 for closing formulae; difference −2.89 | 0.98 | fail, reversed |
| P4 | Legends ending in 001, 595, 679 or 820 sit on larger seals | 11 seals, +0.346 against −0.007; difference 0.353 | 0.021 | pass |
| P5 | Unicorn seals coded `Bull1:W` are larger (auxiliary, no credence effect) | 137 W seals +0.268 against 240 others −0.103; difference 0.371 | 0.0001 | pass |

The seal-level permutation for the P1b correlation, reported beside the frozen test, gives p = 0.025; the frozen rule uses the rearrangement null, so P1b fails.

## Population and method

The confirmation half of the shared split supplied 620 seals in 582 components: square or rectangular seals with both face dimensions, preservation complete, slightly chipped or chipped, and a complete single-line legend of at least two signs without unknown signs, one face per object family. Each component contributed one seal except in P2, which compares all seals sharing a legend. Size is ln(horizontal mm) + ln(vertical mm). Residual size subtracts a least-squares fit with seal type, site class (six named sites and other) and text length class (2 to 8, 9 or more), which explains 32.3% of the variance on this half and leaves a residual standard deviation of 0.491. Every null used 9,999 permutations or draws, labels moved only within type × site × length cells (560 seals movable), and every test was one-sided at p < 0.05. P3 used the 650 seals with a clean legend and a named site, without the size requirement, and shuffled site labels within seal type.

The grade lexicon was frozen as [discovery/lexicon.json](discovery/lexicon.json). Its hash, the prediction file's and the scoring code's are in [PREDICTIONS.sha256](PREDICTIONS.sha256), written at 04:00:09 UTC on 13 October; `confirm.py` checked the lexicon hash and read the half at 04:00:13 UTC. Four reads are logged in `confirmation-access.jsonl`: the scored run, a verification attempt that failed on serialisation after reading, the verification, and the exploratory breakdown.

The coordinator reviewed the draft predictions on 13 October 2026, after Shot B had read the same confirmation half, and changed nothing ([coordinator amendment](../AMENDMENT-2026-10-13-coordinator.md)). This shot's agent did not see Shot B's directory or outcome. The confirmation half's earlier corpus-wide uses, listed in the shot design, include the relation between seal area and text length, which the base model reproduces; the high-set contrast, the lexicon calibration and the unicorn-variant contrast had not been computed on it before.

## Verification

[verify.py](verify.py) rebuilt the population, the residual model and the P1a and P4 statistics without importing `confirm.py`, `rank_lib.py` or `seal_table.py`, and drew its permutations from Python's `random.Random` with seed 777 instead of NumPy's generator with seed 20261013. The population counts (620 seals, 582 components, 11 high-set seals), the residual standard deviation and both observed statistics agree to within 10⁻⁹. The P1a ratio is 1.805 against 1.808 (tolerance 2%), and the p values are 0.0060 against 0.0074 for P1a and 0.0220 against 0.0209 for P4, inside tolerances of 0.0048 and 0.0081 (four Monte Carlo standard errors of a difference of two estimates). Both verdicts and the kill decision agree.

## Adversarial review

An independent [review](../review/REVIEW.md), run after both halves were opened, confirmed that the freeze was clean and that the confirmation half could not have informed the choice of the four signs. It found that the P4 pass depends on three seals ending in 820: dropping M-6, M-16 or M-649 alone gives p = 0.138, 0.071 or 0.066, a rank version of the test gives p = 0.087 to 0.093, and without 820 the other six seals give +0.122, p = 0.40. M-649 is catalogued as silver and M-6 has the fourth-largest face of 582 confirmation seals. The pass survives complete seals only, other size measures and length controls, Mohenjo-daro only, and added covariates for excavation area, period and animal. Measured against the null mean of +0.056, the matched excess is 0.297 in log area, face area × 1.35. P1a's signal comes mostly from signs outside the four-sign set, and first signs carry as much size information as last signs on this half (ratio 1.67, p = 0.002). A Holm correction over the six scored predictions keeps P1a and drops P4. The review's analyses are exploratory and leave the frozen verdict unchanged. Following the review, the conjecture card keeps 0.21 as the value under the frozen credence rules and records a review credence of 0.13.

## What the result means for the conjecture

The claim's central sentence survived its one shot: legends closing in the four signs sit on larger seals in a half of the corpus that played no part in choosing them. The effect is about half its discovery size (0.35 against 0.68 in log area), close to the +0.36 that the split-half rehearsal predicted for held-out seals ([power-split.json](discovery/power-split.json), `pooled_test_half_mean_residual`). The wider claim did worse. The grade order of the whole lexicon fell just short of its calibration test, closing signs did not out-predict opening signs, and the locality sentence failed in the opposite direction. On the discovery half the same locality statistic had pointed the other way (first-sign z 2.54, closing-formula z 0.88; [site-specificity.json](discovery/site-specificity.json)), so site specificity at the two ends of the legend is not stable between halves.

The exploratory breakdown written after the outcome ([amendment](AMENDMENT-2026-10-13-post-outcome.md)) adds that the P4 pass rests mainly on 820, whose five confirmation seals average +0.62 (M-6 at 58.4 mm, M-16 at 41.9 mm and M-649 at 38.3 mm among them), while the four seals ending in 679 average −0.08. Closing signs outside the set also carry size on this half (ratio 1.62, p = 0.027), so the sentence saying no other closing sign marks size does not hold here. P1a, P1b and P4 share the same few seals, so the passes of P1a and P4 count as one confirmation of one pattern.

## The boldest reading and the test that decides it

The boldest reading the two halves support is that a legend closing in sign 820 marked the holder of an upper grade, whose seal was cut larger. Across both halves the ten seals ending in 820 average about +0.64 in residual log area, close to twice the expected face area. Six of the ten rank in the top 25 residuals of their half; the others rank 80th, 262nd, 441st (the Dholavira seal) and 563rd, so the pattern is a few very large seals rather than a uniform shift. This reading was narrowed to 820 after the outcome and has no confirmation of its own.

Two rivals remain. The first is layout: a large face leaves room at the end of the text band, and an extra final sign there may mean nothing about grade. The second is direction. In the full export, sign 820 opens 99 complete single-line seal legends and closes 12; all 12 closing cases carry the catalogue's standard right-to-left code, so a mis-coded direction field is not the explanation, but a legend misread in the catalogue itself would also put an opening 820 at the end (coordinator's check after the outcome, run on the normalized export).

Photographs decide between the reading and both rivals. The 29 seals in both halves whose legends end in the set should show the closing sign inside the text band at normal size and spacing, as on H-1 and M-1, and a reading direction consistent with the rest of the legend. A sign squeezed into leftover space, set apart in the field, or a legend that reads correctly only from the other end would favour layout or direction. Seals outside this export, in later excavation reports or a new concordance, should show at least two thirds of complete seals ending in 820 larger than the median seal of their site, type and length, judged once ten such seals are available. These are prospective predictions 2 and 3 of [PREDICTIONS.md](PREDICTIONS.md), narrowed to 820.

## Files

[README.md](README.md), [EXPLORATION.md](EXPLORATION.md), [PREDICTIONS.md](PREDICTIONS.md), [PREDICTIONS.sha256](PREDICTIONS.sha256), [confirmation/results.json](confirmation/results.json), [verification.json](verification.json), [AMENDMENT-2026-10-13-post-outcome.md](AMENDMENT-2026-10-13-post-outcome.md), [confirmation/post-outcome-exploratory.json](confirmation/post-outcome-exploratory.json), [RETROSPECTIVE.md](RETROSPECTIVE.md), [registry-entry.json](registry-entry.json) and `confirmation-access.jsonl`.
