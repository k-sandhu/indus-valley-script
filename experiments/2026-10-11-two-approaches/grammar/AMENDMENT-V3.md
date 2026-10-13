# Matched positional backoff control

Written 11 October 2026 after run-v2-mixture scores were exposed. The parent reviewer requested the same Markov mixture with positional probabilities to determine whether the class model contributes more than ordinary backoff. Run-v2-mixture improves on Markov, but that comparison alone cannot assign the improvement to learned classes. This amendment defines run-v3-matched-mixtures before any Markov-plus-position mixture score is calculated.

Reuse the frozen run-v1 outer folds and selected constituent configurations. Reuse run-v2-mixture's saved inner Markov and class-grammar probabilities and all its selected weights. Refit only the selected positional configuration on each corresponding inner training set. The positional baseline uses exactly the same training signs and UNKNOWN bucket as the other constituents.

Select the positional mixing weight from the same grid, 0, 0.05, 0.10, 0.20, 0.30, 0.50, 0.75 and 1.00, by pooled inner log likelihood. Apply it to the frozen run-v1 Markov and positional outer probabilities. Compare Markov-plus-class against Markov-plus-position using a paired component bootstrap on the same texts and tokens. Also report each mixture against Markov. Preserve the primary grammar loss, run-v2 results and their labels. The class mixture's weight is not changed in response to this comparison.

Any useful class increment remains an exploratory result on exposed outer outcomes. The extra comparator was requested because the initial mixture was insufficient to isolate a class contribution. A later unseen input should compare both frozen backoff families without retuning.
