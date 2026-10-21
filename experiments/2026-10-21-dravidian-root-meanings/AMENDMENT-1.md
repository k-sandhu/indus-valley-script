# Amendment 1: locating entries and parsing conventions

Recorded on 21 October 2026 (UTC) after the protocol was hashed and after the entry searches of [ENTRIES.md](ENTRIES.md) had been read, before any meaning was coded on the tree, before any tree was downloaded and before any root probability was computed. The searches showed glosses, including the languages in which entry 4876 gives a star sense, so these changes are post-data decisions about locating entries and parsing text. None of them changes a sense class or a pass rule.

## 1. Full-text search for location

The protocol located entries with DSAL's entry-word search. That search indexes only the first Tamil form of each entry, so it cannot find a cited form that DEDR lists inside an entry headed by another form. Applied literally it leaves STAR unlocated: entry 4885 gives *mīṉ* only as "fish", and the protocol's fallback would code STAR absent in every language, Tamil included, although DEDR gives Tamil *mīṉ* "star" in entry 4876. The protocol's own qualification ("the entry in which the Tamil line gives the cited form … with a gloss in the meaning's class") selects 4876, and we apply it with DSAL's full-text search. The same search located CHILD, SPACE, WHITE, VELGOD and LIGHT, whose Tamil forms are also not entry heads.

## 2. EARRING

The Tamil line of entry 4979 glosses *muruku* "ornament worn in the helix of the ear". Under the head rule its head is "helix", so the literal location rule finds no qualifying entry and codes EARRING on 4978, where it is absent by construction. The gloss describes an earring, and the Kannada, Tulu, Telugu and Gondi (Ko.) lines of 4979 carry the class directly ("ear-ring", "bangle", "bracelet", a ring for "the nose and the ear"). The primary analysis locates EARRING in 4979 and codes it there with the frozen class rule, under which the Tamil line itself is coded 0. Two sensitivity analyses are added:

- **S7. Literal location.** STAR coded on 4885 and EARRING on 4978, both absent by construction, with everything else as in the primary analysis.
- **S8. Plain-reading check (exploratory).** We read every needed meaning's coding against its glosses and list each segment the mechanical rule codes differently from a plain reading of the gloss, such as the Tamil earring gloss above. S8 recodes those segments and reruns the primary model. It is a post-outcome check and does not enter the pass rules.

## 3. Parsing conventions

These follow the conventions of the dictionary itself and fix how the coder reads its text.

- An entry is identified by its number; a lettered subentry such as 5496 (a) is a separate cognate set with its own Tamil line, and a meaning is coded on the subentry whose Tamil line qualifies (WHITE on 5496 (a)).
- Within a language line, a series of forms without an intervening gloss shares the next gloss. A form followed by "id." takes the gloss of the immediately preceding glossed form. A form with no gloss, as in most lines of 4885, takes the gloss of the immediately preceding glossed form in the entry, which may lie in an earlier language line.
- Text in parentheses is removed from glosses before segmentation. Dialect and source labels in parentheses, such as "(Oll.)" or "(Mu.)", are read only to map forms to tips.
- Before the article and "to" are removed, a segment loses leading grammatical labels: n., adj., adv., vb., v.i., v.t., intr., tr., caus., pl., obl.
- A form preceded by "?" is doubtful (excluded in S1). A form marked with "<" or "(< X.)", where X is a language abbreviation, is a borrowing and is ignored.
- Material after the slash that closes the Dravidian lines ("/ Cf. Skt. …") and cross-references ("Cf. 5396 Ta. viṇ", "DED(S) 3994") are not language lines.

## 4. The homophone test S4

DEDR marks vowel length in Kota, Toda and Kodava with a raised dot (*mi·n*) and marks Malto stress with an acute accent (*mínu*). Before the S4 test that a star form begins with m, then i or ī, then n, ṉ or ṇ, we delete the raised dot, the IPA length mark ː and combining acute and grave accents. Other letters, such as Kodava ï, are kept as written.
