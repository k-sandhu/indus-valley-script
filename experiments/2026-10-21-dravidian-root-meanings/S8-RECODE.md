# S8 plain-reading recodes

Recorded on 21 October 2026 (UTC), after the codings had been read for parse errors and before the code was frozen and any root probability, parsimony score or reference statistic was computed. [AMENDMENT-1.md](AMENDMENT-1.md) defines S8: we read every needed meaning's coding against its glosses and list each segment that the frozen class rules code differently from a plain reading. S8 recodes these segments and reruns the analysis; it does not enter the pass rules.

We read the glosses of every tip coded 1 and every tip coded 0 for the sixteen needed meanings. No tip coded 1 was wrong on a plain reading. Five tips coded 0 carry the meaning:

| Meaning | Entry | Tip | Gloss | Why the rule missed it |
|---|---|---|---|---|
| THREE | 5052 | Kurukh | "three persons", "three things" | The rule requires the segment to be the numeral alone; these glosses add the class of thing counted. |
| THREE | 5052 | Parji | "three things", "three men", "three women" | As above. |
| THREE | 5052 | Kolami | "three things", "three men", "three women", "three days" | As above. |
| EARRING | 4979 | Tamil | an ornament worn in the helix of the ear | The head rule takes "helix" as the head. |
| SPACE | 5498 | Malayalam | "open field" | "Open field" is an open space but not among the class's listed phrases. |

We considered and left unchanged: Malayalam "Subrahmaṇya" under YOUTH (a name of the god, not the sense "youth"), Telugu "Himalaya" under NORTH (the compound contains the word for north, but the gloss names a mountain range), Malto and Brahui "moon" and Kolami "light" under WHITE, and the "female of animals" and "woman" glosses under CHILD.

The local file `data/raw/2026-10-21-dravidian-root-meanings/codex-run1/manual-recode.json` addresses each segment by meaning, entry, form index and segment index with the SHA-256 of its normalised text, so the recode fails if the parse changes under it.

One observation outside the coded entries belongs here because it bears on the homophony question. Entry 5496 (a), the entry for "white", gives Kodava *boḷḷi mi·nï* "morning star", a compound of the words for white and star in which the second member has the same form as the Kodava word for fish in entry 4885. The S4 homophone test, which requires the star form itself to begin with *min*, does not count it. It is an exploratory observation and enters no rule.
