# Published-claim tests, 12 October 2026

Claude Opus 5.5 ran this package unattended after the user asked for a review of Codex's work, for independent insights and for more aggressive pursuit of ideas. Codex was running its anchor-expansion, satellite, transmission, semantic-comparison and structure-first packages at the same time. This package owned only `experiments/2026-10-12-published-claim-tests/`, `data/raw/2026-10-12-decipherment-claim-tests/` and this file, read other packages' files without modifying them, and added registry, index and README entries at the end.

## Choice of questions

The registry and memos showed many measurements that every candidate system passes and a community-proposals memo asking whether a proposed sign key predicts the corpus better than competing keys with the same freedom. The local Lipi copy turned out to contain the complete key behind Yajnadevam's Sanskrit decipherment (`xlits.csv`, 715 rows, with ligature decompositions and the app's inherent-vowel rule), and his preprint states a numerical unicity-distance argument. That made a decisive test possible with data already held. Two smaller studies were delegated to subagents with distinct directories: inscriptions found outside South Asia (Study B) and the key's allograph and homophone groups (Study C). The protocol was written before outcomes.

## Approach and problems

Study A reconstructed the key's consonant skeletons, measured redundancy on held-out Digital Corpus of Sanskrit text, tested readability against Monier-Williams and DCS lexicons, scored sequential Sanskrit-likeness under an order-5 Kneser–Ney model, and compared the key with frequency-stratified permutations, annealed optima, scrambled-order corpora and a half split. Observable problems and repairs:

- The GitHub contents API truncated the Ṛgveda listing at 1,000 files; a sparse clone of the DCS repository at commit `8aeed5a1` replaced it.
- Academia.edu refused the preprint; the Rare Book Society of India copy (compiled 13 November 2024) was saved locally and its unicity section read directly.
- A timing run showed the key's order gain before the full Stage 3 run. Reference scores (held-out spans, i.i.d. strings, the published readings) were then added and recorded in Amendment 1; decision rules were unchanged.
- The first random-key demonstration chained particles and printed grammatical notes from Monier-Williams. It was revised before rerunning with the same fixed seed; the first output was overwritten and is described, not preserved.
- Verification found that exhaustive choice of the *an/aṃ* reading raises the key from −0.393 to −0.351. A sensitivity gave the same exhaustive choice to 300 permutations; the key stayed at the 90th percentile.
- The free-assignment cross-language stage (3e) failed: optimization put signs on rare classes and Latin reached 8.5 bits per consonant. A first attempt also hung after workers ran out of memory under 20 processes. The failed output is kept; Stage 3g restricts swaps to frequency strata and starts from frequency-matched assignments (Amendment 2). A check showed the original Stage 3 optima did not use the rare-class route.
- Subagents could not write report-type Markdown in their harness. Study C returned its report and retrospective as text, which the coordinating session saved after review.

## Outcomes

Study A met all four frozen decision rules against the key. A lexical emulation of readability accepts 92% to 100% of random strings, the key's order gain (−0.393) sits 1.2 to 2.4 standard deviations above its rearrangements, within-stratum and scrambled-order optima exceed it, and the recomputed unicity distance, an upper estimate, is 1,980 consonants against the 473 of the 50 longest texts. The exploratory power analysis showed what a correct key looks like at this corpus size (27 to 72 permutation standard deviations clear, against 1.2 for the key) and that blind language identification works for some languages and not others. The real corpus transfers equally under Sanskrit, Latin, Old Tamil and Sumerian models. Study B confirmed the published observation about West Asian finds under matched out-of-sample comparison and found that South Asian round seals share the atypicality. Study C found that the key's homophone groups have no substitution support.

An adversarial review of Study A found no implementation bug but ten problems of presentation and design: unconstrained optima that gained by deleting consonants, a percentile that moved from the 89.5th to about the 99th under other training texts or projections, a degenerate one-consonant readability comparison, an upper-estimate unicity distance, under-credited prior critiques, frequency-biased local ranks, unsaved Amendment 2 figures, near-duplicate texts across the half split, a loose verification tolerance and several wording points. Each was addressed with new saved analyses (Amendment 4) and a rewritten report; the conclusions held, with the key's distance from its rearrangements restated as 1.2 to 2.4 standard deviations and its order shown to add nothing. The near-duplicate rerun also showed that synthetic language identification depends on seeds. Review and response are in `experiments/2026-10-12-published-claim-tests/sanskrit-key/review/`.

## Use before repeating

A future phonetic-key claim can be checked with the same scripts by replacing `xlits.csv`: readability against random strings, order gain against within-stratum permutations, the annealed optimum inside the same space, scrambled-order fits and half-split transfer. Re-running readability-style lexical tests on Indus material without these controls repeats a criterion with near-zero redundancy.
