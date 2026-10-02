# Which sequence features support the Markov restoration score?

Post-outcome mechanism study, written October 2, 2026 before these ablation runs. The earlier [conventional comparator](../markov-baseline/README.md) scored 34.59% exact top-one on the preserved one-slot masks. This study separates learned start frequencies, end-state evidence and interior order while keeping the earlier population, five outer folds and selected smoothing strengths fixed.

## Fixed evidence and model variants

Import the immutable conventional-model code and grouping-helper snapshots from `../markov-baseline/main/`. Require their hashes and the unchanged normalized input to match the frozen result. Use its 8,009 query identities, 1,596 unique strings, 1,526 components and outer seed 20261006. Each outer fold retains its previously selected alpha, 20. No ablation is tuned on its outcomes.

| Variant | Learned initial distribution | Transition fit | Final inference factor | Question |
|---|---|---|---|---|
| Frozen full model | Retained | Glyphs and EOT | `A(c,EOT)` | Reference |
| `no_end_factor` | Retained | Unchanged glyphs and EOT | 1 | Contribution of directly observing the final boundary |
| `glyph_only_fit` | Retained | Refit without EOT; outgoing glyph counts and glyph-unigram smoothing | 1 | Contribution of end-event fitting, including row normalization inside strings |
| `unigram_start` | Replaced by training unigram U | Unchanged glyphs and EOT | `A(c,EOT)` | Contribution of learned initial frequencies |
| `unigram_start_no_end_factor` | Replaced by U | Unchanged glyphs and EOT | 1 | Combined direct boundary factors |
| `unigram_start_glyph_only_fit` | Replaced by U | Refit without EOT | 1 | Combined initial/end-event treatment |

At an initial masked slot the score is the chosen initial distribution times the candidate-to-successor transition. At an internal slot it is predecessor-to-candidate times candidate-to-successor. At the final slot it is predecessor-to-candidate times the stated final factor. Normalize over the unchanged training glyph alphabet plus UNKNOWN. A glyph-only fit removes EOT counts from each row's denominator as well as from its smoothing prior, so it can change internal predictions even when the final factor is absent in both variants.

## Training-order controls

Fit the full conventional model after permuting signs separately within each outer-training string. Twenty declared replicates use seed `20261020 + 100*replicate + fold`, with 100000 added for the interior-only control. Hold-out queries keep their observed order.

The all-slot control permutes every sign position. It preserves each row's length, glyph multiset, site/type, original physical aliases and component/fold assignment, while disrupting start, end and adjacent-order patterns. The interior-only control fixes the first and last signs and permutes only the interior. It therefore preserves exact start/end counts and the same per-row observations while disrupting the available interior adjacency. Length-three strings have one interior sign and cannot change under that control; report this restricted mobility.

All permutations operate only on the current outer-training set and never inspect held-out truths or performance. Group membership remains the original artifact/observed-string membership. Record any synthetic shuffled strings that happen to equal held-out strings as accidental coincidences; do not adaptively reject or regroup a shuffle using held-out outcomes. Preserve training unigram and metadata counts exactly, and verify original train/test alias and observed-string exclusions before transforming the training data.

These controls describe model sensitivity to training order. They are not a full-procedure corpus-null test. Report all twenty replicates and their spread, rather than selecting a favorable seed or best variant.

## Endpoints, uncertainty and verification

For every fixed variant, report exact top-one/five/ten, equal-text and equal-code scores, bucket log loss, unknown-code coverage and five-bin calibration, with per-position and complete-benchmark frequency strata. Compare each variant with the frozen full model using 10,000 paired component bootstrap draws, seed 142. Include per-position and per-frequency top-one/top-five and log-loss differences. The intervals are conditional on the preserved training fits and selected alpha.

For each shuffle family, preserve per-mask predictions for every replicate and report the mean score, replicate range and per-position/frequency effects. Component intervals for the mean control average per-mask outcomes across all twenty fitted replicates before resampling components. Report seed variation separately; this interval does not integrate every possible random training order.

Verify start/end count and formula changes on constructed examples. Compare each ablation's conditional distribution with an explicit complete-string product using its stated initial and transition factors. Check unchanged vocabularies, target independence, probability normalization, old reference reproduction and exact query correspondence. An independent count implementation will check all fixed-variant top-ten rankings and target probabilities. Preserve failures, source snapshots, source hashes and complete scored endpoints in fresh directories.
