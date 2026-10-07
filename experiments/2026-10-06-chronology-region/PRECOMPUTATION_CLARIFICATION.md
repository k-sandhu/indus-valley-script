# Implementation clarification

Recorded 7 October 2026 before running outcome calculations. The package began under the October 6 date and continues in its assigned directories. This clarification fixes the following implementation details without changing a computed result.

Regional bootstraps also stratify physical components by site, keeping the sampled site frame represented. Permutation p-values use equal-type weighting without site balancing because permuting regions while preserving each site's region is impossible. The site-balanced effect and its interval are reported separately. Sign-test intervals refer to the same equal-type permutation-population estimand as their p-values. The raw, common-support and site-balanced full-population effects retain their own intervals.

Fold assignment uses deterministic greedy token balance over the full physical/text closure. Training-size sensitivity samples components, retaining all their eligible faces; equal component budgets can still yield unequal token totals, which are reported. Model intervals resample the saved out-of-fold losses and condition on fitted models; they do not measure variability from refitting the training population.

Matched external analyses use the first-order model trained on a core fold complement. Each external component is allocated deterministically to one comparator fold, and each external face is compared with core faces in that fold. The 20-face minimum is checked across all eligible core records in the exact length/type cell; a fold needs at least two comparator faces. A candidate with inadequate fold support is excluded and logged. This prevents a model from scoring its own training examples.
