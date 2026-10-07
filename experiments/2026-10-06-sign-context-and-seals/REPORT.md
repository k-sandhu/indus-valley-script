# Sign frequency, motif concentration and seal dimensions

Sign 740 accounts for 1,928 of 19,946 observed positions (9.67%), or 10.67% of 18,067 readable positions. Its frequency differs across object types, but the site comparison after conditioning on object type gives p = 0.4896 and q = 0.5379. Among the ten most frequent signs, only 032 retains a site association after correction (q = 0.002). No sign has a supported site-area association across the original and amended reference laws. Known square-seal motifs are concentrated: 1,246 of 1,609 are unicorns (77.44%), with HHI = 0.6054. Unicorn texts average 0.7752 positions longer than texts on rare motifs, conditional on site and object type (q = 0.0012). Complete square-seal sizes have CV = 0.2886; larger faces carry more text, with a fitted increase of 1.1590 positions per doubling of face area (q = 0.0002). Each result is detailed below with its denominator and output field.

Status: **Verified computation** for arithmetic and deterministic rerun; **Frozen evaluation** for the original specified endpoint; **Exploratory** for the dated sensitivity and supplemental coverage analyses. External source sampling by the separate reviewer remains outstanding.

## Observations and reference laws

The pinned export has 5,680 faces, 1,879 unreadable positions and 4,695 physical components. Unioning `object_family_id` and unambiguous CISI side aliases adds no new cross-family component in this export. Five nonblank ambiguous references remain unresolved. No component has conflicting site or object-type labels. Inference uses the longest face per component, breaking ties by record identifier; seal comparisons choose the longest seal face in each component. This yields 2,239 seal components. Repeated texts on separate objects remain separate observations because text repetition is an outcome. Counts, hashes and selection totals are in [input-summary.json](run-2026-10-07-01/input-summary.json), fields `faces` through `unresolved_nonblank_cisi`; object identities and selection audits remain local-only.

The [protocol](PROTOCOL.md) preceded computation and fixes the ten signs, source table, family rule, 9,999 permutations, 2,000 bootstrap draws and correction families. Whole objects retain their sign sequences and metadata in resampling. Site labels move within exact object-type blocks; motif labels move within site and exact object type. These are conditional exchangeability assumptions about the acquired objects. Excavation and cataloguing selection can violate an archaeological interpretation of those assumptions. The binomial regressions describe the acquired counts with object-type fixed effects and site-cluster standard errors; permutation supplies the reported association tests. The [amendment](AMENDMENT-2026-10-07.md) records both post-outcome changes before their computation.

The package reused ROOT-09's context work, `src/context_study.py`'s family and principal-face approach, the checked reading-order convention in `research/corpus/orientation_clarification.json`, and Paper 002's treatment of related records. It inspected the earlier classifier endpoint `results/context/confirmatory/bull1_other.json`: 1,086 objects, 1,020 artifact/string groups, gain −0.062575 nats per object and permutation p = 0.8055. That predictive endpoint was not rerun. The present text statistics answer different questions and use physical grouping without merging distinct objects by repeated text.

## Sign frequency, site area and site function

All-face frequencies preserve the lecture's denominator. The intervals below resample complete physical components within a site; the component count includes components whose faces have no readable sign. All sites and all ten signs appear in [site-frequencies.json](run-2026-10-07-01/site-frequencies.json), fields `count`, `readable_positions`, `components` and `component_bootstrap_95_ci`.

| Site | Components | 740 / readable positions | Frequency | 95% component bootstrap interval |
|---|---:|---:|---:|---:|
| Harappa | 1,921 | 779 / 7,178 | 10.85% | 10.27–11.38% |
| Mohenjo-daro | 1,795 | 844 / 7,809 | 10.81% | 10.27–11.34% |
| Dholavira | 230 | 63 / 637 | 9.89% | 7.68–12.32% |
| Kalibangan | 197 | 57 / 513 | 11.11% | 8.78–13.66% |
| Lothal | 182 | 72 / 680 | 10.59% | 8.71–12.50% |
| Chanhu-daro | 72 | 30 / 324 | 9.26% | 6.87–11.89% |
| Nausharo | 38 | 11 / 131 | 8.40% | 5.11–12.08% |
| Banawali | 26 | 5 / 62 | 8.06% | 1.82–15.52% |

Small zero-count samples can have degenerate empirical bootstrap intervals. They cannot establish an absent sign population. Principal-face object types also have different 740 proportions: square seals 763/7,336 (10.40%), `TAB:B` 348/2,480 (14.03%), `TAB:I` 219/1,318 (16.62%), `TAB:C` 114/901 (12.65%), rectangular seals 151/1,638 (9.22%) and `POT:T:g` 94/911 (10.32%). These export categories are retained without assigning administrative meanings. See [sign-analysis.json](run-2026-10-07-01/sign-analysis.json), `object_type_frequencies`.

The site omnibus uses 4,613 readable principal objects across the export, and scores nine labels with at least 20 such objects, including `Unknown`. The table gives Benjamini–Hochberg q across ten signs. It also gives the amended size test, which keeps areas fixed and moves whole object site labels within type blocks. See `site_omnibus.tests` in `sign-analysis.json` and `site_size_grouped_permutation.3.tests` in [results.json](exploratory-2026-10-07-01/results.json).

| Sign | Site p | Site q | Area correlation, 17 sites | Amended area q |
|---|---:|---:|---:|---:|
| 740 | 0.4896 | 0.5379 | 0.0836 | 0.9494 |
| 002 | 0.0358 | 0.0974 | 0.1208 | 0.9494 |
| 032 | 0.0002 | 0.0020 | 0.4559 | 0.3903 |
| 700 | 0.0487 | 0.0974 | 0.2337 | 0.9494 |
| 033 | 0.0327 | 0.0974 | −0.0603 | 0.9500 |
| 400 | 0.0418 | 0.0974 | 0.2834 | 0.9494 |
| 220 | 0.1010 | 0.1683 | 0.2317 | 0.9494 |
| 240 | 0.1325 | 0.1893 | 0.5479 | 0.3903 |
| 520 | 0.2102 | 0.2628 | 0.6642 | 0.2230 |
| 390 | 0.5379 | 0.5379 | 0.0123 | 0.9768 |

For 032, Chanhu-daro has 21 occurrences against 7.633 expected from its types, while Kalibangan has 10 against 20.159. This is a site-distribution result; neither the code's value nor the contrast establishes a sound or function. The exact residuals are in `sign-analysis.json.site_residuals`, rows for sign 032.

The sourced area table contains 18 sites. Seventeen qualify for the size comparison, contributing 4,427 readable principal objects; Ganweriwala has only two. Ten of the 17 sites have fewer than 20 readable objects. Published anchors, qualifiers, source locations and functional classifications are in [site-table.json](site-table.json); join counts are in `sign-analysis.json.sourced_site_eligibility`.

| Site | Reference area, ha | Other compiled anchors / qualifier | Site type | Readable principal objects | Sources |
|---|---:|---|---|---:|---|
| Harappa | 150 | Open lower bound | Urban centre | 1,877 | K1997, K2005 |
| Mohenjo-daro | 250 | 100–250; 250 is open lower bound | Urban centre | 1,784 | K1997, K2005, S2019 |
| Dholavira | 100 | Estimate | Urban centre | 219 | K1997, K2005 |
| Rakhigarhi | 80 | Open lower bound; criteria uncertain | Urban centre | 12 | K1997, S2019 |
| Ganweriwala | 80 | Open lower bound; excluded from model | Urban centre | 2 | K1997 |
| Kalibangan | 11.5 | 11.5–12.1 | Town | 189 | S2019, K2005 |
| Lothal | 7.5 | 7–7.5; differing extent definitions | Port | 181 | K2005, U2014 |
| Chanhu-daro | 6 | Settlement estimate; see source note | Craft settlement | 70 | K2005 |
| Farmana | 18 | Calculation criteria uncertain | Town | 7 | S2019 |
| Alamgirpur | 1 | Estimate | Rural settlement | 3 | S2019 |
| Amri | 8 | Estimate | Function unverified | 5 | K2005 |
| Allahdino | 1 | Estimate | Function unverified | 12 | K2005 |
| Kot-Diji | 1 | Estimate | Function unverified | 10 | K2005 |
| Rupar | 3.5 | Estimate | Function unverified | 3 | K2005 |
| Bala-kot | 4 | Estimate | Function unverified | 7 | K2005 |
| Surkotada | 2.6 | Estimate | Function unverified | 6 | K2005 |
| Nausharo | 4 | Estimate | Function unverified | 38 | K2005 |
| Rodji, source Rojdi | 5.3 | Estimate | Function unverified | 4 | K2005 |

K1997 is Kenoyer's printed p. 54/Table 4.2. S2019 is Suryanarayan's printed p. 87/Table 4.1, supplemented by the Kalibangan description on printed p. 122. K2005 is Kenoyer's settlement-hierarchy paragraph in Treccani, supplemented by Vidale's **Chanu daro** section for craft production. U2014 is the Lothal tentative-list Description, first paragraph. Full titles, authors, venues, URLs and access status are in [sources.json](sources.json). The [source notes](SOURCE-NOTES.md) distinguish visible bounding extent from settlement area and record the post-outcome heading correction. The area spans are published numerical anchors, not statistical intervals; the open bounds have no established maximum.

All 30 binomial fits converge. For 740, the object-adjusted area coefficient is 0.01409 per doubling of area, an odds ratio of 1.0142, with descriptive site-cluster SE 0.01649. Adding site type changes that coefficient to 0.07686 (SE 0.06048). The data have one port, one craft-class site and one rural-class site, with only three readable objects at the rural site. Type coefficients therefore describe these selected sites and cannot estimate a general port or craft effect. The fits, numerical penalty and design ranks are in `sign-analysis.json.binomial_models`.

The original area-vector permutation gives 520 correlation 0.6642, p = 0.0044 and q = 0.044. Its minimum/maximum compiled-area checks have q = 0.044/0.047, but excluding Harappa and Mohenjo-daro raises q to 0.387. The amended whole-object law gives p = 0.0223 and q = 0.223 for the same 17-site statistic. Restricting to seven sites with at least 20 readable objects gives 520 q = 0.5275, and every sign has q ≥ 0.5275. Thus the package does not retain a corrected area claim. Better tests require contemporaneous mapped occupation areas and additional independently sampled objects at small sites; adding another label to the existing tiny samples would not resolve the precision problem.

## Motif concentration and text differences

All known seal motifs have unicorn share 75.54% (1,248/1,652) and HHI 0.5776; 587 of the 2,239 seal components have unknown or absent motifs. Square seals have 127 such records, leaving 1,609 known motifs, 34 categories and HHI 0.6054, equivalent to 1.652 equally abundant categories. The unicorn share's Wilson interval is 75.33–79.41%. The next square-seal categories are Gaur 85, Zebu 57, Elep 41, Bull 33, Rhin 25, Tigr 17 and Buff 15. The complete rank–abundance vectors, shares and intervals are in [motif-concentration.json](run-2026-10-07-01/motif-concentration.json), rows selected by `population`, `level` and `group`.

| Square-seal site | Known motifs | Unicorns | Unicorn share | HHI |
|---|---:|---:|---:|---:|
| Chanhu-daro | 50 | 41 | 82.00% | 0.6808 |
| Dholavira | 72 | 59 | 81.94% | 0.6763 |
| Harappa | 286 | 247 | 86.36% | 0.7487 |
| Kalibangan | 41 | 28 | 68.29% | 0.4789 |
| Lothal | 40 | 35 | 87.50% | 0.7700 |
| Mohenjo-daro | 1,019 | 779 | 76.45% | 0.5917 |

Each of these six adequately sampled sites has a unicorn majority and minority motifs. Regional square-seal samples show Gujarat/Kutch 103/123 unicorns (HHI 0.7044), Inter-Riverine 277/332 (0.6993), and Lower Indus 845/1,099 (0.5982). Eastern Headwaters has 9/27 and falls below the protocol's 30-object comparison threshold. These are export region labels, with full rows in the same output.

Harappa's raw period labels give Period 3B/C 59/70 unicorns, 3C-1 25/34, 3C-2 35/35 and 3C-3 33/34. The 3C-2 sample contradicts the strict prediction of minority motifs in every adequately sampled period. Ambiguous labels remain separate, and the unspecific period records cannot provide an ordered civilization-wide trend. The output also contains the predeclared coarse 3C grouping, with its component count. The concentrated distribution supports the measurable part of Frenez's description. Workshop dominance, institutional selection and uneven excavation can also produce these shares. Production provenance, carving-style clusters and find-context denominators would distinguish those explanations.

The clean-text comparison includes 910 unicorn objects and 155 rare-motif objects. A rare category has less than 5% of all 1,652 known seal components; Gaur is above that threshold and is omitted from the rare cohort. Texts must be complete observed, single-line, have a specified direction and contain no unreadable code. The permutation has 33 site/type blocks, 14 containing both labels and 1,036 movable objects. The shared sign coding and reading-order convention are held fixed.

| Outcome | Unicorn | Rare motifs | Difference or divergence | Primary q |
|---|---:|---:|---:|---:|
| Mean positions | 4.7945 | 4.0194 | +0.7752 | 0.0012 |
| Sign inventory | 416 | 167 | +249 | 0.3031 |
| Distinct texts / objects | 853/910 | 149/155 | −0.02393 | 0.4275 |
| Sign-token distribution, JS bits | Joint comparison | Joint comparison | 0.146319 | 0.0033 |
| Initial-sign distribution, JS bits | Joint comparison | Joint comparison | 0.340463 | 0.2178 |
| Terminal-sign distribution, JS bits | Joint comparison | Joint comparison | 0.170754 | 0.0832 |

All counts and tests are in [motif-association.json](run-2026-10-07-01/motif-association.json), `primary_rare.unicorn`, `primary_rare.other` and `primary_rare.tests`. Raw inventory differences reflect unequal cohort sizes; the grouped references retain those sizes. Distinct-text rate means the number of distinct sequences divided by objects, rather than the proportion of objects with singleton texts.

The exploratory length-conditioned law adds exact recorded length to site/type blocks. It leaves 871 objects movable in 29 mixed blocks. Sign-token divergence then has p = 0.0813 and q = 0.20525 across five variable outcomes; the length difference is invariant by construction. This analysis does not demonstrate a motif-specific sign distribution beyond length. See `results.json.motif_length_conditioned`, with the enclosing **Exploratory** status and the inherited helper-label note in `SOURCE-NOTES.md`.

Within-site comparisons qualify at Harappa (158 unicorn/19 rare), Kalibangan (16/7) and Mohenjo-daro (605/99). Mean-length differences are 1.3598, 2.3750 and 0.4072 positions respectively. No one of the 18 site/outcome tests survives joint correction; the minimum q is 0.0885. This leaves site-specific effects unresolved. Including all non-unicorn motifs yields 229 objects averaging 4.3712 positions: its length comparison has p = 0.0138 and q = 0.0828. The corrected global length result therefore applies to the declared rare cohort. Carving-style assignments and larger minority cohorts at individual sites would test whether it reflects workshops or specific social uses.

## Seal size and standardization

Of 1,736 square-seal components, 1,565 have positive horizontal millimetres, 1,490 positive vertical millimetres and 573 a positive scalar thickness. Both face dimensions are present for 1,451. Exactly 1,027 of these have preservation labelled `complete`, forming the primary sample. Zero is treated as missing; thickness ranges remain nonnumeric. Supplemental coverage of all 2,239 seal components gives 1,904 positive horizontal, 1,879 positive vertical and 734 scalar thickness measurements. Rectangular seals have both face dimensions for 305/380 objects. See [dimensions.json](run-2026-10-07-01/dimensions.json), `positive_dimensions`, `preservation_counts`, and [dimension-coverage.json](supplement-2026-10-07-01/dimension-coverage.json), `dimension_missingness` and `type_groups`.

Characteristic square-seal size is the square root of horizontal times vertical millimetres. Complete seals have mean 26.3305 mm, SD 7.5989, CV 0.2886 and median 25.4 mm. The interquartile range is 21.4896–30.2 mm; the full positive range is 8.2244–68.6 mm. Including all preservation states gives n = 1,451 and CV 0.2863. Exact quantiles, both dimension distributions, area summaries and 2 mm histograms are in `dimensions.json.groups`.

| Complete square-seal site | n | Mean characteristic size, mm | CV |
|---|---:|---:|---:|
| Harappa | 173 | 27.9751 | 0.3262 |
| Mohenjo-daro | 639 | 26.4484 | 0.2811 |
| Dholavira | 45 | 23.5657 | 0.1860 |
| Kalibangan | 32 | 24.9720 | 0.2108 |
| Lothal | 35 | 24.9347 | 0.2392 |
| Chanhu-daro | 44 | 26.7921 | 0.2752 |
| Nausharo | 10 | 26.7963 | 0.1438 |
| Banawali | 13 | 20.1369 | 0.3817 |

No site with at least ten observations meets the protocol's operational CV ≤ 0.10 narrow-size criterion. Motif CVs include unicorn 0.2892 (n = 787), Gaur 0.2099 (57), Elep 0.1893 (24), Zebu 0.2405 (26) and Rhin 0.3367 (20). The unicorn–rare CV difference is 0.01316, p = q = 0.6459, with 787/137 objects. Harappa's better sampled periods have CV 0.2691 for 3B/C (35), 0.2614 for 3C-1 (23), 0.2896 for 3C-2 (22) and 0.2494 for 3C-3 (23). These records describe a broad size population. Separate size classes, shape conventions and standardized carving practices remain compatible with that result. Rounded catalogue conversions also affect apparent modes, as documented in `SOURCE-NOTES.md`.

The fitted length increase per doubling of square-seal face area is 1.1590 positions after adjustment for site and pooled motif, using all 1,027 complete measured objects. Permuting length within site/motif/type blocks leaves 963 objects movable and gives zero exceedances in 9,999 draws: p = 0.0001, q = 0.0002 across the two dimension tests. The ordinary OLS SE is 0.08080 and unadjusted Spearman correlation is 0.4357; those are descriptive. See `dimensions.json.tests`, outcome `length_per_doubling_area_adjusted_site_motif`. Larger usable faces and longer texts are associated in the export. A production-standardization test needs calibrated original measurements, size-class hypotheses defined before fitting, preservation checks and workshop/style assignments.

## Relation to published work and source gaps

Nisha Yadav's 2013 *Sensitivity of Indus Script to Site and Type of Object*, **Scripta** 5:67–103, directly precedes the site/object question. Its acquired PDF, especially printed pp. 67–71 and 75–76, motivates keeping those contexts separate. Michael Philip Oakes's *Statistical Analysis of the Tables in Mahadevan’s Concordance of the Indus Valley Script*, online 2017 and **Journal of Quantitative Linguistics** 26(1), 2019:22–47, directly addresses inscription/iconography relations in section 4, Tables 7–10 and Figure 6. These package results extend an established question to this export and physical-object reference laws; they establish no priority claim. See sources Y2013 and O2019 in [sources.json](sources.json).

Dennys Frenez's 2018 *Private Person or Public Persona? Use and Significance of Standard Indus Seals as Markers of Formal Socio-Economic Identities*, in **Walking with the Unicorn**, proposes the oligopoly/social-identity interpretation. The inspected preview's pp. 186–187 describe roughly 65% unicorns in its reference corpus; our 77.44% is from known square motifs in this export and has a different denominator. Its p. 167 discusses size/style variation and workshops. Adam Stuart Green's 2021 *Killing the Priest-King: Addressing Egalitarianism in the Indus Civilization*, **Journal of Archaeological Research** 29:153–202, discusses seals, corporate groups and social organization. Their political interpretations need the independent context and production evidence identified above. See F2018 and G2021, including their precise access notes.

Jonathan Mark Kenoyer's *Indus Seals: An overview of Iconography and Style*, **Ancient Sindh** 9, issue 2006–2007:7–30, supplies the seal-production/style context; the downloaded filename says 2009, so the bibliographic issue and filename are recorded separately. Marta Ameri and Gregg Jamison's 2022 *Mixed Methodologies: Collaborative Approaches to Indus Tiger Seals*, **South Asian Studies** 38(1):69–99, and Jamison and colleagues' 2017 *Inscribed Unicorn Seals from Bagasra, Gujarat: A Comparative Analysis of Morphology, Carving Styles, and Distribution Patterns*, **Heritage** 5:1–21, identify relevant style-based approaches. Their full texts were not reviewed here. Ayumu Konasukawa and Manabu Koiso's 2018 chapter *The Size of Indus Seals and its Significance* is a direct size precedent found in contents; its full analysis remains unverified. These gaps prevent a claim that the present CV analysis differs from those methods. See Koverview, A2022, J2017 and KK2018.

Rajesh P. N. Rao and colleagues' 2009 *A Markov model of the Indus script*, **PNAS** 106(33):13685–13690, concerns sequence structure. Rao's 2018 *The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor*, **Walking with the Unicorn**, pp. 518–525, proposes economic uses. The requested separate Rao et al. motif–text precedent was not bibliographically verified in the bounded search. Bahata Ansumali Mukhopadhyay's 2019 *Interrogating Indus inscriptions to unravel their mechanisms of meaning conveyance*, **Palgrave Communications** 5:73, and 2023 *Semantic scope of Indus inscriptions comprising taxation, trade and craft licensing, commodity control and access control: archaeological and script-internal evidence*, **Humanities and Social Sciences Communications** 10:972, propose functional interpretations. The present context tests do not discriminate among those semantic proposals. See R2009, R2018, B2019 and B2023.

Mahesh T C's 2026 arXiv:2604.23582v1, *Evidence for a Scale-Free Commercial Network in the Indus Valley Civilization: A Power Law Analysis of Harappan Seal Data*, interprets offering-stand distributions as commercial networks. The current abstract carries the changed title *Asynchronous Barter, Periodic Reconciliation: Evidence for a Scale-Free Commercial Network in the Indus Valley Civilization*. The local witnesses distinguish v1 full HTML from the current abstract. The export's Bull1 suffixes have not been mapped to offering-stand classes, so this package cannot reconstruct that network or test its power law. Motif concentration is a different descriptive quantity. See M2026v1 and M2026current.

The 18 source records give exact URLs, opened-versus-snippet status and local witness hashes. Failed downloads include the Dholavira nomination page (403), Frenez's direct preview (403), Ameri's publisher page (403), a settlement-area PDF with connection reset, and an empty publisher-contents response. The report uses no area from those failures. Reviewer priorities are the uncertain site boundaries, the mixed Chanhu-daro function, three unread style/size papers, and the unidentified Rao motif item. All acquired third-party payloads remain in the ignored local raw directory.

## Computation checks

An exact second run reproduces the hashes of all five analytical outputs. [checks-2026-10-07-01.json](checks-2026-10-07-01.json) records 106 passing checks, zero failures and 82 tail probabilities independently recomputed from saved local reference arrays. Checks reconstruct token totals, grouping counts, square-motif counts, HHI and complete-seal CV, exercise transitive aliases, preserve block counts and verify the invariant length-conditioned statistic. [final-checks-2026-10-07-01.json](final-checks-2026-10-07-01.json) adds 43 passes, including 26 exploratory tails, an independent SciPy check of every correction family and a byte-identical supplement rerun. The combined count is 149 passes and zero failures. Commands for a fresh reviewer run and source sampling are in [README.md](README.md). These checks certify reproducibility and arithmetic within the recorded assumptions; the source and archaeological checks remain separate.
