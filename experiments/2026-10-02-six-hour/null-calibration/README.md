# Conditional references under known observation laws

Independent-slot simulations give rejection rates near their declared thresholds when the reference follows the record process. Treating physical copies or correlated faces as independently movable records raises rejection rates in these experiments. At the nominal 5% threshold, identical-copy populations reject 15.9% under record shuffling and 5.4% under object shuffling; imperfect-face populations reject 11.0% under record shuffling and 5.0% under ordered face-vector shuffling.

Every corpus here is synthetic. The preserved fitting statistic rebuilds physical/text components, five outer folds, three inner folds and smoothing selection for each table. Its score is held-out dependent-minus-independent log probability in bits per noninitial sign. The observation laws, conditional spaces and fitting-domain premises are in [MAIN_PROTOCOL.md](MAIN_PROTOCOL.md), [MATHEMATICS.md](MATHEMATICS.md) and [the domain study](domain-support/README.md).

## Main measured outcomes

Each case uses 1,000 generated populations and 99 reference draws per population. The one-sided p-value is `(1 + number of reference scores ≥ observed score)/100`. The table reports rejection percentages; the interval refers to the 5% threshold and uses Wilson's calculation across the 1,000 populations.

| Generating population | Reference | At 1% | At 5% | At 10% | 95% interval at 5% |
|---|---|---:|---:|---:|---:|
| Independent records | Record columns | 1.1% | 5.0% | 9.9% | 3.813–6.531% |
| Whole-string-unique records | Uniqueness-conditioned columns | 1.1% | 5.9% | 10.6% | 4.601–7.536% |
| Two identical records per object | Record columns | 4.8% | 15.9% | 27.0% | 13.765–18.296% |
| Two identical records per object | Object columns | 1.1% | 5.4% | 10.3% | 4.162–6.979% |
| Two imperfect faces per object | Record columns | 2.5% | 11.0% | 19.6% | 9.208–13.091% |
| Two imperfect faces per object | Ordered face vectors | 0.5% | 5.0% | 10.4% | 3.813–6.531% |

The original [main endpoint](main/results.json) contains 3,000 populations and 396,000 reference fits. [Its full independent audit](verification_main.json) reconstructs all 928,424 proposals, every accepted graph/fold allocation and p-value, and replays 33 complete fits. The [imperfect-face endpoint](noisy-faces/main/results.json) contains 1,000 populations and 198,000 reference fits; [its completed audit](noisy-faces/verification_main.json) reconstructs all proposals, components and p-values and replays fifteen complete fits. Both audits passed.

[The calibration figure](plots/main/calibration.svg) plots all eighteen measured points with their Wilson intervals. Its [numeric table](plots/main/points.csv) and [input hashes](plots/main/figure.json) preserve the figure's correspondence to the endpoints.

The copy comparison's paired difference at 5% is 10.5 percentage points, interval 8.5–12.6. Its original seed schedule links 500 pairs of trials, so [the paired audit](paired_seed_audit.json) uses those 500 clusters. The face comparison's paired difference is 6.0 points, interval 4.3–7.7, from 20,000 population bootstrap draws. Both stream structures and calculation rules are preserved.

## Exact examples and follow-ups

The [evidence map](MANUSCRIPT_MAP.md) links each claim to its output and independent check. [The exact binary experiment](exact/results.json) enumerates 8,000 ordinary tables and 2,880 unique tables. It checks equal permutation multiplicity and fits every unique table. [Copy-tail counting](copy-tail-counts/README.md) isolates copying with an integer adjacency statistic, and [weighted-copy counting](unequal-copy-counts/README.md) supplies a uniform continuation sampler when objects have unequal record counts. [Deduplicated selection](dedup-selection/README.md) shows how retaining distinct strings from raw draws produces different conditional weights.

The [domain witness](domain-support/README.md) preserves two tables with the same face-vector margins and either one or twenty components. The one-component nested fit fails. A separate declared zero-score extension and observed-abstention rule are checked across the complete 8,000-table space, alongside a reference conditioned on fitting feasibility. Their rejection fractions specify both the tail denominator and the observation-selection event.

The [channel follow-up](noisy-channel/README.md) reuses the frozen imperfect faces to fit their supplied symmetric error kernel. It compares agreement inversion, constrained joint likelihood and a matched frequency-shrinkage control. Exact absence probabilities explain frequent negative raw inversions in ten-object cells, and separate calculations establish the rate-identification premises. [RETROSPECTIVE.md](RETROSPECTIVE.md) records failed designs, implementation fixes, prior sources and the next measurements needed for an archaeological application.
