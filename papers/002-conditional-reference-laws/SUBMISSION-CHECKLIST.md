# Preprint submission checklist for Paper 002

This checklist covers standalone reproduction and human statistical review for [manuscript.md](manuscript.md) (GitHub Issue #16). Every experiment in this paper uses exact finite enumeration or synthetic populations generated from fixed seeds and requires zero restricted third-party corpora.

## 1. Standalone reproduction and independent audit steps

Requirements: Python 3.13 (standard library) and `numpy` (version 2.2.6 in the frozen runs; `matplotlib` is needed only to re-render Figure 1 via `experiments/2026-10-02-six-hour/null-calibration/plots/render.py`). No external data download or Indus corpus file is used anywhere in this package.

Run commands from the repository root. Because the audit scripts below rewrite their deterministic verification JSON files in place, run them in a clean working copy (or check `git status` and `git diff` afterward) so frozen artifacts stay unmodified. Direct any fresh simulation rerun to a new dated directory rather than overwriting frozen outputs.

### Fast exact enumerations and audits (seconds to ~2 minutes each)

```powershell
# 1. Exact binary 8,000-table / 2,880-unique-table space and nested-fit replay
python experiments/2026-10-02-six-hour/null-calibration/verify_result.py exact

# 2. Exact copy-tail integer dynamic program (1 to 5 copies per object)
python experiments/2026-10-02-six-hour/null-calibration/copy-tail-counts/verify.py

# 3. Exact deduplication occupancy recurrence and all 11,520 rational tails
python experiments/2026-10-02-six-hour/null-calibration/dedup-selection/verify.py

# 4. Unequal copy-count continuation-DP sampler and 100,000-draw replay
python experiments/2026-10-02-six-hour/null-calibration/unequal-copy-counts/verify.py

# 5. Exact ordered face-vector sampler (14,040 tables and 200,000 stream draws)
python experiments/2026-10-02-six-hour/null-calibration/noisy-faces/verify.py exact

# 6. Twenty-object fitting-domain counterexample and 8,000-table guard/feasibility audit
python experiments/2026-10-02-six-hour/null-calibration/domain-support/verify.py

# 7. Paired-seed 500-cluster bootstrap audit for literal-copy comparison
python experiments/2026-10-02-six-hour/null-calibration/paired_seed_audit.py

# 8. Symmetric noisy-channel recovery audit (1,000 populations, 6,000 KKT checks, 8 replays)
python experiments/2026-10-02-six-hour/null-calibration/noisy-channel/verify.py

# 9. Shared-quality exact sampler (20,000 draws) and rational adjacent-slot covariances
python src/six_hour/null_quality_verify.py exact
python src/six_hour/null_quality_moments_verify.py

# 10. Post-outcome agreement diagnostic (1,000 populations, 1,547 hypergeometric cells, 2,000 exact tails; ~96 s)
python src/six_hour/null_quality_agreement_verify.py
```

### Full saved-grid independent audits (minutes each)

```powershell
# Main 3,000-population study (928,424 proposals, 396,000 groupings, 33 full fit replays)
python experiments/2026-10-02-six-hour/null-calibration/verify_result.py main

# Imperfect-face 1,000-population study (198,000 references, 15 full fit replays)
python experiments/2026-10-02-six-hour/null-calibration/noisy-faces/verify.py main

# Shared-quality 300-population nested study (59,400 references, 16 full fit replays; ~59 s)
python src/six_hour/null_quality_verify.py main
```

To verify that every headline number and JSON key in [manuscript.md](manuscript.md) matches the frozen files on disk without executing any replay, cross-check [claim-evidence-map.md](claim-evidence-map.md) against the listed JSON paths.

## 2. Human statistician reviewer checklist

### Mathematical derivations to verify

- [ ] **Multinomial sufficiency and permutation multiplicity (Section 2.2, `MATHEMATICS.md`):** confirm that under independent cell-wise categorical draws, conditioning on margin counts `m(v)` yields uniform weight `1 / (n! / ∏ m(v)!)` over distinct arrangements, and uniform row-index permutation assigns identical multiplicity `∏ m(v)!` to every distinct arrangement.
- [ ] **Rejection sampling on unique strings (Sections 2.2 and 3.1):** confirm that rejecting column permutations with duplicate whole strings samples uniformly on `Ω ∩ U` (exact acceptance `2,880/8,000 = 0.36` in the six-row binary example) even when `Ω ∩ U` is not closed as a permutation group.
- [ ] **Deduplication occupancy polynomial (Section 3.2, `dedup-selection/README.md`):** verify that drawing `N = 7` independent strings and conditioning on `k = 6` retained strings with balanced binary column margins weights each retained set `S` proportionally to `∏_{x ∈ S} q(x) · Σ_{x ∈ S} q(x)`, where fixed margins keep the product constant while the occupancy sum varies across the four complementary omitted pairs.
- [ ] **Ordered face-vector factorization (Sections 2.3 and 4.2, `noisy-faces/METHODS.md`):** confirm that conditional independence of face errors given the latent sign implies `r(a, b) = Σ_x p(x) K(a|x) K(b|x)`, making whole-vector permutations exact conditional on joint vector margins while also preserving scalar face margins, and verify `P(Y_1 = Y_2) = (1 − ε)^2 + ε^2/7 = 142/175` at `ε = 0.1`.
- [ ] **Unequal copy-count continuation sampler (Section 3.3, `unequal-copy-counts/PROTOCOL.md`):** verify that sampling column entries sequentially in proportion to dynamic-programming counts of valid completions produces exact probability `1/6` on each of the six doubly constrained columns for weights `[1, 1, 1, 2, 2, 3]`, and review whether the single-seed direct-stream Pearson value (`chi_square = 263.5194`, `df = 215`, `p = 0.01336`) warrants any additional note alongside the exact path probabilities.
- [ ] **Fitting feasibility and selective inference (Section 5, `domain-support/GUARD_PROTOCOL.md`, `SUPPORT_PROTOCOL.md`):** confirm the twenty-object one-component counterexample (`ZeroDivisionError`), the distinction between unconditional rejection under the zero-score extension (`400/8,000 = 5.0000%`) and conditional rejection given feasibility (`400/5,760 = 6.9444%` vs `276/5,760 = 4.7917%`), and the single-string-per-block constructive component lower bound.
- [ ] **Symmetric channel inversion, negative-entry recurrence and identifiability (Section 6, `noisy-channel/PROTOCOL.md`, `IDENTIFICATION.md`):** verify `ε = (7/8)[1 − sqrt((8H − 1)/7)]` on `0 ≤ ε < 7/8`, the penalized EM updates (`Dirichlet(1.5)` and `Beta(1.5, 1.5)`), the exact rational absence-probability calculation predicting 10,331.87 negative inversions across 1,000 populations, and the two-observer attenuation-ratio identification limit under uniform versus nonuniform latent frequencies.
- [ ] **Shared-quality exact weights, covariances and hypergeometric convolution (Sections 6.1–6.2):** confirm the unequal broad-margin weights versus uniform quality-conditioned weights, the rational adjacent-slot covariances (`4,761/7,840,000` single-face vs `142,491,969/24,586,240,000` face-vector), the conditional score mean `(a0 · a1 + a1 · a2)/n`, and the exact middle-column hypergeometric convolution verifying all 1,547 cell distributions.
- [ ] **Linked-seed cluster bootstrap (Section 4.1, `PAIRED_UNCERTAINTY_AMENDMENT.md`):** confirm that clustering the 500 linked trial pairs (`i` and `i + 500`, sharing 49,500 reference seeds across the two methods) properly accounts for cross-method dependence in the 10.5-point paired interval (`8.5–12.6`).

### References and statistical positioning to verify

- [ ] Confirm accurate characterization and citation metadata for the four primary methodological pillars: Phipson and Smyth (2010), Hemerik and Goeman (2018), Winkler et al. (2015) and Hurlbert (1984).
- [ ] Confirm accurate citation of Dawid and Skene (1979), Dempster, Laird and Rubin (1977) and Allman, Matias and Rhodes (2009) in Section 6.
- [ ] Decide whether additional canonical citations from the **selective inference** literature (for conditioning on analysis-feasibility events in Section 5) or the **occupancy sampling** literature (for deduplicated draw weights in Section 3.2) should be added for the target statistics venue.
- [ ] Verify that the abstract, introduction and conclusions remain cleanly bounded as an applied statistical methods paper on explicit short-record derivations and preserved counterexamples, with no overclaim of general asymptotic permutation theory.

### Pre-submission administrative items

- [ ] Supply final author names, affiliations, correspondence details and ORCIDs.
- [ ] Select target preprint server (for example, arXiv `stat.ME` or `stat.AP`) and journal venue; apply venue-specific LaTeX or formatting template.
- [ ] Confirm venue disclosure wording for AI-assisted computation and writing.
- [ ] Confirm public release and archive bundle for the synthetic code snapshots, frozen JSON outputs, audits and Figure 1 files (`plots/main/calibration.png`, `calibration.svg`, `calibration.pdf`, `points.csv`, `figure.json`).
