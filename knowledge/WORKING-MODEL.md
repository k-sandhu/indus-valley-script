# Working model of the Indus inscriptions

Version 1, 13 October 2026. This is the project's current best account of what the inscriptions are and how they work, stated at full strength. Each part carries a credence, the coordinator's probability that it holds as stated, and links to the measurements it rests on. The evidence record in `experiments/` and the registry is unaffected by this file; the model is revised whenever a test or a new observation moves a credence, and the changelog at the end records each revision. Individual claims that are being tested have their own cards in [conjectures](conjectures/README.md).

The model does not yet include a language. Every attempt to choose one by fitting has failed calibration, and the next language section will be written as credences once units and boundaries are fixed.

## 1. Three kinds of inscribed object, three jobs

The script was used for three different jobs, and most of its apparent oddness comes from mixing their texts in one corpus. Seals carry identity legends: who, or which office, authorises something. Harappa's moulded and incised tablets are standard tokens, made in series, each binding a descriptor to a tier. Marks on pottery and small objects label contents or owners. Credence 0.6.

The evidence is the different behaviour of the three groups. Long seal texts are almost all unique: none of 445 seals with six or more signs shares its text ([seal-text identity](../experiments/2026-10-12-seal-text-identity/REPORT.md)). Tablet texts recur in large series and stay with one image class within a genre ([structure-first step 2](../experiments/2026-10-12-structure-first/step2-image-text/REPORT.md)). The three commonest texts in the corpus are a group of two, three or four tall strokes followed by sign 700: 93, 127 and 111 faces, all but five on Harappa tablets. Whole multi-face bundles are copied as units, and the W700 face takes several tall-stroke values against a fixed descriptor face ([two approaches, administrative](../experiments/2026-10-11-two-approaches/administrative/REPORT.md)).

## 2. A seal legend is a name with a title

A seal legend has two parts. The opening part, made of many different signs, individualises the holder; it is a personal or family name. The closing part names a title or office from a small shared stock, often ending in the jar sign 740 or in 400. Credence 0.45.

Texts begin with many different signs and end with few (edge asymmetry +0.260 against a shuffle range of ±0.018), and 35.2% of texts end in 740 ([step 6](../experiments/2026-10-12-structure-first/step6-language/REPORT.md)). Many signs that look "closing" stand directly before a final 740 or 400, so the closing unit is often a two-sign formula ([anchor-expansion review](../experiments/2026-10-12-anchor-expansion/claude-review.md)). Catalogued line divisions fall between recurring units, which is how a scribe would break a name from a title ([step 3](../experiments/2026-10-12-structure-first/step3-segmentation/REPORT.md)). Larger seal faces carry longer legends, 1.16 more positions per doubling of area ([sign context and seals](../experiments/2026-10-06-sign-context-and-seals/REPORT.md)).

The first test of a full reading built on this structure failed. [Shot B](../experiments/2026-10-12-conjecture-shots/shot-b-reading/REPORT.md) assigned the 118 commonest signs to classes such as household, name element and office and predicted where seals carrying them were found and how large they were; the map did no better than rearrangements of its own labels on either half (−0.44 and +0.88 standard deviations). The test detects only large effects and leaves the two-part structure itself untested, but it gives no support to the specific glosses, so the credence here drops from 0.5 to 0.45.

### 2a. A legend closing in sign 820 marks an upper grade

Seals whose legend closes with sign 820, a sign that usually opens legends, are cut larger: across both halves the ten such seals average nearly twice the face area of seals of the same type, site class and length, and on the photographs 820 sits at the closing end at normal size and spacing. Credence 0.15. [Shot A](../experiments/2026-10-12-conjecture-shots/shot-a-rank/REPORT.md) froze a four-sign version of this claim and it passed on the confirmation half (p = 0.021), but the [adversarial review](../experiments/2026-10-12-conjecture-shots/review/REVIEW.md) found the pass carried by three very large 820 seals, one of them silver, and the narrowing to 820 came after the outcome. Card [C-0001](conjectures/C-0001-rank-written-twice.md).

## 3. Short recurring legends are titles of offices that existed in many cities

The 65 seal texts that recur, on 174 seals, are mostly short, and 41 of them occur at more than one site. At Mohenjo-daro they are placed as freely as chance would place them. They are titles or role formulae held by several people, not names shared by relatives. Credence 0.55.

Identical texts of four or more signs exceed a bigram model of the corpus three- to fivefold, so they are reused as wholes rather than recomposed by chance. Some duplicates at smaller sites stay local, about 15% of shared texts and compatible up to 25%; those may be family names or local offices ([seal-text identity](../experiments/2026-10-12-seal-text-identity/REPORT.md)).

## 4. Offices worked across cities

Seals were used to seal goods and documents that travelled between cities, and the sealing was often made far from where the seal was found. Most sealings that carry a seal text match seals from other cities: 13 of 16 matching sealings, carrying 4 of 6 texts. Ten Lothal sealings carry the four-sign text of Mohenjo-daro fragment M-895. Either the same office kept holders in both cities, or one holder's goods moved between them. Credence 0.6 for the first reading over the second.

The Lothal sealings show an elephant and M-895 is recorded with a unicorn. If both records are right, the legend names an office that was not tied to one emblem. The [plate check](../experiments/2026-10-13-plate-checks/README.md) of 13 October found the same four signs in the same order on the sealings and on M-895, impressed by a different seal: the face is as wide (23.4 against 23.3 mm) but the signs are spaced and cut differently. The animals remain to be confirmed by a specialist; two AI readers agree on an elephant on the sealings and disagree on M-895. Conjecture [C-0004](conjectures/C-0004-m895-office-text.md).

## 5. The field animal is an affiliation, and the unicorn affiliation was everywhere

The animal on a seal marks the holder's affiliation: a clan, guild or institution. The unicorn affiliation was present in every city and accounts for most seals, 77% of known square-seal motifs in this export. The rarer animals mark smaller or more local affiliations. Credence 0.45.

Seals with identical texts share their animal mainly when it is the unicorn: 88 of 89 concordant pairs are unicorn pairs, and 1 of 42 pairs with another animal matches ([seal-text identity](../experiments/2026-10-12-seal-text-identity/REPORT.md)). Unicorn seals are no more uniform in size than others (CV difference 0.013, p = 0.65), and seal texts do not predict unicorn against other animals ([sign context and seals](../experiments/2026-10-06-sign-context-and-seals/REPORT.md)), so the affiliation is not written in the legend and was not cut to one template. Conjecture [C-0003](conjectures/C-0003-unicorn-affiliation.md) holds the predictions.

## 6. Strokes count tiers on tokens and are frozen parts of names on seals

On tablets, tall strokes before sign 700 count a tier or quantity class: two, three or four of a standard unit. On seals, most stroke groups are fixed parts of names or titles, as Parpola read some stroke-and-fish groups as asterism names, rather than counts of goods. Credence 0.5.

Stroke values are far more fixed to the neighbouring sign than Ur III administrative counts are to their commodity: 3.61 distinct values per item against 4.53–5.15, and code 520 follows three tall strokes in 38 of 41 cases ([step 4](../experiments/2026-10-12-structure-first/step4-numerals/REPORT.md)). That fixity is what names and titles produce. The tablet W700 face is the exception, with several values against one descriptor, which is what a tier produces. Conjecture [C-0005](conjectures/C-0005-tablet-tiers.md) holds the predictions.

## 7. Signs are built from bases and added marks, and the bases carry meaning

Signs that share a graphic base share contextual behaviour, so bases are meaningful units and added marks modify them. Credence 0.55. Graphic families improve held-out prediction of rare signs beyond random groupings, though the Wells order already captures most of it ([step 1](../experiments/2026-10-12-structure-first/step1-signs/REPORT.md)). The modifier prediction failed, so the added marks do not act as one consistent system.

## 8. What the model says about decipherment claims

A key or meaning map that fits the corpus says little by itself: random consonant strings pass a lexical readability test 92% to 100% of the time, and fitted keys transfer equally under unrelated languages ([published-claim tests](../experiments/2026-10-12-published-claim-tests/README.md)). A correct key stands far above rearrangements of itself; on synthetic Indus-shaped corpora, 27 to 72 standard deviations. Any reading this model eventually supports must pass that [calibration](directions/key-calibration-2026-10-12.md) or predict something outside the texts.

## What would change the model most

- Complete, well-described data, which is now the project's first priority: object identities joined across catalogues, every face photographed, dimensions, findspots and dates ([DATA.md](DATA.md)). Every section above is limited by the 28.8% of objects with all three dimensions and the 55.8% with a period label.
- A specialist reading of M-895's field animal and of the trunk-and-tusk element on the Lothal sealings (section 4).
- Photographs of the seals ending in 820 that the project does not hold (M-1701, M-1761 and the Dholavira seal), and seals ending in 820 in material none of these analyses has seen, tested with a rank or leave-one-out rule (section 2a).
- One excavated deposit with both seals and sealings, where the same issuer should appear on both (sections 2 and 4).
- The expanded concordance planned by the Iravatham Mahadevan chair at the Roja Muthiah Research Library, which would supply texts none of these analyses has seen.

## Changelog

- 12 October 2026, version 0: written from the October 6–12 results before the two conjecture shots reported.
- 13 October 2026, version 1: Shot B's reading failed its frozen test (section 2 lowered to 0.45); Shot A's closing-sign result added as section 2a at 0.15 after review; the plate check moved section 4 to 0.6; data completeness added at the head of the list of what would change the model. The reversed-locality pattern seen after Shot B's outcome is left out: it reverses on the other half.

