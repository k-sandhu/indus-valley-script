# Follow-up for package Q from the coordinator: apply the review

A Claude Sonnet reviewer reran your package and wrote `REVIEW.md`, with scripts and outputs in `review/`. Read and reuse them, but do not edit them. Every computed number reproduces, including an independent reimplementation of the lexical test, and the protocol hash precedes the outputs. The problems are in interpretation, the validation audit and the claim ledger. Read the review in full and add a dated amendment to `PROTOCOL.md`. Then apply the required fixes without changing the frozen run outputs, writing any new computation to new dated paths:

1. **Lexical result.** State the following in `REPORT.md`, `README.md` and `registry-entry.json`, as the review documents in `review/role-pair-census.json`:
   - All 13 permutations that score at least 9/10 keep Bonta's value for the PU sign, and none of the 600 that move it reaches 9.
   - Eight of the ten panel strings contain PU or PATI, whose values he reports finding by searching this dictionary against those same contexts.

   The tail fraction is therefore close to circular for those signs. Report a sensitivity that drops or holds fixed the dictionary-derived roles, as a new labelled calculation. Say whether the normalization is broader than his Table 18 value lists; all nine observed matches are exact. Add an erratum for the two wrong catalogue numbers in the `selection.json` note: M212 and M898 should be M-1688 and M-958. Record which PU+tra objects show the sequence in the corpus.
2. **Validation audit.** ICIT 2717 against M-1714 is a parser artefact, because the paper pairs M-1714 with ICIT 2346 throughout. Reclassify it as a third parser false overlap. Of the three confirmed repeated objects, report that only ICIT 3656 is an ICIT-first reading entry. ICIT 3084 is an alias inside an MH-first entry, and ICIT 2816 appears only in an iconography remark. Correct `validation-audit.json` through a new versioned file, and correct the report, README, retrospective and registry entry.
3. **Fish result.** Withdraw the "zero repeats, none longer than three" observation as support for structural distinctions, because it cannot discriminate. If you report fish clustering, use the adjacency test the review describes (135 adjacent pairs against a shuffle mean of 54.6) as a new labelled calculation.
4. **Jar and arrow.** Beside Bonta's categorical statement in Lecture 4 at 45:40 that the jar always occurs in the terminal context, report the exceptions: 358 of 1,196 jar tokens (29.9%) are not final, mostly at Harappa and Mohenjo-daro, and 241 are followed by sign 400 or 090. Do the same for the arrow. Say that the strong final tendency reproduces while the categorical form does not.
5. **Claim ledger.** Correct the 22 records the review lists:
   - Q016 is not in its cited passage.
   - Q013, Q042 and Q015 overstate Bonta.
   - Q034, Q041 and Q053 understate him.
   - Several other records have misdirected evidence fields or ranges.

   Add short quotations, at most 15 words, for his categorical statements. Fix the letter wording ("invalidated only a couple of previously-proposed sign values"), the Lecture 7 gloss and the Lecture 12 language-change row. Then check the 74 records outside the reviewer's sample against the captions or page text with the same care, and record how many changed.
6. **Kalyanaraman.** The page returned HTTP 403. Describe it only as far as you verified it, or mark it unverified.
7. **Opening.** Rewrite the first paragraphs of `REPORT.md` and the first line of `README.md` as a plain summary for the owner, ranked by strength of evidence:
   - what reproduces (strong positional tendencies, with their exceptions);
   - what is weak or circular (the lexical panel);
   - what cannot be judged from the available sources (the validation rate, the field boundaries, the physical metrology).

   Remove the "not X" constructions the review counts, and do not describe the proposal as established in any phrase.

Update `RETROSPECTIVE.md` and the file inventory. Do not write to `knowledge/INDEX.md`, `knowledge/experiments/registry.json` or the first-pass directory. Follow `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Finish with a short report of what changed.
