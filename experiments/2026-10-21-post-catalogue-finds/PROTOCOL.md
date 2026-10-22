# Protocol: inscribed objects reported after the CISI catalogues, 1987 to 2026

Written on 21 October 2026 (UTC) before any object entry was extracted. Question card [Q-1026](../../knowledge/questions/Q-1026-post-catalogue-finds.md). Coordinator: Claude Opus 5.5 (`claude-opus-5-5`) in the Claude Code desktop app. Mechanical work is delegated to the Codex CLI running `gpt-6.1-sol`; each run has its own prompt file in this directory, and [RETROSPECTIVE-CODEX.md](RETROSPECTIVE-CODEX.md) records how each went.

## What we build

We list, one row per physical object, every inscribed Indus object that a publication reported after the *Corpus of Indus Seals and Inscriptions* (CISI) volume covering its site had been published, from 1987 to 2026. Each row says where the object was found, in which season, under which registration or field number, where it is published (page, plate or figure), what kind of object it is, whether the publication shows a photograph or a drawing, whether it prints a transcription, and whether the object is already in the local corpus. Each site then gets a row count from its best publication and a count of the objects the local corpus lacks. The list is a sampling frame for prospective tests: conjecture C-0003's prediction P3, conjecture C-0007's P4, the frozen test of the seal-findspot maps, the prospective predictions of the seal-legend units package and the successor reading of the Mohenjo-daro stratigraphy package all wait on inscriptions that no analysis has read, and objects published after the catalogues are one of the two pools that can supply them.

## The texts stay unread

These inscriptions are reserved for frozen predictions, so this package records where the objects are and what they are, never what they say or show. No file in this package, tracked or local, and no message or log written for it transcribes a sign, counts signs, gives a text length, line count or writing direction, names a motif, animal or scene, or gives a dimension or weight. Where a publication's catalogue entry combines identity and content in one sentence, we copy only the identity fields listed below. Where a table has a remarks or description column, it is skipped. Readers locate entries through the text layer or OCR of each source; page images are opened only when a registration, plate or figure number cannot be read from the text, and the reader then reads captions and numbers only. The local corpus is read through its identity and context fields (site, CISI number, `excavation-idno`, area, block, room, depth, period, phase, object type, material); its sign, motif and size fields are not loaded.

Reading the text of an excavation report exposes its reader to descriptions of the objects. We therefore keep an exposure log (`exposure-log.csv`): for every source, which agent read its text layer, which pages were opened as images, and why. A later test that uses these objects can then state who has seen what.

## Which catalogue covers which site

The catalogue baseline of a site is the latest CISI volume with a section for that site or naming it in its title:

| Volume | Year | Sites |
|---|---|---|
| CISI 1, *Collections in India* | 1987 | Indian sites with a section in CISI 1; every Indian site without a later volume |
| CISI 2, *Collections in Pakistan* | 1991 | Pakistani sites with a section in CISI 2; every Pakistani site without a later volume |
| CISI 3.1, Mohenjo-daro and Harappa | 2010 | Mohenjo-daro, Harappa |
| CISI 3.2 | 2019 | Shahr-i Sokhta, Mundigak, Mehrgarh, Nausharo, Sibri, Dauda-damb, Chanhu-daro, Ahar, Balathal, Gilund, Kalibangan, Rojdi |
| CISI 3.3, Indo-Iranian borderlands | 2022 | Eastern Iran, Turkmenistan, Tajikistan, Uzbekistan, Afghanistan |

An object is a post-catalogue object when a publication dated after its site's baseline year reports it and the baseline volume does not contain it. CISI 1 and 2 are held, so for their sites we check containment directly against the transcribed basic data (`data/raw/2026-10-13-cisi-basic-data-full/`) and the site sections. CISI 3.1, 3.2 and 3.3 are not held. An object at one of their sites that was published before the volume's year may be in it; such rows are kept with `catalogue_status = possibly-in-cisi3` and left out of the post-catalogue count. A CISI 3 number absent from the local export (the 1,127 numbers of the [CISI 3 range count](../2026-10-13-cisi3-range-coverage/README.md)) is a catalogued object the corpus lacks, not a post-catalogue find, and is not listed here. Rows whose excavation season precedes the baseline year but whose first report we found is later (Surkotada, excavated 1971–72 and published in 1990, is the main case) are kept and flagged `excavated_before_baseline = yes`.

Finds outside South Asia belong to [Q-1024](../../knowledge/questions/Q-1024-finds-outside-south-asia.md) and are out of scope.

## What counts as an inscribed object

A row is an object that its publication describes as bearing Indus script: a seal, sealing, tablet, tag, potsherd or vessel, metal or stone tool, ornament or other object said to carry an inscription, a legend, script, signs, characters or letters. Seals described only by an animal or a geometric pattern, button seals, uninscribed sealings and potter's marks or graffiti that the publication does not call Harappan or Indus signs are not rows. A bulk statement such as "157 graffiti" is recorded as a site-level count of marks outside scope, without object rows. A potsherd becomes a row when the publication calls its mark a Harappan or Indus sign, character, letter, script or inscription, individually or in an enumerated list. When the publication's wording leaves the script status open ("signs resembling", "possibly inscribed"), the object is a row with `inscription_status = uncertain`, and uncertain rows are counted separately.

One row is one physical object. Several impressions on one sealing are one object, a seal and a modern impression of it are one object, and fragments the publication says join are one object. A publication that gives only a count ("five inscribed seals") yields that many rows with `row_basis = enumerated-count`, each carrying the same locator and no registration; a description of a group without a count yields no rows and a site-level note.

The same object often appears in several publications: an IAR season summary, a preliminary report, a final report, a journal article. Each object gets one row, and the publication that identifies it best is its primary publication, ranked final excavation report, then excavation report or monograph, then journal article with an object list, then IAR entry, then news report. The others are listed in `other_publications`. Two entries are merged into one row when they share a registration number, or share season, findspot and object type with no conflicting field; otherwise both rows stay, linked by `possible_duplicate_of`, and the site count gives both bounds.

## Fields

`objects.csv` holds one row per object with these fields:

| Field | Content |
|---|---|
| `row_id` | `PCF-<site code>-<nnn>`, stable once assigned |
| `site`, `site_as_published` | The project's site label (the local corpus label where one exists) and the name in the publication |
| `country`, `baseline_volume`, `baseline_year` | From the table above |
| `excavation` | Excavating body or project |
| `season` | As printed |
| `registration` | Registration, field or antiquity number as printed; doubtful characters in square brackets |
| `other_numbers` | Lot, trench-find or catalogue numbers in the publication |
| `findspot`, `depth_or_layer`, `period_or_phase` | As printed, for identity checks and the object record |
| `object_type` | `seal`, `sealing`, `tablet`, `tag`, `inscribed-pottery`, `inscribed-tool`, `other`, `uncertain` |
| `object_subtype`, `material` | Shape class as printed (square seal, cylinder seal, bas-relief tablet) and material as printed |
| `primary_publication`, `page`, `pdf_page`, `plate_or_figure` | Source register id, printed page, PDF page and plate or figure number |
| `photo_published`, `drawing_published`, `transcription_published` | `yes`, `no` or `unknown` from the primary publication; a transcription is a printed sign-by-sign reading or sign-list numbering, and a photograph or drawing is not one |
| `other_publications` | Source ids with pages |
| `row_basis` | `individual` or `enumerated-count` |
| `inscription_status` | `stated` or `uncertain` |
| `catalogue_status` | `post-catalogue`, `possibly-in-cisi3`, `in-baseline-catalogue` |
| `excavated_before_baseline` | `yes`, `no`, `unknown` |
| `possible_duplicate_of` | Another `row_id` |
| `local_match`, `local_family_ids`, `match_basis`, `match_note` | Below |
| `extracted_by`, `reviewed_by` | Run or session that wrote and reviewed the row |

The list carries no motif, sign, text-length, direction, dimension or weight field.

## Matching to the local corpus

The local corpus is the pinned normalized Lipi export, `data/normalized/lipi_observed_faces.jsonl` (SHA256 `1220f559…`, Lipi commit `fc8813a`), in which one object is one `object_family_id`. A row is compared with every family at the same site (and at the site's aliases) on CISI number, `excavation-idno`, findspot, depth, period or phase, object type and material, and with the CISI 1 and 2 basic data for catalogue containment. Registrations are compared after removing case, spaces, punctuation and site prefixes and after allowing for the export's habit of appending other numbers to a registration ([DATA.md](../../knowledge/DATA.md), section 2).

| `local_match` | Rule |
|---|---|
| `matched` | Exactly one family has the same registration after normalisation, or its record cites this publication's plate or figure for the object, and no context field conflicts |
| `candidate` | One or more families of compatible object type at the site could be the object, but no identifier ties them to it; all are listed |
| `absent` | No family can be the object: the site has no local family, or every family of compatible type is matched to another row or has a conflicting registration or context |
| `in-baseline-catalogue` | The object is in the baseline CISI volume; listed for audit and not counted |

Codex proposes a match status for every row with its evidence. The coordinator reviews every `candidate`, every `matched` row whose basis is not an exact registration, and every `absent` row at a site that has local families, and records each decision in `join-decisions.csv`. An uncertain join stays `candidate`; we do not resolve it by reading the inscription on either side.

Per site we report the rows, the matched rows and two bounds on the objects the local corpus lacks. The upper bound counts every row not matched. The lower bound counts the `absent` rows plus the `candidate` rows that exceed the number of local candidate families not matched elsewhere.

## Sources and how they are read

The site list starts from the evidence census batches (north India, Gujarat with Kutch and Maharashtra, Pakistan with Afghanistan), which name the sites and reports and counted finds where publications gave counts. We extend it by a keyword sweep of every post-1987 volume of *Indian Archaeology – A Review* (IAR) we hold or can fetch, every post-1987 issue of *Puratattva* and *Man and Environment* on the Internet Archive, the excavation reports the card names (Farmana 2006–08, Rakhigarhi 1997–2000 by Nath, Surkotada, chapter 6 of the Kanmer report) and others found on the way (Farmana 2007–08, Tarkhanewala Dera 2009), the reports the census already holds (Dholavira 2015 preliminary, Nuhato 2018, Shikarpur 2008–09, Kanmer chapter 8, Khirsara, Binjor, Nagwada) and Pakistani journal reports found by web search (Lakhan-jo-daro, Ganweriwala, Chanhu-daro 2015–17, Wattoowala, Cholistan sites, Nuhato and Gharo Bhiro). The sweep marks every page that names a site together with an inscription keyword (seal, sealing, tablet, inscri-, script, sign, character, letter, legend, graffit-); extraction reads those pages and their neighbours.

Internet Archive items are acquired with the HTTP fetch routine of [tools/fetch_data.py](../../tools/fetch_data.py), called on proposed manifest entries that carry the item identifier, file name, byte count and the archive's MD5 and SHA1; the SHA256 of each file is recorded at download, and the proposed entries go to maintainers in `manifest-proposals.json`. Files already held are used in place and verified by hash. Every acquired file stays local under `data/raw/2026-10-21-post-catalogue-finds/`, is treated as untrusted, and is read only by scripts kept outside that directory and run with `python -I`.

## Work plan and delegation

1. Acquisition and sweep (Codex run 1): fetch and hash the sources, extract per-page text, write the source register, the manifest proposals and the candidate-page index.
2. Extraction (Codex run 2, in regional parts): read candidate pages and write object rows with locators.
3. Matching (Codex run 3): merge the regional rows, deduplicate across publications, propose match statuses against the local corpus and build the per-site counts.
4. Review (coordinator): source selection, join decisions, uncertain inscription status, duplicates.
5. Verification (Codex run 4): re-extract a random sample of rows from their pages without seeing the table's values, recompute every count from `objects.csv`, check every locator against the source register and check that no tracked file carries a forbidden field.

Each Codex run owns only paths inside this directory and `data/raw/2026-10-21-post-catalogue-finds/`, makes no commit, edits nothing outside them, keeps raw material local and does not transcribe texts.

## Outputs

Tracked in this directory: `PROTOCOL.md`, `README.md` with per-site counts and the total of absent objects by site with the publication basis, `objects.csv`, `sites.csv`, `join-decisions.csv`, `source-register.csv`, `manifest-proposals.json`, `exposure-log.csv`, `DATA-UPDATE.md` (new sources, fields and coverage changes for maintainers to fold into DATA.md and the manifest), the Codex prompts and launch scripts, the verification outputs, `RETROSPECTIVE.md` and `RETROSPECTIVE-CODEX.md`. Local only: acquired files, page text, OCR and any page image. Registry entry draft: [POST-CATALOGUE-FINDS-2026-10-21.json](../../knowledge/registry/attempts/POST-CATALOGUE-FINDS-2026-10-21.json).

The list is done when each site with reported post-catalogue finds has a row count from its best publication, every object row is `matched`, `candidate`, `absent` or `in-baseline-catalogue`, and `python tools/kb.py check` passes for this package's files. Objects are counted from publications, so a site count is a count of reported objects; finds that were never published, or published only where we could not reach, are outside it, and the README lists the sources we looked for and could not obtain.
