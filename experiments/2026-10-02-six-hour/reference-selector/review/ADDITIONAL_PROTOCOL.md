# Paired uncertainty and assignment-alternative checks

The primary review has reproduced all saved choices and likelihoods without a discrepancy. This additional review will summarize paired differences at the generated-system level and examine whether the certified slot assignments have equally scoring alternatives. It is a post-outcome diagnostic of the saved worlds.

Average each algorithm's recovery and held-out losses across the eight conditions within a system. Compare the selector with graph, slot and the supplied-family diagnostic, using 20,000 paired resamples of the twelve systems in each family/inventory. Use seed 7710261002 plus 1,000 per inventory index and 100 per family index; use the same draws for all comparators and outcomes within that group. Preserve the system-level differences and percentile endpoints.

For each independently reconstructed slot matrix, use the saved independent dual potentials to build a directed graph of candidate tight edges. A row points to the row currently assigned its proposed alternative column. A directed cycle yields an alternative bijection. Inspect candidate edges with slack at most 1e-7 bits, then verify each proposed cycle's likelihood equality exactly by cancelling prime factors of integer-smoothed reference counts. Mapping-independent denominators cancel. Retain only exact-equality witnesses and save the changed-code set. Report these as witnessed alternatives; do not add a global uniqueness claim when no witness is found.

Keep the primary endpoint unchanged. Store this diagnostic in a separate endpoint. Its certificate concerns the length/slot objective and its observed reference/training records.
