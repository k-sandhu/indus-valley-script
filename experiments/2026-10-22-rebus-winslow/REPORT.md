# REBUS-WINSLOW-2026-10-22: does the veḷ search find chance interlocks in Winslow's dictionary?

Status class: `frozen-evaluation`. The protocol, code and inputs were frozen before the run ([FREEZE.json](FREEZE.json), protocol SHA-256 `84d42ce3a35b6bad1701f0252526cad5c43ca218bb46101e478f7262d4ea25ac`), and the result was computed once with the frozen code. Analyses chosen after the outcome are in a separate, labelled output. Verification tier: submitted.

Date and contributors: 22 October 2026. Claude (Opus 5.5, `claude-opus-5-5`, Claude Code desktop harness), in a session started from the session that wrote C-0014.

## Results

Prediction P2 of [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md) fails under its frozen rule, because Winslow's dictionary does not contain the interlock that the search starts from. In Miron Winslow's *A comprehensive Tamil and English dictionary of high and low Tamil* (1862) no two-member compound begins with *muruku*, against 7 in the Madras *Tamil Lexicon*, and 29 have *mīṉ* as last member, against 82. The replacement words for *muruku*, matched on its productivity and Sangam frequency, are therefore 50 nouns with no compound as first member, and none of the 2,500 replacement pairs can share a member: the rate is 0.0 (Wilson 95% interval 0–0.15%; [interlocks.json](results-v1/interlocks.json) `#/null/I1_T0s/K50`). P2 required a rate above 0.20. By the rule of C-0014 the failure lowers its credence by 0.10, from 0.55 to 0.45. An independent recomputation agrees on every number ([verification-v1.json](verification-v1.json)).

Neither compound behind Parpola's reading of the two-long-strokes sign as *veḷ* is a Winslow entry. The dictionary has no *Muruka-vēḷ*, no *veḷḷi-mīṉ*, and *veṇ-mīṉ* only as a word inside one definition; the name of Skanda that Winslow forms on *vēḷ* is செவ்வேள் *cevvēḷ*, with *cem* "red" ([exploratory.json](exploratory-v1/exploratory.json) `#/X4_forms_ending_in_min`). The search for Parpola's own words therefore fails in Winslow under both tolerances (`#/real/I1_T0s`). Of the five interlocks of Parpola (2010) that the 21 October study encoded, two hold in Winslow: *vaṭa-mīṉ* from the banyan (I2) and the numeral compound *aṟu-mīṉ* (I4, six only; *mu-m-mīṉ* is an entry our parser did not split, and there is no *eḻu-mīṉ*). The squirrel link (I3) and the spindle link *katir-k-kaṭavuḷ* (I5) do not hold. Random words reproduce the two surviving links together in 3.9% of 10,000 draws (95% interval 3.5–4.3%; `#/null/network_T0s`), so in Winslow Parpola's network can raise the odds of a Dravidian reading by a factor of 26 at most, against 227 in the Lexicon.

After the outcome we asked what the search gives in Winslow once the first word has compounds. With the pool for the first word matched to the Lexicon's 7 first-member compounds of *muruku* and the pool for the second word as frozen (29 compounds), random pairs share a member in 14.0% of cases (bootstrap 95% interval 10.3–18.2%; 29.4% under the practised tolerance T1s). The Lexicon, with pools matched to the same two targets, gives 16.6% (12.9–20.6%) ([exploratory.json](exploratory-v1/exploratory.json) `#/X3_equal_set_sizes`). At equal compound-set sizes the two dictionaries make chance interlocks at nearly the same rate. The Lexicon's 30.5% of 21 October comes from the size of its compound set for *mīṉ*, 82 against Winslow's 29, and Winslow's 0% from its lack of any compound of *muruku*: one dictionary recorded the compounds that the search needs and the other did not.

## The two dictionaries side by side

| Quantity | Winslow (1862) | *Tamil Lexicon* (1924–1936) |
|---|---|---|
| Two-member compounds in the parsed table | 18,426 | 56,154 |
| Replacement candidates (native one-member nouns in DEDR) | 2,319 | 4,134 |
| Compounds *muruku*-X / X-*mīṉ* / X-*kaṭavuḷ* | 0 / 29 / 4 | 7 / 82 / 23 |
| I1 *veḷ* search for Parpola's words | does not hold | holds (*veḷ*, *puḷi*) |
| I1 null, both words replaced, pools of 50, T0s | **0.0** | **30.5%** |
| I1 null, pools of 25 / 100; T1s | 0 / 0; 0 | 40.3% / 28.7%; 52.8% |
| I1 null at equal targets (7 and 29 compounds), post-outcome | 14.0% | 16.6% |
| I2 banyan link for Parpola's words | *vaṭa-mīṉ* | *vaṭa-mīṉ*, *peru-mīṉ* |
| I2 chance, with *mīṉ* / with a random head | 13.9% / 10.9% | 42.7% / 25.1% |
| I3 squirrel link | does not hold; 0% / 0% | does not hold; 6.1% / 4.8% |
| I4 numerals three, six, seven with *mīṉ* | six | all three |
| I4 random heads taking at least one numeral | 30% | 36% |
| I5 spindle link | does not hold; 0.8% / 2.5% | *katir-k-kaṭavuḷ*; 7.8% / 10.8% |
| Network: links required, chance rate T0s / T1s | I2, I4: 3.9% / 8.3% | I1, I2, I4, I5: 0.44% / 2.2% |

The Winslow column is [results-v1/interlocks.json](results-v1/interlocks.json) (`#/real`, `#/null/I1_T0s`, `#/null/I1_T1s`, `#/null/pictures_T0s`, `#/null/I4`, `#/null/network_T0s`, `#/null/network_T1s`) and, for the equal-target row, [exploratory.json](exploratory-v1/exploratory.json). The Lexicon column is the 21 October [results-v2/interlocks.json](../2026-10-21-rebus-base-rate/results-v2/interlocks.json) and its report. Picture rates are the share of the 490 picturable concepts with attested Tamil words in DEDR that complete the link. The result file also carries two fields computed by the frozen code under the rules of the 21 October protocol, `killed: false` and `network_pass: false`; they are that study's rules evaluated on Winslow and are not decisions of this protocol.

## How far the parse can be trusted

Winslow prints compounds without hyphens and without romanisation, nested under the member it treats as their root, so we recovered the boundary from the nesting and from Tamil sandhi ([PROTOCOL.md](PROTOCOL.md), "Parsing rule"). Where the same Tamil form is a two-member compound in both dictionaries, our members match the Lexicon's hyphenation in 98.1% of 11,784 cases, and we recover 75.4% of the Lexicon's compounds among Winslow's sub-entries ([parser-validation-v1.json](parser-validation-v1.json)).

The missed quarter does not change the decision. Among all Winslow entries whose Tamil form contains முருக, two have *muruku* as first member under the frozen stem rule and were missed by the parser: முருக்கம்பூ *murukkam-pū*, the flower of the *murukku* tree, and முருக்கஞ்செத்தல் *murukkañ-cettal*, its dry wood, both formed with the *-am-* increment that our sandhi forms do not cover. A complete parse would therefore give A(*muruku*) two compounds. The chance rate grows with that number but stays far below 0.20: it is 2.8% (1.7–4.2%) with pools matched to one first-member compound and 14.0% with pools matched to seven (`#/X2_winslow_muruku_at_one_compound`, `#/X1_winslow_muruku_at_lexicon_productivity`). The script of X2 names only the first of the two missed compounds; we found the second when checking this paragraph. Of the 61 Winslow entries ending in மீன், the parser split 28 as compounds of *mīṉ*, one of them falsely (ஜமீன் *jamīṉ*, Persian *zamīn* "land"). Of the rest, about 16 are two-member names of fish and stars that a complete parse would add: names printed as principals without an etymology (நாண்மீன், செம்மீன், கொக்குமீன்) and forms outside the fixed sandhi rules (பெருமீன், மும்மீன்). The others are longer compounds, phrases and loanwords such as *jāmīṉ* "bail". A complete parse would enlarge B(*mīṉ*) by about half, which raises the chance rate at fixed set sizes but leaves A(*muruku*) at two compounds.

## Post-outcome analyses

[exploratory.json](exploratory-v1/exploratory.json) holds four analyses chosen after results-v1 was read, with seed 20261022 and the functions of the frozen code. X1 matches the *muruku* pool in Winslow to the Lexicon's 7 first-member compounds (14.0%). X2 matches it to one compound (2.8%); a complete parse would give two. X3 builds pools for the same two targets, 7 first-member and 29 second-member compounds, in both dictionaries (Winslow 14.0%, Lexicon 16.6%); the Winslow pools of X1 and X3 are the same, and so are their rates. X4 lists the Tamil forms ending in மீன் in Winslow's text and checks for Parpola's compounds as entries and anywhere in the text. These numbers are descriptions of the two dictionaries; none of them was a frozen prediction.

## Inputs and dependence

The source is the Digital Dictionaries of South Asia edition of Winslow (978 query pages, 953 with entries, 26.4 MB, retrieved on 22 October 2026 between 14:05 and 14:24 UTC; [SOURCES.json](SOURCES.json)). The 25 pages without entries are placeholders for long entries printed in full on the following page and for the two pages after the end of the dictionary. The parsed table has 69,310 records (22,760 principal forms, 46,550 sub-entry forms) and 18,426 two-member compounds. The DEDR table, the 17 Sangam texts from Project Madurai and the concept pools are those of the 21 October study, with unchanged hashes. The DSAL pages carry no licence statement for the digital edition; the raw pages and all derived tables stay local.

The result depends on Winslow's selection of compounds and on our parse. The selection is the finding: a dictionary of 1862 that "embraces both the Common and Poetic Dialects" (Preface, p. v) lacks the compounds that make the Lexicon's interlock. The parse decides which of Winslow's run-on entries count as compounds, and its agreement with the Lexicon is given above. Because the DSAL text writes every initial *e* as ஏ, the Sangam frequency of the 193 native nouns beginning with that letter (1.8% of 10,499) is counted from the long-vowel spelling; none of Parpola's words begins with it.

## Protocol before outcome

[PROTOCOL.md](PROTOCOL.md) fixed the parsing rule, the parser checks, the reuse of `rebus.py`, `run_interlocks.py` and `parse_tamil_lex.py` of the 21 October study with their results-v2 hashes, and one decision rule: P2 passes if the share of the 2,500 replacement pairs with a shared member exceeds 0.20 under T0s with pools of 50. Before the freeze, the wrapper reproduced every section of the 21 October `results-v2/interlocks.json` from the Lexicon table ([check-reuse-v1.json](check-reuse-v1.json)), the package selftest checked transliteration, the junction rule, page parsing, compatibility with the frozen compound index and a planted interlock through the whole wrapper ([selftest-v1](selftest-v1/selftest.json)), and the 21 October selftest and the bench selftest passed on the unchanged code ([selftest-base-v1](selftest-base-v1/selftest.json), [bench-selftest-v1.json](bench-selftest-v1.json)). The only facts about the three anchor words known before the freeze were that each is a Winslow principal noun.

## Commands and outputs

Run from the repository root with Python 3.13 and NumPy 2.2.6.

```text
python experiments/2026-10-22-rebus-winslow/code/acquire.py files
python experiments/2026-10-22-rebus-winslow/code/acquire.py winslow 1 1100
python experiments/2026-10-22-rebus-winslow/code/manifest.py experiments/2026-10-22-rebus-winslow/SOURCES.json
python experiments/2026-10-22-rebus-winslow/code/parse_winslow.py
python experiments/2026-10-22-rebus-winslow/code/validate_parser.py experiments/2026-10-22-rebus-winslow/parser-validation-v1.json data/raw/2026-10-22-rebus-winslow/derived-v1/parser-validation-v1-detail.json
python experiments/2026-10-22-rebus-winslow/code/check_reuse.py experiments/2026-10-22-rebus-winslow/check-reuse-v1.json
python experiments/2026-10-22-rebus-winslow/code/selftest.py experiments/2026-10-22-rebus-winslow/selftest-v1
python experiments/2026-10-21-rebus-base-rate/code/selftest.py experiments/2026-10-22-rebus-winslow/selftest-base-v1
python -m bench selftest --out experiments/2026-10-22-rebus-winslow/bench-selftest-v1.json
python experiments/2026-10-22-rebus-winslow/code/freeze.py
python experiments/2026-10-22-rebus-winslow/code/run_winslow.py experiments/2026-10-22-rebus-winslow/results-v1
python experiments/2026-10-22-rebus-winslow/code/verify.py experiments/2026-10-22-rebus-winslow/results-v1 experiments/2026-10-22-rebus-winslow/verification-v1.json
python experiments/2026-10-22-rebus-winslow/code/exploratory.py experiments/2026-10-22-rebus-winslow/exploratory-v1
```

The download ran as two page-range streams one after the other, pages 1–233 and 234–978, each with its own log file. The bootstrap and draw seed is 20261021 (20261022 for the post-outcome analyses). The compound lists and the full output of the frozen run are local: `data/raw/2026-10-22-rebus-winslow/results-v1/interlocks-detail.json` and `interlocks-synthetic.json`, with their hashes in `#/local_detail`.

## Challenges and repairs

The first download stream stopped at page 233 because two placeholder pages looked like the end of the dictionary; we changed the stop rule before the freeze to require a page without entries and without a link to the next page, and resumed from page 234. The parser went through three rounds of repair against the Lexicon comparison, all before the freeze and recorded in the protocol. The [retrospective](RETROSPECTIVE.md) gives the details.

## Decision and next evidence

Within this protocol P2 fails: in a second Tamil dictionary with compounds, the frozen search finds no chance interlocks, because that dictionary records no compound of *muruku*. The failure falsifies the prediction as written, which assumed that both anchor words have compounds in any large Tamil dictionary, and it supports the claim behind C-0014 in a stronger form: whether Parpola's *veḷ* interlock exists at all depends on which dictionary is consulted. At equal compound-set sizes the chance rate is about 14–17% in both dictionaries, below the 20% line, so the 30.5% kill of 21 October rests on the Lexicon's 82 compounds of *mīṉ*.

Do not rerun the *veḷ* search on Winslow; it has nothing to search. A third Tamil dictionary is informative only if it records compounds of both *muruku* and *mīṉ*; the Kadirvelu Pillai dictionary on DSAL is the next candidate, and the prediction to freeze for it is the equal-target comparison, which this study can no longer test prospectively. A [proposed record line for C-0014](C-0014-RECORD-PROPOSAL.md) is in this package.

## The boldest reading and the test that would decide it

Parpola's *veḷ* is a reading of the Madras *Tamil Lexicon*. The two compounds it rests on are not entries of the largest Tamil dictionary before it, which calls the god *cevvēḷ*; the chance of an interlock is set by how many compounds a dictionary records for the two words, at nearly the same rate per compound in both dictionaries; and his network of interlocks shrinks from four links in the Lexicon to two in Winslow, which random words reproduce in 4% of draws. The interlocks measure the dictionary that was consulted.

The test that decides it is attestation in Old Tamil itself, which Parpola's procedure ranks first among the sources of compounds (Parpola 2010, p. 17, as encoded in the 21 October protocol). Freeze two lists before searching: the compounds of Parpola's interlocks (*muruka-vēḷ*, *veṇ-mīṉ*, *veḷḷi-mīṉ*, *vaṭa-mīṉ*, *mu-m-mīṉ*, *aṟu-mīṉ*, *eḻu-mīṉ*, *katir-k-kaṭavuḷ*) with their Tamil-script sandhi forms, and an equal number of compounds drawn at random from those that complete chance interlocks in the Lexicon null. Then count how many of each occur in the 17 Sangam texts already held for this project. If the language of the script is Dravidian and Parpola's identifications are right, his compounds should be attested at least twice as often as the chance compounds; a similar rate would show that his interlocks, like the chance ones, come from the lexicographers rather than from the oldest Tamil.

## Review and verification

[verification-v1.json](verification-v1.json) recomputes the compound count, the sizes of A(*muruku*) and B(*mīṉ*), the real search, the Winslow productivity and frequency of *muruku* and *mīṉ*, both replacement pools and the null rate with the independent stem, sandhi and search functions of the 21 October `verify.py`, which do not import `rebus.py`; all seven checks agree. No other contributor has reproduced or reviewed this package.
