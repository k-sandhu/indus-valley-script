# Review of package D1: chronological and regional sub-corpora, and non-canonical inscriptions

Reviewer: Claude Sonnet 5.5, 7 October 2026. Package produced by GPT-6.1-Sol, including the post-launch amendment of 7 October. No package file was edited. Everything I wrote is in this file, in `review/`, and under the local raw directory (`reviewer-*`, ignored by Git).

## Verdict

The main results stand as computed. Rerunning every command in the README with the declared seeds reproduced all 60 aggregate files and all 17 record-level detail files; each of the 380 numbers I compared with the saved fields matched, and a plain-Python recomputation gave the same 3B–3C divergence, 0.190483 bits. The original protocol was committed (3183b4d, 00:02:54) before the first outcome file existed (00:04:52). The most important problem is that the 3B and 3C samples come from different excavations and labelling sources that the report does not describe or adjust for: 71% of the unambiguous 3C faces but 4.5% of the 3B faces carry a stratum number and a catalogue number from the earlier-excavation range, and 90% of the 3B faces come from Mound E against 72% of the 3C faces from Mound F. The media-diversity comparison therefore does not account for excavation differences. In subsets built with the package's own functions the media rise and the sign-frequency divergence persist, but the adjusted length increase falls from 0.72 to 0.16 slots. Two lesser problems remain: 499 permutation draws are too few for some reported statuses (Period 2–3C Holm .044 becomes about .060 at 19,999 draws, and sign 034 then passes BH .05), and the Jensen–Shannon effects are mostly sampling noise (0.190 bits against a permutation-null mean of 0.158, with both bootstrap intervals excluding the estimate).

## How to read this review

"Reproduced" means that a fresh run gave identical aggregates (relative tolerance 1e-9) and byte-identical detail files. The scripts write to `<package directory>/<run name>`, which a reviewer restricted to `review/` cannot use. I therefore ran the package's own scripts unchanged through `review/run_review_step.py`, which sends the aggregates to `review/rerun/` and the record-level details to `data/raw/2026-10-06-chronology-region/reviewer-*`. Analyses marked "reviewer check" are mine, use the package's own functions on subsets or with more draws, and are not package results. They are in `review/`, each with its script and a small JSON output of counts.

## Checked claims

Paths are relative to the package directory. All 380 quoted numbers, with the field each was read from, are in `review/number_checks.tsv`; the rows below group them.

| # | Claim | Evidence path | Result | Note |
|---|---|---|---|---|
| 1 | 5,680 faces, 18,067 known tokens, 1,879 unreadable slots, 4,695 physical families, 713 codes, 2,930 clear faces | `main-2026-10-07-v1/audit.json` | confirmed | Alias components number 4,695, equal to the distinct `object_family_id` count, so the CISI-base alias step merges nothing in this export. |
| 2 | Input hash `1220f559…`, reused code hash `ed150239…` | README; `audit.json` | confirmed | Both recomputed from the files. |
| 3 | HARP dates 2600–2450, 2450–2200, 2200–1900 BCE for 3A, 3B, 3C | Kenoyer and Meadow 2010 Table 1 (PDF p. 4); Beas Table 1; Kenoyer 2020 Table 1 | confirmed | Kenoyer 2020 dates Periods 4 and 5 together as 1900–1700; the 2010 table gives 1900–1800(?) and 1800(?)–<1300. No computation uses these dates. |
| 4 | Harappa label counts (3B 201 faces, 3C 574, 3B/C 873, broad Period 3 222, undated 778) | `harappa_major_type_strata.csv`; `period_mapping.json` | confirmed | |
| 5 | 3B vs 3C adjusted JS 0.190483 bits, raw 0.20208, common-support 0.19223; 186 vs 451 faces | `time_comparisons.json` | confirmed | The plain-Python recomputation also gives 0.190483 and 455 vs 1,547 tokens. |
| 6 | Family-reference p .022, Holm .044 (110 vs 335 families) | `permutation_tests.json` | confirmed; stable | 19,999 draws, two seeds: p .0199 and .0192, Holm .040 and .038. |
| 7 | Text-closure p .068 (89 vs 148 faces) | `permutation_tests.json` | confirmed; stable | 19,999 draws: .067 and .064. |
| 8 | Period 2–3C pottery JS 0.61781, Holm .044 | `permutation_tests.json` | discrepancy | Reproduced as saved. At 19,999 draws p is .0600 and .0603, Holm .060, so the comparison no longer passes .05. |
| 9 | Adjusted length increase 0.72395 slots [0.36473, 1.04572] | `time_comparisons.json` | confirmed as computed | The value depends on label source; see finding 4. |
| 10 | No time sign passes BH .05 (24 tests, smallest q .072) | `sign_tests.csv` | discrepancy | Reproduced as saved. At 19,999 draws sign 034 has p .0018 and q .0432 (one seed). |
| 11 | Four of six regional pairs pass Holm .05 under family references, one under text closure | `permutation_tests.json` | confirmed; stable | At 9,999 draws, two seeds, the same four pairs pass (Holm ≤ .0036); the other two have Holm .086. |
| 12 | None of 314 regional sign tests passes BH .05 | `sign_tests.csv` | confirmed | At 9,999 draws the smallest q is .0785. |
| 13 | Held-out other-minus-within excess 0.63860, 0.27428, −1.06756; size-matched 0.26346, 0.18223, −0.03030 | `regional_models.json`; `exploratory-2026-10-07-v1/model_intervals.json` | confirmed | Intervals reproduced. |
| 14 | External: 42 faces, 7 matched, exact-type excess 0.650896 [−0.379864, 1.857194], sign-flip p .380 | `external_models.json` | confirmed | The pooled-model excess has the opposite sign (−0.08632); the REPORT gives it, the README does not. |
| 15 | Wells 090: 7/149 external vs 184/17,792 core; 091: 5/149 vs 22/17,792 | `post-launch-2026-10-07-v1/external_target_counts.csv` | confirmed | |
| 16 | Matched frame has 7 faces and 30 tokens, no target token; excess −0.28739 and −0.01228 points; Holm 1.000 | `external_frequency.json` | confirmed | |
| 17 | All 7 external 090 tokens and 5 external 091 tokens are on circular seals; reasons for exclusion | `post-launch-coverage-2026-10-07-v1/external_selection_counts.csv`; `external_match_coverage.csv` | confirmed | 090 occurs on 7 of the 11 circular-seal faces that fail the ordered-text filter. 091 occurs on 4 clear faces whose cells have 0 or 1 core family and on 1 unclear face. |
| 18 | Media: 115 vs 444 families, 5 vs 14 types, richness +4.598459 [3.191358, 6.143415] Holm .0145, Shannon +0.901051 [0.677074, 1.144351] Holm .001, 200 allocations positive | `media_comparison.json`; `media_interval_allocations.csv` | confirmed | Direction persists in subsets (finding 4). |
| 19 | Early set: 31 families, 37 tokens, 18 signs; later 31-family samples average 63.01051 signs and 128.97599 tokens; type/length +0.120190 [−1.435445, 4.165805], p .5335 | `early_inventory.json`; `early_adjusted_denominators.csv` | confirmed | The early set is 29 pottery graffiti, 1 tag and 1 seal. |
| 20 | Verification counts (23, 104, 14, 10, 7,485; 395,653, 81, 1,921, 248, 44, 20; 13,993 draws) | `verification-*.json` | confirmed | Rerun counts are identical. |
| 21 | Protocol written before outcomes | git 3183b4d; file times | confirmed for the original protocol | The post-launch protocol was never committed before its outcomes; only file times (00:40:58 against outputs at 00:49) support the order. |
| 22 | Wells 090 is the "man" glyph, 091 the "twins" glyph | `sign_identifications.json`; Mayig schema; atlas rows 26 and 31 | confirmed for 090; unverified for 091 | Finding 7. |
| 23 | Tracked outputs hold aggregates only | `review/tracked_output_scan.json` | confirmed | No sequence of three or more corpus signs and no `record_id` field in any tracked file; see finding 9 for single-face cells. |
| 24 | Site-level literature check: Ur corroborated by Parpola 2018, section I.C | `exploratory-2026-10-07-v1/external_literature_check.csv` | discrepancy | The passage never names Ur; the link is only the Gadd (1932) citation. The other six Parpola rows are supported. |
| 25 | Prose scan | `tools/review_prose.py` | confirmed | 0 flags; manual findings in finding 11. |
| 26 | Interval-censored labels handled as the protocol says | `interval_sensitivity.json`; `harappa_attestation_bounds.csv` | confirmed | 3B/C all to 3B gives JS 0.13475, all to 3C 0.18036, 100 uniform draws 0.09727–0.14236; 368 signs with bounds, 209 earliest and 89 latest unresolved; no family has conflicting labels. |
| 27 | Permutations exchange whole components within type blocks, never single faces | `analyze.py` `permutation()`; `permutation_tests.json` | confirmed | Blocks are exact type and face count; mixed-label and mixed-type components are dropped and counted; every draw asserts its margins. |
| 28 | The media-diversity comparison accounts for excavation differences | REPORT media section; `media_comparison.json` | discrepancy | It does not: rarefaction equalizes family counts only, and the export has no excavated volume or area. Finding 4. |

## Reproduction log

| Step | Command (through `review/run_review_step.py`) | Time | Outcome |
|---|---|---|---|
| Main analysis | `analyze --run reviewer-main-v1` | 329.7 s (author 375.2 s) | 31 of 31 aggregate files identical; 4 of 4 detail files byte-identical. |
| Main verification | `verify --run reviewer-main-v1` | 0.9 s | Passed; counts identical to `verification-2026-10-07-v1.json`. |
| Supplement | `supplement --main reviewer-main-v1 --run reviewer-exploratory-v1` | 109.1 s | 11 of 11 aggregate files identical; the one detail file byte-identical. |
| Supplement verification | `verify_supplement …` | 0.2 s | Passed (14, 54, 18, 41 checks as saved). |
| Catalogue join | `check_catalogue_join.py --check source-join-check.json` | seconds | Passed; H-1537 and H-1539 match no face. |
| Post-launch analysis | `post_launch --run reviewer-post-launch-v1` | 29.0 s (author 51.1 s) | 14 of 14 aggregate files identical; 12 of 12 detail files byte-identical. |
| Post-launch verification | `verify_post_launch …` | 0.8 s | 395,653 assertions, 81 immutable files, 1,921 families; check counts identical; coverage files identical. |
| Prose scan | `python tools/review_prose.py --path … --no-write` | seconds | 0 flags. |

Apart from elapsed times and run names, nothing differs. Identical outputs from a fixed seed show that the run is deterministic, not that the random draws are statistically adequate; the stability runs under finding 3 address that. I did not rerun `acquire_sources.py` or `acquire_post_launch_sources.py` because they download third-party files and I had no permission to download. I used the stored copies, checked all four post-launch payload hashes against both manifests, and the package's `verify.py` rechecks the ten original ones. I did not rerun `finalize_post_launch.py`, which writes into the owned directory; its preservation checks are covered by the 81-file hash check, the snapshot comparison and `git status` below. The system drive had no free space at about 01:14 and recovered to 5–7 GB within minutes; no review output was written during that period.

## Source checks

I opened fifteen sources from stored copies or with WebFetch and read the cited passages; Fuls 2022 I saw only through search snippets.

| Source | How opened | Result |
|---|---|---|
| Kenoyer and Meadow 2010, *Inscribed Objects from Harappa Excavations 1986–2007* | stored PDF text and contents page | Table 1 at printed xlv matches the dates used. The contents page assigns H-1020 to H-1520 to "Old excavations" and H-1521 to H-2583 to HARP excavations (finding 4). |
| Beas chronology page | stored HTML | Table 1 identical to the 2010 table. |
| Kenoyer 2020, *Origin and Development of the Indus Script* | stored PDF text | Title, editor, pages 217–236, Tables 1–2 confirmed. Table 2 lists inscribed tablets and wider media from 3B and many more classes in 3C. |
| Yadav 2013, SCRIPTA 5:67–103 | stored PDF text | Title, pages and content at printed 79–81 and 91 confirmed. Printed 85 also reports that Mahadevan sign 1 is among the signs most frequent at West Asian sites, a direct precedent the REPORT does not cite. |
| Suga 2024, *Journal of General Linguistics* 26–27 | stored PDF text | 1,137 seals and the 3A/3B/3C classes confirmed. The title page has no colon between "Script" and "Based"; `sources.json` and the REPORT print one. |
| Rao et al. 2009, PNAS | stored PDF, rendered Table 2 | Eight West Asian rows plus the Indus held-out median row confirmed. |
| Oakes 2019 (online 2017), *Journal of Quantitative Linguistics* 26:22–47 | stored PDF text | Title, author name and abstract confirmed. |
| Parpola 2018, chapter 8 of Ameri et al. | stored author proof | Venue and pages confirmed. Section I.C names Kish, Umma, Failaka, Bahrain, Altyn Depe, Gonur and Shortughai but not Ur. |
| Frenez review page on Harappa.com | stored HTML | Image captions naming Umma, Ur, Oman, Susa and Salut ST1 confirmed; Ra's al-Junayz is not named. |
| Vidale 2005, *South Asian Archaeology 2003* | stored PDF, rendered Figures 4–5 | Title, editors and printed 154–156 confirmed. The Figure 5 label draws a stick figure with stroke pairs beside the head, so the group is "man" and variants, not the plain glyph alone. |
| Vidale 2004, Melammu Symposia 4 | stored PDF text | The "man" sign with variants and the patronymic idea appear at printed 270, with the Parpola 1986:411 citation. The word "twins" does not occur, although the REPORT says the paper discusses "those signs". |
| Laursen 2010, *Arabian Archaeology and Epigraphy* 21(2):96–134 | Crossref abstract (publisher page returns 403) | Title and venue confirmed; the abstract names "the abnormal occurrence of prefixed 'twins' signs in the western inscriptions". |
| Jamison, Uesugi and Yamaguchi 2023 | university record (WebFetch) | Authors, volume 36, article 100486, December 2023 confirmed. |
| Parpola 2005, *South Asian Archaeology 2001* I:267–274 | institutional record | Title, editors, pages confirmed. |
| Koskenniemi and Parpola 1979 | official portal | Title, series, CC BY 4.0 confirmed. |
| Fuls 2022, *Corpus of Indus Inscriptions* | search snippets only | Title, series number and year agree with snippets. The excerpt the package says it read returns 403 for me and has no stored copy, so the section 1.3–1.4 claims are unverifiable. |

Not re-verified: the Parpola 2010 bibliography page used for the 1994 catalogue entry (403), and the Kenoyer and Meadow 2008 chapter, whose bibliography line I confirmed in Kenoyer 2020.

## Method and scope findings

**1. Timing.** `PROTOCOL.md`, `PRECOMPUTATION_CLARIFICATION.md` and `acquire_sources.py` are byte-identical to the versions in commit 3183b4d at 00:02:54. `analyze.py` was last written at 00:04:22 and the first aggregate at 00:04:52. The amendment of 00:13 and the supplement code of 00:14 follow the main run and are labelled exploratory. The post-launch protocol (00:40:58) precedes its code (00:47:57) and outputs (00:49–00:50), but only by file times. Its statement that the sign candidates were fixed independently of measured frequencies cannot be checked, because the original run had already written per-region sign counts including 090 and 091. The registry remedy "Freeze primary graphic candidates and alternatives before counts" should say before the matched-frequency computation.

**2. Period mapping.** Every one of the 1,939 dated Harappa faces maps to at least one period by label prefix; none is unrecognized. "3B/C" gives {3B, 3C} and "Period 3" gives {3A, 3B, 3C}. Within every Harappa family all faces have the same admissible period set, so the union rule of the post-launch run and the intersection rule of the original run give identical families (115 in 3B, 444 in 3C, 696 interval-labelled). The interval handling follows the protocol: unambiguous labels for the primary tests, 3B/C assigned all to 3B and all to 3C, 100 uniform draws, bounds on first and last observed period. The Table 1 dates support the mapping. The cited source does not define the subphase labels 3B-1, 3B-2 and 3C-1 to 3C-4; they are mapped by prefix. In the export they occur only with a stratum number in the `phase` field (`review/harappa_label_origin.csv`). Mohenjo-daro, Kalibangan, Dholavira and Banawali carry the same label vocabulary beside their own period and phase values (for example Mohenjo-daro "Late", phase III, labelled "Period 3C-3"). Restricting the mapping to `site == "Harappa"` is right; the REPORT's description of the subphases as ordered catalogue categories has no cited basis.

**3. Grouping, references and permutation budget.** Both references are defined in `PROTOCOL.md` and REPORT lines 27 and 51: the family reference permutes whole physical components, the text-closure reference whole components closed over identical complete texts (3,477 components, the largest with 1,038 faces), both within exact type and face-count blocks, with margins asserted in every draw (7,485 draws in the main run, 13,993 in the post-launch run). The README uses both names without defining them. The two results are reported side by side, with the text-closure population stated as smaller (it drops 262 mixed-label and 9 mixed-type faces for 3B–3C), so the reporting is fair. The REPORT opens with "differ", which fits the family reference (Holm .044) and not the text-closure reference (.068).

With 499 draws a p-value near .02 carries a Monte Carlo standard error near .006. I reran the package's `permutation()` unchanged with 19,999 draws for the time family and 9,999 for the regional family, two seeds each (`review/permutation_stability_seed11.json`, `…seed12.json`). The 3B–3C family result holds (Holm .038–.040) and so do the four regional passes. The Period 2–3C comparison moves from Holm .044 to .060. The floor p-value of .002 also limits the sign tests: with 314 regional tests, at least 13 tests must sit at the floor for any to reach q < .05, and only 5 did. At 19,999 draws one time-family sign passes (`review/sign_test_resolution_seed21.json`), and at 9,999 draws no regional sign does (smallest q .0785).

**4. Excavation differences between periods.** The media comparison rarefies to equal numbers of families and nothing else. The export has no excavated volume or area, and the REPORT says only that "excavation coverage and preservation can also change recorded diversity". The unambiguous period samples come from different places and labelling sources. In the table, mound is read from the first letters of the export's `area-section` field, and "period-labelled" means that the `phase` field does not hold a stratum number:

| Unambiguous faces | 3B | 3C |
|---|---|---|
| Period-labelled (phase field is not a stratum number) | 192 | 169 |
| Stratum-labelled (H-numbers 1–1517) | 9 | 405 |
| Mound E / Mound F / Mound AB / other | 180 / 13 / 2 / 6 | 74 / 413 / 61 / 26 |

The stratum-labelled faces carry H-numbers inside or below the "Old excavations" range of the 2010 contents page. Reviewer checks on these subsets (`review/sensitivity_label_origin_area.json`; package functions; 999 bootstrap draws for the intervals and 499 permutation draws for the p-values):

| Subset | Families 3B / 3C | Rarefied richness difference | Shannon difference, bits | Equal-type JS, bits (family-reference p) |
|---|---|---|---|---|
| All unambiguous (package) | 115 / 444 | +4.60 [3.19, 6.14] | +0.90 [0.68, 1.14] | 0.190 (.022) |
| Period-labelled only | 108 / 123 | +3.74 [1.88, 4.88] | +0.99 [0.68, 1.24] | 0.219 (.02) |
| Mound E only | 100 / 44 | +4.36 [1.12, 5.02] | +0.78 [0.20, 1.15] | 0.244 (.056) |

The subset divergences use the common types that remain (TAB:B and TAB:I). The direction of both results survives. The length result does not: the 3C-minus-3B mean length is 0.72 slots for the package's three types, 0.50 for TAB:B and TAB:I alone, 0.16 for period-labelled TAB:B and TAB:I, and 0.12 for Mound E. Period-labelled 3C TAB:B tablets average 3.03 slots against 2.88 in 3B, whereas stratum-labelled 3C TAB:B tablets average 3.92.

**5. Effect sizes and intervals.** `permutation_tests.json` stores the permutation-null mean for every test, and the REPORT does not print it. The 3B–3C divergence is 0.190 bits against a null mean of 0.158, an excess of 0.032; the regional family-reference excesses are +0.018 to +0.119 bits. The adjusted estimand gives the 3B seal cell (10 families, 31 tokens) one third of the 3B distribution. The frozen percentile interval for the 3B–3C value, [0.205, 0.279], and the amendment's basic interval, [0.110, 0.178], both exclude the observed 0.190. The REPORT states both facts and the missing calibration; the consequence is that the headline magnitude has no usable interval.

**6. Early inventory.** The type-only inventory result has an interval [−8.37, 1.91] whose estimate (−7.38) lies near the lower end, while the permutation p is .0215; the REPORT attributes this to "different uncertainty/reference constructions" without explaining the asymmetry, whose likely cause is the sparse-inventory bootstrap bias that the post-launch protocol lists as a limitation. The adjusted result rests on 27 early and 12 later pottery-graffiti families, and the 12 later families contain 10 signs in all, so it says little about the restricted early repertoire the lecture describes.

**7. Man and twins identification.** The basis is the Mayig schema (P013 lists W090, M001, V133/V535; P016 lists W091, M002, V110/V692), the crosswalk derived from it, and chart rows 26 and 31. I confirmed the schema and crosswalk entries and viewed the atlas cells: rank 13 is a simple stick figure, rank 16 two joined figures. The Wells numbers rest on one annotator's compatibility arrays (the crosswalk file calls them "many-to-many candidate compatibility"). A reviewer check joins the 179 Mayig faces to the export by CISI number and compares codes at equal positions on 147 equal-length faces (`review/lipi_mayig_alignment.json`): at 11 positions involving 090, 093, P013 or P014, 9 agree, and no position carries 091 or 097, so 091 has no independent check. Of the other Wells human-figure codes, only 093 (2 external tokens), 095 (2), 071, 117, 121, 125, 127, 151 and 160 (1 each) occur outside the valley (`review/external_codes_and_sites.json`). The declared sets cover 093 and 097; 095 (a person with a short stick) is a different graphic outside them, and none of these codes occurs on the seven matched objects, so none could change the matched result.

**8. Circular-seal exclusion and the external set.** The exclusion is explained clearly and with counts (claim 17). The export has 18 external circular seals, and the exact type-and-length cells of those that reach matching hold 0 or 1 core family, so no comparator exists for the class that carries all 12 target tokens. Seven of the 11 "Iranian Plateau" faces come from Nindowari-damb, Sibri, Miri Qalat, Ornach area and Murda Sang, which the package's mapping note calls Baluchistan or Makran contexts, and the one matched Iranian Plateau object is from Nindowari-damb. The matched objects include square seals from Gonur and Shortughai, which Parpola 2018 describes as classical Indus seals. The seven-object endpoint therefore tests mostly standard-type finds and cannot speak to the non-canonical class; the REPORT excludes circular seals and warns about Baluchistan but does not draw this conclusion.

**9. Scope and rights.** No claim of decipherment, sound or meaning appears. "Patronymic" is attributed to Vidale and stated as untested. Novelty is disclaimed ("publication priority is not established"). The package directory holds no PDF, HTML or image of a source, and the data directory is ignored by Git. One residual disclosure: 96 site/type cells and 25 region/type cells contain a single face, and the sign-count, position and length tables list that face's sign multiset, first sign, last sign and length. For the 16 site/type single-face cells with a clear text of three slots or fewer this reconstructs the whole sequence. The scan also reports two coincidental record-id strings (`2017.1` and `2023.1`, parts of DOIs).

**10. Boundaries.** At the end of the review `git status --porcelain` listed 36 paths: my untracked `REVIEW.md` and `review/`, and 34 inside other `experiments/2026-10-06-*` directories (weight-metrology 29; backward-chronology, evidence-census, modern-restoration, research-program and sign-context-and-seals 1 each), which belong to other contributors and kept changing while I worked. No D1 file and no shared repository file changed. `FILES_CREATED.json` and `FILES_POST_LAUNCH_2026-10-07.json` together list the 145 files that exist, with none missing and none extra.

**11. Writing.** The scan flags nothing, and stock vocabulary is absent. The README opens with the follow-up results before the first-pass results and bolds 23 numbers in its first four paragraphs (240 words). The REPORT uses "calibration" six times and "remain(s) unverified", "outstanding" or "unresolved" five times, and uses corrective comparisons such as "describe rarefaction, not population confidence" (line 82) and "not an estimated distribution of archaeological dates" (line 59). Some passages are unclear: "cannot be compared as a correction of the original magnitude" (line 51), "preserve expanded face margins" (line 156) and "these evaluate different uncertainty/reference constructions" (line 245).

## Required fixes, in rank order

1. State the composition of the 3B and 3C samples by label source and mound in REPORT section 1 and the media section, with the counts above, and report the period-labelled and Mound E results next to the full-sample ones. Qualify the adjusted length increase of 0.72 slots, which falls to 0.16 in period-labelled tablets, and replace the generic excavation caution with the specific one.
2. Rerun the permutation tests with at least 9,999 draws (19,999 for the two-test time family) in a new dated endpoint. Then correct the Period 2–3C Holm value, the statement that no time sign passes BH, and the registry text, or label the old values as 499-draw estimates with their Monte Carlo error.
3. Print the permutation-null mean and the excess over it beside every Jensen–Shannon effect, and say in the same place that no interval for the headline magnitudes contains the estimate.
4. Correct the attributions: the Ur row of `external_literature_check.csv`, the "twins" statement for Vidale 2004, the Suga title, and the Fuls access status (search snippets only, excerpt not reproducible). Reword "before counts" in the registry remedy and mark the post-launch protocol as ordered by file times only.
5. Define "family reference" and "text closure" in the README at first use, and put the first-pass results before the follow-up.

## Optional improvements

1. Give each script an output-root option so that the README commands can run without writing into the owned directory.
2. Cite Yadav 2013 (printed 85) and the Laursen 2010 abstract beside Vidale as precedents for the man and twins observation, and say that Vidale 2004 treats the "man" sign and variants only.
3. State that 7 of 11 Iranian Plateau faces come from sites the package's mapping note calls Baluchistan or Makran contexts, that the matched Iranian Plateau object is from Nindowari-damb, and that the matched seals are mostly standard Indus types; state the pooled-model excess (−0.086) in the README beside the exact-type one.
4. Merge or suppress single-face cells in the tracked stratified tables, or record that the disclosure is accepted.
5. Cut the repeated caveats and corrective comparisons to one statement of scope in the methods section, explain the type-only interval against its p-value, and rewrite the three unclear passages.
6. Record the registry status as Frozen evaluation for the primary endpoint and Exploratory for the post-launch assays rather than Verified computation for the whole entry.
7. Identify the lecture's man and twins glyphs from the slides and add a second independent check of 091.

## Files in `review/`

- `run_review_step.py`: runner for the package scripts (commands in its header); `compare_outputs.py`: file-by-file comparison of a rerun with the saved endpoint; `rerun/`: the rerun aggregates and verification records; `logs/`: run logs and comparison results.
- `check_numbers.py` and `number_checks.tsv`: the 380 quoted numbers with the field each was read from; `independent_js_check.py`: the plain-Python divergence recomputation.
- `sensitivity_label_origin_area.py` and `.json`, `harappa_label_origin.csv`, `explore_labels.py`: label source, mound and subset checks (finding 4).
- `permutation_stability.py`, `permutation_stability_seed11.json`, `permutation_stability_seed12.json`, `sign_test_resolution.py`, `sign_test_resolution_seed21.json`: larger-budget permutation checks (finding 3).
- `lipi_mayig_alignment.py`, `external_codes_and_sites.py` and their JSON outputs: identification and external-set checks (findings 7 and 8); `scan_tracked_outputs.py` and `tracked_output_scan.json`: scan of tracked files (finding 9).
