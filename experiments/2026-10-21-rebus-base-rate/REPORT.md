# REBUS-BASE-RATE-2026-10-21: how often does a rebus interlock arise by chance?

Status class: `frozen-evaluation`. The protocol, code and inputs were frozen before the real runs ([FREEZE.json](FREEZE.json), protocol SHA-256 `32f3dff6…ec25`); one code defect found by the independent check was repaired under [Amendment 1](AMENDMENT-1.md), and both versions of the results are kept. Verification tier: submitted.

Date and contributors: 21 October 2026. Claude (Opus 5.5, `claude-opus-5-5`, Claude Code desktop harness), in a session started from the session that wrote the Parpola direction note.

## Results

We encoded Asko Parpola's homophone procedure as a program and asked how often it succeeds when the words he started from are replaced by random words of the same kind. Three results stand out.

The *veḷ* interlock is dead as evidence under the frozen rule. Parpola found that the compounds *Muruka-vēḷ* and *veṇ-mīṉ* share a member, *veḷ*, and read the two-long-strokes sign as that word. In the Madras *Tamil Lexicon*, 7 two-member compounds begin with *muruku* and 82 end in *mīṉ*. When both words are replaced by native nouns of the same compounding productivity and Sangam frequency, the two compound sets share a member in 30.5% of the 2,500 pairs (95% bootstrap interval 25.2–36.2%; [interlocks.json](results-v2/interlocks.json) `#/null/I1_T0s/K50`). That is above the 20% kill threshold, and it stays above it for pools of 25 and 100 words (40.3% and 28.7%) and under Parpola's looser practised tolerance (52.8%). His own pair even produces a second, irrelevant shared member: *murukkam-puḷi* "citric acid" and *puḷi-mīṉ* "fish soured with tamarind" meet in *puḷi* ([interlocks.json](results-v2/interlocks.json) `#/real/I1_T0s/shared`).

Parpola's network of interlocks passes the frozen network rule, and its strength comes entirely from the conjunction. Four of the five interlocks we encoded hold for his words in the *Tamil Lexicon*: *veḷ* (I1), *vaṭa-mīṉ* from the banyan (I2), the numeral compounds *mu-m-mīṉ*, *aṟu-mīṉ* and *eḻu-mīṉ* (I4) and *katir-k-kaṭavuḷ* from the spindle (I5). *Muruka-p-piḷḷai* (I3), which Parpola takes from modern Jaffna names, is not in the Lexicon. With every word and picture replaced at random, all four hold together in 0.44% of 10,000 draws (95% interval 0.33–0.59%; `#/null/network_T0s`), below the 1% threshold. Under the practised tolerance the rate is 2.2% and the network would fail. Most links are cheap on their own. With *mīṉ* kept, 43% of random picturable concepts complete the banyan link, and 25% do when the head noun is replaced as well; 11% complete the spindle link; and 36% of random head nouns of *mīṉ*'s productivity take at least one of the three numerals. The numeral link at its full depth is the exception: none of the 50 random head nouns takes all three numerals, because Tamil names star groups by counting their stars.

Single homophones are easier to find in Dravidian than in the other full dictionaries, so the first prediction fails. A picturable noun and a meaning suitable for a name have a homophone in the *Dravidian Etymological Dictionary* for 2.31% of evaluable pairs (1.95–2.69%), against 1.50% in Turner's Indo-Aryan dictionary and 0.45% in the Sumerian ePSD2 ([homophones.json](results-v2/homophones.json) `#/prediction_single_homophone`). The Dravidian rate is 2.37 times the median of the other two, outside the frozen band of 0.5 to 2. The high rate has two sources. Tamil forms are short, so two random Tamil lexemes coincide seven times as often as two Old Indo-Aryan headwords. And Parpola allows a meaning to be taken from any cognate in a DEDR entry: restricting each Tamil word to its own gloss lowers the Dravidian rate eightfold, to 0.29%.

## Interlocks in detail

| Interlock | Holds for Parpola's words | Chance rate with random words, stated rule (T0s) | Practised rule (T1s) | Largest odds factor (1 / rate) |
|---|---|---|---|---|
| I1 *Muruka-vēḷ* / *veṇ-mīṉ*, both words replaced | yes (*veḷ*, *puḷi*) | 30.5% | 52.8% | 3.3 |
| I1, only *muruku* replaced | | 44% | 64% | |
| I1, only *mīṉ* replaced | | 26% | 54% | |
| I1 restricted to Parpola's semantic sets, by size | frozen sets: no | 3.9% | 9.0% | |
| I2 banyan word ~ first member of X-*mīṉ* | yes (*vaṭa-mīṉ*, *peru-mīṉ*) | 42.7% with *mīṉ*; 25.1% with a random head | 55.9%; 40.9% | 4.0 |
| I3 squirrel word ~ second member of *muruku*-X | no | 6.1% with *muruku*; 4.8% with a random word | 8.4%; 9.2% | |
| I4 numerals 3, 6, 7 with *mīṉ* | all three | 0 of 50 random heads take all three; 36% take at least one | | 2.8 for one numeral |
| I5 spindle word ~ first member of X-*kaṭavuḷ* | yes (*katir-k-kaṭavuḷ*) | 7.8% with *kaṭavuḷ*; 10.8% with a random word | 14.9%; 21.1% | 9.2 |
| Network I1, I2, I4, I5 together | yes | 0.44% | 2.2% | 227 (T0s), 45 (T1s) |

Rates for I2, I3 and I5 are the share of the 490 picturable concepts that have attested Tamil words in DEDR and complete the link ([interlocks.json](results-v2/interlocks.json) `#/null/pictures_T0s`, `#/null/pictures_T1s`). The I4 distribution is at `#/null/I4`; the network distributions are at `#/null/network_T0s` and `#/null/network_T1s`. Odds factors are the reciprocals of the random-word rates, the largest amount by which a link that holds can raise the odds of the reading over the random-word alternative ([exploratory.json](exploratory-v1/exploratory.json) `#/E4_largest_odds_factor`).

The frozen restricted search failed for a reason in the source rather than in Parpola's argument. The *Tamil Lexicon* glosses *muruka-vēḷ* only by cross-reference ("See" followed by a Tamil headword), so the fixed expression for names of Murukan admitted just *muruka-k-kaṭavuḷ*. After the outcome we added *muruka-vēḷ* by hand: the restricted search then finds *veḷ*, and random words whose compound sets are cut to the same sizes (2 and 55) share a member in 7.8% of draws under the stated rule and 16.6% under the practised one ([exploratory.json](exploratory-v1/exploratory.json) `#/E1_restricted_with_muruka_vel`). This is a post-outcome estimate. It shows that the kill rests on the unrestricted search that the protocol fixed; at the narrower depth Parpola describes, the *veḷ* link is worth an odds factor of about 13 at most.

## Single homophones in detail

| Lexicon | Attested lexemes | Picture / name concepts found | Words per found concept | Rate, all words (95%) | Homonyms only | One word per concept | Two random lexemes share a form |
|---|---|---|---|---|---|---|---|
| Dravidian, DEDR (Tamil-headed) | 3,633 | 509 / 331 | 4.8 / 6.8 | 2.31% (1.95–2.69) | 1.42% | 0.27% | 2.5 × 10⁻⁴ |
| Dravidian, DEDR word level | 11,102 | 410 / 227 | 3.1 / 4.3 | 0.29% (0.20–0.38) | 0.22% | 0.03% | 1.3 × 10⁻⁴ |
| Indo-Aryan, CDIAL (Old Indo-Aryan headwords) | 7,414 | 563 / 346 | 7.7 / 10.9 | 1.50% (1.24–1.79) | 0.58% | 0.07% | 3.6 × 10⁻⁵ |
| Sumerian, ePSD2 | 5,843 | 374 / 177 | 2.5 / 2.9 | 0.45% (0.32–0.61) | 0.33% | 0.12% | 2.1 × 10⁻⁴ |
| Munda, Rau 2019 (Santali forms) | 112 | 20 / 9 | 1 / 1 | 0 of 180 pairs | 0 | 0 | 1.6 × 10⁻³ |
| Burushaski, Backstrom 1992 (Hunza) | 204 | 65 / 40 | 1 / 1 | 1 of 2,600 pairs | 1 | 1 | 2.9 × 10⁻⁴ |

All rows use the scaled rule T0s ([homophones.json](results-v2/homophones.json) `#/languages`). Old Indo-Aryan and Sumerian already have a per-segment collision probability above that of Tamil under the stated rule (0.119 and 0.081 against 0.076), so the scaling merged nothing for them; the Munda and Burushaski transcriptions, rich in phonetic detail, needed every step of the ladder. The practised rule doubles the Dravidian rate to 4.88% and raises the others less (Indo-Aryan to 1.71%, Sumerian to 0.68%).

Three quantities separate language from documentation. The chance that two random lexemes share a form is about the same for Tamil and Sumerian and seven times lower for Old Indo-Aryan, whose headwords are longer. The number of words a dictionary offers for one concept is highest in Turner and lowest in ePSD2. The rate with one word per concept, which removes that difference, still ranks Dravidian first (0.27%, against 0.12% and 0.07%). Dravidian therefore supplies single homophones more readily than the other candidates measured here, and a single Dravidian homophone is correspondingly weaker evidence. The Munda and Burushaski wordlists cover too few concepts for a comparison: their intervals include every rate in the table.

The Dravidian rate is about the same for every class of name meaning: deities 2.0%, celestial bodies 1.4%, colours 2.6%, directions 3.3%, kinship 1.5% and qualities 2.5% (`#/languages/dravidian-dedr/tolerances/T0s/by_name_class`).

## An exploratory observation on the numerals

Of the numerals one to ten, only three, five, six and seven form an attested compound with *mīṉ* in the *Tamil Lexicon*: *mu-m-mīṉ*, *ai-m-mīṉ*, *aṟu-mīṉ* and *āṟā-mīṉ*, and *eḻu-mīṉ*, each an asterism counted by its stars ([exploratory.json](exploratory-v1/exploratory.json) `#/E2_numerals_with_min`). Random head nouns take a compound with "two" in 20% of cases, but *mīṉ* has none. On the confirmation seals of the fish-context study two strokes precede a fish in 77 of 102 cases ([direction note](../../knowledge/directions/parpola-forward-2026-10-20.md), from the preliminary [fish-context results](../2026-10-20-fish-context/confirmation-v1/results.json)). Parpola reads that pair as the separate sign *veḷ*, which gives "white star", Venus, and that reading rested on the interlock this study kills. Without it, the commonest fish compound on the seals has no star name in the *Tamil Lexicon*. This was examined after the outcome and is not a frozen result.

## Why this is new work

The [key calibration](../../knowledge/directions/key-calibration-2026-10-12.md) of 12 October showed that dictionary fits mean little until they are set against random strings, and the Bronze Age comparison showed equality-pattern matches fitting Indus faces in four unrelated languages. Neither measured the chance rate of the evidence Parpola actually offers: a homophone between a picture word and a target meaning, and a member shared by two attested compounds. The fish-context study tested the Indus side of his asterism reading; this study tests the lexical side and reads no Indus text.

## Inputs and dependence

The lexicons are the DSAL editions of DEDR (514 pages, 5,623 entries), Turner's CDIAL (836 pages, 15,418 entries) and the *Tamil Lexicon* (4,400 pages, 117,803 entries, 56,154 two-member compounds), the ePSD2 glossary from Oracc (15,940 lemmas, 7,875 of them common words with readable citation forms), Rau's Munda cognate sets (113 with a Santali, Mundari or Ho form) and Backstrom and Radloff's Burushaski wordlists through Lexibank (204 concepts). Concept pools come from Concepticon 3.4.0 and the Brysbaert concreteness norms in NoRaRe 1.1; Sangam word frequencies from 17 Project Madurai texts. [SOURCES.json](SOURCES.json) records every file with its URL, bytes, SHA-256, retrieval time and observed rights. DEDR and Turner carry all-rights-reserved notices and the *Tamil Lexicon* edition a CC BY-NC-ND 2.0 licence, so all raw pages and parsed tables stay local.

Everything depends on the gloss conventions of each dictionary and on our parsers. The concept matching accepts only a gloss item equal to the concept's key, so a dictionary that glosses "banyan tree" instead of "banyan" loses that concept; the counts of concepts found per lexicon show how much each one loses. The Munda and Burushaski sources are comparative wordlists, not dictionaries: no machine-readable dictionary of either was found. The interlock searches use one Tamil dictionary of the 1920s and 1930s, which records literary, colloquial and loan compounds together; Parpola also drew on Old Tamil texts and on modern names, which is why I3 fails here.

## Protocol before outcome

[PROTOCOL.md](PROTOCOL.md) fixed the three tolerances, the lexeme and attestation rules for each language, the gloss matching, the two concept pools (751 picturable nouns, 436 name meanings; [pools-v1.json](pools-v1.json)), the replacement pools (the 50 nearest native nouns in compounding productivity and Sangam frequency), the nulls with their draw counts and seed, and three decision rules: the kill at 20%, the network pass below 1% and the single-homophone band of 0.5 to 2 times the median of the other full dictionaries. The synthetic selftest checked the encoding against Parpola's own pairs, planted homophones and interlocks, and matched the shared-member null to its exact hypergeometric value (observed 0.161 against 0.168; [selftest-v2](selftest-v2/selftest.json)).

## Commands and outputs

Run from the repository root with Python 3.13 and NumPy 2.2.6.

```text
python experiments/2026-10-21-rebus-base-rate/code/acquire.py dedr|cdial|tamil-lex|files
python -I experiments/2026-10-21-rebus-base-rate/code/extract_epsd2.py
python experiments/2026-10-21-rebus-base-rate/code/parse_dedr.py
python experiments/2026-10-21-rebus-base-rate/code/parse_cdial.py
python experiments/2026-10-21-rebus-base-rate/code/parse_tamil_lex.py
python experiments/2026-10-21-rebus-base-rate/code/pools.py
python experiments/2026-10-21-rebus-base-rate/code/manifest.py experiments/2026-10-21-rebus-base-rate/SOURCES.json
python experiments/2026-10-21-rebus-base-rate/code/selftest.py experiments/2026-10-21-rebus-base-rate/selftest-v2
python -m bench selftest --out experiments/2026-10-21-rebus-base-rate/bench-selftest-v1.json
python experiments/2026-10-21-rebus-base-rate/code/freeze.py
python experiments/2026-10-21-rebus-base-rate/code/run_homophones.py experiments/2026-10-21-rebus-base-rate/results-v2
python experiments/2026-10-21-rebus-base-rate/code/run_interlocks.py experiments/2026-10-21-rebus-base-rate/results-v2
python experiments/2026-10-21-rebus-base-rate/code/verify.py experiments/2026-10-21-rebus-base-rate/results-v2 experiments/2026-10-21-rebus-base-rate/verification-v2.json
python experiments/2026-10-21-rebus-base-rate/code/exploratory.py experiments/2026-10-21-rebus-base-rate/results-v2 experiments/2026-10-21-rebus-base-rate/exploratory-v1
```

The bootstrap and draw seed is 20261021 (20261022 for the exploratory draws). Outputs: [results-v1](results-v1/) (frozen code), [results-v2](results-v2/) (repaired code, read here), [verification-v1.json](verification-v1.json), [verification-v2.json](verification-v2.json), [exploratory-v1/exploratory.json](exploratory-v1/exploratory.json), [selftest-v1](selftest-v1/selftest.json), [selftest-v2](selftest-v2/selftest.json) and [bench-selftest-v1.json](bench-selftest-v1.json). Word lists derived from the dictionaries are in local detail files whose paths and hashes the result files record.

## Challenges and repairs

The independent reimplementation matched the real search but drew different replacement pools. The cause was a vowel set that included "y", which made the stem rule cut the final consonant of 1,520 Tamil words such as *nāy* "dog"; [Amendment 1](AMENDMENT-1.md) records the repair, and every decision is the same in both versions (the *veḷ* null rate is 30.8% in v1 and 30.5% in v2, the network rate 0.53% and 0.44%). The [retrospective](RETROSPECTIVE.md) describes the acquisition problems, the parser repairs and the selftest failures that led to fixes before the freeze.

## Decision and next evidence

Within this protocol the *veḷ* reading of the two-long-strokes sign has no lexical support beyond chance: its interlock appears for random word pairs in about a third of cases, and at the narrower depth Parpola describes it is worth an odds factor of about 13 at most. A future argument for *veḷ* needs evidence other than the compound search, such as the stroke-length measurements proposed in the direction note. Parpola's single homophones are cheaper in Dravidian than in Indo-Aryan or Sumerian, so a single Dravidian rebus reading is weaker evidence than the same reading would be in those languages. His five-template network is rare for random words, and it is the only lexical evidence this study leaves standing.

Do not rerun this search unchanged on the same Tamil dictionary. A revisit is justified by a second Tamil lexicon with compounds (Winslow 1862 and Kadirvelu Pillai are on DSAL), a machine-readable Munda or Burushaski dictionary, or a blind list of templates frozen before any Tamil compound is looked up.

## The boldest reading and the test that would decide it

Parpola's case is a crossword whose individual clues are cheap. Each of his rebus interlocks that holds in the *Tamil Lexicon* is something the Lexicon supplies for random words of the same productivity in 8–43% of cases, and the two-long-strokes sign read as *veḷ* carries no weight. The numeral compounds of *mīṉ* are not chance, but they show only that *mīṉ* means "star", which nobody disputes; they bear on the script through the stroke counts before the fish, where two, the count with no star compound in the *Tamil Lexicon*, dominates. Only the conjunction is rare: four of his interlocks hold together for random words in 0.44% of draws, so his 2010 network raises the odds of a Dravidian reading by up to a factor of about 230, provided the five templates in the paper are all he tried. With per-template chance rates near 0.21, four successes become likely by chance once about 17 templates have been tried, and pass 5% once 8 have ([exploratory.json](exploratory-v1/exploratory.json) `#/E3_template_multiplicity`). The network therefore measures either the language of the script or the number of templates tried, and its value lies between a factor of 230 and nothing.

The test that decides it is a blind template test. Freeze a list of at least 20 Indus sign pairs not used by Parpola, each with the picture identification his 1994 sign list gives, before any Tamil compound is looked up. Then count how many yield an attested *Tamil Lexicon* interlock under his word assignments and under random words matched on productivity and frequency, with the code of this package. If the language of the script is Dravidian and the identifications are right, his assignments should succeed at least three times as often as random words. A ratio near one would show that the network measured the density of the Tamil lexicon and the search behind it. The draft conjecture [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md) states the second outcome as our working claim.

## Review and verification

[verification-v2.json](verification-v2.json) recomputes, without importing the measurement code, the compound count, the real *veḷ* search, the sizes of both compound sets, both replacement pools, the *veḷ* null rate and the Dravidian homophone rate; all seven agree with results-v2. The synthetic selftest and the shared bench selftest pass. No other contributor has reproduced or reviewed this package.
