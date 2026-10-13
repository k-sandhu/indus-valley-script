# Verification of selected structure-first numbers

Recorded 12 October 2026. The verifier wrote `recompute.py` from the definitions in the verification assignment, `PROTOCOL.md` and the three amendment files, without opening the step scripts, `common.py` or `segmenters.py`. After all values were computed, `compare.py` read the run summaries and wrote `verification.json`, which lists every check with its definition, both values, the summary key and a tolerance of 1e-6 for counts and 1e-3 for ratios. Only `step3-segmentation/linebreaks.py` and the 2d per-class block of `step2-image-text/analyze_step2.py` were read afterwards, to explain the two observations below. Rerun with `python -X utf8 recompute.py` then `python -X utf8 compare.py`.

The inputs reproduce the stated frame: 1,859 distinct clean reading-order texts with 8,535 signs, 5,680 faces, and no attested code missing from either coding table.

## Results

| Check | Quantity | Recomputed | Run | Agree |
|---|---|---|---|---|
| 1 | W types; share once; top-30 token share | 577; 0.37088; 0.57809 | same | yes |
| 1 | B types; share once; top-30 token share | 78; 0.06410; 0.91283 | same | yes |
| 2 | Coder ARI unweighted; token-weighted | 0.88408; 0.97534 | same | yes |
| 3 | 2a copper: texts on 2+ objects; one class | 12; 10 | 12; 10 | yes |
| 4 | 2d: matching hits; seal (text, class) pairs | 3; 1,209 | 3; 1,209 | yes |
| 5 | Line breaks: faces used; line > better order; reverse | 72; 23; 4 | 72; 23; 4 | yes |
| 5 | Sign-test p, better order | 0.000311 | 0.000311 | yes |
| 6 | Numerals: tokens; items with 5+; mean distinct values; weighted top share | 1,265; 56; 3.607; 0.606 | same | yes |
| 7 | Edge asymmetry: IVS; Sumerian seal legends (309 texts) | 0.2598; −0.2037 | 0.2598; −0.2037 | yes |

All assigned values agree, and most agree to floating-point precision. In check 4 the per-class specific n-gram counts and hits also match (Unicorn 2 hits, composite animal 1, the other six shared classes 0; tiger has no class-specific n-gram). Matching seal texts by shared n-gram sets or by contiguous substring gives the same 3 hits. In check 5, treating `len(A) == len(B)` as one window length or as two leaves the face counts unchanged; the one-length reading reproduces the run's mean straddle rates (0.0808 pooled, 0.1222 better order).

## Line rate counts interior lines twice

Two supplementary step 3 figures disagree. The run reports a mean per-face line rate of 0.22917 and a pooled line rate of 0.24818 (34 of 137 line windows). Counting each line of length at least 2 once gives 0.22685 and 0.24060 (32 of 133). `linebreaks.py` collects line windows inside the loop over adjacent line pairs (`for L in (A, B)`), so in the four faces with three or more lines the middle lines enter twice. The recomputation reproduces the run's figures exactly when it counts interior lines twice (`check5_diagnostic_interior_lines_twice` in `my_values.json`). The fault is in the run, and it is small: the face-level counts (23 against 4 for the better order, 25 against 3 pooled) and both p-values are identical under either counting. `step3-segmentation/REPORT.md` cites the affected figures as 22.9% and 24.8%; with each line counted once they are 22.7% and 24.1%.

## Odds ratios for classes without matching hits

The step 2 amendment says classes with no hits now report `null` odds ratios. The code sets `null` only when a class's specific n-grams hit no seal of any class. In the v2 run every shared class hits at least one seal, so all eight report a Haldane odds ratio, including six with no matching hit; the anthropomorph class, with one matching seal text and no hit on it, reports 31.9. These values come from the 0.5 correction and carry no evidence of association. The 2d statistic and its permutation p are unaffected.
