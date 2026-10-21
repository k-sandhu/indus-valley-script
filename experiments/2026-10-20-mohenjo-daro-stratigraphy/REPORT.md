# Seal legends and stratigraphic height at Mohenjo-daro

Package `2026-10-20-mohenjo-daro-stratigraphy`, 20 October 2026. Conjecture [C-0006](../../knowledge/conjectures/C-0006-closing-stock-fixed-from-lowest-levels.md). Status: **frozen evaluation**, one confirmation read; the post-outcome description at the end is exploratory.

The closing stock of Mohenjo-daro seal legends does not change with height. In Marshall's 1931 areas, the twelve closing signs chosen on Mackay's DK-G seals close 73.1% of the legends in the bottom thirds of the excavated sections and 72.5% in the top thirds (difference −0.006, 90% interval −0.105 to 0.096). The bottom-third share is the same as in DK-G, 73.2%. Nothing at the front of the legend moves either: opening signs (p = 0.17), the contrast between opening and closing signs (p = 0.61), variant choice (p = 0.097) and legend length (p = 0.38) all fail. C-0006 claimed that the front of the legend drifted while the closing stock stayed fixed. With no drift found, its frozen rule kills it, and its credence falls from 0.20 to 0.02.

## Design

The excavators measured height differently, so we split by excavator ([PROTOCOL.md](PROTOCOL.md)). Mackay printed each seal's level against the DK datum, a fixed point in DK-G; his 625 DK-area seals were the discovery population. Marshall printed depth below the modern surface; every seal joined to his table with a numeric depth was the confirmation population, ranked within the excavated section where it was found. No earlier package had related legends to depth at Mohenjo-daro, and the statistic family `stratigraphic_level` appears nowhere in `bench/spent.json`, which lists `seal_size`, `site` and `motif` for the full corpus and, since the fish-context package of the same day, several fish and object-type families.

A seal's height enters every statistic as u, its rank within its stratum scaled from 0 at the deepest to 1 at the highest. Nulls permute u among legends within strata, so each test asks whether legends found deeper in the same section differ from those found higher. Residual seals (older than their layer) can only blur a drift, and intrusive seals can put a late legend low; the bottom-of-sequence predictions are therefore shares over the bottom third that must survive single deletions, and power is stated after a quarter and a half of the seals in each stratum exchange heights at random. The water table limits the deepest digging, so "lowest levels" means the bottom of each excavated sequence: in DK-G that is below −13.6 ft against the datum, and in Marshall's sections it is the deepest third of seals, found between 4 and 18 ft below the surface, half of them deeper than 6 ft.

## Discovery

On Mackay's seals the closing stock stood at 73%, 75% and 72% of legends by third of height, and even the 61 legends below −18 ft closed in it at 74%. The drift half was weak: opening signs carried no height information (z = 0.42), and variant choice (p = 0.13), length (p = 0.11) and the overall sign inventory (p = 0.066) moved without reaching p = 0.05. The clearest change was the seal format, with rectangular seals rising from 10% to 20% of seals between the bottom and top thirds (p = 0.002). We lowered the credence from 0.35 to 0.20 before freezing and kept the claim as stated. Details are in [EXPLORATION.md](EXPLORATION.md) and [discovery-v2/exploration.json](discovery-v2/exploration.json).

## Freeze

The predictions were registered with the bench shots loader on a split of the Marshall file alone, with a package ledger copied from `bench/spent.json`, and frozen at 00:44:49 UTC on 21 October (20:44 local time on 20 October). The freeze hashed [PREDICTIONS.json](PREDICTIONS.json) (`e4b6f43c…`) and, as artifacts, [PREDICTIONS.md](PREDICTIONS.md), [PROTOCOL.md](PROTOCOL.md), [score.py](score.py), [strat_stats.py](strat_stats.py), [confirm.py](confirm.py), [build_inputs.py](build_inputs.py), the [frozen parameters](discovery-v2/frozen-parameters.json) and the Mayig crosswalk ([bench/shots-freeze.json](bench/shots-freeze.json)). [confirm.py](confirm.py) read the loader's confirmation half (246 rows) and then its other half (237 rows) at 00:45:07, 18 seconds after the freeze, pooled them and scored them once ([shots/round.access.jsonl](shots/round.access.jsonl)). The artifact hashes were unchanged after the run. No other shot shares this round. The fish-context package read its own confirmation half of the full corpus at 00:20 UTC for other statistic families; we did not read its results.

## Confirmation

The 483 Marshall rows give 434 seals with a depth in 15 strata: HR-B 72, VS-A 63, C/DK-C 51, HR without section 45, E/DK-E 44, HR-A 32, DK/DK-C 29, DK/DK-B 27, D 15, SD 14, B 10, VS remainder 10, L 9, HR remainder 7 and DM 6. Of these, 307 legends of two or more signs are readable at both ends, 329 are complete and 624 variant rows come from all readable legends. Results are in [confirmation-v1/results.json](confirmation-v1/results.json).

| ID | Prediction | Result | Outcome | Credence step |
|---|---|---|---|---|
| P1 | Closing-stock share equal in top and bottom thirds | −0.006, 90% interval −0.105 to 0.096; all ten single deletions stay inside ±0.20 | pass | +0.05 |
| P2 | At least 60% of bottom-third legends close in the stock | 0.731 (108 legends), 0.729 after the worst deletion | pass | +0.03 |
| P3 | Closing-formula share equal in top and bottom thirds | −0.057, interval −0.163 to 0.047; deletions stay inside | pass | +0.03 |
| P4 | Opening signs sit at different heights | statistic 19.96 against null mean 15.12, z = 0.91, p = 0.17 | fail | −0.06 |
| P5 | Opening signs carry more height information than closing signs | z(opening) 0.95, z(closing) 1.30, difference −0.35, p = 0.61 | fail | −0.04 |
| P6 | Variant choice changes with height | z = 1.39, p = 0.097, eight classes | fail | −0.04 |
| P7 | Legends grow longer upward | r = 0.018, p = 0.38 | fail | −0.03 |
| P8 | DK-G heights of non-final signs predict height (long shot) | r = 0.055, p = 0.16 | fail | −0.01 |
| P9 | Rectangular seals rise (auxiliary) | r = −0.003, p = 0.53 | fail | none |

The effects sum to 0.13, but P4, P5, P6 and P7 all failed, which is the kill condition. C-0006 is dead at 0.02 under the frozen rule. Holm-adjusted p-values across P4 to P8 run from 0.485 to 0.76. A separate script written after the read, which imports none of the package's modules ([verify_independent.py](verify_independent.py), [verification-v1/independent-check.json](verification-v1/independent-check.json)), reproduces the 434 seals in 15 strata, the 307 legends, the bottom and top shares (0.7315 and 0.7255) and the P4 statistic (19.955 over 16 categories, p = 0.167 with 1,999 draws).

Ranking by Marshall's area letters alone, the pre-declared sensitivity analysis, gives the same nine outcomes. Scored separately, the loader's two halves agree on the closing stock (P2 passes in both; P1 passes in one and is inconclusive in the other, whose interval is wider at half the size) and disagree on everything that might drift: length rises in one half (r = 0.16, p = 0.026) and falls in the other (r = −0.16), the rectangular share rises in one (p = 0.0495) and falls in the other, and variant choice passes in one (p = 0.017) and not the other (p = 0.55). The weak signals at the front of the legend reverse between random halves of the same population.

## What the power statement allows

Before the read we measured how often the tests detect planted effects in populations of Marshall's shape ([discovery-v2/power.json](discovery-v2/power.json)). A drift in which one legend in four takes a period-specific opening sign is detected by P4 with probability 0.98, and 0.80 after a quarter of the seals are displaced; a drift of one legend in six is detected with probability 0.56 and 0.39. Under true fixity P1 passes 91% of the time, and when the closing-stock share truly differs by 0.20 it passes 3.5% of the time. The fixity result is an equivalence the test had the power to establish: the closing-stock share at the bottom of Marshall's sections lies within about ten points of its share at the top. The drift result excludes moderate drifts and leaves small ones open.

One check limits the drift result further. The rectangular-seal rise, the clearest change in DK-G, does not repeat in Marshall's sections (P9). Either that rise was particular to DK-G, or Marshall's sections span too little time to show any change: the median seal of a bottom third lies 6 ft below the surface and the median seal of a top third 2.3 ft, a gap of under 4 ft, where DK-G's bottom and top thirds lie 10.9 ft apart (medians −17.35 and −6.5 ft against the datum). The second reading would leave the drift half untested rather than refuted. The kill stands under the frozen rule, and the evidence against the drift half is strongest for drifts of the size the power table names.

## Post-outcome description (exploratory)

Computed after the outcome ([post_outcome.py](post_outcome.py), [post-outcome-v1/summary.json](post-outcome-v1/summary.json)). By third of height from bottom to top, Marshall's legends close in the stock at 0.73, 0.65 and 0.73, end in 740 at 0.44, 0.38 and 0.46, end in a closing formula at 0.37, 0.32 and 0.31, and average 4.97, 4.63 and 5.23 signs; rectangular seals make up 0.18, 0.10 and 0.16. The bottom-third closings are 740 (48), 520 (10), 527 (8), 390 (7), 405 (4), 001, 407 (3 each) and 617 (2).

Combining the one-sided z-values of the two excavations by Stouffer's method gives p = 0.17 for opening signs, 0.14 for length and 0.036 for variant choice. The variant figure does not describe a shared drift. Within the classes measured in both excavations, 405 and 407 sit above 390 in DK-G and below it in Marshall's sections, 555 sits above 550 in DK-G and below it in Marshall's sections, and 706 sits with 705 in DK-G and well above it in Marshall's sections; only 154 over 156 and 806 over 803 point the same way in both. Each excavation shows some local association between variant and height, in different directions.

## Earlier work

The stability of the script through Mohenjo-daro's occupation is an old view. Marshall (1931, vol. I, pp. 40–41) saw no perceptible alteration in the sign forms, and Parpola (1994, p. 54) judged that the script changed little during the Mature Harappan period. Mythili R. Rao and Iravatham Mahadevan, "Archaeological Context of Indus Texts at Mohenjodaro" (*Journal of the Institute of Asian Studies*, pp. 25–38, presented in 1985), grouped Mackay's DK-G seal levels into Early, Middle and Late periods and found no significant variation in the relative frequencies of the frequent sign pairs. Our discovery stage repeats their population with different statistics; the confirmation extends the result to Marshall's sections under a frozen test, and separates the closing stock from the front of the legend. The rise of rectangular seals in DK-G was reported by Andreas Fuls (*Corpus of Indus Inscriptions I*, 2022, p. 13, as quoted in the [harappa.com review](https://www.harappa.com/content/corpus-indus-inscriptions-i)). Mackay (1938, vol. I, p. 325) warned that seals dropped into the holes left by brick-robbers cannot readily be dated by level, the intrusive case our protocol guards against. The main published case for change is J. Mark Kenoyer and Richard H. Meadow, "Inscribed Objects from Harappa Excavations 1986–2007" (CISI 3.1, 2010, pp. xliv–lviii), where seal forms change through Periods 3A to 3C and the authors expect the script to have changed with them. Full citations are in the card's `prior_proposals`.

## Files

Tracked: [PROTOCOL.md](PROTOCOL.md), [EXPLORATION.md](EXPLORATION.md), [PREDICTIONS.md](PREDICTIONS.md), [PREDICTIONS.json](PREDICTIONS.json) and [PREDICTIONS.sha256](PREDICTIONS.sha256), the scripts ([build_inputs.py](build_inputs.py), [strat_stats.py](strat_stats.py), [score.py](score.py), [explore_mackay.py](explore_mackay.py), [power.py](power.py), [confirm.py](confirm.py), [post_outcome.py](post_outcome.py)), [inputs/inputs-summary.json](inputs/inputs-summary.json), [discovery-v1/](discovery-v1/) and [discovery-v2/](discovery-v2/), [confirmation-v1/](confirmation-v1/) with its [stdout](confirmation-v1.stdout.json), [post-outcome-v1/](post-outcome-v1/), the independent check ([verify_independent.py](verify_independent.py), [verification-v1/](verification-v1/)), the loader state, access log and package ledger in [shots/](shots/), the bench envelopes in [bench/](bench/), [RETROSPECTIVE.md](RETROSPECTIVE.md), [DATA-UPDATE.md](DATA-UPDATE.md) and [registry-entry.json](registry-entry.json). Tracked outputs hold counts, statistics, sign codes and Lipi family identifiers; legends of individual objects stay local in `data/raw/2026-10-20-mohenjo-daro-stratigraphy/` (the two input files). Table values derive from Nitin Stephen Koshy's transcriptions of the Mackay and Marshall tables (https://github.com/epachayan/indus-script, commit `5c14a01`, CC BY 4.0).

Commands, from the repository root, in order:

```text
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/build_inputs.py
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/explore_mackay.py experiments/2026-10-20-mohenjo-daro-stratigraphy/discovery-v2
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/power.py experiments/2026-10-20-mohenjo-daro-stratigraphy/discovery-v2/frozen-parameters.json experiments/2026-10-20-mohenjo-daro-stratigraphy/discovery-v2/power.json
python -m bench shots --action create --input data/raw/2026-10-20-mohenjo-daro-stratigraphy/confirmation-marshall1931.jsonl --split experiments/2026-10-20-mohenjo-daro-stratigraphy/shots/round.json --ledger experiments/2026-10-20-mohenjo-daro-stratigraphy/shots/spent-ledger.json --seed 2026-10-20-mohenjo-daro-stratigraphy
python -m bench shots --action register ... --shot stratigraphy --predictions experiments/2026-10-20-mohenjo-daro-stratigraphy/PREDICTIONS.json
python -m bench shots --action freeze ... --shot stratigraphy --artifact ... (the eight artifacts above)
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/confirm.py experiments/2026-10-20-mohenjo-daro-stratigraphy/confirmation-v1
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/post_outcome.py experiments/2026-10-20-mohenjo-daro-stratigraphy/post-outcome-v1
```

Every script refuses an existing output directory. A rerun of the loader steps needs a new split path and a fresh ledger copy, since the recorded split is opened.

## Boldest reading and the test that would decide it

The results support a stronger claim than the one that died: Mohenjo-daro's seal legends were written to one fixed pattern for the whole excavated occupation. The same twelve closing signs end about three legends in four at the bottom of Mackay's 30 ft sequence and at the bottom of Marshall's sections taken together, and no part of the legend (opening sign, variant or length) changes in a way that repeats from one excavation to the other. The legend was a standard that was in place before the lowest seals the excavators reached and that the city kept as it rebuilt.

That reading predicts that wherever a sequence of seals spans a known and long stretch of time, the closing stock holds its share and the opening signs carry no period information. The test that would decide it is a frozen run of P1 to P5 on a sequence with an independent clock and a positive control: HARP's Harappa seals from Periods 3A to 3C within a single mound, where the 3B–3C sign-frequency difference of [CHRONOLOGY-REGION-01](../../knowledge/registry/attempts/CHRONOLOGY-REGION-01.json) shrank inside Mound E, or later Mohenjo-daro seals whose levels are published with the trench (CISI 3.1, not held). If the 3B–3C difference sits in opening signs with the closing stock unchanged, C-0006's contrast returns at another site; if it sits nowhere once the mound is fixed, the fixed-pattern reading stands.
