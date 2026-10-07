# Frozen-loader verification refinement

Written 7 October 2026 after the first frozen-loader smoke test. Status: Exploratory verification refinement. The model, selection, configurations, fitted weights and benchmark outcomes remain fixed.

The first smoke test compared probabilities from a three-string batch with those from one changed string. Its maximum difference was 6.994603918286657e-08. That comparison changed both the hidden target and batch dimensions, so it did not isolate hidden replacement. The original [verification record](frozen-inference-verification.json), `maximum_probability_change`, and its local sample and log remain intact.

The revised check first predicts each original string in its own batch. It compares hidden replacements against that same-size reference with exact array equality, and separately compares single-string and three-string batches. Across 21 masks in three strings, every hidden replacement leaves probabilities exactly unchanged. Changing batch dimensions produces a maximum difference of 6.994603918286657e-08, within the declared 1e-6 numerical tolerance. [Refined record](frozen-inference-v2-verification.json), `maximum_probability_change`, `maximum_batch_probability_change` and `hidden_replacement_exactly_unchanged`.
