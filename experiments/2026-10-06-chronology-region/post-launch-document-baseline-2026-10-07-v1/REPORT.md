# Chronological and regional comparisons in the local corpus

Harappa's unambiguous 3B and 3C records differ in their object-adjusted sign frequencies, with Jensen–Shannon divergence **0.19048 bits** and a physical-family permutation Holm p-value of **0.044**. The stricter text-component reference gives **p = 0.068** on a smaller population. Regional frequency differences also depend on the reference population. The matched external comparison contains only **seven objects** and does not establish a general external-text difference: adjusted surprisal excess is **0.65090 bits per sign**, with a family-bootstrap interval of **−0.37986 to 1.85719**. These findings concern the declared transcription populations and catalogue assignments. [Frequency tests](main-2026-10-07-v1/permutation_tests.json), fields `comparison`, `unit`, `effect_js_bits`, `holm_p`; [external result](main-2026-10-07-v1/external_models.json), `results.type_excess`.

The primary comparisons were specified before computing outcomes in [PROTOCOL.md](PROTOCOL.md) and the [implementation clarification](PRECOMPUTATION_CLARIFICATION.md). Their status is **Frozen evaluation**, with accounting and selected predictions checked as **Verified computation**. A subsequent [Exploratory amendment](AMENDMENT-2026-10-07.md) repairs an unusable site-balanced bootstrap and adds descriptive coverage tables. The original endpoint remains intact.

## Corpus and selection

The input contains **5,680 faces**, **4,695 physical families**, **19,946 observed slots**, **18,067 readable tokens** and **713 known graphic codes**. There are **1,879 unreadable 000 slots**. Frequency tables omit 000 while retaining partial faces with at least one known token. Initial, terminal and sequence analyses require complete, single-line R/L records, giving **2,930 eligible faces**. These restrictions preserve the repository's source-checked reading-order convention. [Audit](main-2026-10-07-v1/audit.json), `population`, `vocabulary_known_signs`; [stratified counts](main-2026-10-07-v1/region_type_strata.csv), columns `known_tokens`, `unreadable_tokens`, `clear_faces`.

| Region | All faces | Known tokens | Unreadable slots | Clear ordered faces |
|---|---:|---:|---:|---:|
| Inter-Riverine | 2,950 | 7,734 | 913 | 1,418 |
| Lower Indus | 2,098 | 8,431 | 588 | 1,286 |
| Gujarat/Kutch | 489 | 1,450 | 320 | 164 |
| Eastern Headwaters | 65 | 168 | 25 | 28 |
| Upper Indus | 6 | 9 | 0 | 0 |
| Persian Gulf | 17 | 57 | 4 | 7 |
| Mesopotamia | 11 | 42 | 9 | 4 |
| Iranian Plateau | 11 | 38 | 6 | 3 |
| Central Asia | 3 | 12 | 0 | 2 |
| Other | 28 | 124 | 12 | 18 |
| South India | 2 | 2 | 2 | 0 |

Table values sum exact object-type rows in [region_type_strata.csv](main-2026-10-07-v1/region_type_strata.csv). Core and external definitions are recorded in [region_mapping.json](main-2026-10-07-v1/region_mapping.json). The Iranian Plateau label includes Baluchistan/Makran contexts, including Nindowari-damb. This export category is not a classification of foreign language or seal style. South India and Other are excluded from the core/external model comparison.

Physical aliases were retained before selection. Predictive folds additionally close identical complete texts transitively over the full register, following the reused repository code. The largest physical component has **7 faces**; the largest physical/text component has **1,038 faces**. Every complete-text component stays within a fold. The frozen audit's `fold_token_loads` records an assignment proxy, because ineligible strings received unique markers; [actual_fold_counts.json](exploratory-2026-10-07-v1/actual_fold_counts.json) gives actual counts, with **2,331–2,455 clear tokens per fold**. [Main verification](verification-2026-10-07-v1.json), `whole_family_and_text_fold_checks`.

Jensen–Shannon divergence is zero for identical sign distributions and reaches one bit for disjoint distributions. Equal-type estimates give each supported object type the same weight. Equal-site/type estimates also give sampled sites equal weight within each type. This standardization separates differences in the sampled object mix from differences within supported types. [Declared statistics](PROTOCOL.md).

## 1. Harappa through time

Kenoyer and Meadow's *Inscribed Objects from Harappa Excavations 1986–2007* (2010), printed xlv, Table 1, assigns approximately **2600–2450 BCE to 3A**, **2450–2200 to 3B** and **2200–1900 to 3C**. Numerical subphases remain ordered catalogue categories within those ranges. Only Harappa receives this mapping; **1,128 non-Harappa faces** also carry `time` values and were not assigned HARP calendar ages. [Primary chronology](https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf), PDF page 4; [mapped labels](main-2026-10-07-v1/period_mapping.json); [all-site labels](main-2026-10-07-v1/all_site_time_strata.csv). Periods 4 and 5 retain the source's approximate/questioned boundaries; Period 5 extends later than 1300 BCE. [Date interpretation](mapping-notes.json).

| Harappa label group | All faces | Known tokens | Unreadable slots | Clear ordered faces |
|---|---:|---:|---:|---:|
| 1 | 2 | 4 | 1 | 0 |
| 2 | 30 | 36 | 8 | 2 |
| 3A | 1 | 1 | 0 | 0 |
| 3B, including numbered subphases | 201 | 461 | 57 | 82 |
| 3C, including numbered subphases | 574 | 1,849 | 151 | 321 |
| 4 | 27 | 89 | 13 | 14 |
| 5 | 9 | 32 | 2 | 5 |
| 3B/C or broad Period 3 | 1,095 | 2,691 | 268 | 589 |
| Undated | 778 | 2,015 | 296 | 348 |

Values sum exact types in [harappa_major_type_strata.csv](main-2026-10-07-v1/harappa_major_type_strata.csv). The individual label and subphase tables remain in [harappa_label_type_strata.csv](main-2026-10-07-v1/harappa_label_type_strata.csv). The one 3A face cannot support an inferential comparison.

Removing wholly unreadable faces leaves **191 faces/115 families in 3B** and **561 faces/442 families in 3C**. Common object support is SEAL:S, TAB:B and TAB:I: **186 versus 451 faces**, with **455 versus 1,547 known tokens**. Raw divergence is **0.20208 bits**; raw divergence on that common support is **0.19223**; equal-type divergence is **0.19048**. The raw observed-length increase is **0.88376 slots** [**0.62465–1.13957**]; after adjustment it is **0.72395 slots** [**0.36473–1.04572**], using the frozen bootstrap intervals. [time_comparisons.json](main-2026-10-07-v1/time_comparisons.json), `3B__3C`, `a`, `b`, `common_support_a/b`, `raw`, `raw_common_support`, `type_adjusted`.

The family-label test permutes complete components within exact type and face-multiplicity blocks, preserving expanded face counts. Its **p = 0.022**, Holm **0.044**, uses **110 versus 335 families**. Text closure retains **89 versus 148 faces** and gives divergence **0.30164**, p/Holm **0.068**. This sensitivity changes both dependence units and the selected population; its larger divergence cannot be compared as a correction of the original magnitude. The Period 2–3C pottery comparison uses **29 versus 13 faces**, divergence **0.61781**, Holm **0.044**. Period 2–3B has no adequately supported common type. [permutation_tests.json](main-2026-10-07-v1/permutation_tests.json), time rows and their `a/b` denominators.

Across **82 versus 321 clear faces**, raw initial and terminal divergence is **0.43713 and 0.20262 bits**. The adjusted ordered comparison has sufficient positional support only for TAB:B and TAB:I: **77 versus 198 clear faces**. Equal-type initial-sign divergence is **0.40179 bits** and terminal divergence **0.17349**. Conditional internal-bigram entropy is descriptively **0.89853 versus 1.88940 bits** on all clear records; averaging the two shared tablet types gives **0.59844 versus 0.83227**. Entropy changes with sample size and does not isolate chronology by itself. [Positional result](main-2026-10-07-v1/time_comparisons.json), `raw/type_adjusted.initial_js_bits/terminal_js_bits`, `sensitivity.clear`; [Exploratory sequence summary](exploratory-2026-10-07-v1/sequence_summary.json), `periods.raw`, `equal_type_mean_conditional_bigram_entropy_bits`.

Sparse divergence estimates showed bootstrap bias: the frozen percentile interval for adjusted frequency divergence is **0.20486–0.27897**, above the observed **0.19048**. The post-outcome, cell-preserving basic interval is **0.11003–0.17814**. Neither interval has coverage calibration for this sparse corpus; the two estimates expose sensitivity to the uncertainty method. Supplemental basic intervals are **0.24914–0.41986** for initial divergence and **0.03712–0.19070** for terminal divergence. Every supported supplemental interval uses all **499 replicates**. [Amendment](AMENDMENT-2026-10-07.md); [time_intervals.json](exploratory-2026-10-07-v1/time_intervals.json), `basic_centered_interval95`, `percentile_interval95`, `valid_bootstraps`.

### Interval-censored attestation

Assigning every 3B/C family to 3B gives adjusted divergence **0.13475**; assigning every such family to 3C gives **0.18036**. Common-type support differs between these endpoints. In **100 uniform admissible-period allocations**, including broad Period 3, divergence ranges **0.09727–0.14236**. This is an allocation envelope under stated assumptions, not an estimated distribution of archaeological dates. [interval_sensitivity.json](main-2026-10-07-v1/interval_sensitivity.json), `all_3BC_to_3B`, `all_3BC_to_3C`, `uniform_allocation.metric_envelopes.frequency_js_bits`.

The attestation table covers **368 signs**. Interval labels leave the earliest observed period unresolved for **209** and the latest for **89**. **88 signs** first appear unambiguously in 3C in this dated sample, and **5** last appear in 3B: 062, 074, 222, 242 and 327. Those five are carried by only **1, 1, 2, 2 and 1 physical families**, respectively. For 015, the first dated occurrence is one 3C family; absence in **115 3B families** gives a one-sided 95% upper presence bound of **2.5713%**, assuming independent-family sampling. Absence in the single 3A family allows a bound of **95%**. These bounds concern readable recorded occurrences; unreadable slots can conceal earlier or later usage. Weak early sampling also prevents interpreting observed endpoints as dates of introduction or disappearance. [Bounds](main-2026-10-07-v1/harappa_attestation_bounds.csv), `earliest_observed_lo/hi`, `latest_observed_lo/hi`, `physical_components_bearing_sign`; [presence intervals](main-2026-10-07-v1/harappa_component_presence.csv), `zero_count_one_sided95_upper`; [object-type bounds](exploratory-2026-10-07-v1/attestation_by_type.csv) and [type-specific presence](exploratory-2026-10-07-v1/presence_by_type.csv).

No individual sign passes BH q < .05 among **24 time tests**. The smallest q is **0.072**, shared by 034 and 390. For 034 the equal-type frequency change is **−2.3405 percentage points**, with a family-bootstrap interval **−3.8178 to −0.9469 points**, before multiplicity correction. [sign_tests.csv](main-2026-10-07-v1/sign_tests.csv), `theme=time`, `type_adjusted_b_minus_a`, `ci95_low/high`, `bh_q`.

## 2. Regional usage and transfer

Regional sign frequencies differ in the sampled populations, but region is completely determined by site. Holding site fixed leaves no regional label to permute or estimate. Equal-site weighting reduces domination by Harappa or Mohenjo-daro while changing the target to the sampled site frame. Sparse sites can then carry substantial weight. [Audit](main-2026-10-07-v1/audit.json), `site_region_multimapping=0`; [site/type denominators](main-2026-10-07-v1/site_type_strata.csv).

| Regional pair | Common-support faces A/B | Raw JS | Equal-type JS | Equal-site/type JS | Family Holm p | Text-closure Holm p |
|---|---:|---:|---:|---:|---:|---:|
| Inter-Riverine / Lower Indus | 1,896 / 1,709 | 0.14980 | 0.15155 | 0.26829 | 0.012 | 0.240 |
| Inter-Riverine / Gujarat/Kutch | 1,761 / 416 | 0.20194 | 0.22092 | 0.31997 | 0.012 | 0.060 |
| Inter-Riverine / Eastern Headwaters | 748 / 45 | 0.33003 | 0.40308 | 0.53201 | 0.012 | 0.072 |
| Lower Indus / Gujarat/Kutch | 1,525 / 268 | 0.12475 | 0.18556 | 0.28458 | 0.076 | 0.162 |
| Lower Indus / Eastern Headwaters | 1,275 / 45 | 0.28811 | 0.42717 | 0.41888 | 0.012 | 0.012 |
| Gujarat/Kutch / Eastern Headwaters | 181 / 45 | 0.29668 | 0.44717 | 0.42438 | 0.076 | 0.240 |

Raw JS uses the entire known-token pair, whereas the adjusted columns use the listed common support. The common type sets differ by pair; they are explicit in [region_comparisons.json](main-2026-10-07-v1/region_comparisons.json), `common_types`. The p-values test equal-type distributions without site balancing, and text closure uses its own reduced populations. [Test denominators](main-2026-10-07-v1/permutation_tests.json), region rows, `a/b`, `unit`, `holm_p`. Only Lower Indus–Eastern Headwaters passes Holm .05 under both references. None of **314 individual regional sign tests** passes BH .05. [Sign tests](main-2026-10-07-v1/sign_tests.csv), `theme=region`, `bh_q`.

The frozen site-balanced intervals for the first, second and fourth pairs retained only **3, 1 and 1** valid draws. The supplement conditions on sampled site/type/recording-quality signatures, preserving whole families and all selected cells. Its exploratory basic intervals for the site/type JS column above are, in row order, **0.20110–0.26414**, **0.25593–0.31671**, **0.43880–0.55751**, **0.21456–0.28101**, **0.30932–0.43145** and **0.30920–0.44662**. They measure a conditioned resampling frame and retain the sparse-divergence calibration limitation described above. [region_intervals.json](exploratory-2026-10-07-v1/region_intervals.json), `site_type_adjusted.frequency_js_bits`.

Equal-token rarefaction confirms that sample effort changes estimated magnitudes. For Inter-Riverine–Lower Indus, the mean equal-type JS is **0.17591**, with a rarefaction simulation spread **0.16224–0.18962**; type budgets range from **35 to 1,457 tokens**. For comparisons with Eastern Headwaters, the pottery and square-seal budgets are only **29 and 79 tokens**. These simulation spreads describe rarefaction, not population confidence. [rarefaction.json](main-2026-10-07-v1/rarefaction.json), `type_adjusted.token_budgets`, `mean_js_bits`, `simulation_interval95`.

Initial and terminal distributions also vary across the regional samples. The following pairs give initial/terminal JS in bits. Raw values use all clear faces in the corpus table; adjusted values use only shared types with adequate clear-family support, whose face counts appear here.

| Regional pair | Adjusted clear faces A/B | Raw initial/terminal | Equal-type initial/terminal | Equal-site/type initial/terminal |
|---|---:|---:|---:|---:|
| Inter-Riverine / Lower Indus | 861 / 1,037 | 0.35525 / 0.31988 | 0.34892 / 0.21410 | 0.50049 / 0.36455 |
| Inter-Riverine / Gujarat/Kutch | 292 / 127 | 0.45212 / 0.44888 | 0.49917 / 0.41510 | 0.53196 / 0.46096 |
| Inter-Riverine / Eastern Headwaters | 215 / 19 | 0.67062 / 0.48678 | 0.66765 / 0.36800 | 0.61696 / 0.53169 |
| Lower Indus / Gujarat/Kutch | 954 / 114 | 0.34906 / 0.24709 | 0.34567 / 0.26159 | 0.57432 / 0.32568 |
| Lower Indus / Eastern Headwaters | 825 / 19 | 0.57424 / 0.36596 | 0.64898 / 0.39956 | 0.67119 / 0.47004 |
| Gujarat/Kutch / Eastern Headwaters | 80 / 19 | 0.58242 / 0.39023 | 0.73355 / 0.39894 | 0.68167 / 0.23318 |

[Positional effects and support](main-2026-10-07-v1/region_comparisons.json), `positional_common_types`, `sensitivity.clear.a/b`, `raw/type_adjusted/site_type_adjusted.initial_js_bits/terminal_js_bits`. The Inter-Riverine–Lower Indus site/type basic intervals are **0.36632–0.51662** initially and **0.24891–0.43690** terminally. All positional intervals are in [region_intervals.json](exploratory-2026-10-07-v1/region_intervals.json), with the same conditional, uncalibrated scope as the frequency intervals. The table describes positional effects; the earlier permutation p-values apply to frequency divergence.

### Held-out sequence prediction

The fixed first-order model uses half-count unigram smoothing and transition shrinkage 20, including an initial context. Other-region and within-region models predict the same held-out faces. Exact object-type models and equal-type/equal-site face weighting give the following results. Positive excess means the other-region model loses more bits per sign.

| Region | Tested faces / families | Within-region bits | Other-region bits | Excess | Exploratory 95% interval | Training-size-matched excess [interval] |
|---|---:|---:|---:|---:|---:|---:|
| Inter-Riverine | 861 / 668 | 6.65469 | 7.29329 | 0.63860 | 0.53459–0.75535 | 0.26346 [0.09530–0.37548] |
| Lower Indus | 1,037 / 1,008 | 7.10144 | 7.37572 | 0.27428 | 0.11884–0.44392 | 0.18223 [0.03222–0.33147] |
| Gujarat/Kutch | 114 / 114 | 7.58400 | 6.51644 | −1.06756 | −1.48527 to −0.62911 | −0.03030 [−0.18635 to 0.15856] |

Point estimates and exact per-fold training denominators come from [regional_models.json](main-2026-10-07-v1/regional_models.json), `adjusted.test`, `adjusted.losses`, `training`. The intervals come from [model_intervals.json](exploratory-2026-10-07-v1/model_intervals.json), `losses.type_excess/size_excess`. They resample saved test losses and condition on fitted models. Unknown batch dependence among separate artifacts and training-refit uncertainty remain unmeasured. Equal training-component counts can still yield different token counts.

The raw token-weighted other-minus-within differences on these same test faces are **0.22941**, **0.68615** and **−0.58101 bits**, respectively. Gujarat's pooled advantage largely disappears when training component counts are matched. Eastern Headwaters and Upper Indus have no object type meeting the 20-training-face rule in every fold. [regional_models.json](main-2026-10-07-v1/regional_models.json), `raw.losses.raw_excess.token_weighted_mean`, `supported_types`, `support_by_fold`.

Withholding an entire site gives a type-model mean loss for Harappa of **8.01667 bits** on **188 faces**, trained on **47** other Inter-Riverine faces; Mohenjo-daro gives **7.51130 bits** on **770 faces**, trained on **65** other Lower Indus faces. These site-transfer populations differ from the regional table. Many peripheral site tests contain only one to six faces. [regional_models.json](main-2026-10-07-v1/regional_models.json), `within_region_leave_site_out`, `test`, `train`, `type_mean_bits`.

## 3. External and non-canonical inscriptions

The declared external set contains **42 faces/families**, **149 known tokens** and **19 unreadable slots**. Of **16 clear ordered faces**, **9** fail exact type/length comparator support, leaving **7** matched objects: **3 Persian Gulf, 1 Mesopotamian, 1 Iranian Plateau and 2 Central Asian**. The matched types are square seals, an incised tablet and pottery graffiti. All circular SEAL:C candidates are excluded from the paired endpoint. [external_models.json](main-2026-10-07-v1/external_models.json), `external_all`, `external_eligible`, `matched_faces`, `matched_cells`, `by_region`; [coverage](exploratory-2026-10-07-v1/external_coverage.csv). Detailed memberships and exclusions remain local under `data/raw/2026-10-06-chronology-region/main-2026-10-07-v1/`.

Each matched external face is scored by the same core fold-complement model as its exact length/type comparator faces. The pooled model gives **7.47287 external versus 7.55918 matched-core bits per sign**, excess **−0.08632** [**−2.20257, 2.22760**]. Exact-type models give **7.87617 versus 7.22528**, excess **0.65090** [**−0.37986, 1.85719**], two-sided component sign-flip p **0.380**, Holm **1.000**. Leaving out one external object gives adjusted excess **0.22658–0.98220**. The sign-flip reference assumes symmetry of independent matched component differences; seven objects provide limited evidence for that assumption. [external_models.json](main-2026-10-07-v1/external_models.json), `results.raw_loss/raw_core_loss/raw_excess/type_loss/type_core_loss/type_excess`.

Adjusted internal-bigram novelty excess is **0.05269** [**−0.17347, 0.27994**] over seven objects; trigram novelty excess is **0.10629** [**−0.10270, 0.26747**] over four objects. Both corrected p-values are **1.000**. The region-specific rows are descriptive; a one-object interval has no between-object sampling information. [external_models.json](main-2026-10-07-v1/external_models.json), `results.type_novel2_excess/type_novel3_excess`, `by_region`. The supplemental [unpaired scores](exploratory-2026-10-07-v1/unpaired_external_scores.csv) include unsupported types as acquisition diagnostics, with training counts beside each value.

Laursen (2010), *The westward transmission of Indus Valley sealing technology: origin and development of the ‘Gulf Type’ seal and other administrative technologies in Early Dilmun, c.2100–2000 BC*, distinguishes morphological groups and discusses unusual prefixed twins. Only the publisher abstract was accessible here. This class is poorly represented in the matched endpoint. [Publisher abstract](https://onlinelibrary.wiley.com/doi/10.1111/j.1600-0471.2010.00329.x/full), abstract paragraphs 1–2; [source access record](sources.json), `laursen2010`.

Parpola's *Indus Seals and Glyptic Studies: An Overview* (2018), author-proof section I.C, PDF pages 4–6, corroborates finds at Kish, Umma, Gulf sites, Altyn Depe, Gonur and Shortughai. Frenez chapter captions reproduced on Harappa.com supply Salut and Susa leads. These are site/type checks; individual local rows and graphic codes were not authenticated from excavation plates. Several Baluchistan and Gulf entries were not located in the inspected passages. [Parpola proof](https://tuhat.helsinki.fi/ws/portalfiles/portal/127255979/Parpola_Asko_2018_Indus_Seals_and_Glyptic_Studies_An_Overview_final_proof_2016_.pdf); [Frenez caption excerpts](https://www.harappa.com/content/indus-valley-early-commercial-connections-central-and-western-asia), images 1–2; [site-level checklist](exploratory-2026-10-07-v1/external_literature_check.csv), `scope`.

## Precedents and what this package adds

| Opened precedent | Relationship to this work |
|---|---|
| Nisha Yadav, 2013, *Sensitivity of Indus Script to Site and Type of Object*, SCRIPTA 5:67–103. [Article](https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf), pp. 79–81, 91. | Site/type differences in frequency and length, and West Asian differences, precede this package. The present contribution is a separate ICIT/Wells-code measurement with explicit adjustment and component references. |
| Ayuha Suga, 2024, *Diachronic Changes in the Indus Script: Based on the Proposed Arrangement of the Indus Seal*, Journal of General Linguistics 26–27:25–65. [Article](https://www.lingua.tsukuba.ac.jp/ippan/JGL/2024/GL26-27_3_paper2.pdf), pp. 32–34, 47. | Direct diachronic precedent, using 1,137 stylistically classified seals and the Parpola inventory. This package uses export context labels, several object types and interval-censored attestations. It does not replicate Suga's classifications. |
| Rajesh P. N. Rao, Nisha Yadav, Mayank N. Vahia, Hrishikesh Joglekar, R. Adhikari and Iravatham Mahadevan, 2009, *A Markov model of the Indus script*, PNAS 106:13685–13690. [Author PDF](https://homes.cs.washington.edu/~rao/PNASIndus.pdf), Table 2, PDF page 5. | External-text likelihood comparison precedes this package. The new local assay adds exact length/type matching and component-separated comparator prediction. Its seven-object result does not settle the broader eight-text comparison in that paper. |
| Michael Philip Oakes, online 2017 / issue 2019, *Statistical Analysis of the Tables in Mahadevan’s Concordance of the Indus Valley Script*, Journal of Quantitative Linguistics 26:22–47. [Author manuscript](https://wlv.openrepository.com/bitstreams/8f84dd81-ba40-4036-86aa-992596cf289c/download), PDF page 3. | Positional and metadata associations are established comparison targets. This package supplies separately defined sample and reference controls. |
| Andreas Fuls, 2022, *Corpus of Indus Inscriptions*, Mathematica Epigraphica 3, independently published, Berlin. [35-page excerpt](https://www.researchgate.net/profile/Andreas-Fuls/publication/373522666_Corpus_of_Indus_Inscriptions/links/64f044280f7ab20a86674daa/Corpus-of-Indus-Inscriptions.pdf), sections 1.3–1.4. | ICIT temporal/spatial catalogue analysis is prior work. The full book's quantitative claims were not audited in this package. |
| Gregg Jamison, Akinori Uesugi and Yuji Yamaguchi, 2023, *Unicorns and seals: New multivariate approaches to exploring patterned stylistic variation in the Indus Civilization*, Archaeological Research in Asia 36:100486. [University abstract/record](https://okayama.elsevierpure.com/en/publications/unicorns-and-seals-new-multivariate-approaches-to-exploring-patte/). | Recent multivariate spatial/diachronic seal research; full article not opened. It addresses stylistic attributes rather than this exact frequency endpoint. |

The bounded 2020–2026 search found direct recent precedents. This package refines sampling, matching and uncertainty in a particular preserved export; publication priority is not established. Exact bibliographies, access scope and failed routes are in [sources.json](sources.json). The motivating Frenez video landing page was opened, but its recording and transcript were not reviewed.

## Records that would sharpen the answers

Harappa needs more securely contextualized 3A objects, HARP field/unit joins for the **873 3B/C and 222 broad Period 3 faces**, and source checks for manufacture age versus redeposited context. [Label counts](main-2026-10-07-v1/harappa_label_type_strata.csv), `time`, `faces`. Kenoyer and Meadow describe contextual/stylistic reassignment in printed xlvii, including H-1537; neither H-1537 nor H-1539 joined the current register under the searched CISI bases. [Primary discussion](https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf), PDF page 6; [join check](source-join-check.json), `checks.matching_faces`. Comparable dated square-seal samples in 3B and 3C would separate chronological change from tablet production more directly.

Regional tests need several adequately sampled sites per region within the same object types. Batch/mould relationships and alias revisions would change the reference units. A harmonized sign inventory and independently reviewed transcriptions would support comparison across the different coding systems used by earlier papers.

External tests need a morphology-coded inventory separating Gulf-type, standard square, cylinder and local impression classes, plus original plates and find contexts for each row. Comparable core circular-seal texts are currently too scarce for the declared match. More complete, direction-resolved Gulf inscriptions would test Laursen's class directly. Additional dated records should enter a new endpoint with its own protocol.

## Verification and unresolved checks

The independent checker rebuilt **three sign-count tables**, recomputed **23 divergence effects**, replayed **104 regional and 14 external model fits/scores**, checked all match and fold exclusions, and verified **10 downloaded payload hashes**. The main run asserted preserved margins for **7,485 permutation allocations**. The supplement checker confirmed **14 unchanged effect groups**, **54 supported intervals with all 499 replicates**, **18 unchanged model means**, actual fold totals and **41 sampled type-presence counts**. [Main verification](verification-2026-10-07-v1.json); [supplement verification](verification-supplement-2026-10-07-v1.json).

Permutation draws, bootstrap intervals and training-size sampling require a full fresh-directory rerun for independent replay. The confidence intervals have not received a simulation calibration audit. Individual archaeological identifications, the full Laursen/Fuls/Frenez sources and a video timestamp remain unverified. [README.md](README.md) gives the commands and reviewer checks; [RETROSPECTIVE.md](RETROSPECTIVE.md) preserves the observed failures and fixes.
