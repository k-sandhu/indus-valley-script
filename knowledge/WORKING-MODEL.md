# Working model of the Indus inscriptions

Version 2, 20 October 2026. This is our current best account of what the inscriptions are and how they work, stated at full strength. Each part carries a credence, our probability that it holds as stated, and links to the measurements it rests on. We revise the model whenever a test or a new observation moves a credence, and the changelog at the end records each revision; the evidence record in `experiments/` and the registry is unaffected by this file. Claims under active test have their own cards in [conjectures](conjectures/README.md).

Signs are named by their numbers in the Wells sign list: 740 is the jar sign and 700 a U-shaped sign, also written W700. A face is one inscribed side of an object. A seal legend is the text cut on a seal; a sealing is clay impressed with a seal, so it carries that seal's text and animal. Object numbers such as M-895 are those of the Corpus of Indus Seals and Inscriptions (CISI). A shot is a single frozen test: we divide the corpus into a discovery half, explored freely, and a confirmation half, read once after the predictions are frozen.

The model does not yet include a language. Every attempt to choose one by fitting it to the texts has failed calibration, the test described in section 8. We will write a language section once the units of the script and the boundaries between them are fixed.

## 1. Three kinds of inscribed object, three jobs

The script was used for three different jobs, and most of its apparent oddness comes from mixing their texts in one corpus. Seals carry identity legends: who, or which office, authorises something. Harappa's moulded and incised tablets are standard tokens made in series: one face, the descriptor, names what the token is for, and another states its tier, a level or quantity class. Marks on pottery and small objects label contents or owners. Credence 0.6.

The evidence is the different behaviour of the three groups. Long seal texts are almost all unique: none of 445 seals with six or more signs shares its text ([seal-text identity](../experiments/2026-10-12-seal-text-identity/REPORT.md)). Tablet texts recur in large series, and within each kind of tablet a recurring text stays with one class of image ([structure-first step 2](../experiments/2026-10-12-structure-first/step2-image-text/REPORT.md)). The three commonest texts in the corpus are a group of two, three or four tall strokes followed by sign 700, on 93, 127 and 111 faces, all but five of them on Harappa tablets. The texts on all faces of a tablet are copied together as a unit, and opposite the same descriptor face the W700 face carries different numbers of tall strokes ([two approaches, administrative](../experiments/2026-10-11-two-approaches/administrative/REPORT.md)).

## 2. A seal legend is a name with a title

A seal legend has two parts. The opening part, made of many different signs, identifies the individual holder; it is a personal or family name. The closing part names a title or office from a small shared stock, often ending in the jar sign 740 or in the comb sign 400. Credence 0.45.

Texts begin with many different signs and end with few. The entropy, or variety, of first signs minus that of last signs is +0.260, against a range of ±0.018 when signs are shuffled within each text, and 35.2% of texts end in 740 ([step 6](../experiments/2026-10-12-structure-first/step6-language/REPORT.md)). Many signs that look like closing signs stand directly before a final 740 or 400, so the closing unit is often a two-sign formula ([anchor-expansion review](../experiments/2026-10-12-anchor-expansion/claude-review.md)). Catalogued line divisions fall between recurring units, where a scribe would break a name from a title ([step 3](../experiments/2026-10-12-structure-first/step3-segmentation/REPORT.md)). Larger seal faces carry longer legends, 1.16 more sign positions for each doubling of face area ([sign context and seals](../experiments/2026-10-06-sign-context-and-seals/REPORT.md)).

The first shot at a full reading built on this structure failed. [Shot B](../experiments/2026-10-12-conjecture-shots/shot-b-reading/REPORT.md) assigned the 118 commonest signs to classes such as household, name element and office, and predicted where seals carrying them were found and how large they were. On both halves the map did no better than rearrangements of its own labels among the signs: −0.44 standard deviations from their mean on the confirmation half, +0.88 on the discovery half. The test detects only large effects and leaves the two-part structure itself untested, but it gives no support to the proposed sign meanings, so the credence here drops from 0.5 to 0.45.

### 2a. A legend closing in sign 820 marks an upper grade

Seals whose legend closes with sign 820, a sign that usually opens legends, are cut larger: across both halves the ten such seals average nearly twice the face area of seals of the same type, length and site class (six named sites, the rest pooled), and on the photographs 820 sits at the closing end at normal size and spacing. Credence 0.15.

[Shot A](../experiments/2026-10-12-conjecture-shots/shot-a-rank/REPORT.md) froze a version of this claim with four closing signs, and it passed on the confirmation half (p = 0.021). The [adversarial review](../experiments/2026-10-12-conjecture-shots/review/REVIEW.md) found the pass carried by three very large seals ending in 820, one of them silver, and we narrowed the claim to 820 only after seeing that outcome. Card [C-0001](conjectures/C-0001-rank-written-twice.md).

## 3. Short recurring legends are titles of offices that existed in many cities

The 65 seal texts that recur, on 174 seals, are mostly short, and 41 of them occur at more than one site. Copies of a recurring text at Mohenjo-daro are found together in that city no more often than chance predicts. These texts are titles or role formulae held by several people, not names shared by relatives. Credence 0.55.

Identical texts of four or more signs occur three to five times as often as a bigram model of the corpus predicts; such a model composes texts from the frequencies of adjacent sign pairs. These texts are therefore reused as wholes, not recomposed by chance. Some duplicates at smaller sites stay local: about 15% of shared texts by our estimate, and up to 25% is compatible with the data. Those may be family names or local offices ([seal-text identity](../experiments/2026-10-12-seal-text-identity/REPORT.md)).

## 4. Offices worked across cities

Seals were used to seal goods and documents that travelled between cities, and a sealing was often made far from where the matching seal was found. Most sealings that carry a seal text match seals from other cities: 13 of the 16 matching sealings, carrying 4 of the 6 texts involved. Ten Lothal sealings carry the four-sign text of the Mohenjo-daro seal fragment M-895. Either the same office had holders in both cities, or one holder's goods moved between them. Credence 0.6 for the first reading over the second.

The Lothal sealings show an elephant and M-895 is recorded with a unicorn. If both records are right, the legend names an office that was not tied to one emblem. In the [plate check](../experiments/2026-10-13-plate-checks/README.md) of 13 October, two AI readers of the CISI photographs found the same four signs in the same order on the sealings and on M-895. The sealings were impressed by a different seal, whose face is as wide (23.4 against 23.3 mm) but whose signs are spaced and cut differently. The readers agree on an elephant on the sealings and disagree on M-895, whose animal still needs a specialist. Conjecture [C-0004](conjectures/C-0004-m895-office-text.md).

## 5. The field animal is an affiliation, and the unicorn affiliation was everywhere

The animal in a seal's picture field marks the holder's affiliation: a clan, guild or institution. The unicorn affiliation was present in every city and accounts for most seals, 77% of square seals with a recorded animal in our corpus. The rarer animals mark smaller or more local affiliations. Credence 0.45.

Seals with identical texts share their animal mainly when it is the unicorn: of the 89 pairs of identical-text seals that share an animal, 88 are unicorn pairs, and of 42 pairs involving another animal, 1 shares it ([seal-text identity](../experiments/2026-10-12-seal-text-identity/REPORT.md)). Unicorn seals are no more uniform in size than others (coefficient of variation differs by 0.013, p = 0.65), and a seal's text does not predict whether its animal is a unicorn ([sign context and seals](../experiments/2026-10-06-sign-context-and-seals/REPORT.md)). So the affiliation is not written in the legend, and unicorn seals were not cut to one template. Conjecture [C-0003](conjectures/C-0003-unicorn-affiliation.md) holds the predictions.

## 6. Strokes count tiers on tokens and are frozen parts of names on seals

On tablets, tall strokes before sign 700 count a tier or quantity class: two, three or four of a standard unit. On seals, most stroke groups are fixed parts of names or titles and do not count goods; Parpola read some groups of strokes and a fish sign in this way, as names of asterisms (star groups). Credence 0.5.

The number of strokes is far more fixed by the sign that follows than a count in the Sumerian Ur III administrative records is fixed by its commodity. A sign that follows strokes takes 3.61 distinct stroke values on average, against 4.53–5.15 in matched Ur III samples, and sign 520 follows three tall strokes in 38 of 41 cases ([step 4](../experiments/2026-10-12-structure-first/step4-numerals/REPORT.md)). Names and titles produce that fixity. The tablet face with sign 700 is the exception: opposite one descriptor face it takes several stroke values, which is what a tier produces. Conjecture [C-0005](conjectures/C-0005-tablet-tiers.md) holds the predictions.

## 7. Signs are built from bases and added marks, and the bases carry meaning

Many signs combine a base shape with added marks such as inner strokes or an enclosure. Signs that share a base behave alike in context, so bases are meaningful units and the added marks modify them. Credence 0.55.

Grouping signs into families by their base improves the prediction of rare signs in texts held out from fitting, beyond random groupings of the same sizes, although the Wells numbering, which already places similar shapes together, captures most of that gain ([step 1](../experiments/2026-10-12-structure-first/step1-signs/REPORT.md)). Grouping signs by their added marks did not improve prediction, so the marks do not act as one consistent system.

## 8. What the model says about decipherment claims

A key (sound values for signs) or a meaning map that fits the corpus says little by itself. Random consonant strings pass a dictionary-based readability test 92% to 100% of the time, and keys fitted to one half of the corpus fit the other half equally well under unrelated languages ([published-claim tests](../experiments/2026-10-12-published-claim-tests/README.md)). A correct key stands far above rearrangements of its own values: on synthetic corpora shaped like the Indus texts, by 27 to 72 standard deviations. Any reading this model eventually supports must pass that [calibration](directions/key-calibration-2026-10-12.md) or predict something outside the texts.

## Fish labels and four-unit tablets

Fish combinations form an ordered designation field within seal legends. Credence 0.45. The frozen order predicts 43 independent text groups, with eight opposing it and two ties. The numeral result depends heavily on two-stroke constructions and does not decide between fixed expressions and standardized quantities. The narrow asterism-coverage model failed its registered rules, leaving credence 0.05. [Fish study](../experiments/2026-10-20-fish-context/REPORT.md), [C-0007](conjectures/C-0007-fish-compound-designations.md), [C-0008](conjectures/C-0008-fish-numerals-asterism-coverage.md).

H-912 B belongs to a standard four-unit series indexed to the Fish category. Credence 0.40. Four catalogue entries preserve three four–V–fish constructions and one four–fish–V construction, with fish-bearing texts on their other faces. The fixed-four category model is a post-outcome conjecture; the confirmation examples supply only one independent text component and cannot distinguish contents, account or recipient roles. The literal four-vessel-units-of-fish reading remains at 0.35. The excavation source describes a broad collection spanning two squares and three months, with no direct container or fish-lot association. [H-912 report](../experiments/2026-10-20-h912-tablet-series/REPORT.md), [C-0012](conjectures/C-0012-fish-category-four-unit-records.md), [C-0009](conjectures/C-0009-h912-vessels-of-fish.md).

A securely new example of the exact short-stroke, plain-V and plain-fish construction with another numeral defeats the fixed-four prediction. A registered tablet–container or tablet–allotment relation must decide its function. Four physical vessels containing fish require a counted membership and contents test; four measures require an independently calibrated unit. The long-stroke forty-litre literature supplies no short-stroke capacity calibration here.

The parallel source audit distinguishes forty pre-firing vessel stamps from six clay tags and one jar stopper. Two stamps have individual locus, lot and item links; contents and attachment evidence remain missing. The parallel graphic-variation model loses 0.01584 bits per target when city is added across 306 independent text groups, with a 95% interval from −0.04107 to +0.00610. This result leaves a common written convention compatible with several spoken-language and institutional mechanisms. [Manufacture and deposition](../experiments/2026-10-20-archaeological-setting/REPORT.md), [graphic variation](../experiments/2026-10-20-script-variation/REPORT.md).

## What would change the model most

- Complete, well-described data, now our first priority: object identities joined across catalogues, every face photographed, dimensions, findspots and dates ([DATA.md](DATA.md)). Every section above is limited because only 28.8% of objects have all three dimensions and 55.8% have a period label.
- A specialist reading of the animal on M-895 and of the trunk-and-tusk element on the Lothal sealings (section 4).
- Photographs of the seals ending in 820 that we do not hold (M-1701, M-1761 and the Dholavira seal), and seals ending in 820 in material none of these analyses has seen, tested with a rule based on ranks or on leaving out one seal at a time (section 2a).
- One excavated deposit with both seals and sealings, where the same issuer should appear on both (sections 2 and 4).
- The expanded concordance planned by the Iravatham Mahadevan chair at the Roja Muthiah Research Library, which would supply texts none of these analyses has seen.

## Changelog

- 12 October 2026, version 0: written from the October 6–12 results before the two conjecture shots reported.
- 13 October 2026, version 1: Shot B's reading failed its frozen test (section 2 lowered to 0.45); Shot A's closing-sign result added as section 2a at 0.15 after review; the plate check moved section 4 to 0.6; data completeness added at the head of the list of what would change the model. The reversed-locality pattern seen after Shot B's outcome is left out: it reverses on the other half.
- 20 October 2026, version 2: added the ordered fish field, failed narrow asterism test, standard four-unit Fish conjecture and source-qualified archaeological and regional comparisons. Frozen evaluations retain historical-exposure and author-verification status.
