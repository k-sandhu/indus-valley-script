# Shot B retrospective

12 October 2026. This records the externally observable course of the shot: what was attempted, what went wrong, how it was repaired and how it ended.

## Approach

The discovery stage profiled every sign on the discovery half, tabulated recurring texts and edges by object type, counted substitution frames and viewed the 118 frequent signs as font renderings. Classes were assigned from position, neighbours and pictures, and the map's implications for the withheld variables were written as five contrasts between class groups, each tested against rearrangements of the map's own records within frequency and position bands. The scoring script was exercised on synthetic withheld fields before freezing.

## Problems and repairs

- **A withheld variable in an unlisted field.** The metadata field `class` carries codes such as `UC` that appear to record the field animal. It was not in the strip list; it was added to the shot's strip list once noticed, and the coordinator was told so that Shot A could be checked.
- **Exposure to aggregate facts.** Several files read for construction summarised withheld variables: the working model, the corpus summary, the split summary and one catalogue row with site counts. Each exposure is listed in PREDICTIONS.md. CISI lookups for the ten quoted texts also showed site prefixes for a few discovery objects.
- **Statistics that grow with frequency.** The first design used per-sign z statistics, which conflate effect and sample size. They were replaced by effect sizes before any real withheld value was loaded.
- **Size model.** A quadratic in text length was replaced by indicators for each length after a synthetic S3 correlation raised the possibility of residual length effects; further synthetic seeds showed the original value was chance.
- **Power of the combined score.** With all five components summed, a planted size effect with z = 3.6 still failed. The coordinator's review reduced the primary score to the two contrasts that follow most directly from the classes, P1 and P2, and kept P3 to P5 as individual tests. The planted run then passed at 3.13 standard deviations.
- **Report file.** The harness refused to let this agent write REPORT.md; the report text was returned to the coordinator for placement.

## Outcome

The frozen primary score was S = −0.567 (33.0th percentile, −0.44 standard deviations), with z₁ = −1.20 and z₂ = +0.63; the kill condition was met and C-0002 is dead. No individual prediction or secondary check passed; P4 (p = 0.082) and S1 (p = 0.051) came closest, and S2 reversed. An independent recomputation reproduced the fail decision.

## Lessons for the next meaning map

Sign-level contrasts on object variables are weak instruments: every sign in a legend shares the legend's site, size and animal, so class differences are diluted, and a rearrangement null within frequency and position bands leaves little for a class map to win. The exploratory pattern, a shared name stock with city-specific closing vocabulary, is a hypothesis for the discovery half's unread site field, to be frozen before that field is opened. The `period` field mixes two excavation sequences and should be used within one site.
