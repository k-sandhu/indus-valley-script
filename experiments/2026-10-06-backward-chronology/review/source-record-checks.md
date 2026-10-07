# Source records, URLs and text damage

Reviewer check of the 44 records in `amendment-2026-10-07-frenez/sources.json` (the first 18 are the first-pass records, identical in `sources.json` of the package root). Authors, titles, years, venues and pages were compared with Crossref, Persée, publisher and library listings, the title pages or OCR of the local copies, and the Peshawar volume indexes for *Ancient Pakistan*. Every URL was requested once with a small GET or HEAD.

## Records with an error or an unresolved point (10)

| id | field | package value | correct value or concern | evidence |
|---|---|---|---|---|
| `frenez2023-caption` | `venue` | The Oxford Handbook of the Indus Civilization | *Oxford Research Encyclopedia of Asian History* (Oxford University Press, online 18 October 2023, DOI 10.1093/acrefore/9780190277727.013.595) | The saved Harappa page the package opened says the chapter is "Part of the Oxford Research Encyclopedias Asian History section" (`frenez2023-caption.text.txt`); Crossref |
| `durrani1995-intro` | `title`, `venue` | "Introduction", pages i–xiii | The volume index titles it "Excavations in the Gomal Valley (Rehman Dheri Excavation Report No. 2): Introduction", pp. 1–13 (the PDF prints roman numerals i–xiii) | `sites.google.com/uop.edu.pk/ancientpakistan/volumes/volume-x` |
| `audouze-jarrige1979` | `authors`, pages | "Francine Audouze"; pp. 213–221 against 213–231 | The author is probably Françoise Audouze; no source gives "Francine". The page conflict between Miller's list (213–221, and she cites p. 220) and Quivron 1980 p. 275 n. 3 (213–231) is unresolved | Finding aid of her papers; Miller 1997; Quivron 1980 scan |
| `kenoyer-meadow1999` | pages | 1–12 | 1–11 | eHRAF; the scan has text pp. 1–7, four unnumbered plates and a cover |
| `winkelmann2004` | `venue` | Venice: Il Punto | A book published by Il Punto Edizioni for the Ligabue Study and Research Centre, 2004, 201 pp.; contributors beyond Winkelmann are not resolved | Frenez 2018 p. 193; bookseller listing |
| `miller1997` | `venue` | Rice and Kingery (eds.), Columbus | P. M. Rice edited volume VII of the series; W. D. Kingery is the series editor; the publisher's address is Westerville, Ohio (Miller's page header says Columbus) | Publisher listing |
| `jarrige1995-report` | `authors` | four authors | The four named persons are the editors | eHRAF; Miller 1997 bibliography |
| `quivron1997` | `url` | the author's institutional page | The page lists only 2000–2023 items and does not list this chapter. Title, editors, pp. 45–62 and publisher come from Coningham 2002 p. 102 alone | `quivron-bibliography.html`; Coningham OCR |
| `harappa-hearth-gallery` | locator | "slides 136–137" | The saved pages read "46 of 90" and "47 of 90"; 136 and 137 are numbers in the site's legacy URLs | local HTML |
| `gadd1932` | pages | reprint pp. 3–22 | The journal pagination of the *Proceedings of the British Academy* 18 article is not stated and could not be confirmed | local scan |

Two records are bibliographically correct but name no local witness. The two saved `changizi2006*.html` files are an error page and a challenge page, while the full text is preserved in the response witness `data/raw/2026-10-06-backward-chronology/web-17.json`, which contains the two section titles and the 36-type statement the package cites; the record does not name it. The local `coningham1996-record.html` is an HTTP 403 challenge page, and the abstract text is preserved in `web-02.json`.

Three records look inconsistent but are explained correctly in the package and need no change: `mahadevan2001` carries the venue *Studia Orientalia* 94, which is right (the volume is the Parpola Festschrift); `kenoyer2009` carries the year 2009 (the Harappa file name) while the journal prints "2006–2007", and both appear in the record; `winkelmann1999` has the year 2000 and the id 1999 because the volume year is 1999 and the publication year 2000, as its venue field says.

The other 31 records are correct on authors, title, year, venue and pages. They include `jarrige-enault1976` (Arts asiatiques 32, 29–70), `coningham1996` (*Cambridge Archaeological Journal* 6(1), 73–97), `changizi2006` (*American Naturalist* 167(5), E117–E139), `quivron1980` (*Paléorient* 6(1), 269–280), `laursen2010`, `laursen2026-abstract` (*Journal of Near Eastern Studies* 85(1), 115–145; five authors in the printed order), `salomon1998`, `mahadevan2001` (*Studia Orientalia* 94, 379–386, the Parpola Festschrift), `sundaresh-gaur1998` (the paper's byline is "Sundaresh and A.S. Gaur"; Sundaresh uses a single name), `frenez2018`, `possehl2006`, `durrani1988` (*Ancient Pakistan* VI, 1–232), `durrani1995` (X, 198–233) and the two Tamil Nadu volumes. The volume identifiers 062969 and 062968 in the two Tamil Digital Library URLs run opposite to the volume numbers (062969 is Volume I, 740 pages), but the package maps them correctly.

## URLs and local witnesses

All 44 URLs answered. Thirty-eight records name a local witness; all exist and every SHA-256 equals the recorded value (the package's own verification checks the same 38). Six records name none: `coningham1996`, `changizi2006`, `winkelmann1999`, `winkelmann2004`, `jarrige1995-report` and `audouze-jarrige1979`. Four existing witnesses are not the document itself: `quivron1980` is a page manifest, `bm120573` is a search-result JSON, `quivron1997` is the institutional page and `frenez2026-lecture` is the package's own note. Bot challenges or HTTP 403 blocked `mahadevan2001` (an Anubis page), `salomon1998`, `changizi2006` and `bm120573`; the other URLs returned 200. Of the 24 records whose URL is a PDF, 23 have a local copy and in all 23 the Content-Length equals the size of that copy.

## Access labels

The labels are consistent with use except in three places. Row `mehrgarh-nausharo1997`, `source_locations[0]` reads "primary Quivron locators45,53,55,61"; Coningham 2002 does cite those pages, but the Quivron chapter was not opened, so the locators are second-hand. The lecture time codes (17:05–24:00, 48:25–48:55, 16:20–17:05) appear in five claims of `continuity-claims.json` without the qualifier "through coordinator note" that the evidence row `harappa-kot-diji-hearth-sealing` carries. The Cambridge abstract is the only opened witness for `coningham1996`, and the abstract does not give the method label "radiometric/stratigraphic" that the row `anuradhapura` attaches to it.

## Text damage

All text files of both directories (160, excluding `review/`) decode as UTF-8 and contain no replacement character, mojibake or control character; only the two CSV files start with a byte-order mark, as designed. The `IIA�III` seen in a default Windows console for row `rangpur` is an en dash (bytes `E2 80 93`) in the file.

The amendment folder, but not the first-pass folder, has lost spaces before digits and after periods. Excluding author-year keys such as `Quivron1980` and real identifiers such as `UW6`, `ZE8` and `AO22310`, a scan found 82 distinct word-plus-digit strings (230 occurrences), 51 label-plus-digit strings (303 occurrences), and about 160 `p.`, `pp.`, `no.`, `;` and `,` followed directly by a digit in four JSON files. The strings originate in `build_amendment.py` (128 occurrences), `make_audits.py` (54) and `compare_coverage.py`, and are copied into `added-rows.json`, both evidence tables, `sources.json` (51), `visual-checks.json` (32), `lecture-claim-audit.json` (22), `continuity-claims.json` (16), `contact-items.json` (13), `dating-details.json` (12), `registry-entry.json` (11) and `search-log.json` (7). Examples:

- `sources.json`, `laursen2026-abstract`, `venue`: "Journal of Near Eastern Studies85(1):115–145".
- `registry-entry.json`, `outcome`: "comprise190 Rehman Dheri sherds and3 Harappa objects,193 specimens" and "remains1300–700 BCE,600 years".
- `added-rows.json` and `evidence-table.json`, `mehrgarh-pottery1980`: "Nearly850 marks", "into50 categories".
- `comparison-01/COVERAGE.md` line 41 and `compare_coverage.py` line 82: "The Indus northwest has12 dated additive rows; South India has4."

Because `registry-entry.json` is meant for the shared registry, its text should be corrected before it is copied.
