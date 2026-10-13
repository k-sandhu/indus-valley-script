# Study B: Indus-script texts found outside South Asia

Run of 12 October 2026 under the [frozen protocol](PROTOCOL.md) (hashes in [FREEZE-2026-10-12.json](FREEZE-2026-10-12.json)). All numbers come from [run-2026-10-12/summary.json](run-2026-10-12/summary.json) unless marked exploratory. Exploratory numbers come from [run-2026-10-12/exploratory-checks.json](run-2026-10-12/exploratory-checks.json), computed after the frozen outcomes. A Claude Opus 5.5 subagent ran the study; the coordinating session saved this report from its returned text because the subagent's harness blocked report files.

## Findings

**Texts found in Mesopotamia, the Gulf and Iran are much less predictable under South Asian sign statistics than South Asian texts of the same length, medium and damage pattern.** Twenty-eight of the 31 West Asian objects in the local corpus have at least one scorable transition. For each object, u is the probability that its mean bigram surprisal exceeds that of a matched South Asian comparator scored out of sample; it is 0.5 when the object behaves like its comparators. The mean over objects is Ū = 0.770 (95% bootstrap interval 0.660–0.866), and 23 of the 28 objects lie above 0.5. Under the null, Ū falls between 0.391 and 0.609 in 95% of 20,000 matched resamples. None of those resamples reached the observed value, so the one-sided p is 0.00005, the smallest value the draw count allows (Holm-adjusted over the two primary tests: 0.0001). On average the West Asian texts cost 7.12 bits per scored transition against 5.00 for their comparators, an excess of 2.11 bits (1.37–2.80).

**The excess is concentrated on the round and cylinder seals, as Parpola describes.** The 16 scorable West Asian round seals (15 circular and the Susa cylinder) give Ū = 0.870 (0.776–0.945) and an excess of 2.81 bits (1.98–3.56); 15 of the 16 lie above 0.5. The exception is the single-sign Kalba seal (u = 0.39), whose one sign is the "two persons" sign 091. Laursen (2010, pp. 118–119) describes a Kalba seal with a pseudo-"twins" sign; its join to this record was not checked. The 12 other West Asian objects give Ū = 0.637 (0.445–0.813). The round-minus-other difference is 0.233 (0.034–0.442), which meets the protocol's round-seal specificity rule. The five scorable square seals average 0.521. Three of them, from Kish and Nippur, behave like Indus texts (u = 0.10–0.43). The Tello seal (0.93) and the Salut seal with a Gaur motif (0.97) do not.

**The West Asian excess is larger than the variation among South Asian regions.** Each South Asian comparison group was removed from the training pool and scored by the procedure used for the foreign texts. Gujarat/Kutch gives Ū = 0.528 (0.498–0.559) over 417 texts, Eastern Headwaters 0.491 (59), Kalibangan 0.553 (175) and Chanhu-daro, a core-region control, 0.566 (57). The West Asian Ū exceeds each of these by 0.20–0.28, and every interval excludes zero: Gujarat/Kutch 0.242 (0.128–0.343), Eastern Headwaters 0.279 (0.148–0.404), Kalibangan 0.217 (0.099–0.324) and Chanhu-daro 0.204 (0.068–0.333). Restricting both sides to seals gives the same ordering. West Asian seals have Ū = 0.787, against 0.43–0.59 for the four regions' seals, and the differences run from 0.201 to 0.356 with intervals above zero. Regional differences inside South Asia are measurable but small: Gujarat/Kutch seals give 0.567 (0.528–0.606).

**Round seals found in South Asia are also atypical, so the deviation follows the seal type as well as the findspot.** The pre-specified group of 16 South Asian round and cylinder seal faces gives Ū = 0.704 (0.531–0.872). The West Asian round seals exceed it by 0.165 (−0.026 to 0.357), an interval that includes zero. An exploratory split shows that the effect comes from the circular seals. The 10 SEAL:C faces (9 objects) from Mohenjo-daro, Chanhu-daro, Dholavira and Daimabad give Ū = 0.785. Eight of the ten lie between 0.79 and 0.97; the exceptions are the single-sign Daimabad seal (0.02) and a damaged two-sign Mohenjo-daro seal (0.41). The six cylinder faces give 0.570. For the transcriptions in this corpus, this does not reproduce Hunter's 1932 statement, as reported by Laursen, that the Mohenjo-daro circular seals carry sequences well supported in the Indus Valley. The two sets of round seals are not atypical in the same way. South Asian round seals share 7.1% of their transitions with the West Asian round seals, no more than length-matched South Asian non-round seals do (7.2%; exploratory E4, 7 unique complete round texts).

**The unusual feature is the ordering of common signs.** The secondary measures, Holm-corrected within H1, rank as follows:

| Measure | Ū over 28 objects (interval) | Holm p |
|---|---|---|
| Unseen transitions | 0.739 (0.644–0.830) | 0.0002 |
| Unsupported span | 0.703 (0.598–0.799) | 0.0002 |
| No terminal 740 | 0.606 (0.529–0.672), 22 objects with a known end | 0.032 |
| Rare signs | 0.578 (0.500–0.660) | 0.032 |

The unsupported span is the share of the longest legible span not covered by a run attested in South Asia. For the round seals, rare signs give 0.574 with Holm p = 0.063. The signs themselves are mostly common South Asian signs; their pairings and positions are not. Parpola's 2005 description, common Indus signs in dissimilar sequences, matches this pattern.

The positional counts show the same thing. Three of the 22 West Asian texts with a known end finish with the jar sign 740, against 34.9% of their matched comparators; for round seals the count is 1 of 13 against 38.5%. None of the 22 texts with a known start begins with one of the three most frequent South Asian initial signs (817, 820, 861), against 23.8% of comparators. Four of those 22 begin with 091, against 0.08% of comparators and 5 of 2,122 unique complete South Asian texts. All four are round seals: Luristan, two from Karzakan, and the single-sign Kalba seal. None of the 15 complete West Asian texts repeats a South Asian text exactly, whereas 19.7% of their matched comparators recur on another South Asian object.

**The decisions do not depend on the model, comparator definition, transcription subset or witness choice.** Across the eight pre-specified sensitivities, Ū for all West Asian objects stays between 0.754 and 0.805 and Ū for round seals between 0.854 and 0.932. Every one-sided p is at most 0.0001.

| Sensitivity | All West Asian Ū (n) | Round Ū (n) |
|---|---|---|
| S1 clean texts only, clean training | 0.804 (12) | 0.932 (7) |
| S2 trigram | 0.760 (28) | 0.875 (16) |
| S3 Witten–Bell bigram | 0.762 (28) | 0.864 (16) |
| S4 square-seal comparators | 0.769 (28) | 0.868 (16) |
| S5 any-object comparators | 0.801 (28) | 0.891 (16) |
| S6 better of forward and reversed reading, for every text | 0.778 (28) | 0.858 (16) |
| S7 Dilmun witness instead of Ur 3898.1 | 0.769 (28) | 0.868 (16) |
| S8 leave one site out (range) | 0.754–0.805 | 0.854–0.901 |

Two exploratory checks address artefacts of the setup. Grouping by object family and identical text chains 1,595 South Asian faces, mostly Harappa tablets, into one cross-validation component. Using only comparators outside it gives Ū = 0.762 and 0.867 (E1). Mapping Wells codes to the 331 Mayig graphic classes merges sign variants and reduces the alphabet from 713 to 547 symbols, counting the end symbol; it gives Ū = 0.757 and 0.859, and South Asian round seals 0.720 (E5).

**The Central Asian and unprovenanced texts fall on opposite sides.** The three Central Asian square seals (Altyn Depe, Shortughai, Gonur Depe) give Ū = 0.403. This agrees with Parpola's description of the Gonur seal as carrying native Harappan sequences. The six scorable unprovenanced round seals give Ū = 0.906 (0.843–0.961). One of them (3889.1) contains adjacent 740–740, the combination Parpola (2005, p. 47) reports on a round seal probably from Mesopotamia. Whether 3889.1 is that seal was not established. In South Asia, adjacent 740–740 occurs once, on a damaged Dholavira square seal (4205.1), and in no unique complete text. No West Asian text contains it.

| Group | n | Ū (95% interval) | Excess, bits per transition |
|---|---:|---|---|
| West Asia, all (H1) | 28 | 0.770 (0.660–0.866) | 2.11 (1.37–2.80) |
| West Asia, round seals (H2) | 16 | 0.870 (0.776–0.945) | 2.81 (1.98–3.56) |
| West Asia, round seals: Gulf and Mesopotamia / Iran | 13 / 3 | 0.847 (0.739–0.936) / 0.966 | 2.64 / 3.58 |
| West Asia, other objects | 12 | 0.637 (0.445–0.813) | 1.16 (0.10–2.17) |
| Gulf / Mesopotamia / Iran | 14 / 10 / 4 | 0.808 / 0.670 / 0.884 | 2.29 / 1.50 / 2.98 |
| Central Asia | 3 | 0.403 | −0.59 |
| Unprovenanced round seals | 6 | 0.906 (0.843–0.961) | 3.29 |
| South Asian round and cylinder seals | 16 | 0.704 (0.531–0.872) | 1.56 (0.27–2.94) |
| Gujarat/Kutch | 417 | 0.528 (0.498–0.559) | 0.15 |
| Eastern Headwaters | 59 | 0.491 (0.415–0.568) | 0.01 |
| Kalibangan | 175 | 0.553 (0.506–0.599) | 0.30 |
| Chanhu-daro (control) | 57 | 0.566 (0.481–0.648) | 0.33 |
| Baluchistan/Makran | 6 | 0.612 (0.366–0.818) | 0.50 |

Per-object values, without sign sequences, are in [run-2026-10-12/objects.csv](run-2026-10-12/objects.csv); group rows are in [run-2026-10-12/groups.csv](run-2026-10-12/groups.csv).

## Relation to the published claim

The published observation holds in this corpus under matched, out-of-sample comparison. Rao et al. (2009) compared eight complete West Asian texts with held-out Indus texts by raw likelihood. Their comparison matched average length but no object type, regional control or interval. The project's earlier test (`CHRONOLOGY-REGION-01`) kept seven mostly square external objects and found an excess of 0.65 bits per sign with interval −0.38 to 1.86. Here, 28 objects enter, damaged texts included. The excess, 2.11 bits per transition, lies mainly on the round seals that the earlier exact-type rule could not match. Parpola's contrast between typical square seals and atypical round seals appears in direction: square 0.52 against round 0.87. It is not clean, because two square seals and five of the seven non-seal objects found abroad are also atypical.

Two published details do not reproduce. Hunter's supported Mohenjo-daro circular seals behave like the Gulf ones. Parpola (1994a, via Laursen 2010, p. 117) counted the Iranian Gulf Type seals and a Girsu seal among the few well-paralleled sequences. In this corpus, the Susa circular seal (u = 0.99), the Luristan seal (0.94) and the Girsu round seal (0.92) are among the least predictable objects. The join of these local records to Laursen's seal numbers 14, 15 and 22 was not established, and Parpola's judgment used his own sign list and readings. The coarse-alphabet check (E5) leaves the result unchanged, so splitting sign variants alone does not explain the disagreement.

Several accounts predict unusual sequences of common signs, and the statistic does not separate them. Names or words in another language written with Indus signs, as Parpola, Laursen and Vidale propose, predict the pattern. So does a pseudo-script copied by carvers who did not read Indus writing; Laursen describes one such pseudo-inscription from Bahrain. A different text genre on round seals would also produce it, for example personal names where square seals carry titles or other content, whatever the language. A later date could contribute: Laursen dates the Gulf Type to about 2100–2000 BCE, near the end of the period the South Asian corpus covers. Transcription is a further source, because the foreign texts are coded from published drawings and photographs. The South Asian round seals bear on these accounts. If they were made by the same Gulf-oriented community, they are foreign texts found at home and support the language or names account. If they are local products, the round-seal genre itself carries the atypical sequences. The overlap count (E4) shows that the South Asian and West Asian round seals share no more transitions than ordinary South Asian seals do, so the two sets do not form one sequence tradition by that measure. That count rests on 7 unique complete South Asian round texts.

## Methods

The input is the normalized Lipi export (`data/normalized/lipi_observed_faces.jsonl`, 5,680 faces, commit `fc8813a5`), with Wells/ICIT sign codes parsed into reading order from the ICIT code string. Groups follow region and site labels fixed before outcomes. South Asia (5,617 faces) includes the Baluchistan/Makran sites that the export files under "Iranian Plateau". West Asia covers Persian Gulf, Mesopotamia, Susa, Tepe Yahya and Luristan: 32 faces and 31 objects after the Dilmun face BM 123208 is joined to the Ur seal U.17649. Central Asia has three faces, and seven unprovenanced round seals are reported separately.

A text is scored only on transitions whose predecessor is observed: start→sign when the reading-start edge is intact, sign→sign within runs of legible signs, and sign→end when the end edge is intact. The model is an interpolated Kneser–Ney bigram over a fixed vocabulary of 712 signs plus the end symbol. It is trained on South Asian texts deduplicated by code string, in ten folds grouped by object family and identical text. No test text is scored by a model trained on an identical code string.

Each test text is compared with complete South Asian texts of the same medium and length. The medium ladder runs square → all seals → all objects for square seals, and all seals → all objects for round seals; pottery, tags and tablets are compared within their own medium. A comparator receives the test text's damage mask and edge flags and is scored by the model of its own fold. The test text is scored by the same model for that comparison. Cells hold 36 to 1,453 comparators.

Ū is the mean over objects of the probability that the test text's surprisal exceeds a comparator's. The null replaces each object with a random member of its own cell, scored against the rest (20,000 draws). Intervals are percentile bootstraps over object families (10,000 draws). The South Asian comparison groups are removed from the pool and scored as test groups. [verify.py](verify.py) reimplements parsing, folds, the model, matching and the statistics without importing the analysis code. Its 22 checks all pass, and the deterministic values agree exactly ([verify-2026-10-12.json](verify-2026-10-12.json)).

## Limitations

Twenty-eight foreign objects and 16 South Asian round faces bound how finely subgroups can be read. The intervals for the Iran (4 objects), Central Asia (3) and South Asian cylinder (6) groups are wide or absent, and those rows are descriptive. The p-values for H1 and H2 sit at the Monte Carlo floor; they show only that no null draw reached the observed Ū. The foreign set contains the objects that the Lipi export transcribes, not the full published inventory. Laursen lists 28 inscribed Gulf Type seals, including those found in the Indus Valley, while the local West Asian set has 17 circular seal objects. Single-object identities, find contexts and dates were not checked against plates. The three Ra's al-Junayz pottery inscriptions and the Salut jar-rim impression may have been made in South Asia, and they enter the West Asian group by findspot.

## Exploratory checks after the outcomes

| Code | Check | Result |
|---|---|---|
| E1 | Comparators outside the 1,595-face cross-validation component | H1 Ū 0.762, H2 Ū 0.867 |
| E2 | South Asian round group split by type | SEAL:C 0.785 (10 faces), SEAL:CY 0.570 (6) |
| E3 | Adjacent 740–740 | South Asia: one damaged Dholavira square seal; unprovenanced round seal 3889.1; no West Asian text |
| E4 | Transitions shared with West Asian round seals | South Asian round 7.1% against length-matched South Asian non-round seals 7.2% |
| E5 | Mayig-class alphabet (547 symbols) | H1 Ū 0.757, H2 Ū 0.859, South Asian round 0.720 |

## Next tests

1. Check the transcriptions of the West Asian round seals and the Mohenjo-daro, Chanhu-daro and Dholavira circular seals against CISI plates and Laursen's Fig. 11, and join the local records to Laursen's Table 1 numbers. This would show whether the Iranian and Girsu disagreement with Parpola comes from coding.
2. Collect find contexts and dates for the South Asian circular seals. Late contexts, or a morphology matching Laursen's Gulf Type groups, would favour treating them as products of the Gulf-oriented community.
3. Score the round-seal texts against each other once the 28 Gulf Type inscriptions in Laursen's list are coded. A shared internal sequence model would indicate one tradition; heterogeneous texts would favour pseudo-writing or several sources.
4. Test the "twins"-initial pattern with an image-checked identification of sign 091 and its variants, since 4 of 22 West Asian texts with a known start begin with it.

## Files

[PROTOCOL.md](PROTOCOL.md) and [FREEZE-2026-10-12.json](FREEZE-2026-10-12.json) record the frozen design; [SOURCES.md](SOURCES.md) records the claim's sources; [ffcore.py](ffcore.py), [prefreeze_audit.py](prefreeze_audit.py), [analysis.py](analysis.py), [exploratory_checks.py](exploratory_checks.py) and [verify.py](verify.py) are the code; [prefreeze-audit.json](prefreeze-audit.json), `run-2026-10-12/` and [verify-2026-10-12.json](verify-2026-10-12.json) are the outputs; [RETROSPECTIVE.md](RETROSPECTIVE.md) records the process. Texts with sign sequences, comparator memberships and source copies are local only under `data/raw/2026-10-12-decipherment-claim-tests/foreign-finds/`.
