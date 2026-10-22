# REBUS-BLIND-TEMPLATES-2026-10-22: Parpola's word assignments on sign pairs he did not choose

Recorded on 22 October 2026, before any Tamil compound was looked up for this study and before the confirmation half of the split was read. Authors: Claude (Opus 5.5, model ID `claude-opus-5-5`, Claude Code desktop harness), in a session started from the session that ran REBUS-BASE-RATE-2026-10-21. Owned directory: `experiments/2026-10-22-rebus-blind-templates/`. Acquired papers, extraction records and every word-level output derived from the *Tamil Lexicon* stay local in `data/raw/2026-10-22-rebus-blind-templates/`.

## Question

The base-rate study of 21 October showed that each of Asko Parpola's Dravidian rebus interlocks that holds in the Madras *Tamil Lexicon* arises for random words of the same compounding productivity in 8–43% of cases, and that only their conjunction is rare. A conjunction of cheap links is rare only when few links were tried, so the value of Parpola's network depends on how many sign sequences he examined before he published the ones that worked. Conjecture [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md) states that the interlocks measure the density of the Old Tamil compound vocabulary and the selection of sign sequences, not the language of the script. Its prediction P1 is the test run here: take Indus sign pairs that Parpola did not choose, give each sign the Dravidian word he assigns to its picture, and count how often the two words form an attested compound, against the rate for random words of the same compounding productivity and frequency.

If the script writes a Dravidian language and Parpola's identifications are right, adjacent signs should often spell compounds and noun phrases, and his words should form attested compounds clearly more often than matched random words. If his successes come from selection, his words on unselected pairs should do about as well as random words.

## Source check

P1 asks for the picture identifications of Parpola's 1994 book, *Deciphering the Indus Script* (Cambridge University Press). The book is not available to the project with clear rights: the Internet Archive holds it as a restricted lending copy (`decipheringindus0000parp`), and the other copies there are uploads by users whose rights we cannot verify, which we do not use. Its sign list (fig. 5.1) gives sign numbers and graphic variants, while the identifications and Dravidian words are spread over its chapters.

We therefore take the identifications from five of Parpola's papers that restate the 1994 readings and add later ones. Each was acquired with a logged request (`code/acquire.py`; URL, status, bytes, SHA-256 and time in `data/raw/2026-10-22-rebus-blind-templates/sources-v1/requests.json`) except the 2010 paper, which the project already held:

| Source | Location | Identifications used |
|---|---|---|
| Parpola 1997, "Dravidian and the Indus script: On the interpretation of some pivotal signs", *Studia Orientalia* 82: 167–192 | journal.fi article 45117 | bull's head, yoke-carrier, numerals one and two |
| Parpola 2005, "Study of the Indus script", *Transactions of the International Conference of Eastern Studies* 50: 28–66 | harappa.com | fish, fig tree, crab, six, seven, eye, water |
| Parpola 2008, "Is the Indus script indeed not a writing system?", *Airāvati*, 111–131 | harappa.com | eye |
| Parpola 2009, "'Hind leg' + 'fish': towards further understanding of the Indus script", *Scripta* 1: 37–76 | harappa.com | hind leg, crab, and restated earlier readings |
| Parpola 2010, *A Dravidian solution to the Indus script problem* | local copy of the fish-context package | fish, six, seven, fig tree, spindle, intersecting circles, squirrel, two long strokes |

Five extraction agents read one paper each, with instructions to record only what the paper states and not to open any dictionary or the *Tamil Lexicon* tables. Their records are in `data/raw/2026-10-22-rebus-blind-templates/extraction-v1/`. We checked the readings against the page images where a form or glyph mattered; the 'bull's head' glyph printed in Parpola 1997 (printed pp. 170–171) is the sign other lists call the 'jar' (ICIT 740), and the paper names its ligatures with one and two strokes between the horns.

## Identifications and words

[identifications-v1.json](identifications-v1.json) fixes 16 signs, their ICIT codes and their Tamil words. A sign enters when a source gives a Dravidian word for what it depicts, as asserted, suggested or alternative, and Parpola does not call its reading unresolved. Ligatures and modified signs that Parpola reads as compounds stay out, because their word is itself a compound. The codes of a sign are the codes at the position Parpola describes in the objects he cites by CISI number. We read the sign sequences of those 45 cited objects directly from the corpus file, outside the loader, to fix sign identity; the listing stays local in `data/raw/2026-10-22-rebus-blind-templates/mapping-v1/`. The 'bull's head' is fixed by its printed glyph, and the numerals one and two are the ICIT short-stroke codes. Words are Tamil forms as printed with diacritics in any source, Proto-Dravidian forms without the asterisk when no Tamil form is given, and one form per stem: a form is dropped when its stem under the base-rate study's stated tolerance equals that of a form already listed.

| Sign | ICIT codes | Words |
|---|---|---|
| fish | 220 | mīṉ |
| numeral one | 001 | oru, oṉṟu |
| numeral two | 002 | iru, iraṇṭu |
| six | 016 | aṟu |
| seven | 017 | eḻu |
| fig tree | 776, 783, 784, 785, 786 | vaṭam |
| spindle | 683, 684 | katir |
| intersecting circles | 840 | muruku |
| squirrel | 257 | piḷḷai, aṇil |
| two long strokes | 032 | veḷ |
| crab | 798 | kōḷ |
| eye | 832 | kaṇ |
| water | 904 | nīr |
| hind leg | 278, 279 | tāḷ, tōḷ |
| bull's head | 740 | ā, āṉ, āvu |
| yoke-carrier | 151 | kā, kāvu, kāvaṭi |

The spear (no CISI example), the *kaḷam* sign (cited only by a Koskenniemi–Parpola text number), the scorpion, oval and cart (several words, none satisfactory to Parpola) and the offering vessel (no word) are left out. The word for the two long strokes, *veḷ*, was found by Parpola through the compound search of 2010 rather than from the picture; it enters because it is his assignment, and every pair that 2010 search used is excluded.

## Templates

A template is an ordered pair of two different identified signs, first and second in reading order, with the words of each sign.

**Primary templates (shape C, "the pair spells a compound").** The template holds when some word of the first sign and some word of the second form an attested two-member compound of the *Tamil Lexicon*: either a compound anchored on the second word has a first member that coincides with the first word, or a compound anchored on the first word has a second member that coincides with the second word. Anchoring and coincidence follow the base-rate code unchanged (`Compounds`, `picture_hits`): anchoring by the stem, coincidence under the stated tolerance T0s with sandhi restoration of first members. This is the template of *vaṭa-mīṉ*, *aṟu-mīṉ*, *eḻu-mīṉ*, *kōṇ-mīṉ*, *nīr-k-kaṇṭi* and *katir-k-kaṭavuḷ*.

**Gapped templates (shape S, "a hidden shared member").** Pairs with exactly one unidentified sign between them hold when compounds W1-X and X-W2 share a member X, the search that produced *veḷ* in 2010 (`i1` of the base-rate code).

**Selection.** Pairs are counted on single-line faces of the pinned corpus, as distinct components of the split (aliases and identical texts joined, so a copied text counts once), summed over both halves. The discovery half was read on 22 October to check that enough pairs exist (`discovery-v1/pairs.json`: 34 ordered adjacent pairs recur in two or more components). The confirmation half is read once, through the loader, after this protocol and its predictions are frozen. The primary list is every ordered adjacent pair in at least two components across both halves, without the pairs Parpola published in the five papers and without the numeral-and-fish pairs whose outcome the base-rate study already reported (numerals one to ten with *mīṉ*); if fewer than 20 remain, the threshold drops to one component. The gapped list follows the same rule. Parpola's twelve published pairs are scored as a separate selected set. `code/build_templates.py` writes `templates-v1.json`, whose SHA-256 is recorded in `FREEZE.json` before the scorer runs.

**Exposure.** No Tamil compound has been looked up for any template. The base-rate study enumerated the compounds anchored on *mīṉ* (82, of which its report names nine first members) and on *muruku* (7), so a template with either word is partly exposed. A sensitivity analysis drops every template that contains *mīṉ* or *muruku*.

## Measurement and null

For each template we record whether it holds for Parpola's words (h = 1 or 0). Each word is then replaced by random words matched on compounding productivity and Sangam frequency, exactly as in the base-rate study: candidates are native one-word nouns of the *Tamil Lexicon* whose form occurs among the Tamil forms of an attested DEDR entry, one per stem; a word in the first slot is matched on its productivity as a first member, a word in the second slot on its productivity as a second member, together with its Sangam frequency, and the 50 nearest candidates form its pool. A word that is not a one-word headword takes the frequency of the headword with the same stated-tolerance form, and frequency 0 if there is none.

The random rate r of a template is the share of replacement pairs for which it holds: exact over all 2,500 pairs when each slot has one word, otherwise estimated from 5,000 draws with each word replaced independently. A random key replaces every sign's word once per draw for its slot, and 10,000 random keys give the distribution of the number of templates that hold.

**Statistic.** The ratio of hit rates is H / R, where H is the number of primary templates that hold for Parpola's words and R the sum of their random rates. Its 95% interval comes from 2,000 bootstrap resamples of templates; the leave-one-out ratios remove each template in turn. We also report the share of random keys that reach H. The seed is 20261022.

**Sensitivities, reported without credence effect.** The practised tolerance T1s; pools of 25 and 100; direction a alone (the picture word as first member of a compound anchored on the second word, the literal shape of *vaṭa-mīṉ*); the primary set without templates containing *mīṉ* or *muruku*; the gapped templates; Parpola's published templates.

## Decision rules for C-0014 P1

- **Pass.** The ratio is below 2, and below 3 after removing any one template.
- **Kill.** The ratio is at least 3, the bootstrap 2.5% bound is above 1.5, and the ratio stays at or above 2 after removing any one template.
- Otherwise the prediction neither passes nor kills.

The influence conditions follow the project's rule for small groups. Joint credence rule for C-0014 (now 0.55): pass sets the credence to 0.8; kill sets it to 0.05 and the conjecture is dead; neither sets it to 0.35. The gapped and published sets and the sensitivities change nothing on their own.

**Power.** `code/power.py` (`power-v1/power.json`) simulates the rules with 30 and 40 templates. When Parpola's words do no better than random words, the pass rule is met in 82–100% of simulations. When they hold three times as often as random words, the kill is reached in 34–66% of simulations at random rates of 5–30%, and in 6–9% at a random rate of 2%, where the pass rule is still met by chance in 34–46%. A low random rate therefore makes a pass weak evidence, and the report states the observed rate.

## Order of work

1. Source acquisition and extraction (done), identifications (done), discovery pair counts (done).
2. `code/selftest.py` into `selftest-v1/`; `python -m bench selftest` and `python -m bench shots --synthetic` into this package.
3. `PREDICTIONS.json` registered and frozen through `bench.shots` with this protocol, the identifications and the code as artifacts.
4. Confirmation read: `code/pairs.py ... confirmation confirmation-v1/pairs.json --shot rebus-blind`.
5. `code/build_templates.py` into `templates-v1.json`; `code/freeze.py` writes `FREEZE.json` with the hashes of this protocol, the predictions, the identifications, the template list, the code and the input tables.
6. `code/run_templates.py templates-v1.json results-v1`.
7. An independent reimplementation of the primary search and of the random rates of a sample of templates, into `verification-v1.json`.
8. Report, retrospective, attempt entry and a proposed record line for C-0014.

Every output goes to a new path and the scripts refuse to overwrite. A repair after the freeze is recorded in a dated amendment that keeps the earlier output.

## References

Parpola, Asko. 1994. *Deciphering the Indus Script*. Cambridge: Cambridge University Press.
Parpola, Asko. 1997. Dravidian and the Indus script: On the interpretation of some pivotal signs. *Studia Orientalia* 82: 167–192.
Parpola, Asko. 2005. Study of the Indus script. *Transactions of the International Conference of Eastern Studies* 50: 28–66.
Parpola, Asko. 2008. Is the Indus script indeed not a writing system? In *Airāvati: Felicitation volume in honour of Iravatham Mahadevan*, 111–131. Chennai: Varalaaru.com.
Parpola, Asko. 2009. 'Hind leg' + 'fish': towards further understanding of the Indus script. *Scripta* 1: 37–76.
Parpola, Asko. 2010. *A Dravidian solution to the Indus script problem*. Chennai: World Classical Tamil Conference.
University of Madras. 1924–1936. *Tamil Lexicon*. DSAL edition, parsed in REBUS-BASE-RATE-2026-10-21.
