# Exploratory extension of Bonta’s sign proposals

This run assigns a preferred working interpretation to all 713 Wells codes in the available inventory. 596 entries are new project assignments; 117 retain Bonta’s mapped proposals. The new assignments include semantic labels, occupational and institutional readings, quantities and grammatical functions. They are conditional hypotheses in a mixed sound/logogram and administrative model, with Sanskrit used as a comparison vocabulary. No entry has an authenticated sound or meaning.

The [searchable visual catalogue](catalogue.html), [complete table](candidates.csv) and [structured catalogue](candidates.json) give each code’s preferred meaning, alternatives, dictionary entry IDs, graphic basis, corpus counts and lexical-search outcomes. The catalogue displays locally rendered drawings and, where available, a Helsinki reference-class image. Those are catalogue drawings, not new artifact photographs. Full inscription contexts and the Lipi drawing witnesses remain under the local-only `data/raw/2026-10-08-bonta-extension/` directory.

## New anchors and how they extend the map

The sixteen new comparisons cover seventeen previously unseeded codes. Bhāra and gaṇa are particularly useful working anchors because their proposed roles can be compared with many recurring contexts. The barley, water, wheel and hall comparisons have much smaller inscription samples. Dictionary attestations establish that the proposed Sanskrit vocabulary exists; archaeological reports help choose useful economic alternatives. Neither source supplies an excavated sign-to-word equivalence.

| Anchor | Wells code(s) | Preferred working meaning | Sanskrit comparison | Complete-sequence occurrences |
|---|---|---|---|---:|
| N01 | W151 | porter service, carried load or transport obligation | bhāra, bhārika, vāha | 57 |
| N02 | W411 | barley/grain allotment | yava, dhānya, śasya | 3 |
| N03 | W450, W452 | water supply or water-related allotment | udaka, jala | 2 |
| N04 | W600 | bounded field or landed holding | kṣetra, koṣṭha | 2 |
| N05 | W319 | tiered access, store or stepped structure | sopāna, koṣṭha, setu | 2 |
| N06 | W825 | woven cloth or textile allotment | vastra, paṭa | 4 |
| N07 | W400 | recorded batch, account total or counted class | gaṇa, gaṇanā, gaṇaka | 192 |
| N08 | W142 | staff-holder or responsible official | daṇḍin, adhikārin | 39 |
| N09 | W130 | cultivator or agricultural service | kṛṣaka, hala | 8 |
| N10 | W121 | livestock keeper or handler of animal products | gopāla, paśu, carma | 1 |
| N11 | W272 | messenger, bird-named person or mobile service | dūta, pakṣin | 3 |
| N12 | W540 | shared portion or distributed allotment | bhāga, saṃyoga | 7 |
| N13 | W645 | together, partnership or joint contribution | saha, saṃyoga | 10 |
| N14 | W370 | seed stock, seed-corn or bulb produce | bīja, phala | 5 |
| N15 | W818 | wheel-related issuer, workshop or emblem | cakra | 1 |
| N16 | W930 | wheel-associated hall or institutional house | śālā, agāra | 1 |

New anchors guide related forms as well as dictionary windows. The porter comparison extends to framed, paired and vessel-headed load carriers. The cultivator comparison extends to human/tool compounds. The field/store comparison extends to bounded and divided rectangles, while the cloth comparison supplies an alternative for cross-hatched panels and leaves. These connections are recorded per sign, including the competing possibility that a modification changes sound or graphic form rather than meaning.

Three interpretations were refined after the expanded dictionary search. W233 becomes a heavy/large asset class under the *ati-bhāra* comparison; W231 becomes a provisioned/collected asset unit under *sam-bhāra*; W204 becomes a shared processed product or share-bearing name element under *sa-bhāga*. These are deliberate post-outcome hypotheses. The dictionary gives several rival completions, and no common residual covers every searched context for these signs.

## Observations and procedure

The full inventory contains 712 non-editorial codes observed on 5,680 faces, plus one additional direct crosswalk code. The clean single-line right-to-left frame has 2,930 faces and 1,859 distinct complete sequences. Context counts use those distinct sequences; whole-corpus counts retain face observations. Object-family support is preserved separately. Signs 000 and 999, used for damage and spacing, are excluded from semantic coverage.

The first pass imports the second edition’s Table 18 through the preserved graphic crosswalk and searches two- and three-sign windows with one unknown slot. It uses 194,059 alphabetic Monier-Williams headwords. Exact matching and a separate tolerant matching layer collapse specified vowel-length, stop and sibilant distinctions. Windows are assumed candidate words; they are not independently identified word boundaries. Exact contexts receive an additional half-point in the ranking, and candidates must contain a vowel and occupy at most six letters. These search choices favour short and common residuals, which remain visible as alternatives.

The October 9 amendment adds full Sanskrit comparison stems in two scenarios: the preferred new anchors and their stated alternatives. Earlier files remain unchanged. Visual reasoning used four sheets of direct graphic classes and five further sheets covering the 215 codes without a direct class mapping. For every code, the map combines that drawing comparison with its position and neighbours. No additional VLM API batch, trained semantic model or calibrated posterior was run.

Priority A marks a recurring code whose proposed role fits its visible form and placement. B marks a plausible but weaker combined case. C marks a rare or predominantly pictorial assignment. These priorities compare hypotheses within the chosen model. They are not percentages of historical correctness. Inherited Bonta proposals remain marked as inherited, with the original values visible.

## Computed outcomes

The preferred-anchor search considered 362 unknown codes. New-anchor windows involved 111 codes in 256 distinct combinations. The alternative-anchor scenario searched the same combinations. There were 164 nonempty full intersections in the preferred scenario and 158 in the alternative scenario; many intersections have only one context or several competing completions. The output records their denominators and candidate counts.

The catalogue contains 44 A, 230 B and 439 C assignments. 342 entries have an explicit connection to a new anchor. All 713 codes have a local font drawing witness; 215 also have a separately authored interpretation from the additional drawing inspection.

## Worked account interpretations

The examples below show how the working map turns short observed strings into tentative account structures. The exact record, object-family IDs, sequence and slot locations are kept in `worked-examples.json` under the local-only run directory. Reading order follows the clean RTL frame. Proposed syllables are retained where a name remains unresolved; logographic labels are glossed in English. Each account explanation is an authored scenario, and several shown structures contain unresolved name components or grammatical relations.

- **Transport obligation** (2733.1, M-209): A carried-load or porter category follows an accounted party or asset category. The recurring final placement makes this a useful transport-service scenario.
- **Closing account category** (1212.1, H-178): The comb-like total/category can follow the jar. A working structure is a named party’s batch or assessment, with the comb supplying the account class.
- **Agricultural worker** (4181.1, -): The person/tool sign supplies a cultivator or agricultural obligation within a name/title or goods account.
- **Textile allotment** (3375.1, M-982): The cross-hatched leaf is read as a cloth lot; a nearby count specifies the allocation. A registered estate/weight class remains an alternative.
- **Heavy load class** (97.1, C-9): The fish grade before the porter/load sign is interpreted as a larger load class. The Sanskrit atibhāra comparison supplies an optional semantic connection.
- **Share-bearing product** (652.2, H-1841): The paired-leaf sign near the opposed-triangle share anchor supplies a shared product or share-bearing name element, under the sabhāga comparison.

## Further resolution

The next useful comparisons are whether the staff-holder and divided-store signs substitute in the same positions, whether leaf/fish grades track numerical quantities, and whether paired carriers systematically accompany larger allocations. Longer strings, securely registered new photographs and artifact-use traces could separate goods, occupation and personal-name readings. The current catalogue keeps those alternatives accessible without waiting for such material.

## Sources

- [A Partial Decipherment of the Indus Valley Script: Proposed Phonetic and Logographic Values for Selected Indus Signs and Readings of Indus Texts (2nd ed.)](https://www.academia.edu/120435855/A_Partial_Decipherment_of_the_Indus_Valley_Script_Proposed_Phonetic_and_Logographic_Values_for_Selected_Indus_Signs_and_Readings_of_Indus_Texts_2nd_ed_). Table 18 values, glyph witnesses, mixed sound/logogram structure and concluding advice on remaining signs and ligatures.
- [Bonta lecture 7](https://www.youtube.com/watch?v=WYu1lqwQ5B0). Previously reviewed anchor and dictionary-intersection procedure; no new viewing claimed in this pass.
- [Monier-Williams Sanskrit-English Dictionary (1899), Cologne digitization](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/webtc2/index.php). Exact headwords, homonyms, definition subentries and full/normalized string searches. Each comparison has entry IDs and print-page columns.
- [Monier-Williams Sanskrit-English Dictionary, University of Hyderabad interface, bh section](https://sanskrit.uohyd.ac.in/SKT/MW/185.html). Internet check of burden/load vocabulary; local Cologne records distinguish bhara, bhāra and bhārika.
- [Monier-Williams page 847 scan](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw0847-yamalacchada.pdf). Search results expose barley compounds; PDF screenshot timed out, so the actual definition check uses the local dictionary entries.
- [The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor](https://arxiv.org/abs/1812.00049). A prior proposal connects miniature tablets and porter/labour rationing. It informs the labour scenario and is not independent verification of a reading.
- [Seal impression](https://www.harappa.com/slide/seal-impression). Primary public photograph and description of an Early Harappan sealing with ladder motifs and a probable bundle-sealing use. No object concordance or new inscription imported.
- [What kinds of things did the Indus people eat?](https://www.harappa.com/answers/what-kinds-things-did-indus-people-eat). Archaeologists’ account of crops and animal resources informs commodity alternatives; it gives no sign-to-word anchor.
- [Ancient Textiles of the Indus Valley Region](https://www.harappa.com/sites/default/files/pdf/Kenoyer2004%20IndusTextilesfinal.pdf). Author paper describes fabric impressions, fibers and production tools; supports considering textile goods, with no claimed correspondence to W825.
- [Dholavira and Its Mysterious Sign Board](https://www.harappa.com/blog/dholavira-and-its-mysterious-sign-board). Public report of excavator Bisht’s reservoir and drainage observations motivates a water-related alternative. This pass read the web account, not the complete excavation report.
- [Lipi corpus and catalogue drawing font](https://github.com/yajnadevam/lipi). Observed signs, object families and U+E000+decimal-code drawings. Upstream proposed decipherments, xlits and translation outputs are excluded.
- [Indus Valley Script Corpus](https://github.com/mayig/indus-valley-script-corpus). Direct many-to-many graphic classes and descriptions. No transitive equivalence is inferred.
- [A Concordance to the Texts in the Indus Script](../../../output/chart_atlas/index.html). Existing chart cells supply an alternative representative class drawing.

## Reproduction and preservation

`analyze.py` produces a new first-pass directory, `extend_search.py` produces a new anchor-scenario directory, and `build_catalogue.py` adds the authored map and review files to that directory. `render_glyphs.py` renders locally retained source drawings. Each creation refuses an existing main run or final catalogue. Source hashes and the selected code versions are recorded. Exact search witnesses, dictionary excerpts and annotated full sequences remain local. The repository contains our code, hypotheses, aggregates, source pointers and the HTML viewer; it does not bundle the unresolved-rights corpus or font drawings.
