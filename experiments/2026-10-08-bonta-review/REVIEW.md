# Review of package Q (Bonta partial decipherment)

Reviewed 8 October 2026 against the committed package (commit aaaf76f, 47 files). Only this file and `review/` were written; temporary files were kept under `data/raw/2026-10-08-bonta-review/reviewer-tmp/` and deleted at the end.

## Verdict

The computed results stand. A fresh run of the frozen analysis code on the pinned inputs reproduced all six aggregate outputs (identical as parsed JSON; the manifest differs only in the protocol hash) and the seven local derivatives byte for byte, the package verifier passed 54/54 on that rerun, and a separate implementation of the lexical test written for this review reproduced 9/10, 13/720, 3/720, both 720-assignment histograms and the 35 prefix classes. The registered protocol, whose hash the run manifest records, precedes every output. The problems are in interpretation, in the source-history audit and in the claim ledger. The most important is the lexical tail: all 13 assignments that score at least 9/10 keep Bonta's own PU value bundle, none of the 600 that move it does, and eight of the ten panel strings contain PU or PATI, values Bonta says he found by searching this dictionary against those same contexts. The report states that the panel is Bonta-selected but not that its dominant role was derived from the panel strings, so 13/720 is easier to read as support than it should be. Three further corrections are required. The fish-run result (757 runs, no repeat, none longer than three) cannot discriminate anything, because no selected text has more than three fish-code tokens and only three texts repeat a code. The audit's "conflicting label" (ICIT 2717 against M-1714) is a parser artefact, and only one of the three confirmed repeated objects is an ICIT-first reading entry. Of 52 ledger records checked, 30 are fair as stated and 22 need correction, among them one claim that is not in the cited passage (Q016), three stated more strongly than Bonta states them and three stated more weakly.

## Numbers checked

Evidence paths are relative to the package directory. "Rerun" means `review/rerun-01/`; "independent" means `review/review-checks.json`.

| Claim | Evidence | Result | Note |
|---|---|---|---|
| 2,469 objects, 10,835 tokens, minimum text length 2 | `run-2026-10-08-v1/distributions.json` | confirmed | rerun identical; independent recount agrees |
| Jar (740) final 838/1,196 = 70.07%, bootstrap 67.43–72.79% | same, `populations.longest_eligible_object_faces` | confirmed | my own 2,000-draw object bootstrap gives 67.43–72.60 (different seed) |
| Arrow (520) final 192/225 = 85.33%, 80.51–89.57% | same | confirmed | |
| Shuffle: jar mean 280.315 (252–308), arrow 54.415 (43–67), q 0.0003 | `principal_reference_tests` | confirmed | analytic expectations 280.24 and 54.45; max of 500 fresh shuffles for the jar was 319 |
| 001 q 0.72552, 002 and 032 q 0.0003, 033 q 0.9998 | same | confirmed | rerun identical |
| Population table 5,680/19,946/1,928; 2,930/11,952/1,247/876; 1,784/8,304/883/643 | `populations`, `all_faces` | confirmed | |
| MS pair 117 (shuffle mean 20.444, 13–29) | `MS_pair_proxy`, `distribution-sensitivities.json` | confirmed | `review/role-pair-census.json` independently lists 117 objects with MA immediately followed by TRA |
| Fish 757 runs, lengths 629/121/7; compound sensitivity 751 (619/123/9, 67 absorbed, 1 ambiguous) | `fish_proxy`, sensitivities | numbers confirmed, interpretation discrepancy | see Distributional tests |
| Mayig clear subset 100/98/477; fish runs 26/4/1; jar 36/45; arrow 11/13 | `clear_Mayig` | confirmed | |
| U-plus-stroke proxy: 154 objects; 3/35/61/35/0 | `U_stroke_proxy` | confirmed | |
| 286,525 k1 rows, 194,059 headwords, 171,644 classes, 32 excluded | `run-2026-10-08-v1/lexical.json` | confirmed | independent parse of the pinned file |
| 9/10; permutation mean 4.858; 13/720 = 0.0180556 | same | confirmed | histograms identical |
| Exact endpoint 9/10; mean 3.933; 3/720 = 0.0041667 | same | confirmed | |
| 35 prefix classes; range 18–60 over 20 three-suffix sets | `consistency_intersection` | confirmed | first draft of my own code gave 38 because it treated `mahA` as a different suffix from `maha`; fixed, then 35 and 18–60 |
| 734 occurrences, 628 MH-primary, 106 ICIT-primary, 76 distinct, 54 single-family joins | `validation.json` | confirmed | rerun identical |
| 3 confirmed, 1 conflicting, 2 false overlaps | `validation-audit.json` | discrepancy | see Validation audit |
| 8 same-entry ICIT-to-MH references (7 without a question mark) | same | confirmed | all eight located in segments 90–167 |
| 126 records; 58 Table 18 entries; 10 reading types; 6 Lecture 12 tests | `claims.jsonl` | confirmed | counts by type agree with `ledger-coverage.json` |
| 47 sources; 17 mappings; 33,133 s = 9:12:13 | `sources.json`, `concordance.json`, `input-checks.json` | confirmed | |
| G fits 13.716 g (CV 1.591%, n 90) and 14.280 g (5.777%, n 147) | `mass-band-estimates.json` | confirmed | |
| D2: 874/1,256 = 69.59% | `terminal740.json` | confirmed | |
| Verification 54/54 | `verification-final.json` | confirmed | reproduced by running `verify.py` on my rerun |
| Zero usable inscription-to-quantity joins | `metrology.json` | unverifiable by rerun | consistent with the inputs I inspected |

## Claim ledger

I checked 52 of 126 records against the caption blocks and paper segments at their cited locations: 11 myself, and 41 through two read-only subagents. I re-read the primary text for every record listed below except Q022, Q024, Q035, Q036 and Q044. Thirty records are fair as stated (Q002, Q007–Q009, Q014, Q017, Q023, Q026, Q027, Q031, Q033, Q037–Q040, Q043, Q045–Q050, Q054, Q071, Q090, Q101, Q104, Q123–Q125). The 22 below need correction. A common fault is an `offered_evidence` field that describes a different passage from the cited one. Every `quotation` field is null, although categorical wording matters for several records, and the test id `E1` does not exist in the protocol.

| Record | Problem | Correction |
|---|---|---|
| Q016 | Unsupported. L05 10:25–15:04 and paper segments 38–40 show recurring C fields concatenated into one longer C field and read as a noun compound. Nothing is reordered and no suffix contrast appears. | Replace with the concatenation claim. |
| Q013 | Stronger than L09. At 9:21–12:49 Bonta says he doubts the ticks are case endings and offers honorific or benefactive as a tentative guess. "Case-like" comes from paper segment 20 and L10 5:00 (Q014). | Split by source. |
| Q042 | Stronger. L11 19:26–23:40 offers two options (an approximate spelling or an earlier form), says "I'm not saying this is necessarily absolutely the case", and closes by leaving the judgement to the listener. | "Proposes as a possibility"; the range should end near 24:00. |
| Q015 | Mis-described. Paper segments 34–35: positional frequencies of CV syllables in Monier-Williams and the Cologne Tamil lexicon were matched against sign dossiers, and the match failed for both languages apart from a handful of signs. It was not an exhaustive search for readings. | Rewrite. |
| Q041 | Weaker. At L11 14:10 Bonta asserts without qualification that the language has prepositions; he also says the signs are not strictly prefixes (about 11:00). | State the categorical assertion. |
| Q034 | Weaker. L10 3:13–3:36 calls such seals "necessary and sufficient" and says they cannot reasonably be interpreted otherwise. | Quote it. |
| Q053 | Weaker. The letter, PDF p. 5, says the ICIT cross-check "invalidated only a couple of previously-proposed sign values"; it does not say "small modifications". Lecture 7 (23:36) reports one value pulled. | Use the letter's wording; the report's chronology note then concerns one against two or more values. |
| Q011 | Wrong location. The MS pair is defined in segment 20 and tied to mātra in 52–53; segments 21–25 cover fish tables. "Mortar/pestle" is in neither source (Bonta says a stick in a vessel, L04 3:34, L06 3:13). | Fix locator and gloss. |
| Q010 | Misstated. L06 1:50 and segment 20: the oval subfield has at most two non-repeating members of a set of three. No ordering restriction is stated. | Rewrite. |
| Q025 | Conflated. L07 5:28–11:34 uses three lists (X+dana, X+ma, X+pala) and a fourth criterion, that X is common as a final or suffix element. `tra` enters only in segment 71, where bhūtra is not a word. | Separate the two passages. |
| Q018 | Wording right, hedge missing. L05 28:58–29:41 says attested Dravidian does not allow compounding "in any form", then adds that an earlier phase may have had these features. Segment 41 hedges similarly. | Record the hedge beside the categorical sentence. |
| Q003, Q005, Q006, Q020 | Evidence field or range wrong: "sign crowding" is in no caption or paper text (Q003); Q005 cites Indus patterns where L03 56:37–59:40 gives English and mathematical examples only; the P-M-C-T order in Q006 is at L04 36:28, before the cited range; Q020 cites "comparison with known weight systems", which L06 1:27–4:58 lacks (the paper makes that comparison in segment 23). | Correct fields and ranges. |
| Q021 | The seven-unit series is Marshall's. Bonta rates his hypothesis very likely on the count of entries and the absence of repeats; "ordering" is not an argument in segment 23. | Correct evidence. |
| Q072 | Table 18 lists `DAna1` and `DAna2`, not an entry labelled DHANA. | Correct label. |
| Q022, Q024, Q035, Q036, Q044 | Subagent-only. Ranges cut off the main evidence (the pala/pāla homophony at L06 12:03–13:53; the bow/bowman distribution at L06 19:30–21:58; temples as banks in L10; the genitive-descendant argument in L11 to 40:05); Q036 cites a sacrificial vocabulary that appears at L10 30:10, outside its range. | Extend ranges and fix evidence. |

The Lecture 12 criteria (Q045–Q050) match the captions at 4:17, 12:07, 28:36, 37:10, 41:42 and 46:18. In the report's application table, "He reports changing his candidate language" overstates L12 40:17, where Bonta says he was "forced by the preponderance of data" to adopt Indo-Aryan as a hypothesis after four or five coincidences. Yajnadevam's 2024 manuscript states that Bonta tried Dravidian for years and then changed, which supports the report's phrase as a secondary account.

At Lecture 7, 22:12–24:37, the ledger is fair. The report's gloss "no contradictory unreadable material" does not follow the caption, which reads "nothing that was not readable, nothing that contradicted my results". Two readings are possible, that no attempted inscription was left unreadable or that no readable one contradicted him. The first would imply no failures at all, so the report should quote the caption and give both readings. The first pass reads this passage as "a dozen to fifteen readable examples and a correction", which agrees with the ledger.

At Lecture 5, 28:36–29:48 the ledger records the categorical sentence correctly. The Cambridge chapter summary confirms noun-plus-noun compounds in Dravidian. It does not measure the productivity of multi-member compounds, which is what the paper's own wording (segment 41, "wholesale compounding of multiple nouns") concerns. The report separates the paper's weaker claim from the lecture's, which is the right treatment.

## Lexical permutation test

**Timing.** `mw.txt` was downloaded at 20:07:56 and the letter at 20:08. `PROTOCOL-registered.md` (mtime 20:11:13, sha256 a3c874b7…) already contains the pre-outcome clarification that names the six roles and ten strings. The frozen code (20:14:40) is byte-identical to `analyze.py`. `selection.json` is dated 20:15:04, `manifest.json` 20:15:13 and the outputs 20:15:33–38. The manifest records the registered protocol's hash, which is stronger evidence than the modification times, since `PROTOCOL-registered.md` is a copy. The post-outcome amendment (20:30:48) is labelled as such. The files cannot show that no exploratory dictionary lookup preceded 20:11, and the panel was written after the contributor had read the paper's Tables 13–17. `RETROSPECTIVE.md` is consistent with this order and records the failed 47/54 verifier run.

**Panel and values.** All ten strings occur in segments 52–53 and 67–75 with the readings listed, and the six value bundles match Table 18 (segments 78–81) exactly, including `maha` restricted to word-initial position. The panel is complete for Bonta's introductory illustration. A08 matches only through *balapati*, which Bonta himself argues for (segment 75), and A06 through *putra* with the value pu (segments 71–72). Two annotations in `selection.json` are wrong: the paper's own entries give MH2109 as M-1688 and MH2348 as M-958 (segment 95), where the A06 note says M212 and M898. Scores are unaffected. Segments 95–96 also call MH2348 doubtful because its strokes are short and refer MH2564 back to it, so Bonta's own support for the PU-TRA string is thin. In the pinned corpus the cited H-467 and M-320 carry DHANA-PALA and M-314 carries DHANA-PALA-PATI as listed. Of the three PU-TRA objects (M-1688, M-958, M-979), only M-1688 shows PU followed by the three full-height strokes; the other two show PU followed by a short-stroke sign, as the paper notes.

**Match rule.** The per-role value lists are reproduced exactly. The normalized endpoint then collapses vowel length, stop voicing and aspiration and retroflex/dental n over every generated form and every headword. That is broader than Table 18's per-role lists and follows Bonta's remark at L07 16:54 that signs often do not distinguish these. The exact endpoint stays inside Table 18. All nine observed matches are exact, so normalization only loosens the null: the permutation mean rises from 3.93 to 4.86 and the tail from 3/720 to 13/720. With vowel length alone the tail is 8/720, with length and aspiration 11/720. The rule is narrower than Bonta's in one respect: he also draws names from the Cologne Purana Index (segments 142 and 154) and accepts unattested compounds, neither of which is modelled.

**Dictionary.** The pinned commit 55e8addb… and the file hash 555ecf5a… are recorded. The repository root carries a CC BY-SA 4.0 LICENSE (sha256 0b7fc260…) and GitHub lists it as the repository licence. The repository README, the file header and the CDSL home page state no per-dictionary licence, so the record rests on the root file. The data stay local, so the current handling triggers no share-alike obligation. Bonta's letter (p. 2) says he used the same Cologne Monier-Williams.

**Conditioning.** The report places "Bonta selected these examples and values during development" in the same paragraph as the tail, which is the right position. It does not say that the PU and PATI values were obtained by searching the dictionary against the other roles' contexts (segments 69–74, L07 5:28–11:34), nor that the tail depends on one role. These reviewer sensitivities were written after the outcome and are Exploratory (`review/review-checks.json`):

| Variation | Result |
|---|---|
| Normalized tail among the 120 assignments that keep PU; among the 600 that do not | 13/120; 0/600 |
| Exact tail among the 120; among the 600 | 3/120; 0/600 |
| PU and PATI held at his values, other four roles permuted (24 assignments) | exact 2/24, normalized 8/24 |
| Strings containing PU or PATI | 8 of 10 |
| Ordered adjacent pairs of the six roles attested in the 2,469 objects | 20 types: 9 in the panel, all matching exactly; 11 outside it, 3 matching |
| Those 11 outside pairs under random assignments | mean 4.9 exact matches; 686/720 assignments score at least 3 |

The last two rows show where the match advantage sits: in the strings Bonta selected. They do not refute him, since an unselected adjacent pair may cross a word boundary. The 35 prefix classes omit his fourth criterion (final or suffix use), and 14 of the 35 are two characters or fewer, so they are not comparable with his estimate of three or four candidates (L07 10:52).

## Distributional tests

The jar and arrow results reproduce. The report says the final claims "reproduce", but at L04 45:40 Bonta says the jar sign "always always always" occurs in the T context, with a couple of exceptions on Middle Eastern seals. In this population 358 of 1,196 jar tokens (29.9%) are not final, in 355 objects: 189 at Harappa, 129 at Mohenjo-daro and 15 at Lothal. Two signs (400 and 090) follow 241 of the 358. The final-position preference reproduces and the near-categorical statement does not. The protocol requires exceptions to categorical rules to be reported, and the report omits them. The failed 001 and 033 endpoints are reported correctly.

For the fish proxy, no face in the 5,680 observed faces has more than three fish-code tokens, so a run longer than three cannot occur under any arrangement. Only three selected texts contain any fish code twice, so the expected number of repeating runs under within-text shuffles is 0.81 and the probability of zero is 0.39. The "zero repeats, none longer than three" result therefore carries no evidence about clustering. Fish codes do cluster: 140 texts have at least two fish tokens and contain 135 adjacent fish pairs, against a shuffle mean of 54.6 (95% range 44–65, maximum 74 in 2,000 draws). This is a reviewer-added test on the package's population and codes.

## Validation-set audit

I located all six parser overlaps and the eight same-entry references in the paper segments.

| Item | Finding |
|---|---|
| ICIT 3084 / M-634 / MH2069 | Same object (segments 86, 94, 147 and 216). Segment 216 prints the combined label "MH2069/ICIT 3084/M-634", so the ICIT occurrence there is an alias inside an MH-first entry, not an ICIT-first example. |
| ICIT 3656 / M-1357 / MH2356 | Same object with the same reading (192, 212, 122). This is the one confirmed ICIT-first reading entry for an object already listed under an MH number. |
| ICIT 2816 / M-296 / MH1387 | Same object. Segment 165 is prose about iconography, so no reading overlaps. |
| ICIT 2717 / M-1714 | Not a conflicting label. Segment 185 reads "M-192/ICIT 2717, M-1714/ICIT 2346, and M-279/ICIT 2800" in one parenthesis, so the parser attached M-1714 to the wrong ICIT number. The paper pairs M-1714 with ICIT 2346 consistently (segments 141, 158, 185). This is a third parser false overlap. |
| ICIT 1802 and ICIT 415 | Parser false overlaps from adjacent unlabelled entries, as recorded. The H-1832 / MH4266 reverse question is a genuine catalogue ambiguity that I could not resolve. |

The corrected tally is three confirmed repeated objects, zero conflicting labels and three parser false overlaps, with the type of each confirmed object stated. The eight same-entry references (ICIT 1114, 1562, 1802, 2135, 2260, 2646, 3355 with its question mark, 3506) are accurate and are the stronger evidence that ICIT-first entries concern objects Mahadevan listed. None of this identifies the lecture's 12–15 readings, and the report says so. The commit message of aaaf76f says "three claimed validation readings concern objects already in the development catalogue", which the audit does not support.

## Letter-based sign mappings

Letter page 2 shows the pala forms, the digraph (three strokes plus a U with a central stroke), the bowman, and the square with an upper stem. Page 4 shows the pati diamond forms. The Mayig descriptions in `mayig_sign_schema.json` fit each: P316 U with a central stroke, P147 three full-height strokes, P086 branching staff, P035 person with bow, P276 square with a bar on top, P385 diamond or leaf with a small diamond on top. The identities rest on matching text descriptions, not on comparing glyph images with the corpus. PALA is the loosest: the letter shows two forms and P086 pools six Wells codes. The report labels the mappings as one reader's provisional annotation, which is accurate.

## Sources opened

| Source | Route | Result |
|---|---|---|
| IMSc Annual Report 2014–2015 | local PDF text | Confirmed. PDF p. 88 gives 4–5 May 2015; pp. 91–92 list "Dr Steven Bonta (Penn State University, Altoona)" among invited speakers. |
| Bonta introductory letter | local text and images, pp. 1, 2, 4, 5 | Six signs and the Cologne dictionary confirmed; p. 5 wording differs from Q053 (above). Undated, hosted by a third party. |
| Krishnamurti, *The Dravidian Languages*, ch. 6 | Cambridge page via subagent | Abstract confirmed: compound stems with a noun head and noun, adjective or verb modifier; *kaṇ-ṇīr* "tear", literally eye-water. The page shows online publication in 2009 and pp. 205–276; `sources.json` gives 2003 for the book. |
| Morpurgo Davies, "Decipherment" | rendered scan, p. 420 | Confirmed: a pure etymological approach is "dangerous"; a decipherment is tested on results; coherence and geographic compatibility. |
| Rao 2018 | local text | Confirmed: partition into patterned and complex texts "following Wells and Bonta"; fish signs linked by Bonta to minas or maashas; terminal function. Printed page numbers not rechecked. |
| Yajnadevam 2024 | local text | Confirmed: bibliography gives 105163460 with a 13 September 2023 archive; text reports Bonta's change from Dravidian. |
| Sengupta 2023 | local text | Confirmed: *Studia Orientalia Electronica* 11(1), 86–102; Bonta 2010, pp. 57–59 on mina. Page 90 not checked. |
| Language Log post 68508 | local HTML | Confirmed: 6 March 2025 post; Rehbein's chance-hit comment quoting a YouTube commenter; Schwartz "unconvinced by both". |
| Fairservis 1992 | local text | Confirmed: suffix, honorific, numeral and storage passages at the cited PDF pages. |
| Mahadevan, *The Indus Script* | local HTML | Confirmed: "Parpola's Methodology of Decipherment" lists the four conditions, which Mahadevan attributes to Parpola. The report attributes them to the essay; say "as reported by Mahadevan". |
| Mukhopadhyay 2019 | Nature page via subagent | Title, journal, year confirmed; no sound values assigned. The category counts were relayed by a summariser and are unchecked. |
| Khanna and Merriam 2025 | IJCA page via subagent | Confirmed: volume 187, number 64; Bonta 2010 is reference 7. Body citations not checked. |
| Cologne MW, `csl-orig` | local file, WebFetch | Licence as above. |
| Kalyanaraman 2024 | HTTP 403 | Unverifiable. A search snippet relayed by a subagent calls the item a tribute to Bonta's functional classes, which does not support "challenges the step to metrological and phonetic readings". Not confirmed either way. |

Snippet-only and failed sources (`B15-wedge`, `B23-requested`, the two videos, `Elst23`) are marked as such in `sources.json`.

## Reproduction log

| Command (outputs in `review/` or `reviewer-tmp/`) | Result |
|---|---|
| `prepare_inputs.py --raw-directory reviewer-tmp/derived --output review/input-checks-rerun.json` | 260 segments, derivative identical, 12 captions, 33,133 s, no manuscript PDF |
| Copy of `analyze-v1-frozen.py` with three path lines changed (`review/analyze-path.diff`, so that nothing is written into the package), `--run rerun-01`, 19 s | six aggregate JSON files identical to `run-2026-10-08-v1` (the manifest differs only in the protocol hash); the seven local derivatives byte-identical, checked by `verify.py` below |
| `verify.py` against that rerun | 54/54 |
| `audit_validation.py`, `extend_distributions.py` with outputs in `review/` | byte-identical to the package files |
| `review/review_checks.py` (independent lexical, distribution, fish, role-pair code; 3 min 37 s) | numbers above |
| `review/role_pair_census.py` | 20 attested ordered role pairs |
| `python tools/review_prose.py --path experiments/2026-10-08-bonta-review --no-write` | 6 files, 0 flags |
| `git status --porcelain` | the only change from this review is `review/`; the other entries (`knowledge/INDEX.md`, `registry.json`, `public-image-audit`, `site-map-and-overview`, the first pass) were there before |

I did not rerun `package_checks.py` (24/24) or the acquisition script. The README's commands write into the package directory, so I ran patched copies as described.

## Scope, rights and writing

No page claims decipherment or presents a sound or meaning as established, and the structural work is credited where the tests reproduce it. A 7-gram overlap scan of every tracked file against the captions, the paper text and the letter finds only the paper's title inside URLs. The 58 Table 18 records carry short value labels that together restate the table, which the task required and which the owner may want to note against `REDISTRIBUTION.md`. The Lipi data and per-text outputs stay in the ignored `data/` tree.

The prose scan is clean, but the reader-facing problems remain. The opening of `REPORT.md` uses terms such as "elementary fish proxy", "conditional tail fraction" and "retained code" without explanation, and it does not rank the evidence by strength. The report has nine corrective "not X" clauses (lines 15, 39, 59, 87, 104, 110, 125, 156, 160) that `WRITING.md` discourages. The first sentence of `README.md` calls the proposal "an early Indo-Aryan logosyllabic script"; the proposal is that the script records an early Indo-Aryan language. Its final section addresses reviewers.

## Required fixes, ranked

1. Rewrite the lexical result in the opening of `README.md` and `REPORT.md` to say that PU and PATI were found by dictionary search against the panel strings, that eight of ten strings contain them, and that every assignment reaching 9/10 keeps the PU bundle. Add a dated erratum for the A06 CISI labels in `selection.json` and a sentence that the normalized rule is broader than Table 18.
2. Correct the validation audit in `validation-audit.json` (as a dated successor file), `REPORT.md`, `README.md`, `RETROSPECTIVE.md` and `registry-entry.json` before the coordinator integrates it: ICIT 2717 is a parser false overlap, and each confirmed object should be described by entry type.
3. Remove the fish-run result as support for structural distinctions, in the opening, the fish paragraph and `registry-entry.json`. State that the text counts make it uninformative, and optionally add the adjacency result.
4. State Bonta's near-categorical jar claim (L04 45:40) beside the 29.9% non-final figure and describe the exceptions.
5. Correct the 22 ledger records above, add short quotations for the categorical statements (Q018, Q034, Q041, Q013), and record the L04 45:40 claim.
6. Fix three wordings: the letter's statement that the ICIT cross-check invalidated a couple of sign values, the Lecture 7 caption ambiguity, and the Lecture 12 "changing his candidate language" row.
7. Rewrite the opening of `REPORT.md` as a plain summary that ranks the parts of the evidence, and remove the repeated corrective clauses.

## Optional improvements

- Add the Cologne Purana Index as a second name source and report the effect on the panel.
- Use the attested role-pair census as the denominator for any later panel, with the pairs fixed before scoring.
- Record both the 2003 print year and the 2009 online date for Krishnamurti; reopen Kalyanaraman and quote what it says about Bonta.
- Give the scripts an `--output-root` option so a reviewer can rerun them without writing into the package.
- Add `E1` to the protocol or rename the test id.

## Not checked

The captions were not compared with the audio. The 74 ledger records outside the sample were not read. No full manuscript PDF was available, so glyph identities rest on the letter. I cannot show that no exploratory lookup preceded the registered protocol. The Mukhopadhyay and Khanna pages were read through a summarising tool.
