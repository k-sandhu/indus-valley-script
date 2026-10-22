# POST-CATALOGUE-FINDS-2026-10-21: inscribed objects reported after the CISI catalogues, 1987 to 2026

Status class: `source-review`.

Date and contributors: 20–21 October 2026; Claude Opus 5.5 (`claude-opus-5-5`) in the Claude Code desktop app as coordinator, with the Codex CLI (`codex-cli 0.160.1`) running `gpt-6.1-sol` for acquisition, extraction, matching and verification ([RETROSPECTIVE-CODEX.md](RETROSPECTIVE-CODEX.md)). Question card [Q-1026](../../knowledge/questions/Q-1026-post-catalogue-finds.md). Registry entry draft: [POST-CATALOGUE-FINDS-2026-10-21.json](../../knowledge/registry/attempts/POST-CATALOGUE-FINDS-2026-10-21.json).

## Result

We listed 503 inscribed objects from excavation reports, *Indian Archaeology – A Review* (IAR), *Puratattva*, *Man and Environment* and other journals, one row per physical object ([objects.csv](objects.csv)). Of these, 301 are post-catalogue objects whose publication states an inscription: they were reported after the CISI volume covering their site, and that volume does not contain them. They come from 21 sites, all but three of them in India. A further 56 post-catalogue rows have an inscription the publication leaves open, 145 rows turned out to be objects already in a CISI volume (138 of them inscribed rods from Harappa and Mohenjo-daro whose CISI numbers Parpola's 2019 paper prints, kept for audit), and one more rod may be in CISI 3.1.

Under the protocol's join rule, which accepts only a registration or a cited plate as evidence of identity, 10 of the 301 match a local object, 271 are candidates for local objects of the same kind at their site and 20 have no possible local counterpart. The local corpus therefore lacks between 55 and 291 of these objects: the lower figure assumes that every candidate is one of the local objects it could be, the upper that none is. Find context narrows the range. When a row's area, trench, phase, type and material, or at Dholavira its grid square, pick out exactly one local object, we recorded that object as a context join, and we treat Khirsara's join on a plate number the same way because the local record does not name the plate's publication; with these 67 joins accepted, 77 rows match and the corpus lacks between 55 and 224. The context joins were defined after the matching run's proposals had been seen, so the protocol figures are the frozen result and the context figures a labelled refinement ([Context joins](#context-joins)). Most of the remaining width comes from Dholavira, where about 140 rows from Bisht's report and a similar number of unregistered local objects cannot be paired without information the corpus does not record.

| Site | Baseline | Rows | Matched | Candidate | Absent | Corpus lacks | With context joins: matched, lacks | Primary publication of the rows |
|---|---|---:|---:|---:|---:|---|---|---|
| Dholavira | CISI 1 (1987) | 208 | 3 | 204 | 1 | 10–205 | 61, 10–147 | Dholavira report, Jan. 2015 preliminary (205); IAR 1997–98, *Puratattva* 29, 37 |
| Surkotada | CISI 1 (1987) | 23 | 0 | 23 | 0 | 19–23 | 0, 19–23 | Joshi 1990, MASI 87 |
| Gola Dhoro (Bagasra) | CISI 1 (1987) | 12 | 6 | 0 | 6 | 4–6 | 6, 4–6 | Jamison et al. 2017 (7); IAR 2003–04 (3), 1995–96, 1996–97 |
| Bhirrana | CISI 1 (1987) | 9 | 0 | 7 | 2 | 4–9 | 0, 4–9 | IAR 2003–04 (4); *Puratattva* 35 (3), 36; Uesugi et al. 2016 |
| Khirsara | CISI 1 (1987) | 8 | 0 | 8 | 0 | 5–8 | 1, 5–7 | IAR 2010–11 (6), 2009–10; Pokharia et al. 2017 |
| Shikarpur | CISI 1 (1987) | 7 | 0 | 3 | 4 | 4–7 | 0, 4–7 | Shikarpur 2008–09 report (3); IAR 1987–88 (2), 2007–08, 2012–13 |
| Farmana | CISI 1 (1987) | 6 | 0 | 6 | 0 | 0–6 | 5, 0–1 | Shinde, Osada and Kumar 2011 (5); Farmana 2007–08 report |
| Kanmer | CISI 1 (1987) | 4 | 1 | 3 | 0 | 0–3 | 3, 0–1 | Kanmer chapter 8 draft (Seth, Kharakwal, Menaria and Bunker) |
| Rakhigarhi | CISI 1 (1987) | 4 | 0 | 4 | 0 | 0–4 | 0, 0–4 | Nath 1997–2000 draft (2); *Puratattva* 28; Chandigarh Circle inventory 1998 |
| Rupar | CISI 1 (1987) | 3 | 0 | 3 | 0 | 2–3 | 0, 2–3 | IAR 2011–12 |
| Tarkhanewala Dera | CISI 1 (1987) | 3 | 0 | 3 | 0 | 0–3 | 0, 0–3 | Trivedi 2009 (2); IAR 2003–04 |
| Baror | CISI 1 (1987) | 2 | 0 | 2 | 0 | 0–2 | 0, 0–2 | *Puratattva* 35; IAR 2003–04 |
| Dhalewan | CISI 1 (1987) | 2 | 0 | 0 | 2 | 2 | 0, 2 | Bala and Kant 2018 |
| Ganweriwala | CISI 2 (1991) | 2 | 0 | 2 | 0 | 0–2 | 0, 0–2 | Parpola and Gulzar 2016, *Current World Archaeology* 77 |
| Karanpura | CISI 1 (1987) | 2 | 0 | 2 | 0 | 0–2 | 1, 0–1 | IAR 2013–14 |
| Bet Dwarka | CISI 1 (1987) | 1 | 0 | 0 | 1 | 1 | 0, 1 | *Man and Environment* 22–23 |
| Juni Kuran | CISI 1 (1987) | 1 | 0 | 0 | 1 | 1 | 0, 1 | IAR 2004–05 |
| Lakhanjo-daro | CISI 2 (1991) | 1 | 0 | 0 | 1 | 1 | 0, 1 | Biagi 2022 |
| Mitathal | CISI 1 (1987) | 1 | 0 | 0 | 1 | 1 | 0, 1 | *Man and Environment* 35 |
| Nagwada | CISI 1 (1987) | 1 | 0 | 0 | 1 | 1 | 0, 1 | IAR 1987–88 |
| Nuhato | CISI 2 (1991) | 1 | 0 | 1 | 0 | 0–1 | 0, 0–1 | Nuhato 2018 report |
| **All 21 sites** | | **301** | **10** | **271** | **20** | **55–291** | **77, 55–224** | |

Source: [sites.csv](sites.csv), which also gives the uncertain-status, catalogued and duplicate counts per site; full bibliographic records are in [matching/source-register.csv](matching/source-register.csv). Eleven post-catalogue rows may be the same object as another row (an IAR season note and the final report describing the same seal, for example); each such row is counted as absent only in the upper bound. The rows count of a site includes them.

The joins add data to the corpus as well as testing it. The 92 local objects matched by a row or by a context join (including uncertain-status rows) gain their first publication locator, with report, page and plate; 59 of them gain a registration and 43 a depth with stratum, nearly all at Dholavira ([DATA-UPDATE.md](DATA-UPDATE.md)).

## How to read a site's count

A site's count comes from the publications we could read, so it is a count of reported objects, not of objects found. The best-described sites are those whose report lists objects by registration: Bagasra (Jamison et al. 2017), Farmana (the 2011 report's Tables 7.2 and 7.3), Kanmer (chapter 8 of the 2012 report, in its public draft) and Dholavira (the report's seal and sealing tables, 203 of 210 rows with a registration). At these sites the joins rest on registrations (Bagasra's seals, Kanmer's sealing 06-1054, three Dholavira seals) or on context joins that pick out a single local object. Elsewhere the sources are IAR season summaries and short articles that give a count and sometimes a plate, so their rows are candidates for whatever local objects of the same kind the site has.

Surkotada needs a separate note. It was excavated once, in 1971–72, and its report appeared in 1990, so its objects are post-catalogue by publication although CISI 1 already holds six of them. CISI 1's two Surkotada seals match the report's two seals, which leave the count; CISI 1's four potsherds carry registrations the report's pottery catalogue does not print, so up to four of the 23 potsherd rows are catalogued objects, and the site's post-catalogue count lies between 19 and 23. The same reasoning places the three Desalpar objects of the 1963–64 excavation, the 1973 Nuhato seal (CISI 2 Grb-1) and the Hulas sealing in CISI 1 and 2.

## Sites with no qualifying object

The sweep and the extraction runs read every candidate page for 61 site labels. Besides the 21 sites in the table, the sources reported no inscribed object after the baseline at Sanauli, Binjor, Banawali, Kunal (its seals are geometric), Masudpur, Alamgirpur, Chandigarh, Lohari Ragho, Padri, Kuntasi, Kotada Bhadli, Navinal, Lothal, Daimabad, Juna Khatiya, Pabumath, Pithad, Nageshwar, Kanewal, Rangpur, Prabhas Patan, Taloor Ji Bhit, Wattoowala, the Cholistan sites and Rajanpur, nor at the leads Brass, Donder Khera, Umta, Siyot and Shaktari Timbo. At Kalibangan, Rojdi, Balathal and Chanhu-daro, whose baseline is CISI 3.2 (2019), and at Harappa and Mohenjo-daro (CISI 3.1, 2010), no publication after the baseline year reports a new object, apart from rods that already carry CISI numbers. For several of these sites the reason is a source we could not read, listed next.

## Where the list is incomplete

The sources we identified and could not read are the main limit:

- The excavation reports themselves at three sites. The Internet Archive copy of Nath's Rakhigarhi report is a draft dated 31 December 2014 without a seal catalogue, and the ASI's download for the published edition, like its download for Bisht's Dholavira report, returns only a two-page cover. The Kanmer final volume (RIHN, 2012) is represented by the public draft of its chapter 8.
- Articles known only from journal contents pages: Karanpura (*Puratattva* 43), Khirsara and Kotada Bhadli (*Puratattva* 42), Bhirrana's inscribed terracotta cake (Rao 2008), Masudpur 2009, and Nath and Kumaran 2012, "Inscribed Material from Khirsara".
- Monographs not openly available: Kuntasi (1996) and Mughal 1997, *Ancient Cholistan*; news reports for Wattoowala (2011) and Lakhan-jo-daro; the Lakhan-jo-daro excavation reports; the 2021 Chanhu-daro preliminary report; and Desset 2022 on the Chanhu-daro seals, whose downloaded file held other material.
- IAR after 2013–14, which we found nowhere online. The Rakhigarhi seasons of 2011–16 and from 2021–22 have no object-level publication we could reach.

The local corpus also holds 41 post-catalogue objects at the listed sites that no row names ([local-unnamed.csv](local-unnamed.csv)): 14 at Lakhan-jo-daro, whose excavation reports we did not read; 10 at Dholavira, 8 of them with DHR registrations absent from the report's tables; 6 marked terracotta objects at Karanpura, where IAR 2013–14 gives bulk graffiti counts that the protocol keeps out of the rows; 3 at Nuhato, 2 each at Farmana, Kanmer and Rakhigarhi, and one each at Bhirrana and Rupar. One of the Kanmer objects is the button seal 09-1997, which the corpus transcribes and run 2G left out as a button seal. Thirteen Dholavira seals show the reverse case: the report's table leaves their inscription cell blank, so the extraction excluded them, but their registrations match corpus objects with transcribed inscriptions; we added them as uncertain-status rows matched to those objects.

## Method

The protocol ([PROTOCOL.md](PROTOCOL.md), frozen by `PROTOCOL.sha256` before any object was extracted) fixes the catalogue baseline of each site, what counts as an inscribed object, one row per physical object, the fields, and the match rules. [Amendment 1](AMENDMENT-1.md), written after the keyword sweep and before extraction, limits object rows at CISI 3 sites to publications from the volume's year on and stops count-only statements from duplicating itemised seasons.

We started from the 40 sites of the evidence census ([selection/sites-seed.csv](selection/sites-seed.csv)) and swept every post-1987 IAR volume we could obtain (1987–88 to 2013–14, with 1996–97 and 2003–04 recovered late), *Puratattva* 18–37, fifteen volumes of *Man and Environment*, seven excavation reports from the Internet Archive and the reports the census already held, marking each page that names a site together with an inscription keyword. A web search of 367 queries added 68 publication records, including six IAR volumes and the seal studies of Farmana, Bhirrana and Bagasra. Every downloaded file was fetched with the HTTP routine of `tools/fetch_data.py` against a pinned identifier and checked against the Internet Archive's MD5 and SHA1 where they exist; the 150 files downloaded before a disk-space stop were all re-hashed afterwards, and none differed. Six extraction runs read the candidate pages and wrote rows; a matching run merged them, checked the CISI 1 and 2 basic data for containment and proposed joins; we then reviewed every candidate, every non-registration match and every absent row at a site with local objects ([join-decisions.csv](join-decisions.csv), built by [review/build_list.py](review/build_list.py) from [review/coordinator-decisions.csv](review/coordinator-decisions.csv) and the Dholavira rules in [review/match_dholavira.py](review/match_dholavira.py)).

The review recorded 291 decisions: it added 13 rows, changed run 3's proposal for 265 rows (180 of them by narrowing or widening a candidate set without changing its status) and confirmed 13. Most changes came from three corrections. Run 3 compared registrations only after removing a site prefix, so it missed Dholavira's `DHR-9697` against the report's `9697`, and its prefix-containment rule produced one false match (`218` against `DHR-21897`); we matched on whole digit runs instead. It treated differently formatted trench fields as not comparable, so the Farmana seals, recorded as `Trench IB6` locally and `1B6` in the report, came out unmatched. And it left families with CISI numbers in candidate sets, although an object catalogued before 1987 cannot be a find of the 2000s.

### Context joins

The second correction runs into the protocol's join rule. That rule asks for a registration or a cited plate, and for many rows the only identity evidence is the find context: Farmana's five rows each share area, trench, phase, type and material with exactly one local object, two Kanmer sealings and one Karanpura seal share a trench with one local object, and at Dholavira a row's grid square is often held by one object of its kind in the report's tables and by one compatible object in the corpus. We wrote a rule for these joins before applying it ([review/match_dholavira.py](review/match_dholavira.py) for Dholavira, [review/coordinator-decisions.csv](review/coordinator-decisions.csv) for the rest): a row without an identifier joins a local object when its find context picks out exactly one object on both sides and no recorded depth, layer or period conflicts. The rule gives 67 context joins, 59 of them at Dholavira; one of them is an uncertain-status row, so 66 enter the main count, and Khirsara's plate-number join makes 67 there. The verification run then pointed out that the frozen protocol does not allow context alone, and we agreed. [objects.csv](objects.csv) therefore keeps those rows as candidates under the protocol, records the joined object in `context_join_family` with its basis in `context_join_basis`, and [sites.csv](sites.csv) reports both sets of figures. A later protocol for this list should admit context joins of this kind in advance; the Farmana and Kanmer ones in particular rest on trench codes that are as specific as a registration.

## Exposure

These inscriptions are reserved for frozen predictions, so no file in this package records a sign, a sign count, text length, direction, motif, animal, dimension or weight, and two source titles carry one withheld word for that reason. Reading the sources still exposes their readers: the `gpt-6.1-sol` runs read the text layer and OCR of every candidate page, and runs 1B, 2D, 2G, 2N, 2P, 2E, 2F and 4 each report that an early text filter showed them descriptive passages before it was narrowed. [exposure-log.csv](exposure-log.csv) lists the sources and pages for each run. The coordinating session (Claude Opus 5.5) read no source page; it read the extraction tables, the CISI basic data, the corpus's identity fields and the October evidence-census notes, which describe a few of these objects. A test that uses these objects as fresh data should treat the Codex runs as exposed and the coordinating session as unexposed apart from those census notes.

## Verification

An independent Codex run checked the list three times: once as first built, again after we made context joins protocol candidates, and a third time after we applied its candidate-set conflict rule to every row. Its report is [verification/VERIFICATION.md](verification/VERIFICATION.md).

The count and locator checks are clean. Every cell of [sites.csv](sites.csv) recomputes with the verifier's own code in all three passes (540 cells in the last two), the final pass finds no candidate set that contains a local object with a conflicting registration, grid square, trench or named area among 5,396 pairs, every matched row rests on a unique registration, and the last two locator audits report no failure. The content scan's 96 hits are 66 runs of numbers that coincide with numeric tables in the sources, 24 bibliographic titles and 6 instances of our own wording of the content rule; no source prose and no restricted field was found.

The verifier re-read 60 rows (seed 20261021, stratified by extraction part) from their cited pages without seeing the table's values. Object type agreed for all 39 rows it could assess and the registration was on the page for all 25 that have one; plate or figure agreed for 29 of 35, drawing for 40 of 43 and photograph for 35 of 43. Season (26 of 43), findspot (9 of 35) and page (39 of 57) agreed less often, mostly because the verifier read only the cited page: the season of an IAR entry comes from the volume year, Dholavira's grid squares come from the report's context tables, and the 2019 rods paper has no printed pages in the table, so the verifier recorded blanks where the table has values from elsewhere in the same source. The transcription flag agreed for only 9 of 43, because the table's `no` means that no sign-by-sign reading appears on the cited pages, which a reader of one page records as unknown. The conflicting values it did find are one figure number, two plates the table omits, one doubtful plate reading, eight photograph flags and one inscription status, and they are listed in [verification/blind-sample.csv](verification/blind-sample.csv).

On 40 randomly drawn candidate pages (seed 20261022) the verifier could assess 39 and found no inscribed object that the list omits, so the share of candidate pages with an omission lies between 0 and 9.0% (exact two-sided 95% interval for 0 of 39). Searching the sources for the registrations of the corpus objects that no row names, it found one in full: the Nuhato potsherd NT18/T5/1479 is printed in the 2018 Nuhato report, which the extraction read, so the list misses that object or the extraction took its mark for a potter's mark. For eight more (Dholavira DHR-2217 and DHR-488, Kanmer 09-1997 and catalogue number 170, and four Karanpura numbers) it found only the bare number on pages the extraction read, which may be a coincidence; Kanmer 09-1997 is the button seal discussed above. The remaining registrations occur in no source read.

Two disagreements remain open. The verifier does not accept containment shown by a site section rather than an identifier, so it would return the three Desalpar rows and the two Surkotada seals to the count, raising the count of post-catalogue rows by up to five; we kept them in the catalogue because CISI 1's Desalpar and Surkotada sections hold exactly those objects from the same excavations. And it reports that its own early display filters, like those of the extraction runs, showed it descriptive source text.

## Files

| File | Content |
|---|---|
| [objects.csv](objects.csv) | One row per object, with locators, catalogue status and local match |
| [sites.csv](sites.csv) | Per-site counts and bounds |
| [join-decisions.csv](join-decisions.csv) | Every coordinator decision, with run 3's proposal beside it |
| [local-unnamed.csv](local-unnamed.csv) | Post-catalogue corpus objects at listed sites that no row names |
| [exposure-log.csv](exposure-log.csv) | Who read which source pages, and how |
| [manifest-proposals.json](manifest-proposals.json) | 156 proposed manifest entries for the acquired files |
| [DATA-UPDATE.md](DATA-UPDATE.md) | New sources, fields and coverage changes for DATA.md and the manifest |
| `acquisition/`, `acquisition-web/`, `acquisition-coordinator/` | Acquisition scripts, source registers, candidate pages |
| `extraction/<part>/`, `matching/`, `review/`, `verification/` | Per-run tables, scripts, self-tests and notes |
| `CODEX-PROMPT-*.md`, `launch-codex-*.sh`, `resume-codex-*.sh` | The Codex assignments and launchers |

Acquired files, page text and OCR stay local under `data/raw/2026-10-21-post-catalogue-finds/`.

## Boldest reading and the test that decides it

The corpus's 230 Dholavira objects are Bisht's 1989–2005 finds, entered from the same report tables, so nearly all of the 147 Dholavira rows that remain candidates after the context joins are already in the corpus. If so, the objects the corpus lacks number about 55 to 90, near the lower bound of both sets of figures, concentrated at Surkotada, Bagasra, Bhirrana, Khirsara and Shikarpur, and Dholavira is not the fresh pool for prospective tests that its 208 rows suggest. The test is to recover registrations for the 187 Dholavira objects the corpus records without one (from the source the Lipi maintainer used, or from ICIT) and join them to the report's 225 seals and 61 sealings: the reading predicts that at least 85% of the 147 candidate rows find a registration match and fails if fewer than 60% do. The same reading implies that conjecture C-0003's prospective prediction P3, which needs a newly published assemblage of at least 30 seals, has no fresh site to test it on: Dholavira is the only post-catalogue site with that many seals.
