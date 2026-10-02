# Independent review of the South Indian source branch

The portal calculations reproduce correctly. The independent check passed 317 comparisons, including all 194 derived compound-property rows and 6,330 comparisons between each form's site count and its habitation, ware and depth margins. The three printed concordance checks also reproduce the reported component counts. Reading 4.19C identified an additional terminal-label difference: the printed component is 5.0, while the API's internal code 390 maps to government variant 5.7. The current report and retrospective now record both differences for that form.

[The review record](independent-review.json) preserves the checks, file hashes, source coordinates and three short comparisons. This review used the existing local sources and reconstructed the counts without importing the branch's counting functions. It acquired no additional corpus and changed no frozen endpoint.

## Counts and data units

The 42 family responses contain 2,110 forms: 42 base forms, 546 variants and 1,522 composites. Their site margins sum to 9,345 reported occurrences. The separate sites route totals 9,349 across 53 labels. The four extra one-occurrence cells have the same literal keys and sites recorded in [aggregate-v1](aggregate-v1/results.json). Family `totals` combine base occurrences with counts of variant and composite forms; the report keeps these units separate.

The sixteen plain stroke classes account for 480 reported occurrences. Their visible-line frequency table and orientation totals reproduce exactly; including the three decorated variants gives 501. The class descriptions were checked on volume I printed p.387, PDF p.426, and their photographic representatives on Plate 5.136, printed p.684, PDF p.723.

The concordance response contains 209 compound keys. An independently parsed client crosswalk identifies the same sixteen plain-stroke component codes. Scanning the component arrays recovers 194 explicit-stroke forms, 142 simple pairs with 413 reported occurrences, 491 resolved occurrences overall, 13 forms with separated stroke blocks and 40 with several other components. The 15 opaque forms account for 17 further reported occurrences. All 194 property rows agree with [stroke-membership-v2](stroke-membership-v2/results.json).

## Printed comparisons

The coordinates below are one-based PDF pages. The registrations retain the catalogue's spelling, including `KDL` in the first row and `KLD` in the second.

| Form and printed registration | Volume II location | Printed components | API components |
|---|---|---|---|
| 1.6C, KDL-G-0042 | Printed 707, PDF 32, row 6 | 39.0 / 1.0 / 39.0 | 39 / 1 / 39 |
| 39.13C, KLD-G-1329 | Printed 982, PDF 307, row 13 | 39.4 / 39.4 | 39.4 / 39.4 |
| 4.19C, SGI(PPT)-G-0137 | Printed 779, PDF 104, row 120 | 3.0 / 4.0 / 39.0 / 4.0 / 39.0 / 5.0 | 3 / 4 / 39 / 4 / 5.7 |

The first two comparisons agree after normalizing the printed `.0` suffix for base classes. For 4.19C, the API omits the second printed stroke component and changes the terminal component label. This leaves six printed components and two stroke blocks against five components and one block in the API.

One wording refinement would help readers: define a **stroke block** as consecutive stroke components in the normalized array. In 39.13C, one such block contains two separately displayed groups of three strokes. The array calculation therefore describes component adjacency, while the source drawing preserves their spatial arrangement.

## Source joins and interpretation

The family rows contain only a sign key and separate margins. Their cells contain `key` and `value`; they supply no individual registration, joint site-depth-ware row, vessel capacity, measured mass, contents count, calendar age or dating-sample key. The Keeladi filter confirms this structure even after selecting one site and graphic class: five occurrences are distributed separately over ware and depth. The three printed registrations provide specific targets for a later specimen join.

The report keeps the numeral question tied to an independently measured feature on an identified object, and treats historical connection as a question requiring dated intermediate or contact evidence. Its 2026 date is the publication date shown in both books. I found no claim that these API records establish numeral meanings or an Indus-to-South-India chronology.

## Source integrity and review history

The acquired volumes have 740 and 712 PDF pages. Their hashes and the two preview/brochure page counts agree with [source-witnesses.json](source-witnesses.json). Fresh renders of volume II pages 32, 104 and 307 at a scale of two have exactly the same RGB pixels as the saved images inspected during this review.

The observable sequence was to read the protocols and endpoints, reconstruct the arithmetic and namespace membership, inspect the selected source pages, and report the additional 4.19C label disagreement to the parent agent. The parent amended current prose while preserving the original analysis files. These three purposefully selected comparisons establish specific agreements and disagreements; they supply no catalogue-wide error rate. The review used the same acquired publications as the source branch, with its questions known.
