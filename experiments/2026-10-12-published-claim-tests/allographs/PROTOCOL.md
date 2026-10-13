# Study C protocol: allographs and homophones in Yajnadevam's key

Recorded 12 October 2026 by Claude Opus 5.5 before any substitution, neighbour or positional outcome was computed. Before writing it, the author inspected the key table's structure (row types, canonical chains, resolved values), the corpus inventory (record, unique-text, type and token counts, frequency strata) and the sizes of the candidate pair sets listed below. Changes after the first outcome run go in a dated `AMENDMENT-*.md` file in this directory, and earlier outputs stay in place. The parent protocol is `../PROTOCOL.md`.

## The claim and what the corpus can test

Yajnadevam's November 2024 preprint, *A cryptanalytic decipherment of the Indus script* (local text `data/raw/2026-10-12-decipherment-claim-tests/papers/yaj.txt`), states that "Variants of 76 allographs constitute most signs" and that conjunct signs constitute the rest. In the preprint's usage an allograph is a graphically distinct sign carrying a phoneme (section 4.4 gives "a median of three allographs per phoneme"), and each allograph has graphic variants (section 4.14 calls these stylistic and says that "different forms of a single allograph rarely occur together in the same inscription"). Section 4.13 describes stroke-marked jar variants as direction markers, with the first jar in reading order carrying the most strokes and the final jar usually none. Section 4.11 reads conjunct signs as their component signs.

The key table (`data/lipi/src/assets/data/xlits.csv`, `yajnadevam/lipi` commit `fc8813a52e183d19c441631dc26c33a4dccbea39`) encodes the variant relation in its `canonical` column and the phoneme assignment in its `xlit` column. Two signs that the key treats as free graphic variants of one grapheme should be able to replace each other in the same inscription context, and should have similar left-neighbour, right-neighbour and positional distributions, more often than two signs of matched frequency chosen without regard to the key. Signs that the key assigns the same pooled consonant value are, under the preprint's homophonic-cipher model, alternative spellings of one plaintext unit; the classical cryptanalytic signature of homophones is a shared contact (neighbour) distribution. Neither prediction depends on Sanskrit. A graphic-similarity grouping made independently of the key, the Mayig class crosswalk, supplies the comparator: if the key's variant groups add distributional information, the key's variant pairs that fall in different Mayig classes should still beat the frequency-matched null.

Positionally conditioned variants would behave differently. They would rarely substitute in identical frames and would have divergent positional profiles. This is tested as a separate, declared prediction rather than folded into the free-allograph test.

## Inputs and key semantics

The corpus is `data/normalized/lipi_clean_rtl_singleline.jsonl` (2,930 complete single-line records without unknown signs; field `signs_reading_rtl`). The primary analysis population is the 1,859 distinct reading-order sequences, because copies of one text on several objects are not independent substitution evidence. Every unique text has at least two signs. Sign counts are token counts in the analysis population.

Key rows are read as follows, after checking `canonize`, `mkregex` and `xlitize` in `data/lipi/src/pages/index.vue` and `resolveXlit` in `data/lipi/src/pages/glyphs.vue`. Codes `000` and `999` are not signs. A row whose `canonical` equals its `sign` is a base sign. A row whose `canonical` is a different single code is a variant of that code; eight variants point to another variant, so each variant is assigned to its root by following single-code pointers to a base (the pointer relation is a function, so roots are unique). A row whose `canonical` contains hyphens is a ligature; its components in reading order are the hyphen-separated codes reversed, as `mkregex` and `resolveXlit` read them. A sign's value is its own `xlit` if nonempty; otherwise its root's value, or for a ligature the concatenation of its components' values in reading order (`resolveXlit`). The main page's `mkregex` differs for variants whose canonical code has no leading zero, because `json-2-csv` parses such codes as numbers and that branch overwrites a variant's own `xlit` with its canonical's; the number of rows affected is reported, and the homophone primary set uses base signs only, which this difference does not touch.

Pooled value: delete vowels (`a A i I u U e E o O`), map `h` to `s`, and keep the remaining consonant string, matching the key's own pooling of aspirates, retroflexes and sibilants (`decipher.csv`). A sign whose value has no consonant is labelled by its vowel (`a` and `A` merged). Under this rule the key's `an` signs join `n` and its `as` signs join `s`, as preprint section 4.10 states for nasals and sibilants. A strict sensitivity keeps exact `xlit` strings.

The graphic comparator is `data/normalized/mayig_wells_class_crosswalk.json`. Following its stated sensitivity rule, two Wells codes share a Mayig class if and only if their class lists intersect; connected components are not formed. In this file every mapped code has exactly one class, so the rule partitions the 498 mapped codes.

## Pair sets

- **P1, key variant pairs.** All unordered pairs of distinct non-ligature codes with the same root (variant with its base, variant with variant). P1 is split by the comparator into P1-in (both codes mapped to Mayig and sharing a class), P1-out (both mapped, different classes) and P1-unmapped (at least one code without a Mayig class).
- **P2, key homophone pairs.** All unordered pairs of distinct base signs (roots) with identical pooled value. P2 excludes ligatures and is disjoint from P1 by construction.
- **P3, Mayig graphic pairs.** All unordered pairs of distinct Wells codes sharing a Mayig class. P3-only denotes P3 pairs that are not in P1.
- **N, frequency-matched null pairs.** Generated per replicate from each real set, as described below.

A pair is eligible at threshold k when both codes occur at least k times in the analysis population. Thresholds k = 1, 3 and 5 are reported; k = 3 is primary. Pre-outcome sizes at k = 3 are 377 P1 pairs in 58 roots (71 P1-in, 235 P1-out, 71 P1-unmapped), 230 P2 pairs, 80 P3 pairs and 9 P3-only pairs.

## Measures

**Minimal-pair substitution.** For each pair of distinct analysis texts of equal length L ≥ 3 that differ at exactly one position, record the unordered pair of signs at that position. MP(a, b) is the number of such text pairs whose differing signs are a and b. The set statistics are the mean MP per pair and the share of pairs with MP ≥ 1. Texts of length 2 are excluded from MP because their frames contain a single sign; a sensitivity uses L ≥ 2.

**Neighbour divergence.** For each code, count the sign immediately before each of its tokens (or a start symbol) and the sign immediately after (or an end symbol). Each count vector is smoothed toward the corpus-wide context distribution q with a Dirichlet weight β = 1, p = (n + βq)/(N + β). The neighbour divergence of a pair is the mean of the base-2 Jensen–Shannon divergences of the two left distributions and the two right distributions. Sensitivities use β = 0 (maximum likelihood) and contexts whose codes are replaced by their key roots, which favours the key.

**Positional divergence.** Each token is classed as initial, medial or final (a sole class is defined but empty, since no unique text has length 1). Profiles are smoothed toward the corpus-wide profile with β = 1, and the pair statistic is the Jensen–Shannon divergence.

## Null, effect sizes and intervals

The null preserves each set's pair structure and matches each member's frequency. At threshold k, the universe is every code with count ≥ k. Codes are stratified by floor(log₂ count); starting from the highest stratum, any stratum with fewer than five codes is merged into the stratum below it. One replicate draws an independent uniform permutation σ of codes within each stratum and maps every pair (a, b) of the set to (σ(a), σ(b)); the same σ is applied to all sets within a replicate. There are R = 2,000 replicates (NumPy `default_rng(20261012)`).

For a set mean m̄ and its 2,000 null means, the one-sided p-value for the free-allograph direction is (1 + #{null ≥ m̄})/(R + 1) for MP and (1 + #{null ≤ m̄})/(R + 1) for the two divergences. The per-pair null expectation is the mean of that pair's statistic over replicates, and the per-pair excess is the observed value minus that expectation. The set effect is the mean excess, with a 95% percentile interval from 2,000 cluster-bootstrap resamples (seed 20261013). Clusters are roots for P1 and its subsets, pooled values for P2 and Mayig classes for P3 and P3-only, so that a large variant family is not counted as many independent pairs. A naive pair bootstrap is reported beside it. For MP the ratio of the observed mean to the null mean is also reported. P1 is compared with P3, and P1-out with P1-in, by the difference in mean per-pair excess with independent cluster-bootstrap intervals.

## Decision rules

The primary family has eight one-sided tests at k = 3 on the deduplicated population: mean MP and mean neighbour divergence for P1, P1-out, P2 and P3. Holm's procedure controls the family-wise error at 0.05.

1. A set substitutes beyond frequency if its mean-MP test survives Holm, and shares neighbour contexts beyond frequency if its neighbour test survives Holm.
2. The key's variant grouping captures distributional equivalence beyond graphic similarity if P1-out passes at least one of its two primary tests. If P1-out passes neither while P3 or P1-in shows excess, the support for the key's variant groups is confined to pairs that the Mayig classes already group.
3. The key's homophone structure has internal support if P2 passes at least one primary test. Passing would be consistent with a homophonic assignment but would not identify the language or the values; failing means the same-value groups show no corpus-internal sign of interchangeability beyond frequency.
4. Positional divergence forms a second family (P1, P1-out, P2, P3 at k = 3) with two-sided p = min(1, 2·min(p_low, p_high)) and Holm correction. A divergence below the null indicates shared positions; above the null indicates complementary positions, the signature of conditioned variants.

Results at k = 1 and k = 5, with duplicates, with L ≥ 2 frames, with β = 0, with root-collapsed contexts, with a null universe excluding ligature codes, for P2-strict (exact `xlit`) and P2-all (all non-ligature codes of the same pooled value in different roots) are sensitivities. They are reported in full and do not change the primary decisions; a sensitivity that reverses a primary decision is stated next to that decision.

## Declared secondary predictions

**S1, jar direction markers.** Mayig class descriptions give the number of small strokes in the jar mouth: W740 none, W741 one, W742–W744 two, W745–W747 three, W748 four. Among unique texts with at least two of these jar tokens, at least one of them stroked, the preprint predicts that stroke counts do not increase in reading order and that the final jar is the unstroked W740. Under a null that permutes stroke labels among a text's jar tokens, exactly one distinct arrangement of a text's stroke multiset is non-increasing, so the per-text probability is ∏m_j!/n!, and the count of conforming texts follows a Poisson-binomial distribution. The exact upper-tail p-value is reported for both statements (for the second, the per-text probability is the share of W740 among that text's jar tokens). Mean relative position (index/(L − 1)) of stroked and unstroked jar tokens is reported descriptively.

**S2, variant consistency within inscriptions.** For each root with at least two attested codes, excluding the jar root 740 because the preprint assigns its variants a directional function, a unique text containing two or more tokens of that root is mixed if those tokens are not all the same code. The preprint predicts fewer mixed texts than chance. The null permutes codes among all tokens of the same root across the analysis population, keeping positions fixed (2,000 replicates); the lower-tail p-value is reported, with the jar root included as a sensitivity.

**S3, conjunct decomposition.** For each attested ligature λ with reading-order components c₁…c_m and each occurrence of λ in a unique text, replace that token by c₁…c_m and check whether the resulting sequence is itself a unique text. The statistic is the number of such matching occurrences, with the number of ligature types having a match. The null replaces λ by σ(c₁)…σ(c_m) under the stratified permutation at k = 1 (2,000 replicates); the upper-tail p-value is reported. A sensitivity uses the components in written (unreversed) order.

## Inventory figures reported without a test

The number of base signs, variants, chained variants and ligatures in the table; the number of roots attested in the corpus; the number of codes and roots sharing each pooled value; the token share (deduplicated and with duplicates) of codes whose pooled value is shared by at least ten non-ligature codes; the rows whose own value differs from their root's value; and the share of P1 pairs (both mapped) that share a Mayig class.

## Outputs and verification

`allograph_test.py` writes a dated run directory `run-YYYY-MM-DD/` containing `summary.json`, pair-level tables (`pairs_k*.csv`, sign codes and statistics only) and value-group tables, and records the SHA-256 of this protocol and of each input. Full inscription sequences and long example lists go to `data/raw/2026-10-12-decipherment-claim-tests/allographs/`, which is local only; `REPORT.md` may quote a few short minimal-pair examples. `verify.py` recomputes the inventory figures, pair-set sizes, observed set statistics at k = 3, the S1 and S3 observed counts and the primary null p-values with separately written code (brute-force text comparison, SciPy Jensen–Shannon distance, an independent permutation stream with fewer replicates) and records agreement in `verification.json`.

This study evaluates the internal consistency of a published key with corpus distributions. It does not assess the language of the script or any sound value.
