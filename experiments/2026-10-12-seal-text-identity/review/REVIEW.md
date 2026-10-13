# Adversarial review of the seal-text identity study

Claude Opus 5.5 subagent, 12 October 2026, read-only, with scratch scripts under `data/raw/2026-10-12-seal-text-identity/review/` (local). It reviewed REPORT.md as it stood at 17:06, including Amendment 2. The text below is the reviewer's returned report, saved unchanged except for this header. The [response](RESPONSE.md) records the changes.

## Verdict

The arithmetic holds: about 40 numbers in REPORT.md match the JSON outputs, the protocol and input hashes match, and the coincidence calculation is correct. Several statements and interpretations are not supported, though. The pooled locality statistic is dominated by Mohenjo-daro, and it hides a strong local excess of duplicates at Harappa and the smaller sites. "At most about 15%" is a point estimate presented as a bound. The S5 paragraph contains factual errors. The S3 bias direction is asserted without support, and the S4 concordance comes entirely from unicorn pairs. The frozen-rule outcomes themselves are unchanged: S1 stays "pan-site", S3 stays below tenfold and S4 stays below threshold. The headline and the hypothesis table need rewording before integration.

## Findings, most severe first

**1. The locality result is not uniform across sites: duplicates are at chance at Mohenjo-daro and clearly local elsewhere.**
- **Evidence.** I split the 183 duplicate pairs by site under the length-stratified null of Amendment 2:
  - Mohenjo-daro–Mohenjo-daro: 59 pairs against 60.4 expected.
  - Harappa–Harappa: 10 against 6.0.
  - All other sites: 7 same-site pairs against 1.5 expected (p = 0.002). Under the frozen global null it is 7 against 0.85 (p = 0.0002).
  - Restricted to the 513 seals outside Mohenjo-daro, S1 gives L = 0.413 against 0.248 (p = 0.023). Pair-weighted it is 0.415 against 0.234 (p = 0.016).
  - The local groups are three Banawali seals sharing one text (B-5, B-7, B-15) plus a second Banawali pair, two Dholavira pairs, Lothal L-35/L-55 and eight Harappa texts.
- **Consequence.** "Seals that carry the same text are distributed among cities as seals in general are" holds only for Mohenjo-daro. The Amendment 2 model, where a uniform fraction of pairs is always local, misdescribes a pattern concentrated at the smaller sites. The pooled statistic also mixes many chance coincidences into the test. S3 expects 97.2 of the 122 two-sign pairs from sequencing alone. For texts of three or more signs, the length-stratified ratio is 1.29 (p = 0.060, 29 texts).
- **Caveats to state with it.** The analysis is post hoc and the counts are small. Dholavira 128.1 and 4225.1 have the same motif and near-identical dimensions but come from different source sets, so they may be one seal catalogued twice; without both Dholavira pairs the count is 5 against about 1.5. The three Banawali seals share period II.
- **Remedy.** Add a dated exploratory amendment with this site-class breakdown. Revise the first heading, the "one owner" table row and the conclusion paragraph.

**2. "At most about 15%" is a point estimate, and it is computed in the wrong unit.**
- **Evidence.** f = (0.473 − 0.382)/(1 − 0.382) is the point estimate, and it uses the text-weighted statistic while the text calls it "pairs". I simulated a mixture of wholly local texts with the length-stratified null. The observed L remains compatible up to f ≈ 0.30 (P = 0.043 at 0.30, 0.011 at 0.35). The pair-weighted point estimate is 0.07.
- **Evidence (merged variants).** The Mayig-merged sensitivity is quoted only under the global null (ratio 1.07). Under the length-stratified null it gives 0.479 against 0.393, ratio 1.22, p = 0.026, so merging variants does not remove the excess.
- **Consequence.** The conclusion paragraph and `registry-entry.json` overstate how tightly the data exclude local owners.
- **Remedy.** Report f ≈ 0.15 of shared texts with an upper value near 0.30. Report the merged result under both nulls.

**3. The S5 paragraph contains factual errors.**
- **"In every case the matching seals come from another site" is false for 3 of the 16 rows.** The Mohenjo-daro tags M-2010 (2408.1), M-429 (2923.1) and M-1388 (3683.1) match Mohenjo-daro seals: 2 of 5 matching seals for 003-390 and 4 of 7 for 003-156. The code's `other_site_matches` counts any other-site seal, not all. `registry-entry.json` repeats the error.
- **The ten Lothal records 2093–2102 are CISI L-161 to L-170,** ten catalogue objects with different dimensions and excavation numbers. Only L-161 carries "Layer 2".
- **The 16 rows are 6 distinct texts,** and 10 of the rows are the one M-895 text.
- **The REPORT describes "the same three signs" for a four-sign text** (four signs; codes in the local Lipi record for CISI L-161). L-161_A shows four graphic units: the U-shaped sign, the bracketed strokes, a heart-shaped sign, and a tall stem at the right. The heart and the stem are probably two signs.
- **M-895 is a fragment** (vertical dimension recorded as 0; the photographs show only the upper part, with a striated band below the text). "If the motif records are right" is a fair hedge. It should add that the unicorn code may itself be the cataloguer's inference from a fragment.
- **Remedy.** Correct the count to 13 of 16 rows (4 of 6 texts) matching only other-site seals, give the L-161–L-170 range, and describe four signs.

**4. The stated direction of S3's bias is unsupported, and the ratio depends on the training set.**
- **Evidence (bias direction).** I simulated deduplicated corpora from the fitted bigram, refitted the KN model and compared expectations. The refit underestimates the true expectation for four or more signs: mean 0.93, range 0.69–1.10 over 12 replicates. Deduplication and discounting flatten the model, which is the opposite of "upper estimate".
- **Evidence (training set).** Fitting to distinct seal texts only gives a ratio of 3.1; fitting to non-seal texts gives 4.2; the reported fit gives 5.3.
- **Consequence.** The tenfold verdict holds in every variant. The sentence calling the ratio "a lower one" wrongly implies the true ratio could exceed tenfold.
- **Remedy.** Replace that sentence and give the 3.1–5.3 range.

**5. S4 misdescribes its statistic, and the concordance comes only from unicorns.**
- **"72.6% of pairs" is the mean of per-text shares.** The actual pair share is 89 of 130 (68.5%) against 61.6%, p = 0.149, from the frozen output.
- **All concordance is unicorn–unicorn.** Of the 42 pairs involving a non-unicorn seal, one shares its motif. Of the 11 pairs where both seals carry non-unicorn motifs, the only match is H-352/H-354 ("Bult"). Banawali's shared text (817-002) appears with four different animals.
- **"None" is not missing data.** 231 of the 276 seals coded "None" are rectangular text-only seals (SEAL:R). Treated as a category, pair concordance is 0.547 against 0.436 (p = 0.017).
- **Consequence.** "Somewhat more than chance" overstates. The non-unicorn evidence counts against text–emblem bundling, which matters for the clan row.
- **Remedy.** Report the pair share, the unicorn decomposition and the "None" handling.

**6. The hypothesis table adds a description after the outcomes without marking it, and drops one prediction.** The row "Personal names, duplicates as common names" is not in the frozen protocol, yet it is the row marked "Compatible" and it carries the conclusion. It should be labelled as a post-outcome refinement. The clan row omits its frozen S3 prediction, "reuse above the model", which the 5.3-fold result meets.

**7. S2 quotes the text-weighted statistic where the protocol wording asks for the pair share.** The protocol specifies "the share of within-Mohenjo-daro duplicate pairs whose period labels agree". That is 13 of 19 (0.684) against 0.458 (ratio 1.49, p = 0.051). The REPORT quotes 0.50 against 0.46 instead. Duplicates at Mohenjo-daro lean contemporaneous, which bears on the one-owner reading.

**8. Amendment 1 reporting is incomplete, though the conclusion stands.**
- The pair-weighted version the amendment specified is omitted. It shows opening and closing pairs equal (1.11 against 1.12). Single opening and closing signs are local by pair weight (1.10, p = 0.010; 1.07, p = 0.021), which contradicts "show no locality".
- The amendment's literal rule is met: opening L = 0.598 is above its 97.5th percentile (0.568), and closing L = 0.534 is below its own (0.539). The REPORT rightly declines to apply it but should say so.
- The bootstrap resamples the two group sets independently, although 401 seals belong to both, and it holds the null mean fixed. A permutation null for the difference gives −0.21 to 0.22 (observed 0.13, p = 0.12), so "not established" holds.

**9. Provenance and verification claims are weak.**
- `PROTOCOL.sha256` was written at 16:56 and rewritten at 17:04, after `summary.json` (16:53). The package is untracked, so the freeze rests only on file mtimes (PROTOCOL.md 16:52).
- `verify.py` imports `kn_bigram`, `FOREIGN` and `NO_MOTIF` from `analysis.py` and checks the DP only up to length 2. "Recomputes them by separate code" overstates what it does.
- The one-face rule misses one Harappa duplicate: 033-700 on the second faces of H-352, H-354 and H-369. H-352 and H-354 match on both faces and share a findspot. Their photographs differ, so they appear to be separate objects.

## Checks that found no problem

- **Hashes.** The protocol, amendment and input hashes match.
- **Filters.** The filters implement the protocol. No sealings are coded as SEAL: tags carry no bosses, and the clay seals have bosses. The foreign-site list is correct, and 15 Unknown-site faces are excluded.
- **Null calibration.** The null mean matches the exact hypergeometric value (0.4478).
- **Other stratifications.** Stratifying the S1 null by object type or by unicorn/other/none motif class leaves the ratio unchanged (1.04, 1.06).
- **Within-city spatial test.** There is no area-level locality within Mohenjo-daro: 0.408 against 0.363 (p = 0.30) across DK-G, HR, VS and the other excavation areas.
- **S3 mechanics.** KN rows normalize, the empty-text mass is removed by length normalization, and the squared-transition DP is correct for all lengths.
- **Photographs.** M-712 matches its description. L-161 and M-895 show the same signs in the same order.
- **Numbers.** All spot-checked numbers match: eligibility and group counts, S1 by length, S2, Amendment 2 values, every S3 row, the S4 figures, the S5 record and CISI links, the Amendment 1 values and the 917-of-1,430 limitation.
- **Overclaiming.** There are no claims about meaning, language or decipherment.

Publication note, 13 October 2026: one code sequence was replaced by a pointer; the original review is preserved locally.
