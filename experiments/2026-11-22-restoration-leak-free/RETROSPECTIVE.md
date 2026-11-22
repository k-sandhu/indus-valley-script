# Retrospective: leak-free restoration refit

Date: 22 November 2026.

## Approach

We began by checking the 6 October restoration audit, the Paper 001 methods record, and the local Python environment before freezing [PROTOCOL.md](PROTOCOL.md). Because PyTorch is not installed in the workstation's Python 3.13 environment (`numpy` 2.2.6 only), we implemented all four classical Paper 001 and 6 October comparators (`PM`, `M1`, `M2`, `MKN`) in pure NumPy alongside two exact-probability structured ensembles (`MKN-GF` using the `F-0010` base-shape classes, and `MKN-GF-SB` adding distance-2 skip-bigrams and positional priors).

Before freezing the split definitions, we inspected placeholder patterns in `source_cisi` and `metadata.excavation-idno` across all 5,680 faces so that missing-value tokens (`-`, `KLB???`, and the digit-free site prefix `BNL`) would not falsely merge unrelated objects, and confirmed that `sign_components_v1.tsv` covers all 548 benchmark sign codes with zero unmapped signs. We also verified that both Split 2's largest component (715 slots) and Split 3's largest component (1,872 slots) fit cleanly inside a single outer fold and inside a single inner fold during nested three-fold selection.

## Challenges and fixes

1. **Inner-fold leakage risk in naive refits:** Paper 001's original inner-fold helper rebuilt connected components solely from the outer training rows (`group_records(train)`). Reusing that helper on Splits 2 and 3 would have allowed full-corpus short-face aliases or near variants to cross inner validation folds during hyperparameter selection. We fixed this in `code/splits.py` by preserving the precomputed Split 2 and Split 3 component identifiers inside every inner three-fold split, and verified zero inner-fold violations in `code/verify.py`.
2. **Speed of second-order Markov evaluation:** The original `markov_order2.Restorer` evaluated candidate probabilities through Python list comprehensions over the entire training vocabulary at each query slot. We rewrote `M2Restorer` in `code/models.py` using pre-indexed sparse lookup tables keyed by first and second history states, reducing runtime dramatically while reproducing the original `MARKOV-03` predictions with `0.0` maximum floating-point difference on all 8,009 Split 1 queries.
3. **Protocol formula check:** Before running any code, we caught a minor notation slip in the initial draft of `PROTOCOL.md` where the right skip-bigram lift ratio repeated `/ U(x_{i+2})` inside a term already defined as a lift ratio. We corrected the notation before fitting started so the written formula matches `SkipBigramPosModel` exactly.
4. **Absence of PyTorch for neural refits:** Because `torch` is unavailable in this environment, the neural GRU and transformer models from the 6 October study could not be refitted here. Their leak-free refit on Splits 2 and 3 remains an explicit follow-up task on a PyTorch-enabled workstation; the exact fold registers saved under `data/raw/2026-11-22-restoration-leak-free/folds/` make that follow-up directly drop-in compatible.

## Outcomes

All 18 split-by-model fits ran cleanly in 514.1 seconds, and the independent verifier (`code/verify.py`, 17.9 seconds) confirmed zero outer and inner leakage on Splits 2 and 3, exact bit-level Split 1 reproduction against all four frozen baselines, exact recomputation of all 18 summary cells (maximum difference `8.88e-16`), and brute-force complete-sequence likelihood agreement within `6.66e-16` across 270 replayed evaluations. The refit resolves the core validation gap raised in GitHub Issue #19 and Section 5 of the 22 October novelty review: full-corpus alias removal leaves `MKN` and the model ranking intact, near-variant isolation cleanly separates genuine higher-order grammar (`MKN` and `MKN-GF`) from template-dependent trigram shrinkage (`M2`), and `F-0010` base-shape class pooling adds verified out-of-family predictive and calibration gains.
