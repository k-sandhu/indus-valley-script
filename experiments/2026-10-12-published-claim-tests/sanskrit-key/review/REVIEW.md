# Adversarial review of Study A

Claude Opus 5.5 subagent, 12 October 2026, read-only with scratch scripts r1–r11 under `data/raw/2026-10-12-decipherment-claim-tests/review/` (local). It reviewed REPORT.md as it stood after Amendment 3. The text below is the reviewer's returned report, saved unchanged except for this header. The [response](RESPONSE.md) records what was changed.

**Verdict.** Study A's main conclusions hold, and none of the problems below changes a decision-rule outcome. The emulated acceptance criterion has almost no redundancy. The key scores far below held-out Sanskrit. Within-stratum annealing beats it by about 0.6 bits per consonant without deleting material. The key sits 1.2 to 2.1 standard deviations above its permutations, against about 27 for a correct key in the synthetic power test. I found no bug in the Kneser–Ney code or in the key reconstruction. Several headline numbers and sentences still need revision before integration:

- The unconstrained annealing gains are inflated because the optimiser deletes consonants.
- The "random-like" percentile moves to about the 99th under defensible projection or training choices.
- The one-consonant-stem readability comparison only counts texts with empty skeletons, and the stricter DCS result was left out.
- The unicity distance of 1,980 is an upper estimate.
- The report does not credit prior critiques of the unicity argument.

## Findings, by severity

**1. The Stage 3 unconstrained optima gain much of their order gain by turning frequent signs into empty values.** The key leaves 1,049 of the 8,535 sign tokens without a consonant. The eight real-order optima leave 1,898 to 3,905 (22–46%), and the six scrambled-corpus optima leave 4,292 to 5,157 (50–60%). Up to 223 texts end up with no consonant at all and drop out of the score (r3; consonant counts in `stage3/summary.json`: real 6,184–9,242, scrambled 4,141–5,086, key 7,833).
- **What this explains.** The highest real optima are the ones with the fewest consonants (0.69 at 6,308; 0.47 at 8,657). The scrambled fits "beating" the real fits (0.58–0.80 against 0.47–0.69) is a deletion effect, and it contradicts Stage 3g, where real order beats scrambled order (0.19–0.23 against 0.02–0.04) and consonant counts stay at 7,702–7,882.
- **What Amendment 2 missed.** Its check looked only at the rare-class route. Shuffling each optimum's own skeletons still leaves −0.15 to −0.30, against −0.46 for the key, so part of the optima's gain is compositional.
- **Consequence.** Three sentences in the third finding are inflated or misleading: "0.47 to 0.69 … above real Sanskrit text", "0.58 to 0.80 on the scrambled texts" and "0.30 to 0.44 on the real sign order". The decision outcomes still hold, because the 3g optima also exceed the key.
- **Remedy.** Report the consonant count and empty-token share beside every optimum. Use the 3g numbers as the like-for-like evidence in the third finding and in decision rows 2 and 3. Present the unconstrained runs as an upper bound that includes deletion.

**2. The key's position among its permutations depends on reasonable projection and training choices.** The DCS `# text` lines are not uniform:
- Ṛgveda, Atharvaveda and Arthaśāstra lines are unsandhied pausa forms with compounds split, for example "agniḥ pūrvebhiḥ ṛṣibhiḥ īḍyaḥ nūtanaiḥ uta". They supply 36% of training consonants.
- Rāmāyaṇa, Manusmṛti and Śatapatha lines are sandhied, for example "śrutvaitān ṛṣayo dharmān".

I rescored the key and 1,000 frequency-stratified (N1) permutations (r7, r8). The baseline reproduces exactly: share at or above the key 0.105.

| Variant | Key | Permutation mean | Share of permutations at or above key |
|---|---|---|---|
| Baseline | −0.393 | −0.463 | 0.105 |
| Unsandhied texts only | −0.385 | −0.497 | 0.025 |
| Anusvara projected to *m* | −0.338 | −0.458 | 0.011 |
| Both | −0.368 | −0.501 | 0.005 |

Projecting ṃ to *m* is defensible: sandhied texts write word-final *-m* as ṃ, and the key's *an/aṃ* jar sign (902 tokens) is read as *m*. The key is also above independent random strings at Sanskrit frequencies (−0.393 against −0.435).
- **Consequence.** The heading "no more Sanskrit-like than random strings" and the sentence "They score like random strings, and like arbitrary rearrangements" are not robust. Under these variants the key is about 2 standard deviations above its permutations. That is still far below Sanskrit text (+0.38 to +0.43) and far below the 27 standard deviations of a correct synthetic key, so the overall conclusion survives.
- **Remedy.** Add this sensitivity table. Describe the training text as a mixture of sandhied and unsandhied lines. Rephrase the heading as "far below Sanskrit text and within about two standard deviations of rearrangements of its own values".

**3. Stage 2 has a degenerate primary comparison, omits the strongest result, and has no fitted control.**
- **One-consonant stems.** All fifteen single classes are headword skeletons in both lexicons (r9), so every non-empty skeleton is readable. The key's 0.43% failures are exactly its 8 empty-skeleton texts. "99.57% against 99.67%, 76.8% at least as well" therefore only counts texts made entirely of vowel or empty signs.
- **Omitted DCS result.** Under DCS lemmas with two-consonant stems, the key reads 94.8%. The permutation mean is 88.9%, the maximum is 94.1%, and none of the 1,000 permutations reaches the key (`stage2/summary.json`). The rule is "met" only through its 90%-of-median clause. The sentence "buys about two percentage points" leaves this out; the DCS gap is 5.9 points.
- **Fitted control.** Within-stratum hill-climbing for readability (20,000 proposals, a few seconds) reaches 99.0–99.4% (DCS, two-consonant) and 99.6% (Monier-Williams, two-consonant) (r9).
- **Lexicon fairness.** The preprint says roots, grammatical terms and lexicographers' words "should be removed" (`yaj.txt` lines 639–640), but the Monier-Williams k1 lexicon keeps them. The DCS attested-lemma results answer this objection: random strings of 4–16 consonants remain 95–96% readable.
- **Consequence.** The conclusion survives, but the evidence shown is the weaker one.
- **Remedy.** State that one-consonant-stem readability equals a non-empty skeleton. Lead with the DCS numbers. Report the key's above-maximum DCS result together with the fitted-control result. Retitle the first finding "A lexical emulation of the acceptance criterion accepts random strings", since the preprint's own text says an incorrect key yields no words ("mapagakajh", lines 623–629).

**4. The unicity distance of 1,980 rests on an order-5 estimate of redundancy, which understates redundancy.** The preprint's formula reduces to N/ρ, and applying it to the skeleton is consistent, so that part is correct. The problem is the estimate of ρ:
- The report itself calls the full-text order-5 value of 0.573 "near" the preprint's 0.7. Applying the same correction to the skeleton gives ρ of about 0.29 to 0.42, so d is about 790 to 1,120 consonants. That is still above the 473 consonants in the 50 longest texts, but by 1.7 to 2.4 times rather than 4.
- N = 330 includes the preprint's +37 allowance for pooled phonemes in a 48-letter plaintext. The fifteen-class alphabet already absorbs that pooling, so N = 293 is the consistent value (d = 1,758).
- Another preprint version uses N = 439 and d = 627 (quoted in `rag.txt` lines 991–995). The report should name the version it used (the 13 November 2024 RBSI copy).
- The preprint's own sentence "Abjads would require multiplying the signs by the number of vowels" (line 289) directly supports the representation argument but is not cited.
- The clean unique population has only 34 texts of ten or more signs. Across all distinct records, the 50 longest have at least ten signs and carry 504 key consonants (r11). This is minor.
- **Remedy.** Present 1,980 as an upper estimate with the correction range and the N sensitivity. Quote the abjad sentence.

**5. The report does not credit prior critiques of the unicity argument.**
- Raghavendra (arXiv:2608.02999) already showed that a non-linguistic corpus exceeds the claimed distance about 22 times and concluded that "the inequality cannot validate a reading on its own" (`rag.txt` lines 991–1003). According to the project's `key-calibration-2026-10-12.md`, he also reconstructed the search behind this key.
- REPORT.md credits him only for dictionary coverage, gives no arXiv link, and places the credit after the findings.
- A web search also turned up a January 2025 r/IndianHistory critique arguing the distance is far larger than claimed. I saw only the search summary, not the post.
- I found no Sproat critique of this preprint. Sproat (2010) on non-linguistic symbol systems is cited elsewhere in the knowledge base but not here, and the community-proposals memo appears in PROTOCOL.md but not in the report.
- **Remedy.** Add a short related-work paragraph before the findings. Recast the fourth finding's contribution as measuring the redundancy of the representation the key fixes.

**6. The Stage 3f local ranks are biased by letter frequency, and the W002 example mostly reflects that bias.** Ranking by raw log-likelihood favours common classes. Of W002's 1,080 bits as *s*, 519 bits (478 tokens × 1.086) come from *s* being twice as frequent as *v*. Ranked by order gain, the best class for W002 is *j* with an 879-bit deficit, because that ranking favours rare classes instead. Under order-gain ranks the key averages 6.86 against 7.25 (sd 0.15) for five permuted keys, so it is modestly better than its permutations, consistent with finding 2 (r10).
- **Remedy.** Drop or qualify the W002 sentence, and label the 3f paragraph exploratory as Amendment 1 does.

**7. Amendment 2's divergence figures describe a different reading of the key and have no saved output.** The figures "m 32.8%, 0.495 bits" reproduce only when the jar sign always reads *m* (r5). Under the greedy choice that Stage 3 actually scores, *m* is 24.1% and the divergence is 0.313. The optima recompute to 0.26–0.57, not 0.36–0.62. No script or output exists, which conflicts with AGENTS.md's requirement that claims link to exact outputs.
- **Remedy.** Save the check, correct the numbers, and add the deletion check from finding 1.

**8. The half-split transfer is confounded by near-duplicate texts.** 334 of the 927 half-B texts (36%) are within one edit of a half-A text, and 84 are substrings of longer A texts (r10).
- **Why it matters.** The synthetic running-text corpora in Stage 5 lack this structure. That confounds two claims: the 3g transfer (z of 7.7–8.6), and the Stage 5 statement that this level "occurred only under the correct model".
- **Wording.** "Which is what repeated formulae … would produce" is an untested explanation and should be marked as a hypothesis.
- **Remedy.** Split by clusters of texts within one edit of each other and rerun 3g, or give the synthetic corpora a matched near-duplicate structure.

**9. `verify.py` does not verify what the report says it does.**
- **Loose tolerance.** It compares the greedy key score (−0.393) with the exhaustive one (−0.351) at a tolerance of 0.05. These are different estimators, and the check passes only because the tolerance is wide.
- **No separate scoring path.** No step compares the dense-table scoring with `logprob_seq`. I ran that comparison myself and it agrees exactly, so the problem is the claim, not the results.
- **Remedy.** Compare like with like (greedy against greedy, exhaustive against exhaustive) at about 1e-9.

**10. Other wording problems.**
- "That difference cannot rescue the key" should read "does not explain the gap".
- The heading "A correct key would stand far outside its permutations" should be conditioned on a homophonic encoding of running text.
- "So the readings carry no evidence about the key" should say "readability carries no evidence".
- Decision row 1 reads "96.0% lies above … 89.9% to 96.0%"; give 96.02% against 95.97%.
- PROTOCOL.md says "715 sign rows"; the file has 716 rows (714 signs plus 000 and 999).

## Checks that found no problem

- **Key reconstruction.** I emulated the app's csv2json number typing and single-pass `mkregex`. Three signs differ from `resolve_values`, but only one occurs in the corpus (563, one token, same skeleton). The *an/aṃ* handling matches `decipher.csv`. The vowel signs and the inherent-*a* rule do not affect skeletons.
- **Kneser–Ney model.** Probabilities sum to 1 (largest error 1e-16). The dense table equals `logprob_seq` exactly on 300 random and 300 held-out sequences. Base-16 indexing and the start context are correct, and continuation counts are right. Start contexts get non-standard continuation counts at lower orders, but their backoff weight is negligible with 82,311 lines.
- **Start symbol with no end symbol.** Skipping the first consonant puts the key at the 92nd percentile. Using an order-only statistic (gain minus the gain of within-text shuffles) puts it at the 47th: key +0.057, permutation mean +0.061.
- **Readability and redundancy logic.** −log₂P(readable)/L is sound. Near-zero redundancy is supported for both lexicons.
- **Numbers.** About 60 numbers in REPORT.md match their JSON outputs. These include 1,859, 2,930, 577, 7,833, 473, 0.573, 0.167, 0.096, 1,979.6, all Stage 2 shares and intervals, every Stage 3 reference and null value, the 3f, 3g and Stage 5 figures, the Stage 0 counts, and the halves of 932 and 927. The only mismatches are the Amendment 2 figures in finding 7.

Sources named by the reviewer: [Raghavendra, arXiv:2608.02999](https://arxiv.org/pdf/2608.02999); r/IndianHistory thread 1iekde1 (search summary only).
