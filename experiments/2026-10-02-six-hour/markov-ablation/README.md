# End boundaries and interior order contribute to restoration

The conventional Markov model's 34.59% top-one score depends on both sequence boundaries and interior order. Removing its final end-of-text factor lowers final-slot accuracy from **53.95% to 48.25%**. Preserving each training string's first and last signs while shuffling its interior lowers overall accuracy to **24.52%**, averaged over twenty training orders. The complete results are in [main/results.json](main/results.json); the [protocol](PROTOCOL.md) identifies this as a mechanism study designed after the earlier comparator's outcome.

| Model or intervention | Exact top-one | Exact top-five | Bucket loss, bits per slot |
|---|---:|---:|---:|
| Frozen full Markov model | 34.59% | 58.46% | 5.119 |
| Remove only final end factor | 33.45% | 57.71% | 5.267 |
| Refit transitions without end events | 33.11% | 57.12% | 5.277 |
| Replace learned start distribution with unigram | 34.22% | 57.98% | 5.042 |
| Unigram start and remove final end factor | 33.09% | 57.24% | 5.190 |
| Unigram start and refit without end events | 32.56% | 56.47% | 5.224 |
| All-slot training shuffle, twenty-order mean | 14.88% | 34.33% | 7.069 |
| Interior-only training shuffle, twenty-order mean | 24.52% | 45.04% | 6.155 |

Every intervention uses the same 8,009 masks, original physical/text components and outer folds. Each fold keeps the smoothing strength selected in the earlier comparator. The baseline predictions and source snapshots remain unchanged. Unknown-target coverage stays at 3.13% for every fitted variant and training shuffle.

## The final boundary supplies useful evidence

Removing only `A(candidate,EOT)` leaves initial and internal distributions exactly unchanged. At final masks, top-one falls by 5.70 percentage points, with paired component-bootstrap 95% interval −7.29 to −4.11. Top-five falls by 3.76 points, with interval −5.02 to −2.54. Final-slot bucket loss increases by 0.740 bits, with interval 0.691–0.789. Because final masks are about one fifth of all slots, the overall top-one change is smaller: −1.136 points, with interval −1.453 to −0.819.

Removing end events from training also changes the transition fit. An outgoing row then divides by internal-successor counts alone and uses a glyph-only smoothing prior. Internal-slot top-one falls from 33.59% to 33.07%, a difference of −0.519 points with interval −0.928 to −0.142. This additional effect explains why deleting the inference factor and deleting end-event fitting are separate interventions. Their final top-one values happen to coincide here; their internal rankings, top-five scores and losses differ.

## Starting frequencies create an accuracy–loss tradeoff

Replacing the learned initial distribution with the training unigram changes only initial masks. Initial top-one falls from 18.23% to 16.42%, a difference of −1.817 points with interval −3.508 to −0.126. Initial top-five falls from 45.05% to 42.67%.

The same change improves initial bucket loss from 6.819 to 6.430 bits. The difference is −0.388 bits, with interval −0.502 to −0.276. A distribution can rank more top answers correctly while assigning very small mass to other observed outcomes. This observed tradeoff suggests a separate training-only choice for start-distribution smoothing or its shrinkage toward the unigram. The present ablations retain the earlier alpha and were not retuned to choose between these objectives.

Removing both direct boundary factors lowers overall top-one by 1.498 points. Their direct effects add because one changes initial masks and the other changes final masks. Replacing the initial distribution while also refitting glyph-only transitions scores 32.56%; its effects additionally involve changed successor likelihoods and row normalization.

## Interior order carries information beyond endpoint counts

The interior-only control fixes every training string's first and last sign and keeps the entire sign multiset, length, site/type, aliases and original component assignment. Across its twenty seeds, 62.47% of training rows changed and 40.10% of training sign positions changed. Short strings with one interior sign cannot move under this intervention. The model's initial distribution and end-transition probabilities remain exactly identical to the unshuffled fit.

| Mask position | Full model | Interior-shuffle mean | All-slot-shuffle mean |
|---|---:|---:|---:|
| Initial | 18.23% | 12.00% | 1.28% |
| Internal | 33.59% | 21.00% | 12.52% |
| Final | 53.95% | 47.65% | 35.60% |

Interior-shuffle top-one ranges from 23.85% to 25.30% across seeds. Its mean difference from the full model is −10.067 points, with component interval −10.817 to −9.333. Internal masks lose 12.588 points, with interval −13.649 to −11.538. The boundary-mask losses arise because their known adjacent signs still interact with transitions learned from the shuffled interiors.

The all-slot control changes 95.12% of training rows and 79.81% of training positions. It disrupts endpoint counts as well as interior order. Top-one ranges from 14.18% to 15.69%; the mean difference is −19.707 points, with interval −20.680 to −18.769. Fifteen shuffled training rows coincided with held-out strings across the complete set of seeds and folds. These accidental coincidences were recorded after transformation and did not alter a training set or its original split. The interior-only control had none.

The component intervals above resample the per-mask mean across the declared twenty training orders. The seed ranges describe additional sensitivity to the random order transformation. This experiment holds the original grouping and fitting strengths fixed; the earlier corpus-null tests address a different question.

## Frequency and calibration

For the 76 codes with at least twenty benchmark occurrences, full-model top-one is 42.20%, interior-shuffle mean is 30.27%, and all-slot-shuffle mean is 18.46%. For codes occurring 5–19 times, those values are 6.86%, 2.64% and 1.04%. Every singleton remains an unseen training code and receives zero exact successes. The detailed frequency intervals and calibration curves are saved for each variant and replicate.

The full model's overall five-bin calibration error is 2.56%. Its error within true-code frequency strata is 24.95% for singleton targets, 24.68% for targets occurring 2–4 times, 21.03% for targets occurring 5–19 times and 3.10% for common targets. Those diagnostic strata use complete-benchmark truths; they describe which outcomes fail, rather than a rule available before seeing a masked answer. They show why the overall calibration number should be accompanied by a frequency audit. Start masks also have a higher unseen-target rate, 6.39%, than internal masks, 2.26%, or final masks, 2.51%.

## Verification and next experiments

Nine pre-run checks passed, including twenty explicit complete-string likelihood comparisons. The frozen full predictor was reproduced exactly on every query before the interventions. [Independent verification](verification.json) recalculated all **40,045 fixed-variant predictions**, checked correspondence and summaries for **320,360 control predictions**, and recalculated a position/coverage-stratified sample of 1,600 control predictions. Probability and bucket-loss differences were zero at the recorded precision. The [retrospective](RETROSPECTIVE.md) records the implementation and preservation choices.

A useful next protocol would choose start shrinkage independently from transition smoothing inside the existing training folds, with both top-one and log-loss objectives recorded in advance. Another would retain boundary evidence while replacing the transition estimator with the historical Kneser–Ney family. The current fixed scores and per-mask records give those experiments an identifiable comparison. The artificial masks still assume one known missing slot, intact neighbors and known length, as declared in the earlier benchmark.

The reusable [ablation script](../../../src/six_hour/markov_ablation.py) imports the frozen comparator and helper snapshots. Run it with a new output directory and an appropriate protocol in its parent; it refuses to replace an existing endpoint.
