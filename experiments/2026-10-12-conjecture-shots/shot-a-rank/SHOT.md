# Shot A: rank is written twice on Indus seals

Recorded 12 October 2026 before any outcome of this shot was computed.

## Conjecture

Indus seals were issued to holders of graded offices. The seal's size marks the holder's grade, and the closing signs of its legend name that grade or office. The opening signs individualise the holder, so they vary from city to city, while the closing title formulae are shared across cities. Seals that carry the same legend were issued for the same office and grade, so they were cut to the same size.

Starting credence: 0.25. The shot revises it before freezing predictions and again after the confirmation outcome.

## What earlier packages measured

These results bear on the conjecture and are not reproduced as confirmation.

- Complete square seals have a size coefficient of variation of 0.2886, and larger faces carry more text: 1.159 more positions per doubling of face area (q = 0.0002). Unicorn seals are no more uniform in size than seals with rarer animals (CV difference 0.0132, p = 0.65). [Sign context and seals](../../2026-10-06-sign-context-and-seals/REPORT.md).
- An earlier classifier could not predict unicorn versus other animals from seal texts (gain −0.063 nats per object, p = 0.81). The same report cites Konasukawa and Koiso's 2018 chapter *The Size of Indus Seals and its Significance* as a direct precedent whose analysis was not examined.
- Identical seal texts are spread across cities about as chance would place them at Mohenjo-daro, with some local duplicates at smaller sites; long texts almost never repeat; identical texts share the field animal mainly on unicorn seals; most sealings that carry a seal text match seals from other cities. [Seal-text identity](../../2026-10-12-seal-text-identity/REPORT.md).
- Texts end in a small closing class and begin with many different signs; the jar sign 740 is the commonest sign (about 10% of readable positions). [Structure-first step 6](../../2026-10-12-structure-first/step6-language/REPORT.md).
- The anchor-expansion review found that many signs counted as "closing" sit directly before a final 740 or 400 rather than last, so the closing unit may be a two-sign formula. [Review](../../2026-10-12-anchor-expansion/claude-review.md).

## Exploration on the discovery half

Use `shots_common.load_half("discovery")`. Anything may be explored: face area or side length from the catalogue dimensions (handle zeros, inch-to-millimetre rounding and fragments), seal shape and boss, the final sign, the final two signs and the jar-sign formula, the opening sign, length, site, animal, period. Build the strongest version of the conjecture the discovery half supports, including an ordinal grade lexicon of closing units if one appears. Revise the conjecture, or replace parts of it, when the data point elsewhere; record each revision.

## Predictions to freeze

`PREDICTIONS.md` must contain at least these three, stated with exact populations, statistics, nulls and pass rules, plus any others the exploration motivates:

1. Closing units carry seal size beyond length and site. The grade order of closing units estimated on the discovery half reappears on the confirmation half, and closing units explain more size variation than opening signs under a matched comparison.
2. Seals with identical legends are closer in size than seals matched on length, site and shape.
3. Opening signs are more specific to site than closing units, measured against a permutation null that accounts for their different entropies.

Name the kill condition: which combination of failures makes the conjecture dead rather than weakened. Add prospective predictions for material outside the corpus, such as impression sizes of the Lothal sealings that carry the text of Mohenjo-daro M-895, or seals in a future concordance.
