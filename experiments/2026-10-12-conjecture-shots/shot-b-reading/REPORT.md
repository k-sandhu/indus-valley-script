# Shot B result: the working reading does not predict the objects

The gloss map of [C-0002](../../../knowledge/conjectures/C-0002-working-reading.md) failed its frozen primary test on the confirmation half. The primary score is the sum of the standardised site-concentration contrast (P1) and the standardised size contrast (P2). It came out at S = −0.567, at the 33.0th percentile of 10,000 rearrangements of the map's own labels within frequency and position bands. The pass threshold was the 95th percentile, S = 2.073. S stands 0.44 standard deviations below the rearrangement mean, with z₁ = −1.20 and z₂ = +0.63. Because the distance is below zero, the frozen kill condition is met and the conjecture is recorded dead at credence 0.02. None of the three individual predictions and none of the three secondary checks passed. An independent recomputation reproduces T₂ exactly, T₁ to 0.0004, and S, z₁, z₂ and the fail decision within Monte Carlo error ([verification.json](verification.json)).

The predictions were frozen in [PREDICTIONS.md](PREDICTIONS.md) before the confirmation half was read. Its SHA-256 (`c864fea5…312a04`) is recorded with the hashes of the map and the scoring script in [PREDICTIONS.sha256](PREDICTIONS.sha256), written at 03:48:20 UTC on 13 October 2026. `confirm.py` read the confirmation half once, at 03:48:28 UTC, and `verify.py` read it a second time at 03:49:21 UTC ([confirmation-access.jsonl](confirmation-access.jsonl)). The frozen output is [confirmation/results.json](confirmation/results.json), fields `primary`, `components`, `secondary` and `verdict`. At the coordinator's review before freezing, the primary score was reduced from five components to P1 and P2, with the other three kept as individual predictions; the reason is recorded in PREDICTIONS.md.

## Population

The confirmation half holds 2,870 faces in 2,346 object families, 1,134 of them seals. Merging families within their split components gives 1,086 seal site units (Mohenjo-daro 59.3%, Harappa 19.4%, Dholavira 6.5%, Lothal 4.1%, Chanhu-daro and Kalibangan 2.6% each, other sites 5.4%), 846 seal size units with a residual standard deviation of 0.736 log₂ units after subtype and text length, 784 square-seal units with a recorded animal (unicorn share 0.751), 855 units at Harappa or Mohenjo-daro (Harappa share 0.247) and 475 units with a recorded period. Eligible signs number 89 for site, 86 for size, 77 for the unicorn, 91 for the Harappa share and 57 for period.

## Primary test

| Score | S | 95th percentile | Percentile of S | One-sided p | Distance (SD) | Result |
|---|---:|---:|---:|---:|---:|---|
| S = z₁ + z₂ (frozen) | −0.567 | 2.073 | 33.0 | 0.670 | −0.44 | fail; kill condition met |
| Numerals held fixed | −0.356 | 1.924 | 37.9 | 0.622 | −0.30 | fail |
| Five-component sum (reference) | −1.023 | 3.794 | 33.1 | 0.669 | −0.45 | no pass rule |

The test detects large effects only. On the discovery half with synthetic withheld fields that plant a site lean for name signs and 25% larger linear dimensions for official legends (1.56 times the face area), the same procedure gives z₁ = 1.06, z₂ = 3.56 and S at 3.13 standard deviations, a pass ([synthetic_dryrun_planted.json](discovery/synthetic_dryrun_planted.json)). The [adversarial review](../review/REVIEW.md) planted size effects in the real discovery data: 1.2 times the face area on legends with an official sign fails (94.75th percentile), and 1.5 times is needed to pass. Per-sign site concentration is not reproducible between the halves (r = −0.092 across 83 signs), so P1 can detect only very large effects. Run on the discovery half with its real withheld fields, which this shot never loaded, the frozen code gives S = 1.256, +0.88 standard deviations, at the 80th percentile: also a fail, without meeting the kill condition.

## Individual predictions

| ID | Contrast | Eligible signs | T | Rearrangement mean (SD) | z | One-sided p | Result |
|---|---|---|---:|---:|---:|---:|---|
| P1 | site concentration, local minus pan | 52 / 37 | −0.0259 | −0.0042 (0.0182) | −1.20 | 0.875 | opposite direction |
| P2 | size residual, official minus other | 19 / 67 | +0.0536 | +0.0249 (0.0457) | +0.63 | 0.268 | predicted direction, weak |
| P3 | unicorn excess, official minus name | 18 / 18 | −0.0442 | +0.0050 (0.0373) | −1.32 | 0.898 | fail |
| P4 | Harappa excess, stock H minus MD | 6 / 4 | +0.1087 | −0.0146 (0.0894) | +1.38 | 0.082 | fail |
| P5 | period concentration, name minus pan | 12 / 29 | −0.0244 | −0.0074 (0.0331) | −0.51 | 0.690 | fail |

## Secondary checks

| ID | Prediction | Data | Result |
|---|---|---|---|
| S1 | commodity signs less often on steatite than their object type predicts | 1,714 components | T = 0.0138 against a null mean of 0.0047 (SD 0.0055), p = 0.051; fail, in the predicted direction |
| S2 | seals ending 740-400 larger than seals ending 740-090 | 5 against 21 components | mean size residuals −1.133 against −0.016, p = 0.999; fail, reversed |
| S3 | stroke count before a final sheaf rises with seal size | 29 components | ρ = −0.19, two-sided p = 0.33; fail |

## What the result means for the reading

The reading made two claims about objects that follow directly from its classes. The first, that names and commodities belong to one city while households, offices, links and numerals are shared, is contradicted: the signs the map calls local are less site-concentrated than its shared vocabulary, by 1.2 standard deviations of the rearrangements. The second, that legends of office are cut on larger seals, points the right way and cannot be told apart from a rearranged map. Official signs are found on unicorn seals less often than name signs, the period contrast is null, and only the city-vocabulary prediction P4 came near its threshold.

The class structure built from sign position, neighbours and pictures therefore carries no detectable information about a seal's site, size, animal or date beyond what frequency and position already carry. The grammar as a description of how the discovery texts are built, with openers, name cores and closing phrases, is not what failed. What failed is the claim that those units are households, personal names and offices of a kind that leaves a trace on the objects. The review adds the scope of that failure: this map fails this test on both halves (−0.44 and +0.88 standard deviations), and the test cannot show that the grammar, the individual glosses or a class structure built another way are wrong.

The [exploratory amendment](AMENDMENT-2026-10-12-exploratory.md), computed after the outcome from the frozen results, shows where the locality claim went wrong. The name stock, fish signs included, is the most evenly spread vocabulary (class mean of the bias-corrected site-concentration effect 0.000), while determinatives (0.102), titles (0.044) and the numeral form 013 (0.474) are the most site-concentrated. The opener signs are not concentrated by site, and their large size residual comes from sign 692 alone. The period field mixes two numbering systems, 2–5 and Early/Intermediate/Late, so P5 partly measures site.

## The boldest reading the result supports

The result reverses the reading's locality. The name stock, with the fish signs as pan-Indus name or deity elements as Parpola's star reading implies, was shared across the cities, and what differed from city to city was the closing vocabulary of offices and determinatives, together with local ways of writing numerals. That pattern fits a script whose personal and divine names drew on one civilisation-wide stock while each city's administration wrote its own titles.

The adversarial review found no support for this reading. On the half where it was found, title and determinative signs against name signs give z = 1.67 (p = 0.057) under the shot's own within-band null; without Mohenjo-daro the value falls to 1.09, and on the discovery half the pattern reverses (z = −1.02; without Mohenjo-daro −0.61). The most concentrated confirmation signs, 013, 621 and 923, are not concentrated on the discovery half. The pattern and Shot A's reversed site prediction are one observation, closing formulae concentrated at Mohenjo-daro on the same confirmation seals, and the working model leaves it out. The confirmation half cannot test this reading in any case, because it was formed after the outcome. The discovery half's site field was never read by this shot, but Shot A explored it, so a test there would not be fresh for the project. The decisive test is prospective: on texts none of these analyses has seen, such as the expanded concordance planned by the Iravatham Mahadevan chair or newly published seals, freeze the P1 statistic with its direction reversed (TITLE and DET signs against NAME signs, same within-band null, one-sided p below 0.05) before reading their sites.
