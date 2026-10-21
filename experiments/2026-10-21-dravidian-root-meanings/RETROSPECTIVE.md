# Retrospective: Dravidian root meanings

## Approach

We ran study 6 of the [Parpola direction note](../../knowledge/directions/parpola-forward-2026-10-20.md) in one day, 21 October 2026 (UTC). The protocol fixed the sixteen needed senses, the rule for each sense class, the coding of a tip as present, absent or missing, the language-to-tip mapping rule, the two reconstruction methods, the reference draw, the pass rules, the kill condition and the credence rule, and was hashed at 01:49 before any dictionary entry was opened. We then chose the entries by searching the DSAL edition of the dictionary, recorded them with an amendment at 02:00, and handed acquisition, parsing, tree reading, coding and the reconstruction code to Codex in two runs. After reviewing Codex's output against the source text and against the sense rules, we wrote the plain-reading recodes, froze the code by hash at 05:16 and computed once. An independent implementation of the primary model reproduced every root probability. The report, card update and registry entry were written from the frozen output.

## Challenges and repairs

**The search tool and the protocol disagreed.** The protocol told us to find entries by the dictionary's entry-word search. That search indexes only the first Tamil form of each entry, and Tamil *mīṉ* "star" sits inside entry 4876, headed *miṉ* "lightning", while entry 4885, *mīṉ*, gives only "fish". The literal procedure would have coded "star" absent in every language, Tamil included. We used the full-text search, recorded the change in [AMENDMENT-1.md](AMENDMENT-1.md) before any coding, and kept the literal procedure as sensitivity S7, which meets the kill condition by construction. A protocol that names a search tool should also name what to do when the tool cannot reach the rule's target.

**A mechanical rule missed plain meanings.** The class rules were written before any gloss was seen and coded "three things" as not "three" and an ornament "worn in the helix of the ear" as not an earring. We kept the rules for the primary analysis and fixed five recodes, by segment and hash, in [S8-RECODE.md](S8-RECODE.md) before computing. They changed no pass decision.

**A parser error would have changed a coding silently.** Codex's first parser attributed the Gondi forms of the entry for "three" to Gadba. Counting language labels in the flattened source text, independently of the parser, found it; Codex had repaired the same defect before its run ended, and a follow-up repaired a second case. The final parse agrees with the count for every chosen entry.

**The drive filled.** Several sessions downloading at once filled drive C: near the end of Codex's first run. Codex deleted its own regenerable cache and finished, but could not write its final message; we waited for space before freezing.

**The pass threshold was weaker than it looked.** The tree's root separates South I from all other branches, and the other side is sparsely attested in the dictionary, so a meaning found only in South I can exceed one half at the root ("north" reaches 0.677). The parsimony reconstruction and the 0.2 kill line carry more information than the 0.5 pass line on this tree. A future protocol on this tree should set its pass line by simulation of meanings confined to one branch.

## Outcome

P1, P2 and P3 passed and the kill condition failed; the frozen rule raised C-0011 from 0.15 to 0.35, and review set it at 0.20 because the homophone the pun needs reaches the root at 0.41 and the North node at 0.22, and because the northern star words may continue *viṇ* "sky". The study found that three of Parpola's senses, *vaṭam* "banyan", *piḷḷai* "squirrel" and *vēḷ* "Murukan", have no entry in the dictionary, and that Kodava *boḷḷi mi·nï* "morning star" is a "white star" compound of the kind Parpola reads as Venus. The next test, a count of northern *b-* against Tamil *m-* and *v-* across the dictionary, is recorded as C-0011 P5.

## Files

Protocol and freeze: [PROTOCOL.md](PROTOCOL.md), [ENTRIES.md](ENTRIES.md), [AMENDMENT-1.md](AMENDMENT-1.md), [S8-RECODE.md](S8-RECODE.md), [FREEZE.json](FREEZE.json). Code and tests: [code/](code/), [run1/](run1/), [TOOLS.md](TOOLS.md). Results and verification: [results.json](results-v1/results.json), [verification-v1.json](verify/verification-v1.json). Delegation: [CODEX-PROMPT.md](CODEX-PROMPT.md), [CODEX-PROMPT-1B.md](CODEX-PROMPT-1B.md), [CODEX-NOTES-RUN1.md](CODEX-NOTES-RUN1.md), [RETROSPECTIVE-CODEX.md](RETROSPECTIVE-CODEX.md). Sources and rights: [DATA-UPDATE.md](DATA-UPDATE.md). Local only: `data/raw/2026-10-21-dravidian-root-meanings/` (dictionary pages, parsed entries, codings, pools, downloads, logs and the per-tip detail of the results).
