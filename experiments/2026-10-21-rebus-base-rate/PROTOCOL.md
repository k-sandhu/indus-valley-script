# REBUS-BASE-RATE-2026-10-21: the base rate of a rebus

Recorded on 21 October 2026, before any homophone rate or interlock search was computed on real lexicon data. Authors: Claude (Opus 5.5, model ID `claude-opus-5-5`, Claude Code desktop harness), working in a session started from the session that wrote the Parpola direction note. Owned directory: `experiments/2026-10-21-rebus-base-rate/`. Acquired sources and every table derived from them stay local in `data/raw/2026-10-21-rebus-base-rate/`.

## Question

Asko Parpola reads Indus signs as rebuses for Proto-Dravidian words and argues that his readings interlock "to an extent that excludes chance coincidences" (Parpola 2010, p. 28; page numbers are those printed in the running heads of the PDF). This study is study 1 of the [Parpola direction note](../../knowledge/directions/parpola-forward-2026-10-20.md). It measures the chance rate that note asks for. We encode Parpola's homophone procedure as a program and measure two things: how often a picturable noun and a meaning suitable for a name have homophones in each candidate language, and how often his interlock searches find a shared member when the words he started from are replaced by random words of the same kind. The study reads no Indus text and spends no part of the corpus.

The claim under test, from the direction note: Parpola's interlocking readings would rarely arise by chance, and Dravidian supplies them more readily than the other candidate languages. Its predictions are that a single homophone pair is about as easy to find in Dravidian as elsewhere, while his whole network of interlocks arises in fewer than 1% of random replacements. The reading is dead as evidence if random replacements produce interlocks of the same depth in more than 20% of draws.

## Prior attempts and what is new

The key-calibration work of 12 October showed that dictionary fits carry no weight until they are compared with random strings: consonant strings at Sanskrit letter frequencies divide into dictionary words in 92–100% of cases ([key calibration](../../knowledge/directions/key-calibration-2026-10-12.md), PUBLISHED-KEY-READABILITY-UNICITY-2026-10-12). The Bronze Age comparison found that equality-pattern word matches fit 91–97% of Indus faces in four unrelated languages (BRONZE-AGE-LEXICAL-PATTERN-AMBIGUITY-2026-10-12). The fish-context study of 20 October found that fish signs combine in a fixed order, failed Parpola's narrow asterism model on seals and lowered it to a credence of 0.05 (FISH-CONTEXT-2026-10-20, [C-0008](../../knowledge/conjectures/C-0008-fish-numerals-asterism-coverage.md)). No earlier package measured the chance rate of a rebus homophone or of a compound interlock. The new inputs are digital lexicons of five candidate language groups and the Old Tamil compound vocabulary of the Madras Tamil Lexicon.

No task of the shared harness scores lexical homophony. The nearest, `key-calibration`, ranks a sign key against rearrangements of its values on Indus texts, and this study reads none. We run `python -m bench selftest` once to record the state of the harness, run the study's own synthetic mode (`code/selftest.py`) before any real measurement, and add no statistic family to `bench/spent.json`.

## Parpola's procedure as a program

Parpola (2010, pp. 13–28) states four conditions for reading a sign: the depicted object is recognised, the sign is used as a rebus, the intended meaning follows from context, and a historically likely language has homophones for the picture and the meaning. For Proto-Dravidian he allows variation in "the length of vowels and consonants" and "not much else" (p. 13). Words must be represented in more than one subgroup and reconstructible for Proto-Dravidian (p. 15), compounds must be attested, Old Tamil above all (p. 17), and readings must interlock like a crossword. The program encodes these rules as follows.

A form is segmented into phonemes and compared as a sequence of segment classes. Three tolerances are fixed:

- **T0, the stated rule.** Vowel length and consonant gemination are free (merge step L below); nothing else is.
- **T0s, the scaled rule.** T0, followed for each non-Dravidian language by further merges from a fixed ladder until that language's per-segment collision probability (the chance that two segments drawn from its lexicon are identical) reaches the value for Tamil forms under T0. Languages that already reach it under T0 receive no further merge. For the Dravidian lexicon T0s equals T0.
- **T1s, the practised rule.** T0s plus the stem tolerance that Parpola's published matches use: a final *-m* after a vowel is dropped, then a final vowel, while at least two segments remain. This equates *vaṭam* with *vaṭa*, *veḷi* and *veḷḷi* with *veḷ*, and *muruka-* with *muruku*.

The ladder merges, in this order: L vowel length and gemination; A aspiration and secondary articulation; V voicing; R retroflex and alveolar with dental; S sibilants; N nasals other than *m*; Q liquids; E mid with high vowels. In compounds of the Tamil Lexicon a first member also receives its sandhi bases: a final *-a* adds *-am* and *-aṉ* (*vaṭa-* < *vaṭam*, *muruka-* < *murukaṉ*), and a final *ṇ, ṉ, ṅ, ñ, n, ṭ, ṟ* adds *ḷ, l, m, m, m, ḷ, l* (*veṇ-* < *veḷ*). Sandhi restoration identifies a word; it is applied under every tolerance.

The synthetic checks place Parpola's own matches on this scale: *mīṉ* "fish" / *mīṉ* "star", *muruku* / *muruku*, *katir* / *katir*, *piḷḷai* / *piḷḷai* and *vēḷ* / *veḷ* need only T0; *veṇ* / *vēḷ* and *vaṭam* / *vaṭa* need sandhi restoration; *veḷi* / *veḷ*, *veḷḷi* / *vēḷ* and *muruka-* / *muruku* need T1s.

## Inputs

| Source | Access | Use | Rights observed |
|---|---|---|---|
| Burrow and Emeneau, *A Dravidian Etymological Dictionary*, 2nd ed. (1984), DSAL edition | `dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page=1..514` | Dravidian lexicon | Copyright 1984 Oxford University Press, no storage without permission; local-only |
| Turner, *A Comparative Dictionary of the Indo-Aryan Languages* (1962–1985), DSAL edition | `soas_query.py?page=1..836` | Indo-Aryan lexicon | rights-unverified; local-only |
| University of Madras, *Tamil Lexicon* (1924–1936), DSAL edition | `tamil-lex_query.py?page=1..~4360` | Old Tamil compounds | rights-unverified; local-only |
| Oracc, ePSD2 JSON (`json/epsd2.zip`, glossary timestamp 2023-01-19) | `oracc.museum.upenn.edu` | Sumerian lexicon | CC0 declared in the JSON |
| Rau, *Munda cognate set with proto-Munda reconstructions* (2019) | Zenodo 10.5281/zenodo.3380874 | Munda lexicon | CC0 |
| Backstrom and Radloff (1992) via Lexibank `backstromnorthernpakistan` v1.1 | GitHub release | Burushaski wordlist | CC BY 4.0 |
| Concepticon 3.4.0, `concepticon.tsv` | GitHub tag v3.4.0 | concept pools | CC BY 4.0 |
| NoRaRe 1.1, Brysbaert et al. (2014) concreteness mapping | GitHub tag v1.1 | picturability filter | CC BY-NC 4.0; values local |
| Project Madurai Unicode texts of the Eṭṭuttokai and nine Pattuppāṭṭu poems | `projectmadurai.org/pm_etexts/utf8/` | Old Tamil word frequency | free distribution with header; local |

Every request is logged with URL, status, bytes, SHA-256 and UTC time in `data/raw/2026-10-21-rebus-base-rate/sources-v1/<source>/requests.jsonl`, and `SOURCES.json` in this package aggregates the record. No full Munda or Burushaski dictionary in machine-readable form was found: Berger's and Tiffou's Burushaski dictionaries and Bodding's Santali dictionary are print or image editions. The Munda and Burushaski lexicons are therefore comparative wordlists of a few hundred concepts, and we compare them with the full dictionaries only through the one-word-per-concept rate and the word-pair collision defined below.

## Lexemes and attestation

Each language supplies lexemes with forms, English gloss items and an attestation flag that plays the part of Parpola's two-subgroup rule.

- **Dravidian.** One lexeme per DEDR entry. Its forms are the headword forms of the Tamil block, or of the first-listed language when the entry has no Tamil. Its gloss items are the glosses of every language in the entry, since Parpola takes the meaning "squirrel" of *piḷḷai* from Central Dravidian (p. 26). Attested means reflexes in at least two of South Dravidian I (with Tulu), South Dravidian II, Central and North Dravidian. A word-level variant, one lexeme per Tamil word with only its own gloss, is reported as a sensitivity.
- **Indo-Aryan.** One lexeme per CDIAL entry, with the Old Indo-Aryan headword as its form and every quoted gloss outside bracketed notes. Attested means reflexes in at least two of the zones Dardic, Northwestern, Pahari, Central, Eastern, Southern and Romani.
- **Sumerian.** One lexeme per ePSD2 lemma of the parts of speech N, V/t, V/i, AJ, AV and NU whose citation form is a reading (no sign names), with the meanings of its senses. Attested means at least two corpus instances.
- **Munda.** One lexeme per cognate set of Rau (2019), with the Santali form (else Mundari, else Ho) and the set's gloss. Attested means forms in both North and South Munda.
- **Burushaski.** One lexeme per Concepticon concept in Backstrom's list, with the forms of the Hunza variety that has most entries and matching by Concepticon ID. Attested means forms in at least two of the Hunza, Nagar and Yasin dialects.

A gloss item is one comma-, semicolon- or colon-separated part of a gloss, lower-cased, with parenthetical and bracketed notes removed and a leading "to be", "to", "be" or "the" dropped. A lexeme expresses a concept when one of its items equals the concept's key or the key with *-s* or *-es*. Items with an article, such as "a fish", name a kind and do not match.

## Concept pools

The pools are fixed in `pools-v1.json`, written by `code/pools.py` from Concepticon and NoRaRe. Picturable nouns are Concepticon concept sets of the category Person/Thing in eleven concrete semantic fields (animals, the body, agriculture and vegetation, the physical world, food and drink, basic actions and technology, clothing and grooming, the house, warfare and hunting, motion, possession) whose English word is rated at least 4.5 for concreteness and is dominantly a noun: 751 concepts. Meanings suitable for names fall in six classes: deity (13 listed sets), celestial body (14), colour (26 sets defined by colour), direction (13), kinship (102 sets of the kinship field, category Person/Thing) and quality (268 other property sets): 436 concepts. The pools are disjoint, and concept sets joined with "OR" are excluded.

## Measurement 1: single homophones

For each lexicon and tolerance, an evaluable pair is a picturable concept and a name concept that both have at least one attested lexeme. The pair is a homophone pair when some form of a picture lexeme and some form of a name lexeme coincide under the tolerance. We report:

- the rate over all lexemes, as Parpola's procedure permits any attested word;
- the homonym rate, counting only coincidences between two different lexemes, which excludes polysemy such as *mīṉ* "fish, star" in one DEDR entry;
- the rate with one lexeme per concept, the one attested in most languages (Sumerian: most instances);
- the word-pair collision, the probability that two random attested lexemes share their first form;
- the rate by name class.

Intervals are 95% percentile intervals from 2,000 bootstrap replicates that resample picture and name concepts independently (seed 20261021).

**Prediction P1 and pass rule.** The Dravidian rate over all lexemes under T0s lies between 0.5 and 2 times the median of the rates of the two other full dictionaries, Indo-Aryan and Sumerian. The Munda and Burushaski wordlists are reported beside them and do not enter the rule.

## Measurement 2: interlocks

The interlock searches use the two-member compounds of the Tamil Lexicon. The Lexicon romanises compounds with hyphens and writes a sandhi consonant between members as a separate segment (*aṅkāṭi-k-kūli*); one-consonant segments are dropped and entries with exactly two remaining members are kept. A compound belongs to a word W as first member when the T1s stem of one of its first member's sandhi bases equals the T1s stem of W, and as second member when the T1s stem of its second member does. Anchoring by stem identifies the word and is the same under every tolerance.

For two words W1 and W2, A(W1) holds the second members of compounds W1-X and B(W2) the first members of compounds X-W2. The search succeeds when a member of A and a member of B coincide under the tolerance, with members that coincide with W1 or W2 themselves excluded. The primary tolerance is T0s, the stated rule with sandhi restoration, under which Parpola's *Muruka-vēḷ* and *veṇ-mīṉ* meet in *veḷ*; T1s is reported beside it.

Five searches reproduce the interlocks of Parpola (2010):

| ID | Parpola's interlock | Search |
|---|---|---|
| I1 | *Muruka-vēḷ* and *veṇ-mīṉ* share *veḷ* (pp. 26–27) | shared member of A(*muruku*) and B(*mīṉ*) |
| I2 | *vaṭam* "banyan" ~ *vaṭa* "north", *vaṭa-mīṉ* (pp. 19–20) | a Tamil word for the banyan coincides with a member of B(*mīṉ*) |
| I3 | *piḷḷai* "squirrel", *Muruka-p-piḷḷai* (pp. 25–26) | a Tamil word for the squirrel coincides with a member of A(*muruku*) |
| I4 | *aṟu-mīṉ*, *eḻu-mīṉ* (p. 17), and *mū-mīṉ* from Parpola (2005) as cited in the fish-context protocol | number of the numerals three, six and seven with a compound in B(*mīṉ*) |
| I5 | *katir* "spindle" ~ *katir* "shine", *katir-k-kaṭavuḷ* (pp. 21–22) | a Tamil word for the spindle coincides with a member of B(*kaṭavuḷ*) |

For Parpola's pictures the Tamil words are the words he names (*vaṭam*; *piḷḷai* and *aṇil*; *katir*) together with the Tamil forms of every attested DEDR entry glossed with the picture's key ("banyan", "squirrel", "spindle"). For a random picturable concept they are the Tamil forms of every attested DEDR entry glossed with its key. A restricted version of I1 follows Parpola's narrower sets: A limited to compounds glossed as names of Murukan or Skanda, B to compounds glossed as stars, planets, asterisms or fish, by fixed regular expressions in `code/run_interlocks.py`.

**Replacement words.** Candidates are Tamil Lexicon headwords of one member, marked as nouns, without the Lexicon's asterisk for words of foreign origin, whose T0 form occurs among the Tamil forms of an attested DEDR entry, with one candidate per T1s stem. Each candidate has its compounding productivity (the number of compounds anchored on it as first member, or as second member) and its frequency, the number of word tokens in the Sangam corpus that begin with its Tamil-script stem. For W1 = *muruku* we take the 50 candidates nearest in standardised (log(1 + first-member productivity), log(1 + frequency)); for W2 = *mīṉ* and W3 = *kaṭavuḷ* the same with second-member productivity. The real word is excluded from its own pool. Pools of 25 and 100 are sensitivities.

**Nulls.**

- N1 (I1). All 50 × 50 pairs of replacement words for W1 and W2 are enumerated exactly. We report the share of pairs with a shared member, a 95% interval from 2,000 bootstrap replicates over pool words, the mean number of shared members, and the shares with only W1 or only W2 replaced.
- N2 (restricted I1). In 10,000 draws a pair of replacement words is drawn and their compound sets are subsampled to the sizes of Parpola's restricted sets.
- Pictures (I2, I3, I5). The share of picturable concepts with Tamil words whose words complete the search, first with Parpola's W and then averaged over the replacement pool.
- I4. The distribution, over the W2 pool, of the number of the three numerals with a compound.
- Network. In 10,000 draws W1, W2 and W3 are replaced from their pools and the three pictures by three distinct random picturable concepts. A draw reproduces the network when every interlock that holds for Parpola's own words also holds. We also report the distribution of the number of interlocks held.

Draws use the seed 20261021.

## Decision rules

- **Kill.** If the N1 share for I1 under T0s with pools of 50 exceeds 0.20, the *veḷ* interlock is dead as evidence for the Dravidian reading.
- **P2, network.** Parpola's network passes if the share of network draws that reproduce every interlock holding for his words is below 0.01 under T0s. It fails otherwise.
- When the share r for an interlock lies at or below 0.20, the interlock can raise the odds of the Dravidian reading by at most a factor of 1/r, and we report that factor.
- If an interlock does not hold for Parpola's own words in the Tamil Lexicon, we report that the encoded procedure does not reproduce it from this source, leave it out of the network requirement and still measure its null rate.
- P1 is decided as stated under Measurement 1.

No Indus reading changes credence on these results alone. The results set an upper bound on what the interlocks can contribute to the identification of the language, and a conjecture card is drafted only if the results support a claim stated at full strength.

## Order of work and stopping

1. Acquisition and the source manifest (`SOURCES.json`).
2. Parsing into local tables: `parse_dedr.py`, `parse_cdial.py`, `parse_tamil_lex.py`, `extract_epsd2.py`; pools with `pools.py`.
3. `selftest.py` into `selftest-v1/` and `python -m bench selftest` into `bench-selftest-v1.json`; both must pass.
4. Freeze: `FREEZE.json` records the SHA-256 of this protocol, of every script and of every input table.
5. `run_homophones.py` and `run_interlocks.py` into `results-v1/`.
6. `verify.py`, an independent reimplementation of the I1 search and null and of the Dravidian single-homophone rate, into `verification-v1.json`.
7. Report, retrospective, attempt entry, data records and, if supported, a conjecture card.

No step stops on a favourable outcome. Every output is written to a new path, and scripts refuse to overwrite. A parser or code repair after the freeze is recorded in a dated amendment with the hashes of the tables before and after, and any result already computed is kept beside the repaired one.

## Data handling

Raw pages, archives, parsed tables, compound lists and word-level examples stay in `data/raw/2026-10-21-rebus-base-rate/`. The package tracks our code, this protocol, the concept pool definitions without concreteness values, the source manifest and aggregate JSON results whose word content is limited to Parpola's own published words and the replacement headwords.

## References

Parpola, Asko. 2010. *A Dravidian solution to the Indus script problem*. Chennai: World Classical Tamil Conference. Local copy `data/raw/2026-10-20-fish-context/sources-v1/parpola2010-attempt1.txt`.
Brysbaert, Marc, Amy Beth Warriner and Victor Kuperman. 2014. Concreteness ratings for 40 thousand generally known English word lemmas. *Behavior Research Methods* 46: 904–911.
Krishnamurti, Bhadriraju. 2003. *The Dravidian Languages*. Cambridge University Press.
Masica, Colin P. 1991. *The Indo-Aryan Languages*. Cambridge University Press.
