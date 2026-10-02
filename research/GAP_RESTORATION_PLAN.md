# Unknown-length gap experiment

Exploratory extension written after source review rejected single-P000 as proof of a single lost glyph, and before these outputs. Creation time is preserved in the final manifest.

Use the same alias-preserving unique complete RTL texts and five physical/text component folds as the single-slot restoration benchmark. Freeze PM and PMB alpha20, previously selected in the single-slot task. For each held-out text, erase ONE internal contiguous span of k glyphs, with k sampled uniformly from1..min(3,L-2), then uniformly choose a valid internal start. Seed20261012. Give the predictor only the surviving left/right glyphs and site/type, never original length or hidden content.

For candidate k=1,2,3, compute exact marginal probability of the surviving graphic sequence by summing over all hidden-state paths of the normalized length/position/metadata Markov model. Multiply by a training-only length prior: half-count global lengths1..max(32,max_training_length), with site/type distribution shrunk to this global prior at alpha20. Normalize over the declared candidate counts. Compare a factored PM model under the same length prior. This count posterior is uncalibrated model mass, not certainty about an archaeological gap.

Report exact count accuracy, confusion matrix, empirical mass calibration, OOV surviving signs, and paired artifact/text-component bootstrap interval. The count sampling distribution is a benchmark design, not an archaeological prior. No glyph identity or word is reconstructed by this count test. Unknowns in the model's alphabet are one common bucket; actual damaged spans may be longer than three or contain separators.

Independently validate forward marginalization by exhaustive enumeration on a tiny alphabet and check invariance when hidden truth or original length is changed outside the predictor input. Only source cases with independently assessed physical bounds may be queried; existing catalogue unknown-unit counts are corroborating hypotheses, not gold truth.
