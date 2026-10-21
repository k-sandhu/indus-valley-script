# Did Proto-Dravidian *mīn mean "star"? Report of DRAVIDIAN-ROOT-MEANINGS-2026-10-21

The frozen test passes, narrowly. On the dated tree of Kolipakam and colleagues, the meaning "star" in the *Dravidian Etymological Dictionary* (DEDR) entry that holds Tamil *mīṉ* "star" reaches the root of the family with a maximum-likelihood probability of 0.524 and the North Dravidian node with 0.681, and the meanings Parpola's readings need reach the root far more often than meanings drawn from the same entries that nobody proposed (7 against a reference mean of 0.54, p = 0.0001). The kill condition fails because Kurukh and Malto, in the north, and Gondi, in central India, have star words in the same entry. Three results temper the pass. Parsimony places "star" absent at the root. A star word homophonous with *mīn* "fish", which the pun needs, reaches the root with probability 0.41 and the North node with 0.22. And the Kurukh and Malto star words begin with *b-*, the reflex these languages show for Tamil *v-* in the entries we coded, so they may belong to DEDR's cross-referenced *viṇ* "sky" rather than to *miṉ* "to shine". The frozen credence rule moves conjecture [C-0011](../../knowledge/conjectures/C-0011-proto-dravidian-min-fish-and-star.md) from 0.15 to 0.35; after review we hold it at 0.20.

## Question and design

Parpola reads the Indus fish sign as "star" through the Dravidian pun *mīn* "fish" and *mīn* "star". For a writer of the third millennium BCE to use the pun, his language had to have both senses on one form. Kolipakam and colleagues (*Royal Society Open Science* 5: 171504, 2018) date the breakup of Proto-Dravidian to about 4,400 years ago (4,433 years at the root of their maximum clade credibility, or MCC, tree), inside the Mature Harappan period, so a meaning present at the root of their tree was in use then, and a meaning found only inside one branch is younger than the family.

We coded each meaning Parpola's readings need (sixteen senses of nine words; [ENTRIES.md](ENTRIES.md)) on the twenty tips of that tree, using the DEDR entry in which Tamil gives the cited form with that meaning. A tip was coded 1 when DEDR lists a form for its language in the entry with a gloss in the meaning's class, 0 when it lists forms with no such gloss, and missing when it lists no form. We reconstructed every meaning by parsimony and by a symmetric two-state Markov model (Mk1) with its rate fitted by maximum likelihood on the tree and a flat root prior, and compared the needed meanings with 10,000 reference sets, each drawing one unproposed gloss from the entry of each needed meaning. The sense classes (what counts as "star" and the fifteen other meanings), the coding rules, the models, the pass rules, the kill condition and the credence rule were frozen in [PROTOCOL.md](PROTOCOL.md) at 01:49 UTC on 21 October, before any entry was opened. [AMENDMENT-1.md](AMENDMENT-1.md) records two post-data decisions about locating entries, both repeated literally as a sensitivity analysis, and [S8-RECODE.md](S8-RECODE.md) the plain-reading recodes, written before any result was computed. The code was frozen by hash in [FREEZE.json](FREEZE.json) at 05:16:43 UTC and run once into [results.json](results-v1/results.json). An independent implementation of the primary model reproduces every root probability to within 3×10⁻⁹ and every parsimony root set ([verification-v1.json](verify/verification-v1.json)).

DEDR is the only lexical witness for the primary analysis, and its online edition is all rights reserved, so its pages, the parsed entries and the per-language codings stay local; tracked files hold counts and probabilities. DEDR records forms; when it lists no form for a language in an entry, the tip is missing, which is common in the smaller languages: Yeruva has no DEDR label at all, and Badaga and Betta Kurumba are missing from every coded entry.

## Results

### "Star"

| Analysis | Root | North Dravidian node | Parsimony at root |
|---|---|---|---|
| Primary: entry 4876, Mk1, MCC tree | 0.524 | 0.681 | absent |
| Doubtful forms excluded (S1) | 0.524 | 0.681 | absent |
| Two rates, flat root prior (S2) | 0.509 | 0.681 | |
| Two rates, stationary root prior (S2) | 0.531 | 0.685 | |
| 1,000 posterior trees (S5): mean, 95% range, share above 0.5 | 0.520, 0.498–0.561, 0.89 | 0.679, share 0.92 | |
| Homophone: star forms beginning *min-* in any entry (S4) | 0.412 | 0.220 | absent |
| Fieldwork word for "star" in DravLex containing *mīn* (S3) | 0.001 | 0.000 | absent |
| Literal entry location: STAR on 4885, "fish" (S7) | 0.000 | 0.000 | absent |
| Exploratory, after the result: Kurukh and Malto star words removed (missing / coded 0) | 0.472 / 0.344 | | absent |

Entry 4876 is headed by Tamil *miṉ* "flash, glitter, lightning" and gives a star sense in Tamil, Malayalam, Kota, Toda and Kannada (South I), Gondi (South II), and Kurukh and Malto (North). It gives forms without a star sense in Kodava and Tulu (South I), Telugu, Kuwi and Koya (South II) and Parji (Central); Brahui, Kolami and Ollari Gadba have no form in it. Entry 4885, *mīṉ* "fish", gives only "fish", in thirteen tips. The fitted rate of change for "star" is high, 1.28 changes per root height, so the tree retains little information about the root state and the likelihood estimate sits close to one half; parsimony needs four changes and places "star" absent at the root, so that the sense arose more than once.

Under the frozen rules P1 passes (0.524 > 0.5), P3 passes (0.681 > 0.5) and the kill condition fails, because two North tips are coded 1. The posterior trees keep the root above one half in 89% of samples, and the two-rate model agrees. The literal location of S7, which codes "star" on the fish entry where DEDR gives no star sense, meets the kill condition by construction and records what the protocol's entry-word search alone would have produced.

### All needed meanings and the reference

| Meaning | Entry | Root | North | Parsimony root |
|---|---|---|---|---|
| fish | 4885 | 1.000 | 1.000 | present |
| star | 4876 | 0.524 | 0.681 | absent |
| six | 2485 | 1.000 | 1.000 | present |
| seven | 910 | 1.000 | 1.000 | present |
| three | 5052 | 0.913 | 0.775 | present |
| banyan | 5220 | 0.000 | 0.000 | absent |
| north | 5218 | 0.677 | 0.537 | ambiguous |
| earring or bangle | 4979 | 0.500 | 0.500 | ambiguous |
| youth | 4978 | 0.500 | 0.500 | ambiguous |
| squirrel | 4198 | 0.000 | 0.000 | absent |
| child | 4198 | 0.500 | 0.500 | present |
| space | 5498 | 0.500 | 0.500 | absent |
| white | 5496 (a) | 0.855 | 0.522 | present |
| Kāma, for *vēḷ* "Murukan" | 5528 | 0.004 | 0.049 | absent |
| spindle | 1195 | 1.000 | 1.000 | present |
| to shine, ray | 1193 | 0.594 | 0.491 | ambiguous |

The entries for "fish" and "spindle" have no gloss outside the needed sense, so the comparison uses the other fourteen meanings. Seven of them have a root probability above one half (star, six, seven, three, north, white, to shine); in the 10,000 reference sets, drawn from 361 unproposed glosses, the count averaged 0.54 and reached 4 at most, so P2 passes with p = 1/10,001. Restricted to the seven value meanings that carry the puns, the count is 4 against a reference mean of 0.05. The comparison holds under every coding variant (S1, S6, S7 and S8 give counts of 6 to 8 against reference means near 0.5).

Three of Parpola's senses have no entry in DEDR: *vaṭam* "banyan" (DEDR's *vaṭam* means "cable, rope"), *piḷḷai* "squirrel" and *vēḷ* "Murukan" (the qualifying entry gives "Kāma", in Tamil and Malayalam only). Four meanings sit at exactly one half because a few disagreeing tips drive the fitted rate to its upper range, where the root is uninformative.

## What the result means

Parpola's pun has two parts that the dictionary separates. "Fish" is one etymon, *mīn*, present at the root without doubt. "Star" belongs to a second etymon, *miṉ* "to shine", whose star sense DEDR attests in the North, South II and South I branches. Where that star word has the bare form *mīn* (Tamil, Malayalam, Kannada, Kota, Toda) it is homophonous with "fish"; in Gondi, Kurukh and Malto it carries a suffix in *-k-* (*miḍkos*, *bīnkō*, *bínḍke*), and two Gondi forms begin with *min-* or *mīn-*: Maria *minˀ konj(i)* "star, firefly" and Trench's *mīnkō*, glossed as the stars a dazed man sees. The reconstruction therefore supports a star word from the root "to shine" at the root of the family with about even odds, and supports the bare homophone *mīn* "star" mainly in South I.

Two facts about the tree shape these numbers. The MCC tree splits South I from all other branches at the root, so any meaning shared by a South I language and Gondi is placed at the root unless it was borrowed; under the traditional subgrouping, with South I and South II as sisters and the northern branch splitting first, the same Gondi attestation would place the meaning at Proto-South Dravidian instead. And because the other side of the root is sparsely attested in DEDR, a meaning found in South I alone can exceed one half: "north" reaches 0.677 with no attestation outside South I and one Telugu form without it. The 0.5 threshold of P1 is therefore a weak bar on this tree, and the 0.2 kill line and the parsimony reconstruction carry more of the information.

The Kurukh and Malto forms decide most of the northern evidence. Both begin with *b-*. In entry 5496 (a), Tamil *veḷ* "white" corresponds to Kurukh *bilc-* "to shine" and Malto *bilpu* "moon", so *b-* answers Tamil *v-*; in entries 5052 and 4885 Tamil *m-* stays *m-* in Kurukh (*mūnd* "three") and Malto (*mínu* "fish"). DEDR closes entry 4876 with a cross-reference to entry 5396, Tamil *viṇ* "sky". If the northern star words continue *viṇ* "sky", they leave entry 4876, "star" is confined to South Dravidian, and its root probability falls to between 0.34 and 0.47; that is still above the kill line, because Gondi keeps the link to South I. This check was made after the result and is exploratory.

The pass of P2 says that Parpola chose senses that are old in the family more often than chance choice from the same entries would, which is what a scholar who checks attestation across subgroups should achieve. It does not test the interlocks themselves, and it rests mostly on the numerals and on well-attested words.

## Credence

The frozen rule gives 0.35: P1 and P2 pass, P3 passes, and the parsimony root score of 0 lowers the pass from 0.45 to 0.35. The protocol lets the sensitivity analyses lower the credence after review, and three of them bear on the claim as stated, that *mīn* itself meant "star": the homophone reconstruction (0.41 at the root, 0.22 at the North node), the fieldwork lists, in which only Tamil uses a *mīn* form for "star" today, and the *b-*/*v-* correspondence that may remove the northern evidence. We set the credence at 0.20, above the starting 0.15 because the star sense of the "shine" etymon is attested in Gondi and, on DEDR's reading, in the north, and below the frozen 0.35 because the homophone that the pun needs is reconstructed mainly for South I.

## Deviations and exploratory steps

The protocol's entry-word search could not find Tamil *mīṉ* "star", which DEDR lists inside entry 4876; we located it, and four other forms, by full-text search, and repeated the literal procedure as S7 (Amendment 1). The EARRING location follows the plain meaning of the Tamil gloss, also repeated literally in S7. The posterior archive holds 18,000 trees, the post-burn-in count the article reports, so the protocol's further 10% discard only thinned the sample. Codex's first parser attributed the Gondi forms of entry 5052 to Gadba; an independent check found this before the freeze, and the corrected parse was used (see [RETROSPECTIVE-CODEX.md](RETROSPECTIVE-CODEX.md)). The *b-*/*v-* observation, the reconstruction without the northern forms and the Kodava compound *boḷḷi mi·nï* "morning star" (literally "white star", the form of Parpola's *veḷ-mīn* "Venus", with a second member identical to Kodava *mi·nï* "fish") were all noticed after the results and enter no rule.

## Boldest reading and the test that decides it

The speakers of Proto-Dravidian, about 2400 BCE, called a star "the shining one" with a word built on *miṉ* "to shine", and in the South Dravidian languages that word had the bare form *mīn*, the same as the word for fish; a writer in that language could draw a fish to write "star", and the Kodava compound *boḷḷi mi·nï* "morning star", literally "white star", is the very compound Parpola reads as Venus in the Indus fish signs.

The test that decides the northern half of this reading is a correspondence count across the whole dictionary: for every DEDR entry with a Tamil initial *m-* or *v-* and a Kurukh or Malto reflex, record whether the northern form begins with *m-* or *b-*. If northern *b-* answers Tamil *v-* and northern *m-* answers Tamil *m-* without exception, *bīnkō* and *bínḍke* belong to *viṇ* "sky", the star word of the root of the family was not *mīn*, and the pun is a South Dravidian pun, whose Indus use would need an early South Dravidian language in the north-west. If northern *b-* also answers Tamil *m-* before long *ī* in other entries, the northern star words continue *mīn-k-*, and the homophone reaches the North node. The count uses no Indus text and can run on the DEDR pages the project already holds, or on the openly licensed DEDR-linked lexicon of Merriam and Fuls. Prediction P4 of C-0011, a *mīn* form for "star" recorded in a North or Central language by a source independent of DEDR, would decide it directly.
