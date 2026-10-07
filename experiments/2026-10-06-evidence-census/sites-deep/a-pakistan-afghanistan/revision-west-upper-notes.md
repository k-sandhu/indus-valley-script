# Pakistan west and upper Indus revision

Status: Exploratory. Research date: 7 October 2026.

## Findings

All 11 assigned sites now have four distinct live searches, an inspected primary source, and eight metadata fields tied to an inspected page or section. There are 57 live queries: 44 site queries and 13 supplemental queries. Two subsequent local gazetteer checks are recorded separately, giving 59 search-ledger entries. The source ledger records 466 returned leads and access routes, including irrelevant results, failed fetches and bibliographic records. Its `opened` and `access_scope` fields identify the text actually inspected.

Seven sites have directly checked CISI ranges containing 310 catalogue objects. Their local export contains 10 distinct CISI identifiers, or 3.23% of those ranges. The denominator includes pottery marks and seals without confirmed Indus writing. The largest omission is Rehman Dheri: 2 local identifiers against 270 catalogue objects, comprising one bone seal, 266 marked pottery objects and three marked objects labelled scrapers (?) in the p.378 caption. Sarai Khola contributes no local records against 10 photographed CISI sherds; CISI cites a larger excavation total of 68 marked sherds. See [revision-west-upper.json](revision-west-upper.json), fields `cisi`, `reported_object_counts` and `local_coverage_judgment`.

| Site | Inspected catalogue range | Local distinct CISI IDs | Catalogue coverage |
|---|---|---:|---:|
| Rehman Dheri | CISI2 pp.352–378,416; Rhd1–270 | 2 | 0.74% |
| Jhukar | CISI1 p.356, Jk1–2; CISI2 p.396, Jk3 | 1 | 33.33% |
| Nindowari | CISI2 pp.409–410; Nd1–3 | 2 | 66.67% |
| Lohumjo-daro | CISI1 p.357; Lh1 | 1 | 100.00% |
| Gumla | CISI2 pp.392–394; G1–16 | 2 | 12.50% |
| Sarai Khola | CISI2 pp.410–411; Skh1–10 | 0 | 0.00% |
| Hissam-dheri | CISI2 p.395; Hd1–7 | 2 | 28.57% |

These are verified catalogue-range computations, subject to the class distinctions stated in each row. Jhukar has three catalogued seals, of which Jk2 is the one clearly inscribed Indus seal in the inspected plates. Jk1 has an elephant without writing and Jk3 has a Late Harappan geometric design. Gumla has one button seal, fourteen incised pottery objects and one painted sherd. CISI2 p.XXVIII describes most Gumla and Hissam marks as potter marks. Rehman Dheri's local maximum of269 does not describe the complete catalogue, which ends at270. The numbering assumption is checked against printed contents and plates; CISI2 p.XXVII explicitly explains its consecutive per-site numbering.

Ten sites have sourced coordinates: eight from opened official DOAM gazetteer pages, Lohumjo-daro from a2015 Sindh gazetteer search snippet, and Gumla from the opened Uesugi2010 gazetteer p.101. The Lohumjo-daro PDF could not be obtained. Hissam-dheri coordinates remain unresolved, with web searches and the Uesugi chapter check recorded. Rehman Dheri's malformed UNESCO coordinate string is retained as a disagreement with the modern gazetteer.

Eight sites have an identified excavation report or comprehensive publication. None of those full final reports was inspected here; primary CISI pages, preliminary reports and a final-season summary supply the direct object evidence. Nindowari's correct comprehensive publication is the 2011 book by Jean-François Jarrige, Gonzague Quivron and Catherine Jarrige, published by Ginkgo, ISBN9782846790864. Its library record and publisher description were opened; the monograph itself remains unavailable. The first-pass title *Fouilles de Nindowari* was unsupported.

Ganweriwala has a documented 2015 tablet, published with its photograph and drawing in *Current World Archaeology*77(2016), p.7. The same primary notice documents a distinct 2007 tablet. Its latest site-specific CISI coverage has not been established, so its strict post-CISI status remains unresolved. No other assigned site supplied a dated later inscribed find from an inspected season report. Pakistan Archaeology searches were conducted for every site, but the search record does not establish exhaustive coverage of that journal.

## Source inspection and reuse

The existing local coverage fields were reused from `part-west-upper.json`, which in turn copied the coordinator's `local-site-coverage.json`. Existing first-pass outputs were not edited. CISI1 was reused from `research/literature/sources/joshi_parpola_1987_cisi1.pdf`. The parent acquired CISI2 in `data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf`; this subtask inspected its contents, introduction, site plates and basic-data tables. Rendered witness pages remain in `data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/west-upper-revision/`.

The downloaded 1964 *Pakistan Archaeology*1 scan contains Judeir-jo-daro on printed p.11, PDF p.24. It credits R.L.Raikes with identification and describes surface collections; it supplies no inscribed-object count. This replaces the first pass's unsupported Casal excavation attribution. The 1972 Mughal summary, pp.126–127, documents Sarai Khola's fifth and final season. The 2023 Khyber Pakhtunkhwa taskforce report, p.5, documents Hissam Dheri's 1978 Durrani excavation and gives Gumla1969, differing from CISI2's1971 date. Both Gumla dates remain recorded.

The Fuls2022 preview was opened, but it does not expose the full site inventories. Fuls2023 bracketed site-index numbers count legible signs. They have not been used as physical-object totals. The parent handles the shared Mahadevan1977 and Fuls count extraction.

## Access failures and remaining work

Full report access failed for the Majumdar1934 PDF routes, the Lohumjo-daro gazetteer PDF, and the Dales–Lipo1992 content PDF. Some web fetches timed out but terminal acquisition succeeded: the full *Pakistan Archaeology*1 scan, *Pakistan Archaeology*7 scan and Khyber Pakhtunkhwa report. The DOAM *Pakistan Archaeology*1 link downloaded only a cover. All such outcomes remain in the raw download logs and source `open_attempts` fields.

The main missing fields are current object custody, complete class inventories for sealings/tablets/metal/other objects, and full final-report metadata. CISI collection codes identify historical holdings, not present locations. No source grants redistribution rights for the downloaded images or scans, so they remain local. The final-report availability and CISI3.2 site page checks are recorded as unresolved rather than inferred from bibliographic titles.

## Checks for the reviewer

Repeat the plate counts and inspect the introduction caveats in CISI2 pp.XV–XVIII and XXVII–XXVIII. Check Rhd1–270 on pp.352–378,416; Gumla G11 and G8 on pp.393–394; and the68-versus10 Sarai Khola count in p.XVIII n46. Inspect CISI1 pp.356–357,375 for Jhukar and Lohumjo-daro.

Verify the ten coordinate records and acquire the Lohumjo-daro gazetteer p.I/96 if available. Obtain the 2011 Nindowari monograph and CISI3.2 site pages before extending its count or declaring a later-find absence. Reconcile Gumla1969/1971 against Dani's original report, and inspect the Ganweriwala2016 notice before assigning strict post-CISI status.

## Changed paths

This subtask created `revision-west-upper.json`, `revision-west-upper-sources.json`, `revision-west-upper-searches.json` and this Markdown file. It also created downloads, extracted text, rendered page images and web-response logs exclusively under the assigned local `west-upper-revision/` raw subdirectory.


## Gazetteer follow-up: 7 October 2026

Uesugi2010, printed pp.100–101 (PDF pp.6–7), supplies Gumla coordinates of 31°53′00″N,70°50′00″E, citing Possehl1999 p.762. It assigns the excavation to 1970 and Ahmed Hassan Dani of Peshawar University, citing Dani1970–71. This adds a third reported campaign year beside 1969 and 1971; those dates remain side by side. The page-text search removed whitespace to match letter-spaced English names. The full 40-page Pakistan chapter supplies only a neighbouring-site mention of Hissam Dheri at p.104, without its coordinate or campaign record. The reused raw source files were read without changes.
