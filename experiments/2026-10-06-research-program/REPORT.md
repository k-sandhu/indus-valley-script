# What the October 6–7 program found

This report answers the user's October 6 questions from the reviewed packages of the [research program](README.md). Every package result is Exploratory unless stated otherwise. Each package directory holds its protocol, outputs, Sonnet review and later amendments; the numbers below come from those files, and where a review changed a result the corrected figure is given. Nothing here assigns a sound, meaning or numerical value to an Indus sign.

## Stronger models on the Paper 001 restoration benchmark

Better smoothing and a small ensemble improve exact restoration on the saved 8,009 known-slot masks; larger neural models do not. Package A reproduced the saved population, components, folds and queries exactly before fitting.

| Procedure | Top-one | Probability loss (bits) |
|---|---:|---:|
| Paper 001 first-order Markov | 34.59% | 5.12 |
| Paper 001 second-order Markov | 37.27% | 5.25 |
| Modified Kneser–Ney, order 3 | 39.72% | 4.58 |
| GRU masked-slot model | 38.09% | 4.60 |
| Small transformer | 34.20% | 4.97 |
| Kneser–Ney and GRU log ensemble, with extra text | 41.17% | 4.35 |

The ensemble improves on the saved first-order model by 6.58 points (paired component-bootstrap interval 5.74–7.43) and on the second-order model by 3.90 points (3.18–4.65), with the best calibration (0.98% ECE). Accuracy still rises by 1.21–1.71 points between 75% and 100% of each training set, so more transcribed text is likely to help more than model size. Extra text from outside the benchmark population improves probability loss mainly through targets absent from the training alphabet and leaves top-one accuracy unchanged. These comparisons reuse masks that earlier models saw; the chosen ensemble is frozen in `frozen-model/` for a fresh population. [Report](../2026-10-06-modern-restoration/REPORT.md), [review](../2026-10-06-modern-restoration/REVIEW.md).

The review traced a dependence that bears on Paper 001's component-held-out independence claim. Sixteen identical one- or two-sign texts on faces of different objects link 192 benchmark strings across folds, touching 748 queries (9.3%). Respecting those links would lower the paper's first- and second-order top-one by about 0.75 and 0.84 points without changing the order of models. A further 31.9% of strings have a training string one sign edit away; removing those neighbours costs 1.47–2.32 points. The paper's restoration figures should carry this note when it is next revised. [Errata](../2026-10-06-modern-restoration/ERRATA-2026-10-07.md).

## Is all findable evidence indexed with full metadata?

No. The census measured gaps in specific frames, and the frames use different units, so they cannot be added into one worldwide missing-object figure. [Synthesis](../2026-10-06-evidence-census/synthesis/REPORT.md).

Within 19 CISI volume 1 site ranges in Gujarat and north India, 327 of 493 catalogue identifiers appear in the local corpus export and 166 (33.7%) do not, including 111 at Lothal, 26 at Kalibangan and 14 at Banawali; Rehman Dheri has 268 absent keys among 270 mixed entries. Mahadevan's 1977 concordance selected 2,906 inscribed objects from 3,455 photographed. ICIT's last published totals (2023) are 4,665 objects and 5,650 texts, with no current object-level inventory available. Online museum catalogues expose at least 114 original records of inscribed Indus objects at six institutions (National Museum New Delhi 76, Indian Museum Kolkata 18, British Museum 6, Metropolitan Museum 5, Penn Museum 5, Louvre 4); at least 61 of them join to corpus records through CISI concordances and excavation numbers (the census review found further records that meet the same standard). Bibliography is absent from 101 of the 114 records.

The local corpus export, the broadest machine-readable record the project holds, has these fields:

| Field | Present in 5,680 faces |
|---|---:|
| Named site | 99.5% |
| Excavation or registration number | 90.6% |
| Material | 82.9% |
| Period or phase | 55.9% |
| Depth | 49.5% |
| Room or grid findspot | 38.6% |
| All three dimensions | 20.3% |
| Numerical date, link to a dated sample, photograph link, item-level rights | 0% |

The largest gains would come from current ICIT and complete CISI inventories, the Harappa and Mohenjo-daro field registers behind 4,640 local faces, the Rehman Dheri and Lothal catalogue gaps, and post-CISI inventories from Dholavira, Kalibangan, Farmana and Rakhigarhi. The synthesis proposes schema changes for a complete index in [SCHEMA-AMENDMENTS.md](../2026-10-06-evidence-census/synthesis/SCHEMA-AMENDMENTS.md); no request to an institution has been sent.

## Results outside decipherment that could be published

The corrected inventory ranks five deliverables first, each with a finite saved result: the 687-cell annotated sign chart from the CC BY 1979 Helsinki edition, with 16 retained lower-code ambiguities read by AI models and awaiting epigraphic review; the context-completeness audit of the corpus export; a notice that the government-hosted CISI volume 1 PDF repeats its own 431 pages; the exact solution set of the published 10/8/6 numerical proposal with its premise audit; and the cross-catalogue join audit. The Susa catalogue discrepancies remain candidates. [Inventory](../2026-10-06-byproduct-inventory/REPORT.md), [review](../2026-10-06-byproduct-inventory/REVIEW.md).

## Frenez's lecture statements tested against the corpus

The coordinator checked the user's summary of the lecture against its captions; every summarized point is in the talk ([caption check](frenez-talk-check.md)). Packages D1 and D2 then tested the statements that the local corpus can address.

| Statement in the lecture | Result | Package |
|---|---|---|
| Sign 740 accounts for 10% of occurrences | 9.67% of all positions, 10.67% of readable ones, 10.03% in deduplicated texts | D2 |
| Top three, six and twenty signs hold 20%, 30% and half | 18.64%, 27.51% and 48.76% of readable positions | D2 |
| Sign 740 usually ends an inscription | 874 of 1,256 occurrences (69.59%) are final, against 299 expected by position | D2 |
| Large sites show more than 500 signs, small ones 20–50 | No adequately sampled site departs from a shared rarefaction curve; inventory size follows sample size | D2 |
| Sign 740's use relates to site size or type | No corrected association across 17 sites | D2 |
| Unicorn dominates inside the valley, the "Indus bison" outside | 1,236 of 1,604 core known motifs are unicorns; 15 of 27 external known motifs are gaur, including all 13 circular motifs | D2 |
| Motif frequencies stay the same for almost a millennium | The q = 0.007 difference comes from Period 3C subphase labels that share one date range; unambiguous phases give 6 of 7 unicorns in 3B and 112 of 123 in 3C, which does not contradict persistence | D2 |
| Inscribed media diversify around 2100 BCE | Period 3C has 4.60 more rarefied object types than 3B (Holm p = .0145), and 3.74 and 4.36 more within period-labelled faces only and Mound E only, so the rise survives the excavation-composition difference between the periods | D1 |
| A small sign set marks the earliest phase | 31 early families with 18 signs match what later samples of the same size show | D1 |
| "Man" and "twins" signs are frequent outside the valley | Wells 090 and 091 are 7 and 5 of 149 external tokens against 184 and 22 of 17,792 core tokens; all external cases are on circular seals, so no matched comparison exists | D1 |
| Statistical work treats the corpus as monolithic | Harappa 3B and 3C differ by 0.190 bits after object-type adjustment, 0.033 bits above the permutation-null mean, and sign 034 passes a false-discovery correction; the apparent rise in text length (0.72 signs) falls to 0.12–0.16 within single-excavation subsets; regional differences pass in 4 of 6 pairs under one reference and 1 of 6 under another | D1 |

The lecture's interpretive claims, such as seals as corporate badges and the unbalanced oligopoly, are attributed positions; Frenez develops the oligopoly argument in his 2018 chapter, pp. 186–187. [D1](../2026-10-06-chronology-region/REPORT.md), [D2](../2026-10-06-sign-context-and-seals/REPORT.md).

## What other researchers recommend

After two reviews and a rebuild from opened sources, the survey holds 56 recommendations from 27 sources covering 21 of 25 named researchers. Regional and chronological analysis, separating artefact classes, and accessible collaborative data recur; whether statistical regularities can establish a language remains disputed (Farmer, Sproat and Witzel against Rao and colleagues). The survey's top-ranked action for this project is extending the object, source, date, site and type ledger, which the census has begun. [Survey](../2026-10-06-field-recommendations/REPORT.md), [second review](../2026-10-06-field-recommendations/REVIEW-2.md).

## Working backwards from later scripts

The dated evidence table, after review and correction, holds 65 rows from 50 sources and 17 attributed continuity claims, with 30 dated contributors to the coverage count. Every century from about 3500 to 200 BCE has some dated marked material in the broad record. Restricted to the two strongest dating grades, two 100-year bins are empty; restricted further to high or moderate dating strength, the empty stretch is 400–1,600 years long depending on how two rows, Pirak's seals and Perumbalai, are dated. An earlier figure of a 600-year gap at 1300–700 BCE came from a table that omitted dated contexts such as Daimabad Phase V (1400–1000 BCE, marked pottery and a cylinder seal) and a Sivagalai urn dated to 1155 BCE. No dated transmission chain links Indus signs to later scripts. The early end is better documented: pre-firing potters' marks in the fourth millennium, seal use by the early third millennium, and a sealing at Harappa attributed to the Kot Diji phase. Frenez's remark that writing was reintroduced in the fifth century BCE is recorded beside the dated Brahmi evidence (Anuradhapura, Porunthal, Kodumanal, Keeladi and the Ashokan inscriptions), which constrains timing but not who reintroduced writing. Four test designs specify what would distinguish transmission from independent invention. [Report](../2026-10-06-backward-chronology/REPORT.md), [corrections](../2026-10-06-backward-chronology/amendment-2026-10-07-review-corrections/README.md), [test designs](../2026-10-06-backward-chronology/TEST-DESIGNS.md).

## The Indus civilization beyond the script

The weight catalogue gives a precise picture of the Dholavira standard once mass bands are separated: 90 weights of 5–100 g fit a unit of 13.716 g with 1.6% variation, matching the commonly cited Harappan unit, while 147 weights of 1.3–5 g fit 14.280 g with 5.8% variation. Ascalone's 2022 catalogue already reports the heavier small-weight group. Matching western weights against the Indus standard gives no evidence of Indus-standard weights in Mesopotamia and Iran: the observed close fits (136 and 18 under two rules) fall below those produced by masses without fine structure (170 and 39). [Weights](../2026-10-06-weight-metrology/REPORT.md), [review](../2026-10-06-weight-metrology/REVIEW.md).

Seal measurements give two physical results. Of 1,027 complete measured square seals, size varies with a coefficient of variation of 0.29, and text length rises by 1.16 signs for each doubling of face area. Texts on unicorn seals average 0.78 signs longer than on rare-motif seals, and once length is controlled their sign distributions do not differ. [D2](../2026-10-06-sign-context-and-seals/REPORT.md).

## A chance baseline for the reported graffiti resemblance

A shape-descriptor pilot on the 42 Tamil Nadu base signs shows that an unrelated script matches about as often as the Indus subset under a coarse rule: Indus 30, Ogham 24 and Tifinagh 31 of 42. Under a strict rule without orientation the counts are 4, 2 and 9. In the 4–6 segment band the Indus subset matches 14 of 15 drawings against 10 for Ogham and 7 for Tifinagh. Two coders agreed on 46% of complete descriptors, 78% without orientation. The 2025 study's own matching criteria were not available. [Pilot](../2026-10-06-resemblance-baseline/REPORT.md), [review](../2026-10-06-resemblance-baseline/REVIEW.md).

## What is new and what would move the field

The program's clearest new contributions are measurements that other researchers can check and use. The catalogue-coverage figures, the museum-to-corpus joins and the field-completeness table describe the state of the evidence in specific, citable terms. The tests of Frenez's statements confirm several with exact denominators (the jar sign's share and final position, sign concentration, the gaur on external seals), find no evidence of motif change between unambiguous Period 3B and 3C labels (6 of 7 and 112 of 123 unicorns, a small 3B sample) and qualify others (site inventory size follows sample size; the early small sign set is a sample-size effect). The resemblance pilot shows that a reported resemblance rate needs a chance baseline and a coding rule two people can apply. The weight analysis separates two Dholavira mass bands and finds no western Indus-standard signal under a chance control. The restoration comparison improves the Paper 001 benchmark by 6.6 points and identifies a dependence the original split missed.

Precedents limit the novelty of several results. Yadav et al. 2010 had already used a deduplicated held-out restoration evaluation, and Ascalone 2022 reported the heavier small-weight group. Sub-corpus comparison is less unattempted than the lecture suggests: Yadav 2013 compared sign frequency and length by site, object type and West Asian provenance; Suga 2024 traced diachronic change across 1,137 stylistically ordered seals; Rao et al. 2009 compared external texts by likelihood; Vidale 2004 and 2005, following Parpola 1986, discussed the "man" and "twins" signs on external seals as possible patronymics; and Kenoyer 2020 already places inscribed tablets in Harappa Period 3B and wider media in 3C. Packages D1 and D2 add explicit object-type adjustment, whole-family resampling and sample-size controls on one preserved export, which is a refinement of those studies rather than a first attempt. The remaining limit is the evidence itself: the corpus lacks dated contexts for nearly half its faces and photographs or rights links for all of them, and no bilingual or independently counted object has been found. The most useful next steps are the ledger the survey and census both point to, archive requests for the catalogue gaps the census names, and fresh transcribed text for the frozen restoration model.
