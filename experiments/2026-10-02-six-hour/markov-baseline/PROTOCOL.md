# Conventional Markov comparison on the preserved masks

Written before fitting this new baseline, October 2, 2026.

The existing restoration benchmark hides each of 8,009 signs in 1,596 intact unique strings. Its five folds keep 1,526 connected physical-artifact/text components together. We will fit a conventional first-order Markov model on those same training sets and compare its predictions with the saved position/metadata (PM) and bidirectional local (PMB) predictions. This tests how much the current PMB improvement depends on its length, position and metadata terms once a conventional sequential comparator is available.

## Population and exact correspondence

Use `data/normalized/lipi_clean_rtl_singleline.jsonl`, minimum length three, unique strings with all physical aliases retained. Recreate grouping and five token-balanced folds with seed 20261006. Verify every saved query's record, slot, actual code, length, group and fold against the reconstructed rows. Require all 8,009 unique queries and the original input/helper hashes to match. Compare newly summarized PM and PMB scores with their saved benchmark summaries. Abort and preserve a failure record if correspondence fails.

## Model

Let V be the sorted training glyph codes followed by `__UNKNOWN__`, matching the existing predictor. Add an end-of-text state E only as a possible transition destination. The initial distribution is the training count of first signs, smoothed toward the training glyph unigram U. Each glyph's outgoing transition distribution includes internal successors and E; it is smoothed toward the corresponding training destination unigram Q. U and Q add 0.5 to each state before normalization. Q contains every glyph occurrence and one E per training string.

For smoothing strength α,

`π(c) = [start_count(c)+α U(c)]/[number_of_strings+α]`

`A(c,d) = [transition_count(c,d)+α Q(d)]/[outgoing_count(c)+α]`.

The transition matrix is the same at every position. Here “stationary” refers to a position-independent transition rule; the initial distribution need not be its equilibrium distribution. With candidate c in an internal slot between a and b, the unnormalized score is `A(a,c) A(c,b)`. At the first slot it is `π(c) A(c,b)`, and at the final slot it is `A(a,c) A(c,E)`. Normalize over V. Observed neighbors unseen in training map to `__UNKNOWN__`. The hidden target is never used to compute its distribution. E cannot be suggested as a glyph.

[Rao et al., *A Markov model of the Indus script* (2009)](https://homes.cs.washington.edu/~rao/PNASIndus.pdf) supplies the conceptual comparator: initial probabilities, first-order transitions, an end-of-text state, and missing-sign inference. Their study used the 417-sign Mahadevan list and modified Kneser–Ney smoothing. This run uses the present fine-code corpus, pooled unknown state and the smoothing formula above, so it evaluates a documented first-order baseline on our own benchmark.

## Training and endpoints

Select α from 20, 100, 500 and 2000, matching the existing restoration grid. Three inner component-held-out folds, with seed `20261006 + outer_fold`, maximize exact all-slot top-one accuracy; ties favor greater α. Outer outcomes cannot select α or change the grid. Reuse saved PM/PMB predictions without refitting them.

Report exact top-one, top-five and top-ten micro accuracy; equal-text accuracy; and macro accuracy over the observed true-code types. Preserve the descriptive complete-benchmark frequency strata 1, 2–4, 5–19 and 20+ occurrences. Exact unseen-code predictions count as failures. Bucket log loss maps unseen truths to the pooled unknown state.

For Markov–PM and PMB–Markov differences, resample the 1,526 components 10,000 times with seed 142. Use paired differences for top-one, top-five, top-ten, bucket log loss and top-label Brier score. Equal-text paired top-one intervals use inverse string-length slot weights. Report five fixed confidence bins [0,.2), [.2,.4), [.4,.6), [.6,.8), [.8,1], expected calibration error and the top-label Brier score `(top_mass - exact_top1)^2`. These describe the model's masked-data predictions without fitting a calibrator on the outer outcomes.

## Verification and preservation

Test the conditional distribution against explicit complete-string likelihoods for first, internal and final masks. Test successor sensitivity, hidden-target independence, normalization, unknown-neighbor fallback, end-state exclusion, common alphabet and exact saved-query correspondence. Save source snapshots, source hashes, folds, tuning scores, full top-ten suggestions, all summaries and comparison intervals in a fresh run directory. Refuse an existing endpoint. Record coding defects and repairs in the run retrospective before using its measurements.
