# Chance baseline for cross-script resemblance

The resemblance rate changes sharply with the declared rule. Across 42 Tamil Nadu base drawings, the Indus sample matches 30 under a two-count rule and four under the full descriptor. Tifinagh matches 32 and ten under the same rules. This pilot therefore finds no Indus advantage over both controls within the selected inventories. Its main limitation is annotation quality: six sampled Indus cells were excluded and 22 retained uncertainty, while complete-vector agreement is 12/19 comparable drawings. These results support testing a stated matching rule and its controls before interpreting a resemblance percentage. They do not estimate the authors' 90% claim. [Observed outcomes](run-v1/observed.json), [coverage](run-v1/manifest.json), [agreement](run-v1/agreement.json).

## What the 2025 source specifies

K. Rajan and R. Sivanantham's *Indus Signs and Graffiti Marks of Tamil Nadu: A Morphological Study* was published by the Department of Archaeology, Government of Tamil Nadu, in 2025. The [government download](https://tamildigitallibrary.in/assets/docs/uploads/catalogue_article_file/BOK/upload/2025/08/TVA_BOK_0065888_Indus_Signs_and_Graffiti_Marks_of_Tamil_Nadu_A_Morphological_Study.pdf) contains eight PDF pages. Its SHA256 matches the preserved October 2 brochure. A bookseller search result describes a 145-page monograph, so the audit below applies to the brochure. The complete book remains unexamined. [Source record](sources.json), `rajan-2025-brochure` and `exotic-book-record`.

PDF page 5 treats recognizable scratches on South Indian ceramics, and some Indus ceramics, as graffiti, while distinguishing the signs on seals and metal objects as script. It defines variants by additional strokes and composites by multiple base signs. Pages 4–5 give 42 bases, 544 variants and 1,521 composites, totaling 2,107 classified forms. Page 5 reports 15,184 graffiti-bearing potsherds from 140 sites and approximately 14,165 documented sherds. These are different units and populations. [Source observations](source-observations.json), `morphology-input-population`, `morphology-documented-population`, `morphology-classification`.

Page 5 distinguishes exact and near parallels. It reports nearly 60% for base signs and their variants and more than 90% for South Indian and Indus graffiti marks. It supplies no numerator, eligible denominator, weighting rule or reproducible tolerance for either percentage. Page 3 cites Indus lists of 419, 386 and 695 signs without identifying a single comparison inventory behind those percentages. Pages 6–7 arrange named pottery and seal examples beside one another; PDF page 6, left panel row 2, explicitly labels a flipped Mohenjadaro seal beside Kodumanal_TNSDA-G-0780. A displayed reversal is therefore part of the presentation, although a general rotation/reflection policy is not stated. Page 8 asks for additional material evidence to strengthen the contact hypothesis. [Source observations](source-observations.json), `morphology-parallels`, `morphology-inventory-reference`, `morphology-transform-example`, `morphology-additional-evidence`.

No operational threshold, negative script inventory, chance calculation or coder-agreement measurement occurs in this eight-page witness. The full monograph might contain additional method information. The PTI-labelled [Oneindia report of 6 January 2025](https://www.oneindia.com/chennai/tamil-nadu-graffiti-links-to-indus-valley-civilization-reveals-ancient-exchange-4034613.html) repeats nearly 90%; the exact The Week URL mentioned in the contribution assessment was not recovered. [Source records](sources.json), `rajan-2025-brochure`, `pti-oneindia-2025`; [method observation](source-observations.json), `morphology-criteria`.

## Precedents and comparison witnesses

Changizi, Zhang, Ye and Shimojo's 2006 paper, *The Structures of Letters and Symbols throughout Human History Are Selected to Match Those Found in Objects in Natural Scenes*, *The American Naturalist* 167(5): E117–E139, reports similar distributions of contour configurations across writing and symbol classes. The [journal abstract](https://www.journals.uchicago.edu/cgi-bin/resolve?id=doi:10.1086/502806) was opened; the topology-method section was visible only in a search snippet and the full-text route returned 403. This motivates a configuration baseline but supplies no tested null for the present inventories. The [Harappa book review](https://www.harappa.com/content/indus-signs-and-graffiti-marks-tamil-nadu) already discusses independently recurring basic geometric marks. This qualitative criticism precedes this pilot; its reviewer byline and publication date were not identified. [sources.json](sources.json), `changizi-2006`, `harappa-review`.

The bounded search found no verified quantitative shape baseline for the 2025 comparison. A public CypherSolver page uses a chance baseline for lexical-picture matching and discusses Tamil Nadu composite order; those are adjacent questions, and its code and outcomes were not audited here. The search and failed-download record is preserved locally in `web-search-log.json`, `acquisition.json` and `acquisition-retry.json`. [Source record](sources.json), `cyphersolver-adjacent`.

The controls use [Unicode Ogham](https://www.unicode.org/charts/PDF/U1680.pdf), PDF page 2/printed page 149, and [Unicode Tifinagh](https://www.unicode.org/charts/PDF/U2D30.pdf), PDF page 2/printed page 321. The acquired files identify themselves as version 18.0. Their charts and [terms](https://www.unicode.org/copyright.html) permit internal annotated copies but do not provide an open redistribution licence for these PDF drawings. Full chart copies, crops and coding rows remain local. Their reference glyphs are modern typographic witnesses; genealogical independence from Indus and Tamil Nadu marking traditions is a control-selection assumption, not demonstrated by this pilot. Ogham includes the visible stemline, and its five filled vowel lozenges were interpreted as outlined centreline diamonds and flagged uncertain. Tifinagh includes a fixed contiguous 32-letter subset, U+2D30–U+2D4F. These choices prevent the controls from representing all historical forms of either script. [Source records](sources.json), `unicode-ogham`, `unicode-tifinagh`, `unicode-terms`; [codebook](PROTOCOL.md).

## Coding and observed rates

The descriptor counts maximal straight portions and smooth arcs rather than inferred pen strokes. It also counts enclosed regions, corner and junction types, endpoints, connected components and dots, then records coarse symmetry and direction. R1 requires identical segment and loop counts. R2 requires all integer counts. R3 adds symmetry and direction. These summaries omit adjacency, relative length and exact angle: even an R3 match need not be an identical drawing. The full rules and fixed sampling seeds appear in [PROTOCOL.md](PROTOCOL.md).

| Reference inventory | Coded references | R1 | R2 | R3 |
|---|---:|---:|---:|---:|
| Indus seeded cell sample | 36 | 30/42, 71.43% | 5/42, 11.90% | 4/42, 9.52% |
| Ogham traditional letters | 20 | 24/42, 57.14% | 3/42, 7.14% | 1/42, 2.38% |
| Tifinagh fixed subset | 32 | 32/42, 76.19% | 13/42, 30.95% | 10/42, 23.81% |

Source: [observed.json](run-v1/observed.json), fields `matched`, `queries`, `rate`. Every base type receives equal weight. Census fractions have no sampling confidence interval. The Indus references are cells of the 687-cell atlas, including possible variants of one numbered sign, and are not the authors' complete comparison list. Six exclusions were declared before computation and no replacements were selected: I00, I01, I08, I10, I11 and I39. [Manifest](run-v1/manifest.json), `excluded_indus_cells`; local `indus-selection.json` and `coder-a.json` retain every source coordinate and decision.

The independent pass coded 20 prescribed drawings without primary annotations or outcomes. Nineteen were comparable because the primary pass excluded I00. Segment, curve and loop counts each agree on 18/19; symmetry agrees on 16/19 and direction on 15/19. R1 and R2 descriptor vectors each agree on 17/19 (89.47%); R3 and complete vectors agree on 12/19 (63.16%). I14 differs in segment and curve segmentation; U2D3F differs in loop/contact interpretation. Both passes are agents using the same codebook, so this measures agent-pass reproducibility. It does not establish reliability for trained human coders. Disagreements remain unadjudicated and primary rows define this endpoint. [Agreement](run-v1/agreement.json), `fields`, `rule_vector`, `complete_vector`; local `coder-b.json` and `coder-b-notes.md` preserve the independent decisions.

## Inventory size and complexity

At a common reference size of 20, the following table gives the mean Tamil Nadu match percentage over 2,000 samples without replacement and the central 95% simulation interval. These are intervals over reference subsets, conditional on the coded inventories.

| Inventory | R1 mean [interval] | R3 mean [interval] |
|---|---:|---:|
| Indus | 53.38% [33.27%, 69.05%] | 5.10% [0%, 9.52%] |
| Ogham | 57.14% [57.14%, 57.14%] | 2.38% [2.38%, 2.38%] |
| Tifinagh | 67.70% [54.76%, 76.19%] | 16.19% [9.52%, 21.43%] |

Source: [subsampling.json](run-v1/subsampling.json), `n=20`, `mean`, `q025`, `q975`; `exact_mean` gives the corresponding combinatorial expectation. The Ogham interval is degenerate because all 20 references are retained. All sizes 5, 10, 20 and each full inventory, with complexity-stratified intervals, are in the same file.

Size alone does not balance complexity. Tamil Nadu has 24 drawings with 1–3 segments, 15 with 4–6 and three with 7+. The Indus sample has 5, 16 and 15; Ogham has 6, 10 and 4; Tifinagh has 21, 11 and zero. Under R1, simple Tamil Nadu marks match 16/24 Indus, 14/24 Ogham and 24/24 Tifinagh references; medium-complexity marks match 14/15, 10/15 and 8/15. None of the three complex queries matches under any rule. Those three failures are too few to characterize complex-mark transmission, and Tifinagh has no sampled complexity support there. [Manifest](run-v1/manifest.json), `counts.*.complexity_counts`; [observed.json](run-v1/observed.json), `complexity`.

## Synthetic descriptor null

The null draws complete descriptor vectors with replacement from each inventory's own joint distribution. Each surrogate therefore has an observed combination of segment complexity, loops and contacts. Independent surrogate query and reference sets measure descriptor collisions. The expected rate is `sum_d p(d) * [1 - (1-p(d))^n]`; simulations use 42 queries and 2,000 replicates at each reference size. This generates surrogate descriptors without new drawings and preserves the inventories' observed dependencies. It is an empirical-support baseline, not a geometric model of independently invented marks.

| Empirical distribution | R1 at n=20, exact mean [95% simulation interval] | R3 at n=20, exact mean [95% simulation interval] |
|---|---:|---:|
| Indus | 61.87% [42.86%, 80.95%] | 43.07% [26.19%, 59.52%] |
| Ogham | 88.13% [66.67%, 100%] | 76.00% [54.76%, 92.86%] |
| Tifinagh | 84.46% [64.29%, 97.62%] | 54.97% [35.71%, 73.81%] |

Source: [synthetic-null.json](run-v1/synthetic-null.json), `n=20`, `surrogate_query.exact_mean`, `q025`, `q975`. These columns compare queries drawn from each control's own distribution, so they cannot be read as chance probabilities for Tamil Nadu. The file separately reports `fixed_tamil_query` using the same random references. For example, its Tifinagh R1 expectation rises from 34.01% at n=5 to 61.91% at n=20 and 70.75% at n=42. At n=400 the surrogate R1 means exceed 99.999% in all three inventories, while the fixed-query means approach the observed 71.43%, 57.14% and 76.19% ceilings. Repeated descriptors saturate the available support; they do not create the diversity of a real 400-sign inventory.

## What a full study needs

The coarse rule yields substantial resemblance with both controls, and the strict rule gives Tifinagh more matches than this Indus subset. Annotation disagreement, unequal complexity support, six cell exclusions and modern reference glyphs prevent an archaeological test of transmission. The synthetic null does not learn how frequently previously unseen geometric configurations arise. Dating, object function, positional distributions and ordered composites were outside this shape-only endpoint.

A full study should first acquire the complete 2025 method and comparison tables, then identify whether its percentage counts sign types, variants, composites, occurrences or potsherds. It should register clear source drawings and allowed transformations, including seal reversal, before coding. Two trained human coders should trace the entire Tamil Nadu inventory and a deduplicated Indus list, with adjacency and angle information and source photographs for ambiguous contacts. Several separate script families should supply controls balanced jointly by inventory size and complexity. A geometric generator should be fitted on training controls and checked against held-out drawings; copying observed descriptors alone cannot validate it. Only after that shape endpoint is held fixed should securely dated specimens, positional behavior and composite structure test whether any excess resemblance has historical support.
