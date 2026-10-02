# Independent review of reference-only model selection

The saved experiment's choices and numerical results are reproduced. The review checked 48 generated systems, 96 reference selections, 384 mapping conditions and 1,536 algorithm outputs. All 6,489 checks passed. The complete-record Markov likelihood includes the exact-length normalizer, and an independent state recursion agrees with the saved scores. The largest pooled reference-score difference is 3.46 × 10⁻¹¹ bits; the closest model-choice margin is 2.887 bits.

The selector chooses graph mapping for every transition reference sample. It chooses length/slot mapping for every 20-symbol administrative sample and every 400-record, 8-symbol administrative sample. Among the twelve 40-record, 8-symbol administrative samples, six choose each model. Across the complete grid, the selector recovers 309 of 384 maps, compared with 283 for fixed graph mapping, 168 for fixed slot mapping and 310 for the supplied-family diagnostic.

| Generated family and inventory | Fixed graph | Fixed slot | Reference selector | Supplied-family diagnostic |
|---|---:|---:|---:|---:|
| Transition, 8 symbols | 92 / 96 | 26 / 96 | 92 / 96 | 92 / 96 |
| Administrative form, 8 symbols | 94 / 96 | 96 / 96 | 95 / 96 | 96 / 96 |
| Transition, 20 symbols | 76 / 96 | 0 / 96 | 76 / 96 | 76 / 96 |
| Administrative form, 20 symbols | 21 / 96 | 46 / 96 | 46 / 96 | 46 / 96 |

In the 20-symbol administrative group, the selector's complete-recovery gain over fixed graph mapping is 26.04 percentage points. A paired bootstrap over twelve system means gives a 95% percentile interval of 14.58–38.54 points. In the 8-symbol administrative group, its loss relative to fixed slot mapping is 1.04 points, with an interval of −3.13–0.00 points. Every system mean includes its eight reference-size, training-size and process-change conditions. The complete [paired output](additional-v1/paired-comparisons.json) also preserves symbol accuracy and both held-out likelihood differences.

The held-out likelihoods reproduce for every returned map. The graph loss is scored conditional on observed record length and divided by held-out symbol count; the slot loss uses the same record lengths and symbol denominator. The biggest review discrepancy is 1.93 × 10⁻¹³ bits per token for the slot loss and 7.19 × 10⁻¹⁴ for the conditional graph loss. The [reviewed rows](main-v1/reviewed-rows.json) retain all values and answer-key comparisons.

An additional assignment audit found exact likelihood ties in eleven slot conditions: six transition and five administrative conditions, all with twenty symbols and forty reference records. It preserves 32 alternative-permutation witnesses. The five administrative tied conditions use slot mapping in the selector. Each alternative has an exactly equal integer-smoothed likelihood numerator, certified by prime-factor cancellation. These witnesses preserve unresolved code identities beside the selected point map. The [alternatives](additional-v1/exact-slot-alternatives.json) give the conditions, changed codes and complete returned alternatives.

## Likelihood reconstruction

The review rebuilt start, internal-transition, end and length/position counts directly from saved records with Counters. The smoothed start denominator is the number of reference records plus inventory size. Each symbol's outgoing row has a denominator equal to its occurrence count plus the number of symbol destinations and one end destination. Each length/position cell has a denominator equal to the number of reference records of that length plus inventory size. An unobserved cell is uniform.

For length L, let the start vector be s, the symbol transition matrix T and end probabilities e. The review starts with v₁ = s, recursively computes vₗ₊₁(b) = ∑ₐ vₗ(a) T(a,b), and ends with Z_L = ∑ᶜ v_L(c) e(c). Each complete-record log likelihood subtracts log₂ Z_L. Exact Fraction enumeration of all two-symbol records at lengths one through four verifies the recurrence and verifies that both conditional sequence distributions sum to one.

Reference folds were recreated from the declared permutation seed using a separate index-to-fold assignment route. Choices were recomputed from pooled held-out reference scores. Truth permutations were reconstructed from world seeds for evaluation; selected and supplied-family rows were checked against their corresponding fixed-method maps. All saved input bytes and code-snapshot hashes remained unchanged.

An independent dual linear program certifies every slot assignment within 10⁻⁷ bits and checks constraint feasibility at that tolerance. Candidate tight-edge cycles generated the alternative maps; exact integer-factor cancellation then certified equality for each retained witness. This certificate covers the linear slot objective. Graph maps retain their saved heuristic-search status, and the review checks their objectives and test predictions. The paired uncertainty calculation concerns these two generated families and twelve systems per family/inventory.

Read [the review protocol](PROTOCOL.md), [primary verification](main-v1/verification.json), [additional protocol](ADDITIONAL_PROTOCOL.md), [additional outputs](additional-v1/verification.json) and [retrospective](RETROSPECTIVE.md) for the complete record.
