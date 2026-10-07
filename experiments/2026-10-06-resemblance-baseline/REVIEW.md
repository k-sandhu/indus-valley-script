# Review of package H: a chance baseline for cross-script sign resemblance

Reviewer: Claude Sonnet 5.5, 7 October 2026. Reviewed state: commit 93eafbc (protocol commit 3183b4d). Paths are relative to the package directory unless they start with `data/` or `experiments/`. Files written: this file, `review/`, and temporary files in `data/raw/2026-10-06-resemblance-baseline/` (`review-tmp/`, `reviewer-sheets-rev2/`).

## Verdict

The computation and the coarse-rule results stand; the strict-rule counts and the reported coder agreement do not hold up under an independent recoding. Every headline figure in the README, REPORT and registry entry matches the saved outputs (R1 30/42, 24/42 and 32/42; R3 4/42, 1/42 and 10/42; complete-vector agreement 12/19; six exclusions), the analysis reruns byte for byte, and the protocol was committed at 00:02:54 on 7 October, before any coding file reached its saved state (00:04:36 to 00:11:24) and before the first outputs (00:11:33). I then recoded 113 of the 130 drawings without opening the primary rows (all 42 Tamil Nadu bases, all 32 Tifinagh letters, 15 Ogham stem letters, 24 Indus cells). R1 survives: Indus 30/42 under all four combinations of package and reviewer coding, Ogham 24/42, Tifinagh 31 to 32/42. R3 does not: Indus falls from 4 to between 1 and 3, Ogham from 1 to between 0 and 1, Tifinagh from 10 to 8 or 9, and every changed match is one the recoding lost. Complete-vector agreement between the reviewer and the primary coder is 52/113 (46%), and 9/19 on the package's own sample, against 12/19 between the package's two coders. The most important problem is that the orientation field is underspecified (54% agreement between reviewer and primary) and that several clean Tifinagh glyphs and Tamil sign 10 are coded in ways the source drawings contradict, so the strict-rule counts, and the 12/19 figure offered in support of them, overstate how reproducible the descriptor is. The qualitative reading survives recoding: the strict rule lowers every inventory's match rate, and the Tifinagh control matches at least as many Tamil Nadu drawings as the Indus subset under every rule and every coding combination.

## Checked claims

| # | Claim | Evidence | Result | Note |
|---|---|---|---|---|
| 1 | R1 matches 30/42 (71.43%), 24/42 (57.14%), 32/42 (76.19%) | `run-v1/observed.json` (`matched`, `rate`) | confirmed | Pair loop in `review/independent_checks.py` agrees; stable under recoding (30, 24, 31 to 32) |
| 2 | R2 matches 5/42, 3/42, 13/42 | `run-v1/observed.json` | confirmed | Recoding gives 4 to 5, 3, 11 to 13 |
| 3 | R3 matches 4/42 (9.52%), 1/42 (2.38%), 10/42 (23.81%) | `run-v1/observed.json` | confirmed as computed; discrepancy under recoding | 1 to 3, 0 to 1, 8 to 9 (section on recoding) |
| 4 | Complexity counts: Tamil Nadu 24/15/3, Indus 5/16/15, Ogham 6/10/4, Tifinagh 21/11/0; uncertain 6, 22, 5, 5 | `run-v1/manifest.json` `counts` | confirmed |  |
| 5 | R1 by band: 16/24, 14/24, 24/24 (simple); 14/15, 10/15, 8/15 (medium); 0/3 (complex) | `run-v1/observed.json` `complexity` | confirmed | The medium-band lead of the Indus subset (14/15) is absent from the REPORT's first paragraph |
| 6 | Six cells excluded before outcomes (I00, I01, I08, I10, I11, I39) | `run-v1/manifest.json`; `coder-a.json` notes | confirmed (list); unverifiable (timing) | Timing rests on the author's note (identical wording for all six, no per-cell reason) and file times. The excluded cells look dense and no matched reference in the endpoint has more than six segments, so the exclusions probably change no count (their descriptors were not recorded) |
| 7 | Agreement 12/19 (63.16%); segments, curved and loops 18/19, symmetry 16/19, direction 15/19; R1 and R2 17/19 | `run-v1/agreement.json` | confirmed | A third coder reaches 9/19 on the same drawings |
| 8 | n=20 subsampling table and intervals | `run-v1/subsampling.json` | confirmed | 33 exact finite-subset means reproduced independently to 1e-12 |
| 9 | Synthetic null at n=20 (six cells) | `run-v1/synthetic-null.json` | confirmed | 54 collision formulas reproduced; interpretation in the null section |
| 10 | Tifinagh fixed-query R1: 34.01% (n=5), 61.91% (n=20), 70.75% (n=42) | `run-v1/synthetic-null.json` | confirmed |  |
| 11 | At n=400 surrogate R1 means exceed 99.999%; fixed-query means equal the observed ceilings | `run-v1/synthetic-null.json` | confirmed | 99.99943%, 100%, 99.99995%; ceilings 71.43%, 57.14%, 76.19% |
| 12 | Brochure has 8 pages; SHA-256 equals the October 2 file | `verify_package.py`; library MARC record | confirmed | Live URL still serves 21,360,423 bytes (Last-Modified 22 Aug 2025) |
| 13 | 15,184 sherds from 140 sites; about 14,165 documented; 42, 544, 1,521, 2,107 | brochure PDF pp. 4-5 | confirmed | The 2026 Volume I table gives 551, 1,531, 2,124 (PDF p. 273); the package does not mention the revision |
| 14 | About 60% and more than 90%; no numerator, denominator, threshold or transformation rule | brochure PDF p. 5 | confirmed |  |
| 15 | Indus lists of 419, 386 and 695 signs | brochure PDF p. 3 | confirmed |  |
| 16 | Flipped seal labelled on PDF p. 6, left panel row 2 | page image | confirmed | `Mohenjadaro_0148_Flipped` stands beside `Kodumanal_TNSDA-G-0780` |
| 17 | Charts are Unicode 18.0; printed pages 149 and 321 | chart footers | confirmed |  |
| 18 | A bookseller lists a 145-page monograph | Exotic India product page | confirmed | `sources.json` marks it unopened; I opened it: 145 pages, ISBN 9788197784255 (check digit valid), paperback |
| 19 | Exact The Week URL "not recovered" | web search | discrepancy | One search returns `theweek.in/wire-updates/national/2025/01/06/mes7-tn-excavations-indus-valley.html`, a PTI item |
| 20 | Changizi et al. abstract was opened | none available to me | unverifiable | Citation confirmed from search-result summaries (Caltech, ScienceDaily and NBC listings); the journal site returns 403 to me |
| 21 | Protocol preceded coding and outcomes | `git log`; file times | confirmed | `PROTOCOL.md` unchanged since 3183b4d; file times are last-save times, so rows may have been started earlier |
| 22 | Endpoint inputs unchanged since the frozen run | `run-v1/manifest.json` hashes | confirmed | Five hashes match |
| 23 | Pre-outcome T18 correction | diff of `coder-a-controls-tamil.json` and `coder-a.json` | confirmed | Only T18 differs (T 3 to 1, L 0 to 2, terminals 3 to 2); it changes no match under any rule. The RETROSPECTIVE names I24 instead, and no earlier Indus file exists (unverifiable) |
| 24 | Registry entry agrees with README | `registry-entry.json` | confirmed |  |
| 25 | FILES.json inventory | `FILES.json` | confirmed | 112 of 113 entries match size and SHA-256; the remaining entry is FILES.json |
| 26 | `verification.json` counts 3, 9, 54, 108, 5 | rerun of `verify_package.py` | confirmed |  |
| 27 | Source titles are exact | `sources.json` | discrepancy | Five titles or venues have "?" in place of non-ASCII characters (Tami?i, 1680?169F, Parpola?s, E117?E139); about 20 strings lack spaces before digits |
| 28 | "Independent agent passes" show 12/19 reproducibility | `review/coding-agreement.json` | discrepancy | See next section |

## Reproduction log

| Command | Result |
|---|---|
| `python experiments/2026-10-06-resemblance-baseline/analyze.py --verify` | "Verified exact aggregate and per-query recomputation: run-v1" (4.8 s) |
| `python experiments/2026-10-06-resemblance-baseline/verify_package.py` | 3 source hashes, 9 census cells, 54 exact-formula cells, 108 interval cells, 5 manifest hashes; brochure bytes identical; registry entry valid (0.2 s) |
| `python experiments/2026-10-06-resemblance-baseline/review/rerun_fresh.py` | Imports `analyze.compute()`, writes `review/rerun/`; five aggregates and the per-query file are byte-identical to `run-v1` and to `run-v1-query-matches.json` (3.7 s). Used in place of the README's `analyze.py --output reviewer-run-01`, which would create a directory inside the package folder |
| `python experiments/2026-10-06-resemblance-baseline/prepare_inputs.py --directory reviewer-sheets-rev2` | Seeded 42-of-687 selection equals the pinned JSON; `indus-selection.json`, three contact sheets and the Tamil page render are byte-identical to the originals (1.1 s) |
| `python tools/review_prose.py --path experiments/2026-10-06-resemblance-baseline --no-write` | 4 files scanned, 0 flags |
| `python experiments/2026-10-06-resemblance-baseline/review/independent_checks.py` | Own pair loop, hypergeometric and collision formulas: 9 observed counts, 33 finite-subset means, 54 collision means and the manifest counts all agree |

`prepare_sources.py` (live downloads) was not rerun; I checked the live government PDF headers and the bookseller, library, news and review pages instead.

## Independent recoding of the descriptors

I rendered the pinned Unicode PDFs (vector) at 4x to 20x, the brochure page 4 at 6x to 30x, and enlarged the atlas cell PNGs (about 220 by 125 pixels) 4x to 12x, then coded with the PROTOCOL definitions and its 7 October clarification. Before coding I had seen the identifiers of the package's matched pairs, the second coder's prose notes, the first primary row (I00, excluded) and the T18 correction, so T18 is not independent. No other primary value was opened until `review/reviewer_coding.py` was complete. Two subjective fields follow a stated rule (docstring of that file): orientation is the direction of the longest segment, with `mixed` for near ties and closed curved figures; symmetry is reflection symmetry within ordinary irregularity. One entry was corrected after comparison (T07 apex corner, L 2 to 3); the first-pass copies are `review/reviewer-coding-precomparison.json` and `review/coding-agreement-precorrection.json`. Not recoded: 12 complex Indus cells (I04, I15, I16, I22, I23, I25, I27, I33, I36, I37, I38, I40) and the five Ogham lozenge letters (U+1690 to U+1694).

| Inventory | Drawings | Same R1 vector | Same integer vector (R2) | Same complete vector | Complete vector without orientation |
|---|---:|---:|---:|---:|---:|
| Tamil Nadu | 42 | 41 (98%) | 40 (95%) | 27 (64%) | 39 (93%) |
| Tifinagh | 32 | 28 (88%) | 25 (78%) | 19 (59%) | 24 (75%) |
| Ogham stem letters | 15 | 15 (100%) | 15 (100%) | 0 | 10 (67%) |
| Indus cells | 24 | 17 (71%) | 15 (63%) | 6 (25%) | 15 (63%) |
| All | 113 | 101 (89%) | 95 (84%) | 52 (46%) | 88 (78%) |

Field by field over all 113 drawings the reviewer and primary agree on segments 102 (90%), terminals 102 (90%), loops 111 (98%), symmetry 103 (91%) and orientation 61 (54%). On the package's 19 comparable sample drawings:

| Pair | Complete | Without orientation | Integer | R1 |
|---|---:|---:|---:|---:|
| primary and second pass (package figure) | 12 | 15 | 17 | 17 |
| reviewer and primary | 9 | 14 | 15 | 16 |
| reviewer and second pass | 9 | 13 | 15 | 15 |

The two drawings the README names (fields: segments, curved, loops, L, T, X, Y, other, terminals, components, symmetry, orientation):

| Drawing | Coder | Row |
|---|---|---|
| I14 | primary | 11, 1, 3, 7, 0, 0, 1, 2, 1, 1, none, mixed |
| I14 | second pass | 7, 4, 3, 4, 1, 0, 0, 2, 1, 1, none, mixed |
| I14 | reviewer | 9, 2, 3, 6, 1, 0, 0, 2, 1, 1, none, vertical |
| U2D3F | primary | 4, 0, 1, 1, 1, 1, 0, 0, 3, 1, none, diagonal |
| U2D3F | second pass | 4, 0, 2, 2, 0, 1, 1, 0, 1, 1, diagonal, diagonal |
| U2D3F | reviewer | 4, 0, 1, 3, 1, 0, 0, 0, 1, 1, none, mixed |

All three coders agree that I14 has three loops, two four-way contacts and one terminal. They differ in how the stem and leaf edges are split (7, 9 or 11 segments; 1 to 4 curved) and in one contact type (T for the second pass and reviewer, Y for the primary). U+2D3F, rendered at 20x, is a right triangle (left vertical, base, hypotenuse) with one extra stroke from the upper right that ends on the hypotenuse: 4 segments, 1 loop, 3 corners, 1 T contact, 1 terminal. The primary row has one corner, a T contact, a crossing and three terminals, and the second pass reads two crossing diagonals enclosing two loops, so neither matches the glyph. U+2D3D has the same structure and is also miscoded by the primary.

Three causes account for most disagreement. First, orientation ("predominant segment direction") has no length rule or angle tolerance: the primary appears to count segments (an upward arrow and a Y with a long vertical stem are both `diagonal` because two of three segments are oblique), the second pass uses visible extent, and I used the longest segment. All 15 Ogham stem letters differ on orientation for this reason, and the five diagonal-stroke letters also differ on symmetry (0/15 complete agreement). Without orientation the package's two coders agree on 15/19 and the reviewer and primary on 88/113. Second, the primary rows misread six clean Tifinagh glyphs that the pinned charts settle: U+2D3C (an H with four outward serifs, no loop, coded with two loops and no terminals), U+2D3D and U+2D3F (above), U+2D45 (an X with a vertical stroke ending at the crossing, coded as a plain X), U+2D47 (open on the right, coded with two loops and no terminal) and U+2D49 (a four-segment sigma shape, coded with three segments). The extra strokes are visible even in the saved 2x page render, so these are reading errors; per-row notes are boilerplate ("Unicode18 chart PDF2, column 4, row 5") and give no rationale. Tamil sign 10 is also misread: the horizontal line extends left of the arrowhead vertex (four terminals), but the primary codes a three-terminal Y. Third, Indus composites are segmented unstably (R1 agreement 17/24): the primary counts the four short corner ticks of I07 as part of the sign (8 segments, 5 components) although its note says "central glyph only", and counts the bent arm of I05 as one segment.

Effect on the match counts, using the package's matching rules (`review/sensitivity.json`). "Hybrid" references use reviewer rows where coded (24 of 36 Indus cells, 15 of 20 Ogham letters, all 32 Tifinagh letters) and primary rows elsewhere.

| Queries / references | Indus R1 / R2 / R3 | Ogham R1 / R2 / R3 | Tifinagh R1 / R2 / R3 |
|---|---|---|---|
| primary / primary (package) | 30 / 5 / 4 | 24 / 3 / 1 | 32 / 13 / 10 |
| primary / hybrid | 30 / 5 / 1 | 24 / 3 / 0 | 31 / 11 / 9 |
| reviewer / primary | 30 / 4 / 3 | 24 / 3 / 1 | 32 / 13 / 9 |
| reviewer / hybrid | 30 / 4 / 2 | 24 / 3 / 0 | 31 / 11 / 8 |
| R3 without orientation, same four rows | 4, 4, 4, 4 | 2, 0, 2, 0 | 11, 9, 11, 9 |

No recoding adds a match. The lost matches are Tifinagh R1 T18 (the primary U+2D3C row), Indus R2 T10 with I13 and Tifinagh R2 T29 and T30 with U+2D45 (the misreads above), Indus R3 T03, T04 and T13 with I13 (orientation words), Ogham R3 T29 with U+168B (the primary codes the slash across a horizontal stemline as symmetric about both axes; the second pass and the reviewer code it as having no such symmetry) and Tifinagh R3 T28 and T30. The R3 pairs that remain under reviewer coding are Indus T13 with I13 and T39 with I17, and Tifinagh T01, T02, T19, T20, T24, T32, T36 and T39. Six of the eight Tifinagh pairs are visually the same shape up to size or flip (T01 with U+2D34, T02 with U+2D37, T19 with U+2D30, T20 with U+2D32, T32 with U+2D35, T39 with U+2D4F); T36 with U+2D43 is similar; T24 and U+2D44 differ (a comb against a bracket with a stem). The identical pairs are the useful part of the pilot, since they show the same simple mark in Tamil Nadu graffiti and in Tifinagh. Limits of this check: one reviewer, 17 drawings not recoded, and an orientation rule that is itself a convention.

## What the 2025 PDF is

`data/raw/2026-10-02-connections-and-priority/south-india/morphological-study-2025.pdf` (21,360,423 bytes) is an 8-page A4-landscape illustrated booklet. It is neither the full monograph nor a truncated copy. It was exported from Adobe InDesign 20.0 on 3 January 2025, three days before the PTI reports. The Tamil Digital Library record TVA_BOK_0065888 (retrieved 7 October 2026, saved as `data/raw/2026-10-06-resemblance-baseline/review-tmp/marc-2025.html`) gives "8 pages." in MARC field 300 and subject headings that repeat the booklet's own headings, and the TNSDA portal text says the book is available at tamildigitallibrary.in. A bookseller separately lists a 145-page paperback with ISBN 9788197784255; that book was not available. The package's statement that the complete monograph is unrecovered is therefore accurate, and its scoping of every finding to the brochure is correct. The package could add that the 8-page count is the library's own cataloguing, not a failed download.

| PDF page | Content | Matching criteria or headline figures |
|---|---|---|
| 1-2 | Cover; introduction to the Indus civilisation | none |
| 3 | Indus script: 419 (Mahadevan), 386 (Parpola), 695 (Wells) signs; ICIT 3,898 artefacts, 4,791 texts, 3,723 complete texts with 13,556 signs | comparison lists named but not tied to any percentage |
| 4 | The 42 base-sign drawings and the table of variants (544) and composites (1,521), total 2,107 | headline counts |
| 5 | Definitions of graffiti, variants and composites; 15,184 sherds from 140 sites, about 14,165 documented; "exact" and "near" parallels; about 60% of base signs and variants with parallels in the Indus script; more than 90% of South Indian and Indus-civilisation graffiti with parallels | headline percentages; no threshold, numerator, denominator or transformation rule |
| 6-7 | 16 triplets of seals and sherds with red boxes on the compared signs; p. 6 left panel row 2 labels a flipped seal | examples only |
| 8 | Contact discussion; asks for more material evidence | none |

The brochure states no matching criterion beyond the words "exact" and "near", as the package reports. Two points the package does not make: the 60% sentence concerns the 42 base signs and variants against the Indus script, whereas the 90% sentence speaks of graffiti marks of South India and of the Indus civilisation, that is pottery marks, and the pilot's Indus references are script signs from the 1979 sign list. The local 2026 volumes (same authors, 740 and 712 PDF pages) were not read for method statements, although they are the nearest available text. They contain no matching rule either, but Volume I repeats the figure of about 60% in its preface (PDF p. 12), cites B. B. Lal's 1962 figures of 89% and 85% parallels (PDF p. 302), gives revised totals of 551 variants, 1,531 composites and 2,124 forms (Table 3.3, PDF p. 273), and describes the Indus comparison as plates prepared "so that one can visualize their similarity" (PDF p. 282). Its cross-references send the comparison to a Chapter 7 that, in the published volumes, treats Tamiḻi inscribed potsherds (Volume II PDF p. 388).

## Source checks

| Source | What I opened | Result |
|---|---|---|
| Rajan and Sivanantham 2025 | local PDF (all pages' text; pages 4, 6, 7 as images); live URL headers | title, authors, publisher, year, figures as in the package |
| Tamil Digital Library record (not cited by the package) | catalogue page and MARC view | 8 pages; Chennai, 2025 |
| Exotic India record | product page | 145 pages, ISBN, paperback; package marks it unopened |
| PTI via Oneindia | saved page | "nearly 90 percent", 6 January 2025; over 15,000 sherds, 140 sites |
| PTI via The Week | page via WebFetch (direct HTTP is blocked) | found by one search, which contradicts "not recovered"; says "nearly 90" in one sentence and "more than 90 percent" in another |
| Harappa review | saved page | no byline; cites the 90% and 60% figures; raises basic geometric shapes (V-shapes, crosses, double lines) used independently |
| Changizi, Zhang, Ye and Shimojo 2006 | search results (Caltech, ScienceDaily and NBC listings) | title, authors, *American Naturalist* 167(5): E117-E139 confirmed; journal page returns 403 |
| Unicode Ogham and Tifinagh charts | local PDFs, pages 1-2 | Version 18.0; internal-use permission and "not prescriptive" glyph notice on page 1 |
| Unicode terms | local copy | definitions exclude PDF charts from data files; internal copies permitted |
| CypherSolver page | page via WebFetch | section 03 baseline is Tamil words for pictures against Parpola's star names (15%, 30%); section 04 reports composite order 70.5% against 88.0%; the title in `sources.json` is corrupted |
| TNSDA portal | client bundle from October 2 | "42 base signs, 544 variants and 1521 composites ... 9486 recognised graffiti data" |
| 2026 *Inscribed Potsherds of Tamil Nadu: Graffiti and Tamiḻi*, vols I and II | local PDFs | authors, 2026, 740 and 712 pages, ISBN 978-81-977842-3-1; title in `sources.json` loses the ḻ |
| Koskenniemi and Parpola 1979 | atlas metadata | CC BY 4.0 note matches `knowledge/provenance/REDISTRIBUTION.md`; the Helsinki record is behind an anti-bot page, and the atlas cites a different `source_url` than `sources.json` |

Snippet-only status is marked where it applies (Changizi full text, Exotic India). No third-party payload is tracked: the 18 tracked files are code, prose, aggregates and source metadata, and `sources.json` records `quotes_used: 0`.

## Inventories, size dependence and the null

Sources, versions, hashes, rights and selection rules for the three inventories are documented (`sources.json`, PROTOCOL), and sizes, complexity bands and uncertainty counts are reported (`run-v1/manifest.json`). Not recorded is why Linear A, Cypro-Minoan, Old Turkic and Vinča-type marks, named in the package prompt, were set aside. The Mayig schema holds verbal sign descriptions and cross-references rather than geometry, so leaving it unused is justified.

The package handles inventory size by subsampling to common sizes and by exact formulas, which is sound up to the largest inventory (36). At common sizes the Indus subset matches fewer Tamil Nadu drawings than either control under R1: 17.6%, 32.4% and 53.4% at n=5, 10 and 20, against 33.7%, 50.5% and 57.1% for Ogham and 35.8%, 52.9% and 67.7% for Tifinagh. The REPORT prints only n=20, and its first paragraph compares full-size counts for inventories of 36, 20 and 32 references.

R1 is a coverage test. The 42 drawings occupy 16 (segments, loops) classes, and five classes hold 27 of them ((3,0): 8, (2,0): 6, (5,0): 5, (1,0): 4, (3,1): 4). The Indus subset covers 9 classes (30 drawings), Ogham 6 (24), Tifinagh 10 (32). The 52 pooled Ogham and Tifinagh glyphs cover 12 classes and 38 of 42 drawings (90.5%), and adding the Indus subset adds none; only T07, T23, T35 and T38 stay unmatched (`review/exploratory.json`). A random 36-glyph draw from the pooled unrelated glyphs covers 35.2 drawings on average (interval 29 to 38) at R1, 11.0 (8 to 13) at R2 and 8.0 (5 to 11) at R3, against 30, 5 and 4 for the Indus subset. R1 also pairs T18 (a dome with an arrow) with a ladder (I31), an Ogham lozenge letter and Tifinagh U+2D3C. Every match under every rule comes from references with at most six segments; the 15 Indus cells with seven or more contribute none. With references restricted to at most six segments and drawn at n=16, Indus and Tifinagh coverage under R1 is the same (26.8 and 26.5 drawings), and Tifinagh leads under R2 (8.0 against 3.8) and R3 (5.6 against 3.0).

The stratified numbers qualify the headline sentence "no Indus advantage over both controls". In the 4-6 segment band Indus matches 14/15 drawings under R1 (Ogham 10/15, Tifinagh 8/15), in the 1-3 band 16/24 (Tifinagh 24/24), so the pooled result depends on the query mix and on the controls being simple. Paired exact tests on the 42 drawings do not resolve Indus against Tifinagh (R1: 6 against 8 discordant pairs, p = 0.79; R3: 3 against 9, p = 0.15), while the two controls differ from each other more than either differs from the Indus subset (R3: Tifinagh 10, Ogham 1, p = 0.012). The baseline therefore depends on which unrelated inventory is chosen.

The synthetic null draws surrogate queries and references from one inventory's own distribution, so a surrogate query matches whenever its own catalogued item is among the references. For the Indus subset every R3 class is unique (36 classes for 36 cells), and the reported 43.07% at n=20 equals 1 - (35/36)^20 exactly. These values measure re-drawing, they cannot serve as chance rates for Tamil Nadu, and the fixed-query version only climbs to the observed ceiling. Step 4 of the package prompt asked for random marks generated from the inventories' complexity distributions; no marks are generated, so the extrapolation to inventories of several hundred signs, where the authors' comparison sits, is not addressed (the PROTOCOL says so).

## Method, scope and writing

- Deliverables: README, PROTOCOL, REPORT, RETROSPECTIVE, `registry-entry.json`, `sources.json`, the code (`analyze.py`, `prepare_inputs.py`, `prepare_sources.py`, `verify_package.py`) and the `run-v1` aggregates all exist, with `source-observations.json`, `verification.json` and `FILES.json` besides. The coder rows and per-query matches are local-only by design, so a clean checkout cannot rerun the endpoint (the README says so). Counts carry their bases throughout (42 queries; 36, 20 and 32 references; 19 comparable agreement drawings). `run-v1` is the only run, and the one dated amendment (the 7 October codebook clarification) precedes it.
- The primary coder coded Tamil Nadu and the two controls first (file saved 00:04:36) and the Indus cells afterwards (00:11:24), knowing the rules and the query descriptors. The second pass was saved at 00:06:01 without sight of primary rows and used the same codebook; both are agent passes. No intermediate run is preserved, so whether match counts were seen before the last edits cannot be established (the T18 edit changed no match).
- The Indus references are sign-list entries from the 1979 atlas, including composite and variant entries, and cells are resampled as independent. Related families (I06, I07, I09; I18, I19, I21; mirrored Tifinagh letters) are not clustered; this leaves R1 coverage unchanged but is unmodelled. The controls are two alphabets with simple stroke-based glyphs; Ogham gives 10 R1 classes for 20 letters.
- Status labels (Exploratory, Synthetic) fit; `verification.json` labels the computation "Verified computation", which applies to determinism and formulas, not to the manual codes. The PROTOCOL says it preceded descriptor coding; the commit shows its text, clarification included, was fixed before the coding files reached their saved state, and the clarification reflects prior viewing of Tamil Nadu sign 5.
- Scope: I found no claim of decipherment, sound or meaning assignment, transmission, or novelty beyond the stated search, and the 2025 study is attributed to its authors. One sentence goes past the data: the RETROSPECTIVE says the pilot "establishes that the computational baseline and manual codebook are usable".
- Writing: the prose scan has zero flags. Manual read: the first REPORT paragraph's "no Indus advantage over both controls" is ambiguous (Indus exceeds Ogham at R2 and R3); the null's limitation is stated in the PROTOCOL, README, registry entry and three places in the REPORT; "bounded" qualifies five nouns; the REPORT title reads as a finished baseline although the work is a pilot.
- Boundaries: at the final check `git status --porcelain` listed 106 paths, all under other packages' `experiments/2026-10-06-*` directories (backward-chronology 1, byproduct-inventory 2, chronology-region 14, evidence-census 39, field-recommendations 5, modern-restoration 24, sign-context-and-seals 18, weight-metrology 1) plus this review's two paths (`REVIEW.md`, `review/`). Nothing lies outside `experiments/2026-10-06-*`. HEAD moved from 93eafbc to 93f4aa9 during the review through other packages' commits; those commits touch only `experiments/2026-10-06-*` paths other than this package, whose tracked files are identical to 93eafbc.

## Required fixes, ranked

1. Do not edit `run-v1`. Add a dated amendment and an Exploratory `run-v2` that recodes the six misread Tifinagh glyphs and Tamil sign 10 from renders of at least 12x, with a one-line rationale per changed row, and report both runs side by side. Until then, state in the README, REPORT and registry entry that independent recoding changes the strict counts (Indus 4 to 1-3, Ogham 1 to 0-1, Tifinagh 10 to 8-9, R1 unchanged) and that 12/19 is not an upper bound for reproducibility.
2. Define orientation and symmetry operationally (angle tolerance, length-weighted rule, threshold for balanced directions) before any recode, or drop orientation from R3 and report R3 without it (Indus 4/42 in every coding, Tifinagh 9-11, Ogham 0-2).
3. Rewrite the first REPORT paragraph: replace "no Indus advantage over both controls" with the size-matched numbers, the paired uncertainty and the stratified pattern; replace "usable" in the RETROSPECTIVE with the measured agreement.
4. Describe the synthetic null once, as re-drawing within an inventory (the Indus R3 value at n=20 is 1 - (35/36)^20), say that step 4's random-mark generator was not built, and keep its values out of the headline discussion.
5. Repair `sources.json` and `source-observations.json` (non-ASCII characters replaced by "?", missing spaces); add the library MARC record, The Week URL, and the 2026 Volume I findings with page numbers (revised totals 551/1,531/2,124 against the 544/1,521/2,107 of the 2025 brochure and the portal, Lal 1962, the visual-plate method, the Chapter 7 cross-reference).
6. Reconcile README and RETROSPECTIVE on the pre-outcome correction (T18 against I24), and keep the earlier Indus row file if one exists.

## Optional improvements

- Report the pooled and size-matched control draws and the 16-class coverage table (`review/exploratory.json`), and compare with the brochure's and the 2026 preface's 60%.
- Code references before looking at queries, use two human coders, render vector charts at 12x or more, and replace boilerplate row notes with per-row rationale.
- Add a control of Indus-like complexity (a syllabary) and record why Linear A, Cypro-Minoan, Old Turkic and Vinča-type marks were not used.
- Track a descriptor-only copy of `coder-a.json` and `coder-b.json` (ids, 13 fields, flags; no images or crops) after a `REDISTRIBUTION.md` check, so the endpoint reruns from a clean checkout.
- Consolidate the repeated caveats on the null and retitle the REPORT as a pilot.
