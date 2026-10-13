# Category prediction with word boundaries concealed

Written after inspecting `run-v1` and before the new calculations. The original category control supplies source word segmentation. IVS does not supply independently established word boundaries. This follow-up changes the prediction unit to anonymous sign-readings or glyphs while retaining the original outputs.

For each legible source record, expand each word's source category over the reading/glyph units that write that word. The predictor receives the complete anonymous unit sequence, position and length, but no word boundaries, word identities, glosses or written-unit category markers. Training category labels remain available, as in the original supervised calibration. This asks whether those categories can be predicted on held-out source groups with a weaker observation set.

Use whole Sumerian tablets/seals, whole Akkadian tablets/seals, complete Linear B documents and the Egyptian complete-glyph sentence extension. Retain only unit-sequence lengths 3–12. Also report the cuneiform/Linear B natural-line extensions separately. Preserve source text/physical aliases and exact complete unit-sequence closure before five folds. The models, seed, smoothing, feature bins and frequency/position/label-shuffle comparisons remain those specified in COHORT-SPEC.md. UNKNOWN category targets are counted and excluded from scores.

Require the flattened word-unit groups to equal the source unit sequence exactly. Save that alignment audit and every fold and prediction locally. A category such as NAME marks units within a source-tagged name, not a recovered sound or an independently discovered word boundary. Greek's classes remain SYLLABIC, LOGOGRAM and NUMBER; its task does not acquire a personal-name key from this transformation. The Egyptian extension remains a sentence rather than a complete vessel or seal.

The amendment is an exploratory refinement motivated by the initial word-level outcome and its observation advantage. Write it to `sign-control-v1` without replacing run-v1, the normalized records or any earlier project result.
