# Chance baseline for cross-script resemblance

At a common reference size of 20, the amended coarse rule gives mean coverage of **53.70% for Indus, 57.14% for Ogham and 65.11% for Tifinagh**. The paired Tifinagh-minus-Indus difference is **11.41 percentage points**, with a central 95% interval of **[-9.52, 35.71]** across reference-subset pairs using the same 42 queries. Full inventories give **30, 24 and 31 matches**. Complexity changes the ordering: counts for 1–3 segment queries are **16/24, 14/24 and 24/24**; for 4–6 segments, Indus leads with **14/15**, against **10/15 and 7/15**; all inventories miss the three 7+ segment queries. Restricting references to at most six segments and common size 16 gives Indus and Tifinagh means of **63.89% and 61.48%**, a paired difference of **2.41 points [-16.67, 19.05]**. The coarse ordering is sensitive to inventory composition. [Size comparisons](run-v2/paired-size-comparisons.json), `version=v2`, `rule=R1`, `n`, `inventories`, `paired`; [counts and bands](run-v2/observed.json), `matched`, `complexity`.

Inter-coder reliability limits interpretation. Original primary/reviewer complete agreement is **52/113 (46.02%)**, including **61/113 orientation agreements (53.98%)**. Without orientation, complete agreement is **88/113 (77.88%)**. A consistently applied shape descriptor is a prerequisite for interpreting a resemblance percentage. The amended strict rule removes orientation; symmetry and composite segmentation still require independent tracing. [Reliability](run-v2/inter-coder-reliability.json), `primary_reviewer_113`; [amendment](PROTOCOL.md).

## What the sources specify

K. Rajan and R. Sivanantham's *Indus Signs and Graffiti Marks of Tamil Nadu: A Morphological Study* was published by the Department of Archaeology, Government of Tamil Nadu, Chennai, in 2025. The [government PDF](https://tamildigitallibrary.in/assets/docs/uploads/catalogue_article_file/BOK/upload/2025/08/TVA_BOK_0065888_Indus_Signs_and_Graffiti_Marks_of_Tamil_Nadu_A_Morphological_Study.pdf) has eight pages and matches the October 2 witness by SHA-256. The [library MARC record](https://tamildigitallibrary.in/Marc-Articles/Indus%20signs%20and%20graffiti%20marks%20of%20Tamil%20Nadu) identifies it as an **8-page booklet**, field 300, record TVA_BOK_0065888. A [separate paperback record](https://www.exoticindiaart.com/book/details/indus-signs-and-graffiti-marks-of-tamil-nadu-morphological-study-hby328/) gives **145 pages and ISBN 9788197784255**. The complete edition remains unexamined. [sources.json](sources.json), `rajan-2025-brochure`, `library-marc-2025`, `exotic-book-record`.

Booklet page 5 defines recognizable scratches on ceramics as graffiti, distinguishes them from script on seals and metal objects, and defines variants by added strokes and composites by multiple bases. Pages 4–5 report **42 bases, 544 variants, 1,521 composites and 2,107 forms**. Page 5 reports **15,184 graffiti-bearing potsherds from 140 sites**, with approximately **14,165 documented sherds**. These counts use different units. [Original observations](source-observations.json), `morphology-classification`, `morphology-input-population`, `morphology-documented-population`.

Page 5 distinguishes exact and near parallels and reports about **60%** for base signs and variants against Indus script, and more than **90%** for South Indian and Indus graffiti. The latter concerns pottery marks; this pilot uses an Indus script-sign subset. Neither percentage has a stated numerator, eligible denominator, weighting rule or numerical tolerance. Page 3 names lists of **419, 386 and 695 signs** without tying a list to those percentages. Pages 6–7 present comparison triplets; page 6, left panel row 2, labels a flipped Mohenjadaro seal beside Kodumanal_TNSDA-G-0780. A general transformation policy is unstated. Page 8 asks for further material evidence for contact. [Original observations](source-observations.json), `morphology-parallels`, `morphology-inventory-reference`, `morphology-transform-example`, `morphology-additional-evidence`.

The booklet supplies no operational threshold, negative inventory, chance calculation or coder agreement. The exact [The Week PTI item of 6 January 2025](https://www.theweek.in/wire-updates/national/2025/01/06/mes7-tn-excavations-indus-valley.html), recovered in this follow-up, uses nearly 90% initially and more than 90% later. The [Oneindia PTI item](https://www.oneindia.com/chennai/tamil-nadu-graffiti-links-to-indus-valley-civilization-reveals-ancient-exchange-4034613.html) was the v1 news witness. [Sources](sources.json), `pti-theweek-2025`, `pti-oneindia-2025`; [criteria observation](source-observations.json), `morphology-criteria`.

The targeted reading of the authors' 2026 *Inscribed Potsherds of Tamil Nadu: Graffiti and Tamiḻi*, Volume I, adds revised counts and a precedent. Table 3.3 at **PDF p. 273 / printed p. 234** gives **551 variants, 1,531 composites and 2,124 forms**. PDF p. 282 describes comparison plates for visual assessment, but labels those totals differently; the table supplies the category labels used here. The preface, PDF p. 12, repeats nearly 60%. On **PDF p. 302 / printed p. 263**, the authors attribute to **B. B. Lal (1962:21)** nearly **89%** of Iron Age megalithic signs having parallels in Harappan and central Chalcolithic cultures, and, in reverse, **85%** of Harappan-Chalcolithic signs occurring in Iron Age culture. These figures are reported through Volume I; Lal's original paper was not opened. No numerical matching threshold appears on the inspected pages; this was a targeted reading. [Volume I catalogue](https://tamildigitallibrary.in/Articles/062969_Inscribed_Potsherds_of_Tamil_Nadu_Vol_1); [new observations](source-observations-v2.json), `volume-I-classification-revision`, `volume-I-lal-1962`, `volume-I-method-scope`.

## Precedents, inputs and scope

Changizi, Zhang, Ye and Shimojo (2006), *The Structures of Letters and Symbols throughout Human History Are Selected to Match Those Found in Objects in Natural Scenes*, *The American Naturalist* 167(5): E117–E139, reports similar contour-configuration distributions across writing and symbol classes. Its [abstract](https://www.journals.uchicago.edu/cgi-bin/resolve?id=doi:10.1086/502806) was opened during v1; full text returned 403 and a topology-method passage was seen only in a snippet. It motivates a baseline without supplying this null. A [Harappa book review](https://www.harappa.com/content/indus-signs-and-graffiti-marks-tamil-nadu) discusses independent geometric recurrence; its reviewer byline and date remain unidentified. A [CypherSolver page](https://dbourdeau.github.io/cyphersolver/indus.html) gives an adjacent lexical-picture chance test whose code and outcomes were not audited. The bounded search established no verified quantitative baseline for the 2025 shape comparison. Original search failures remain local. [sources.json](sources.json), `changizi-2006`, `harappa-review`, `cyphersolver-adjacent`.

The pilot reuses the October 2 source audit, booklet, portal base-sign crosswalk and 687-cell atlas. Its seeded 42-cell Indus sample supplies **36 readable references**, including possible variants of one numbered sign. I00, I01, I08, I10, I11 and I39 were excluded without replacement; **22/36** retained uncertainty. Controls are **20 Ogham letters**, including stemlines, and **32 Tifinagh letters, U+2D30–U+2D4F**, from [Unicode Ogham](https://www.unicode.org/charts/PDF/U1680.pdf) and [Tifinagh](https://www.unicode.org/charts/PDF/U2D30.pdf), version 18.0, PDF page 2, printed pages 149 and 321. Five filled Ogham lozenges were interpreted as centreline outlines and flagged uncertain. These modern glyphs supply assumed unrelated controls with limited historical coverage. [Manifest](run-v2/manifest.json), `counts`, `excluded_indus_cells`; [sources](sources.json), `koskenniemi-parpola-1979`, `unicode-ogham`, `unicode-tifinagh`.

The [Unicode terms](https://www.unicode.org/copyright.html) permit internal annotated copies; no open redistribution licence for these chart PDFs was verified. Drawings, crops, raw coding and extracts stay local. Each Tamil Nadu base type has equal weight. Segments are maximal straight portions or smooth arcs, rather than inferred pen strokes. [PROTOCOL.md](PROTOCOL.md) fixes the fields and assumptions. Adjacency, relative lengths, exact angles, chronology, position and composite order are outside this endpoint.

## Corrections and version comparison

The **7 October post-outcome amendment is Exploratory**. V1, its code and original inputs remain unchanged. Seven source drawings were reopened at enlarged resolution. Historical orientation labels were retained as unused metadata. Local `amendment-20261007/corrections-v2.json` records each old/new value, reason and source/crop path.

| Drawing and source | Correction v1→v2 | Visible reason |
|---|---|---|
| T10, booklet PDF 4 | Y 1→0; other 0→1; terminals 3→4 | Line continues past arrowhead vertex: four rays, one through-line |
| U+2D3C, Unicode PDF 2 | segments 5→7; loops 2→0; terminals 0→4 | H with four outward serifs; neither side closes |
| U+2D3D, Unicode PDF 2 | L 1→3; X 1→0; terminals 3→1 | Triangle plus branch ending at a T contact on hypotenuse |
| U+2D3F, Unicode PDF 2 | L 1→3; X 1→0; terminals 3→1 | Same topology, with reversed triangle orientation |
| U+2D45, Unicode PDF 2 | segments 2→3; X 1→0; other 0→1; terminals 4→5; symmetry both→vertical | Vertical ray meets crossing: five-way contact |
| U+2D47, Unicode PDF 2 | loops 2→1; T 2→0; Y 0→1; terminals 0→1 | Upper triangle closes; bottom bar ends freely at right |
| U+2D49, Unicode PDF 2 | segments 3→4; L 1→3; Y 1→0; terminals 3→2 | Four-part zigzag, three corners, two endpoints |

Uncertainty flags for U+2D3D, U+2D3F and U+2D47 were cleared for the inspected contacts. R3S requires all integer counts plus symmetry, dropping orientation because coders applied different direction conventions. The amendment defines symmetry using normalized centreline reflection, a 0.05-distance tolerance, matching contacts and preserved connectivity. Most existing rows have not been retraced under that criterion. R3S tests sensitivity to omitting orientation; it does not validate every legacy symmetry label.

This bounded correction covers the seven specified drawings. The review also disputes U+168B's symmetry, I05's bent-arm segmentation and the corner ticks counted in I07. Those primary rows remain in v2 and their alternative reviewer rows enter the sensitivity analysis. They require source tracing in the next pass. [REVIEW.md](REVIEW.md), independent recoding section; [sensitivity](run-v2/coding-sensitivity.json).

| Inventory (size) | R1 v1 / v2 | R2 v1 / v2 | Original R3 v1 / v2 | R3S on v1 rows / v2 |
|---|---:|---:|---:|---:|
| Indus (36) | 30 / 30 | 5 / 4 | 4 / 4 | 4 / 4 |
| Ogham (20) | 24 / 24 | 3 / 3 | 1 / 1 | 2 / 2 |
| Tifinagh (32) | 32 / 31 | 13 / 11 | 10 / 9 | 11 / 9 |

Every denominator is 42. R3S on v1 rows is a new sensitivity calculation. [Version comparison](run-v2/v1-v2-comparison.json), `cells`; [original counts](run-v1/observed.json); [amended counts](run-v2/observed.json).

## Three codings and agreement

The original blind second pass coded 20 drawings; 19 are comparable after excluding I00. The reviewer recoded **113/130 readable drawings**: 42 Tamil Nadu, 32 Tifinagh, 15 Ogham and 24 Indus. The reviewer overlay retains primary rows for **17** drawings; the second-pass overlay retains primary rows for **111**. These are partial sensitivity sets, rather than three independently completed inventories.

| Inventory | R1 all-nine range | R2 range | Original R3 range | R3S range |
|---|---:|---:|---:|---:|
| Indus | 30–30 | 4–5 | 1–4 | 4–4 |
| Ogham | 24–24 | 3–3 | 0–1 | 0–2 |
| Tifinagh | 31–32 | 11–13 | 8–10 | 9–11 |

All nine combinations cross three query codings with three reference codings. Using the same coding set for both gives original-R3 ranges **2–4, 0–1 and 8–10**; other rule ranges are unchanged. The review's three alternatives to primary/primary give **1–3, 0–1 and 8–9**, reconciling its quoted ranges with this table. Tifinagh matches at least as many drawings as Indus under every full-inventory rule/coding combination tested; this does not extend to every random subset or complexity restriction. [Sensitivity](run-v2/coding-sensitivity.json), `cells`, `ranges`; [review sensitivity](review/sensitivity.json).

Primary/reviewer agreement is **101/113 for R1**, **95/113 for integer counts**, **103/113 for symmetry** and **61/113 for orientation**. Complete agreement is **52/113**, or **88/113** without orientation. On the shared 19 drawings, complete agreement is **12/19 primary/second, 9/19 primary/reviewer and 9/19 second/reviewer**; without orientation, **15/19, 14/19 and 13/19**. V2 corrections were informed by review and supply no new independent agreement estimate. [Reliability](run-v2/inter-coder-reliability.json), `primary_reviewer_113`, `shared_sample`.

Before coding, the reviewer saw matched identifiers, second-pass notes, excluded I00's primary row and the T18 correction; T18 is not independent. T07's L count changed after comparison, with the earlier row preserved. One reviewer, partial coverage and shared instructions limit this assessment. I14's codings agree on three loops but give **7, 9 or 11 segments**, illustrating unresolved segmentation. [REVIEW.md](REVIEW.md), independent recoding section; [reviewer rows](review/reviewer-coding.json) and local coder files.

## Paired size and complexity comparisons

Subsampling uses 2,000 draws without replacement. The paired calculation samples references independently while retaining the same 42 queries. Intervals describe subset-pair variation; census counts receive no population confidence interval.

| Common size 20, v2 | R1 mean [central 95% interval] | R3S mean [interval] |
|---|---:|---:|
| Indus | 53.70% [33.33%, 71.43%] | 5.42% [0%, 9.52%] |
| Ogham | 57.14% [57.14%, 57.14%] | 4.76% [4.76%, 4.76%] |
| Tifinagh | 65.11% [52.38%, 73.81%] | 14.57% [9.46%, 21.43%] |

Paired Indus-minus-Tifinagh R3S is **-9.15 points [-19.05, 0]**. Ogham intervals are degenerate because all references are retained. The new paired simulation uses its declared separate random stream; Monte Carlo means differ slightly from v1's independent per-inventory simulation, whose exact R1 means at n=20 were **53.57%, 57.14%, 67.74%**. [Paired outputs](run-v2/paired-size-comparisons.json), `version=v2`, `n=20`; [v1 subsampling](run-v1/subsampling.json), `exact_mean`; [v2 subsampling](run-v2/subsampling.json).

Restricting references to at most six segments leaves **21 Indus, 16 Ogham and 31 Tifinagh**. At n=16, R1 means are **63.89%, 57.14% and 61.48%**. This balances upper complexity support without equalizing band frequencies, loops or curves. The medium-band Indus lead and simple-band Tifinagh lead require joint complexity matching in a fuller design. Queries have **24/15/3** drawings in the three bands; three complex-query failures provide little information about that band. [Paired outputs](run-v2/paired-size-comparisons.json), `version=v2`, `n=16`, `eligible_sizes`, `complexity`; [manifest](run-v2/manifest.json), `counts`.

The full-inventory paired test reproduces the review's v1 R1 Indus/Tifinagh discordances: **6 Indus-only, 8 Tifinagh-only**, exact two-sided **p=0.7905**. V2 gives **7 and 8**, **p=1.0000**; amended R3S gives **3 and 8**, **p=0.2266**. These exploratory, unadjusted tests condition on unequal full inventories and assume independent exchangeable discordant query types; repeated shape classes weaken that assumption. [Paired full-inventory output](run-v2/paired-full-inventory.json), `v1.cells`, `v2.cells`, `only_left`, `only_right`, `exact_two_sided_p`.

## Synthetic calculation and missing generator

The Synthetic calculation is **within-inventory re-drawing**: observed complete descriptor vectors are sampled with replacement from each inventory's empirical joint distribution, independently for 42 surrogate queries and n references. Collision expectation is `sum_d p(d) * [1 - (1-p(d))^n]`. A second column holds Tamil Nadu queries fixed. It preserves observed combinations without introducing unseen shape classes. Surrogate-query rates describe inventory self-collision; fixed-query rates describe coverage of these Tamil Nadu drawings. Larger reference sizes saturate observed support. [V1 calculation](run-v1/synthetic-null.json); [v2 calculation](run-v2/synthetic-null.json), `surrogate_query`, `fixed_tamil_query`, `support_ceiling_fixed_tamil`.

The requested random-mark generator **was not built**. This correction pass lacks traced adjacency/angle data and held-out inventories to fit and validate segment, loop and junction dependencies. An arbitrary geometric generator would add untested choices to an unreliable descriptor. The missing component prevents estimation of novel invented-mark frequency. A full study should register a generator fitted on training controls and test its distributions and drawings against held-out families before using its collision rate as a chance baseline.

## Next study

A full study should acquire the complete 2025 method and comparison tables, identify each percentage's unit, and fix drawings, allowed transformations and exclusions before coding. Two trained human coders should independently trace a deduplicated Indus list, Tamil Nadu bases and composites, and several historical controls with adjacency, angles and relative lengths. Balance size and complexity jointly and assess reliability before interpreting resemblance rates. Secure specimen dates, object function, positional behavior and ordered composites can then test any surviving shape excess.
