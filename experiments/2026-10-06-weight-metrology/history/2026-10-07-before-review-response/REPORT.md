# Indus weight metrology across the catalogue

The 298 intact, complete-mass objects in Ascalone's certain Dholavira class give a fitted conventional unit of **14.003 g**, with a 200-refit bootstrap interval of **13.819–14.518 g**. The fitted signal has a **4.32% coefficient of variation (CV; bootstrap interval 2.41–15.85%)** and signal probability **0.562**. Only **110/298 (36.91%)** lie within 3% of a declared denomination. These quantities describe a mixture fit to catalogue measurements; the CV applies to its fitted signal component. The broader 568-object Dholavira sample gives **17.24% CV**, so classification substantially changes the result. [Model results](runs/2026-10-06-main/model-comparisons.json), `fits[group=Dholavira, model=indus_binary_decimal]`; [strata](runs/2026-10-06-main/stratified-estimates.json), `fits[group=Dholavira/all-classes/primary]`.

Of 701 eligible western catalogue records, **136 (19.40%; Wilson 95% interval 16.64–22.49%)** have smaller nearest-denomination residuals to the Dholavira reference than to every declared local alternative. Requiring a fit within 3% and at least one percentage point of advantage reduces this to **18 (2.57%; 1.63–4.02%)**. Susa and Girsu assemblages fit the local 8.4 g family better overall. These comparisons locate mass-compatible records in a selected, mixed-period catalogue. Object origin and contemporaneous exchange require archaeological evidence beyond the residuals. [Western comparison](runs/2026-10-06-main/western-compatibility.json), `comparisons[frame=primary]`.

The mass fits are a Frozen evaluation with Verified computation. The observed cosine scores are also numerically verified. Successive site seeds differ from the single Monte Carlo seed named in the protocol; the affected envelope comparisons and the additional all-class diagnostic are labelled Exploratory in [endpoint annotations](endpoint-annotations.json). The separate seven-object Gulf supplement is Exploratory. The package began on 6 October and reached its endpoint on 7 October 2026.

## Catalogue extraction and page validation

The parser extracted **2,058 unique entries**, including every ID from 1 through 2058 and the expected **938 Greater Indus entries**. The Indus totals are Dholavira 870, Bagasra 19, Nagwada 16, Rakhigarhi 15, Farmana 8, Shikarpur 7, Kuntasi 2 and Nageshwar 1. [Extraction coverage](extraction-v6.json), `row_count`, `ids_complete_unique`, `site_counts`; [site/class table](summary-tables/counts-by-site-class.csv).

Each local row retains catalogue number, identifiers, literal excavation/museum context, area, level, grids, period/date, material, shape, labelled dimensions, mass, condition, damage/wear flags, marks, explicit entry unit attribution and both PDF and printed page pointers. It also preserves the full entry text. The rows are in `data/raw/2026-10-06-weight-metrology/extraction-v6/catalogue-rows.json`. The tracked files contain aggregates and driving IDs. Five entries lack a printed mass: 602, 1293, 1496, 1497 and 1914. No value was imputed. Three entries have no ordinary labelled dimension, including a slash-form measurement. Interpretative unit assignments in chapter prose and tables have not been comprehensively joined to individual entries. Literal context and entry text preserve information beyond the structured fields; marks containing long comma-separated inscriptions need further field review.

A uniform random sample of **60 IDs**, seed 20261006, was checked by eye against rendered PDF entries across the full catalogue. Fourteen fields per entry were examined. The first audited extraction had **5 erroneous entries (8.33%; Wilson interval 3.61–18.07%)**, all involving period text: IDs 652, 758, 892, 930 and 1892. There were **0 observed mass or +x errors**. Repairs left **0 errors in the rechecked sample**. The zero-error Wilson upper bound is 6.02%, but rechecking a repaired sample does not estimate error in untouched entries independently. This is the author's source-informed review. [Validation report](parser-validation-v2.json), `entry_errors_before_repair`, `error_fields`, `entry_errors_remaining_in_sample`; detailed notes and images remain local.

Ascalone's explicit Dholavira ID ranges yield **435 certain**, **11 possible**, **36 excluded related finds** and **388 potential** objects. The chapter's prose says 393 potential objects, a five-object discrepancy requiring review. It reports 505 objects with archaeological context. Our parsed nonempty area, level, grid and period counts are respectively **473, 646, 739 and 393**; these fields use different definitions from that contextual total. No reconciliation to the 505-object set was completed. [Ascalone 2022](https://airus.unisalento.it/retrieve/c39309c8-8dae-4dba-b990-86171612edf6/E.%20Ascalone%2C%20Bronze%20Age%20Weights%20from%20Mesopotamia%2C%20Iran%20and%20Greater%20Indus%20Valley_compressed.pdf), printed pp. 135–136 and Table 6.2; [context coverage](summary-tables/context-coverage.json).

## Selection, models and comparisons

The [protocol](PROTOCOL.md) preceded fitting. The primary sample requires a positive complete numeric mass and good, perfect or excellent condition, with no wear, abrasion, chipping, breakage, restoration or other recorded damage. Dholavira uses the source's certain class; Rakhigarhi uses its explicit certain IDs. Other Indus sites retain eligible uncertain classes because comparable complete chapter classifications were unavailable. Their site estimates therefore describe different ascertainment frames. Western primary comparisons admit certain/class-unresolved objects and exclude accession collisions 119, 120 and 129 identified by the earlier Susa audit. Possible/potential western objects form a separate sensitivity.

For each declared multiple, the model places a normal component in log mass at log(unit × multiple), with common multiplicative dispersion. Components have equal fixed probability. A log-uniform background over 0.01–100000 g accommodates observations outside the series. Unit, log dispersion and signal probability are fitted with ten starts. Indus units range from 12.5 to 15 g; local alternatives range around 7.8, 8.4 and 9.4 g. The Indus list extends the central doubling-then-decimal levels with declared terminal levels; it is an operational support, not a complete historical inventory. Near Eastern alternatives use a shared list of integer and fractional multiples. The exact lists, bounds, versions and hashes are in [the manifest](runs/2026-10-06-main/manifest.json), `models`.

All models have three fitted parameters and are compared by AIC on the same mass sample. Fixed support and equal denomination frequencies affect the densities, especially when denomination lists have different sizes. AIC preference consequently depends on these declared supports. Bootstrap intervals use 200 object resamples for the Indus model at eligible Indus sites and the best local model at eligible western sites. Stratum fits have point estimates only. The signal CV is `100 × sqrt(exp(sigma_log²) − 1)`. It combines manufacture, calibration, surviving wear and recording error. Additional historical fractions, such as the 1/24 discussed by Ascalone on p. 167, can account for apparent outliers under this restricted support.

## Sites and Dholavira strata

The following Indus results use the declared Indus mixture. All numbers come from [model comparisons](runs/2026-10-06-main/model-comparisons.json), the indicated site/model fields and `bootstrap`; a flat table is in [unit estimates](summary-tables/unit-estimates.csv).

| Site | Primary n | Unit g (bootstrap 95% interval) | Signal CV | Signal probability | Within 3% |
|---|---:|---|---:|---:|---:|
| Dholavira, certain | 298 | 14.003 (13.819–14.518) | 4.32% | 0.562 | 110 |
| Rakhigarhi, certain | 9 | 14.313 (14.084–14.560) | 1.46% | 0.644 | 6 |
| Nagwada | 14 | 13.605 (12.500–14.699) | 13.95% | 0.990 | 4 |
| Bagasra | 11 | 14.941 (13.696–15.000) | 11.30% | 0.990 | 2 |

Dholavira's Indus model beats pure binary by **15.262 AIC units**. Rakhigarhi has an exact numerical tie between the two supports because its selected levels are shared. Nagwada's difference is only 0.000007 AIC units, and Bagasra weakly prefers pure binary by 1.914. The latter two have broad, boundary-touching bootstrap intervals. These results support concentrated subsets at Dholavira and Rakhigarhi, with limited evidence for site differences or larger-series discrimination. Farmana, Shikarpur, Kuntasi and Nageshwar supply only **2, 2, 1 and 1** eligible masses, below the declared eight-object fitting threshold. [Counts](runs/2026-10-06-main/counts.json), `sites[].primary_n`; model comparisons `aic_minus_best`.

The material and shape estimates below concern Dholavira's certain primary frame. They are descriptive comparisons with overlapping memberships. The source's class, preservation and material labels may each correlate with mass range and archaeological period. [Stratified estimates](runs/2026-10-06-main/stratified-estimates.json), `fits[group=Dholavira/certain/material/*]` and `shape/*`.

| Stratum | n | Unit g | Signal CV | Within 3% |
|---|---:|---:|---:|---:|
| Chert | 100 | 14.031 | 4.26% | 49 |
| Other stones | 156 | 14.363 | 15.13% | 38 |
| Non-stone | 42 | 12.500, lower bound | 20.20%, upper log-dispersion bound | 4 |
| Cuboid | 226 | 14.069 | 4.79% | 79 |
| Biconic | 54 | 13.101 | 17.48% | 7 |
| Hemisphere | 8 | 12.500, lower bound | 20.20%, upper log-dispersion bound | 1 |

Context also changes the fitted dispersion. Bailey, Castle, Lower Town and Middle Town have units of **13.869, 13.990, 13.824 and 14.271 g**, with CVs **0.50%, 3.49%, 1.80% and 6.20%**, from **14, 60, 29 and 122** objects. Bailey reaches the dispersion floor. The 73 objects without a parsed area give 16.04% CV. Explicit periods IV, V and VI give **3.82%, 13.66% and 1.96% CV**, with **82, 80 and 23** objects. Mixed IV–V has nine objects and 2.28% CV; unprovided period has 100 and 16.80% CV. Strata below eight objects are omitted. These differences warrant context recovery and joint material/period analysis before a temporal or production explanation. [Stratified estimates](runs/2026-10-06-main/stratified-estimates.csv), groups `Dholavira/area/*` and `Dholavira/period/*`.

Admitting otherwise complete worn/abraded certain objects raises n to **333**, moves the unit to **13.963 g** and gives **3.52% signal CV**, with signal probability 0.480. Admitting all complete numeric masses despite damage raises n to **363**, with **13.944 g**, **3.46% CV** and signal probability 0.482. The background mixture changes with selection, so decreasing fitted signal CV does not establish an improvement in the accuracy of worn objects. Only five perfect-condition primary certain objects were available; their separate fit was omitted. [Strata](runs/2026-10-06-main/stratified-estimates.json), `Dholavira/certain/wear` and `all-complete`; [condition counts](condition-coverage.json).

## Quantograms and western alternatives

Quantograms use primary complete masses at most 100 g, scanning **0.4–15 g in 0.01 g steps**. Each synthetic control independently perturbs every mass by a log-uniform ±0.15 factor. The envelope compares the observed maximum with 999 surrogate maxima across the entire declared range. It is conditional on this local perturbation null and does not establish a unique base from harmonics. Tests across different site groups receive no additional multiplicity correction. [Quantogram outputs](runs/2026-10-06-main/quantogram-peaks.json), `samples`; full grids and pointwise envelopes are in its `grid_file` paths.

| Sample | n after mass cap | Highest quantum g | Q maximum | Global 95% envelope | Monte Carlo p |
|---|---:|---:|---:|---:|---:|
| Dholavira certain | 289 | 1.71 | 8.004 | 7.666 | 0.004 |
| Dholavira all classes | 552 | 15.00, boundary | 13.464 | 13.797 | 0.319 |
| Susa | 463 | 4.13 | 7.247 | 3.551 | 0.001 |
| Girsu | 67 | 8.42 | 4.280 | 3.360 | 0.001 |
| Rakhigarhi | 9 | 0.44 | 2.736 | 2.935 | 0.124 |

The certain Dholavira maximum at 1.71 g has an eight-fold value of 13.68 g. Another peak occurs at 14.67 g, Q = 7.575. The differences between these peaks and the mixture estimate show dependence on harmonics, mass cap and density assumptions. Bagasra, Nagwada, Shahr-i Sokhta, Kish and Tepe Yahya have p values **0.357, 0.789, 0.378, 0.815 and 0.190** and fail this envelope comparison. The seed annotation makes the affected Monte Carlo findings Exploratory.

Susa's best local fit is **8.313 g (8.271–8.357)** with **2.76% CV**, and Girsu's is **8.404 g (8.321–8.484)** with **2.63% CV**. Their local model advantages over the Indus model are **110.826 and 18.923 AIC units**. Shahr-i Sokhta's best local point is 7.429 g, but its interval spans the entire 7.4–8 g range. Tepe Yahya reaches the 7.4 g unit bound and 20% log-dispersion bound. Kish's best local model loses to background by 3.697 AIC units; its overall Indus/binary tie also reaches the dispersion bound. The latter three assemblages do not establish precise standards under these models. [Unit estimates](summary-tables/unit-estimates.csv), `aic_minus_background` and bootstrap boundaries; [model comparisons](runs/2026-10-06-main/model-comparisons.json).

## Western driving objects and the Gulf

The 18 close western preferences occur at the sites below. Page numbers refer to Ascalone's printed catalogue pages. [Driving-object output](runs/2026-10-06-main/western-driving-objects.json), `objects[].cat`, `site`, `source_printed_pages`, and residual fields.

| Site | Close / eligible | Driving catalogue IDs with printed pages |
|---|---:|---|
| Susa | 10/542 | 35 (44), 82 (45), 174 (47), 220 (48), 257, 280, 281, 282 (50), 476 (55), 590 (59) |
| Girsu | 4/72 | 761, 777 (79), 825, 845 (81) |
| Kish | 1/10 | 875 (86) |
| Tepe Yahya | 2/32 | 953 (105), 993 (106) |
| Shahr-i Sokhta | 1/25 | 1100 (117) |

The fixed-dispersion mixture comparison prefers Indus for **147/701 (20.97%)**, differing from geometric classification for 11 objects. The close count changes to **10/701 at 2%**, **28/701 at 5%**, and **22/701 using canonical 13.65 g**. Removing three historical mass disagreements leaves **18/698** close preferences. Including possible/potential western classes gives **24/818**. Wilson intervals condition on these selected records, fixed supports and estimated reference units; they do not propagate unit-fit uncertainty or account for within-assemblage dependence. [Sensitivities](summary-tables/western-sensitivities.csv); full intervals in `western-compatibility.json`.

The catalogue's proposed Susa Indus-related objects 694 and 698 illustrate reference sensitivity. Their published masses, 13.43 and 27.25 g, come from printed pp. 62–63, and the earlier project reconstructed their proposed relation. They are absent from the primary 18-object set using 14.003 g. Cat. 694 enters the canonical sensitivity; cat. 698 is also close to a three-fold local alternative. The primary list is therefore a model-defined measurement check of candidates, not a census of known imports. [Earlier source report](../2026-10-02-connections-and-priority/regional-west/REPORT.md); local per-object sensitivity scores.

In the Gulf, Bibby's seven Qala'at al-Bahrain weights were already associated with Harappan ratios and the north-gate setting. His English summary lists the masses on printed p. 350. The [post-endpoint amendment](GULF-AMENDMENT.md) compares all seven using source-derived Gulf levels, including a 50-fold level absent from the main Indus list. **6/7** fall within 3% at either **13.5 or 13.65 g** using that Gulf list; the main list at 13.65 g gives **5/7**. Each local 7.8, 8.4 and 9.4 g list gives **1/7** within 3%. The source-derived Gulf list gives smaller residuals than all three local lists for all seven, while the tiny rounded mass remains outside 5%. These seven selected objects cannot identify whether a particular weight was made in the Indus region or Bahrain. [Bibby 1970](https://tidsskrift.dk/kuml/article/view/105436), summary lines 37–66 and printed p. 350; [supplement](gulf-supplement.json), `references`.

## What the precedents established

The bibliography and access record are in [sources.json](sources.json). Full-text access is distinguished from abstracts, figure excerpts and bibliographic notices. The historical subject and the numerical method both have precedents.

| Work | Verified preceding contribution and access limit | Addition here |
|---|---|---|
| Hemmy 1931, *System of weights at Mohenjo-Daro*, pp. 588–598 | Opened chapter, p. 591 Table III: condition-based selection, Harappa/Mohenjo-daro agreement and the doubling then decimal-related levels. | A declared likelihood fit to a different catalogue and explicit uncertainty/selection outputs. |
| Hemmy 1935, *The Statistical Treatment of Ancient Weights*, pp. 83–93 | Opened digitized primary transcript: log-mass distributions, proportional error and sums of probability curves; Susa/Indus attribution ambiguity. OCR details require scan verification. | Reusable bounded mixture code and object-level compatibility checks. |
| Hemmy 1937/1938 | Ascalone p. 197 identifies the 1937 paper as Egyptian Petrie weights; the relevant later Indus chapter is *System of weights* (1938), pp. 601–612. Full texts were not recovered. | Bibliographic clarification only. |
| Mainkar 1984, *Metrology in the Indus Civilization*, pp. 141–151 | Full chapter unavailable. Kenoyer p. 117 describes pooled site averages and questions their regional assumption. | Site-separated fits; no detailed priority judgment against an unread chapter. |
| Kenoyer 2010, *Measuring the Harappan world: Insights into the Indus order and cosmology* | Opened full chapter, pp. 115–117: shared levels, extra categories, material/shape/context differences and regional variation; requests remeasurement and condition study. | Quantified catalogue strata with a specified mixture and retained negative results. |
| Miller 2013, *Weighty Matters: Evidence for Unity and Regional Diversity from the Indus Civilization Weights*, pp. 161–176 | Author bibliography opened; full chapter unavailable. Unity/regional diversity is explicitly an earlier research subject. | No claim of a new regional-variation question. Detailed comparison remains pending. |
| Ascalone and Peyronel 1999/2003; Ascalone 2022 | Earlier regional comparison titles verified in the opened book. The 2022 chapters already analyze local standards, material differences and Dholavira concentrations, including additional fractions. The two earlier full texts were not recovered. | Complete ID extraction, page sample, frozen alternative-model fits and reusable aggregates. |
| Bibby 1970; Højlund 1994, *Stone weights*, pp. 395–397 | Bibby's full source was opened. Højlund's chapter was found through Laursen 2016 pp. 2, 17, which cites Bahrain cubical weights; chapter text remains unavailable. | A seven-object source-led residual sensitivity; broader Gulf assemblage analysis remains incomplete. |
| Ialongo, Vacca and Peyronel 2018, *Breaking down the bullion. The compliance of bullion-currencies with official weight-systems in a case-study from the ancient Near East* | Opened full paper, sections 3–4: frequency distributions, CQA, Monte Carlo and correlations compare Ebla silver and western balance weights; overlapping systems share clusters. | A different catalogue and explicit series/background likelihood comparisons. |
| Ialongo and Lago 2021, *A small change revolution. Weight systems and the emergence of the first Pan-European money* | Opened full paper, sections 3.3–3.5: CQA/Monte Carlo tests of weight regulation against balance weights. | A metrology-specific bounded reanalysis, not a new CQA method. |
| Rahmstorf 2020, *Weight metrology in the Harappan Civilization*, pp. 77–96 | Author abstract and figure excerpts opened: Harappan CQA, a 13.68 g peak, morphology, chronology, contexts and western conversions already studied. Full sample/settings remain unavailable. | Catalogue-specific strata and validation; no priority claim for Harappan CQA. |
| Petruso 1992, *Ayia Irini: The Balance Weights. An Analysis of Weight Measurement in Prehistoric Crete and the Cycladic Islands*, Keos VIII | Bibliography/contents opened. Ialongo and Lago section 3.3 and Lago et al. section 1 identify its earlier CQA application. Monograph text unavailable. | No methodological novelty claim. |
| Lago, Cardarelli and Ialongo 2024, *CQARCHAEO: A PYTHON PACKAGE FOR COSINE QUANTOGRAM ANALYSIS AND MONTE CARLO SIMULATIONS* | Opened article, pp. 215–232: Python CQA/Monte Carlo package and parameter/subsampling discussion. | Custom fixed-series likelihood and extraction code; an existing Python CQA implementation predates it. |
| Vahia and Yadav 2007, *Harappan Weights*, pp. 213–217 | Opened full paper: an earlier numerical reanalysis reports about 6% class dispersion. Its statistic and transcription assumptions differ from this signal CV. | Explicit selection, background mixture and catalogue source audit. |

## Measurements and review still needed

Reweigh the same accessioned objects on a calibrated balance, recording resolution, repeated measurements and rounding. Document edge wear, chips, restoration and material on the same objects. Recover excavation context through DHR/grid/level registers and reconcile the source's 505 contextual objects and five-object class discrepancy. Then compare material, shape, period and mass range jointly with denomination-frequency and additional-fraction models under a new protocol.

For western candidates, review each driving object's identity, condition, creation date and context beside its local standard. The earlier Susa source audit's collisions and conflicting masses remain relevant. Gulf coverage needs Højlund's original chapter and complete additional Bahrain/Failaka assemblages. Harappa and Mohenjo-daro masses were used as literature precedents and are absent from this catalogue endpoint. Original Mainkar, Miller, Ascalone/Peyronel and Rahmstorf texts remain needed for detailed priority comparison.

[Verification](verification.json) reproduces all 2,058 rows, checks endpoint hashes, independently evaluates 45 likelihoods and 169 scalar quantogram points, and independently rescores all 701 western objects. Maximum likelihood and cosine differences are **4.55×10⁻¹³** and **2.31×10⁻¹⁴**. All **1,800 bootstrap refits** are present, and the 45 main fits report **0 optimizer failures**. Bootstrap/Monte Carlo draws were integrity-checked, rather than independently regenerated; independent visual transcription and archaeological classification review remain open.

A full same-code [rerun](reproduction.json) reproduced all **18 numerical files** and **nine local derivative files** byte for byte in a separate dated directory. This includes independently executing the complete bootstrap and Monte Carlo routines with their recorded seeds, while the algorithm and archaeological review limits above remain.
