# Class grammar as backoff after the first outcome

Written 11 October 2026 after run-v1 completed. Run-v1's grammar trails the tuned Markov model by 0.473 bits per token overall. The predeclared stratum of known target codes in unseen training bigrams shows the opposite comparison, while positional prediction performs best in that stratum. These outcomes suggest testing whether a class model can supply probability mass to combinations that the sign-level model underrates.

This refinement reuses the same outer corpus and was motivated by its outcomes. It is exploratory even though every numerical weight below is selected within the outer training set. Preserve run-v1 and write run-v2-mixture separately. No main configuration or endpoint is replaced.

For each outer fold, use the Markov and grammar configurations already selected from run-v1's inner scores. Refit both constituents on each original inner training partition, using the exact run-v1 seeds and two grammar starts. Save new per-token probabilities locally. Select a constant grammar mixing weight from 0, 0.05, 0.10, 0.20, 0.30, 0.50, 0.75 or 1.00 by pooled inner conditional-length sequence log likelihood. At each code position use

`p_mix(code | prefix, length) = (1 - w) p_markov(code | prefix, length) + w p_grammar(code | prefix, length)`.

Both constituents have the same training-only output alphabet and give normalized next-code distributions. The mixture therefore gives a normalized fixed-length sequence distribution, without a target-dependent gate. Obtain outer mixture likelihood from the frozen run-v1 constituent probabilities and the newly selected weight. This is exactly equivalent to recomputing their convex probability mixture for each target; the full candidate distributions need not be redistributed. Zero weight reproduces the original selected Markov predictor exactly.

Report pooled all-token, noninitial and equal-text differences, every fold and the same target/context strata. Use the same 5,000-draw conditional component bootstrap. A gain whose interval includes zero will be reported that way. No new semantic interpretation is selected by the mixture. Freeze a full-data mixing weight using pooled inner scores from all outer training sets, rather than outer performance; this can accompany the descriptive full-data class grammar for a later genuinely unseen corpus.

Verification must reproduce every inner constituent score from the original seed/configuration within floating tolerance, verify normalization for a toy mixture at every registered weight, audit inner closure exclusions, recover the zero-weight outer benchmark exactly and preserve input/protocol/code hashes. Any discrepancy receives its own failed endpoint before a repair. The mixture's weight grid was fixed before any mixture likelihood was calculated.
