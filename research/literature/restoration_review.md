# Independent restoration-method review

Reviewed 2 October 2026, read-only. Scope: `src/restoration.py`, the record loading/grouping helpers in `src/methods/conditional_structure.py`, and the saved `results/restoration/benchmark.json`. No source code was changed. Benchmark source SHA-256: `1b81454afac07f6586106403aaaa9c711e901e45304e66a2bc5a94a1a3f8b6e5`; dependency SHA-256: `ed150239452339a04ef35f04b5814a236d9bd3ad0b64702e66a0230760de0ca8`.

## Finding

No hidden target-sign access or train/test overlap was identified in the inspected implementation. The reported gain supports masked graphic-code prediction for this corpus under its stated assumptions. It supplies neither meanings nor sounds.

| Check | Inspection result | Consequence |
|---|---|---|
| Prediction access | `Restorer.distribution` uses slot position, length, metadata stratum, and surviving previous/next signs. It does not read the sign at the masked slot; that sign is used after prediction for scoring. | The prediction does not directly disclose its target. Both neighboring signs are legitimate observed context only when the neighboring transcription is reliable. |
| Vocabulary | Sign inventory and counts are fitted on outer-fold training records. Test-only glyphs fall into an UNKNOWN bucket and fail exact ranking metrics. | Fine-glyph performance is not inflated by a test-vocabulary oracle. Bucket cross-entropy is descriptive and merges multiple unseen glyphs. |
| Duplicate/physical groups | `load_records(unique=True)` retains all physical-object aliases for each repeated text. `group_records` takes the transitive closure of identical text and shared physical-object aliases. Whole components enter a fold together. | Duplicate strings and multiple faces/copies linked by this metadata cannot straddle train/test. Full text is used to prevent leakage, not to tune a test prediction. Missing or incorrect object identifiers remain a corpus limitation. |
| Tuning | Smoothing is selected using three inner folds restricted to outer training data. Five outer folds supply final scores. | The reported test scores are not the tuning criterion. Grid choice and model-family design still reflect researcher choices, as usual. |
| Source audit removal | Primary-compatible test strings and their physical aliases are excluded from training with the same connected-component closure. Explicit assertions check no test-string or test-artifact overlap. | No overlap was found. These exclusions do not turn the selected audit sample into a random external validation set. |
| Baseline | The comparison baseline includes length, exact slot, site/object-type stratum; the local model adds neighboring signs. | The gain is beyond that metadata baseline. It is the contribution of combined local context, not a measurement isolating only one neighbor. |
| Uncertainty | Accuracy gain uses a paired bootstrap over 1,526 artifact/text components rather than independently resampling 8,009 slots. | This respects the main within-object dependence. The interval is conditional on the fitted cross-validation predictions; it does not include retraining or uncertainty over the archaeological sampling process. |
| Interpretation | Output and confidence warnings explicitly prohibit semantic/phonetic readings and calibrated historical probabilities. | Keep these limitations in any headline or deliverable. A high model mass is not a historical probability. |

The saved benchmark reports local top-one accuracy 33.81% versus 16.99% for the metadata baseline across 8,009 masked slots, an absolute gain of 16.82 percentage points. The component-bootstrap 95% interval is 15.64–17.98 points. The score concerns unique, filtered transcriptions of at least three signs; it cannot be generalized without qualification to all inscriptions, illegible signs, uncertain segmentation, missing spans, or arbitrary restored lengths/directions.

The primary-photo compatibility sample contains 16 qualifying texts and 79 masked slots. Its local top-one score is 41.77% versus 18.99%. It was selected nonrandomly and checked for catalogue-family compatibility, which is weaker than independently established fine-glyph identity. It is best reported as a source check. The original 25 source-audit cases and their exclusions should remain visible.

## Historical novelty

[Rao et al. 2009, *PNAS*](https://doi.org/10.1073/pnas.0906237106) already modeled Indus sign sequences with a Markov method, discussed prediction of missing signs, and used a deduplicated text corpus. Missing-sign prediction and text deduplication are therefore established prior. This project's defensible contribution is the particular reproducible benchmark: training-only vocabulary, transitive artifact/text grouping, nested tuning, a metadata-and-position baseline, component-level uncertainty, an explicit nonrandom primary-source compatibility check, and clearly stated restoration assumptions. Do not claim that the Markov method, broad local-order result, or prediction of missing signs itself is new.

## Boundaries for claims and future use

1. Present the result as graphic-code prediction, not a decipherment or a linguisticity test.
2. Preserve the assumption of exactly one masked glyph, correct surviving transcription, line length, and direction. Real damage may violate all four.
3. Keep top-five candidates available and retain image-level ambiguity rather than selecting a visually unsupported top-one restoration.
4. Interpret intervals as conditional component-bootstrap intervals on this benchmark. They do not quantify historical truth or representativeness.
5. Treat newly submitted complete-text predictions as exploratory if the same text or linked artifact is already present in training. The separately held-out benchmark is the evidence for performance.
