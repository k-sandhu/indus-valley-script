# Structure before meaning: diagnosis and plan

We wrote this diagnosis on 12 October 2026 after reading the 152 entries of the experiment registry (the project's record of every study and its outcome), the retrospectives, the direction memos and the studies begun on 11–12 October. The [interactive research map](https://claude.ai/artifact/PN2ShkmWxYKnMS5XV77dHD) shows every investigated path by line of thought and evidence type; its generator is kept in [the program directory](../../experiments/2026-10-12-structure-first/map/). The six-step program that follows from the diagnosis is recorded in [experiments/2026-10-12-structure-first](../../experiments/2026-10-12-structure-first/README.md).

The corpus figures below are descriptive counts made on 12 October from two local files derived from the Lipi transcription. The clean single-line set (`data/normalized/lipi_clean_rtl_singleline.jsonl`) keeps one record per distinct text in reading order and excludes texts with unknown signs; the full face export (`data/normalized/lipi_observed_faces.jsonl`) holds every face record of the Lipi export. These are exploratory counts, not results fixed in advance by a protocol.

## Why the work has not produced a substantive result

The goal was set where desk research cannot reach it. Our working definition of a substantive result has been a reading confirmed by an independent physical anchor: a counted collection, an attachment trace or a bilingual object. Those need museum access, new photography or excavation. A keyword search shows that 80 of the 152 registry entries can be retried only with new photographs, specimens, registrations, dated contexts or similar observations. Studies end with a protocol for data the project cannot obtain, and the next working session opens a different topic. Results that the corpus in hand can support were never set as targets: a tested sign list, a segmentation into recurring units, a description of how the numerals behave and a function for one class of texts.

Most measurements cannot separate the hypotheses. Restoration accuracy (how often a model guesses a deliberately hidden sign), Markov gain (how much better the previous sign predicts the next than sign frequencies alone) and the advantage of real over shuffled sign order are high for every system tried: the Indus script (IVS), an invented office-routing code (0.631-bit gain) and all eleven testable Sumerian, Akkadian, Egyptian and Linear B cohorts. Registry entry ROOT-12 recorded this on 1 October. Studies of sign sequences still grew to 47 entries, and restoration rose from 33.8% to 41.2% top-one (correct sign ranked first) without changing what we believe about the script. Dictionary fitting has the same defect: if each face is read as one word, words that repeat units where the face repeats signs cover 91–97% of IVS faces in all four Bronze Age languages. A test is worth running when the hypotheses in play predict different values for it.

The sign list was taken as given. The corpus codes signs by the Wells numbering used in ICIT, the Interactive Corpus of Indus Texts. In the clean set (1,859 distinct texts, 8,535 signs) 577 codes occur; 214 of them (37%) occur once and 303 (53%) at most twice, while the 30 commonest codes carry 58% of all signs. Much of this long tail consists of compounds: a frequent base such as the jar, fish, human figure or U-shape with added strokes, hatching or an attached object. Counting each compound as an unrelated symbol fragments the evidence. Restoration fails on rare codes, the groups of signs that replace one another in identical contexts (substitution families) depend on the classes of the sign chart, and our catalogue of proposed meanings gives separate meanings to variants of one sign. Mahadevan's list has 417 signs, Parpola's about 386 and the coding used here about 700. No analysis measured how the results depend on that choice.

Meanings were assigned before structure. We constructed 596 new meanings to cover all 713 codes, pruned them under review to seven families on nine codes, and began extending them to the 567 unreviewed codes. The criterion for accepting a meaning (a dictionary sense, a pictorial resemblance and compatible positions) admits many candidates per sign, so each sign given a meaning (an anchor) adds freedom faster than evidence. The language was inherited from the sources, the Lipi maintainer's Sanskrit readings and Bonta's Indo-Aryan proposal. It was never compared with Proto-Dravidian, Munda or an unknown language under matched freedom, that is, with the same number of free choices for each. The Rigveda, the earliest attested Sanskrit, was composed roughly 1500–1200 BCE, after the Mature Harappan period of about 2600–1900 BCE. Decipherments that succeeded went from the sign list to numerals, then to segmentation and inflection (Kober's triplets for Linear B), then to the content of texts from their context (Proskouriakoff's dates and events on Maya monuments), with sound values last, from names or bilinguals.

The most informative material was filtered out. The main population is complete single-line texts of at least three signs read right to left. Only 2 of 69 Harappa tablets, sealings and stamped vessels, and 2 of 355 rows in the catalogue's numerical class, pass that filter. The local export holds 190 Mohenjo-daro copper tablets carrying 77 distinct texts. The 12 tablets with a hare carry one text, the 10 with an anthropomorphic figure carry one text, and the elephant tablets carry two texts that differ by a single stroke. On these objects the image predicts the text. The 2 October readiness review named the graph linking copper-tablet images to texts as the useful next task; no study took it up. Every main analysis also left out 2,060 bas-relief and incised tablet faces, the line breaks of 118 multi-line faces and the faces found outside South Asia.

Rigor went where it was cheap. Of the registry entries, 33 work only on invented or simulated data: eleven exact enumerations of chance models (null laws), twelve mapping studies on artificial record systems, simulations of khipu accounts and of measurement acquisition, a stamp-contact model and a societal renewal model. Of the 46 entries that measure real Indus material, 29 are variants of two statistics first computed on 1 October. One maintainer's transcription supplies almost every sequence, and its sign list, segmentation and reading-order conventions were adopted without a test.

Breadth replaced accumulation. Since 6 October the project has opened about twenty lines of work. Five of the ten research programmes started on 11–12 October address questions outside the script. Each carries a protocol, reviews, a retrospective and packaging, and ends with next tests that later sessions rarely run. The Lothal attachment test and the Harappa short-record table recommended on 2 October each received one limited pass.

Reviews check for defects without asking what a result decides. Adversarial review adds controls and caveats until a claim is safe, but does not ask which hypothesis a result moves, or by how much. A short hypothesis ledger fixes this. Candidate descriptions of the script include a logo-syllabic language, names and titles in a language, a nonlinguistic administrative code and an emblem or identity system. Each planned test should state what each candidate predicts, and a test on which they all agree should not run.

## Directions not yet investigated

| Direction | Status in the record | Data in hand |
|---|---|---|
| Base-plus-modifier sign coding and a tested allograph policy | Absent; one fish-stroke image audit | 1979 chart, Mayig feature schema, local Lipi glyph font, CISI 1 |
| Line breaks and face splits as segment-boundary evidence | Absent; multi-line texts filtered out | 118 multi-line faces, Harappa tablet frame |
| Recurrent-unit segmentation and Kober-style alternation | Absent | Corpus; Ur III seal legends and lines with word boundaries |
| Copper and moulded tablet image–text concordance | Proposed 2 October, not run | 190 copper objects, 2,060 tablet faces, CISI 1 |
| Seal animal and text-segment association | One whole-text test | Image field on about 2,500 faces |
| Counting versus lexical behaviour of stroke numerals | Absent | Corpus; Ur III accounts, Linear B sample |
| Blind rehearsal on a readable script at Indus scale | Absent | Sumerian, Akkadian, Egyptian and Linear B records |
| Proto-Elamite structure recovery | Proposed, not run | Public CDLI editions |
| Foreign finds as a natural experiment | Being tested in the concurrent [published-claim tests](../../experiments/2026-10-12-published-claim-tests/PROTOCOL.md) | 42 faces |
| Meluhhan names and loanwords in cuneiform; substrate vocabulary in early Indo-Aryan | Absent beyond a bilingual-object search | Published literature |
| Structural language comparison with matched freedom | Proposed in the community memo, not run | Requires segments |
| Early Harappan marks, pottery graffiti as a genre, carver hands | Absent or touched once | HARP publications, export, CISI 1 |

In the table, an allograph is a graphic variant of one sign, and Kober-style alternation is a stem that recurs with different endings, the pattern Kober used on Linear B.

## The program

The six steps use material already held. Steps 2–5 can run in parallel once step 1 has fixed how signs are represented. Each step states in advance what result would change the next action.

1. Fix the sign list. Code every attested sign as a base plus modifiers. Build inventories at the level of Wells's codes, of the Mahadevan and Parpola sign lists, and of bases; recompute the frequency profile, held-out probability and substitution families under each; and test whether a model that shares statistics across a base predicts the original codes better than one that does not, and better than random groupings of the same sizes. A refinement made before any data were examined replaces the map's draft rule ("merged signs never contrast in otherwise identical texts"). Without meanings, substitution in an identical context cannot distinguish allographs from different signs that fill the same slot, so the decision uses held-out prediction and random-grouping controls instead.
2. Read copper and moulded tablets as image–text pairs. Build the graph linking images to texts, identify sign groups fixed within an image class, test whether a text's image can be predicted from other text types with the same image, and test whether segments specific to copper tablets recur on seals showing the matching animal.
3. Segment, then look for inflection. Score segmenters against line breaks; count alternations of stem and ending on the segments and compare with Sumerian seal legends and lines of matched size.
4. Find out whether the strokes count things. For each sign that follows a stroke group, tabulate the stroke values it takes, and compare with commodity counts in Ur III accounts and Linear B.
5. Rehearse on scripts we can read. Run the step 3 and 4 procedures on Sumerian, Egyptian and Linear B material cut to Indus scale, with word boundaries and values hidden, and score what they recover.
6. Compare languages only on structure. With segments in hand, compare the measured profile with the typological predictions for each candidate language family under matched freedom.

Until these steps report, pause further restoration models on the same hidden positions, new enumerations of null laws, new artificial mapping systems, more Sanskrit anchors before steps 1–3, new topics outside the script and further packaging passes.

## Results of the program

The six steps ran the same day; the [integrated report](../../experiments/2026-10-12-structure-first/REPORT.md) gives the measurements and the [review responses](../../experiments/2026-10-12-structure-first/review/RESPONSE.md) the corrections. In brief:

- Grouping signs into graphic families improves prediction of rare signs. Random contiguous cuts of the Wells order recover about three quarters of that gain, and the published Parpola-level and Mahadevan-level groupings predict unseen signs better.
- Harappa tablet texts pair with their images within each genre. Sign groups specific to copper tablets appear on seals showing the same animal no more often than expected; the test could have detected a fivefold excess.
- Catalogued line divisions fall between recurring units.
- Stroke values are more tied to neighbouring signs than Ur III counts are.
- At Indus scale, unsupervised segmentation and Kober-style alternation do not discriminate even on readable scripts.
- Indus texts end in a small class of signs, a descriptive property that leaves every candidate language tied.

Each of the four descriptions in the hypothesis ledger failed at least one prediction fixed in advance. The report's next steps replace the plan's items where the results changed them, including a comparison of seals and sealings from within one deposit, segmentation scored against line divisions, and a corpus of seal legends in head-final languages for the structural comparison.
