# Recovering a known channel from paired simulated faces

Paired agreement recovered the generating replacement rate on average, while direct frequency inversion produced negative components in every small simulated population. The constrained joint fit produced valid distributions and lower frequency error than projected inversion. A simple matched shrinkage estimate had still lower error for the ten-object cells. Pooling the populations made channel correction useful for recovering the generating frequencies. [Main results](main/results.json), [independent verification](main/verification.json).

The study reuses the 1,000 frozen noisy-face populations. Each has sixty ordered sign pairs and six cells with ten objects per cell. The eight categories and symmetric channel are known, and the generating rate is .1. The [protocol](PROTOCOL.md) consolidates the model's identification assumptions, estimands and fitting rules. It was written before fitting the saved populations, with prior pilot/outcome exposure recorded. The [comparison amendment](COMPARISON_AMENDMENT.md) adds the matched shrinkage baseline before those fits.

Agreement gives a direct rate estimate through `ε=(7/8)[1−sqrt((8H−1)/7)]` on the positive-association branch. The joint estimator maximizes the ordered-pair likelihood with fixed Dirichlet(1.5) cell penalties and a Beta(1.5,1.5) rate penalty. It uses three starting rates and selects their largest final penalized objective. A known-rate companion fixes ε=.1. Latent truth supplies the evaluation targets and source checks.

| Rate estimator | Mean rate | Mean absolute rate error | Root mean squared rate error |
|---|---:|---:|---:|
| Agreement inversion | .099261 | .023162 | .028757 |
| Penalized joint fit | .101605 | .022195 | .027905 |

The mean agreement-estimator bias is −.000739, with a 95% bootstrap interval of −.002501 to .001041. The joint bias is .001605, interval −.000104 to .003325. An independent enumeration of all 61 binomial agreement counts predicts agreement-estimator mean .100531 and mean absolute error .022898. The calculation uses exact count probabilities and independently checks its moment sums with 70-digit decimal arithmetic. [Exact sampling distribution](exact-agreement-estimator/results.json).

Frequency error is measured against the generating cell probabilities. Total variation is half the sum of absolute component errors, averaged across the six cells:

| Frequency estimator | Mean total variation | 95% bootstrap interval | Pooled total variation |
|---|---:|---:|---:|
| Observed mean face marginal | .310903 | .308692–.313122 | .020967 |
| Matched .5-per-category shrinkage | .227690 | .226078–.229311 | .021002 |
| Projected agreement inversion | .334097 | .331812–.336383 | .012282 |
| Joint fit, estimated rate | .245280 | .243590–.246976 | .012236 |
| Joint fit, known rate | .245255 | .243564–.246952 | .012234 |

The paired mean joint-minus-projected total-variation difference is −.088816, interval −.089651 to −.087966. For these ten-object cells, the matched shrinkage baseline's error is .227690, compared with .245280 for the joint fit. The fixed prior and small sample contribute to that comparison. In the pooled sixty-thousand-pair table, the same joint fit has error .012236 and the observed marginal has error .020967. The pooled agreement and joint rates are .0987282 and .0987285. These are the declared larger-sample checks using the same generating cell distributions.

Both raw inversions, at the estimated rate and at the known .1 rate, have 10,335 negative components across 5,466 of 6,000 cells. All 1,000 populations have an affected cell. At the known rate, a component becomes negative exactly when its category is absent from both observed faces. Rational inclusion/exclusion predicts 10.33187 negative components per population and 5.46922 affected cells, compared with observed means 10.335 and 5.466. An independent ten-step category-set recurrence checks the coverage probability and both absence-count moments. [Exact absence results](exact-negative-inversions/results.json).

All four thousand fitting-start traces met the stopping rule within 34 iterations. The largest objective spread between the three unknown-rate starts is 1.42e−13. The audit independently reconstructed every pair-count table, checked four thousand objectives and traces and six thousand simplex projections, replayed eight fits and the 20,000 bootstrap draws, and compared three selected solutions with a separate constrained optimizer. All checks passed. The complete fitting and bootstrap run took 11.57 seconds. Every input population hash is retained in [the manifest](main/input_hashes.json).

[The implementation-domain note](IMPLEMENTATION_DOMAIN_NOTE.md) records an unspecified uniform fallback at the direct inverse's boundary. No main population reached that boundary. [The identification note](IDENTIFICATION.md) derives the shared-rate inversion and an unequal-rate ideal limit, including a rational example of uniform-frequency ambiguity. [Related work](RELATED-WORK.md) links observer-error fitting, expectation/maximization and latent-mixture identification.

The next experiment would vary the replacement mechanism, face dependence and degree of latent-frequency concentration. Those changes would test how the rate estimator and frequency correction behave when this symmetric observation model is misspecified. An archaeological fit would first need aligned measurements and a source model for their joint errors.
