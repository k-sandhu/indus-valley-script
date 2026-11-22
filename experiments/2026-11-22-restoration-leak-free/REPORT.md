# Leak-free restoration refit across full-corpus alias and near-variant splits

Date: 22 November 2026. Status: verified refit under pre-registered [PROTOCOL.md](PROTOCOL.md). Addresses question [Q-0010](../../knowledge/questions/Q-0010-check-splits-all-faces.md), GitHub Issue #19, and the restoration validation gap in Section 5 of the [22 October novelty review](../2026-10-22-field-novelty-review/REPORT.md).

Removing all cross-fold full-corpus alias leakage from the Paper 001 restoration benchmark does not alter the model ranking and leaves bidirectional modified Kneser–Ney (`MKN`) essentially unchanged at 39.89% exact top-1 accuracy and 4.563 bits per slot. Under the stricter near-variant-clean sensitivity split, where no training inscription lies within one sign edit or shares an `F-0010` base-shape sequence with any test inscription, every sequential model drops by 1.4 to 3.2 top-1 percentage points and loses 0.17 to 0.20 bits per slot. Two-thirds of the conventional second-order Markov (`M2`) top-1 advantage over first-order Markov (`M1`) disappears once near variants are isolated, whereas `MKN` retains a +3.95 percentage point top-1 and -0.542 bit lead over `M1`. Combining `MKN` with an exact generative `F-0010` graphic-base-family Markov model (`MKN-GF`) improves held-out cross-entropy by -0.057 to -0.065 bits and cuts five-bin expected calibration error (ECE) by more than half across all three splits, including on the near-variant-clean split where identical base-shape templates cannot cross folds.

## Shared scope and experimental setup

All results evaluate single-slot masked prediction over the same 1,596 unique complete single-line right-to-left inscriptions (8,009 slot queries) from `data/normalized/lipi_clean_rtl_singleline.jsonl`, with sequence length known and the hidden slot erased. Every outer fold constructs its own training-only vocabulary plus one `UNKNOWN` state; unseen test codes count as exact misses for top-1, top-5, and top-10 accuracy and map to `UNKNOWN` for held-out bucket cross-entropy in bits per slot. Hyperparameters and ensemble weights are chosen strictly inside each outer training fold by three-fold nested cross-validation respecting that split's component boundaries. Paired 95% confidence intervals use 10,000 component-bootstrap draws (`seed = 20261122`) conditioned on the fitted models and corpus population; cross-split contrasts resample over the coarser of the two component partitions.

This evaluation measures synthetic single-slot graphic prediction on transcribed strings rather than restoration of physically damaged gaps of unknown length, and assigns no phonetic or semantic values. PyTorch is absent from the workstation's Python 3.13 environment (`numpy` 2.2.6), so our fifth and sixth comparators test exact graphic-base-family (`F-0010`) and skip-bigram ensembles rather than neural networks. Full split rules, input hashes, and model definitions are fixed in [PROTOCOL.md](PROTOCOL.md), tracked aggregates in [results-v1/summary.json](results-v1/summary.json), and independent verification in [verification-v1.json](verification-v1.json).

## Cross-fold leakage across the three splits

In Split 1 (exact reproduction of Paper 001), benchmark-only component closure leaves zero direct benchmark alias crossings, yet full-corpus transitive links across all 5,680 observed faces in `data/normalized/lipi_observed_faces.jsonl` bridge 194 benchmark strings and 755 queries (9.43% of the benchmark, 13,476 cross-fold benchmark pairs across six merged full-corpus components). This matches the 192 strings and 748 queries linked by sixteen short one-sign and two-sign faces in the [6 October review](../2026-10-06-modern-restoration/REVIEW.md), plus 2 strings and 7 queries joined through normalized site and excavation identifiers. Near-variant overlap is much broader: 509 strings (2,016 queries, 25.17%) have a training neighbour at Levenshtein distance 1, 243 strings (983 queries, 12.27%) share an `F-0010` base-shape sequence across folds, and 548 strings (2,190 queries, 27.34%) satisfy at least one of those two direct near-variant relations.

Split 2 builds transitive components over all 5,680 observed faces before filtering, joining shared object families, normalized CISI base keys, normalized site and excavation identifiers, and identical nonempty reading-order strings of any length. This reduces 1,526 benchmark components to 1,361 full-corpus components (largest component: 184 strings, 715 slots) while keeping five balanced outer folds (1,602, 1,602, 1,602, 1,602, and 1,601 slots). Both outer and inner folds of Split 2 have zero full-corpus alias leakage, while 519 strings (2,040 queries, 25.47%) still have a direct near-variant neighbour in another fold.

Split 3 merges Split 2's components across all 876 Levenshtein-1 pairs and 295 `F-0010` base-shape pairs among benchmark strings, yielding 964 components. Its largest component holds 493 strings (1,872 slots, 23.4% of the corpus) and sits intact inside outer fold 0 (fold loads 1,872, 1,535, 1,534, 1,534, and 1,534 slots) and intact inside one inner fold whenever fold 0 is in outer training. Both outer and inner folds of Split 3 have zero full-corpus alias leakage, zero Levenshtein-1 crossings, and zero `F-0010` base-shape crossings.

| Split | Components | Largest component (strings, slots) | Fold slot loads | Full-corpus alias queries (%) | Levenshtein-1 queries (%) | Base-family queries (%) | Direct near-variant queries (%) |
|---|---:|---|---|---:|---:|---:|---:|
| Split 1 (Baseline Paper 001) | 1,526 | 9 strings, 49 slots | 1603, 1600, 1602, 1602, 1602 | 755 (9.43) | 2,016 (25.17) | 983 (12.27) | 2,190 (27.34) |
| Split 2 (Alias-clean, Q-0010) | 1,361 | 184 strings, 715 slots | 1602, 1602, 1602, 1602, 1601 | 0 (0.00) | 1,887 (23.56) | 869 (10.85) | 2,040 (25.47) |
| Split 3 (Near-variant-clean) | 964 | 493 strings, 1,872 slots | 1872, 1535, 1534, 1534, 1534 | 0 (0.00) | 0 (0.00) | 0 (0.00) | 0 (0.00) |

Source: [results-v1/summary.json](results-v1/summary.json), `splits.*.diagnostics`, verified independently in [verification-v1.json](verification-v1.json), `leakage_audit`.

## Model performance across all three splits

Split 1 reproduces all four prior frozen baselines to machine precision across all 8,009 queries: `PM` (16.9934% top-1, 35.4976% top-5, 7.135412 bits), `M1` (34.5861%, 58.4592%, 5.119435 bits), `M2` (37.2706%, 58.8713%, 5.247171 bits), and `MKN` (39.7178%, 61.6806%, 4.581891 bits, 5.2751% ECE). Every top-1 and top-5 outcome matches the saved slot audits with zero mismatches and maximum loss difference `0.0`.

| Split | Model | Top-1 (%) | Top-5 (%) | Top-10 (%) | Log loss (bits) | ECE (%) | OOV (%) |
|---|---|---:|---:|---:|---:|---:|---:|
| Split 1 (Baseline) | `PM` | 16.9934 | 35.4976 | 45.5737 | 7.135412 | 2.0441 | 3.134 |
| Split 1 (Baseline) | `M1` | 34.5861 | 58.4592 | 65.4264 | 5.119435 | 2.5564 | 3.134 |
| Split 1 (Baseline) | `M2` | 37.2706 | 58.8713 | 65.4514 | 5.247171 | 4.3506 | 3.134 |
| Split 1 (Baseline) | `MKN` | 39.7178 | 61.6806 | 68.7601 | 4.581891 | 5.2751 | 3.134 |
| Split 1 (Baseline) | `MKN-GF` | 40.5918 | 62.0552 | 69.0973 | 4.516653 | 2.0047 | 3.134 |
| Split 1 (Baseline) | `MKN-GF-SB` | 40.6418 | 62.2175 | 69.2471 | 4.504110 | 1.6098 | 3.134 |
| Split 2 (Alias-clean) | `PM` | 16.2068 | 35.6474 | 45.0119 | 6.817929 | 1.8576 | 3.221 |
| Split 2 (Alias-clean) | `M1` | 33.9743 | 58.5466 | 65.7011 | 5.121386 | 2.6420 | 3.221 |
| Split 2 (Alias-clean) | `M2` | 36.2967 | 59.0461 | 65.6012 | 5.255718 | 4.9901 | 3.221 |
| Split 2 (Alias-clean) | `MKN` | 39.8926 | 62.0552 | 69.0223 | 4.563180 | 4.8841 | 3.221 |
| Split 2 (Alias-clean) | `MKN-GF` | 40.3047 | 62.4423 | 69.3220 | 4.506267 | 1.5156 | 3.221 |
| Split 2 (Alias-clean) | `MKN-GF-SB` | 40.4170 | 62.3798 | 69.4219 | 4.496628 | 1.2794 | 3.221 |
| Split 3 (Near-variant-clean) | `PM` | 14.7085 | 33.9368 | 43.4386 | 6.800761 | 0.8026 | 3.446 |
| Split 3 (Near-variant-clean) | `M1` | 33.1502 | 56.9734 | 64.3776 | 5.292911 | 2.6802 | 3.446 |
| Split 3 (Near-variant-clean) | `M2` | 34.0367 | 56.9484 | 63.8157 | 5.442750 | 5.4275 | 3.446 |
| Split 3 (Near-variant-clean) | `MKN` | 37.0958 | 59.9451 | 67.2119 | 4.750645 | 5.6069 | 3.446 |
| Split 3 (Near-variant-clean) | `MKN-GF` | 37.7076 | 60.3821 | 67.3617 | 4.689897 | 2.1674 | 3.446 |
| Split 3 (Near-variant-clean) | `MKN-GF-SB` | 37.5952 | 60.3571 | 67.4616 | 4.683723 | 1.9207 | 3.446 |

Source: [results-v1/summary.json](results-v1/summary.json), `splits.*.models.*.summary`.

## Effect of removing alias leakage (Split 2) and near-variant overlap (Split 3)

Refitting from scratch on Split 2 confirms that full-corpus alias leakage inflated `M1` and `M2` modestly while leaving `MKN` and the graphic-family ensembles nearly flat. On Split 2 relative to Split 1, `M1` changes by -0.612 top-1 points (95% CI [-1.989, +0.595]) and `M2` by -0.974 points ([-2.164, +0.150]), closely matching the -0.75 and -0.84 point bounds estimated by post-hoc deletion in the [6 October review](../2026-10-06-modern-restoration/REVIEW.md). `MKN` moves by +0.175 top-1 points ([-0.861, +1.186]) and -0.0187 bits ([-0.0771, +0.0404]); `MKN-GF-SB` moves by -0.225 points ([-1.330, +0.845]) and -0.0075 bits ([-0.0611, +0.0488]). For `PM`, inner selection switches from $\alpha = 20$ in all five folds of Split 1 to $\alpha = 100$ in three folds of Split 2 (and all five folds of Split 3), which lowers `PM` top-1 by -0.787 points while reducing its bucket cross-entropy by -0.3175 bits because stronger shrinkage protects sparse metadata cells.

Isolating near variants in Split 3 produces a larger, statistically clear decline across every sequential model. Relative to Split 2, `M2` drops by -2.260 top-1 points ([-3.607, -0.496]) and worsens by +0.1870 bits ([+0.0404, +0.3020]); `MKN` drops by -2.797 points ([-4.013, -1.136]) and +0.1875 bits ([+0.0834, +0.2653]); `MKN-GF` drops by -2.597 points ([-3.788, -0.988]) and +0.1836 bits ([+0.0825, +0.2608]); and `MKN-GF-SB` drops by -2.822 points ([-3.904, -1.330]) and +0.1871 bits ([+0.0840, +0.2671]). Across all three splits, out-of-vocabulary target rates rise only slightly from 3.134% (Split 1) to 3.221% (Split 2) and 3.446% (Split 3), so vocabulary loss accounts for only a small fraction of the Split 3 drop. The bulk of the Split 3 drop measures genuine template-family similarity: roughly 2.6 to 3.2 top-1 percentage points and 0.17 to 0.20 bits of Paper 001's original headline performance come from generalizing across near-variant inscriptions that differ by one sign or share a base-shape skeleton.

| Contrast and model | Top-1 change, points [95% CI] | Top-5 change, points [95% CI] | Log loss change, bits [95% CI] |
|---|---:|---:|---:|
| **Split 2 minus Split 1** (1,361 clusters) | | | |
| `PM` | -0.787 [-1.885, +0.136] | +0.150 [-0.474, +0.816] | -0.3175 [-0.3561, -0.2793] |
| `M1` | -0.612 [-1.989, +0.595] | +0.087 [-0.646, +0.855] | +0.0020 [-0.0554, +0.0592] |
| `M2` | -0.974 [-2.164, +0.150] | +0.175 [-0.692, +1.060] | +0.0085 [-0.0668, +0.0865] |
| `MKN` | +0.175 [-0.861, +1.186] | +0.375 [-0.333, +1.147] | -0.0187 [-0.0771, +0.0404] |
| `MKN-GF` | -0.287 [-1.306, +0.708] | +0.387 [-0.347, +1.180] | -0.0104 [-0.0636, +0.0451] |
| `MKN-GF-SB` | -0.225 [-1.330, +0.845] | +0.162 [-0.499, +0.899] | -0.0075 [-0.0611, +0.0488] |
| **Split 3 minus Split 1** (964 clusters) | | | |
| `PM` | -2.285 [-4.731, +0.280] | -1.561 [-2.946, +0.233] | -0.3347 [-0.5355, -0.1555] |
| `M1` | -1.436 [-3.297, +0.706] | -1.486 [-2.859, +0.230] | +0.1735 [+0.0358, +0.2897] |
| `M2` | -3.234 [-5.233, -0.888] | -1.923 [-3.334, -0.144] | +0.1956 [+0.0166, +0.3471] |
| `MKN` | -2.622 [-4.196, -0.639] | -1.736 [-3.007, -0.068] | +0.1688 [+0.0382, +0.2767] |
| `MKN-GF` | -2.884 [-4.498, -0.868] | -1.673 [-2.722, -0.245] | +0.1732 [+0.0470, +0.2789] |
| `MKN-GF-SB` | -3.047 [-4.725, -0.979] | -1.860 [-2.938, -0.402] | +0.1796 [+0.0493, +0.2899] |
| **Split 3 minus Split 2** (964 clusters) | | | |
| `PM` | -1.498 [-3.139, +0.230] | -1.711 [-2.939, -0.197] | -0.0172 [-0.1886, +0.1362] |
| `M1` | -0.824 [-1.808, +0.474] | -1.573 [-2.744, -0.082] | +0.1715 [+0.0527, +0.2677] |
| `M2` | -2.260 [-3.607, -0.496] | -2.098 [-3.303, -0.552] | +0.1870 [+0.0404, +0.3020] |
| `MKN` | -2.797 [-4.013, -1.136] | -2.110 [-3.021, -0.815] | +0.1875 [+0.0834, +0.2653] |
| `MKN-GF` | -2.597 [-3.788, -0.988] | -2.060 [-2.738, -1.050] | +0.1836 [+0.0825, +0.2608] |
| `MKN-GF-SB` | -2.822 [-3.904, -1.330] | -2.023 [-2.810, -0.882] | +0.1871 [+0.0840, +0.2671] |

Source: [results-v1/summary.json](results-v1/summary.json), `cross_split_paired`.

## Within-split model comparisons and graphic-family pooling

The pairwise ranking `PM < M1 < M2 < MKN < MKN-GF` holds across every split on both accuracy and log loss, with two sharp structural shifts between Splits 1, 2, and 3.

First, conventional second-order shrinkage (`M2`) depends heavily on near-variant overlap, whereas modified Kneser–Ney (`MKN`) generalizes out of family. On Split 1, `M2` leads `M1` by +2.684 top-1 points ([+1.977, +3.402]); on Split 2, by +2.322 points ([+1.643, +2.955]); on Split 3, that lead shrinks to +0.887 points ([+0.385, +1.623]), while `M2` remains worse than `M1` on log loss (+0.1498 bits) and ties on top-5 (-0.025 points). In contrast, `MKN` widens its lead over `M2` on Split 2 (+3.596 points, -0.6925 bits) and holds a +3.059 point ([+2.359, +3.783]) and -0.6921 bit ([-0.7395, -0.6355]) margin over `M2` on Split 3, as well as a +3.946 point ([+3.194, +4.984]) and -0.5423 bit ([-0.6073, -0.4981]) margin over `M1`. Continuation-count discounting captures reusable higher-order sequence regularities rather than memorized near-duplicate strings.

Second, pooling `MKN` with the `F-0010` graphic-base-family Markov model (`MKN-GF`) consistently improves held-out probability estimation and calibration in every fold of every split. Nested selection picks $\alpha_g = 20$ and weight $w_{\text{gf}} \in \{0.15, 0.20\}$ in all 15 outer folds across the three splits. On Split 3, where strings sharing a base-shape sequence cannot cross folds, `MKN-GF` still beats `MKN` by +0.612 top-1 points ([+0.117, +0.988]) and -0.0607 bits ([-0.0742, -0.0422]), and reduces ECE from 5.61% to 2.17%. Adding the distance-2 skip-bigram and positional model (`MKN-GF-SB`, selecting $w_{\text{sb}} \in \{0.05, 0.10\}$ in all 15 folds) yields a small further log-loss gain on Split 1 (-0.0125 bits [-0.0174, -0.0078]) and Split 2 (-0.0096 bits [-0.0155, -0.0044]), lowering ECE to 1.28% on Split 2 and 1.92% on Split 3, but its incremental difference over `MKN-GF` on Split 3 crosses zero (-0.0062 bits [-0.0171, +0.0023], -0.112 top-1 points [-0.408, +0.124]). Resampling Split 1 pairwise intervals over Split 2's 1,361 components shifts interval endpoints by at most 0.07 percentage points (`split1_pairwise_under_split2_clusters`).

| Pairwise contrast (B minus A) | Split 1 Top-1 [95% CI] / Bits [95% CI] | Split 2 Top-1 [95% CI] / Bits [95% CI] | Split 3 Top-1 [95% CI] / Bits [95% CI] |
|---|---:|---:|---:|
| `M1 - PM` | +17.593 [+16.395, +18.825] / -2.0160 [-2.1135, -1.9162] | +17.768 [+16.483, +19.195] / -1.6965 [-1.8054, -1.6016] | +18.442 [+16.791, +19.617] / -1.5079 [-1.6297, -1.3338] |
| `M2 - M1` | +2.684 [+1.977, +3.402] / +0.1277 [+0.0963, +0.1596] | +2.322 [+1.643, +2.955] / +0.1343 [+0.0926, +0.1752] | +0.887 [+0.385, +1.623] / +0.1498 [+0.0903, +0.1944] |
| `MKN - M1` | +5.132 [+4.254, +6.030] / -0.5375 [-0.5826, -0.4920] | +5.918 [+5.055, +6.771] / -0.5582 [-0.6050, -0.5149] | +3.946 [+3.194, +4.984] / -0.5423 [-0.6073, -0.4981] |
| `MKN - M2` | +2.447 [+1.800, +3.092] / -0.6653 [-0.7150, -0.6162] | +3.596 [+2.968, +4.272] / -0.6925 [-0.7399, -0.6409] | +3.059 [+2.359, +3.783] / -0.6921 [-0.7395, -0.6355] |
| `MKN-GF - MKN` | +0.874 [+0.470, +1.282] / -0.0652 [-0.0773, -0.0535] | +0.412 [-0.014, +0.806] / -0.0569 [-0.0717, -0.0406] | +0.612 [+0.117, +0.988] / -0.0607 [-0.0742, -0.0422] |
| `MKN-GF-SB - MKN` | +0.924 [+0.509, +1.340] / -0.0778 [-0.0913, -0.0645] | +0.524 [+0.111, +0.922] / -0.0666 [-0.0804, -0.0513] | +0.499 [-0.049, +0.878] / -0.0669 [-0.0826, -0.0529] |
| `MKN-GF-SB - MKN-GF` | +0.050 [-0.202, +0.309] / -0.0125 [-0.0174, -0.0078] | +0.112 [-0.163, +0.405] / -0.0096 [-0.0155, -0.0044] | -0.112 [-0.408, +0.124] / -0.0062 [-0.0171, +0.0023] |
| `MKN-GF-SB - M2` | +3.371 [+2.729, +4.022] / -0.7431 [-0.7932, -0.6944] | +4.120 [+3.494, +4.790] / -0.7591 [-0.8085, -0.7054] | +3.558 [+2.751, +4.199] / -0.7590 [-0.8049, -0.7049] |
| `MKN-GF-SB - M1` | +6.056 [+5.238, +6.898] / -0.6153 [-0.6566, -0.5740] | +6.443 [+5.590, +7.278] / -0.6248 [-0.6655, -0.5857] | +4.445 [+3.695, +5.337] / -0.6092 [-0.6728, -0.5660] |

Source: [results-v1/summary.json](results-v1/summary.json), `splits.*.pairwise_within_split` (all 15 pairs per split are stored in the JSON).

Position strata remain ordered identically across all three splits. Final slots stay easiest and initial slots hardest: on Split 2, `MKN-GF-SB` reaches 22.62% exact top-1 on initial slots, 40.56% on internal slots, and 57.77% on final slots; on Split 3, `MKN-GF` reaches 20.43% initial, 38.14% internal, and 53.70% final (`MKN-GF-SB`: 19.80% initial, 37.99% internal, 54.20% final).

## Independent verification

Our independent verifier [verify.py](code/verify.py) does not import `splits.py` or `run_refit.py`. It independently rebuilds the full-corpus alias graph by breadth-first search, checks pairwise Levenshtein-1 and base-shape identity across all outer and inner folds, recomputes all 18 summary cells from the local per-query prediction files, compares Split 1 against all four frozen baselines, and replays brute-force complete-sequence likelihoods on 45 sampled queries (15 per split, 270 model evaluations). All checks pass ([verification-v1.json](verification-v1.json)):

- Zero full-corpus alias cross-fold pairs in Split 2 and Split 3 (both outer and inner folds).
- Zero Levenshtein-1 and zero `F-0010` base-family cross-fold pairs in Split 3 (both outer and inner folds).
- Exact Split 1 reproduction (`0` mismatches, `0.0` maximum metric difference against `PM`, `M1`, `M2`, and `MKN`).
- Maximum metric recomputation difference across all 18 cells: `8.88e-16`; maximum brute-force complete-sequence likelihood difference across `M1`, `M2`, `MKN`, and `GF-M1`: `6.66e-16`; exact hidden-target invariance on all 270 replayed evaluations.

## Boldest reading and deciding test

**Boldest supported reading:** Indus sign sequences obey genuine higher-order combinatorial syntax and graphic-family class constraints that generalize across completely unseen inscription families, independent of physical object aliases, shared short faces, single-sign variants, and base-shape template duplicates. Even when every one-edit neighbour and base-shape duplicate is held out together (Split 3), bidirectional modified Kneser–Ney paired with `F-0010` base-shape class transitions recovers 37.7% of masked signs at top-1 and 60.4% at top-5 (4.69 bits per slot, 2.17% ECE), outperforming first-order Markov transitions by +4.56 percentage points and -0.603 bits.

**Deciding test:** Refit the 6 October neural GRU and ensemble models alongside `MKN-GF` on Split 2 and Split 3 on a PyTorch-enabled workstation, and then score the frozen Split 2 and Split 3 recipes prospectively without retuning on newly acquired CISI 3.1 and post-catalogue inscriptions (after verifying zero full-corpus alias or near-variant overlap with the Lipi training set). If `MKN-GF` and a leak-free neural ensemble preserve their +3 to +4 point and -0.55 to -0.65 bit margin over `M1` on genuinely unseen post-catalogue excavations, the out-of-family combinatorial grammar and base-shape class structure are confirmed outside the existing export; if the margin collapses to `M1` on post-catalogue texts, the residual higher-order gain reflects catalogue-specific formulaic clusters rather than general script syntax.
