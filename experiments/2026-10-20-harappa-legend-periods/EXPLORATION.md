# Exploration: discovery seals and the undated pool

Computed 20 October 2026 on the 109 discovery families and on the 253 Harappa seals outside the confirmation population, before the predictions were frozen. No Mound F stratified legend was read. Outputs: [discovery-v1/exploration.json](discovery-v1/exploration.json), [design-v1/](design-v1/), [discovery-v2/rehearsal/rehearsal.json](discovery-v2/rehearsal/rehearsal.json), [discovery-v2/reliability.json](discovery-v2/reliability.json).

## The discovery sequence

Ninety-nine discovery seals sit in frames of five or more: Vats's Mound AB (46 seals, Strata VII to I, which the export maps to 3B-2 through Period 4), HARP's Mound E (18 seals, 3A to 3C), HARP's Mound F (10 seals, 3B to 3C), Vats's Mound D (8), Area J (6) and Area H (5 with strata, 6 with an export period of 4 or 5); four HARP seals without a mound and two each from HARP's Mound AB and Vats's Area G fall in frames too small to use. Each frame has its own clock, so u is ranked within the frame. The population is small and spread over seven frames; it can show the direction of an effect and exercise the code, and its tests have little power.

## Closing stock

Mackay's DK-G stock of twelve signs closes 61.0% of the 195 pool legends of two or more signs whose closing is read: 65% on square seals and 52% on rectangular ones. Harappa closes with signs that DK-G does not use as closers: the pool rule (at least five closings, at least half of the sign's occurrences final) gives 740, 520, 405, 154, 090, 151, 407 and 595, and 405, 154 and 595 are absent from the DK-G stock. Sign 740 alone closes 39.5% of pool legends. The union of the two stocks, fifteen signs, closes 72.8% in sample and 69.6% when its Harappa part is derived on half of the pool and measured on the other half. We froze the union, so that the test measures the stock in use at Harappa while keeping the twelve signs that were fixed through Mohenjo-daro's sequence; the DK-G stock alone is a reported sensitivity analysis.

Through the discovery sequence the closing stock does not move. By third of the period rank the DK-G stock closes 0.61, 0.61 and 0.55 of legends (28, 31 and 22 legends; late minus early −0.06, p = 0.69), the Harappa stock 0.68, 0.68 and 0.73 (+0.05, p = 0.81), and the frozen union 0.71 in the early third and 0.73 in the late third (+0.01, 90% interval −0.20 to 0.21). Sign 740 closes 0.36, 0.39 and 0.50 (p = 0.47). Within Mound AB, the largest discovery frame, the DK-G stock closes 0.75 of 16 legends in the earlier half and 0.45 of 20 in the later half; in HARP's Mound E it goes the other way, 0.40 of 5 and 0.70 of 10.

## Drift

No part of the legend carries period information in the discovery seals. Opening signs give p = 0.55 when a sign needs five legends to form its own category (three categories) and p = 0.090 at three legends (nine categories); closing signs give p = 0.58 and 0.47. Mean length is 4.3, 5.1 and 4.7 signs by third (within-frame rank correlation 0.08, two-sided p = 0.51). The sign inventory (signs in at least eight legends) gives p = 0.52 on complete legends and 0.82 on all legends. Variant choice, measurable in two Mayig classes (P086 and P385), gives p = 0.087.

## Seal form

Rectangular seals make up 0.09, 0.32 and 0.29 of the seals by third (r = 0.21, one-sided p = 0.015), and seals with script alone 0.15, 0.39 and 0.29 (p = 0.075). Every rectangular discovery seal has script alone, and four of 80 square seals do. Within frames the rise holds in Mound AB (3 of 19 seals in the earlier half, 8 of 27 in the later half), Mound E (0 of 6, 4 of 12) and HARP's Mound F (0 of 3, 3 of 7). Seal form is the change the positive control will look for in Mound F; the boss and cross-section fields of the export follow the format and add no independent control.

## Rehearsal of the frozen scorer

Run on the discovery seals with the frozen parameters ([rehearsal.json](discovery-v2/rehearsal/rehearsal.json)), the scorer gives P1 inconclusive (late minus early +0.013, 90% interval −0.196 to 0.214, inside the margin of 0.25, but two of ten single deletions push the upper end to 0.250 and 0.253), P2 pass (early share 0.714), "no drift" for opening signs (p = 0.56), length (p = 0.51), inventory (p = 0.82) and closing signs (p = 0.59), "inconclusive" for variants (p = 0.084), and a passing positive control (p = 0.015). Under the joint rule this would move the credence from 0.40 to 0.51. The rehearsal is in sample and is not evidence for the conjecture.

## Reliability

Per-sign period means barely replicate across random halves of the discovery seals. For signs in any position, the correlation of per-sign mean u between halves is 0.11 (Spearman–Brown 0.20), and a score learned on one half predicts the other half's u at r = −0.02. Opening and closing signs never reach three legends in both halves for four signs. A shrunken opening-sign score transfers at r = 0.19 on average (SD 0.19, positive in 85% of halvings), and a closing-sign score at r = −0.06. At Mohenjo-daro the same measures were 0.13 for any position and 0.25 for opening signs ([stratigraphy exploration](../2026-10-20-mohenjo-daro-stratigraphy/discovery-v2/exploration.json)). The opening-sign transfer is the one hint of period information in the discovery legends, and it is the drift that P3 tests.

## Choices made on synthetic data

The quick power pass ([design-v1/power-quick.json](design-v1/power-quick.json)) filled populations of Mound F's shape with pool legends. A sign needs five legends to form its own opening or closing category (false-positive rates 0.03 to 0.05; power 0.61 to 0.66 against a period-specific opening in one legend of four), and the inventory uses signs in at least eight legends (power 0.58 to 0.63 against a period-specific interior sign in one legend of two, against 0.47 to 0.49 at six). Under true fixity the late-minus-early difference in the closing-stock share has a standard deviation of 0.11 across populations, so the equivalence margin was set at 0.25, which passes 54% of fixed populations, 32% with a true shift of 0.10, 11% with 0.20 and 1% with 0.30. The first fail rule, a 95% bootstrap interval excluding zero, failed 7.7% of fixed populations; the frozen rule uses a within-frame permutation test instead. The early-third share threshold of P2 is 0.55, below the 5% quantile (0.59) of the early share in fixed populations.

## Credence before the freeze

The card opened at 0.35 as the successor reading of the Mohenjo-daro report. The discovery seals show no drift in any part of the legend, a closing stock that holds its share and a seal form that changes, all at low power. We raised the credence to 0.40 before freezing.
