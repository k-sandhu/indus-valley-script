# Final delta review of papers 002 and 003

The new shared-quality section agrees with its saved numerical endpoint. Paper 003 carries all four factual corrections and both wording changes from the first review. Paper 002's interval-denominator sentence was corrected during this delta review, leaving no remaining factual correction. The [starting manuscript snapshot](manuscript-inputs.json) fixes the initial line references; the [completion snapshot](completion-delta.json) records the two subsequent Paper 002 changes. The [check record](numerical-checks.json) contains 41,979 passing arithmetic assertions and hashes of 1,308 inspected output files.

## Denominator correction completed

In the starting version of [Paper 002 methods](../../../../../papers/002-conditional-reference-laws/methods.md), line 22 described every method's interval as using 1,000 populations, following a table containing the 300-population shared-quality nested study. The completed edit now reads:

> Marginal rate intervals are Wilson intervals across the stated independent populations: 1,000 for the original main studies and agreement diagnostic, and 300 for the shared-quality nested comparison.

The manuscript itself supplies the correct denominators in Section 6.1, line 118, and Section 6.2, line 124. No numerical correction is needed there.

The new abstract also carries the 300-versus-1,000 populations and post-outcome score development accurately. One optional wording edit would make its final comparison more precise: replace “independent exact tails” with “exact conditional tails.” The tails evaluate the same fresh populations; a separate calculation independently checks their arithmetic.

## Shared-quality result and its follow-up

Paper 002 Section 6.1 reports twelve broad-reference rejections and nine quality-reference rejections among 300 populations. The saved gains reproduce the 4% and 3% rates. Wilson intervals match, as does the saved independently audited paired interval of -1 to 3 percentage points. The six-column broad space, four-column quality space, sixty-four uniform quality tables and stated covariance values also match their separate endpoints.

Section 6.2 accurately describes a new statistic developed after that result and fixed before a fresh 1,000-population run. Its score uses observed face pairs. Quality labels define reference cells. The new generation seeds are distinct from all 300 nested-study seeds. The manuscript retains both results and identifies their different scores and populations in adjacent sections.

| Cutoff | Broad, 99 draws | Quality, 99 draws | Broad, exact | Quality, exact |
|---:|---:|---:|---:|---:|
| 1% | 790/1,000 | 0/1,000 | 848/1,000 | 0/1,000 |
| 5% | 942/1,000 | 10/1,000 | 950/1,000 | 8/1,000 |
| 10% | 972/1,000 | 22/1,000 | 976/1,000 | 21/1,000 |

These counts reproduce every entry in the manuscript's table, lines 126-130. At 5%, the paired Monte Carlo counts are ten joint rejections, 932 broad-only rejections, no quality-only rejections and 58 joint nonrejections. Their difference is 93.2 percentage points. The reported interval of 91.6-94.7 agrees with the independently audited 20,000-draw bootstrap output.

The generator mean recomputes as `1859177/98000`, the expected broad conditional mean as `2647129/196000`, and their gap as `42849/7840`. These round to 18.9712, 13.5058 and 5.4654. The observed signs give mean score 18.855; per-cell agreement counts give broad mean 13.4469 and quality mean 18.8614. All three match line 132.

The finite check fixes the middle agreement column and counts the overlaps of each outer column with it. Multiplying the two overlap distributions and the number of middle-column arrangements independently reproduces all 1,547 saved integer distributions. Their totals equal the products of three binomial coefficients; their means equal `(a0*a1+a1*a2)/n`. Cell convolution then reproduces all 2,000 saved exact population tails. Quality-conditioned score distributions have one possible score in 104 of the 1,000 populations and at most nine possible scores throughout this run. This supports line 136's explanation of constant scores and inclusive ties. The claimed audit sizes in line 134 match the audit record.

## Physical corrections now carried

| Paper 003 line | Current content checked |
|---:|---|
| 43 | The reversal control changes selected rows' column order. Whole-row permutation remains a separate additive invariance check. |
| 55 | Visible local rows contribute equality votes even when associations are missing. |
| 55 | The collective operation uses the same quantity type, units and event, with content marks and pooling without loss or exchange. All parent and pool marks are available before the first local prefix, with no assigned acquisition cost. |
| 59 | KHI-05 reuses held-out coefficient rows after prior outcomes. Selector inputs, target separation, unit-anchor availability and abstract one-check cost remain explicit. |
| 119 | The minimum-check comparisons retain their one-versus-two and two-versus-three budgets; the misleading equal-count phrase has been removed. |
| 144 | Base collections or seeds are independent units. Prefixes, representations, policies and reused condition views share them. |

The current text preserves the counted-unit scale premise, separate normalized rays, local support gates, partial-inventory inequality and KHI-05's fixed-population reuse. Its methods and claim map retain the exact linked endpoints. No further correction arose from these edits.

Paper 002 line 110 now identifies the agreement-estimated rate in the `.334097` comparator. Its line 63 correctly gives Pearson statistic 263.5194, 215 degrees of freedom and p=.01336. The first review's line-63 finding was already stale relative to its own saved manuscript snapshot; this delta records that discrepancy while preserving the original review.

## Review scope

The [helper](check_delta.py) reads saved observed signs, gains, reference scores and rational distributions. It checks 1,000 observed agreement scores, 2,000 Monte Carlo tails, 2,000 exact tails and 600 nested-score tails. No fitting routine, generator, sampler or bootstrap was rerun. Paired intervals are compared with the contributor's independent audit. This reviewer left shared files and frozen source endpoints untouched. The current prose explains the score change and physical premises directly.
