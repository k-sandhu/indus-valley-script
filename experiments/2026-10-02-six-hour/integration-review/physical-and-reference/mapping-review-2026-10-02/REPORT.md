# Paper 004 latent-form integration review

The six-row recovery table, overall counts, reference-CV medians and optimization/audit totals agree with the saved records. The added population-identification section also matches its exact certificates and primary theorem. The coordinating agent completed the single notation edit identified below during review. The [mapping check record](numerical-checks.json) contains 2,383 passing assertions and sixteen source-file hashes; the [identification check record](identification-checks.json) adds 2,057 passing assertions and six source pins. The [starting manuscript snapshot](manuscript-inputs.json) fixes the initial file versions and line numbers; the [completion snapshot](completion-delta.json) records subsequent edits. No fit or bootstrap was rerun.

## Notation edit completed

The starting version of [manuscript Methods 2.6](../../../../../papers/004-reference-model-selection/manuscript.md), line 63, used `(count+3)/(N+60)` without defining its two quantities. The completed edit adds: “Here `count` is a symbol's reference frequency at one slot, and `N` is the number of reference records.” This gives the reader the formula's denominator without having to inspect the control source. No numerical correction was found.

## Recovery and prediction checks

Independent aggregation of the reviewed rows and collapsed-control rows reproduces all six manuscript rows:

| Reference records | Shared mass | Earlier selector | Fixed mixture | Three-model selector | Collapsed profile |
|---:|---:|---:|---:|---:|---:|
| 40 | 0 | 8/24 | 12/24 | 12/24 | 8/24 |
| 40 | .35 | 2/24 | 4/24 | 3/24 | 1/24 |
| 40 | .70 | 0/24 | 0/24 | 0/24 | 0/24 |
| 400 | 0 | 22/24 | 24/24 | 24/24 | 21/24 |
| 400 | .35 | 22/24 | 24/24 | 24/24 | 22/24 |
| 400 | .70 | 16/24 | 18/24 | 16/24 | 17/24 |

Each row contains twelve systems with two encoded-population mixture conditions. Across all 144 conditions, the totals are 82 fixed-mixture recoveries, 79 three-model selections, 70 earlier selections and 85 supplied-label recoveries. Every four-model selection has the same complete-recovery outcome as its three-model counterpart. The selector's chosen model can change in a small-reference case while this complete-map outcome remains unchanged.

At reference size 400, the median mixture-minus-collapsed CV differences recompute as 1,669.36812194, 530.80142888 and -36.47557325 bits for shared mass 0, .35 and .70. Each median uses twelve reference-fit scores, one per system. These round to the manuscript's 1,669.37, 530.80 and -36.48. All large-reference zero/.35 cases select mixture; all large-reference .70 cases select ordinary slot. The saved paired selected-minus-earlier recovery differences are .125, .0625 and zero, with the stated intervals and twelve-system resampling units.

## Fitting and audit scope

The three-component prior and six independent categorical slot profiles are explicit in Methods 2.6. Adding one pseudocount is the MAP update under Dirichlet(2) priors. When three profiles coincide, each component has one third of the expected counts, giving the collapsed slot formula `(count+3)/(N+60)` for twenty categories. The fixed-reference mapping stage retains actual likelihood as its objective.

The saved model list contains 72 full-reference fits and 216 fold fits, for 288 total. Each has eight starts, giving 2,304 individual starts. The maximum iteration count is 150, and 178 starts reach it. Saved mapping traces contain 4,433 updates, matching the contributor's independent dual-certificate count. Every start respects the 25-update mapping budget.

The objective diagnostics contain 62 failed fixed-mixture mappings. Fifty-six returned maps score above truth; six score below it. These reproduce the manuscript's fitted-objective and search-miss counts. Retained near-tie entries contain the returned map itself, with no distinct map inside the declared likelihood tolerance. The manuscript describes the finite retained search and linear subproblem certificates accurately.

The independent contributor audit reports 68,014 checks passed with no failures. The largest selected-assignment Q discrepancy is `1.4551915228366852e-11` nats, correctly rounded to `1.46e-11`. Its scope covers scalar reference-start scores and terminal update equations, reference-fold scores, mapping responsibilities and updates, likelihood bounds and assignment duals. Saved intermediate reference trajectories receive ascent/stopping checks. The manuscript's wording preserves the distinction between saved reference trajectories and certified linear updates.

## Scientific premises and readability

Methods collects the known reference, supplied three-component count, absence of per-record form labels, fixed-reference mapping stage and reused benchmark together. The 144 conditions are post-outcome reuse of twelve systems. Encoded test records and mapping truth remain outside reference selection. The supplied-label comparison retains its stronger input, and the separately specified collapsed control has its own protocol. Those premises carry through the results and claim map.

The results explain the recovery comparison, smoothing control and optimizer failures in consecutive paragraphs. Their comparisons use the same records and retain the earlier outcomes. With the formula definition added, no further correction was found in the current version. The updated abstract's large-reference counts and distinction between fixed mixture and reference-selected outcomes agree with the table.

## Population-identification addition

Methods 2.7 and Results 3.5 accurately specify the fixed three-component product model, positive weights, ordered slot pairs, two population conventions and common component permutation. [Allman, Matias and Rhodes, Corollary 2](https://arxiv.org/pdf/0809.5032v2) states the positive-weight condition with row Kruskal ranks summing to at least `2r+2`; here `r=3` gives eight. Full independence of three rows gives Kruskal rank three. Pair marginalization recovers the original slot distributions, as described by the source's Lemma 14.

Independent determinant expansion reproduces all 288 saved minor certificates: 216 rank-three main matrices and 72 rank-one control matrices. All 144 saved main mixing vectors are positive and sum exactly to one. The 36 parameter profiles and two conventions yield 72 main population profiles. The manuscript carries those counts accurately.

The audit sizes also reconcile: 96 main/control convention profiles times three matrices, three rows and 400 columns give 345,600 entries. Their six twenty-category slot marginals give 34,560 checked values. The two collapsed weight vectors have unit sums and different multisets; identical component factors give equal population laws. The saved support counts include 39 six-symbol slots under the zero-mass threshold convention, matching the described repair. The manuscript preserves that first failure and identifies the population parameters and empirical mapping as distinct evaluated quantities. No correction is needed in this addition.

## Source pins

The complete pin lists are in the two check records. Principal hashes are:

| Source | SHA-256 |
|---|---|
| Main mixture results | `5e1a087288ee3d9f1978549a262aac802a970468e313bcb8878f0a56e24be6e6` |
| Independently reviewed rows | `5289fe94076bb745df1f4a32739a5617c241f45eea9605669a6ab269b56c812b` |
| Primary mixture audit | `517cb6f7897e3dec8763d5d3a6740f52eb3790a0f04671da7f664e73079ca538` |
| Collapsed-control audit | `982bce4b6b9b4fc77aa78eeda63aeee137ca0401b8f5d767500b15f6e33fbb63` |
| Population-identification main | `957eea4b7f9275e5845405410039a5ae3d6e57edb054ce20b41c76d1711ac66d` |
| Collapsed population controls | `1244400b82ea5e4ea322cd9602b19025f72a1365d24a850522a774a640c6fa41` |

This reviewer wrote only this new review directory. Shared manuscripts, source witnesses and earlier review endpoints remain preserved.
