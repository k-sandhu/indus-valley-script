# Calibrating the project's semantic sign assignments

Recorded 12 October 2026 before any permutation, annealing or transfer outcome in this directory was computed. Claude Opus 5.5 runs this package at the user's request. It owns `experiments/2026-10-12-anchor-calibration/`, `data/raw/2026-10-12-anchor-calibration/` and `knowledge/retrospectives/2026-10-12-anchor-calibration.md`, reads the packages it tests without modifying them, and adds registry and index entries at the end. Codex owns `experiments/2026-10-12-anchor-expansion/` and may still be working in it. The package is written in the git worktree for branch `claude/practical-visvesvaraya-5bcb35`; the tested packages and local corpora are uncommitted files in the main checkout, which the scripts read in place.

## Question

Study A of the [published-claim tests](../2026-10-12-published-claim-tests/sanskrit-key/REPORT.md) placed Yajnadevam's Sanskrit key among frequency-stratified permutations of its own values and found it at the 89.5th percentile under an order-5 Sanskrit model, while true keys on synthetic Indus-shaped corpora stood 27 to 72 permutation standard deviations clear. The [key calibration memo](../../knowledge/directions/key-calibration-2026-10-12.md) asks for the same comparison for semantic maps. The project's own semantic work assigns Sanskrit comparison words, working meanings and positional roles to Wells codes and reports three kinds of support: lexical windows and dictionary intersections, role coherence in complete inscriptions, and coverage of inscription slots. This package asks, for each frozen assignment, whether those statistics depend on which sign received which assignment, how far the same freedom can push them, and whether fitted role constraints transfer between halves of the corpus.

The published values were seen before this protocol was written. The permutation, bound and transfer values were not.

## Shared population, strata and splits

The population is the 1,859 distinct reading-order strings of the anchor-expansion complete frame: 2,930 complete, clean, single-line Lipi faces of length at least two, deduplicated by string after object and text closure. Strings, closure components and the published 70/30 discovery/transfer labels are read from the local companion `data/raw/2026-10-12-anchor-expansion/context/run-v2/complete-records.json` (SHA-256 `63bfb74e…a962f`), whose strings must equal those of `data/normalized/lipi_clean_rtl_singleline.jsonl` (SHA-256 `9e539dae…84ba8`). Reading order follows `signs_reading_rtl`.

Sign-frequency strata are the eight token-count bins of the published-claim tests (1, 2–3, 4–7, 8–15, 16–31, 32–63, 64–127, ≥128), counted over the 1,859 strings. Codes absent from the strings form a separate zero stratum; permuting them changes no statistic. Every null permutes assignments only among codes that already hold one, within a stratum, so the multiset of assignments in each stratum is kept. Random draws use NumPy's `default_rng` from a `SeedSequence` with entropy 20261012 and a fixed spawn key per study; seeds are written with the outputs.

The half split for transfer assigns each closure component to half H1 or H2 by whether the first byte of SHA-256(`indus-anchor-calibration-2026-10-12-half-v1|<component_id>`) is below 128. Identical strings and faces of one object therefore stay in one half. A near-duplicate control repeats every transfer evaluation after removing evaluation-half strings that lie within one substitution, insertion or deletion of, or are contained in, a string of the fitting half.

## Study R: role coherence of the anchor-expansion family map

The assignment is the frozen visual map `experiments/2026-10-12-anchor-expansion/visual/families.json` (SHA-256 `022db17e…a6a3`): 673 Wells codes in 70 families, each family with one declared role. Fifty-three families, holding 539 codes, declare a constrained role; seventeen are unconstrained. Role definitions, analytic bag-shuffle expectations and the two-split directional rule are those of the [context protocol](../2026-10-12-anchor-expansion/context/PROTOCOL.md): closing (last, or directly before terminal W400/W740), counted entity (immediately after W001–W005), non-final, internal and opening. These definitions refer to fixed codes and stay fixed when family labels move.

The statistics are:

- **R1**, the number of constrained families with at least five containing strings, nonempty discovery and transfer frames, and matching tokens above the analytic expectation in both (published: 21 of 53);
- **R2**, the number of constrained-family member codes meeting the same rule with their own counts under their family's role (published: 62 of 539);
- **R3**, the total excess, the sum over constrained families of matching minus expected tokens in all 1,859 strings;
- **R4**, each constrained family's own excess in all strings;
- **R5**, the number of strings containing at least one constrained-family token in which every such token matches its family's role, which is the whole-inscription compatibility of the semantic walks, with the number of strings containing any contradiction;
- **R6**, coverage: tokens held by constrained-family codes, and tokens held by codes that meet the R2 rule. Tokens held by any family are invariant under this null by construction and are reported as such.

The null permutes family labels among the 673 assigned codes within strata, 1,000 times; each family keeps its role and its number of members in each stratum. The achievable bound maximizes each statistic over the same swaps. R2 and R3 are sums over codes of a quantity that depends only on the role a code receives, so their maxima are found exactly by linear assignment within each stratum. R1 and R5 are not additive; their bounds come from simulated annealing over within-stratum swaps, four restarts from permuted starts, with ties in R1 broken by a secondary term worth less than one family. A single-family bound gives each family the largest excess its stratum counts allow when it alone chooses members.

Transfer fits the map on H1 by exact assignment maximizing R3 on H1 strings, with roles fixed, and scores R3 and the number of constrained families with positive excess on H2 against 1,000 within-stratum permutations scored on H2. The published map is scored on H2 against the same null. Both directions are run. A sensitivity also lets each family choose the role with the largest H1 excess, alternating with membership refits for five rounds, before scoring on H2.

## Study P: positional statistics of the October 11 leading codes

The [adversarial review](../2026-10-11-bonta-adversarial/REPORT.md) reports final-position z values with fixed analytic moments for its leading codes and uses them as support for carrier, comb and panel meanings: W151, W154, W156, W158, W161, W400, W527 and W617 as closing or final, and W142 as non-final. When a single meaning moves to another code of the same stratum, the null distribution of its statistic is the distribution over that stratum's codes, so it is computed exactly rather than sampled. For each named code the study reports its final z (its negative for W142) and closing-block share, its rank among the codes of its stratum, the share of stratum codes at or above it, and the stratum maximum as the bound. The published z values must be reproduced first.

## Study L: lexical windows of the Bonta extension

The assignment is the seed map of the October 9 search (`run-2026-10-09-v2`, reused byte for byte in v5): 134 Wells codes with nonempty SLP1 value lists, 117 inherited from Bonta's Table 18 through the frozen first-coder crosswalk and 17 new anchor codes with one preferred and one alternative probe each. Each seeded code carries its pair of preferred and alternative value lists as one unit. The search is the published one: two- and three-sign windows with exactly one unseeded code, at most 80 value combinations, residuals of one to six SLP1 letters containing a vowel, exact and normalized matching against 194,059 Monier-Williams headwords (`dictionary-index.json`, SHA-256 `f6c42b48…546a`).

The statistics are those of `search-summary.json` and the catalogue builder: searched unknown codes, unknown codes in new-anchor windows, distinct new-anchor windows, codes with several contexts, codes with a nonempty full intersection in each scenario (published 164 and 158), codes with a residual of at least two exact contexts in the top five of both scenarios, and the mean support fraction of each code's top residual. For the post-outcome refinements W233 → ati, W231 → sam and W204 → sa the study also tracks the support of the published residual and of the top residual for those codes.

Null L1 permutes value pairs among the 134 seeded codes within strata, 1,000 times; the seeded set and therefore the window frame stay fixed. Null L2 keeps the 117 inherited codes fixed and moves each of the 17 new-anchor value pairs to a random unseeded code of the same stratum, 1,000 times; it asks whether the chosen anchor codes open more windows or intersections than frequency-matched codes. The bound anneals within-stratum swaps among the 134 seeded codes to maximize preferred-scenario full intersections and, separately, the both-scenario repeated-residual count. A reimplementation of the search with cached dictionary queries must reproduce the published counts exactly and agree with the original `lexical_search` on several permuted assignments before it is used.

## Reporting and decision rules

For each statistic the report gives the published value, the null mean, standard deviation and range, the permutation p = (1 + number of draws at or above the published value)/1,001, the published value's z in null standard deviations, the bound and the share of the achievable gain that the published value reaches, (published − null mean)/(bound − null mean).

1. A statistic supplies no assignment-specific support when p > 0.01: rearranging the same assignments within strata produces it as often.
2. When p ≤ 0.01 the statistic depends on which code received which assignment. Its share of the achievable gain then shows whether the corpus singles out the published assignment within its own freedom.
3. Per-family results in R4 use the same p, with Benjamini–Hochberg adjustment across the 53 constrained families.
4. Fitted constraints transfer when the H1 fit scores above the 99th percentile of the null on H2. If the H1 fit's H2 z exceeds that of the published map, a fit made on half the texts with no reference to pictures or meanings recovers more transferable order structure than the published roles.

Role statistics are functions of the code-to-role mapping alone, as the anchor-expansion builder notes for item and issuer readings of the same family. Any meaning labels that preserve that mapping score identically, so these statistics can show that order structure exists and how much of it a map captures, and cannot by themselves select a meaning. Lexical statistics depend on Sanskrit value strings and so do test the lexical assignment, with the caveat, measured in Study A of the published-claim tests, that dictionary completion has very low redundancy.

## Outputs and storage

Code, this protocol, aggregate JSON outputs and the report are kept in this directory. Fitted and permuted code-to-family maps are project-generated and public. Per-string compatibility lists, near-duplicate lists, per-draw arrays and any file containing complete inscription strings or dictionary witnesses stay under `data/raw/2026-10-12-anchor-calibration/`, which Git ignores. Any change to this design after outcomes is recorded in a dated amendment, and earlier outputs stay unchanged. No CI/CD, deployment or recurring automation is added.
