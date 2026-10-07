# Review of Package F: recommendations from Indus researchers

Reviewer: Claude Sonnet 5.5, 7 October 2026. The package files were unchanged from 00:04 to the end of this review (committed in afd3b95). Supporting tables and scripts are in `review/`.

## Verdict

The CSV regenerates byte for byte and the repository figures the report quotes are correct, but the attribution of recommendations to named researchers does not hold up, and the table cannot be cited as it stands. Of the 33 rows, 7 state something the cited source says; 9 are partly supported (the source says something narrower or different, the sentence is the paper's method presented as a recommendation, or the suggestion belongs to a reviewer); 8 attribute to Parpola, Vahia, Mahadevan, Ameri, Green, Wright, Possehl and the RMRL institution a recommendation that the cited source does not contain; 5 attribute nothing and say so; and 4 lecture rows rested on the user's notes, which the coordinating session has since confirmed from the captions. Fourteen of the 31 source records have a wrong title, author list, year, venue, URL or attribution, and the Heather Miller record could not be found at all. Five files carry encoding damage: `README.md`, `REPORT.md`, `recommendations.json`, `recommendations.csv` and `sources.json`. The report says no Frenez publication was found for the "unbalanced oligopoly" claim, yet it is argued at printed pp. 186-187 of a chapter the package lists as an opened PDF. The package's main direction, that sign sequences should be tied to dated, regional and contextual records, stands and is better supported than the table shows. Wells's Preface, Fuls's 2023 abstract, Rao et al. 2009, Kenoyer 2006 and 2020, Konasukawa's 2023 abstract and Yadav 2013 each argue for at least one of those links. The most important problem is attribution: 17 rows need repair before anyone cites a named researcher from this table.

## Checked claims

| # | Claim | Evidence path | Result | Note |
|---|---|---|---|---|
| 1 | 33 recommendation rows | `recommendations.json`, `recommendations.csv` | confirmed | 33 objects and 33 data rows. |
| 2 | 31 source records | `sources.json` | confirmed | The 33 rows use 27 distinct title-and-URL pairs. `FRENEZ-2005`, `FRENEZ-2024` and `KENoyer-MEADOW-2010` appear only as comparators, and the Green row carries Frenez's chapter title instead of `GREEN-2016`'s. |
| 3 | 11 snippet-only, 6 citation-only, 1 failed search | `source_access` in `recommendations.json` | confirmed (row level) | The counts come from the package's final summary; the files do not state them. Source level is 8, 7 and 1. |
| 4 | `build_tables.py` regenerates the CSV | reproduction log below | confirmed | Byte-identical. It covers only the JSON-to-CSV step. |
| 5 | 5,680 records, 4,695 families, 19,946 token positions | `experiments/2026-10-02-dataset-landscape/README.md`, `landscape.json` | confirmed | Same figures in `main-v1/local-input-audit.json`. |
| 6 | 22 Harappa short-record objects, 66 faces | `experiments/2026-10-02-six-hour/context-audit/README.md` | confirmed | Copied tablets H2218-H2239: 22 objects, 66 faces, all two-sign, none in the 3-sign sample. |
| 7 | ICIT access is requested, not bulk-open | `experiments/2026-10-02-dataset-landscape/README.md` | confirmed | |
| 8 | Contribution assessment treats Yadav et al. 2010 as a precedent | `experiments/2026-10-06-contribution-assessment/REPORT.md` | confirmed | |
| 9 | Five priorities, six themes | `REPORT.md` | confirmed | Themes exist only as REPORT headings; rows have no theme column. |
| 10 | "Verified publication years range from 2000 to 2026" (L57) | `sources.json` | discrepancy | The range is arithmetically right, but years are wrong for Frenez 2017 (published 2018), the Salūt paper (2016, not 2022) and Petrie (2020, online 2019). The Fuls record gives the book's year for a 2023 abstract. |
| 11 | "No available source ... establishes a common exposure denominator" (L19) | Fuls abstract, IITGN booklet p. 45 | discrepancy | Fuls compares sign frequencies with those expected from the number of artefacts excavated at each site. |
| 12 | The search "did not verify publications stating the reported unbalanced oligopoly" (L5) | Frenez 2018, printed pp. 186-187 | discrepancy | Defined and applied to seals; also p. 167 (indigenous tradition) and p. 170 (script derived from Harappa graffiti, introduced 2800-2600 BC). |
| 13 | Three Frenez publications "provide separately checkable recommendations" (L5) | `sources.json` | discrepancy | None of the three records a recommendation. The Lothal abstract has none, and the other two have wrong titles, years or venues. |
| 14 | "Wells and Fuls explicitly stress maintaining and updating a comprehensive corpus and sign list" (L11) | Fuls p. 45; Wells Preface | partly confirmed | Fuls says it. The Preface does not say it of Wells. |
| 15 | Wells Preface: regional variation and multiple languages need chronological control (L11) | Wells 2015, p. viii | confirmed, with a shift | The text says they need further work, and that without chronological control the developmental characteristics of the script are unlikely to be understood. |
| 16 | Kenoyer calls for better collation and publication of marks across sites (L17) | Harappa essay; PDF printed pp. 230-231 | confirmed | |
| 17 | Rao et al. 2009 final paragraph (row 10) | PNAS 106(33), Discussion | confirmed | The same passage also proposes a site-by-site analysis, which the row omits. |
| 18 | Rao's statements on longer or bilingual texts and a number system (L39) | Live Science, 15 March 2026 | confirmed | `sources.json` names the wrong author. |
| 19 | Roster gaps are Ratnagar, Possehl, Vidale, Bisht and Miller (L55) | `recommendations.json` | discrepancy | Possehl's row attributes a recommendation instead of recording a gap. Shinde's row is empty and unlisted. Seven more rows carry unsupported statements: Parpola, Vahia, Mahadevan, Ameri, Green, Wright and RMRL. |
| 20 | Lecture title confirmed; transcript, date and venue not obtained | YouTube page; `experiments/2026-10-06-research-program/frenez-talk-check.md` | confirmed | Title and ILARA-EPHE channel confirmed. The coordinating session later read the captions (posted 3 October 2026, 56:30) and confirmed each point of the user's summary. I did not re-read them. |
| 21 | Repository links resolve | `repository_link` | discrepancy | 1 of 18 distinct paths is missing, `experiments/2026-10-02-connections-and-priority/regional-west/README.md` (rows 2 and 4). The Sproat and Vahia rows link the null-calibration README, which concerns synthetic observation laws and not nonlinguistic comparison systems. |
| 22 | Protocol preceded outcomes | file times; git history | partly | Disclosed. Searches preceded `PROTOCOL.md` (saved 00:01:25). The first table snapshot (00:02:54) had 31 rows and no `comparison_source_ids`; the final tables date from 00:04:39 to 00:04:59. |
| 23 | All 33 rows and the synthesis are marked Exploratory (`AMENDMENT-2026-10-06.md`) | rows; `REPORT.md` | discrepancy | Neither the rows nor `REPORT.md` carry the label. README and the registry entry do. |
| 24 | `registry-entry.json` has the registry's fields | `registry-entry.json` | confirmed, one defect | All nine fields present. A UTF-8 BOM makes a strict `json.loads` fail; the main registry has none. |
| 25 | Prose passes the repository scan | `python tools/review_prose.py --path ... --no-write` | confirmed for the script | 6 files scanned, this review included, 0 flags. Manual reading finds repeated caveats and contrasts (see Writing). |

## Reproduction log

1. `python experiments/2026-10-06-field-recommendations/build_tables.py` was run on a copy in `data/raw/2026-10-06-field-recommendations/tmp/rerun/`, because the script writes beside itself. It printed "Wrote 33 recommendation rows." The CSV hash, `eae1a95b63067ce2a024ca34578fb942e26835ca1a53643bcb33d0c4a6a12d5e`, equals the package CSV.
2. Row counts, source counts and access labels were recomputed from the JSON. Row-level labels: snippet-only 11, opened HTML 9, citation-only 6, opened PDF text 4, opened bibliography 1, opened catalogue 1, failed search 1. Source-level labels: snippet-only 8, opened HTML 7, citation-only 7, opened PDF text 5, opened abstract 1, opened catalogue 1, opened bibliography 1, failed search 1.
3. `review/encoding_scan.py` scanned every package file and the committed snapshot (`review/encoding-scan.json`).
4. `review/url-status.json` holds header-only status codes for the 30 distinct URLs. Three return 404 (Wright, Rajan, Shinde landing page), one gave no response (Bisht), three return 403 to automated requests (Frenez 2024, the Smithsonian record, the Parpola profile), and the Google Scholar entry is a search URL.
5. The three harappa.com PDFs cited by the package have the same byte lengths as the copies in `research/literature/sources/` (22,194,691; 2,056,271; 5,054,373), so I read the repository copies. The Kenoyer 2006 copy is an image scan; I read it by OCR.
6. Source routes are listed per record in `review/source-checks.csv`. Several pages were read through a text proxy, which returns a summary rather than exact text. Every discrepancy reported here has either a primary-text reading or two agreeing routes.
7. The package could not be reproduced beyond the CSV: no code produces `recommendations.json` or `sources.json`, and the raw directory `data/raw/2026-10-06-field-recommendations/` was empty, so no page, hash or access date was saved.
8. `review/build_row_audit.py` and `review/build_review_tables.py` write `row-audit.csv`, `source-checks.csv` and `missing-recommendations.csv`. The verdicts and notes are typed into the scripts from my readings, so the scripts regenerate the tables and do not recompute the findings.

## Encoding damage

Five files are affected; the other package files are clean. The question marks that end the real titles "Private Person or Public Persona?" and "Will the Indus Valley script ever be deciphered?" are correct.

| File | Damaged items | Examples | Introduced |
|---|---|---|---|
| `README.md` | 3 mojibake sequences, line 5 | the opening and closing quotation marks around the lecture title and the apostrophe in "user's" show the Windows-1252 pattern, each starting with U+00E2 U+20AC | final rewrite; the 00:02:54 snapshot is clean |
| `REPORT.md` | 3 question marks, line 5 | the apostrophe in "user's" and the two quotation marks around "unbalanced oligopoly" are question marks | final rewrite; snapshot clean |
| `recommendations.json` | 24 | 15 possessive apostrophes (the Kenoyer, Sproat, Tosi, Possehl and Frenez possessives among them); 6 en dashes in ranges (13685-13690 twice, 1-5 twice, 457-481, 19-57); the dash in Indus-Oman; the é in Méry twice | present in the 00:02:54 snapshot (20) and carried forward |
| `recommendations.csv` | the same 24 strings | generated from the JSON | as above |
| `sources.json` | 9 | two possessives (a locator note and the Law title), the é in Méry, the dash in Indus-Oman, and five ranges (13685-13690, 1-5, 19-57, 457-481, 1986-2007) | present in the snapshot (8) |

The JSON contains no non-ASCII character at all, which indicates it was written through an ASCII or code-page path that replaced every unmappable character. `README.md` and `REPORT.md` show the pattern of UTF-8 text read as Windows-1252 and saved again. Fixing the five files and adding a check to `build_tables.py` (reject "?" between letters or digits, and U+00E2 followed by U+20AC) would prevent a repeat.

## Source checks

I checked 31 records. Fourteen are confirmed (two by bibliography only), fourteen contain at least one error, and three could not be verified (Wright, Ratnagar, Bisht). Thirteen of the errors are in this table; the fourteenth, `POSSEHL-2002`, follows it.

| Record | The package says | Verified |
|---|---|---|
| `FULS-2022` | "Corpus of Indus Inscriptions", Archaeopress, 2022, at the IITGN abstract URL | URL is the booklet of the IIT Gandhinagar colloquium of 10-12 February 2023; Fuls's abstract is "A Digital Corpus and Epigraphical Database for Indus Script Research", p. 45. Archaeopress is unsupported: Harappa's book page gives no imprint, and Archaeopress published Wells 2015, which carries Fuls's appendices. |
| `KENoyer-2006` | in *Between the Empires* | RIHN Kyoto volume of 2006 edited by Osada Toshiki (the cover of the scan). The PDF has no text layer. |
| `FRENEZ-2017` | "Stamp Seals as Visual Identifiers of Formal Socio-Economic Roles", 2017, Archaeopress, in *Seals and Sealing in the Ancient World* | "Private Person or Public Persona? Use and Significance of Standard Indus Seals as Markers of Formal Socio-Economic Identities", in *Walking with the Unicorn* (Archaeopress and ISMEO, 2018), printed pp. 166-193. |
| `FRENZEZ-OMAN-2022` | "Seal and sealing with Indus script", 2022, in *Bronze Age Indus Connections* | Frenez, Degli Esposti, Méry and Kenoyer, "Bronze Age Salūt (ST1) and the Indus Civilization: recent discoveries and new insights on regional interaction", *Proceedings of the Seminar for Arabian Studies* 46 (2016) 107-124. The package's title is a section heading on p. 116. The id has a typo. |
| `FRENEZ-2005` | *Mesopotamia* 40 | *Studi in onore di Enrica Fiandra* (De Boccard), pp. 65-103. |
| `FRENEZ-2024` | "Sealings, storage and social organization at Lothal" | "Were the Cretulae (Clay Sealings) from the Indus Town of Lothal Part of an Administrative Archive? Contextual, Interpretative, and Comparative Evidence", *South Asian Studies* 40(2), per Frenez's CV. |
| `GREEN-2016` | "Operational sequences and stamp seals ...", *J. Archaeol. Sci.: Reports*, at Frenez's PDF | Green 2016 is "Finding Harappan Seal Carvers: An Operational Sequence Approach to Identifying People in the Past", *J. Archaeol. Sci.* 72:128-141. The package's title is a 2018 chapter in the Cambridge volume it lists as `AMERI-2018`. |
| `YADAV-2010` | Yadav, Vahia, Joglekar, Rao, Mahadevan, Adhikari | PLOS ONE order: Yadav, Joglekar, Rao, Vahia, Adhikari, Mahadevan. |
| `SPROAT-2014` | URL `aclanthology.org/J10-3012.pdf` | That URL is Sproat 2010, *Computational Linguistics* 36(3). The 2014 article is *Language* 90(2):457-481. |
| `RAO-2026-INTERVIEW` | by Michael Philip Oakes (interviewer) | Live Science, 15 March 2026, by Owen Jarus. Oakes (Wolverhampton) is a researcher quoted in it. The page did not show Rao's statements to be an interview. |
| `PETRIE-2020` | Petrie and Catherine R. Green, *Journal of Archaeological Research* | Petrie and Frank Lynam, *Journal of Field Archaeology* 45 (Cambridge repository metadata). |
| `MILLER-2013` | "The Indus Script and the Origins of South Asian Writing", 2013, Oxford Handbook of the Archaeology of the Levant | No such record found. The URL is a Google Scholar query. Miller's own page describes a 2025 project on record-keeping technologies. |
| `RAJAN-2025` | recommendation attributed to the authors; PDF URL | The book exists (Government of Tamil Nadu Department of Archaeology, 2025). The URL returns 404. Deeper comparison with graffiti from Indus cities, other regions and further excavation are a Harappa.com reviewer's suggestions; the authors caution that similarity does not mean the same people made the signs. |

`POSSEHL-2002` is the fourteenth error: Mukhopadhyay 2023 (p. 2) cites "Possehl 2002 p. 138" for flawed decipherment methods, which the row turns into a Possehl recommendation. The three PDFs labelled "opened" whose titles, years or venues disagree with their own title pages (`KENoyer-2006`, `FRENEZ-2017`, `FRENZEZ-OMAN-2022`) were probably assembled from search excerpts. `FARMER-2004` is labelled "text not opened" but the PDF opens.

## Attribution accuracy

`review/row-audit.csv` gives a verdict, the source's statement and the locator for every row. Counts: 7 supported (rows 5, 7, 8, 10, 11, 27, 32), 9 partly supported (6, 14, 15, 16, 17, 20, 25, 30, 31), 8 not stated in the cited source (9, 12, 13, 18, 19, 21, 23, 26), 5 empty by the package's own statement (22, 24, 28, 29, 33), 4 lecture rows (1-4). Four patterns account for the problems.

1. The sentence is the paper's method presented as a recommendation: Mukhopadhyay 2019, Sproat 2014, Petrie, Frenez 2018, the Salūt paper.
2. A catalogue or institution description is read as a recommendation: Ameri, RMRL, Parpola (an author profile page).
3. The package supplies the sentence. The Mahadevan row cites Yadav et al. 2010, which contains no such recommendation. The Vahia row duplicates the Rao source with a copied locator and cites "Nair 2026", which is not in `sources.json`. The Possehl row restates the project's rule, and its `repository_link` is `AGENTS.md`.
4. `comparison_source_ids` was added after the first snapshot and matches names in the free-text agreement field to source ids. Nine rows list the same five Frenez sources, including the unretrievable video and the citation-only 2024 paper, whatever their topic; 17 rows list at least one comparator that was never opened. The column therefore makes agreement look sourced. The final pass also replaced the Green row's title with Frenez's.

Two rows misstate a source's position. Mukhopadhyay 2023 says a researcher should first narrow the semantic scope and only then study individual signs; the row says "compare proposed semantic domains against archaeological evidence". The Sproat row says Sproat "contests inference from statistical metrics", but his 2014 paper proposes two statistical measures and classifies the Indus inscriptions as nonlinguistic with them. Rao et al. (*Language* 91(4), 2015) and Rao et al. (*Computational Linguistics* 36(4), 2010) are the published replies to Sproat; the package cites neither.

## Roster coverage

Twenty-five researchers are named. Every one has a row, but only six have a row whose statement I confirmed in the cited source: Kenoyer, Wells, Fuls, Rao, Yadav and Law. Seven are partly supported: Sproat, Farmer and Witzel (through one paper, whose research priorities at pp. 37, 43, 44 and 46 the row misses), Mukhopadhyay, Petrie, Rajan and Frenez (written rows). Twelve have no recommendation or an unsupported one. The report lists five of the twelve.

| Researcher | Package row | Source I found for the next pass |
|---|---|---|
| Parpola | not stated in source | "Is the Indus script indeed not a writing system?", *Airavati* (2008) pp. 111-131: a logo-syllabic script of the Sumerian type; reply to Farmer, Sproat and Witzel |
| Vidale | empty | "The Collapse Melts Down: A Reply to Farmer, Sproat and Witzel", *East and West* 57(1-4):333-366 |
| Possehl | not stated in source | *Indus Age: The Writing System* (1996), Possehl's Penn page: an authoritative sign list, many small-scale efforts, and independent lines of inference to test claims |
| Mahadevan | not stated in source | Ganesan, Subramanian, Babu and Mahadevan, "The Indus Script: Text and Context" (2010): frequent signs, pairs and triplets by site, object type and field symbol |
| Vahia | not stated in source | "Understanding the Harappan Script: going beyond grammar and language", BITS Scripts 2025 slides 34-35, 47 |
| Ameri | not stated in source | "Regional diversity in the Harappan world: the evidence of the seals", *Connections and Complexity* (2013) pp. 355-374 |
| Green | not stated in source | "Finding Harappan Seal Carvers", *J. Archaeol. Sci.* 72 (2016): five Mohenjo-daro seals, three carvers, preliminary insights into communities of practice |
| Miller | empty | University of Toronto Mississauga page: a 2025 project to identify possible Indus bureaucracies or record-keeping centres from technological data |
| Wright, Ratnagar, Shinde, Bisht | not stated or empty | No recommendation located in a bounded search; Bisht's 2015 Dholavira report exists but its URL is dead |

## Missing recommendations

`review/missing-recommendations.csv` gives 16 sources with locators. The ones that bear most on the user's Frenez summary and on packages D1 and D2:

1. Frenez, "Private Person or Public Persona?" (2018), pp. 186-187: an unbalanced oligopoly in which one component, the unicorn at about 65% of seals, holds the absolute majority; a limited, consistent set of firms or brands regulated by legal or cultural prescriptions. Footnote 6 on p. 171 says no systematic study yet gives the share of high-fired steatite seals. The chapter gives the same definition and instability argument that the caption check records at 41:30-43:30.
2. Fuls, IITGN booklet p. 45: a modified chi-square test of sign frequencies against expectation from per-site artefact numbers; inscribed artefacts should not be treated as one homogeneous set.
3. Wells 2015, Preface pp. viii-x: do not mix the corpus into a monolithic unit; define regional differences in text structure; progress needs international and interdisciplinary cooperation.
4. Yadav 2013 (*SCRIPTA* 5:67-103) and Ganesan et al. 2010: sign usage by site and object type, with a call for a more holistic, context-linked approach.
5. Rao et al. 2009, Discussion: a site-by-site analysis to see whether sequential patterning differs by region.
6. Farmer, Sproat and Witzel 2004, pp. 37, 43, 44, 46: rare-symbol studies; the second-hand seal problem before linking seal symbols to users; sign-frequency fluctuations as indicators of social change; the symbols' role in cohesion.
7. Kenoyer 2020, pp. 223 and 230-231, and 2006: more excavation of Early Harappan sites; recording and quantifying pre- and post-firing marks by region; collaboration and accessible data; re-examining earlier-excavated inscribed objects chronologically.
8. Konasukawa (IITGN 2023, pp. 49-50): seal chronology must enter discussion of the script. Gokhale (pp. 48-49) argues that the search for bilinguals leaves artefact typology understudied, a documented dispute with Rao 2026.
9. Rao 2018 (*Walking with the Unicorn*), printed pp. 521 and 524-525: further analysis and archaeological evidence are needed to test the economic functions ascribed to text components.

## Method and scope

The protocol and amendment disclose that searching preceded `PROTOCOL.md`, and the package makes no claim of decipherment or of sound or meaning assignment. Semantic readings are flagged as hypotheses. No third-party payload sits in the owned directory, and no row quotes a source at length.

Limitations sit apart from the claims they affect. The access labels are in `sources.json` and the CSV, while `REPORT.md` states claims that rest on snippet-only or unopened sources (Fuls, Mukhopadhyay, Farmer, Sproat, Wright) without saying so. "Corpus improvement is widely shared" should carry a count of independent sources. The sources listed above provide it: Wells, Fuls, Rao 2009, Kenoyer, Konasukawa, Yadav 2013 and Ganesan et al. make seven.

Priorities 1, 4 and 5 in the report rest on repository holdings and stand. Priority 2 rests on the statement that no denominator method exists, which Fuls's abstract contradicts. Priority 3, the Tamil Nadu graffiti comparison, leans on a reviewer's suggestion and a dead URL. Two items could inform the D1 and D2 follow-up on inventory size and sample size: Fuls's per-site test, and Petrie and Lynam's point that surveyed settlements are not all occupied at once.

## Writing

The prose script reports no flags. Reading the files, I found the following. The lecture caveat appears in five places (`README.md` line 5; `REPORT.md` lines 5, 13, 19, 33). Corrective contrasts recur at `REPORT.md` lines 13, 19, 23 and 55 ("not consensus", "not a settled choice", "does not mean the field voted"). The phrase "every claim about indigenous invention in the same terms" (line 5) is unclear. `README.md` line 3 says the survey covers the named researchers, which 12 of 25 do not support. The gap list at line 55 omits seven names.

## Boundaries

At 00:45, `git status --porcelain` listed 56 paths. One, `grep.exe.stackdump` at the repository root, was written at 00:40:59 by a crashed grep.exe; none of my commands printed a crash message, so I cannot attribute it, and I left it in place for the coordinator. The other 55 are under `experiments/2026-10-06-*`: 7 in this package (this file and six files in `review/`; the package's own files were committed in afd3b95) and 48 in other packages (backward-chronology, byproduct-inventory, chronology-region, evidence-census, modern-restoration, resemblance-baseline). Nothing under `knowledge/`, `papers/`, `research/` or the shared registry changed.

## Required fixes, ranked

1. Rebuild the eight unsupported rows and the nine partly supported rows from sources that were read. Give each row the source's own statement (under 15 words) and a page, and keep the package's gloss in a separate field. Replacement sources are in the roster table and in `review/missing-recommendations.csv`.
2. Correct the fourteen source records, drop or mark the Miller record as a failed search with no invented title, and replace the dead URLs (Wright, Rajan, Shinde landing page, Bisht, the Parpola profile).
3. Repair the encoding in the five files, write the JSON as UTF-8 without ASCII replacement, regenerate the CSV, and add the encoding check to `build_tables.py`.
4. Replace the lecture rows with the caption-checked statements and timestamps in `frenez-talk-check.md` (24:45-25:40, 28:45-30:40, 30:05-30:25, 51:00-53:00) and add the written parallels: Frenez 2018 pp. 167, 170, 171 and 186-187. The deliberate rejection of neighbouring script conventions has no written Frenez source yet.
5. Correct `REPORT.md` lines 5, 19 and 55 and `README.md` line 3, and list every roster member without a supported recommendation.
6. Fix the two repository links, and point the Sproat and Vahia rows to the nonlinguistic-control work in `knowledge/retrospectives/methods.md` and `research/literature/nonlinguistic_controls/`.
7. Replace `comparison_source_ids` with the opened sources that state agreement or dispute, each with a locator, and add the published replies: Rao et al. 2010 and 2015, Parpola 2008, Vidale 2007 and Sproat 2010.
8. Save fetched pages or their hashes and access dates under the raw directory, record them in `sources.json`, and use `research/literature/sources/` before searching again.
9. Add a `status` field (Exploratory) to the rows and the label to `REPORT.md`, as the amendment promises.
10. Re-save `registry-entry.json` without a BOM after the revision.

## Optional improvements

- Add `theme`, `shared_or_contested` and `n_independent_sources` columns to the table.
- State the lecture caveat once, near the top of `REPORT.md`, and remove the repeated contrasts.
- Record the Rao 2026 and Gokhale 2023 disagreement on excavating for bilingual texts under new excavation.
- Use Wells's Preface and Konasukawa to support the chronological and regional recommendation, and Fuls and Yadav 2013 to support the site-size recommendation.

## What I could not check

I could not open Wright 2010, Ratnagar 2001, Possehl 2002, Vidale 2000, Bisht's report, the Rajan book, the Shinde article or CISI 3.3, and the Frenez 2024 and Ameri pages returned 403. I read the Possehl 1996 and Vahia 2025 items as summaries or slides, and I did not re-read the lecture captions.
