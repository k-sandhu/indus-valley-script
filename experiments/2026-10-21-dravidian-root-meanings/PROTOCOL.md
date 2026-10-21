# DRAVIDIAN-ROOT-MEANINGS-2026-10-21: did Proto-Dravidian *mīn mean "star"?

Recorded on 21 October 2026 (UTC) before any entry of the *Dravidian Etymological Dictionary* was opened for this study and before the tree, the posterior sample or the cognate data of Kolipakam and colleagues were downloaded. Author: Claude Opus 5.5 (`claude-opus-5-5`) in the Claude Code desktop app, for k-sandhu. Mechanical work is delegated to the Codex CLI running `gpt-6.1-sol`; the delegation is recorded in `CODEX-PROMPT*.md` and `RETROSPECTIVE-CODEX.md`. Owned paths: `experiments/2026-10-21-dravidian-root-meanings/`, `data/raw/2026-10-21-dravidian-root-meanings/` (local only), one new conjecture card and `knowledge/registry/attempts/DRAVIDIAN-ROOT-MEANINGS-2026-10-21.json`. This is study 6 of the [Parpola direction note](../../knowledge/directions/parpola-forward-2026-10-20.md).

## Claim under test

Proto-Dravidian *mīn* meant both "fish" and "star", so the pun on which Parpola's astral reading of the fish sign rests was available to speakers of a Dravidian language in the third millennium BCE. Parpola checks that a word occurs in more than one subgroup of the family. A dated tree allows a sharper question: with what probability did the ancestor of all Dravidian languages, about 4,500 years ago on the estimate of Kolipakam and colleagues, carry the meaning? The same question applies to every other meaning his readings need, and the meanings he did not need, drawn from the same dictionary entries, give the reference against which the needed ones are judged.

The study uses dictionaries and a published tree. It reads no Indus text, spends no part of the corpus, and needs no shots round; `bench/spent.json` is not changed. No bench task scores a lexical reconstruction, so the package attaches a `python -m bench selftest` output only as a record of the harness version in use.

## What we had read before writing

We had read the direction note (its readings table and studies 1, 5 and 6), conjecture cards C-0007 and C-0008, the fish-context report summary given there, the landing page of the Digital Dictionaries of South Asia (DSAL) edition of the dictionary with its rights notice, the open-access article of Kolipakam and colleagues on PubMed Central, and the file list of its figshare supplement. From the article: 20 varieties were sampled, North (Brahui, Malto, Kurukh), Central (Ollari Gadba, Parji, Kolami), South II (Kuwi, Gondi, Koya, Telugu) and South I (Tamil, Malayalam, Kannada, Kodava, Tulu, Yeruva, Toda, Kota, Badaga, Betta Kurumba); the preferred analysis is a covarion model with a relaxed lognormal clock and a Yule tree prior, summarised as a maximum clade credibility (MCC) tree; its root has a mean age of 4,650 years (95% interval about 3,000–6,500); North Dravidian is monophyletic only because the analysis constrained it; the first split in the MCC tree separates South I from the other three groups, with low support for the higher nodes; and Kolami falls with South II.

From general reading before this study the author recalls that the dictionary gives "star" for *mīn* chiefly in Tamil and Malayalam. The recollection is unchecked and is the main reason for the low starting credence below. We had not opened any dictionary entry, the tree file, the posterior trees, the BEAST XML or any cognate table.

## Sources

| Source | Use | Rights observed | Handling |
|---|---|---|---|
| T. Burrow and M. B. Emeneau, *A Dravidian Etymological Dictionary*, 2nd ed. (Oxford: Clarendon Press, 1984), DSAL web edition, data updated February 2021, <https://dsal.uchicago.edu/dictionaries/burrow/> | Forms and glosses of the chosen entries; abbreviation list | "Copyright 1984 by Oxford University Press. No part of this publication may be stored, transmitted, retransmitted, lent, or reproduced in any form or medium without the permission of Oxford University Press." No licence and no permission recorded: status `rights-unverified` (all rights reserved) | Only the chosen entries, the definition searches of the secondary analysis and the abbreviation list are fetched, once, with a logged hash. Pages, parsed forms and per-language codings stay in `data/raw/2026-10-21-dravidian-root-meanings/`. Tracked files hold entry numbers, our own sense rules, counts per subgroup, root probabilities and hashes. Prose quotes a gloss only where an argument needs it. |
| V. Kolipakam, F. M. Jordan, M. Dunn, S. J. Greenhill, R. Bouckaert, R. D. Gray and A. Verkerk, "A Bayesian phylogenetic study of the Dravidian language family", *Royal Society Open Science* 5: 171504 (2018), <https://doi.org/10.1098/rsos.171504> | MCC tree `drav_cov_est_ucln_yule.mcct.trees` (figshare 5982046), posterior sample `drav_cov_est_ucln_yule_no_burnin.trees.zip` (figshare 5965690), BEAST XML (figshare 5982055), supplementary text (figshare 5982052) | Article CC BY 4.0; the figshare items' licence is recorded on download | Downloaded into a new empty directory under the local raw directory, hashed, and read only by scripts run with `python -I`. Tracked files hold the tree's hash, tip list, node ages and our results. |
| DravLex, the cognate database cited in the article's data statement (Zenodo), if openly licensed | Secondary check S3 only | Recorded on download | As above. |

## Words and meanings

Parpola's readings table (direction note, after Parpola 2010, pp. 15–28, and Parpola 2005 for three strokes and fish) uses the Dravidian words below. A needed meaning is a sense the reading requires of the word: the picture sense, which lets the sign depict the word, the value sense, which the reading assigns, or a numeral. The role column separates them because the two roles are expected to behave differently: a picture sense is usually the commonest sense of a word, and the pun's value sense is the one in question.

| Word (Tamil citation form) | Needed meaning | Code | Role |
|---|---|---|---|
| *mīṉ* | fish | FISH | picture |
| *mīṉ* | star | STAR | value |
| *āṟu*, *aṟu-* | six | SIX | numeral |
| *ēḻu*, *eḻu-* | seven | SEVEN | numeral |
| *mū-*, *mūṉṟu* | three | THREE | numeral |
| *vaṭam* | banyan | BANYAN | picture |
| *vaṭa*, *vaṭakku* | north | NORTH | value |
| *muruku* | earring or bangle | EARRING | picture |
| *muruku* | youth | YOUTH | value |
| *piḷḷai* | squirrel | SQUIRREL | picture |
| *piḷḷai* | child | CHILD | value |
| *veḷi* | space | SPACE | picture |
| *veḷ* | white | WHITE | value |
| *vēḷ* | a name of Murukan | VELGOD | value |
| *katir* | spindle | SPINDLE | picture |
| *katir* | to shine | LIGHT | value |

### Choosing the entries

For each Tamil citation form we search the DSAL edition by entry word, exact match and then "beginning with". A needed meaning is assigned to the entry in which the Tamil line gives the cited form, or a form built on it, with a gloss in the meaning's class; if no Tamil line qualifies, the Malayalam line is used in the same way. When two homonymous entries both qualify, both are coded and the meaning's result is the mean of the two root probabilities. When no entry qualifies, the meaning is coded on the entry that holds the cited form with its other needed meaning, or, for a word with one needed meaning, on the first entry returned for the cited form; it is then absent in every language by construction, and the report says so. The chosen entry numbers are recorded in `ENTRIES.md`, hashed before any coding is computed.

### Sense classes

A gloss is the English text DEDR gives for one form in one language. We split it into segments at commas and semicolons that lie outside parentheses, remove parenthesised text, lower-case it, and remove a leading "a", "an", "the" or "to". The head of a segment is its last word, or, when the segment contains " of ", the last word before the first " of ", after a leading "kind of", "sort of", "species of", "variety of" or "type of" has been removed (with or without "a"). A final "s" is removed from the head when the word has more than three letters and does not end in "ss". A segment falls in a class when the class rule below holds; the rules were written before any entry was read.

- **STAR.** The head is star, planet, constellation, asterism, nakshatra (any spelling, including nakṣatra and naṭcattiram), comet or meteor; or the segment contains the phrase "lunar mansion", "shooting star", "morning star", "evening star", "pole star", "polar star" or "north star"; or the segment names a particular star, planet or star group: Venus, Jupiter, Mars, Mercury, Saturn, Sirius, Canopus, Arcturus, Aldebaran, Antares, Spica, Regulus, Capella, Vega, Pleiades, Orion, Ursa Major, Great Bear, Seven Sages, Seven Rishis, Rohiṇī, Kṛttikā, Ārdrā, Mṛgaśiras, Revatī or Aśvinī. Excluded even when the rule above holds: the sun, the moon, the sky, a zodiac sign or constellation whose name is the word "fish" (Pisces, "the fish sign"), any segment containing starfish, star-anise, star apple or star-shaped, and any segment containing star together with mark, spot, blaze or forehead. Shining, light, lightning, glitter, spark and brightness are not STAR; they belong to LIGHT where a class needs them.
- **FISH.** The head is fish. Fisherman, fishing, fishery, fish-hook, fish-trap, fish net and other compounds whose head is not fish are excluded.
- **SIX, SEVEN, THREE.** The segment is the numeral word itself (six, seven, three) or the digit. Sixth, sixty, sixfold and similar derivatives are excluded.
- **BANYAN.** The segment contains banyan or banian, or names *Ficus benghalensis*, *F. bengalensis* or *F. indica*.
- **NORTH.** The segment contains north, northern, northward, northwards or northerly as a whole word.
- **EARRING.** The head is earring, ear-ring, ear ornament, ear-ornament, ear-pendant, ear-drop, eardrop, ear jewel, bangle or bracelet, or the segment contains both ring and ear.
- **YOUTH.** The segment contains youth, youthful, youthfulness, young, juvenile, juvenility, adolescence, adolescent or "tender age".
- **SQUIRREL.** The segment contains squirrel.
- **CHILD.** The head is child, children, infant, baby, boy, girl, son, daughter, offspring or "young one", or the segment is "young", "young one" or "young ones" or begins with "young of".
- **SPACE.** The head is space, interval, gap, interspace, void, vacuum, vacancy, emptiness or expanse, or the segment is "open place", "open ground" or "open air".
- **WHITE.** The segment contains white, whiteness or whitish.
- **VELGOD.** The segment names Murukan (any spelling), Skanda, Subrahmanya, Kāma, Cupid or the god of love, or is "god" or "deity".
- **SPINDLE.** The segment contains spindle.
- **LIGHT.** The head is ray, beam, sunbeam, light, lustre, luster, radiance, brightness, brilliance, splendour, splendor, gleam, glitter, shine, shining, glow or effulgence, or the segment begins (after the "to" is removed) with shine, glitter, gleam, glisten, glow, sparkle or flash.

A class applies only within the entry to which its meaning is assigned. A segment can belong to more than one class.

### Coding languages

Each needed meaning is coded on the 20 tips of the Kolipakam tree. A tip is coded 1 when DEDR lists, under the assigned entry, at least one form for a language mapped to that tip with a segment in the class; 0 when DEDR lists at least one form for that tip but none has such a segment; and missing when DEDR lists no form for that tip. Derived forms and compounds listed for the language under the entry count, because DEDR lists them as part of the etymon's record in that language.

DEDR language labels are mapped to tips by the abbreviation list in its front matter. Dialect and source labels pool to their language: Ta. to Tamil; Ma. to Malayalam; Ka. and its dialect labels to Kannada, except a label the abbreviation list identifies as Badaga, which goes to Badaga; Koḍ. to Kodava; Tu. to Tulu; To. to Toda; Ko. to Kota; Te. to Telugu; Kol. to Kolami; Pa. to Parji; Ga. (Oll.) to Ollari Gadba; every Gondi dialect to Gondi except Koya, which goes to Koya; every Kuwi dialect to Kuwi; Kur. to Kurukh; Malt. to Malto; Br. to Brahui; the labels the abbreviation list gives for Yeruva and Betta Kurumba, if any, to those tips. Languages that are not tips (among them Irula, Pālu Kurumba, Koraga, Belari, Naikri, Naiki, Salur Gadba, Konḍa, Pengo, Manḍa and Kui) are not used, and neither are Indo-Aryan and other non-Dravidian words cited in an entry. A tip with no DEDR label is missing for every meaning. The mapping table is built from the abbreviation list and recorded before any meaning is coded.

A form that DEDR marks as borrowed from another language is ignored; if every form of a tip in the entry is so marked, the tip is missing. Forms that DEDR marks as doubtful with "?" are included in the primary coding and excluded in sensitivity analysis S1.

## Reconstruction

**Tree.** The primary tree is the MCC tree of the preferred analysis, `drav_cov_est_ucln_yule.mcct.trees`, with the branch lengths written in the file. Tip labels are matched to the 20 varieties by name; a mismatch stops the run. The North Dravidian node is the most recent common ancestor of Brahui, Kurukh and Malto. We also report the South I node (most recent common ancestor of the ten South I tips) and the node ages from the tree's heights.

**Parsimony.** For each meaning we compute the most-parsimonious reconstruction sets at every node with unit cost for a change in either direction and missing tips allowed either state (Sankoff's algorithm with a downward and an upward pass, so that each node's set holds the states that some most-parsimonious reconstruction of the whole tree assigns to it). The parsimony score at a node is 1 when the set is {1}, 0 when it is {0} and 0.5 when both states are most parsimonious.

**Maximum likelihood.** The primary model is the symmetric two-state Markov model (Mk1): one rate of change q for gain and loss, estimated by maximum likelihood for each meaning separately on the tree rescaled to a root height of 1, by bounded one-dimensional optimisation of log q over q in [10⁻⁶, 10³]. Missing tips contribute a likelihood of 1 for both states. The root prior is flat (one half for each state), which is also the stationary distribution of Mk1. The probability that the meaning was present at a node is its marginal posterior state probability given the data and the fitted rate, computed for the root by Felsenstein's pruning algorithm and for internal nodes by a second, downward pass. A meaning coded 1 in every observed tip has a fitted rate at the lower bound and a root probability near 1; one coded 0 everywhere has a probability near 0. A meaning with fewer than two observed tips is reported but not interpreted.

**Age of the oldest node.** For each needed meaning we report the oldest node whose ML probability exceeds 0.5 and its age, to show how far back the tree places the meaning when it does not reach the root.

**Sensitivity analyses.** None of these enters the pass rules; each is reported beside the primary result.

- S1. Doubtful forms excluded.
- S2. Asymmetric two-state model (Mk2, separate gain and loss rates) with a flat root prior and with the stationary root prior.
- S3. A secondary witness from fieldwork: if DravLex is available under an open licence, each tip whose form for the concept "star" contains a match of the regular expression `m[iīɪ]ː?[nṉɳ]` after Unicode NFC normalisation and lower-casing is coded 1, other tips with a form 0; the same reconstructions are run. This asks whether any modern variety outside South I still uses a *mīn* form for "star".
- S4. Homophone search: every DEDR entry returned by a DSAL definition search for star, planet, constellation, asterism, comet or meteor is scanned, and a tip is coded 1 when any of its forms with a STAR segment begins with m followed by i or ī and then n, ṉ or ṇ, 0 when the tip has a form in the *mīn* "fish" entry but no such star form, and missing otherwise. This asks whether a star word homophonous with *mīn* reaches the root through any etymon, since Parpola's pun needs homophony and does not need a single etymon.
- S5. The posterior sample: from `drav_cov_est_ucln_yule_no_burnin.trees.zip` we discard the first 10% of samples as burn-in (or the burn-in stated in the supplementary text, if it states one) and take 1,000 trees evenly spaced over the remainder. For each tree the Mk1 rate is re-estimated and the root and North Dravidian probabilities computed; we report the mean, the 2.5th and 97.5th percentiles and the share of trees above 0.5.
- S6. Keyword coding: each needed meaning is coded by head match of its first keyword only (fish, star, six, seven, three, banyan, north, earring, youth, squirrel, child, space, white, Murukan, spindle, ray), the same unit used for the reference draw, so that the comparison in P2 is repeated without the synonym lists.

## Reference draw

The reference asks whether Parpola's needed meanings reach the root more often than meanings nobody proposed, taken from the same entries. For each entry used by a needed meaning, the pool of reference meanings is the set of distinct segment heads (defined above) found in the glosses of forms of tip languages under that entry, less every head whose segment falls in a needed class assigned to that entry. A reference meaning is coded on the tips like a needed meaning, with "the segment's head equals the reference head" as its class rule. Heads that are grammatical labels (pl., obl., n., adj., adv., v.i., v.t., intr., tr., caus., imper., past, fut., neg., inf., ger.), cross-references (any segment containing DED, DEDR, Turner, CDIAL, a digit, "<" or "=") and empty segments are dropped.

One reference set draws, for each needed meaning, one head uniformly at random from the pool of that meaning's entry (with replacement across draws, so two needed meanings on the same entry draw independently). A needed meaning whose pool is empty is left out of the comparison on both sides, and the report names it. We draw 10,000 sets with the NumPy generator `default_rng(20261021)`. The root probability of every pooled head is computed once under the primary model, so a draw only resamples them.

The statistic T is the number of needed meanings with an ML root probability above 0.5. T* is the same count in a reference set. The one-sided p-value is (1 + #{T* ≥ T}) / (1 + 10,000). We also report the mean root probability, and both statistics restricted to the seven value meanings (STAR, NORTH, YOUTH, CHILD, WHITE, VELGOD, LIGHT), which compares the pun meanings with unproposed meanings without the advantage of picture senses and numerals.

## Predictions, pass rules and kill condition

From the direction note, frozen here with the definitions above:

- **P1.** The ML root probability of STAR on the *mīn* entry under the primary model on the MCC tree exceeds 0.5.
- **P2.** Needed meanings reach the root more often than reference meanings: T exceeds the mean of T* and the one-sided p-value is at most 0.05.
- **P3.** The ML probability of STAR at the North Dravidian node exceeds 0.5. The note asks for this estimate; if the pun was Proto-Dravidian, the branch nearest the Indus inherited it.
- **Kill condition.** The reading of the fish sign as "star" in a third-millennium language is dead if STAR is confined to South Dravidian, meaning that no Central or North tip is coded 1 (South Dravidian here is South I and South II together, as in Krishnamurti's classification and the article's Table 1), and its ML root probability is below 0.2.

**Credence rule.** The claim starts at 0.15. After the run the frozen rule sets it as follows: P1 and P2 pass, 0.45 (0.35 if P3 fails or the parsimony root score is 0); P1 passes and P2 fails, 0.30; the kill condition holds, 0.02 and status dead; STAR reaches a Central or North tip but its root probability is below 0.2, 0.08; any other outcome with P1 failing, 0.10. The sensitivity analyses can lower the credence after review but cannot raise it under this rule.

## Order of work

1. This protocol is hashed into `PROTOCOL.sha256` before any entry is read for coding and before any tree is downloaded.
2. Entries are chosen by the rule above and recorded in `ENTRIES.md`, which is hashed.
3. Codex run 1 downloads the tree, posterior sample and supplementary files; fetches the chosen entries, the S4 definition searches and the abbreviation list; parses them; builds the language-to-tip table; and implements and tests parsimony and ML reconstruction on synthetic trees of known answer, the sense coder and the reference draw. It computes no root probability on real codings.
4. We review the parsed entries for parse errors only, the mapping table and the tests. Corrections of parsing are recorded in an amendment with their reasons; sense rules are not changed. The code is hashed into `FREEZE.json`.
5. The frozen scripts compute the results once into `results-v1/`. Any later rerun goes to a new dated directory and leaves `results-v1/` unchanged.
6. The report, the conjecture card's record and the retrospectives are written from those outputs.

Exploratory steps, if any, are named as such in the report and kept apart from the frozen endpoints.
