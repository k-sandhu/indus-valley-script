# Discovery stage: Mackay's DK-G seals

Recorded 20 October 2026, before the freeze. Everything here is exploratory and was computed on Mackay's 1938 seals only. Exact values are in [discovery-v2/exploration.json](discovery-v2/exploration.json); [discovery-v1](discovery-v1/) is the first run, kept because the variant test changed population between the two runs (below).

## Population

Mackay's table gives a level for each seal in feet against the DK datum, a fixed point in his DK-G excavation. Of his 651 joined objects, 625 are seals from the DK area with a numeric level; three surface finds, the 11 SD-area seals (levels against a bench mark 2.2 ft above the datum) and the five from DK-H are left out of the discovery population. Levels run from −30.5 to +2.0 ft. The deepest levels are thinly sampled: 82 seals lie below −18 ft and five below −24 ft, because the lowest deposits at Mohenjo-daro lie under the present water table and were reached only in small deep soundings.

We work with height rank, not feet. Each seal gets u, its rank by level within its excavation area scaled to run from 0 at the deepest to 1 at the highest. The bottom third of the DK seals lies below −13.6 ft and the top third above −8.7 ft. A legend is used for a position only when it is complete, on one line and readable at that position; 439 legends of two or more signs qualify for the opening and closing positions, and 467 complete legends of any length for length. Identical complete legends found in the same area count once, at their median height.

## The closing stock does not move

The closing stock is the set of signs that close at least five Mackay legends and stand last in at least half of their occurrences: 740, 520, 090, 400, 151, 156, 527, 617, 621, 226, 892 and 407. These twelve signs close 73% of legends in the bottom third, 75% in the middle third and 72% in the top third. Sign 740 alone closes 38%, 39% and 43%. The 61 legends below −18 ft close with the same signs (740 21 times, then 390, 151, 400, 156, 520, 621 and 090), and 74% of them end in the stock. The 25 two-sign endings that close at least four legends, which we call the closing formulae, end 36%, 34% and 42% of legends by third.

Whether the closing sign carries information about height was measured with a rank analysis of variance: the spread of mean height between groups of legends with different closing signs, divided by the spread expected when heights are shuffled among the legends. Grouping signs with at least 3, 5 or 8 closings gives z = 1.20, −1.05 and −0.70 (p = 0.12, 0.86, 0.74). Closing signs carry no height information in DK-G.

## Opening signs, variants and length barely move

The same test on opening signs gives z = −0.09, 0.42 and 0.79 (p = 0.51, 0.31, 0.20), and ranking within the north and south parts of DK-G gives z = −1.23. Opening-sign richness at an equal sample of 138 legends is 77, 83 and 80 from bottom to top third. Per-sign mean heights do not replicate: a height score learned for each opening sign on a random half of the legends predicts the other half's heights at r = 0.025 on average over 200 splits (0.065 standard deviation), and closing-sign scores at r = 0.003. Signs in any position do slightly better, r = 0.065, positive in 90% of splits, and the overall sign inventory associates with height at z = 1.59 (p = 0.066). The signs sitting lowest are 156, 892, 151, 031, 003 and 861; the highest are 806, 900, 798, 032, 692, 760 and 017.

Variant choice was tested on Wells codes that the Mayig crosswalk assigns to exactly one Mayig class, in classes where at least two codes each occur three or more times (12 classes, among them 817 and 861, 803 and 806, 705 and 706, 390 and 405–407). The summed between-variant statistic gives p = 0.129 over all readable legends. In the first run the test used complete legends only and gave p = 0.47 (discovery-v1); we chose the population of all readable legends for the frozen test because a damaged legend still shows which variant was cut, and we record that the choice was made after seeing both values.

Mean legend length is 4.77, 4.76 and 5.06 signs by third; the within-area rank correlation with height is 0.056 (one-sided p = 0.11), 0.055 when ranked within the north and south parts.

## What did move: the seal format

Rectangular seals make up 10%, 15% and 20% of the seals by third, a correlation of 0.118 with height (p = 0.002). The single formula 760-740 also rises (3, 7 and 13 legends by third).

## Reading of the discovery stage

DK-G supports the first half of the claim strongly and the second half weakly. The closing stock was in place in the lowest seals Mackay recovered and its share did not change over some 30 ft of deposit. Opening signs show no drift at all; variant choice, legend length and the overall inventory move in the predicted direction at p between 0.07 and 0.13. The format of the seal moved more clearly than anything written on it. We therefore lowered the card's credence from 0.35 to 0.20 before freezing, kept the claim as stated, and froze predictions that can kill its drift half as well as confirm its fixity half.

## Rehearsal of the frozen scorer

The frozen scorer run on Mackay's own seals ([exploration.json](discovery-v2/exploration.json), `rehearsal_in_sample`) passes P1 (closing-stock difference −0.013, 90% interval −0.100 to 0.073), P2 (bottom-third share 0.73) and P3 (formula difference 0.055, interval −0.041 to 0.152), which were defined on these seals, and fails P4 (p = 0.31), P5 (p = 0.15), P6 (p = 0.13) and P7 (p = 0.11). P8 is circular in-sample (r = 0.40); cross-fitted on two halves it gives r = 0.050 and 0.043 (p = 0.24, 0.25). The auxiliary P9 passes (p = 0.002).
