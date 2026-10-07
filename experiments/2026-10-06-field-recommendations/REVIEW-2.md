# Second review of Package F: field recommendations

Reviewer: Claude Sonnet 5.5, 7 October 2026. Package state reviewed: commit 09534a8, "Rebuild the field-recommendations survey from sources actually read". None of the package's existing files changed during this review. The first review is [REVIEW.md](REVIEW.md). Scripts and tables for this review are in `review-2/`.

## Verdict

The rebuilt catalogue can be cited at row level. In a random draw of 15 rows (seed 20261007, from the 54 rows outside a fixed set), all 15 state what their source says at the cited place. With the four lecture rows and the two Frenez 2018 items (F39 and the position row P01), 19 of 21 checked items are supported, 2 are partly supported and none is unsupported; the first pass had 7 of 33 supported. I also opened the cited passage for the other 39 rows. Across all 59 rows, 54 are supported and 5 say more than their source (F03, F04, F24, F53, F55). I found no error in the 35 source records, no byte-order mark or damaged character in the active files (words fused to numbers remain in 68 places) and no broken local link, and `build_tables.py --check`, the audit and the prose scan pass. Of the ten required fixes, eight are done, fix 7 is mostly done and fix 1 is partly done: the source's own words are stored for 1 of 59 rows, and the comparison entries reuse the same two passages on eight rows and include one self-comparison. The most important remaining problem is the lecture. F04 asks readers to study inscriptions found outside the Indus Valley, which the speaker does not ask, and rank 5 of the action list rests on it. F03 adds a sample-size control that comes from the coordinator's note. The report's themes, shared groups and two disputes follow the rows. Its ranks 3 and 5 do not, because they include rows that the package marks as limited or that overstate their source.

| Group | Rows | Supported | Partly supported | Unsupported |
|---|---:|---:|---:|---:|
| Random sample | 15 | 15 | 0 | 0 |
| Lecture rows F01 to F04 | 4 | 2 | 2 | 0 |
| Frenez 2018 (F39, P01) | 2 | 2 | 0 | 0 |
| Checked items | 21 | 19 | 2 | 0 |
| Other rows, one reading each | 39 | 36 | 3 | 0 |
| All 59 recommendation rows | 59 | 54 | 5 | 0 |

With 15 of 15 supported in the draw, an exact hypergeometric bound puts the share of fully supported rows in the 54-row frame above 81% at 95% confidence. The three weak rows found outside the draw (F24, F53, F55) are consistent with that bound. Every row's result and note is in [row-checks.csv](review-2/row-checks.csv).

## What I ran

1. `python experiments/2026-10-06-field-recommendations/build_tables.py --check` passed. It reports 59 rows, 35 sources, 35 witness hashes, 8 repository links, 8 exports identical byte for byte, 19 preserved first-pass files unchanged and 29 active files with clean encoding.
2. `audit_catalogue.py` rewrites five package files (coverage counts, row ledger, audit checks, roster coverage and the manifest), so I ran it on a copy under the scratchpad, with the repository's `data/`, `research/` and sibling experiment folders linked for reading only. One line of the copy needed a change: the local-link check had to normalise `..` before testing a path, because my scratch path exceeds the Windows path limit once `..` is kept. With that change the audit wrote the same bytes as the package for four of its five outputs. FILE-MANIFEST.json differs only in the entry for the patched script (5,415 bytes in the package, 5,456 in the copy). The audit checked 59 local Markdown links and 50 acquisition hashes.
3. `python tools/review_prose.py --path experiments/2026-10-06-field-recommendations --no-write` scanned 13 files and reported 0 flags, the same result as `prose-check.json`. With this review added it scans 14 files and still reports 0.
4. [draw_sample.py](review-2/draw_sample.py) reproduces the sample (Python 3.13.5; [sample.json](review-2/sample.json)): F09, F11, F13, F19, F22, F23, F27, F37, F41, F42, F44, F45, F50, F51, F58. The frame excludes F01 to F04 and F39, which are checked separately.
5. Sources. I read the cited passages in the package's local witnesses. Nine of the PDFs at the cited URLs (Wells, Fuls, Parpola, Yadav, Farmer-Sproat-Witzel, Vahia, Sproat 2013, Rao 2015, Rajan-Sivanantham) matched their witnesses by first-page text. I read Possehl's Penn page live in a browser pane, because the package's script received 403 and used proxy text; the live text is identical. I read the lecture's English auto-captions in the browser pane (3,390 s and 7,055 words, the same counts as the coordinator's note). I checked ten DOIs in Crossref and Rao 2018 on arXiv, and requested all 35 source URLs ([url-status.json](review-2/url-status.json)).

## Sampled rows

Supported means the row states what the source says at the cited place. Partly supported means the source says something narrower or different, or reports a finding that the row turns into a request. Unsupported means the source does not contain the statement.

| Row | Source and locator | Result | Note |
|---|---|---|---|
| F09 | Fuls 2023, IITGN abstract booklet, p. 45 | supported | Fuls's own database aims at worldwide access and updates after new publications. An author's plan, worded in the row as advice. |
| F11 | Kenoyer 2020, p. 223 | supported | Producer marks and user marks on pottery need to be separated in future work. |
| F13 | Kenoyer 2020, p. 230 | supported | Asks for finer recording and counting of marks made before and after firing, on pottery and other objects, region by region. The row narrows this to pottery marks. |
| F19 | Yadav 2013, pp. 96-98 | supported | Page 98 concludes that interpretive models must treat site and object type as sources of variation in the signs. |
| F22 | Parpola 2008, p. 127 | supported | Iconic meaning has to be settled before rebus readings are considered. A premise argued inside a rebuttal of Farmer, Sproat and Witzel; restated faithfully. |
| F23 | Farmer, Sproat and Witzel 2004, p. 37 n. 23 | supported | Future Indus work depends on rare-symbol studies, which bear on how the system worked and was controlled. The Parpola (pp. 113-115) and Vidale (conclusion) comparison entries also match. |
| F27 | Sproat 2010, p. 592 | supported | Sets an evidence standard for classifiers: they must separate a large set of known linguistic and nonlinguistic systems with high accuracy. A condition rather than advice; restated faithfully. |
| F37 | Mukhopadhyay 2023, p. 29 | supported | Leaves to future studies whether stamped pointed-base goblets were standardized administrative vessels. |
| F41 | Petrie and Lynam, accepted manuscript, lines 656-658 | supported | Sees much to learn about how settlers lived from local subsistence, geomorphology and hydrology. The locator is the accepted manuscript, not published pagination. |
| F42 | Petrie and Lynam, accepted manuscript, lines 675-678 | supported | Suggests further models of mobility and of sedentary and pastoral relations in Cholistan. The theme is coded computational method although the models describe behaviour. |
| F44 | Law 2011, p. 503 | supported | Studying the northern borderlands needs new data from question-led excavation or re-excavation, with Ropar, Manda, Musa Khel and Hisham Dheri named. |
| F45 | Law 2011, p. 503 | supported | Law's plan for a long-term sourcing program with scholars in India, Pakistan and elsewhere. The row words it as an instruction. |
| F50 | Possehl, Penn page describing Indus Age: The Writing System | supported | Principle 2 of three: many small-scale studies of the script. A description of the 1996 book on the author's page, undated, without page numbers; read live. |
| F51 | same page | supported | Principle 3: test decipherment claims through independent lines of inference. |
| F58 | Green 2021, p. 183 | supported | Proposes asking whether the Indus had more heterarchical corporate groups than early societies with exclusionary elites, and why. |
| F01 | Frenez lecture, 30:05-30:25 | supported | Captions 30:08-30:30: earlier efforts were by single scholars, and he proposes team work across kinds of expertise. |
| F02 | Frenez lecture, 24:45-25:40 | supported | Captions 24:36-25:12: regional corpora are not yet attempted but feasible, and the corpus has so far been treated as one block with no chronological or geographical split. The coordinator's note describes this; the captions make it a suggestion. |
| F03 | Frenez lecture, 28:45-30:40 | partly supported | At 29:00-29:15 he says how sign inventories vary with site size (over 500, 100-200 and 20-50 signs) could be investigated further in the context of use. The assemblage-size control is the coordinator's rarefaction gloss, and sign 740 at 10% (29:20-29:50) is reported as a finding. The row's limitation credits sample-size questions to the talk; the captions have none. |
| F04 | Frenez lecture, 51:00-53:00 | partly supported | Captions 51:00-52:50 describe non-canonical sequences outside the valley and two readings of two frequent signs, introduced as an interesting closing point. The talk contains no request to study them; the imperative is the package's. |
| F39 | Frenez 2018, printed p. 186 n. 11 | supported | The footnote says Wengrow's branding assumptions need more testing and a stronger theoretical frame before use here. |
| P01 | Frenez 2018, pp. 186-187 | supported | The oligopoly argument as a position row: unicorn at about 65% (Ameri 2013, table 19.1) and persistence over more than six centuries. The report describes it correctly. The lecture makes the same argument at 41:10-43:50. |

## Rows outside the sample

Three of the other 39 rows say more than their source. F24 gives the Farmer-Sproat-Witzel caution (p. 43 n. 28) as applying "before linking Near Eastern seal symbols to users", while the footnote applies the Near Eastern second-hand seal problem to the symbols on Indus seals. F53 turns Rao's expectation that the number system might be partly reconstructed into an instruction, and the tally-mark and weight-ratio method is the reporter's hedged description. F55 relays a colleague's remark about repetitive studies of plant and animal remains, with Ratnagar's comment that archaeology should take it seriously; the subject is excavation sampling, remote from the script. Two rows match their source but carry a defect. F10 cites a paragraph "beginning Since the inscribed artifacts" that does not exist (the sentence ends the paragraph that begins "A special issue"), and the comparison entry on F06 cites Wells's own Preface.

Six rows record the author's own plan or aim and not advice to the field (F09, F21, F31, F43, F45, F46). The README admits "stated project aim" rows, so they are within the rule, but no field separates them.

## Lecture rows against the captions

The English auto-captions confirm the package's timestamp windows to within 10 seconds for F01 to F04. They support F01 and F02 as explicit suggestions and the core of F03 (investigate the site-size gradient in context), and they do not contain the request that F04 states. The oligopoly passage (41:10-43:50) and the statement that Indus people probably rejected influence from other scripts (53:25-53:45) agree with positions P03 and P04. I did not re-read the windows that P04 and P05 cite at 16:20-24:00 and 48:25. The captions are machine-generated and garble names, as the coordinator's note says. Details are in [caption-check.csv](review-2/caption-check.csv).

## Status of the first review's ten fixes

| # | Required fix | Status | Evidence |
|---|---|---|---|
| 1 | Rebuild unsupported and partly supported rows from sources read; give each row the source's own words (under 15 words) and a page; keep the gloss separate | Partly done | All 33 first-pass rows have a disposition (28 rebuilt, 5 dropped), and all 59 rows have a page, line, paragraph or timestamp. The source's own words are stored for one row (F57); the other 58 hold paraphrases in `recommendation`. |
| 2 | Correct 14 source records; resolve Miller; replace dead URLs | Done | All 14 corrections hold: 10 records corrected or replaced (Miller's real project page among them) and 4 dropped, with the right bibliography kept in `source-corrections.json`. The other 25 records match their title pages, running heads or Crossref on title, authors, year and venue (I did not check the editors of Ameri 2013 or the series note for Law 2011). 31 of 35 URLs resolve; the other 4 are DOI links (PNAS, MIT Press twice, Taylor and Francis) that return 403 to scripts and resolve in Crossref. No Wright, Shinde, Bisht or Parpola-profile URL remains. |
| 3 | Repair encoding; write JSON without ASCII replacement; regenerate CSV; add a check | Done | 29 active files: 0 byte-order marks, 0 invalid UTF-8, 0 replacement characters, 0 mojibake sequences, 0 letter-question-letter patterns ([scan-results.json](review-2/scan-results.json)). Diacritics survive. The builder rejects each of these. |
| 4 | Lecture rows from the caption check; written Frenez parallels | Done, two rows overstate | Timestamps are those of `frenez-talk-check.md`. P02, P07, P01 and F39 cite printed pp. 167, 170-171, 186-187 and match the chapter. Deliberate rejection stays a position (P04) with no written source. F03 and F04 are the two rows that overstate. |
| 5 | Correct the report and README statements; list roster members without a supported recommendation | Done | README line 5 says 22 of 25; REPORT line 26 places the oligopoly at pp. 186-187, line 51 removes the Wells claim about corpus updates, line 53 states Fuls's per-site artefact counts, line 103 names Wright, Shinde and Bisht. |
| 6 | Fix two repository links; repoint Sproat and Vahia rows | Done | 8 of 8 distinct links resolve. The regional-west link now targets `REPORT.md`. Sproat rows F27, F29 and F30 link `research/literature/nonlinguistic_controls/README.md`. The Vahia rows link D2, H and G; `knowledge/retrospectives/methods.md` is not linked. |
| 7 | Replace `comparison_source_ids` with opened sources and locators; add the published replies | Mostly done | 50 comparison entries on 37 rows, each with locator, relation and statement. The replies by Rao (2010, 2015), Parpola (2008), Vidale (2007) and Sproat (2010 and counterreply) are opened and the entries match them. Defects: the same Wells (pp. viii-ix) and Yadav (pp. 97-98) pair is attached to eight rows (F02, F06, F10, F13, F17, F35, F40, F47); on F06 the Wells entry cites Wells; F17 is compared with a paper that shares an author; the entries on F40, F45 and F47 match by topic only. |
| 8 | Save fetched pages or hashes with access dates; reuse local witnesses first | Done | 51 acquisition records with path, bytes, SHA-256, UTC time, route and HTTP status; 21 reuse existing local witnesses; 5 failed responses and 2 unusable 200 responses are recorded. Each source record carries its hash and log path. |
| 9 | Add the Exploratory label to rows and report | Done | 59 of 59 rows have `status` Exploratory; REPORT, README and RETROSPECTIVE carry it. |
| 10 | Re-save `registry-entry.json` without a byte-order mark | Done | No byte-order mark; strict JSON parsing succeeds; the nine fields match the registry's. |

## The report

**Themes.** The theme counts (9, 21, 4, 7, 8, 10) equal the row counts. Nine rows are discussed under a heading that differs from their theme (F09, F29, F33, F34, F35, F41, F42, F45, F53), and F26, F47 and F50 are not cited, so the headings do not map one to one onto the table's counts.

**Shared groups.** Each group the report names matches the rows I read. Six authors or groups prescribe chronological, regional or site and type control (Wells, Kenoyer, Rao 2009, Yadav, Fuls, Konasukawa), with Frenez's F02 as a seventh voice. Wells and Fuls worked together on Wells 2015 (Fuls wrote the appendices and the software), and Rao 2009 and Yadav 2013 share an author, so the six come from four groups. Five sources seek cooperation or access (Wells, Kenoyer, Vidale, Fuls, Frenez), with the same Wells and Fuls overlap. Rao, Possehl, Yadav and Vahia overlap on corpus definition and sign variants, as the report says. The report does not count independent sources per recommendation, and the table has no field for it. The comparison entries carry the status (26 rows have a shared-priority entry, 11 a dispute or difference, 22 none), but a reader cannot see that per row.

**Disputes.** The report records two debates with opened replies: the non-writing thesis (Parpola 2008 pp. 111-115 and Vidale 2007 pp. 361-362 against Farmer, Sproat and Witzel) and statistical classification (Sproat 2010 against Rao and coauthors 2010 and 2015, with Sproat's counterreply). I read every cited passage and the relation labels fit. The report confines both disputes to the thesis or the inference and leaves the recommendation itself (rare-sign study, grammar induction) outside the dispute, which is accurate. One disagreement from the first review is still unlabelled: Rao's hope for excavated bilingual texts (F54) and Gokhale's objection to the search for bilinguals both appear in the report without a link between them.

**Ranked actions.** The D2 figures match the D2 files (1,928 of 19,946 positions is 9.67%, 1,928 of 18,067 readable positions is 10.67%, and 1,246 of 1,609 known square-seal motifs is 77.44% unicorn), and the six linked packages exist and their READMEs report the kinds of input the table names. Ranks 1, 2, 4, 6 and 7 follow from rows that match their sources. Rank 3 cites F58 and F59, which the package's own feasibility field marks Limited and which ask about corporate groups, not motif stability. Rank 5 rests on F04 and F24, and both overstate their sources. Rank 7 includes F53. Six of the 36 rows in the table (F03, F04, F24, F53, F58, F59) are partly supported or limited. The report names three criteria (available inputs, value of resolving an uncertainty, dependence on specialists or field access) but shows no scores, so the order of the ranks cannot be reproduced.

## Method, scope and reproduction

The amendment file was created at 00:49, before the first acquisition record (00:50) and before `curation.py` (01:07). `PROTOCOL.md` carries dated sections for the later additions (the continuation after the disk interruption, Green 2021 and the Lothal 2005 record). The package makes no claim of decipherment or of a sound or meaning assignment, attributes the lecture positions to the speaker, and states in F08 that candidate-language readings cannot be authenticated here. The only text stored in a `quotations` field is nine words long (GREEN-2021).

The exporter asserts the SHA-256 of all 35 witnesses. Those files sit under `data/` and `research/literature/sources/`, which `.gitignore` excludes, so `build_tables.py` cannot run in a fresh clone, and two REPORT links (the acquisition log and the Frenez PDF) do not resolve there. This follows the repository's local-only rule. The README says the scripts use "existing witnesses" without saying they are untracked.

## Writing

The prose scan reports no flags. Reading the files, I found three problems.

1. REPORT.md uses a negation to correct an impression the reader has not formed in ten sentences (lines 5, 11, 13, 51, 55, 57, 63, 69, 81, 99). Line 5 says that the counts "do not measure a vote across the field". The writing rules ask for shared assumptions in one methods block.
2. The mediated-lecture caveat appears in README (lines 12 and 37), REPORT (lines 17, 28, 51 and 105), RETROSPECTIVE (lines 19 and 35) and three fields of the registry entry. The captions have now been read directly, which removes the need for most of these.
3. Words are fused to numbers in 68 places across 8 files, and 112 compact locators read the same way. Examples: "about65%", "Ameri2013", "Table19.1", "before2800BCE", "opened2023", "Read2020text223,230-231 and visually read2006scan printed21". The strings are in `curation.py` and `build_tables.py`, so the exports carry them. README.md and REPORT.md are clean; RETROSPECTIVE.md has four.

## Remaining required corrections, ranked

1. **F04 and F03.** Move F04 to `positions.json` as an observation (Frenez reports non-canonical sequences outside the valley and notes two interpretations), or cite a passage where he asks for the study. Reword F03 to what the captions say (investigate how sign inventories differ with site size, in the context of use, 29:00-29:15), keep the rarefaction control as the package's implementation note, and delete the credit to the talk for sample-size questions in its limitation. Update REPORT lines 19-24 (lecture table), line 47 (Frenez's lecture "emphasizes external inscriptions"), rank 5, and the counts in README, REPORT, `summary.json` and the registry entry if F04 leaves the table. Cite the caption windows directly.
2. **F24.** Say that the second-hand seal problem documented for the Near East must be weighed before the symbols on Indus seals are linked to their users, and revise the rank 5 description of F24.
3. **REPORT ranks 3 and 5, and the ranking basis.** Remove F58 and F59 from rank 3 or describe the action they support. Rebuild rank 5 from rows that survive items 1 and 2. State how the seven ranks were ordered, or show the scores.
4. **Comparison entries.** Delete the F06 self-comparison. Replace the repeated Wells and Yadav pair on F02, F10, F13, F17, F35, F40 and F47 with the passage that matches each row's proposition, or remove it (22 rows already have none). Drop the F17 to Yadav 2013 entry or state the shared author. Add per-row `shared_or_disputed` and `n_independent_sources` fields so the report's groups can be audited.
5. **Source's own words.** Store a short verbatim anchor (under 15 words) with each row, at least for rows that rest on one sentence (F22, F25, F27, F45, F46, F49 to F51, F53, F55). Only F57 has one.
6. **Locators and fused tokens.** Correct the F10 paragraph label. Put spaces between words and numbers in the strings of `curation.py` and `build_tables.py`, and regenerate the exports. Add a fused-token check beside the existing encoding check.
7. **F53 and F55.** State F53 as Rao's expectation that part of the number system may be recoverable, or drop it. Drop F55 or move it to coverage as a general remark on archaeological practice.
8. **Prose.** State the lecture caveat once, in the evidence section of REPORT.md, and remove the ten corrective sentences or fold them into one methods paragraph.
9. **Theme and heading alignment.** Align the nine rows whose REPORT heading differs from their theme, and cite F26, F47 and F50 or say why they are omitted.

## Optional improvements

- Add a `kind` column (advice, priority, own plan) so that F09, F21, F31, F43, F45 and F46 are counted separately.
- Label the Rao 2026 and Gokhale 2023 disagreement over excavating for bilingual texts.
- Link `knowledge/retrospectives/methods.md` on the Sproat and Vahia rows.
- Move maintenance notes out of `limitation` (F21 and F46 mention the first pass). `repository_status` is the same sentence in 58 rows and `limitation` is empty in 30; fill them with row-specific content or drop them.
- State in the README that the exporter needs the untracked witnesses.
- Use one line-ending convention: 16 active files are CRLF, 12 are LF and `PROTOCOL.md` has both. `.gitattributes` disables conversion, so the mixture persists.

## Not checked, and boundaries

I did not search for recommendations by Wright, Shinde or Bisht, who remain gaps. Neither the package nor this review has read Sproat's 2014 main article or Possehl's 1996 book. Vidale 2007 was read from the Scribd copy of the JSTOR text that the package holds. The 39 rows outside the draw and the lecture set received one reading each. `git status --porcelain` for the package lists only `REVIEW-2.md` and `review-2/` as new. The first-pass folder is byte-identical to commits afd3b95 and f0c966c (19 of 19 files). The scratch copy of the package, which linked to repository folders for reading, was deleted.
