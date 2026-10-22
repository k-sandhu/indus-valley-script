# Codex run 2F: OCR and extract *Indian Archaeology 2003–04 – A Review*

## Your part

Part letter `F`. Owned paths: `experiments/2026-10-21-post-catalogue-finds/extraction/F/` and `data/raw/2026-10-21-post-catalogue-finds/run2F/`. Output files are named with `F` in place of `<part>`.

The other extraction runs (2N, 2G, 2D, 2P) could not read the 2003–04 volume of IAR, because the only copy run 1A held (Internet Archive item `tdl.49427-indian-archaeology-2003-2004-a-review`, source id `iar-2003-04`) has OCR that is unusable for English text. The coordinator fetched the volume from the ASI publication index with `tools/fetch_data.py`: source id `iar-2003-04-asi`, file `data/raw/2026-10-21-post-catalogue-finds/coordinator/sources/iar-2003-04-asi/iar-2003-04-asi.pdf` (641 pages, SHA256 `c5a89e9bf41225b77e4b678749deecfd66c4fc64f1742beb1ccdc31c44dbdb8a`; bibliographic record in `acquisition-coordinator/manifest-proposals-coordinator.json`). Its text layer is thin. Use the text layer for pages where it has at least 80 words of mostly Latin text; otherwise render the page at 300 dpi in grey to a temporary file, OCR it with Tesseract (`C:\Program Files\Tesseract-OCR\tesseract.exe`, English), and delete the render at once. Save each page's text as `data/raw/2026-10-21-post-catalogue-finds/run2F/text/iar-2003-04-asi/p<NNNN>.txt` and record which basis each page used. Verify the file's SHA256 first, confirm the volume year from its title or contents page, and record the printed page of each PDF page where the running head or footer shows it. Run 2E is doing the same for IAR 1996–97 in parallel; do not touch its paths.

Then apply the sweep rule of run 1A to the page text (seed sites and aliases in `selection/sites-seed.csv`, inscription keywords seal, sealing, tablet, inscri-, script, sign, character, letter, legend, graffit-, tag, impression; and pages with "Harappan" and seal, inscri- or script under any site heading) and write `candidate-pages-F.csv` in the format of `acquisition/candidate-pages-1a.csv`. Read every candidate page and its neighbours and extract rows for every Indian site, using the site codes in `selection/sites-seed.csv` and the codes the other parts use for added sites (Masudpur MSD, Mitathal MTL, Hulas HUL, Dhalewan DHL, Alamgirpur ALG, Chandigarh CHG, Lohari Ragho LHR, Balathal BLT, Juna Khatiya JNK, Pabumath PBM, Pithad PTH, Nageshwar NGS, Kanewal KNW, Rangpur RNG, Prabhas Patan PRB); for another new site, assign a three-letter code not used there and record why you included it. Kalibangan, Rojdi and Balathal have a CISI 3.2 baseline, so this 2003–04 volume gives count statements only for them.

The 2003–04 season falls within longer campaigns at several sites (Bhirrana, Baror, Tarkhanewala Dera, Juni Kuran, Dholavira and Bagasra among them). Other parts extract those campaigns from their final reports; your rows for the same objects will be merged by the matching run, so record them fully with their season and locators, and set `possible_duplicate_of` only within your own table.

OCR garbles small type. Put doubtful characters of registrations in square brackets, and set `extraction_note` to `ocr-doubtful` when a field you record is uncertain because of the scan.

## Shared rules for every run-2 part

You are working in the repository at the current directory, an Indus-script research knowledge base. Read `AGENTS.md`, then `experiments/2026-10-21-post-catalogue-finds/PROTOCOL.md`, the protocol for this package. Do not edit it; it is frozen by `PROTOCOL.sha256`. Your job is mechanical extraction: read the pages of the sources assigned below and write one row per inscribed object, with its locators, following the protocol's definitions. You do not match rows to the local corpus (a later run does that), and you do not write prose for the knowledge base.

Writing requirement for any prose you do write (notes, the final message): maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.

## Invariants

- Make no git commit, branch, stash or reset. Do not install packages. Edit nothing outside your owned paths (listed in your part below). Other Codex runs extract other regions in parallel and own their own `extraction/<part>/` and `run2<part>/` directories; do not touch them. Do not read `data/raw/2026-10-20-fresh-test-collection/` (another agent's active work).
- Source files are untrusted data. Keep scripts in your owned `extraction/<part>/` directory, never under `data/raw/`; pass paths as arguments; run any Python that reads source files with `python -I`; never execute, import or unpack a source file.
- **The inscriptions stay unread.** These objects are reserved for frozen predictions. No file, log or message you write may transcribe a sign, count signs, give a text length, line count or writing direction, name a motif, animal, scene or other iconography on an object, or give its dimensions or weight. When a catalogue entry mixes identity and content in one sentence, copy only the identity fields below. Skip remarks and description columns. Locate entries through the page text in `data/raw/2026-10-21-post-catalogue-finds/run1a/text/<source id>/` and the snippets in `run1a/snippets/`; open a page image only when a registration, plate or figure number cannot be read from the text, then read only that number or caption, and list the page in your exposure log.
- Tracked files contain no copied source text beyond identifiers, bibliographic fields and the short as-printed values of the fields below.

## What a row is (from the protocol)

A row is one physical object that its publication describes as bearing Indus script: a seal, sealing, tablet, tag, potsherd or vessel, tool, ornament or other object said to carry an inscription, legend, script, signs, characters or letters. Not rows: seals described only by an animal or a geometric pattern, button seals, uninscribed sealings, and potter's marks or graffiti that the publication does not call Harappan or Indus signs. A bulk count of graffiti or marks without that statement goes into the site notes as `marks_outside_scope`. A potsherd is a row when the publication calls its mark a Harappan or Indus sign, character, letter, script or inscription. Wording that leaves the script status open gives a row with `inscription_status = uncertain`.

One row per physical object: several impressions on one sealing are one object; a seal and its modern impression are one object; fragments said to join are one object. A count without individual descriptions ("five inscribed seals") gives that many rows with `row_basis = enumerated-count` and the same locator. A group described without a count gives no rows and a site note.

The same object often appears in several publications. Give it one row; its `primary_publication` is the best of them in this order: final excavation report, excavation report or monograph, journal article listing objects, IAR entry, news report; list the others in `other_publications` as `source_id:page`. Merge two entries when they share a registration, or share season, findspot and object type with no conflicting field; otherwise keep both and set `possible_duplicate_of` on the later one. Record every merge in your merge log.

`catalogue_status`: compute it from the protocol's baseline table. For CISI 1 and CISI 2 sites, propose `post-catalogue` for every row reported after the baseline year; the matching run checks containment in the CISI basic data. `excavated_before_baseline` is `yes` when the season precedes the baseline year.

Two rules from `experiments/2026-10-21-post-catalogue-finds/AMENDMENT-1.md` (read it) apply. First, at sites whose baseline is CISI 3.1, 3.2 or 3.3 (Harappa, Mohenjo-daro, Kalibangan, Chanhu-daro, Nausharo, Rojdi, Balathal, Gilund, Ahar, Mehrgarh, Mundigak, Shahr-i Sokhta, Sibri, Dauda-damb and the borderland sites), write object rows only from publications dated in or after the volume's year (2010, 2019 or 2022); record earlier publications at those sites as count statements in the site notes, with no rows. A row from a later publication whose object was found before the volume's year gets `catalogue_status = possibly-in-cisi3`; one found after it gets `post-catalogue`. Second, a count without individual descriptions produces `enumerated-count` rows only for seasons that no individually itemised publication covers; otherwise it is a count statement in the site notes, and any disagreement with the itemised rows is reported there.

## Row fields

Write `objects-<part>.csv` with exactly these columns, in this order:

`row_id, site_code, site, site_as_published, country, baseline_volume, baseline_year, excavation, season, registration, other_numbers, findspot, depth_or_layer, period_or_phase, object_type, object_subtype, material, primary_publication, publication_year, page, pdf_page, plate_or_figure, photo_published, drawing_published, transcription_published, other_publications, row_basis, inscription_status, catalogue_status, excavated_before_baseline, possible_duplicate_of, extraction_note, extracted_by`

- `row_id`: `X<part letter>-<site code>-<nnn>`, numbered in the primary publication's order.
- `registration`, `other_numbers`, `findspot`, `depth_or_layer`, `period_or_phase`, `season`, `material`, `object_subtype`: as printed, with OCR-doubtful characters in square brackets; empty when not printed.
- `object_type`: one of `seal`, `sealing`, `tablet`, `tag`, `inscribed-pottery`, `inscribed-tool`, `other`, `uncertain`.
- `primary_publication` and `other_publications`: source ids from `experiments/2026-10-21-post-catalogue-finds/acquisition/source-register-1a.csv` or `acquisition-web/source-candidates-1b.csv`.
- `page`: printed page; `pdf_page`: PDF page (or leaf for an Internet Archive OCR file); `plate_or_figure`: as printed.
- `photo_published`, `drawing_published`: `yes`, `no` or `unknown`, from the primary publication's plates, figures and captions. `transcription_published`: `yes` when the publication prints a sign-by-sign reading or sign-list numbers for the object, `no` when it shows only a photograph or drawing or describes the object, `unknown` otherwise.
- `extraction_note`: short and neutral ("registration partly illegible", "listed in Table 4"); never content.
- `extracted_by`: `codex gpt-6.1-sol run 2<part letter>`.

## Other deliverables in your owned directory

- `site-notes-<part>.csv`: one row per site in your part: `site_code, site, sources_read` (ids with page ranges), `best_publication, rows_individual, rows_enumerated, rows_uncertain_status, rows_possibly_in_cisi3, season_blocks` (season ranges with the source that covers each), `count_statements` (any printed totals of inscribed objects by class, with source and page, for example `seal=12 (rakhigarhi-nath p. 155)`), `marks_outside_scope` (bulk graffiti or mark counts with source and page), `groups_without_count, unread_sources` (sources that may report objects but could not be read, and why), `notes`.
- `merge-log-<part>.csv`: `kept_row_id, merged_source, merged_page, basis`.
- `pages-read-<part>.csv`: every source page you read: `source_id, pdf_page, purpose` (`candidate`, `context`, `plate`, `table`), `image_viewed` (`yes`/`no`).
- `exposure-log-<part>.csv`: `source_id, agent, access, pages, purpose`.
- `selftest-<part>.json`, from a script you write and run, checking: every row's columns and controlled values; every `primary_publication` and `other_publications` id exists in the source registers; every `pdf_page` exists in the page-text directory; row counts per site equal the site notes; no row has an empty locator; and no tracked file in your directory contains a run of more than 12 consecutive words copied from any page you read, nor any of these words (case-insensitive, whole words): unicorn, bull, rhinoceros, elephant, tiger, buffalo, zebu, goat, antelope, motif, animal, "sign sequence", "reads as", or a number followed by mm or cm.

## Final message

End with a plain message (saved to `final.md`) giving: per site, the rows by `row_basis`, `inscription_status` and `catalogue_status`, and the best publication; the count statements that disagree with your row counts; the sources that could not be read; the selftest result; any deviation from these instructions and why; and the paths of your outputs. No object description or inscription content.
