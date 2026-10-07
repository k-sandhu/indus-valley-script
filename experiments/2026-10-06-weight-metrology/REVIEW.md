# Review of package G: the Indus weight system across sites and regions

Package: `experiments/2026-10-06-weight-metrology/`, produced by GPT-6.1-Sol. Reviewer: Claude Sonnet 5.5, 7 October 2026. Reviewer code and aggregate outputs are in `review/`. Page images and rerun outputs are in the local raw directory and are not tracked. Reviewer fits reuse the package's own `fit` function and selection IDs, and the analyses added by the reviewer (sections 1.1 and 1.3) are post-outcome and exploratory.

## Verdict

The computed results stand and two interpretations do not. All 201 headline numbers in `README.md` and `REPORT.md` match the saved outputs, every command in the README reproduces its outputs (byte for byte for the 18 numerical files), an independently written likelihood and a regenerated Monte Carlo envelope agree with the Dholavira results, and the protocol body was committed at 00:02:54 on 7 October, before the first fit began at 00:09:43. The most important problem is the headline Dholavira unit: 14.003 g is the best single scale for a sample that contains two populations, and it describes neither. Weights of 5 to 100 g give 13.72 g (CV 1.6%), the 1.3 to 5 g weights give 14.27 g (CV 5.8%), and Ascalone 2022 already reports the heavier group (mean 14.44 g). The report never relates its unit to the 13.7 g of Hemmy and Kenoyer. The second problem is the western-compatibility result: the observed 136 geometric and 18 close preferences are lower than the counts the same rule gives to masses with their fine structure removed (about 170 and 39), so they are not evidence of Indus-standard weights in the west.

Other findings, in order of weight: the competing "local" units sit on the edges of their fitting ranges (9.1 and 8.0 g), and seven of the 18 close-fit objects disappear with canonical units, including cat. 220, which is 30 times 9.40 g to within 0.05% and which the book places in its 470 g mina group; two catalogue masses printed with a decimal comma were parsed a hundred times too large (cats. 1201 and 1730); the precedent table omits closer precedents from the same book; and `sources.json` has five bibliographic slips.

## 1. The five specified checks

### 1.1 Why the fitted unit is 14.0 g

**The model.** `analyze.py` fits, in log mass, an equal-weight mixture of 16 normal components at u times {1/32, 1/16, 1/8, 1/4, 1/2, 1, 2, 4, 10, 12.5, 20, 40, 100, 200, 400, 1000}, one shared dispersion sigma, and a log-uniform background (0.01 to 100,000 g). The unit u runs over 12.5 to 15.0 g and is the multiple "1", the same weight class as Hemmy's 16th ratio (13.70 to 13.71 g in Hemmy 1931, Tables I and III) and Kenoyer's "approximately 13.7 grams". The definitions therefore agree. Damage does not explain the gap: the primary frame excludes every weight with a damage or wear term, and the wear-inclusive and all-complete frames give 13.96 and 13.94 g. The estimator treats every object alike, so the 199 of 298 weights below 5 g (67%) dominate the fit.

**Fixed unit.** With u fixed at 13.65 g (package optimiser, sigma and p free) the log-likelihood falls from -662.29 to -679.51, a drop of 17.2 (AIC +32.4 after counting two free parameters). The 95% likelihood-ratio interval for u is 13.88 to 14.14 g, so inside the model 13.65 g is rejected. Of the 17.2 units, 15.7 come from the 146 objects between 1.3 and 5 g, and the objects from 5 g upward contribute 1.3 (`review/unit-decomposition.json`, `review/unit-check.json`).

**Where the pooled value comes from.** The unit falls as the mass band rises:

| Mass band, intact certain Dholavira | n | Unit g (bootstrap 95%) | Signal CV |
|---|---:|---|---:|
| above 100 g | 9 | 13.45 | 0.8% |
| 5 to 100 g | 90 | 13.72 (13.63 to 13.86) | 1.6% |
| 1.3 to 5 g | 146 | 14.27 (13.96 to 14.55) | 5.8% |
| all | 298 | 14.00 (13.82 to 14.52) | 4.3% |

The smallest well-preserved cuboid chert weights (96 objects) show the same step. Their cluster medians, multiplied by the level, are 14.7 g for 9 weights near 0.9 g (median 0.92 g), 14.24 g for 17 near 1.75 g (median 1.78 g), 14.02 g for 28 near 3.5 g (median 3.505 g, interquartile range 3.44 to 3.62 g), then 13.65 g for 18 near 6.8 g, 13.66 g for 10 near 13.7 g, 13.63 g for 4 near 27.3 g and 13.68 g for 2 near 54.7 g. The sample is also composed differently from Hemmy's: 204 of 298 Dholavira weights (68%) are under 6 g, against 21 of 147 (14%) in Hemmy 1931, Table III. Ascalone 2022 (pp. 123 to 124) says the early studies kept only weights above 6 g that connected to 13.65 g. Hemmy 1935 (witness `open-10.json`) already observed equal-sharpness peaks on a log scale with the smaller groups less sharp, which the single sigma ignores.

**Series and dispersion.** The estimate moves by about 0.15 g at most under reasonable changes, and none reaches 13.65 g: 13.95 g without the 1/32 and 1/16 levels, 14.10 g with Hemmy's 8/3 group (1/6) and the 1/12 and 1/24 levels Ascalone reports (log-likelihood +62, signal probability 0.56 to 0.92; three random extra levels add 17 on average), 14.11 g using levels 1/4 to 4 only, and 13.85 to 14.03 g with sigma fixed at 0.02 to 0.05. The package's likelihood is also blind to a hundredfold error at five pairs of levels (1/8 and 12.5, 1 and 100, 2 and 200, 4 and 400, 10 and 1000): moving cat. 1730 from 184.0 to 1.84 g changes u by 8e-9 g (`review/series-sensitivity.json`).

**Two units.** A mixture of two copies of the series, fitted without Ascalone's lists, improves AIC by 101 with free dispersions (13.82 g at CV 2.0% plus a diffuse 14.74 g component), by 34 with both sigmas capped at 0.05 (13.78 g at CV 2.0%, 63% of the signal weight, plus a component at the 15.0 g bound), and by 24 with caps of 0.03 (`review/two-unit-mixture.json`). The book's list of 95 weights with a heavier unit (pp. 169 to 171, mean 14.44 g) overlaps the sample by 82 objects; without them the other 216 give 13.68 g (CV 1.3%), and the 82 alone give 14.45 g (CV 2.5%). That list was selected by deviation from 13.65 g, so the 13.68 g figure is conditional on it (`review/ghaggar-group-check.json`).

**Assessment.** The unit is not a definitional difference and not a numerical artefact. It is the maximum-likelihood scale for pooled weights whose heavier part sits near 13.7 g and whose 1/8 and 1/4 levels sit near 14.0 to 14.5 g. It is defensible as a description of the pooled intact sample and indefensible as an estimate of the Harappan unit or of a single Dholavira unit. The package's own quantogram shows the split: the highest peak is 1.71 g (8 times 1.71 is 13.68 g, Q 8.004) and the second is 14.67 g (Q 7.575). `REPORT.md` attributes the difference from the mixture to "harmonics, mass cap and density assumptions", which does not describe it. The Gulf weights fit 13.65 g better than 14.003 g (median error 1.1% against 2.8%), and the Rakhigarhi estimate of 14.31 g recomputes the book's own 14.43 g (range 14.02 to 14.56) from the same cubes (the package's nine objects are those eight cubes plus cat. 1122).

### 1.2 Re-audit of extracted rows

I drew a seeded random sample of 36 IDs (seed 20261011) from the 1,998 IDs the package did not audit, covering 18 Susiana and Mesopotamian, 4 Iranian and 14 Greater Indus entries, and added six IDs that scans had flagged (82, 1201, 1212, 1400, 1503, 1730), which are kept out of the rates. Each entry was rendered from the PDF with PyMuPDF at 3.2 times and compared by eye with the `extraction-v6` row. Verdicts per row are in `review/row-audit.csv`.

| Field | Errors in 36 | Wilson 95% | Detail |
|---|---:|---|---|
| mass (including +x) | 0 | 0 to 9.6% | |
| site | 0 | 0 to 9.6% | |
| material | 1 | 0.5 to 14.2% | cat. 719 prints copper/bronze; parsed as bronze, with "copper/" left in the condition field |
| shape | 0 | 0 to 9.6% | |
| class | 0 | 0 to 9.6% | Dholavira ranges checked against p. 135 (435, 11, 36 and 388 follow the printed ranges; the text's 393 is the book's own inconsistency), Rakhigarhi against p. 122 |
| context | 2 | 1.5 to 18.1% | cats. 1020 and 1053: a date in the Tepe Yahya field number was read as a grid reference. The context string, area and level were right in all 36 |
| period | 0 | 0 to 9.6% | 11 of the 36 entries print a period; the repair of the five period errors holds in version 6 |

Scans of the whole catalogue found problems that a sample of this size cannot. Two entries print a decimal comma: cat. 1201 ("4,44+x g", outside every fit because of +x) and cat. 1730 ("1,84 g"), which the parser read as 444.0 and 184.0 g. Cat. 1730 is one of the 298 fitted objects; the book's own list gives 1.84 g. The mass-error rate from this cause is 2 in 2,058, so the package's "0 observed mass/+x errors" is true of its 60 entries only. The grid field is filled for 111 of 1,188 non-Dholavira rows (90 at Tepe Yahya), every one a date (90) or an accession or excavation number (21). Six rows keep "copper/" in the condition field. Figure captions leak into the period field of four entries (1069, 1121, 1148, 1173), the context field of one (1083) and the dimension field of one (1137), without changing a mass or a date range. A density screen of 413 box-shaped entries flags 13 whose printed mass and dimensions imply a density below 1 or above 5 g/cm3 (median 2.3). Most are printed-source inconsistencies, for example cat. 1503 (810.00 g for a block of about 3 cm3) and cat. 1212 (70.00 g for about 3.6 cm3); two of the 13 (1730 and 1763) are among the 298. One numeric unit attribution, "(= 180)" in cat. 593, is not captured in `entry_unit_attribution`.

### 1.3 Western compatibility

**Alternatives.** The package compares the Indus list at Dholavira's 14.003 g with three Near Eastern lists of 27 levels each. The unit of each Near Eastern list is refitted inside 7.4 to 8.0, 8.1 to 8.7 and 9.1 to 9.7 g at every site with at least eight records. The Gulf 13.5 g, the 11.75 g shekel of the 470 g mina, the 8.9 g heavy shekel and the sexagesimal fractions (1/6, 1/3, 2/3, 5/6) are absent, although the book's Dholavira Mesopotamian group uses those fractions (p. 172). The refitted units are mostly boundary solutions: 9.1 g for the 9.4 g family at Susa, Girsu, Tepe Yahya and Shahr-i Sokhta (at Susa with sigma 20%), 8.0 g for the 7.8 g family at Susa and Girsu, and 7.4 g at Tepe Yahya.

**Bias toward denser lists.** A nearest-multiple residual is smaller on average for a denser list, and the rule asks the Indus residual to beat the smallest of three competing lists. I applied the package's rules (reproduced object by object) to masses with the fine structure removed. The observed counts are lower than these chance counts, so the statistic cannot show Indus compatibility:

| Reference | Geometric preference (observed 136) | Close preference (observed 18) |
|---|---:|---:|
| observed masses with each mass jittered by up to 15% | 170 (95% interval 153 to 187) | 39 (28 to 51) |
| jittered by up to 35% | 209 (186 to 232) | 50 (38 to 64) |
| log-uniform inside each site's range | 194 (172 to 216) | 44 (32 to 57) |
| observed masses, 251 Indus units from 12.5 to 15.0 g | 107 to 194 (64% of units give 136 or more) | 15 to 47, mean 26 (70% of units give 18 or more; 13.65 g gives 22) |

The jitter destroys real local structure, which is why the observed counts fall below it. The point is that 18 is a count the procedure returns for most arbitrary reference units (`review/western-null.json`).

**Competitor definition.** With canonical local units (7.8, 8.4, 9.4 g) the counts become 111 and 11, and 174, 220, 476, 590, 845, 953 and 1100 drop out. Adding the 7.83, 8.36 and 11.75 g units leaves 55 and 10. Adding the sexagesimal fractions and 1/5 leaves 29 and 5 (cats. 35, 281, 282, 761 and 777). At 13.65 g with the extended competitors the close count is 27 (`review/western-checks.json`).

**The 18 objects.** All 18 are ovoid, duck, discoid or flat-pebble forms, and none is a cuboid, the Harappan diagnostic shape. Five are hematite ovoids with flat ends of 1.70 to 1.75 g (cats. 280, 281, 282, 825, 875), the dominant Susa hematite type; the Near Eastern lists lack 1/5 of a shekel (1.68 g at 8.4 g), and adding it with the other sexagesimal fractions removes three of the five. Cat. 476 is dated Middle Elamite I (1500 to 1400 BC) and cat. 993 Proto-Elamite (3000 to 2700 BC). Cats. 220 and 257 carry stroke marks that a mass-only rule ignores. Cat. 82 prints dimensions that cannot belong to a 6.85 g stone (a printed-source anomaly). Ascalone 2022 (pp. 69 to 70) names 12 Susa weights as made locally to the Harappan standard and gives Indus-system values for 17 (cats. 34, 35, 81, 82, 224, 233, 324, 487, 499, 504, 601, 628, 680, 694, 698, 699, 700), and it places six in a "Western group" (20, 70, 80, 220, 530, 669). Only two of the 17 (35 and 82) are among the 18, four of the 17 lie within 3% of 14.003 g and seven within 3% of 13.65 g, and cat. 220, a Western group member, is among the 18. The book also names cats. 698 to 700 on p. 39, where `REPORT.md` cites 694 and 698.

**Assessment.** The western results are arithmetic that reproduces and a screen that selects objects without the typology, dating, marks or the book's own attributions. They give no evidence that Indus-standard weights occur in the west. The report's wording ("locate mass-compatible records", "model-defined measurement check of candidates") is cautious, but its headline percentages and Wilson intervals invite the opposite reading.

### 1.4 Precedents

| Work | What it already established | Package treatment |
|---|---|---|
| Hemmy 1931 (Marshall, vol. II, pp. 589 to 598) | Unit 0.856 to 0.857 g, 16th ratio 13.70 to 13.71 g, binary then decimal ratios, 147 of 159 condition-selected weights fit the table, equal percentage error assumed for all weights | Cited correctly. Table III counts are misattributed in `sources.json` |
| Hemmy 1935 | Log-scale peaks of equal sharpness, proportional error, smaller groups less sharp, sums of probability curves | Cited. The single sigma ignores its remark on small weights |
| Hemmy 1937 | Egyptian Petrie weights (JEA 23); no Indus paper of that year found | Correctly identified. Hemmy 1938b (relation to Egyptian and Susian weights) and 1943 (Chanhu-daro) are in the same bibliography and absent |
| Kenoyer 2010 | 16th ratio about 13.7 g, first ratio 0.871 g, decimal levels, Mainkar's pooling questioned, regional variation, request for remeasurement and condition study | Accurate. The 0.871 g (13.94 g at 16 times) is not discussed |
| Vahia and Yadav 2007 | About 6% class error, base 0.89 g (14.2 g at 16 times) per the package's own witness | The 6% is cited; the 0.89 g base is not |
| Rahmstorf 2020 | CQA peak at 13.68 g, with 1/2, 1/3, 1/4, 1/5, 1/6, 1/8 and 1/16 also high | Cited. The 1/3, 1/5 and 1/6 levels are missing from the declared Indus list |
| Ialongo, Vacca and Peyronel 2018; Ialongo and Lago 2021; Lago, Cardarelli and Ialongo 2024 | FDA and CQA as the standard methods; systems can share clusters; units can differ by order of magnitude, handled by subsampling by mass range; error about 5% | Cited correctly. Subsampling by mass range is not applied |
| Ascalone 2022 (this book) | CQA of Dholavira weights giving c. 13.60 g (pp. 166 to 168); mass clusters per range with unit ranges; a 95-weight heavier group at 14.0 to 15.24 g, mean 14.44 g, matching Rakhigarhi and Farmana at 14.43 g (14.02 to 14.56); Western and Mesopotamian groups at Dholavira; 17 Harappan-standard and six Western-group weights at Susa; Bagasra c. 13.70 g | Described only as "local standards, material differences and Dholavira concentrations". The Rakhigarhi and Dholavira heavier-unit results and the Susa lists are not named |
| Ascalone 2018c, 2021a; Hendrickx-Baudot 1972 | By title and the book's citations (not opened): Rakhigarhi and Ghaggar weights; Indus- and Oman-related weights and ingots at Kish, Telloh and Susa; the 13.60 g unit | Absent |

The package adds a parser for all 2,058 entries with a page audit, explicit intact-weight selection rules, a background-mixture likelihood with bootstrap intervals for each site, and area and period strata at Dholavira (the book prints context counts but no unit estimates by area). The unit levels, the heavier Ghaggar-type group, the Rakhigarhi 14.3 g unit and the Susa Harappan-standard weights are results of Ascalone 2018c, 2021a and 2022. The Gulf supplement is an arithmetic check of Bibby's own ratios (1.714 g times 8 is 13.71 g), and its list was built from the same seven weights.

### 1.5 Catalogue content in the tracked directory

Confirmed: none. Pattern searches for entry text (identifiers, museum numbers, condition and shape strings, dimension strings) over every tracked file outside `review/` returned no match. The tracked JSON files hold counts, IDs, fitted values and short audit notes, `sources.json` holds bibliographic records with no quotations, and `FILES.json` lists local files by path and hash only. My own `review/` files hold IDs, verdicts and fitted aggregates. Hashes in `FILES.json` match all 79 owned and 277 local files, and no owned file is missing from it.

## 2. Checked claims

All 201 numbers were compared by `review/check_numbers.py` (`review/numbers-check.json`), with tolerance of half a unit in the last printed digit.

| Claim | Evidence | Result | Note |
|---|---|---|---|
| 2,058 entries; 938 Greater Indus; site counts 870, 19, 16, 15, 8, 7, 2, 1 | `extraction-v6.json`, `runs/2026-10-06-main/counts.json` | confirmed | the rerun parse is identical to the local rows |
| 60-entry audit: 5 period errors (8.33%, Wilson 3.61 to 18.07%), 0 mass/+x errors, 0 remaining | `parser-validation-v2.json` | confirmed | mass errors exist outside the sample (1.2) |
| Dholavira certain: n 298, unit 14.003 (13.819 to 14.518), CV 4.32% (2.41 to 15.85%), p 0.562, 110 within 3% | `model-comparisons.json` | confirmed | interpretation: discrepancy (1.1) |
| Dholavira all classes: n 568, CV 17.24% | `stratified-estimates.json` | confirmed | |
| Rakhigarhi, Nagwada, Bagasra rows; AIC differences 15.262, tie, 0.000007, 1.914 | `model-comparisons.json` | confirmed | Rakhigarhi repeats the book's analysis |
| Material, shape, area, period and wear strata (36 fits) | `stratified-estimates.json` | confirmed | pooled-unit caveat applies |
| Ten quantograms, maxima, envelopes and p values | `quantogram-peaks.json` | confirmed | envelope regenerated with new seeds |
| Western: 701 records, 136 (19.40%), 18 (2.57%), Wilson intervals, 2%, 5%, 13.65 g and exclusion sensitivities | `western-compatibility.json` | confirmed | interpretation: discrepancy (1.3) |
| 18 driving objects by site (10, 4, 1, 2, 1) | `western-driving-objects.json` | confirmed | cat. 220 misclassified in effect |
| Gulf: 6/7 at 13.5 or 13.65 g with the Gulf list, 5/7 with the main list, 1/7 per local list | `gulf-supplement.json` | confirmed | circular by construction |
| Verification: 45 likelihoods, 169 cosine points, 701 classifications, 1,800 draws | `verification.json` | confirmed | reproduced by `verify.py` |
| Reproduction: 18 numerical files and 9 derivatives byte-identical | `reproduction.json` | confirmed | same environment, so this shows determinism |
| Dholavira classes 435, 11, 36, 388; context counts 473, 646, 739, 393 | `counts.json`, `summary-tables/context-coverage.json` | confirmed | the book's 393 potential weights is its own inconsistency |
| Protocol preceded the fits | commit 3183b4d (00:02:54); manifest (00:09:43) | confirmed | see section 5 |
| No catalogue rows in the tracked directory | pattern search, `FILES.json` | confirmed | |
| Hemmy 1931 Table III "147 Mohenjo-daro of 159, 34 Harappa of 39" | `sources.json` | discrepancy | 147 of 159 is both sites combined; Mohenjo-daro 113 of 120 |
| Five entries lack a printed mass (602, 1293, 1496, 1497, 1914) | `parser-validation-v2.json` | confirmed | entry text has no mass |
| Retrospective: 713 tuple/list differences in the first verifier | `RETROSPECTIVE.md` | unverifiable | the first verifier run is not preserved |

## 3. Reproduction log

Environment: Python 3.13.5, NumPy 2.2.6, SciPy 1.17.1, PyMuPDF 1.28.0, the versions the package records. Outputs went to `review/` or the local raw directory.

| Step | Result |
|---|---|
| `parse_catalogue.py --render-sample` | 2,058 rows; the rows file is byte-identical to `extraction-v6`; the eight-site count assertion passed |
| `validation_audit.py` | 5 errors before repair, 0 after; summary equals `parser-validation-v2.json` except the path |
| `analyze.py` (200 bootstrap refits for 9 groups, ten quantograms of 999 surrogates) | 124 s; manifest equal except time and path |
| `verify.py` | passed: reparse equal, 45 likelihoods (maximum difference 4.5e-13), 169 cosine points (2.3e-14), 701 classifications, 1,800 draws, 0 optimiser failures |
| `compare_runs.py` | 18 numerical files and 9 local derivatives identical |
| `make_summaries.py`, `gulf_supplement.py` | five summary tables and the Gulf aggregates identical |
| `tools/review_prose.py --path experiments/2026-10-06-weight-metrology --no-write` | 7 Markdown files (six package files and this review), 0 flags |
| Hash inventory of `FILES.json` | all hashes match |
| `review/check_numbers.py` | 201 of 201 numbers confirmed |
| `review/quantogram_mc_check.py` | threshold 7.687 and 7.697 for two new seeds; p 0.004 and 0.002 |

Nothing failed to match except paths and timestamps. During the review the volume had 0 free bytes for several minutes while other packages were writing large logs and PDFs. I removed my own two rerun directories (11 MB) from the raw directory, reran the one interrupted script, and confirmed that every JSON file in `review/` parses.

## 4. Source checks

| Source | How checked | Result |
|---|---|---|
| Ascalone 2022 | local PDF (SHA-256 equals `sources.json`); title pages, pp. 39, 69 to 70, 121 to 136, 166 to 175, 197 | Details accurate; the title page adds "with a contribution from Jan Tavernier". Hemmy 1937, 1938a, 1938b, 1943 and Hendrickx-Baudot 1972 confirmed on p. 197 |
| Hemmy 1931 | local PDF | Title accurate; pages are 589 to 598, not 588 to 598; Table III counts misattributed (section 2) |
| Hemmy 1937 | Ascalone bibliography; web search | JEA 23, 39 to 56, Egyptian weights; the package is correct. The article itself was not found |
| Kenoyer 2010 | Cambridge chapter page by WebFetch; package witness `open-08.json` | Title, editors, publisher, pp. 106 to 122 confirmed; passages on p. 116 to 117 as described. The harappa.com PDF returned HTTP 403 to me |
| Ialongo, Vacca and Peyronel 2018 | local PDF | Accurate (JAS 91, 20 to 32; 171 silver items) |
| Ialongo and Lago 2021 | local PDF | Accurate (JAS 129, 105379; about 3,000 objects; sections 3.3 to 3.5) |
| Lago, Cardarelli and Ialongo 2024 | local issue PDF | Title, pages and DOI accurate; the second author is Lorenzo, not Luca, Cardarelli |
| Bibby 1970 | local scan, pp. 345 and 350 | Seven masses and the ratios 1:8:16:8:100:400:800 match `gulf-bibby-rows.json`; the printed title is "... efter Dilmun norm" with ellipsis and guillemets |
| Vahia and Yadav 2007 | WebFetch of the Puratattva 37 contents; witness `open-08.json` | Pages 213 to 217 consistent; the 6% error is in the witness, as is a 0.89 g base the package does not report |
| Rahmstorf 2020 | web search; witness excerpt | Bibliographic details and the 13.68 g peak confirmed; the chapter was not opened by either of us |
| Miller 2013, Ascalone and Peyronel 1999, Laursen 2016, Petruso 1992, Højlund and Andersen 1994, Mainkar 1984 | web search, book bibliography, Danino 2014 reference list | Bibliographic details confirmed; contents unverifiable |

Sources seen only as snippets or bibliography entries are marked as such in `sources.json`, and no quotation appears in it. I did not open Hemmy 1938a and 1943, Mainkar, Miller, Højlund, or the Ascalone and Peyronel texts.

## 5. Method, scope, writing and boundaries

**Deliverables.** All required files are present: `README.md` (with rerun commands), `PROTOCOL.md`, `REPORT.md`, `RETROSPECTIVE.md`, `sources.json` (19 records), `registry-entry.json` (all nine registry fields), nine Python scripts, and aggregate outputs under `runs/` and `summary-tables/`. `IMPLEMENTATION-NOTES.md`, `GULF-AMENDMENT.md` and `FILES.json` are extra.

**Protocol timing.** Commit 3183b4d (00:02:54) holds the 45-line protocol, including the declared series, the western rules and the seed. The eight-line pre-fit clarification was last saved at 00:09:29, 14 seconds before the run began, and its final paragraph describes the assertion failure of the first attempt. The producer's run log shows no fit output before that failure. The design choices criticised above (the series, equal weights, site-fitted local units) are in the committed protocol.

**Exploratory labels.** The seed deviation, the extra all-class quantogram and the post-endpoint Gulf comparison are labelled. The package's per-site and per-stratum units are presented as descriptive but carry the pooling problem. The Monte Carlo envelopes were not independently regenerated by the package; my regeneration for Dholavira closes that gap for one sample. `verify.py` imports the series lists from `analyze.py`, so it checks arithmetic and rule implementation and leaves the choice of series untested.

**Dependence.** Bootstrap and surrogate draws treat records as independent. Three DHR numbers occur twice among the 298 (cats. 1781 and 1782, 1860 and 1896, 1867 and 1868; the last pair shares context and a mass of 6.90 g), ten DHR numbers repeat across the 870 Dholavira entries, and ten museum identifiers are shared by two to six of the 701 western records (six for SH 095366), against three collisions the earlier Susa audit removed. These records are 6 of the 298 Dholavira objects and about 26 of the 701 western records, so I expect little effect, but I did not rerun with clustering.

**Bases and limitations.** Counts keep their bases. Limitations sit beside the claims except for the two main ones: the pooling of mass bands in the Dholavira unit, and the chance baseline for the western counts. The protocol's own negative-result rule says a western claim stays unestablished if few close preferences survive or object identity is unresolved. Both conditions hold, and the report does not say so.

**Scope.** No claim of decipherment, sound or meaning, no resemblance presented as fact, and no priority claim beyond the precedent search. The table's "addition" column is accurate but understates how much of the unit and Susa results the book already contains.

**Writing.** The prose scanner flags nothing and I found no stock phrases. Three passages need work: "fitted conventional unit" in the first paragraph of `REPORT.md`, the vague "harmonics, mass cap and density assumptions" sentence, and about six "does not establish" or "cannot identify" caveats in `REPORT.md` that could be stated once in the methods block.

**Boundaries.** `git status --porcelain` shows two entries for this package, my untracked `REVIEW.md` and `review/`; the package's tracked files are unchanged since commit 53d03b0. Every other changed path lies under `experiments/2026-10-06-*` (evidence-census, modern-restoration, sign-context-and-seals, chronology-region, field-recommendations, backward-chronology, byproduct-inventory, resemblance-baseline), the parallel packages and their reviews. No path outside that pattern changed. A stray `grep.exe.stackdump` at the repository root was present when I began and later disappeared; I did not create it.

## 6. Fixes

Required, in rank order:

1. Rewrite the Dholavira unit statement in `README.md` and `REPORT.md`. State that 14.003 g pools weights near 13.7 g and 14.4 g or more, give the band estimates or a two-unit fit beside it, relate it to Hemmy's 13.70 g, Kenoyer's 13.7 g and Ascalone's 14.44 g group, replace "fitted conventional unit", and correct the quantogram sentence.
2. Add a chance baseline to the western section (jittered masses and a reference-unit sweep), replace boundary-fitted local units with canonical units or bound them near 7.83, 8.4 and 9.4 g, add the missing fractions and units, and compare against Ascalone's Susa lists. Remove cat. 220 from the driving objects and state that the counts give no evidence of Indus-standard weights in the west.
3. Correct the decimal-comma parse (cats. 1201 and 1730), add a mass-against-dimension screen, and say in `parser-validation-v2.json` that the 60-entry sample cannot bound the mass error rate.
4. Extend the precedent table with Ascalone 2018c and 2021a, Hemmy 1938b and 1943, Hendrickx-Baudot 1972 and the Vahia and Yadav base unit, and describe the book's own analyses concretely.
5. Fix `sources.json`: Hemmy 1931 counts and pages, Cardarelli's first name, the Bibby title as printed, and the Ascalone 2022 contributor.

Optional:

- Run the common-seed Monte Carlo control that `IMPLEMENTATION-NOTES.md` offers.
- Resample by find context, and merge records that share an excavation or accession number.
- Fit levels by mass band, following Ialongo and Lago's subsampling, and report the Dholavira bands in the strata tables.
- Restrict `grids` to Dholavira and capture "(= 180)" style attributions.
- Present the Gulf supplement as an arithmetic check and move it out of the README's headline paragraph.
- Compare each site estimate with the book's own site notes (Bagasra c. 13.70 g against the package's 14.94 g at the edge of the range; Farmana 14.18 to 14.88 g).
- Have an independent person repeat the visual audit with the same field list.

## 7. Files written by this review

All reviewer scripts and outputs are in `review/`, and each section above names the file that holds its numbers. The header of each script gives its command, to be run from the repository root. `review/row-audit.csv` has the per-row audit verdicts and `review/*-rerun.json` the summaries of the rerun. Temporary files, including page crops and rerun outputs, are under `data/raw/2026-10-06-weight-metrology/review-*` and are not tracked.
