# NORTH-B-CORRESPONDENCE-2026-10-21: does northern *b-* answer Tamil *m-*?

Recorded on 21 October 2026 and hashed at 18:41 UTC, before any entry of the *Dravidian Etymological Dictionary* (DEDR) was read for this study. Author: Claude Opus 5.5 (`claude-opus-5-5`) in the Claude Code desktop app, working for k-sandhu in a side session started from the coordinating session of the Parpola studies. Owned paths: `experiments/2026-10-21-north-b-correspondence/`, `data/raw/2026-10-21-north-b-correspondence/` (local only) and `knowledge/registry/attempts/NORTH-B-CORRESPONDENCE-2026-10-21.json`. The study runs prediction P5 of conjecture [C-0011](../../knowledge/conjectures/C-0011-proto-dravidian-min-fish-and-star.md) and does not edit the card.

## Question

DEDR entry 4876, headed by Tamil *miṉ* "to flash, glitter", lists star words in Kurukh (*bīnkō*) and Malto (*bínḍke*), the two North Dravidian languages of the Ganges plain. On the dated tree of Kolipakam and colleagues (2018) these two words carry the star sense of entry 4876 to the North Dravidian node with probability 0.681 ([report](../2026-10-21-dravidian-root-meanings/REPORT.md)). Both begin with *b-*. In the entries the root-meanings study coded, northern *b-* answers Tamil *v-* (5496 (a), Tamil *veḷ* "white") and Tamil *m-* stays *m-* in the north (5052 "three", 4885 "fish"), and DEDR closes entry 4876 with a cross-reference to 5396, Tamil *viṇ* "sky". If northern *b-* answers Tamil *m-* nowhere else in the dictionary, the two star words are better read as derivatives of *viṇ* "sky", and the homophone *mīn* "star" does not reach the north.

The question is a count over the whole dictionary: when Tamil begins a word with *m-* or *v-*, with what initial do Kurukh and Malto begin the same word, according to DEDR?

## What we had read before writing

We had read conjecture C-0011, the report and protocol of DRAVIDIAN-ROOT-MEANINGS-2026-10-21, its session note, the DEDR parser of REBUS-BASE-RATE-2026-10-21 (`experiments/2026-10-21-rebus-base-rate/code/parse_dedr.py`) and that study's request log. To learn the page format we printed the opening of DSAL page 1 (entries headed by Tamil *a-*) and the two printed versions of entry 137 (Tamil *atir* "to shake"), and counted entry-number tags across the 514 pages without printing their contents. Those reads showed that language labels are italic, sometimes inside bold runs and sometimes after a grammatical label in the same italic run ("(tr.). Malt."); that a lettered sub-entry begins with a label such as "(b) Ta." in a new `new_p` span inside the same entry block; that DSAL prints 98 entry numbers more than once, and in entry 137 the shorter print is a prefix of the longer; that cross-references such as "Cf. 37 Ta. acaṅku" set "Ta." in bold without italics; and that 62 entries on pages 509 to 514 are numbered afresh. Of the entries with a Tamil initial *m-* or *v-* we know only those the root-meanings study coded: 4876, 4885, 5052, 5396 and 5496 (a).

From general reading, unchecked, the author recalls three things. Proto-Dravidian *w-* (written *v-* in Tamil) became *b-* in Kurukh, Malto and Brahui, and in Kannada. Some South Dravidian forms show *m-* where other branches show *v-* before a syllable containing a nasal, which some authors explain as a southern change of *w-* to *m-* in that position. And we recall no DEDR entry other than 4876 in which Kurukh or Malto *b-* answers Tamil *m-*. We do not recall whether Parpola discusses the initial of *bīnkō*.

## Source

T. Burrow and M. B. Emeneau, *A Dravidian Etymological Dictionary*, 2nd ed. (Oxford: Clarendon Press, 1984), DSAL web edition, data updated February 2021, <https://dsal.uchicago.edu/dictionaries/burrow/>. The 514 pages were fetched on 21 October 2026 between 01:37 and 01:58 UTC by REBUS-BASE-RATE-2026-10-21 into `data/raw/2026-10-21-rebus-base-rate/sources-v1/dedr/`, with a SHA-256 hash for each page in `requests.jsonl`. We read those files without changing them; the code checks every page against its logged hash before parsing and stops on a mismatch.

The DSAL edition carries the notice "Copyright 1984 by Oxford University Press. No part of this publication may be stored, transmitted, retransmitted, lent, or reproduced in any form or medium without the permission of Oxford University Press." Parsed lines and per-entry tables therefore stay in `data/raw/2026-10-21-north-b-correspondence/`. Tracked files hold counts, entry numbers, initial and vowel classes, hashes and our own rules. Prose cites an individual form only where the argument needs it.

## Units

**Entry and part.** An entry is one DEDR number; the 62 entries on pages 509 to 514 are named with the prefix `a` (`a53`). When DSAL prints a number more than once, we use the longest print and check that every shorter print is a prefix of it; a failure of that check is reported, and the union of northern lines over all prints is reported beside the primary count. An entry whose body contains lettered sub-entries, marked by "(a)", "(b)" and so on immediately before a language label, is divided into parts at those markers; an entry without such markers is one part. Parts are named by number and letter, as in "5496 (a)".

**Lines and forms.** A language line starts at an italic language label and runs to the next italic language label in the same part, or to the start of DEDR's comparison notes: the first " / " outside a bold run, or a closing "DED", "DEN" or "DBIA" reference. A label in a bold run without italics, such as a cross-reference, does not start a line. A label repeated in the same part starts a second line of the same language; the language's forms in the part are the forms of all its lines, in order. A form is a word in a bold run of the line, split at commas, semicolons and slashes; suffix and stem notes beginning with a hyphen, parenthesised stem notes and empty strings are dropped. The first form of a language in a part is its first form, in order of appearance, that is not borrowed; its first undoubted form is the first form that is neither borrowed nor doubtful (both terms are defined below).

**Tamil initial.** The Tamil initial of a part is the first letter of the first Tamil form, taken after Unicode NFD decomposition, after removing leading characters that are not letters (such as "?", "-", "(" and "*"), and after lower-casing. Parentheses around an optional letter are removed with the letter kept, so "(v)iṇ" counts as *v-*. A part belongs to the Tamil *m-* group when that letter is "m" and to the Tamil *v-* group when it is "v".

**Northern initial.** The initial class of a Kurukh (label "Kur.") or Malto (label "Malt.") form is found the same way, after also removing the acute and grave accents that DEDR uses for Malto stress. The classes are *m* (the letter m), *b* (b, including aspirated bh, which is flagged), *v* (v or w) and *other*.

**Doubtful and borrowed forms.** DEDR marks a doubtful comparison with "?". Every form of a line is doubtful when a "?" is the last character before the line's language label or stands inside the label's italic run; a single form is doubtful when a "?" or "(?)" immediately precedes it or follows it before its gloss. A "?" inside a gloss marks the gloss and is ignored. A form is borrowed when a "<" occurs between it and the next form or label, as in "(< IA)" or "(< Te.)", or when the text of its line contains "borrowed" or "loan". Borrowed forms are excluded from every count; a line all of whose forms are borrowed counts as absent. Doubtful forms are counted and flagged, and the pass rule below uses undoubted forms only.

**Vowel context.** For the first Tamil form and the first northern form of each language we record the vowel after the initial consonant (after bh, the vowel after the h) and the next consonant. The vowel class is *long front* (ī, ē), *short front* (i, e), *long back* (ā, ō, ū), *short back* (a, o, u), *diphthong* (ai, au) or *none*. A vowel is long when it carries a macron or is followed by "·" or ":". Accents are removed first. We also record whether the first consonant after that vowel is a nasal (m, n, ṉ, ṇ, ñ, ṅ, ŋ). The vowel class enters no rule; it shows whether the cases of northern *b-* for Tamil *m-* share the long front vowel of *mīn*, as P5 proposes, and whether they share the following nasal in which a southern change of *w-* to *m-* has been proposed.

## Population

The population is every part with a Tamil line whose first form begins with *m-* or *v-* and with at least one Kurukh or Malto form that is not borrowed. Entry 4876 belongs to the population but is left out of the pass rule.

## Counts

The primary unit is a part and a northern language. For each Tamil initial (*m*, *v*) and each northern language (Kurukh, Malto, and both pooled) we count the units whose first undoubted form begins with *m*, *b*, *v* or *other*, and again using the first form with doubtful forms allowed. At the entry level we count, for each Tamil initial, the entries (distinct numbers, parts pooled) in which the first undoubted Kurukh form or the first undoubted Malto form begins with *b-*. Every table is given with entry 4876 and without it.

Secondary counts, none of which enters the pass rule:

- S1. Every form instead of the first form: a unit counts for each initial class found among its non-borrowed forms.
- S2. Brahui (label "Br."), counted like Kurukh and Malto.
- S3. Every part with a Tamil line and a Kurukh or Malto line, whatever the Tamil initial: the northern first-form classes for each Tamil initial letter. This shows which Tamil initials northern *b-* answers, and how often *b-* appears for Tamil initials from which no regular change derives it (the irregular rate against which the Tamil *m-* count is read).
- S4. The vowel class and the following-nasal flag of the Tamil and northern first forms, for each Tamil-initial and northern-initial pair.
- S5. Parts whose Tamil line contains forms with both initials *m-* and *v-*, listed by number, and the entry-level counts repeated without them.
- S6. For every part in which northern *b-* answers Tamil *m-*, the initial classes of the first Telugu, Kannada and Gondi forms (Telugu and Gondi keep Proto-Dravidian *w-* as *v-*; Kannada changes it to *b-*).
- S7. The union of northern lines over all prints of a repeated number, against the longest print.

The results file lists the entry numbers of every part in which northern *b-* answers Tamil *m-* and of every part in which northern *m-* answers Tamil *v-*, with their doubt flags and vowel classes, without forms.

## Pass rule and credence

From C-0011, made exact here:

- **Pass.** At least two entries other than 4876 have a Tamil *m-* part in which the first undoubted Kurukh form or the first undoubted Malto form begins with *b-*. C-0011 then moves from 0.20 to 0.30.
- **Failure.** No entry other than 4876 has a Tamil *m-* part with any non-borrowed Kurukh or Malto form beginning with *b-*, doubtful forms and non-first forms included, and at least one entry has a Tamil *v-* part with a Kurukh or Malto first form beginning with *b-*. C-0011 then moves from 0.20 to 0.10.
- **Otherwise** (one qualifying entry, or only doubtful or non-first *b-* forms), P5 is unresolved and the credence stays at 0.20.

The proposed credence follows this rule. After review it may be lowered and not raised. One lowering is foreseen: if every entry behind a pass has a nasal as the first consonant after the Tamil vowel and a Telugu or Gondi form beginning with *v-*, the pass fits Proto-Dravidian *w-* with a southern change to *m-* as well as it fits *m-* with a northern change to *b-*, and the report says which reading the entries favour.

No bench task scores a sound correspondence, and the study reads no Indus text, spends no part of the corpus and leaves `bench/spent.json` unchanged. The package attaches a `python -m bench selftest` output as a record of the harness version, as the root-meanings study did.

## Order of work

1. This file is hashed into `PROTOCOL.sha256` before any entry is read for the study.
2. We write the parser and counter in `code/` and test them on synthetic entries that reproduce the known traps: a label after a grammatical label in the same italic run, a bold cross-reference containing a label, a doubtful label, a borrowed form, a lettered sub-entry, and a repeated print.
3. A boundary check compares, for every entry, the language labels found in the flattened text of the entry with the lines the parser produced, for the Tamil, Kurukh, Malto and Brahui labels. We inspect the mismatches for parse errors only. Corrections are recorded in `PARSE-CHECK.md` with their reasons, and no rule above changes.
4. The code is hashed into `FREEZE.json`.
5. The frozen code computes the counts once into `results-v1/results.json`. A rerun goes to a new dated directory.
6. A second implementation, written from this protocol without the first implementation's code, recomputes the pass-rule counts and the primary table into `verify/`.
7. The report, the retrospective, the registry draft and a proposed record entry for C-0011 are written from those outputs.
