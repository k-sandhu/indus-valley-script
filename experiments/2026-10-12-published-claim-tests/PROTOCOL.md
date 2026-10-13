# Tests of published Indus decipherment and usage claims

Recorded 12 October 2026 before any outcome in this directory was computed. Claude Opus 5.5 ran this package unattended at the user's request to pursue new ideas more aggressively. Codex was concurrently running the anchor-expansion, satellite-prospection and transmission-hypothesis packages; this package owns only `experiments/2026-10-12-published-claim-tests/`, `data/raw/2026-10-12-decipherment-claim-tests/` and its own retrospective.

The package converts three published claims into tests that the local corpus can decide or constrain. Study A tests Yajnadevam's Sanskrit sign key and its unicity-distance argument. Study B tests whether Indus-script inscriptions found outside South Asia follow heartland sequence statistics. Study C tests the allograph and homophone structure asserted by the same key against substitution evidence internal to the corpus. The community-proposals memo had already asked whether a proposed mapping predicts material better than competing mappings with the same freedom; no project run had answered it.

## Shared inputs

The corpus is the pinned Lipi export (`yajnadevam/lipi` commit `fc8813a52e183d19c441631dc26c33a4dccbea39`, `inscriptions.csv` SHA-256 `c36d0c26…a272f77dba62c`) as normalized in `data/normalized/lipi_clean_rtl_singleline.jsonl`: complete, single-line records without unknown signs, in reading order. Analyses deduplicate identical reading-order sign sequences unless a study states otherwise, because identical texts on different objects would otherwise be counted as independent evidence. The key file is `data/lipi/src/assets/data/xlits.csv` from the same commit. Source sequences remain local; published outputs are aggregates, authored code and short examples.

## Study A: the Sanskrit key and its unicity argument

### The claim

Yajnadevam's November 2024 preprint, *A cryptanalytic decipherment of the Indus script*, models the corpus as a homophonic cipher with Sanskrit plaintext. It assigns each sign a consonant or vowel value, reads ligatures as their components, supplies vowels and word division during reading, and applies the unicity formula d = N/ρ with N = 330 effective signs and redundancy ρ = 0.7, giving d ≈ 471 characters. It states that reading the 50 inscriptions of length ten or more exceeds this distance, so the readings must carry information from the inscriptions rather than from the key. The local key table has 715 sign rows; many signs share a value (58 signs read `r`, for example), aspirates, retroflexes and all sibilants plus *h* are pooled, and the app inserts an inherent *a* mechanically.

### Representation

The information an inscription fixes under this key is a consonant skeleton. Every Sanskrit form is projected onto fifteen classes matching the key's pooling: k(kh), g(gh), c(ch), j(jh), t(th ṭ ṭh), d(dh ḍ ḍh), n(ṇ ñ ṅ ṃ), p(ph), b(bh), m, y, r(ṛ ṝ), l(ḷ), v, s(ś ṣ s h ḥ). Vowels are deleted. A sign's skeleton is the projection of its key value; a ligature with an empty value takes its components' values in the app's order. Word spaces are deleted in running text because inscriptions mark no word division.

### Stage 0: reproduction audit

Reproduce the app's mechanical transliteration and compare the skeleton of each published reading (`sanskrit` field, SLP1) with the skeleton implied by the key for the same inscription. Report agreement and the kinds of departure. Departures measure reading freedom beyond the table; they do not test the readings.

### Stage 1: redundancy of the representation

Train interpolated Kneser–Ney character models on Digital Corpus of Sanskrit text (commit `8aeed5a1`, Ṛgveda, Atharvaveda Śaunaka, Śatapathabrāhmaṇa, Manusmṛti, Arthaśāstra, Rāmāyaṇa), holding out every tenth chapter file of each text. Report held-out cross-entropy and fractional redundancy ρ = 1 − H/log₂|A| for (i) the full transliteration with vowels and spaces and (ii) the fifteen-class skeleton without spaces. Orders 3, 4 and 5 are reported; order 5 is primary. Recompute the preprint's distance with the measured skeleton redundancy, holding N = 330 as the preprint states.

### Stage 2: readability as the acceptance criterion

The preprint accepts a reading when the inscription can be read as Sanskrit words. Emulate that criterion with lexicons independent of the key: Monier-Williams headwords (Cologne `csl-orig` `mw.txt`) and DCS lemmas. A skeleton is readable if it divides into one or more stem skeletons, each at least m consonants long, with an optional final ending skeleton from {∅, s, m, n, y, t, sy}. The primary setting is m = 1 because the published readings use one-consonant stems; m = 2 is a stricter sensitivity. Report the readable share of unique texts under the key, under 1,000 frequency-stratified permutations of the key's values (null N1), and for random strings drawn from Sanskrit skeleton class frequencies at each length. The criterion's effective redundancy per consonant is −log₂ P(readable at length L)/L.

### Stage 3: sequential Sanskrit-likeness and achievable fit

The primary statistic is order gain: Σ[log₂ P₅(s) − log₂ P₁(s)] / Σ|s| over unique texts, where P₅ is the order-5 skeleton model with a start symbol and P₁ the class unigram model from the same training text. It measures how much better Sanskrit sequencing predicts the skeletons than Sanskrit letter frequencies alone. Raw log-likelihood per consonant is secondary.

1. Place the key among 1,000 permutations of its own value multiset, uniform (N0) and within sign-frequency strata (N1; strata at 1, 2–3, 4–7, 8–15, 16–31, 32–63, 64–127 and ≥128 tokens in the unique-text population).
2. Optimize the order gain by simulated annealing over value swaps between signs, which keeps the key's exact value multiset and therefore less freedom than the preprint used. Eight restarts. Compare the best and median optimum with the key.
3. Repeat the optimization on three order-scrambled corpora in which each text's signs are permuted uniformly. If scrambled optima reach the key's real-order gain, Sanskrit-like sequencing at the key's level does not require the attested sign order.
4. Split unique texts into halves by a hash of the sequence. Optimize on one half and score the other against N1 on that half. This calibrates how much in-sample fit transfers.
5. Secondary, if time allows: give Sanskrit, Latin and Old Tamil the same free assignment (each sign takes one of fifteen labels or no consonant) under models trained on each language's projected text, with labels matched by frequency rank. Compare the share of the gap between N1 and each language's own held-out text that optimization closes.

### Stage 4: random-key demonstration

Using one N1 key fixed by seed before inspection, segment the longest unique texts into Monier-Williams headwords and print their first English glosses. This is a control showing what the acceptance criterion admits; it is not a reading.

### Decision rules

- If the key's readable share lies inside the central 95% of N1, or the N1 median is at least 90% of the key's share, readability gives no key-specific support.
- If swap-optimized keys reach the key's order gain on the real corpus, the key is neither unique nor best under this Sanskrit criterion.
- If scrambled-corpus optima reach the key's real-order gain, its sequential Sanskrit-likeness does not depend on the attested order.
- The recomputed unicity distance is compared with the consonant count of the 50 longest unique texts.

These rules evaluate the evidential argument for the key. They do not decide which language, if any, the script records.

## Study B: inscriptions found outside South Asia

Parpola and others observed that some Indus-script seals from Mesopotamia and the Gulf carry sign sequences unusual in the Indus Valley, which they interpret as local names or language written in Indus signs. Train sign-sequence models on South Asian texts and score texts found in Mesopotamia, Iran, the Gulf and Central Asia against length- and type-matched held-out South Asian texts, with peripheral South Asian sites as a regional comparison. The sub-study records its own frozen protocol before outcomes.

## Study C: allographs and homophones in the key

The preprint states that variants of 76 allographs constitute most signs. True free allographs should substitute for one another in otherwise identical contexts more often than frequency-matched sign pairs. Test the key's canonical-variant pairs and same-value pairs for minimal-pair substitution and neighbour-distribution similarity against frequency-matched random pairs and Mayig graphic-class pairs. The sub-study records its own frozen protocol before outcomes.

## Writing and review

Every assignment and report follows `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. An adversarial review precedes integration. Amendments after outcomes are dated and leave earlier outputs in place.
