# Winslow rerun study record

We acquired Winslow's Tamil-English dictionary of 1862 from DSAL with a request log per page, wrote a parser that recovers two-member compounds from Winslow's nesting of compounds under their root, checked it against the *Tamil Lexicon*, froze a protocol that reuses the 21 October code unchanged, and ran the *veḷ* search with random replacement words. P2 of C-0014 failed under its frozen rule because Winslow has no compound of *muruku*; post-outcome analyses compared the two dictionaries at equal compound-set sizes.

## Approaches and repairs

The acquisition script follows the logging of the 21 October `acquire.py` and gives each page-range stream its own log file. The first stream stopped at page 233, because pages 232 and 233 have no entries and its stop rule ended a run after two such pages. They are placeholders: DSAL prints the whole of a very long entry, here கண் *kaṇ* with 204 sub-entries, on the page after the print pages it covers, and marks those pages "Please click next to see digital content for this page". We changed the rule to stop only at pages with neither entries nor a link to the next page and resumed from page 234 in a second stream, which ended at page 978 after the two pages that follow the dictionary. Both streams ran one request at a time, and the 978 log records match the 978 pages on disk.

Winslow prints no hyphens and gives sub-entries no romanisation, so the first question was whether compounds can be recovered at all. The front matter answered it: derivatives and compounds are nested under their primitives, compounds of genus and species under the genus, and the junction follows "the usual rules for the mutation of letters". We wrote a transliteration into the DSAL scheme, checked it against the romanisation printed with every principal (99.92% exact), and a junction rule that splits a sub-entry at a sandhi form of its root.

The parser needed several rounds before the freeze, each judged by its agreement with the *Tamil Lexicon*'s hyphenation on compounds present in both dictionaries. Matching the other member by its T1s stem accepted suffixes as words (*kali-ppu* became *kal* + *ippu*); an exact match to a headword replaced it. A Python generator consumed by the first of two passes left the list of first-member forms empty, so no compound ending in its root was found until we passed a list. On the first 600 pages agreement was 85%, held down by headwords not yet downloaded and by splits such as *kaḷam* + *ati* where the Lexicon has *kaḷa-mati*; with the full dictionary and a preference for consonant-initial second members it rose to 98.1%. Half of the Winslow sub-entries that the Lexicon prints as single words were still split, because Winslow gives every syllabic letter, ending and particle its own principal entry, so that *pu*, *aṉ* and *al* counted as words. Excluding those entries by the opening of their first sense, and refusing one-syllable endings in sub-entries labelled as verbal nouns, brought the share to 27%, much of it compounds that the Lexicon writes solid. An attempt to exclude every principal without a part of speech would have dropped real nouns such as சாலை and மகள், which Winslow prints without a label, and we did not adopt it. A regular expression written through a shell heredoc lost its `\b` to a backspace character, so the first version of the rule flagged a single entry; we repaired the file directly.

Running the scripts with `python -I` hid NumPy, which this machine installs in a per-account package directory that isolated mode skips, so the measurement scripts run without `-I` from the repository root; the parser reads the downloaded pages only as data.

Before the freeze we ran the wrapper on the *Tamil Lexicon* table and compared its output with the 21 October results-v2 section by section; every section was identical. This showed that calling the frozen `run()` in its synthetic mode, with our own provenance block, changes no number.

## The outcome and what we did with it

The frozen run gave a chance rate of exactly zero. We confirmed it with an independent recomputation built on the 21 October `verify.py` functions, then searched the raw pages for every Tamil form containing முருக and every form ending in மீன். That search showed that the zero comes from the dictionary: Winslow has no *Muruka-vēḷ*, and its only compounds with *muruku* as first member under the stem rule, *murukkam-pū* and *murukkañ-cettal*, were missed by the parser because they carry the *-am-* increment; with them the chance rate would still be far below the threshold. It also found the false split *ja-mīṉ* (Persian *zamīn*) and about 16 fish and star names that a complete parse would add to the compounds of *mīṉ*. The analyses that compare the dictionaries at equal compound-set sizes were chosen after the outcome and are in `exploratory-v1/` with their own seed.

## What we did not obtain

We did not parse principal headwords that are compounds without an etymology, compounds of three or more members, or junctions outside the fixed sandhi forms, such as the *-am-* increment of tree names (*murukkam-pū*, *murukkañ-cettal*). The Kadirvelu Pillai dictionary, the other second dictionary named in C-0014, was not acquired.

## Verification and source handling

[verification-v1.json](verification-v1.json) agrees with the frozen result on all seven checks. The bench selftest wrote its ledger to a temporary directory, and this package adds nothing to `bench/spent.json`; no Indus text was read. The DSAL pages carry no licence statement for the digital edition, so the pages, the parsed table, the compound lists and the parser's disagreement list stay local under `data/raw/2026-10-22-rebus-winslow/` (29 MB). Tracked files hold our code, the protocol, page hashes and aggregate results.

## Decision

Rerunning the *veḷ* search on Winslow adds nothing. The next steps are the Sangam attestation test named at the end of the [report](REPORT.md) and, for C-0014, a third dictionary tested with a prediction about the chance rate at equal compound-set sizes.
