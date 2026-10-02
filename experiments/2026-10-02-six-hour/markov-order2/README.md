# Second-order restoration on preserved masks

Second-order context raised exact top-one restoration to 37.27%, compared with 34.59% for the first-order model. Its probability loss increased from 5.119 to 5.247 bits per slot. When a separate run selected smoothing by held-out probability loss, all five folds chose the first-order backoff. The two selection objectives therefore lead to different results on this benchmark.

Both runs use the same 8,009 masks, 1,596 distinct strings and 1,526 artifact/string components as the earlier comparator. Outer components remain excluded from fitting and inner selection. These model choices were developed after inspecting earlier benchmark results. [Top-one protocol](PROTOCOL.md), [loss-selection protocol](loss-selected/PROTOCOL.md).

The [findings](FINDINGS.md) give the paired results and implementation details. [The retrospective](RETROSPECTIVE.md) records the failed ranking check and its exact rational resolution. Detailed source-derived predictions remain local; aggregates, code snapshots, protocols and reviews are retained in the repository.

| Endpoint | Selection rule | Result | Independent review |
|---|---|---|---|
| MARKOV-03 | Maximize inner exact top-one | [Five-fold result](main/results.json) | [All 8,009 queries](review-ties/verification.json) |
| MARKOV-04 | Minimize inner bucket loss | [Five-fold result](loss-selected/main/results.json) | [All 8,009 queries](loss-selected/review/verification.json) |

Working source: [model and selection](../../../src/six_hour/markov_order2.py), [independent full-record reviewer](../../../src/six_hour/review_markov_order2.py). Each endpoint retains the source actually used.
