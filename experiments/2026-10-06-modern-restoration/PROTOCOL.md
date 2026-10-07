# Protocol: modern restoration models on preserved masks

Written 6 October 2026 before model fitting. Status: Exploratory, reused benchmark.

## Question and inputs

Test whether modified Kneser–Ney smoothing, a bidirectional recurrent model, a small transformer, archaeological metadata, and additional observed text improve known-slot graphic-code prediction. The saved first-order and second-order results are known: 34.5861% and 37.2706% top-one, with 5.119435 and 5.247171 bucket bits. This experiment reuses their masks and cannot supply a fresh confirmatory evaluation.

Rebuild `lipi_clean_rtl_singleline.jsonl` using the existing alias-preserving loader, group builder and fold allocator. Require equality of the input hash, all 8,009 record/slot keys, targets, lengths, artifacts, components and outer folds against both root restoration audits and the two Markov audits before fitting. Require 1,596 distinct strings, 1,526 components and seed 20261006. Stop on a mismatch. Reuse saved predictions rather than refitting the comparators.

## Extra text and exclusions

Build a transitive graph over every observed face and every benchmark representative using identical nonempty reading-order strings, object family identifiers and artifact aliases. Benchmark representatives retain all aliases. Extra candidates must have nonempty, complete observed sequences, no unknown or blank codes, no flagged damage/uncertainty, and a string absent from the benchmark. Keep one lexicographically first face per extra string after exclusions. Short, multiline and other-direction faces can enter; their stored reading order is used without assigning line breaks that the export does not supply. Record these composition counts.

For each outer fit remove extra faces in the full-graph closure of its test components. For each inner fit also remove the closure of inner validation components. Audit any graph connections between benchmark components; do not change the saved benchmark folds. Report eligible and excluded faces, retained faces/tokens and added distinct strings/tokens for every fit. Additional text is from the same derivative export and may change its domain and target alphabet. Its loss uses a finer training vocabulary when it introduces codes; report OOV rates alongside loss.

## Families and fixed grids

All vocabularies contain only fitted training codes plus one UNKNOWN output bucket; exact top-k never credits UNKNOWN for a fine-code target. Stable descending rank uses sorted codes followed by UNKNOWN. Boundaries and padding are excluded from candidate alphabets.

1. Interpolated modified Kneser–Ney orders 2, 3, 4 and 5. The top order uses occurrence counts; lower orders use distinct preceding-context counts. Count-of-count estimates supply separate discounts for counts 1, 2 and 3+, with explicit safe fallbacks and clipping where sparse counts make estimates undefined. Multiply the discounts by 0.75 or 1.0. Add 0.5 to the bottom continuation counts, including UNKNOWN and end, to give finite bucket probabilities. Use order-minus-one start sentinels and an end state. Score each candidate through every affected full-sequence factor, then normalize. This finite-vocabulary floor is an implementation choice, not an exact reproduction of the 2010 estimator.
2. Bidirectional GRU masked-slot model. Two configurations: width 64, one layer; width 128, two layers. Embedding width equals hidden width. Feed a MASK at the hidden position and read its two-sided recurrent output. Dropout 0.35, including embeddings/output and between layers when applicable.
3. Transformer masked language model. Two configurations: two layers, width 64, four heads; two layers, width 128, four heads. Feed-forward width twice model width, learned absolute positions, dropout 0.35, pre-normalized layers. Read the masked position.
4. Condition the best neural family, separately within each outer fold and text regime, on object type, site, region and motif symbol together. Each category has a training-only vocabulary and an unknown category. Concatenate four 8-dimensional category embeddings to the masked representation. Reuse that family's selected width/depth, and retune training duration on the three inner folds. Metadata comes from the retained representative; it may reflect corpus composition.
5. Fit every family with and without extra text. Train every neural fit with seeds 20261006, 20261007 and 20261008. Main neural predictions average the three probability vectors; report each seed's outer performance and range.
6. Geometric (log-probability) ensemble of the loss-selected n-gram and best loss-selected neural family, including conditioned models as candidates. N-gram weights: 0, 0.25, 0.5, 0.75, 1. Choose within each outer training set on inner predictions. Constituents use the same fitted alphabet.

Neural training masks every training position once per epoch. AdamW, learning rate 0.002, weight decay 0.01, label smoothing 0.05, gradient clipping 1, batch size 1024, maximum 45 epochs. Validation uses ordinary bucket cross-entropy, with no smoothing. Check after each epoch; stop after six epochs without an improvement of at least 0.001 bits. Restore the lowest-loss epoch. Fit the outer model for the median best inner epoch for its configuration and seed, rounded upward; no outer-query early stopping. Deterministic seeds, CUDA backend settings and versions are recorded. If runtime prevents completion, preserve completed stages and identify missing cells; do not silently reduce the declared grid.

## Selection and comparisons

Use the existing three component-held-out inner folds on each outer training subset, seeds 20261006 plus outer-fold index. All validation masks are evaluated. Primary selection minimizes pooled inner bucket loss of the three-seed mean probabilities. Ties prefer the earlier, smaller configuration and then the lower order. Secondary analysis selects the same candidates by pooled top-one; early stopping remains loss-based. Train and report that variant if its configuration differs. Never use an outer query to select a setting, metadata family or ensemble weight.

Report top-one, top-five, top-ten, bucket bits and the original five-bin expected calibration error; also report initial/internal/final and whole-benchmark target-frequency strata 1, 2–4, 5–19, 20+. Use paired resampling of benchmark components, 2,000 draws, seed 23101, for differences against both saved Markov models. Include strata and calibration contrasts. These intervals condition on fitted models and fixed strata; they do not refit selection or capture transcription uncertainty.

## Learning curves and carry-forward record

For each outer fold and regime retain the classical and neural family/configuration selected by full-training inner loss. Train on nested deterministic component subsets at 25%, 50%, 75% and 100%; subset seed 20261006 plus fold. Extra text is fixed at the outer-safe pool in the added-text regime. Report actual texts/components/tokens. Neural duration uses the full-training inner-selected epochs. Use all three seeds and their mean. Compare 75% with 100% using paired component intervals. These curves describe the fixed selected methods, with selection already informed by full training; they are exploratory capacity/data diagnostics. A rise at full size supports further-data testing. A flat curve does not establish an information-theoretic ceiling.

Freeze one carry-forward recipe chosen by pooled inner loss across outer training sets, not outer performance. Freeze its configuration, epochs, seeds, code/input/protocol hashes and full-data weights or counts. Source-derived payloads stay local-only; `frozen-model/` contains a manifest and loader instructions pointing to their hashes and paths. Future fresh data must use this recipe without retuning.

## Checks and negative outcomes

Before corpus fitting, compare n-gram masked scoring with brute-force complete likelihood for all positions of a small case, check discount/continuation counts and row normalization, and confirm hidden-target replacement invariance. For each neural family verify probability normalization, batch/padding behavior and hidden-target replacement invariance. Audit graph exclusions and exact saved-query correspondence. Save detailed probabilities/query records locally and aggregate results in the owned directory.

A model that fails to improve either primary probability loss or exact accuracy against the saved first-order result supplies a negative comparison. Accuracy improvement paired with greater loss is a tradeoff. Report intervals and values even when they include zero. Failure of metadata or extra text to help is retained. Do not infer decipherment, sounds, meanings or novelty from restoration performance.

## Precedent review

Open and record Yadav et al. (2010), Rao et al. (2009), Venkatesh and Farghaly (2023), Tiwari (2026), Ithaca (2022), Aeneas (2025), and Linear B restoration (2024). Compare their corpus, splits and outcome definitions, especially Yadav's 74% sensitivity inside a 90% probability set, which differs from exact top-one. Record inaccessible sources and unsuccessful searches in `sources.json`.


## Review amendment and errata, 7 October 2026

This amendment follows the [Sonnet review](REVIEW.md). It changes interpretation and source attribution after the outcomes. The reviewer graph-rule sensitivities, fixed-hyperparameter linked-string and one-edit-neighbour removals, and extra-text loss decomposition are Exploratory analyses of the reused benchmark. Their existing scripts and aggregates in `review/` supply the evidence; this follow-up fits no models and changes no selections, predictions, aggregate endpoints or carry-forward weights.

The cross-fold links bear on Paper 001's component-held-out independence. They arise from 16 identical one- or two-sign texts on faces of different objects, joining 192 benchmark strings and 748 queries through six sets. The review measures their source, size and sensitivity separately from the saved comparison. Extra-text loss gains must be interpreted alongside the 251 targets absent from the benchmark-only training alphabet. Target-frequency strata condition on the outcome, so their ECE cannot diagnose calibration; position strata retain that use. [Graph rules](review/graph-rule-sensitivity.json), `strings_whose_faces_reach_two_or_more_saved_components`; [graph size](review/graph-links-summary.json), `bridged_rows_total`, `bridged_queries_total`; [loss decomposition](review/extra-text-decomposition.json), `families`.

Three corrections preserve the original protocol wording above. Yadav et al. 2010 used Witten–Bell smoothing with Katz backoff; Rao et al. 2009 already applied modified Kneser–Ney to Indus sequences. The original reference to a 2010 estimator in the first family specification misattributes that estimator. All ten n-gram outer cells existed by 00:09:07 and their summary by 00:16:07, before the 00:18:07 auxiliary-loss amendment. The amendment's original account of only the first outer fold being available understates the outcomes already visible. Finally, epoch restoration in the code uses the last epoch improving best loss by at least 0.001 bits. The original sentence saying lowest-loss epoch omits that threshold. The common-alphabet loss remains an exploratory post-outcome addition. Exact source locations and the timing record are in the [dated errata](ERRATA-2026-10-07.md).
