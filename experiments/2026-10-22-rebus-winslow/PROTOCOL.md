# REBUS-WINSLOW-2026-10-22: the veḷ search in Winslow's dictionary

Recorded on 22 October 2026, after Winslow's dictionary had been acquired, parsed and checked against the Tamil Lexicon, and before any compound set of *muruku*, *mīṉ* or *kaṭavuḷ* or any chance rate was computed on it. Authors: Claude (Opus 5.5, model ID `claude-opus-5-5`, Claude Code desktop harness), in a session started from the session that wrote C-0014. Owned directory: `experiments/2026-10-22-rebus-winslow/`. Acquired pages and every table derived from them stay local in `data/raw/2026-10-22-rebus-winslow/`.

## Question

Asko Parpola read the two-long-strokes sign of the Indus script as Proto-Dravidian *veḷ* because two attested Tamil compounds meet in that word: *Muruka-vēḷ*, a name of the god Murukan, and *veṇ-mīṉ* "white star", Venus (Parpola 2010, pp. 26–27). The study of 21 October ([REBUS-BASE-RATE-2026-10-21](../2026-10-21-rebus-base-rate/REPORT.md)) encoded his search as a program and replaced *muruku* and *mīṉ* by random native nouns of the same compounding productivity and Sangam frequency. In the Madras *Tamil Lexicon* the compound sets of the two replacement words shared a member for 30.5% of 2,500 pairs, above the frozen 20% threshold, which killed the *veḷ* interlock as evidence.

Conjecture [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md) holds that such interlocks record the density of the Tamil compound vocabulary rather than the language of the script. Its prediction P2 is that the same search rerun in a second Tamil dictionary with compounds again finds a shared member for more than 20% of random replacement pairs. This study tests P2 in Miron Winslow's *A comprehensive Tamil and English dictionary of high and low Tamil* (Madras, 1862), compiled two generations before the *Tamil Lexicon* (1924–1936) by a different editorial team. It reads no Indus text and spends no part of the corpus.

## Prior attempts and what is new

The registry entry REBUS-BASE-RATE-2026-10-21 names a second Tamil lexicon with compounds as a reason to revisit its searches, and rules out rerunning them on the *Tamil Lexicon*. No earlier package has used Winslow. The study of 21 October also rests on the key-calibration work of 12 October, which showed that dictionary fits carry weight only against random strings. The blind-template test of C-0014 P1 is being prepared in a separate package, `experiments/2026-10-22-rebus-blind-templates/`; this study shares no files with it.

No task of the shared harness scores lexical compounds, and this study adds no statistic family to `bench/spent.json`. We ran `python -m bench selftest` once to record the state of the harness ([bench-selftest-v1.json](bench-selftest-v1.json), passed).

## The source and how it marks compounds

We acquired the Digital Dictionaries of South Asia edition of Winslow page by page (`winslow_query.py?page=1..978`), one request at a time with a 0.6 s pause, logging URL, status, bytes, SHA-256 and time for every request ([SOURCES.json](SOURCES.json); 978 pages, 26.4 MB, no hash mismatches). Of these pages 953 carry entries. The other 25 are placeholders: 23 mark print pages covered by a very long entry, such as கண் *kaṇ* (204 sub-entries) or கை *kai* (329), whose text DSAL places in full on the following page, and the last two follow the end of the dictionary. No part of the dictionary is missing. The DSAL front matter states that Winslow's errata were applied and that the data were last updated in October 2020. The pages carry no licence statement for the digital edition, so the pages and our tables stay local.

Winslow does not hyphenate compounds, and his compounds carry no romanisation. He arranges the dictionary by primitives: a principal headword in large type gives its Tamil form and a romanisation, and its derivatives and compounds follow as run-on sub-entries in Tamil script only, "brought under their primitives … when the initial letters are the same or changed by common grammatical rules" (Plan of the Lexicon, p. x). A compound is therefore nested under its first member. Compounds "of a genus and species" are nested under the genus, their last member (Directions for Using the Lexicon, p. xi): சாழையகத்தி *cāḻaiyakatti*, a fruit tree, stands under அகத்தி *akatti*. Some principals are compounds themselves and name their members in a bracketed etymology, "[*ex* அகம், inside, *et* பகை.]". The boundary between the members is not printed; the nesting gives one member, and Winslow leaves the junction to "the usual rules for the mutation of letters" (p. xi).

This is enough to recover two-member compounds, so we did not stop at the source review. The rule below finds the junction from the nesting and from Tamil sandhi, and keeps the members as written, as the *Tamil Lexicon*'s hyphenation does, so that the frozen code of 21 October applies to them unchanged.

## Parsing rule

`code/parse_winslow.py` reads every entry block (`<div>` with `<hw>`) and every run-on sub-entry (`<p2>`). It records, for each principal form, the Tamil form, the DSAL romanisation, the part of speech, Winslow's asterisk (which marks Sanskrit primitives, Preface) and any mark of non-Dravidian origin in the opening label (Hind., Ar., Pers., For., Mah., St., Sans. and similar). Winslow's "s." (substantive) becomes the noun label "n" used by the frozen code. A principal is a verb when its label is "v. a.", "v. n." or "inf.". Each written form of a headword or sub-entry, including forms joined by a dash, is its own record. Sub-entries are romanised by our transliteration in the DSAL scheme, which reproduces the romanisation printed with 22,742 of the 22,760 principal forms (99.92%; the rest contain zero-width joiners or Latin letters).

A sub-entry nested under a principal with romanised form *h* is a two-member compound in one of three ways:

- **First member.** The sub-entry begins with a sandhi form of *h* and the rest is a principal headword. The sandhi forms of a first member are fixed in `first_variants`: the word itself; a final *-m* dropped or assimilated (*mara-*, *kuḷaṅ-*) and the oblique *-att-* of *-am* nouns; a final *-u* dropped before a vowel, with the doubled stop of *āṭu* > *āṭṭu-* and the hardened clusters *-ntu* > *-ttu-*, *-mpu* > *-ppu-* and their kin; *ḷ* > *ṭ*, *ṇ*; *l* > *ṟ*, *ṉ*; *ṇ* > *ṭ*; *ṉ* > *ṟ*; the masculine *-aṉ* dropped (*muruka-* < *murukaṉ*); and the doubled final consonant of a short monosyllable before a vowel (*kall-* < *kal*). At the junction the doubled initial stop of the second member (*añcaṉa-k-kalikkam*) and a glide *y* after *i*, *e*, *ai* or *v* after *a*, *u*, *o* are removed. When several splits qualify, a second member that begins with a consonant is preferred (*kaḷa-mati* over *kaḷam-ati*), then the longest first member.
- **Second member.** The sub-entry ends with *h*, and the part before it, after removal of the sandhi doubling or glide, is a sandhi form of some principal headword.
- **Etymology.** A principal whose etymology names two Tamil-script members and whose form splits into them by the same junction rule.

A two-word sub-entry is a compound when one word is *h* in the corresponding position and the other is a headword. Matching treats *e* and *ē*, *o* and *ō* as one vowel, because the DSAL text writes every initial *e* with the long letter ஏ (no principal begins with எ) while medial *e* and *ē* are distinguished. Three classes of entry are excluded from the compound vocabulary. Winslow's grammatical entries for letters, endings, particles and prefixes, recognised by the opening of their first sense ("A syllabic letter composed of …", "The eleventh vowel"; and, when the entry has no part of speech, "An increment", "A Sanscrit prefix", "A poetic expletive"), are not words and are not split under (167 principal forms). Sub-entries without a part of speech are example phrases and sentences and are not split (5,552). A sub-entry labelled as a verbal noun is not split when its second part has one syllable, because such a part is a verbal-noun suffix: Winslow's verbal nouns end in ல் and பு (Plan of the Lexicon, p. x) and also in *-kai*.

The resulting table, `data/raw/2026-10-22-rebus-winslow/derived-v1/winslow-entries.jsonl` (SHA-256 `5697e42a…d1e5`), has 69,310 records: 22,760 principal forms and 46,550 sub-entry forms, with 18,426 two-member compounds (16,332 by first member, 1,861 by second member, 212 by etymology, 21 two-word phrases). The *Tamil Lexicon* table of 21 October has 117,803 entries and 56,154 two-member compounds.

## Parser checks before the freeze

The checks in [parser-validation-v1.json](parser-validation-v1.json) compare our compounds with the *Tamil Lexicon*'s hyphenation wherever the same Tamil form occurs in both dictionaries. They use no word of the interlock searches; no compound of *muruku*, *mīṉ* or *kaṭavuḷ* in Winslow was looked up before the freeze. We checked only that each of the three is a Winslow principal noun of one member (one, two and one entries).

- **Agreement.** Of 11,784 Winslow compounds whose Tamil form is a two-member compound of the Lexicon, 11,560 (98.1%) have the same members: the same second member and first members that share a sandhi base under T0s. The rate is 98.1% for first-member splits, 98.3% for second-member splits and 98.3% for etymologies.
- **Coverage.** Of 15,550 Winslow sub-entries whose Tamil form the Lexicon hyphenates into two members, we split 11,726 (75.4%). The rest are mostly three-member compounds, compounds whose other member is not a Winslow headword, and junctions outside the fixed sandhi forms.
- **Splits of single words.** Of 5,109 sub-entries whose Tamil form the Lexicon prints as one unhyphenated word, we split 1,369 (26.8%). Many are compounds that the Lexicon writes solid, such as *kurutt-ōlai* and *mārp-elumpu*; others are derivatives in *-mai*, *-tuvam*, *-vāṉ* and the masculine and plural endings.

The parser reached this state through repairs made on these checks alone. An exact match of the other member to a headword replaced a match of T1s stems, which had split *kalippu* as *kal* + *ippu*. On the first 600 pages an early version agreed with the Lexicon for 85% of first-member splits, most disagreements coming from headwords not yet downloaded and from vowel-initial second members such as *kaḷam-ati* for *kaḷa-mati*; with the full headword list and the preference for consonant-initial second members the agreement is 98.1%. Excluding the grammatical entries lowered the share of split single words from 50% to 33%, and the rule for verbal nouns lowered it to 27%.

## Measurement

`code/run_winslow.py` passes the Winslow table to `run()` of `experiments/2026-10-21-rebus-base-rate/code/run_interlocks.py`, which it imports unchanged, together with the unchanged `rebus.py` (as repaired in Amendment 1 of that study) and `parse_tamil_lex.py`. FREEZE.json records their hashes, which must equal those under which the 21 October results-v2 were computed. `run()` is called in its synthetic mode, which writes its full output to a local directory and adds no provenance block; the wrapper moves the compound lists to a local detail file, adds this package's provenance and writes the tracked result. Run on the *Tamil Lexicon* table, the same wrapper reproduces every section of the 21 October `results-v2/interlocks.json` exactly, including the null rate 0.3052 and the network rate 0.0044 ([check-reuse-v1.json](check-reuse-v1.json)).

Everything the frozen code does is therefore fixed, with Winslow in place of the Lexicon:

- **Compounds of a word.** A compound belongs to *W* as first member when the T1s stem of one of its first member's sandhi bases equals the T1s stem of *W*, and as second member when the T1s stem of its second member does. A(*W1*) holds the second members of compounds *W1*-X, B(*W2*) the first members of compounds X-*W2*.
- **The search.** The *veḷ* search succeeds for *W1* and *W2* when a member of A and a member of B coincide under the stated rule T0s (vowel length and gemination free, with sandhi bases of first members), members that coincide with *W1* or *W2* excluded.
- **Replacement words.** Candidates are Winslow principal forms of one member labelled as nouns, without the asterisk or a foreign mark and not verbs, whose T0 form occurs among the Tamil forms of an attested entry of the *Dravidian Etymological Dictionary* (the DEDR table of 21 October), one per T1s stem. Each has its first-member and second-member productivity in Winslow and its frequency, the number of word tokens in the 17 Sangam texts of 21 October that begin with its Tamil-script stem. The pool for *muruku* is the 50 candidates nearest in standardised (log(1 + first-member productivity), log(1 + frequency)); the pools for *mīṉ* and *kaṭavuḷ* use second-member productivity.
- **The null.** All 50 × 50 pairs of replacement words for *muruku* and *mīṉ* are enumerated, with a 95% interval from 2,000 bootstrap replicates over pool words, seed 20261021.

Of Winslow's 10,499 principal forms that are native one-member nouns, 193 (1.8%) begin with ē. Because the DSAL text writes every initial *e* as ஏ while the Sangam texts distinguish எ and ஏ, the frequency of these words is counted from the long-vowel spelling. We keep the source spelling and report this as a limit.

## Decision rule

**P2 passes** if the share of the 2,500 replacement pairs (both *muruku* and *mīṉ* replaced, pools of 50, stated rule T0s) whose compound sets share a member is above 0.20 (`#/null/I1_T0s/K50/rate` of `results-v1/interlocks.json`). It fails otherwise. Following C-0014, a pass raises the credence of C-0014 by 0.05 and a failure lowers it by 0.10.

The frozen code computes further quantities, which we report beside the decision without a rule of their own: whether the search holds for Parpola's own words in Winslow and with which members; the rates for pools of 25 and 100; the practised rule T1s; the rates with only one word replaced; the restricted search over compounds glossed as names of Murukan or as stars and fish; the picture searches I2, I3 and I5; the numeral search I4; and the network null of 10,000 draws. We also report the sizes of A(*muruku*) and B(*mīṉ*) and the mean compound-set sizes of the pools in both dictionaries, because the chance of a shared member grows with the sizes of the two sets and Winslow has a third as many two-member compounds as the Lexicon.

## Order of work and stopping

1. Acquisition and the source manifest ([SOURCES.json](SOURCES.json)).
2. Parsing (`code/parse_winslow.py`) and the parser checks ([parser-validation-v1.json](parser-validation-v1.json)).
3. The package selftest ([selftest-v1](selftest-v1/selftest.json)), the selftest of 21 October rerun on the unchanged code ([selftest-base-v1](selftest-base-v1/selftest.json)), the bench selftest and the reuse check; all pass.
4. Freeze: `code/freeze.py` writes FREEZE.json with the SHA-256 of this protocol, our code, the reused code and every input.
5. `code/run_winslow.py` into `results-v1/`; the script refuses to run if any frozen file has changed.
6. Report, retrospective, attempt entry and a proposed record line for C-0014.

No step stops on a favourable outcome. Every output is written to a new path, and scripts refuse to overwrite. A parser or code repair after the freeze is recorded in a dated amendment with the hashes before and after, and any result already computed is kept beside the repaired one.

## Data handling

Raw pages, the parsed table, compound lists and the parser's disagreement list stay in `data/raw/2026-10-22-rebus-winslow/`. The package tracks our code, this protocol, the source manifest with page hashes, the parser checks and the aggregate results, whose word content is limited to Parpola's published words, the replacement headwords and the shared members of the real search, as in the study of 21 October.

## References

Parpola, Asko. 2010. *A Dravidian solution to the Indus script problem*. Chennai: World Classical Tamil Conference.
Winslow, Miron. 1862. *A comprehensive Tamil and English dictionary of high and low Tamil*. Madras: P. R. Hunt. Digital Dictionaries of South Asia edition, https://dsal.uchicago.edu/dictionaries/winslow/.
University of Madras. 1924–1936. *Tamil Lexicon*. Madras: University of Madras. Digital Dictionaries of South Asia edition.
Burrow, T. and M. B. Emeneau. 1984. *A Dravidian Etymological Dictionary*. 2nd ed. Oxford: Clarendon Press.
