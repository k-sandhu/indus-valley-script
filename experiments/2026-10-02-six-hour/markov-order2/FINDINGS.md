# More exact guesses, greater probability loss

The top-one-selected second-order model correctly restored 37.2706% of the 8,009 masked glyph slots. First order restored 34.5861%. The paired improvement is 2.6845 percentage points, with a component-bootstrap interval of 1.9902–3.3968 points. Bucket cross-entropy increased by 0.1277 bits per slot, with an interval of 0.0965–0.1589. The added context helped choose the most likely code while worsening the probabilities assigned to the observed targets. [Frozen results and contrasts](main/results.json).

| Metric | Local metadata/neighbour model | First order | Second order, top-one selection | Second order, loss selection |
|---|---:|---:|---:|---:|
| Exact top-one | 33.81196% | 34.58609% | 37.27057% | 34.58609% |
| Exact top-five | 55.33775% | 58.45923% | 58.87127% | 58.45923% |
| Exact top-ten | 62.70446% | 65.42640% | 65.45137% | 65.42640% |
| Bucket loss, bits per slot | 5.74773 | 5.11943 | 5.24717 | 5.11943 |
| Five-bin calibration error | 8.04843% | 2.55636% | 4.35062% | 2.55636% |
| Mean exact top-one across code types | 5.13219% | 4.79861% | 6.12345% | 4.79861% |

The top-five difference between second and first order is 0.4120 percentage points, with an interval of −0.0887 to 0.8937. Their top-ten difference is 0.0250 points, with an interval of −0.4207 to 0.4482. Those outcomes concentrate the observed improvement in the first guess. Equal-text top-one rises from 33.3524% to 35.6699%; equal-code top-one rises from 4.7986% to 6.1235%. Rare-code recovery remains low in both models.

## Model and selection

The second-order model counts the next state after each pair of previous states. A row shrinks toward the first-order transition distribution after its latest state. Two start sentinels and an end state supply boundary factors. At a masked slot, the candidate can affect its own factor, the next factor and the factor two positions later. The restorer includes every affected factor before normalization. Replacing the hidden target leaves the prediction unchanged.

The first-order prior has fixed strength 20. Three grouped inner folds select second-order strength from 5, 20, 100, 500, 2,000 and a backoff-only option. Exact top-one selection chose 20, 20, 100, 20 and 20 across the five outer folds. The main run took 71.47 seconds.

After seeing the accuracy/loss tradeoff, a separate protocol retained the model family and grid but minimized inner bucket loss. Every outer fold selected backoff-only. All stored query outcomes then matched the first-order model exactly; the paired accuracy and loss differences are zero. This run took 69.53 seconds. [Separate result](loss-selected/main/results.json). The benchmark was reused during model development, and that status belongs with any published comparison.

An unseen target is scored through the common unknown bucket for loss and remains an exact-code failure for accuracy. Bootstrap draws resample the 1,526 fitted components 10,000 times, using seed 23101. They condition on the saved fits and corpus. They do not refit inner selection or represent transcription uncertainty.

## Verification and related work

An independent implementation reconstructs flat triple and edge counts, then scores each candidate through the entire record likelihood. It checked all 8,009 queries, every target loss, saved candidate masses, correspondence and hidden-target replacement invariance. Maximum loss disagreement was `3.55 × 10⁻¹⁵` bits. The initial review found one query whose lower-ranked floating-point scores changed order. Exact rational likelihoods established two genuine ties; all target top-k outcomes were unchanged. [Original failed check](review/failure.json), [rational-tie review](review-ties/verification.json), [loss-selected review](loss-selected/review/verification.json).

Higher-order Indus n-grams have prior literature. [Yadav and colleagues' author paper](https://arxiv.org/abs/0901.3017) studies conditional probabilities, while a [September 2026 author abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7436801) reports its own trigram comparison. The present result supplies a matched comparison on preserved artifact-held-out masks with two declared selection objectives. An equivalent evaluation of modified Kneser–Ney smoothing, or a different corpus, remains a new experiment.
