# Amendment 2: Stage 3e failed; Stage 3g repairs the comparison

Recorded 12 October 2026, after Stage 3e outcomes. Stage 3e's output remains in [`stage3e/summary.json`](stage3e/summary.json) as a failed implementation.

## What failed

Stage 3e let every sign take any consonant class and optimized order gain, the per-consonant difference between the order-5 log-probability and the class-unigram log-probability. For Latin, all three full-corpus fits and both scrambled fits reached exactly 8.517 bits per consonant, and the half-A fits reached 8.505. Real Latin text scores 0.47 to 0.66. The optimizer had placed most signs on rare classes. The unigram term then contributes a large positive amount for each token, while the backed-off order-5 probability of a repeated rare class stays moderate. The statistic stops measuring sequential agreement when the token-level class distribution is free to move. The first attempt at this stage also hung after a worker memory failure under 20 processes; the rerun used eight workers and kept only probability tables in each worker.

Stage 3's swap optimization keeps the key's multiset of values over sign types, but the token-level distribution can still shift when values move between frequent and rare signs. A check after Stage 3e found that the eight real-order Stage 3 optima are 0.36 to 0.62 bits (Kullback–Leibler divergence) from the Sanskrit class unigram. The published key itself is 0.495 bits away, mainly because the frequent *an/aṃ* jar value makes *m* 32.8% of tokens against 7.4% in Sanskrit text. The Stage 3 optima therefore did not gain their order gain by the rare-class route.

## Repair

Stage 3g ([script](stage3g_constrained.py), [output](stage3g/summary.json)) restricts swaps to signs in the same frequency stratum, the strata used by null N1, so the token-level class distribution stays close to its starting point.

1. Sanskrit with the key's own option multiset starts from an N1 draw. The optimum is therefore the best arrangement found inside the space that N1 samples, which answers directly whether the key is a good arrangement of its own values.
2. For Sanskrit, Latin, Old Tamil and Sumerian, signs in descending frequency take the class with the largest remaining token quota under that language's unigram, the assignment is permuted within strata, and within-stratum swaps optimize order gain. Fifty randomized token-matched starts per language give the null for that space. Each language is compared with its own held-out line-initial spans.

Stage 3g was designed after Stage 3e's outcome and is exploratory. The Stage 3 decision rules, which use the swap optimization over the key's multiset, are unchanged.

## Correction after review, 12 October 2026

The adversarial review found two problems with the check above, and [`stage3_token_check.py`](stage3_token_check.py) now saves it ([output](stage3/token_check.json)). The figures *m* 32.8% and 0.495 bits assumed that the *an/aṃ* jar value always reads *m*. Under the greedy choice that Stage 3 scores, *m* is 24.1% of the key's consonants and the divergence is 0.313 bits; the eight real-order optima lie at 0.262 to 0.573 bits. The statement that the optima did not gain through rare classes stands. The check missed a second route: the unconstrained optima turn 1,898 to 3,905 of 8,535 sign tokens into vowels (the key: 1,049) and leave up to 118 texts with no consonant, and the scrambled-corpus optima turn 4,292 to 5,157 tokens into vowels. Their order gains therefore include deletion. The within-stratum optima of Stage 3g keep 7,702 to 7,882 consonants against the key's 7,833 and are the like-for-like comparison.
