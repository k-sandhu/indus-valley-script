# Auditable missing-glyph prediction

Registered 2026-10-01 23:57:17 UTC (file creation timestamp) before restoration outcomes. This extends the published Markov-restoration approach; prediction of a catalogue sign is not reading a word.

Purpose: establish how reliably a structural model can suggest one missing glyph when the exact missing-slot count and the surviving transcription are known. Real eroded sections may contain multiple signs, so a `000` code does not establish this premise. Never overwrite a transcription or describe a suggestion as an authenticated restoration.

Main benchmark: one deterministic representative per globally identical complete right-to-left text of length at least three. Group physical artifacts and identical texts in outer five-fold evaluation. Mask every position in each held-out sequence, keeping surviving signs. Fit a length/position/site/type baseline and compare a bidirectional local-context model. Hyperparameter grids are fixed; select by grouped inner training folds. Training vocabularies only: an unseen glyph is counted as a failed exact prediction, with unknown-bucket rate reported separately. Report top-one, top-five and top-ten accuracy, broken down by initial/internal/final position, and cluster-bootstrap uncertainty.

The bidirectional model scores a candidate by the forward conditional factor at its slot and, if a following sign exists, the forward conditional probability of that next sign given the candidate. Normalize scores over the training vocabulary plus the unknown bucket. This is a local factorization with known surrounding glyphs, not a semantic model.

Smoothing grid: 20, 100, 500, 2000. Choose each model's value by exact top-one accuracy over all masked slots in three grouped inner training folds; ties choose stronger smoothing. Out-of-vocabulary truths are failures. Confidence will be presented as normalized model mass, not empirically guaranteed correctness. Bucket cross-entropy is descriptive only because unseen fine glyphs share an unknown bucket.

External source check: hold out every Lipi text represented by the primary-photo compatibility audit, along with all physical artifacts sharing those texts. Evaluate the complete, right-to-left, single-line compatible cases separately. Those cases were selected for audit, not sampled at random. Candidate compatibility is weaker than fine-glyph identity; this secondary benchmark cannot establish population accuracy.

Deliver a command-line predictor accepting Wells codes, site and object type, printing ranked alternatives and explicit assumptions. Include a symbolic nonidentifiability demonstration: changing a hypothetical sound/meaning assignment without changing sign codes leaves every structural likelihood and restoration unchanged. No language identification or accepted decipherment will be inferred from accuracy.
