# Study B protocol: Indus-script texts found outside South Asia

Frozen 12 October 2026 before any statistic using the sign identities of a text found outside South Asia was computed. Later changes go into dated `AMENDMENT-*.md` files; earlier outputs stay in place. Parent protocol: [../PROTOCOL.md](../PROTOCOL.md), Study B.

## Claim under test

Asko Parpola has written repeatedly that Indus inscriptions on round "Gulf" seals and on cylinder seals found in Mesopotamia and the Gulf use common Indus signs in sequences unlike those of South Asian texts, while square Indus seals found in the same region carry typical Harappan sequences; he interprets the difference as Harappans abroad writing local names or another language. Steffen Terp Laursen (2010) restates the observation for the Gulf Type seals of Bahrain and Mesopotamia and contrasts them with Gulf Type seals from Iran and Mohenjo-daro. Rao and colleagues (2009) found that eight West Asian texts had much lower first-order Markov likelihood than 100 held-out Indus texts. Exact sources, locators and quotations are in [SOURCES.md](SOURCES.md).

The project's earlier test (`CHRONOLOGY-REGION-01`, [report section 3](../../2026-10-06-chronology-region/REPORT.md)) required exact object type and observed length with at least 20 comparators and kept only seven external objects, mostly square seals; it gave an excess of 0.65 bits per sign with interval [−0.38, 1.86] and listed "matched core circular seals" among its retry conditions. This study differs in four ways. Damaged texts contribute their observed spans and are compared with South Asian texts carrying the same damage mask. Round seals are compared with South Asian seals of any shape because the South Asian round class is too small for its own matched cells. South Asian round seals and peripheral regions are scored by the same leave-group-out procedure as the foreign texts. The published round-versus-square contrast is tested directly.

## Data and groups

Input: `data/normalized/lipi_observed_faces.jsonl` (5,680 faces, SHA-256 recorded in `prefreeze-audit.json`), derived from Lipi commit `fc8813a52e183d19c441631dc26c33a4dccbea39`. Sign codes follow Wells/ICIT numbering. The ICIT code string is parsed into reading order: the visual sequence is reversed, `+` marks an intact edge, `]` and `[` a broken edge, `000` an illegible sign, `999` a blank space and `/` a line break. An edge counts as known only when it carries `+` and the record is either marked complete or contains an explicit damage marker that explains its incompleteness.

Groups were fixed from region and site labels before outcomes:

| Group | Definition | Faces |
|---|---|---:|
| South Asia (training pool) | Lower Indus, Inter-Riverine, Gujarat/Kutch, Eastern Headwaters, Upper Indus, South India, and the Baluchistan/Makran sites Nindowari-damb, Sibri, Ornach area, Miri Qalat and Murda Sang (exported under "Iranian Plateau") | 5,617 |
| West Asia | Persian Gulf (17), Mesopotamia (11), and Susa, Tepe Yahya and Luristan (4) | 32 |
| Central Asia | Altyn Depe, Gonur Depe, Shortughai | 3 |
| Unprovenanced round seals | Region "Other", object type SEAL:C or SEAL:CY | 7 of 28 |

Two West Asian faces record one seal. The export's "Dilmun" face 6000.1 carries British Museum number BM 123208, which the 2026-10-06 finds-abroad census joined to Ur excavation number U.17649 (Gadd 1932 no. 16); Ur face 3898.1 carries excavation number U17649. The primary analysis keeps 3898.1 and drops 6000.1, leaving 31 West Asian objects. Tello (3885.1, square) and Girsu (5222.1, round) are the same site and different objects. Luristan is a provenance region, kept in the Iran subgroup as labelled. Shortughai is a Harappan settlement and is reported only within the Central Asian group. The remaining 21 unprovenanced faces are excluded from training and testing.

Media are fixed from object type: square (SEAL:S), round (SEAL:C and the cylinder SEAL:CY, the two shapes Parpola groups together), other seal (SEAL, SEAL:R, SEAL:L), pottery (POT*), tag (TAG*), tablet (TAB*) and miscellaneous. The West Asian set has 18 round or cylinder seals (17 SEAL:C and the Susa cylinder), 6 square seals and 7 other objects: the Hajar prism (TAB:I), three Ra's al-Junayz pottery inscriptions, the Tepe Yahya sherd, the Tell Umma sealing (TAG:L) and the Salut jar-rim impression (TAG). Within the round seals, the Gulf and Mesopotamian subgroup has 15 objects and the Iranian subgroup 3 (Susa circular, Susa cylinder, Luristan).

## Scoring units

Each text is split into spans, the maximal runs of legible signs between illegible signs, blanks and line breaks. A span receives a start symbol only if it begins at a known reading-start edge of a single-line text, and an end symbol only if it ends at a known reading-end edge. The scored events are the transitions inside spans with an observed predecessor: start→first sign, sign→sign and last sign→end. The first sign of a span without a known start is never predicted, so no event conditions on unobserved context. Multi-line texts contribute only within-line transitions and are excluded from matched comparisons because line order is unresolved. Texts with no events are unscorable and are listed.

Structure-only checks before freezing ([prefreeze-audit.json](prefreeze-audit.json)) show three unscorable West Asian objects: the Ra's al-Junayz copper seal 935.1 (one illegible sign), Ur 5225.1 (legible signs isolated by damage) and the two-line Karzakan seal 5230.1. The primary set therefore has 28 scorable West Asian objects, 16 of them round or cylinder seals.

## Models

The primary model is an interpolated Kneser–Ney bigram over sign codes with start and end symbols. The discount is D = n₁/(n₁ + 2n₂) from count-of-counts at each level. The lowest level interpolates Kneser–Ney continuation counts with a uniform distribution over a fixed vocabulary: every legible sign code in the full export plus the end symbol. The surprisal of a text is its mean −log₂ P per scored event, in bits.

Training texts are deduplicated by identical code string. A test text is never scored by a model whose training data contain a text with an identical code string or a face from the same object family.

## Comparison distribution

South Asian faces are divided into ten folds. Faces sharing an object family or an identical code string form one component, and each component is assigned to fold `int(sha256("ff-" + smallest record id)) mod 10`. Each fold model is trained on the other nine folds.

Every test text is scored by each of the ten fold models (with any identical code strings removed from training). Its comparators are South Asian texts that are complete, single-line and free of illegible signs and blanks, drawn from a medium cell and a length rule:

- If both edges of the test text are known, comparators have the same length L. Otherwise they have length at least L, and the window of L positions is aligned at the known edge or centred when neither edge is known.
- The test text's damage mask and edge flags are applied to each comparator window, so comparator and test have the same scored event structure.
- Medium ladder, using the first level with at least 20 comparators: square seals → square, then all seals, then all objects; round, cylinder and other seals → all seals, then all objects; pottery, tags and tablets → the same medium, then all non-seals, then all objects; miscellaneous → all non-seals, then all objects.

Each comparator is scored by the model of its own fold, which excludes it. The test text is compared within each fold against that fold's comparators using that fold's model, so both share the same training data.

For a statistic x (higher meaning less South-Asian-like), the per-object score is u = mean over comparators j of [1(x_test > x_j) + ½·1(x_test = x_j)], with x_test computed by the model of j's fold. Under the null hypothesis that the test text is exchangeable with its matched comparators, E[u] = 0.5. The excess Δ is the mean of x_test − x_j over the same pairs.

## Hypotheses, statistics and null distributions

- **H1:** The 28 scorable West Asian objects are less predictable than their matched South Asian comparators. Statistic: Ū, the mean of u over objects, for bigram surprisal.
- **H2:** The 16 scorable West Asian round and cylinder seals are less predictable than their matched comparators. Same statistic.

H1 and H2 are the primary tests, with a Holm correction over the two one-sided p-values. The null distribution is Monte Carlo with 20,000 draws (seed 20261012). In each draw, every test object is replaced by a randomly chosen member j′ of its own comparator cell, whose u is computed against the remaining members with each member's out-of-fold score. The one-sided p-value is (1 + #{Ū_null ≥ Ū_obs})/(1 + 20,000). The null 2.5% and 97.5% quantiles of Ū are reported as the effect size this sample can detect. Effect intervals are 95% percentile bootstraps over objects, resampling object families, with 10,000 draws (seed 20261013); they are reported for Ū and for Δ in bits per event.

Four secondary measures use the same u framework, the same null and a Holm correction within each of H1 and H2:

1. **Unseen transitions:** the share of scored events whose bigram never occurs in training.
2. **Rare signs:** the share of legible signs with at most two token occurrences in the deduplicated training texts.
3. **Unsupported span:** 1 − R, where R is the length of the longest contiguous legible run that occurs as a contiguous run in some training span, divided by the length of the longest legible span.
4. **Terminal 740:** absence of the jar sign 740 in final position, defined only when the end edge is known. Before freezing, 740 ended 672 of 2,122 unique complete South Asian texts.

The following measures are descriptive, with matched comparator rates and exact counts:

- presence of 740 anywhere;
- an initial sign in {817, 820, 861}, the three most frequent initial signs of unique complete South Asian texts (114, 114 and 111 texts), defined only when the start edge is known;
- an initial 091, the "two persons standing side by side" sign in the Mayig crosswalk, which Laursen identifies with the "twins" sign; before freezing, 091 began 5 of 2,122 unique complete South Asian texts;
- adjacent 740–740, which Parpola (2005) states never occurs in the Indus Valley;
- complete foreign texts whose code string also occurs in South Asia, compared with the share of complete South Asian comparator texts duplicated on another object family.

## Regional and type comparisons

Each South Asian comparison group is scored by the procedure used for the foreign texts. The group is removed from the pool, ten folds are refitted on the remainder, and the group's texts serve as test texts. The groups are Gujarat/Kutch (489 faces), Eastern Headwaters (65), Kalibangan (212), Baluchistan/Makran (7), Upper Indus (6), Chanhu-daro as a core-region site control (74), and South Asian round and cylinder seals (16 faces: 10 SEAL:C and 6 SEAL:CY). Within any test group, faces of one object family with identical code strings are collapsed. Remaining multi-face families keep each face as a unit; bootstraps resample families, and null draws treat faces independently.

Ū and its bootstrap interval are reported for each group, over all media and over seals only. For H1, the differences Ū_West − Ū_group, with intervals from independent bootstraps, are reported for the groups with at least 20 matched texts: Gujarat/Kutch, Eastern Headwaters, Kalibangan and Chanhu-daro. For H2, the difference Ū_West-round − Ū_SA-round is reported; it tests Hunter's observation (as reported by Laursen 2010) that the Mohenjo-daro round seals carry supported sequences. Within the West Asian set, the round-minus-non-round difference tests Parpola's square-versus-round contrast. Subgroups by subregion (Gulf, Mesopotamia, Iran), the Gulf/Mesopotamian versus Iranian round seals, the Central Asian group and the unprovenanced round seals are reported descriptively.

## Sensitivity analyses for H1 and H2

| Code | Change |
|---|---|
| S1 | Clean-only: training on the South Asian clean subset (complete, single-line, R/L, no unknown signs); tests are West Asian clean texts (12 objects); comparators are clean texts of equal length |
| S2 | Order-3 model: absolute-discounting trigram interpolated with the primary Kneser–Ney bigram; events with a one-sign history use the bigram |
| S3 | Witten–Bell bigram in place of Kneser–Ney |
| S4 | Square-seal comparators for every seal test |
| S5 | Any-object comparators, matched on length and mask only |
| S6 | Orientation-favourable: every test and comparator text is scored as the minimum of its forward and reversed mean surprisal |
| S7 | The Dilmun witness 6000.1 replaces Ur 3898.1 |
| S8 | Leave one site out: range of Ū |

## Decision rules

- **Deviation:** H1 (or H2) is supported when its Holm-adjusted one-sided p is below 0.05 and the bootstrap interval for Ū lies above 0.5. If the interval includes 0.5, the corpus does not show a deviation at this sample size, and the null quantiles state the smallest Ū the test could detect.
- **Beyond regional variation:** If H1 holds, the deviation exceeds sampled regional variation only if Ū_West − Ū_group has an interval above zero for all four qualifying peripheral groups. Otherwise it is reported as within the range of regional variation.
- **Round-seal specificity:** Parpola's contrast is supported when West Asian round seals have Ū above 0.5 with an interval excluding 0.5, and the round-minus-non-round difference within West Asia is positive with an interval excluding zero. The South Asian round-seal comparison is reported with its interval; with 16 faces it constrains rather than decides.
- **Sensitivity:** A sensitivity that reverses a decision is reported next to the primary result. It does not replace the result.

A deviation, if found, measures sequence predictability under South Asian statistics. It does not identify a language, a name or a reading.

## Outputs

Tracked: `run-2026-10-12/summary.json` (all aggregate statistics), `run-2026-10-12/objects.csv` (per-object record ID, site, group, object type, length, damage structure, event count, comparator level and size, and statistics, without sign sequences), `run-2026-10-12/groups.csv`, `verify-2026-10-12.json`, `REPORT.md`, `SOURCES.md` and `RETROSPECTIVE.md`. Local only (`data/raw/2026-10-12-decipherment-claim-tests/foreign-finds/`): texts with sign sequences, comparator memberships and per-comparator scores. `verify.py` recomputes the headline numbers through a separate implementation that does not import `ffcore.py` or `analysis.py`.
