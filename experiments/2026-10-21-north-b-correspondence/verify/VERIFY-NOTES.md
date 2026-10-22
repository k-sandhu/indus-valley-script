# Second implementation of the count (protocol step 6)

Written on 21 October 2026 by Claude Opus 5.5 (`claude-opus-5-5`), working as a subagent in the Claude Code desktop app for k-sandhu. We wrote [verify.py](verify.py) from [PROTOCOL.md](../PROTOCOL.md) and [PARSE-CHECK.md](../PARSE-CHECK.md) alone. We did not open the first implementation's code, its results, the parse-check output, the self-test, `FREEZE.json`, or the code of the rebus-base-rate and root-meanings studies. To learn the markup and check the parse we read raw DSAL HTML (among the Tamil *m-* and *v-* entries, 4673, 4876, 4952 and 5496) and printed the parsed Tamil, Kurukh and Malto forms of every part in the population. Forms and per-part tables are in `data/raw/2026-10-21-north-b-correspondence/verify-v1/` (local only). [verification-v1.json](verification-v1.json) holds counts, entry numbers and initial classes. The script's docstring gives the command; it runs under `python -I` with the standard library and takes about 50 seconds, most of it for the alternative readings.

## Result

The outcome under the pass rule is **unresolved**. Entry 4952 is the only entry other than 4876 with a Tamil *m-* part whose first undoubted Kurukh or Malto form begins with *b-*. In 4952 both northern forms begin with *b-* and carry no doubt mark. The pass rule needs two such entries. Entries 4876 and 4952 are also the only Tamil *m-* entries with any non-borrowed northern *b-* form, counting doubtful and non-first forms, so the failure condition does not hold either, although 41 Tamil *v-* entries have a northern first form in *b-*.

Of 374 parts whose first Tamil form begins with *m-*, 63 (63 entries, 62 without 4876) have a non-borrowed Kurukh or Malto form. For *v-* the figures are 278 and 44 parts (44 entries). The primary table counts parts by the initial of the first undoubted form, without 4876:

| Tamil initial | Language | *m* | *b* | *v* | other |
|---|---|---|---|---|---|
| *m-* | Kurukh | 45 | 1 | 0 | 2 |
| *m-* | Malto | 38 | 1 | 0 | 1 |
| *m-* | pooled | 83 | 2 | 0 | 3 |
| *v-* | Kurukh | 1 | 26 | 0 | 2 |
| *v-* | Malto | 1 | 24 | 0 | 1 |
| *v-* | pooled | 2 | 50 | 0 | 3 |

With 4876 the Tamil *m-* row gains one *b* in each language. In the 4952 part the first Tamil vowel is short back and is followed by a non-nasal consonant, and the first Telugu and Kannada forms begin with *m-* (the entry has no Gondi line). The only northern *m-* for Tamil *v-* among first forms is entry 5516, where the Tamil vowel is short front and a nasal follows; 5532 has northern *m-* forms after first forms in *b-*.

## How the parser reads the pages

The script checks all 514 pages against the SHA-256 values in `requests.jsonl` and stops on a mismatch. Before parsing it escapes every "<" that does not open a known tag, so DEDR's borrowing sign and a stray "<Santali" on page 1 survive as text. Bold and italic are tracked as depth counts per character, which resolves misnested tags such as `<i><b>Ta.</i> a</b>`; the counts restart at each `new_p` span, so an unbalanced tag (nine entries in the *m-*/*v-* range have one) cannot spread into the next entry.

Each plain `<div>` holding `new_p` spans is one print of an entry. A number printed more than once is kept as one entry when every print is a prefix of the longest, which holds for 94 of the 98 repeated numbers; the prints under 1287, 1288, 2835 and 5282 differ, and the later one is kept as a separate entry ("5282/2"), as PARSE-CHECK.md describes. Pages 509 to 514 hold 62 prints under 61 numbers, because a53 is printed twice. One number tag reads "4896(a)"; the script takes 4896 as the number and the letter as the first part marker. Tags such as "5400A" are kept as written.

A part begins at "(a)", "(b)" and so on when the marker stands immediately before an italic label that starts a line. Markers inside cross-references ("Cf. 5020(b) Ta.") follow an entry number and so mark nothing.

An italic run starts a line at every language label it contains, including a label after a grammatical label in the same run. We accept the misspellings "Kur" (1474, 3045), "Malt;" (4473), "Ta:" (3512) and "Ta," (4002) as labels; none lies in the population. Following correction 3, an italic label whose preceding text ends in a cue word (cf., esp., see, s.v., viz., i.e., e.g., also, "=") or in a number is a citation. That rule catches ten Tamil labels where PARSE-CHECK.md reports nine, and the Kurukh label in 969. A label in plain type that ends its plain run and is followed by a bold run starts a line when the five conditions of correction 1 hold: the text before ends in ".", ";" or ")", no cue word precedes it, it lies outside parentheses counted from the start of the current line, its language comes later in DEDR's order than the current line's, and the bold run holds a form. The six plain lines found among Tamil, Kurukh, Malto and Brahui labels are exactly those PARSE-CHECK.md lists (Brahui 55, 392, 753; Malto 392, 395, 1040). Any other plain label followed by a bold run is a citation, and that bold run gives no form (correction 2).

A part's lines end at DEDR's comparison notes: the first "/" outside bold with spaces on both sides, or with a space on one side when a capital, "?", "<", ">", "(" or "[" follows, or the first DED, DEN or DBIA reference after which no italic label follows. Across the dictionary the cut removes three italic labels of the four languages: Tamil in 26, and Kurukh and Malto in the Indo-Aryan note of 1145.

Forms are the bold runs without italics inside a line, split at commas, semicolons and slashes after parenthesised groups are handled: a group attached to a letter is an optional letter and keeps its contents (so a bracketed initial *v* still counts as *v-*), a detached group is a stem or dialect note and is dropped, and "(?)" is kept as a doubt mark. Pieces that begin with a hyphen or contain no letter are dropped. Doubt, borrowing and initials follow the protocol's wording; the Tamil first form is also the first form that is not borrowed.

## Decisions where the rules left room

Each decision was rerun with the alternative reading; the results are in the `sensitivity` block of the JSON.

| Point left open | Our reading | Alternative run | Effect |
|---|---|---|---|
| Unbalanced tags | Style restarts at each span | Carried to the end of the page, as a browser renders it | One Kurukh *m* unit lost (5114, made italic by an unclosed tag in 5105); lists and outcome unchanged |
| Misspelt italic labels | Accepted | Canonical spelling only | None |
| Bold run opening with a label (a cross-reference such as "Cf. 5504 **Ta. …**") | Gives no form | Its text counts as a form | None |
| Bold run after an italic citation label | Gives no form | Counts | None |
| Correction 1 for languages other than the four checked | Applied to all languages | Only Tamil, Kurukh, Malto and Brahui | None |
| Slash variants ("/Cf.", "id./ Cf.") | Start the comparison notes | Only " / " | None |
| Detached parenthesised group inside a form run | Dropped as a note | Read as a further form unless it begins or ends with a hyphen | One Kurukh unit moves from *m* to other (4866, where a bracketed source name sits in leaked bold); lists and outcome unchanged |
| "?" after a run of several forms | Marks the last form of the run | Not run | Does not occur in a population line |

We also cross-checked the parse with a separate regular-expression scan of the flattened text, which looked for any bold word in *b-* after a Kurukh or Malto label in entries with a Tamil *m-* label. It found 4876, 4952 and one Indo-Aryan comparison word after the slash in 4673, which the parser correctly cuts.

## Entries the rules may mishandle

Entry 4952 qualifies under the rules, yet DEDR closes it with Sanskrit and Prakrit comparisons after the slash, and its Kurukh form is cited from the source marked "(BB)". That mark opens no other Kurukh line in the dictionary; 752 of the 806 Kurukh lines carry no source mark. The borrowing rule reads only "<", "borrowed" and "loan" inside the line, so an Indo-Aryan comparison set off by "Cf." after the slash never counts against a form. If the word of 4952 is taken as a loan, no entry other than 4876 shows northern *b-* for Tamil *m-*.

In 5052 the first Kurukh form begins with *n-* and an *m-* form follows, so the first-form rule counts the part as other although the entry has the expected *m-*. In 644 and 4392, which DEDR files under *u-* and *p-*, the Tamil line opens with a form in *m-* (a Tinnevelly dialect word in 644) and in *v-*, so the parts join the *m-* and *v-* groups; their northern forms count as other. In 4866 and 4886 an unclosed bold tag turns the rest of the entry into bold text, so glosses join the form list; the first forms are still right. In 5401 the rule removes a Malto *b-* form as borrowed because a note says the northern and central words may come from Indo-Aryan; this costs the Tamil *v-* list one entry and does not change the outcome.
