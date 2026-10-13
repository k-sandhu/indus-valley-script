# Amendment 3: checks added in response to the review

Recorded 12 October 2026 after the [review](review/REVIEW.md). Exploratory. [review_response.py](review_response.py) recomputes the reviewer's checks and saves them in [run-2026-10-12/review-response.json](run-2026-10-12/review-response.json); earlier outputs are unchanged.

1. Same-site duplicate pairs split by site class (Mohenjo-daro, Harappa, other sites) against the length-stratified and global nulls, and S1 restricted to seals outside Mohenjo-daro.
2. A mixture bound: the share f of shared texts that could be wholly local while the observed statistic stays within the lower 95% of the mixture distribution, in steps of 0.05.
3. The variant-merged texts under the length-stratified null.
4. The coincidence calculation with the bigram model fitted to distinct seal texts only and to distinct non-seal texts only.
5. Motif concordance split into unicorn and other pairs, and with "no motif" treated as a category.
6. A permutation null for the difference between the opening-pair and closing-pair locality ratios of Amendment 1.
7. A recount of sealings whose matching seals are all at other sites, and of distinct texts among them.

The reviewer's restricted-to-other-sites null (0.248) differs from the recomputation (0.286, the exact hypergeometric value for those 513 seals), and its mixture bound (0.30) from the recomputed one (0.25); the report uses the recomputed values.
