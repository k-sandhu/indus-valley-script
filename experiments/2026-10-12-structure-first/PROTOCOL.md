# Structure before meaning: protocol for steps 1–6

Recorded 12 October 2026 before any outcome in this directory was computed. Claude Opus 5.5 runs this program unattended at the user's request, following the diagnosis in [knowledge/directions/structure-first-2026-10-12.md](../../knowledge/directions/structure-first-2026-10-12.md). Before writing it the author inspected input formats and sizes only: the clean Lipi frame (1,859 distinct reading-order texts, 8,535 signs, 577 attested codes), the full face export (5,680 faces, 118 with marked line breaks), the Mayig sign schema (498 Wells codes mapped to Mayig classes, 470 to Mahadevan numbers), the rendered Lipi glyph font, the Parpola 2008 copper-tablet relation table in `research/literature/copper_constraints.csv`, and the Bronze Age normalized records (522 Ur III seal legends, 31,215 Sumerian lines and 1,071 tablets with numeral tokens, 1,966 Egyptian glyph sentences, 4,114 Akkadian letter lines and a 269-line Linear B sample). Changes after a first outcome go into dated amendment files, and earlier outputs stay in place.

## Ownership and concurrency

This program owns `experiments/2026-10-12-structure-first/`, `data/raw/2026-10-12-structure-first/`, `knowledge/directions/structure-first-2026-10-12.md` and its own retrospective. A concurrent package, [published-claim tests](../2026-10-12-published-claim-tests/PROTOCOL.md), tests Yajnadevam's allograph and homophone key by minimal-pair substitution and neighbour divergence, and tests inscriptions found outside South Asia. This program does not repeat either test. Step 1 asks a different question, whether graphic bases and modifiers predict context, and cites the concurrent results where they bear on it. Codex packages for anchor expansion, satellite screening and transmission are also running; their files are read only.

## Hypothesis ledger

Each step states what four candidate descriptions of the script predict. They are not exhaustive and can combine.

| Label | Description |
|---|---|
| H-LANG | Logo-syllabic writing of a spoken language, with grammatical elements and phonetic signs |
| H-NAME | Names, titles and offices in a language, written as short formulae |
| H-ADMIN | A nonlinguistic administrative code of categories, quantities and authorities |
| H-EMBLEM | Fixed identity labels tied to owners, groups or images |

A test whose outcome these candidates predict alike is reported as descriptive and does not enter the decision summary.

## Shared inputs and grouping

The Indus corpus is the pinned Lipi export (`yajnadevam/lipi` commit `fc8813a52e183d19c441631dc26c33a4dccbea39`) as normalized in `data/normalized/`. The primary population is the clean frame `lipi_clean_rtl_singleline.jsonl`: complete single-line records with no unknown sign, in reading order, deduplicated to distinct sequences. Held-out evaluation uses components formed by union-find over object families and identical sequences within the clean frame, so that copies of one text or faces of one object never cross folds. Folds are assigned by a seeded hash of the component's smallest record identifier (seed `20261012`). Other populations (multi-line faces, copper and moulded tablets, numeral contexts) are defined in their steps.

Sequences remain local. Public outputs contain aggregates, authored code, sign codes and short examples.

## Step 1: the sign list

**Coding.** The author coded every font code from 001 to 958 as a base family plus modifiers from a fixed vocabulary (`encl`, `dots`, `inner`, `side`, `top`, `cap`, `bar`, `hatch`, `double`, `hold`, `pole`, `yoke`, `X`, `variant`) with stroke counts for numerals, from rendered glyph sheets, in `step1-signs/sign_components_v1.tsv`. An independent second coder codes the same sheets with the same vocabulary, without access to the first coding, the Mayig schema or any other coding file. Agreement is reported as the adjusted Rand index between the two base partitions over attested codes, unweighted and token-weighted, and as Cohen's kappa for the presence of each modifier.

**Inventories.** W is the Wells code. V merges codes whose base, modifier set (ignoring `variant`) and stroke count are identical. P is the Mayig class where mapped, otherwise W. M is the Mahadevan number where mapped, otherwise W. B is the base family alone. For each, report attested types, the share of types occurring once and at most twice, the token share of the 30 commonest types, and unigram entropy, on the deduplicated clean frame.

**Primary test: does a grouping predict context?** Every model predicts the original W codes, so held-out log loss is comparable across groupings. The baseline is an interpolated Kneser–Ney bigram over W codes with start and end symbols, discount 0.75. A class model interpolates the baseline with a class bigram, P(w | v) = λ P_KN(w | v) + (1 − λ) P(c(w) | c(v)) P(w | c(w)), where the class terms are add-0.5 smoothed. λ is chosen from {0.5, 0.6, 0.7, 0.8, 0.9, 0.95} by inner three-fold grouped validation on training data only. Five outer grouped folds give held-out bits per sign, reported overall and for target codes seen 0, 1–2, 3–9 and 10+ times in training. Groupings tested: B (coder 1), B (coder 2), V, P, M and a modifier signature grouping (codes sharing the same modifier set across different bases; strokes excluded). The null for each grouping is 200 random partitions of the same codes with the same group sizes, each refitted with the same procedure (seed `20261013`).

*Decision.* A grouping carries distributional information if its gain over the baseline is positive and exceeds the 95th percentile of its random-partition gains. The working representation for steps 2–4 is W codes plus the coarsest grouping that passes, as an added feature layer. If no grouping passes, steps 2–4 use W codes alone and the sign-family hypotheses below are recorded as unsupported.

*Predictions.* H-LANG and H-ADMIN predict that bases and modifier signatures pass, because a base would mark a word, commodity or category and a modifier a grammatical or quantitative distinction that recurs across bases. H-EMBLEM predicts that bases pass weakly or not at all and modifier signatures fail, because each emblem is an idiosyncratic whole.

**Descriptive outputs.** Modifier productivity: for each modifier, the number of distinct bases it attaches to among attested codes, and token totals. Granularity sensitivity: under W, V, P, M and B, the held-out bigram gain over a unigram model and the count of one-slot substitution frames among distinct texts.

## Step 2: images and texts on the same object

**Population.** Copper tablets (`TAB:C`) and moulded or incised tablets (`TAB:B`, `TAB:I`) from the full face export, each object with its image label from the export's `symbol` field and every complete readable text. Parpola's 2008 copper type relations (`copper_constraints.csv`) are a published comparator. Objects whose image is recorded as other or absent are reported and excluded from tests that need an image class.

**Tests.**

- *2a, image consistency.* Among distinct texts carried by at least two objects, the share whose objects all show one image class, against 10,000 permutations of image labels across objects.
- *2b, shared vocabulary within an image class.* Mean Jaccard similarity of sign-bigram sets between distinct texts of the same class against pairs from different classes, with a class-label permutation null over distinct text types.
- *2c, held-out prediction.* Predict the image class of each distinct text type from the other text types by the largest shared-bigram overlap, ties broken by class frequency. Accuracy against the majority class and against 10,000 label permutations.
- *2d, transfer to seals.* For every image class shared by copper tablets and seal field animals (elephant, rhinoceros, tiger, buffalo, gaur, zebu, unicorn and goat as recorded), collect the sign bigrams and trigrams that occur in that copper class and in no other copper class. Count seal texts containing any of them, split by seal field animal. The statistic is the number of hits on seals whose animal matches the copper class, summed over classes, against 10,000 permutations of field labels among seals with a recorded animal. Each class's odds ratio is reported.

*Predictions.* H-EMBLEM and H-NAME predict 2a and 2c strongly and a positive 2d, since a text naming the depicted being should recur where that being is depicted. H-ADMIN predicts 2a from mould series, weak 2c and no 2d. H-LANG is compatible with either.

*Decision.* A passing 2d (p < 0.05) is the first internal evidence that a sign group refers to what an image shows. A failing 2d with passing 2a and 2c means copper and tablet texts pair with their images inside their own genre and are not labels reused across genres.

## Step 3: segmentation and inflection

**Line-break evidence.** For the 118 multi-line faces, each line is read right to left. The test does not need line order: it asks whether each complete line occurs as a contiguous substring of a clean single-line text from another object family, compared with control windows of the same length that straddle the break under either line order. Report the two rates and an exact paired sign test over faces with both kinds of window.

**Segmenters.** Three segmenters run on distinct clean texts: (a) branching entropy, with a boundary where the right-branching entropy of the preceding n-gram (n = 1, 2) rises; (b) a Bayesian unigram Dirichlet-process segmenter (Goldwater, Griffiths and Johnson 2009) with α = 20, boundary prior 0.5 and a uniform sign base distribution, 2,000 Gibbs sweeps with annealing, seed `20261014`; (c) greedy longest match against n-grams of length 2–4 occurring in at least three distinct texts. The segmenter applied to IVS for the alternation analysis is the one with the highest boundary F1 in the step 5 rehearsal; this choice is fixed before IVS segment outcomes are examined. Each segmenter's agreement with line breaks is reported.

**Alternation.** Within a set of units (segments or words), a stem is a unit minus its last sign; a stem alternates if at least two units with that stem and different final signs are attested. Report the share of stems of length at least two that alternate, the number of distinct final signs involved, and the share of alternations covered by the five commonest finals. Compute the same quantities on Sumerian seal legends, Sumerian lines, Akkadian letter lines and Egyptian glyph sentences, using gold words and the chosen segmenter's output, after subsampling each to the IVS number of distinct units and length distribution (200 subsamples, seed `20261015`).

*Predictions.* H-LANG predicts an alternation rate near the inflected written languages with a small set of recurring finals. H-NAME predicts a moderate rate concentrated in a few title or case finals. H-ADMIN and H-EMBLEM predict low alternation.

## Step 4: stroke numerals

**Population.** Tokens of the short-stroke family (B001) and the tall-stroke family (B031) in clean distinct texts, with values from the coding table, and the next sign in reading order. Repeated in all complete faces as a sensitivity.

**Measures.** For each following sign with at least five numeral-preceded tokens: number of distinct values, normalized entropy of values and the share of the commonest value. Corpus-level: mutual information between value and following sign, against 10,000 permutations of values among numeral tokens. Short against tall strokes: Jensen–Shannon divergence of their following-sign distributions against a permutation of the short/tall label.

**Comparison.** Ur III tablets: numeral tokens (`NUM:n(unit)`, digit n) and the next word as the counted item. Linear B: the logogram preceding each numeral. Both are subsampled to the IVS number of numeral tokens and of qualifying items (200 subsamples).

*Predictions.* Counting (H-ADMIN, and accounting in H-LANG) predicts several values per item, high value entropy and low mutual information relative to value entropy, as in Ur III and Linear B. Lexical numerals in names, titles or fixed terms (H-NAME, H-EMBLEM) predict one dominant value per item and high mutual information.

## Step 5: rehearsal on readable scripts

Using the Bronze Age records with word boundaries hidden, run the step 3 segmenters on Sumerian seal legends (all 522), Sumerian lines and Egyptian glyph sentences subsampled to the IVS text count and length distribution, and Akkadian letter lines. Report boundary precision, recall and F1 and exact word recovery, and compute the step 3 alternation statistics on gold and predicted units. Run the step 4 numeral measures on the Ur III and Linear B subsamples. The rehearsal fixes which segmenter step 3 uses and shows whether, at Indus scale, the step 3 and 4 measures recover known properties of known systems.

*Decision.* A measure that fails to separate known systems at Indus scale is reported for IVS as descriptive only.

## Step 6: structural comparison of language families

No lexical or phonetic fitting is performed: the October 12 lexical-ambiguity study showed that pattern fits do not discriminate, and no phonetic anchor exists. The step compares measured structure with typological predictions.

**Measured profile (IVS and comparison corpora).** (i) Affix asymmetry: within multi-sign segments, the entropy of final signs minus that of initial signs, normalized by the log of the inventory. (ii) Closed-class position: for the 20 signs with the highest ratio of distinct neighbours to frequency among signs with at least 20 tokens, their mean normalized position. (iii) Numeral–item order from step 4. (iv) Segment length distribution.

**Predictions.** A typology table records, with sources, whether each candidate (Proto-Dravidian, Old Indo-Aryan, Proto-Munda, Sumerian, Elamite, Burushaski, Akkadian) is predominantly suffixing or prefixing in nominal morphology, places genitives and adjectives before or after the noun, and places numerals before or after the counted noun. Each measured statistic is mapped to a predicted direction under the explicit assumption that the seal texts are noun phrases; the Sumerian and Akkadian seal corpora check whether those directions appear in real seal legends of head-initial languages.

*Decision.* A candidate is disfavoured only if a statistic that separated known head-initial and head-final seal legends in step 5 or 6 points the other way for IVS. Candidates that share all predicted directions remain tied, and the report says so.

## Outputs, verification and review

Each step writes a dated run directory with `summary.json`, aggregate tables, the hashes of this protocol and of every input, and a short report. A separate verification script recomputes headline numbers with independently written code where feasible. After the six steps, an adversarial review by a separate agent checks the code, the decision rules and the prose; findings and responses are saved in `review/`. The integrated report states each decision against the hypothesis ledger, preserves failed and null outcomes, and lists what each result changes in the next action.
