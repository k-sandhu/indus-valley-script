# Amendment, 13 October 2026: post-outcome breakdowns (exploratory)

Status: **Exploratory, post-outcome.** Written after [confirmation/results.json](confirmation/results.json) existed. The frozen verdicts in that file are the shot's result; nothing here changes them. The breakdowns come from the frozen output's own fields and from [post_outcome.py](post_outcome.py), which wrote [post-outcome-exploratory.json](confirmation/post-outcome-exploratory.json). Each of these reads of the confirmation half is logged in `confirmation-access.jsonl`.

## Which high-set signs carried P4

Eleven confirmation seals end in the high set (`P4.seals` in the results). Five end in 820, with residuals +1.74 (M-6, 58.4 mm), +1.08 (M-16, 41.9 mm), +1.08 (M-649, 38.3 mm), +0.05 and −0.87 (M-998, 15.5 mm); their mean is +0.62. Four end in 679, at +0.22, −0.15, −0.08 and −0.31; three of the four are rectangular seals, and their mean is −0.08. One ends in 001 (H-642, +0.62) and one in 595 (H-645, +0.43), both rectangular seals from Harappa. The P4 pass therefore rests mainly on 820, with single supporting seals for 001 and 595, while 679 did not repeat its discovery behaviour.

## Where P1a's signal came from

The confirmation last-sign signal (ratio 1.81) is not the discovery lexicon's. The four largest contributions to the between-sign sum of squares are 220 (+0.74 on 5 seals, discovery score +0.02), 400 (−0.38 on 16 seals, discovery score −0.12), 820 (+0.62 on 5 seals) and 368 (+0.27 on 11 seals, discovery score −0.06) (`last_sign_units`). The ten signs scored −0.10 or lower in discovery average −0.07 on 62 confirmation seals (`discovery_low_scored_last_signs`). Without the high set, last signs still give ratio 1.62 (p = 0.027, the frozen output's `reported.last_sign_without_high_set`), so on this half closing signs other than the four carry size information, against the claim's sentence that no other closing sign does. First signs give ratio 1.66 (p = 0.0015, `reported.first_between_unit`), led by first signs with three to five seals that were absent from the discovery lexicon (017, 632, 495, 921). The statistic at a minimum of three seals per sign responds to a few rare signs on unusual seals in either position, which is why P1c found no difference between closing and opening.

## The reversed site result

P3 failed in the opposite direction to the prediction: closing formulae are site-specific on this half (z = 2.72) and first signs are not (z = −0.16); last signs alone give z = 3.79 (`reported.site_specificity_first_vs_last`). The formulae with the largest contributions to the mutual information are concentrated at Mohenjo-daro beyond its 63% share of the population: 390 (20 of 31 seals), 527 (9 of 12), 923-740 (9 of 10), 226 (8 of 10) and 520 (45 of 62) (`closing_formula_site_profiles`). On the discovery half the order was the reverse (first signs z = 2.54, closing formulae 0.88). The two halves disagree, so neither supports a stable difference in locality between the two ends of the legend.

## Consequences for a revised claim

Three sentences of the frozen claim did not hold on the confirmation half: openings are not more local than closings, closing signs outside the high set do carry size here, and 679 did not mark larger seals. A narrower claim consistent with both halves is that a legend closing in 820 marks a larger seal (discovery: 5 seals, mean residual +0.67; confirmation: 5 seals, +0.62). This claim was formed after seeing the outcome and needs new material: the prospective predictions in [PREDICTIONS.md](PREDICTIONS.md), restricted to 820, are its test.
