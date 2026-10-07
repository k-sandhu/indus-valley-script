# Chronology, region and external inscriptions

Harappa's 3B–3C sign-frequency comparison exceeds its physical-family permutation reference in the full sample and among period-labelled faces. On Mound E the corrected p-value exceeds .05. The length increase is much smaller in the restricted excavation frames. Regional results retain four of six physical-family rejections; larger runs give two of six under copied-text closure. The seven matched external objects provide little coverage of the non-canonical circular-seal class. Exact estimates and populations follow below.

The first-pass endpoint is **Frozen evaluation**. Its support repairs, caption-led assays and this review response are **Exploratory**. The [Sonnet review](REVIEW.md) reproduced all 60 aggregate files and 380 quoted numbers, then identified interpretation problems. The [second amendment](REVIEW-AMENDMENT-2026-10-07.md), appended to [PROTOCOL.md](PROTOCOL.md), specifies the response after those problems were known. Old endpoints, source manifests and review files are unchanged. [Document snapshots](review-response-baseline-2026-10-07-v1/) retain the earlier wording.

## Shared inputs and reference assumptions

The observational input has 5,680 faces, 4,695 physical families, 3,477 transitive complete-text components, 19,946 observed slots, 18,067 known tokens and 1,879 unreadable `000` slots. Its vocabulary has 713 known codes. Frequency calculations omit `000` and retain partially readable faces with at least one known token. Ordered analyses require complete, single-line R/L texts without blanks or `000`, giving 2,930 faces. [Original audit](main-2026-10-07-v1/audit.json), `population`, `vocabulary_known_signs`; [new audit](review-response-2026-10-07-v1/audit.json), `population`.

Physical families join object-family identifiers and catalogue aliases before selection. The family reference permutes complete physical components within exact object-type and selected-face-count blocks. Text closure adds transitive links through identical complete known texts over the full corpus, before orientation filtering. Mixed-label or mixed-type components are excluded from a comparison. The largest physical component contains seven faces; the largest text component contains 1,038. Thus closure tests can use a different population. These procedures reuse [Paper 002](../../papers/002-conditional-reference-laws/) and [conditional_structure.py](../../src/methods/conditional_structure.py). They condition on recorded objects and assume exchangeable labels within blocks; excavated area, preservation and production-batch selection are absent from the input.

Equal-type frequencies average supported type-specific distributions. Common support requires ten physical families per arm and type. Region is fixed by site in every input row; equal-site weighting describes the sampled site frame, and a region effect conditional on fixed site is unidentifiable. Sequence folds keep complete text components together. [Original selection rules](PRECOMPUTATION_CLARIFICATION.md); [audit](main-2026-10-07-v1/audit.json), `site_region_multimapping=0`; [actual fold counts](exploratory-2026-10-07-v1/actual_fold_counts.json).

The new runs use seeds 21 and 22, 19,999 allocations for time and restricted-time tests, and 9,999 for the other permutation references. Frequency p-values have separate Holm families for time, region and the two excavation subsets, within each dependence reference. Sign tests use BH across the original 24 time or 314 regional hypotheses. The tables print each observed divergence, its own null mean and their difference. Means shown are seed 21; [divergence_baselines.csv](review-response-2026-10-07-v1/divergence_baselines.csv) also gives seed 22, finite-draw counts and raw/positional statistics. Null excess describes this conditional permutation reference. No usable confidence interval is supplied for JS magnitudes: both earlier bootstrap constructions exclude the observed time divergence, and no replacement with demonstrated coverage was obtained. [Interval withdrawal](review-response-2026-10-07-v1/permutation_tests.json), `statistics.*.magnitude_interval95` and `interval_status`.

## 1. Harappa through time

The calendar mapping follows J. Mark Kenoyer and Richard H. Meadow, *Inscribed Objects from Harappa Excavations 1986–2007* (2010), *Corpus of Indus Seals and Inscriptions* 3(1), xliv–lviii, printed xlv/Table 1, physical PDF page 4. It assigns Period 1 approximately 3700–2800 BCE, 2 to 2800–2600, 3A to 2600–2450, 3B to 2450–2200 and 3C to 2200–1900. Period 4 has questioned 1900–1800 boundaries; Period 5 extends from approximately 1800 to later than 1300. Labels such as 3C-2 are mapped by prefix. The source does not provide an independently checked calendar ordering of those numbered export subphases. Only Harappa receives HARP ages. [Primary PDF](https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf); [label mapping](main-2026-10-07-v1/period_mapping.json); [boundary notes](mapping-notes.json).

| Harappa assignment | Faces | Known tokens | Unreadable slots | Clear faces |
|---|---:|---:|---:|---:|
| 1 | 2 | 4 | 1 | 0 |
| 2 | 30 | 36 | 8 | 2 |
| 3A | 1 | 1 | 0 | 0 |
| 3B | 201 | 461 | 57 | 82 |
| 3C | 574 | 1,849 | 151 | 321 |
| 4 | 27 | 89 | 13 | 14 |
| 5 | 9 | 32 | 2 | 5 |
| Interval: 3B/C or broad 3 | 1,095 | 2,691 | 268 | 589 |
| Undated | 778 | 2,015 | 296 | 348 |

The table sums [original major/type strata](main-2026-10-07-v1/harappa_major_type_strata.csv). Current presentation copies suppress sparse cells as described below; total denominators above include them. A span 3B/C admits both periods, and broad Period 3 admits 3A, 3B and 3C. Primary comparisons use unambiguous assignments. Earlier whole-family extreme assignments and 100 uniform admissible-period allocations are preserved in [interval_sensitivity.json](main-2026-10-07-v1/interval_sensitivity.json). They describe sensitivity to specified date allocations.

### Excavation composition and frequency

| Composition of unambiguous faces | 3B | 3C |
|---|---:|---:|
| Period-field labels | 192 | 169 |
| Stratum labels | 9 (4.48%) | 405 (70.56%) |
| Mound E | 180 (89.55%) | 74 (12.89%) |
| Mound F | 13 (6.47%) | 413 (71.95%) |
| Mound AB | 2 | 61 |
| Mound J | 0 | 5 |
| Unknown mound | 6 | 21 |

A stratum label has `Stratum` in `metadata.phase`; other dated rows have an explicit period field. Mound is the prefix of `area-section`. The HARP 2010 contents page, physical PDF page 2, assigns H-1020–H-1520 and H-2590 to old excavations, and H-1521–H-2583 to HARP. All nine 3B stratum faces have earlier-range H-numbers. Of the 405 3C stratum faces, 392 have such numbers, ranging H-1–H-1517; 13 have no catalogue number. This sharpens the review's group-level count: 405 is the stratum total, while 392 is the directly numbered earlier-catalogue subset. Catalogue ranges are proxies for source composition, without supplying manufacture dates. [Composition](review-response-2026-10-07-v1/excavation_composition.csv), `period`, `label_source`, `mound`, `faces`; [catalogue check](review-response-2026-10-07-v1/catalogue_number_ranges.csv), `faces_earlier_proxy`, `faces_with_H_number`; [source check](review-response-sources-2026-10-07-v1/sources.json), `stored_source_checks`.

The full known-token comparison shares SEAL:S, TAB:B and TAB:I; restricted physical comparisons share TAB:B and TAB:I. Whole-family restrictions lose no mixed-origin or mixed-mound families because none occurs in the Harappa input. The following frequency tests use physical families; raw and adjusted distributions share each row's retained population.

| Comparison | Faces A / B | Observed JS bits | Null mean, seed 21 | Excess, seed 21 | Holm p, seeds 21 / 22 |
| --- | --- | --- | --- | --- | --- |
| 2 / 3C | 29 / 13 | 0.617808 | 0.504223 | 0.113586 | 0.06075 / 0.06305 |
| 3B / 3C | 186 / 451 | 0.190483 | 0.157180 | 0.033303 | 0.03920 / 0.03580 |
| period labelled | 172 / 101 | 0.219445 | 0.176564 | 0.042881 | 0.03420 / 0.03100 |
| mound e | 165 / 60 | 0.244466 | 0.206696 | 0.037770 | 0.06545 / 0.06555 |

| Frequency frame | Raw JS bits | Null mean, seed 21 | Excess, seed 21 |
| --- | --- | --- | --- |
| 3B / 3C | 0.192235 | 0.147535 | 0.044700 |
| period labelled | 0.222867 | 0.176461 | 0.046406 |
| mound e | 0.243511 | 0.206000 | 0.037511 |

[Tests](review-response-2026-10-07-v1/permutation_tests.json), `theme=time/subset`, `unit=physical_component`, `a/b`, `common_types`, `statistics`. The full 3B–3C row uses 110/335 physical families and 455/1,547 known tokens, including 44/102 unreadable slots. Period-labelled support has 97/60 families, 414/269 known tokens and 40/20 unreadable slots; Mound E has 93/34 families, 398/156 known tokens and 38/11 unreadable slots. The pottery-only Period 2–3C row has 29/13 families and 35/23 known tokens. Its updated Holm values exceed .05. Period 2–3B has no supported common type.

Text closure gives the following separate populations and references:

| Comparison | Faces A / B | Observed JS bits | Null mean, seed 21 | Excess, seed 21 | Holm p, seeds 21 / 22 |
| --- | --- | --- | --- | --- | --- |
| 3B / 3C | 89 / 148 | 0.301639 | 0.266994 | 0.034645 | 0.06500 / 0.06265 |
| period labelled | 89 / 50 | 0.349565 | 0.299779 | 0.049786 | 0.09290 / 0.09130 |
| mound e | 31 / 18 | 0.373894 | 0.379460 | -0.005567 | 0.52320 / 0.52535 |

Full closure drops 262 mixed-label and nine mixed-type faces. Its 89/148 faces belong to 142 retained text components. The restricted closure rows also fail Holm .05. The two seeds agree on all frequency decisions. [Seed agreement](review-response-2026-10-07-v1/seed_agreement.json), `frequency_tests`; [component exclusions](review-response-2026-10-07-v1/permutation_tests.json), `excluded`, `components`. The positive full-sample family result and the weaker closure/subset results support a graphic difference in the observed frame, with incomplete separation of chronology from excavation and copying.

### Length, positions and sequences

| Frame | Common faces 3B / 3C | Raw length change, slots | Equal-type change, slots | Conditional 95% interval |
| --- | --- | --- | --- | --- |
| all | 186 / 451 | 0.883762 | 0.723952 | [0.387, 1.045] |
| period labelled | 172 / 101 | 0.091388 | 0.162414 | [-0.151, 0.469] |
| mound e | 165 / 60 | 0.224132 | 0.115848 | [-0.265, 0.542] |
| all tablets | 176 / 312 | 0.883762 | 0.498158 | [0.255, 0.740] |

[Length results](review-response-2026-10-07-v1/length_comparisons.json), `comparisons`, with within-type means in [length_type_means.csv](review-response-2026-10-07-v1/length_type_means.csv). Raw changes use all faces with a known sign in each selected excavation frame. The all-tablets row retains the full raw frame and restricts its adjusted estimate to TAB:B/TAB:I. Intervals resample 999 whole physical families within observed exact-type/face-count signatures. The full adjusted increase of 0.724 slots falls to 0.162 among period-labelled tablets and 0.116 on Mound E, with restricted intervals spanning zero. The original full-sample estimate should therefore not be read as a uniform temporal increase.

| Frame | Position | Equal-type JS bits | Null mean, seed 21 | Excess, seed 21 |
| --- | --- | --- | --- | --- |
| 3B / 3C | initial | 0.401792 | 0.285758 | 0.116034 |
| 3B / 3C | terminal | 0.173488 | 0.128425 | 0.045064 |
| period labelled | initial | 0.382569 | 0.327354 | 0.055215 |
| period labelled | terminal | 0.245220 | 0.195382 | 0.049839 |

[Positional baselines](review-response-2026-10-07-v1/divergence_baselines.csv), `statistic=initial_js_bits/terminal_js_bits`, `theme=time/subset`, `unit=physical_component`. These are descriptive positional effects with the same conditional null construction; frequency Holm values do not test them. The full shared tablet support has 77/198 clear faces. Mound E has no type reaching ten clear families in both periods, so its type-adjusted positional comparison is unsupported. Internal-bigram conditional entropy on all clear texts rises from 0.89853 to 1.88940 bits; averaging the two tablet types gives 0.59844 to 0.83227. The sample grows from 82 to 321 clear texts, which also raises empirical sequence diversity. [Preserved sequence summary](exploratory-2026-10-07-v1/sequence_summary.json), `periods.raw`, `equal_type_mean_conditional_bigram_entropy_bits`.

Sign 034 changes by −2.34048 percentage points on the full equal-type frame. The historical linear-frequency family-bootstrap interval is [−3.8178, −0.9469] points. Larger time-family tests give p=.00180/.00185 and BH q=.0432/.0444 for seeds 21/22. It passes both seeds; every other time sign and all 314 regional signs fails BH .05. The old statement of zero time-sign passes is superseded. [New sign tests](review-response-2026-10-07-v1/sign_tests.csv), `theme=time`, `sign=034`, `p`, `bh_q`; [historical frequency interval](main-2026-10-07-v1/sign_tests.csv), `ci95_low/high`. This interval is conditional on the recorded family sample and supplies no independent archaeological dating evidence.

### Observed first and last occurrences

The attestation table covers 368 signs; interval labels leave 209 earliest and 89 latest bounds unresolved. Eighty-eight signs first occur unambiguously in 3C in this sample. Five last occur in 3B: 062, 074, 222, 242 and 327, borne by 1, 1, 2, 2 and 1 families. For 015, one family supplies the first 3C occurrence. Zero recorded occurrences in 115 3B families permits a one-sided 95% presence bound of 2.5713%; the single 3A family permits 95%, under independent-family sampling. Unreadable slots and interval assignments widen the evidence beyond these readable bounds. [Attestation bounds](main-2026-10-07-v1/harappa_attestation_bounds.csv), `earliest_observed_lo/hi`, `latest_observed_lo/hi`; [presence](main-2026-10-07-v1/harappa_component_presence.csv), `zero_count_one_sided95_upper`; [type-specific bounds](exploratory-2026-10-07-v1/attestation_by_type.csv). Secure early objects, stratum-to-period source documentation and narrower context dates would sharpen introduction/disappearance bounds.

## 2. Regional usage and sequence transfer

The eligible regional pairs retain the original common-type selections. Their physical-family references are:

| Comparison | Faces A / B | Observed JS bits | Null mean, seed 21 | Excess, seed 21 | Holm p, seeds 21 / 22 |
| --- | --- | --- | --- | --- | --- |
| Inter-Riverine / Lower Indus | 1896 / 1709 | 0.151553 | 0.124776 | 0.026776 | 0.00240 / 0.00120 |
| Inter-Riverine / Gujarat/Kutch | 1761 / 416 | 0.220922 | 0.157342 | 0.063581 | 0.00060 / 0.00060 |
| Inter-Riverine / Eastern Headwaters | 748 / 45 | 0.403076 | 0.313188 | 0.089887 | 0.00540 / 0.00390 |
| Lower Indus / Gujarat/Kutch | 1525 / 268 | 0.185562 | 0.167248 | 0.018314 | 0.09200 / 0.07980 |
| Lower Indus / Eastern Headwaters | 1275 / 45 | 0.427168 | 0.308298 | 0.118870 | 0.00060 / 0.00060 |
| Gujarat/Kutch / Eastern Headwaters | 181 / 45 | 0.447173 | 0.397609 | 0.049564 | 0.09200 / 0.07980 |

Complete-text closure changes those selections:

| Comparison | Faces A / B | Observed JS bits | Null mean, seed 21 | Excess, seed 21 | Holm p, seeds 21 / 22 |
| --- | --- | --- | --- | --- | --- |
| Inter-Riverine / Lower Indus | 1159 / 1507 | 0.151927 | 0.146413 | 0.005514 | 0.23500 / 0.23920 |
| Inter-Riverine / Gujarat/Kutch | 1112 / 381 | 0.218395 | 0.194152 | 0.024242 | 0.04150 / 0.03700 |
| Inter-Riverine / Eastern Headwaters | 668 / 37 | 0.439592 | 0.364921 | 0.074672 | 0.06280 / 0.05880 |
| Lower Indus / Gujarat/Kutch | 1416 / 247 | 0.190183 | 0.172573 | 0.017610 | 0.14610 / 0.14820 |
| Lower Indus / Eastern Headwaters | 1183 / 39 | 0.436804 | 0.344076 | 0.092728 | 0.01080 / 0.00840 |
| Gujarat/Kutch / Eastern Headwaters | 168 / 43 | 0.465576 | 0.429676 | 0.035900 | 0.23500 / 0.23920 |

Both seeds give four physical-family and two closure rejections. Inter-Riverine–Gujarat/Kutch now joins Lower Indus–Eastern Headwaters under closure; the original 499-draw result had only the latter. No regional individual sign passes BH, with minimum q=.0785/.0942. [Updated tests](review-response-2026-10-07-v1/permutation_tests.json), `theme=region`, `a/b`, `common_types`, `statistics`; [seed/sign summary](review-response-2026-10-07-v1/seed_agreement.json). Each printed JS has its matching null mean and excess; none has a usable magnitude interval.

Original raw, equal-type and equal-site/type frequencies, positions and token rarefactions are retained in [region_comparisons.json](main-2026-10-07-v1/region_comparisons.json) and [rarefaction.json](main-2026-10-07-v1/rarefaction.json). Rarefaction equalizes known-token effort by type. Eastern Headwaters shares only 29 pottery and 79 square-seal tokens in the relevant rarefaction cells. Its small population and the lack of site-crossed regions limit inference beyond those sampled sites. The new [baseline table](review-response-2026-10-07-v1/divergence_baselines.csv) supplies raw and positional null summaries on each retained component population; the site-balanced descriptive estimand has no fixed-site regional test.

The fixed first-order sequence model uses half-count unigram smoothing and transition shrinkage 20. It compares other-region and within-region models on identical held-out faces, with complete text components confined to folds. Equal-type/site test weighting gives:

| Region | Test faces / families | Within / other bits per sign | Other-minus-within [conditional 95% interval] | Equal training-component excess [interval] |
|---|---:|---:|---:|---:|
| Inter-Riverine | 861 / 668 | 6.65469 / 7.29329 | 0.63860 [0.53459, 0.75535] | 0.26346 [0.09530, 0.37548] |
| Lower Indus | 1,037 / 1,008 | 7.10144 / 7.37572 | 0.27428 [0.11884, 0.44392] | 0.18223 [0.03222, 0.33147] |
| Gujarat/Kutch | 114 / 114 | 7.58400 / 6.51644 | −1.06756 [−1.48527, −0.62911] | −0.03030 [−0.18635, 0.15856] |

[Preserved models](main-2026-10-07-v1/regional_models.json), regional `adjusted.test`, `adjusted.losses`, `training`; [conditional test-loss intervals](exploratory-2026-10-07-v1/model_intervals.json), `losses.type_excess/size_excess`. Intervals resample saved test losses while holding fitted models fixed. Matching training-component budgets removes most of Gujarat/Kutch's apparent transfer advantage. Eastern Headwaters and Upper Indus lack a type with 20 training faces in every fold. Additional independently sampled sites per region, production groups and training-refit uncertainty would make regional generalization more informative.

## 3. External and non-canonical inscriptions

The external field set contains 42 faces/families, 149 known tokens and 19 unreadable slots: Persian Gulf 17 faces, Mesopotamia 11, Iranian Plateau 11 and Central Asia 3. Sixteen faces pass the ordered-text filter; nine lack exact type/length support. Matching retains seven objects, from those regions in counts 3/1/1/2. Seven of the eleven Iranian Plateau rows are Baluchistan/Makran sites in the package mapping, and the matched row is from Nindowari-damb. The retained types are mostly standard Indus square seals, with an incised tablet and pottery graffiti. Parpola's 2018 section I.C describes Gonur/Shortughai examples as classical Indus seals. This endpoint consequently gives little coverage of the non-canonical circular class. [Original external selection](main-2026-10-07-v1/external_models.json), `external_all`, `external_eligible`, `matched_faces`, `by_region`; [reviewed site counts](review/external_codes_and_sites.json); [mapping](mapping-notes.json).

Each external text is scored against a core model excluding its test fold and all external-touched text components. Comparator texts share exact type, observed length and fold. The external exact-type loss is 7.87617 bits/sign, versus 7.22528 for matches: excess 0.65090, family-bootstrap interval [−0.37986, 1.85719]. A pooled model gives excess −0.08632. Exact-type bigram novelty excess is 0.05269 [−0.17347, 0.27994] on seven objects; trigram excess is 0.10629 [−0.10270, 0.26747] on four. The enlarged six-statistic sign-flip family gives Holm 1.000 in both seeds for every score. Exact enumeration of the seven-family type-loss reference gives p=.359375; Monte Carlo p=.3650/.3628. [Fixed-model results](main-2026-10-07-v1/external_models.json), `results`; [new flips](review-response-2026-10-07-v1/other_permutation_references.json), `external_score_sign_flips`. These conditional intervals do not represent excluded types or refitted-model uncertainty.

The [corrected literature checklist](review-response-sources-2026-10-07-v1/external_literature_check.csv) replaces Ur's erroneous Parpola 2018 attribution with the Frenez Harappa.com image 1 caption, a secondary site lead. Ra's al-Junayz is a general Oman lead rather than a named caption location. Individual object identities and non-canonical classifications still need original plates and find contexts. Regional field membership alone supplies neither a language class nor evidence for patronymics.

## Published precedents and the scope of the contribution

Nisha Yadav, *Sensitivity of Indus Script to Site and Type of Object* (2013), *SCRIPTA* 5:67–103, directly compares site/type usage and lengths; printed 85 reports frequent West Asian Mahadevan signs including sign 1. Michael Philip Oakes, *Statistical Analysis of the Tables in Mahadevan’s Concordance of the Indus Valley Script* (2019, online 2017), *Journal of Quantitative Linguistics* 26:22–47, studies positional and metadata associations. These establish regional/type/position precedents. [Yadav PDF, printed 79–85 and 91](https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf); [Oakes manuscript, abstract](https://wlv.openrepository.com/bitstreams/8f84dd81-ba40-4036-86aa-992596cf289c/download).

Ayuha Suga, *Diachronic Changes in the Indus Script Based on the Proposed Arrangement of the Indus Seal* (2024), *Journal of General Linguistics* 26–27:25–65, analyzes 1,137 seals in proposed 3A/3B/3C arrangements. Its exact title has no colon. Gregg Jamison, Akinori Uesugi and Yuji Yamaguchi, *Unicorns and seals: New multivariate approaches to exploring patterned stylistic variation in the Indus Civilization* (2023), *Archaeological Research in Asia* 36:100486, supplies a recent stylistic precedent at abstract/bibliographic scope. Andreas Fuls, *Corpus of Indus Inscriptions* (2022), *Mathematica Epigraphica* 3, is retained as a catalogue bibliography only. The earlier section 1.3/1.4 content attribution is withdrawn: the reviewer could not reproduce it, and direct downloads again returned 403. A current cached web excerpt is distinguished from a preserved PDF witness. [Suga PDF, title page and printed 32–34](https://www.lingua.tsukuba.ac.jp/ippan/JGL/2024/GL26-27_3_paper2.pdf); [Jamison author record](https://okayama.elsevierpure.com/en/publications/unicorns-and-seals-new-multivariate-approaches-to-exploring-patte/); [Fuls author record](https://www.researchgate.net/publication/373522666_Corpus_of_Indus_Inscriptions); [corrected access record](review-response-sources-2026-10-07-v1/sources.json), `sources`.

Rajesh P. N. Rao, Nisha Yadav, Mayank N. Vahia, Hrishikesh Joglekar, R. Adhikari and Iravatham Mahadevan, *A Markov model of the Indus script* (2009), *PNAS* 106:13685–13690, Table 2 compares eight West Asian strings with Indus texts. Asko Parpola, *Indus Seals and Glyptic Studies: An Overview* (2018), in *Seals and Sealing in the Ancient World*, 127–143, provides external seal context. D1 repeats the broad questions and refines their observational tests through physical/copying groups, explicit interval labels, exact object-type/length support and excavation-frame sensitivity. Publication priority is not established. [Rao PDF, page 5/Table 2](https://homes.cs.washington.edu/~rao/PNASIndus.pdf); [Parpola proof, section I.C](https://tuhat.helsinki.fi/ws/portalfiles/portal/127255979/Parpola_Asko_2018_Indus_Seals_and_Glyptic_Studies_An_Overview_final_proof_2016_.pdf). Original [sources.json](sources.json), [sources-post-launch.json](sources-post-launch.json) and the [correction manifest](review-response-sources-2026-10-07-v1/sources.json) preserve exact bibliographies, access scopes and failed routes.

## Caption-led post-launch assays

These assays follow the coordinator's [caption check](../2026-10-06-research-program/frenez-talk-check.md) and [7 October protocol](POST-LAUNCH-PROTOCOL-2026-10-07.md). The candidates preceded the matched-frequency computation according to file times; broad per-region frequencies already existed. Their nomination cannot be characterized as independent of all earlier counts. Exact lecture-slide identifications were not inspected.

### Human and paired-human signs

| Candidate | Wells / Mayig | Finnish chart IDs, column 0 | Graphic scope |
|---|---|---|---|
| Simple human | 090 / P013 | 133/535, rows 26–27 | Primary man candidate; Mayig M001 |
| Paired humans | 091 / P016 | 110/692, rows 31–32 | Primary twins candidate; Mayig M002 |
| Modified human | 093 / P014 | 394, row 28 | Declared single-figure alternative |
| Bracketed human | 097 / P015 | 518/150, rows 29–30 | Alternative sharing Mayig M002 |

The atlas index `pdf_page=20` is zero-based, physical PDF page 21. Its source is Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), University of Helsinki Research Reports 1. The Mayig compatibility arrays and their derived Wells crosswalk are one annotation source. The review's independent positional join agrees at nine of eleven relevant 090/093/P013/P014 positions, while no position tests 091/097. Wells 091 therefore still lacks an independent code check. [Identification output](post-launch-2026-10-07-v1/sign_identifications.json); [schema](../../data/normalized/mayig_sign_schema.json), `signs.P013/P016/P014/P015`; [crosswalk](../../data/normalized/mayig_wells_class_crosswalk.json), `by_wells_id`; [alignment check](review/lipi_mayig_alignment.json); [chart source](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/).

Raw 090 usage is 7/149 external known tokens (4.69799%) versus 184/17,792 core (1.03417%); 091 is 5/149 (3.35570%) versus 22/17,792 (0.12365%). All twelve external target tokens occur on the eighteen circular seals. Every 090 occurrence fails the ordered-text filter. Four 091 occurrences pass but have zero or one core family in their exact cells, below the minimum two. The matched frequency frame retains seven external faces/30 tokens against 958 core faces/881 families/3,042 tokens, and contains no external target occurrence. Equal-type matched excesses are −0.28739 and −0.01228 percentage points, with historical grouped intervals [−0.55029, −0.06202] and [−0.07366, 0.00000]. Both seeds give enrichment Holm 1.000 for all six candidate sets under physical and text references. [Raw/matched counts](post-launch-2026-10-07-v1/external_target_counts.csv); [matched effects/intervals](post-launch-2026-10-07-v1/external_frequency.json), `results`; [selection](post-launch-coverage-2026-10-07-v1/external_selection_counts.csv); [new references](review-response-2026-10-07-v1/other_permutation_references.json), `external_targets`. The published circular-class observation remains unsupported by exact matching here; reviewed direction metadata and same-type/length core circular comparators are the missing inputs.

Massimo Vidale, *Growing in a Foreign World: For a History of the “Meluhha Villages” in Mesopotamia in the 3rd Millennium BC* (2004), *Melammu Symposia* 4:261–280, printed 270 discusses man and variants and cites Parpola 1986:411 for the patronymic hypothesis. It does not discuss twins there. Vidale's *The Short-Horned Bull on the Indus Seals: A Symbol of the Families in the Western Trade?* (2005), *South Asian Archaeology 2003*:147–158, Figure 5, printed 155, supplies the separate graphic/distribution precedent. Steffen Terp Laursen, *The westward transmission of Indus Valley sealing technology: origin and development of the ‘Gulf Type’ seal and other administrative technologies in Early Dilmun, c.2100–2000 BC* (2010), *Arabian Archaeology and Epigraphy* 21:96–134, explicitly discusses prefixed twins in its abstract, printed 96. The newly acquired primary PDF confirms that passage. [Vidale 2004 PDF](https://www.harappa.com/sites/default/files/201402/Vidale-Indus-Mesopotamia.pdf); [Vidale 2005 PDF](https://publications.dainst.org/books/dai/catalog/view/2043/2440/4491); [Laursen primary PDF](https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf). These frequency observations leave the proposed patronymic meaning untested. Parpola 1983/1986/1994 full underlying analyses remain bibliographic leads in the source manifests.

### Inscribed-media diversity around the 3C date bin

Harappa has 1,921 physical families and 2,717 faces. Media counting includes unreadable inscribed objects because their type is observed. In the full 3B/3C sample there are 115/444 families, five/fourteen exact types and Shannon diversity 1.56323/2.53051 bits. Period-labelled families have five/nine types; Mound E has four/eight. Equal-family rarefaction and 999 whole-family bootstrap summaries give:

| Frame | Families 3B / 3C | Faces 3B / 3C | Budget | Rarefied richness change [interval] | Shannon change, bits [interval] | Richness Holm 21 / 22 | Shannon Holm 21 / 22 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | 115 / 444 | 201 / 574 | 115 | 4.598459 [3.114, 6.126] | 0.901051 [0.686, 1.136] | 0.0132 / 0.0126 | 0.0004 / 0.0002 |
| period labelled | 108 / 123 | 192 / 169 | 108 | 3.742102 [1.878, 4.865] | 0.987639 [0.688, 1.253] | 0.0106 / 0.0116 | 0.0030 / 0.0018 |
| mound e | 100 / 44 | 180 / 74 | 44 | 4.361847 [1.174, 5.008] | 0.784685 [0.198, 1.103] | 0.0014 / 0.0010 | 0.0018 / 0.0041 |

[New comparisons](review-response-2026-10-07-v1/media_comparisons.json), `comparisons.*.effects`; [type counts](review-response-2026-10-07-v1/media_type_counts.csv), `subset`, `period`, `type`, `families`, `faces`; [all-period counts/diversity](post-launch-2026-10-07-v1/media_period_summary.csv). Both seeds retain positive rarefied richness and entropy effects and Holm values below .05 in every frame. The period-labelled frame removes the 9/405 stratum-labelled faces; Mound E compares 180/74 faces from that mound. These restrictions reduce the specific excavation imbalance shown above, while excavated area and preservation remain unmeasured.

All 200 earlier sampled admissible-date allocations give positive rarefied differences. [Preserved allocation results](post-launch-2026-10-07-v1/media_interval_allocations.csv). The bin covering 2100 BCE is 3C, spanning 2200–1900; the data do not locate a change at a specific year. Jonathan Mark Kenoyer, *Origin and Development of the Indus Script: Insights from Harappa and other sites* (2020), in Kaleemullah Lashari (ed.), *Studies on Indus Script*, 217–236, Table 2 at printed 221–223 already describes wider inscribed media in 3B/3C. This assay quantifies a published chronology observation within the exported sampling frame. [Kenoyer primary PDF](https://www.harappa.com/sites/default/files/pdf/Kenoyer2020%20Origin%20of%20Indus%20Script-2.pdf). Additional area/volume denominators and consistent object recovery across excavations would sharpen the temporal interpretation.

### Earliest dated sign inventory

Unambiguous Periods 2/3A, 2800–2450 BCE, supply 31 readable families, 37 known tokens, eight unreadable slots and eighteen signs. Later 3B/3C supplies 557 readable families/773 faces and 2,310 known tokens. A sample of 31 later families averages 63.01051 signs and 128.97599 known tokens, so equal object counts leave unequal text effort. Exact type-only support has 29 early/17 later pottery families, common budget 17, and expected inventories 12.61970/20.00000. Exact type/observed-length support has 27 early/12 later families, budget 12, and expected inventories 10.12019/10.00000. [Original inventory endpoint](post-launch-2026-10-07-v1/early_inventory.json), `raw_family_reference`, `adjusted`; [cell denominators](post-launch-coverage-2026-10-07-v1/early_adjusted_denominators.csv).

The new type-only difference is −7.38030 signs with Holm .0422/.0420; copied-text closure gives .1700/.1632. Type/length adjustment gives +0.12019 with Holm .5046/.5077, and closure .6571/.6414. Both seeds agree. [Larger references](review-response-2026-10-07-v1/other_permutation_references.json), `early_inventory`. This adjusted result concerns one/two-slot pottery graffiti; the twelve later families contain ten signs in total. It offers little coverage of an early seal repertoire.

The old type-only inventory bootstrap has mean −3.67576 against observed −7.38030, a shift of +3.70455 signs; type/length has mean 1.21571 against 0.12019, a shift of +1.09552. Resampling families with replacement reduces the distinct objects/sign union differently on each side. This explains why the old bootstrap interval and permutation decision looked discordant: the bootstrap distribution is not centred on the observed union statistic. Those historical intervals are retained as resampling diagnostics and are not usable population confidence intervals here. [Bias diagnostics](review-response-2026-10-07-v1/early_interval_diagnostics.json), `bootstrap_mean`, `observed`, `mean_minus_observed`. Securely dated early seals/sealings and richer same-type/length later comparator populations are needed to test the lecture's proposed early graphic repertoire. The full Kenoyer–Meadow 2008 chapter remains unchecked; its exact bibliography is recorded from Kenoyer 2020, printed 233.

## Disclosure and computation checks

The immutable original tables contain 96 single-face site/type cells and 25 single-face region/type cells. The review finds sixteen clear site/type singleton cells of at most three slots whose complete sequence can be reconstructed. New [presentation copies](review-response-2026-10-07-v1/disclosure_safe/) suppress cells with fewer than five faces, including their sign, position and length rows. Site/type suppression removes 157 cells/261 faces and retains 64 cells; region/type removes 52/104 and retains 49. [Suppression totals](review-response-2026-10-07-v1/disclosure.json). Historical private outputs are explicitly retained under the instruction to preserve endpoints; they require a disclosure/rights decision before redistribution. Count-only composition/media tables do not contain individual sign sequences, and the five-face threshold supplies no general anonymity guarantee.

The accelerated implementation matched the preserved permutation function on nineteen supported 31-draw schedules, including 650 sign p-values. The new run completed in 267.12 seconds with 1.53 MB aggregates and 34.64 MB local memberships/draws at completion. Verification checks 38 enlarged frequency rows, 676 sign-test rows, exact combinatorial media expectations, saved tails/corrections, 114 independently recounted label draws, 280 immutable archival pins and five archived documents. [Acceleration checks](review-response-2026-10-07-v1/acceleration_checks.json); [run audit](review-response-2026-10-07-v1/audit.json); [verification](review-response-checks-2026-10-07-v1/verification.json). Full independent regeneration of every draw and archaeological authentication remain reviewer tasks. [README](README.md) gives fresh-output commands and source checks.
