# Codex run A2: acquire and transcribe the Bhita seal list (Marshall 1911–12) and the Tamil-Brahmi seals, rings and coins (Mahadevan 2003)

Today is 21 October 2026 (UTC). The project is building comparison corpora of seal legends in head-final and head-initial languages for a test written in `experiments/2026-10-21-head-direction-corpora/PROTOCOL.md`. Your part is two head-final sources: the seals and sealings from Bhita (Allahabad district) published by John Marshall, and the Tamil-Brahmi seals, rings and coins catalogued by Iravatham Mahadevan.

The Archaeological Survey reports are Government of India publications of 1914 and 1915, public domain by age; record them as `rights-unverified` with the note "Government of India publication of <year>; public domain by age in India and the United States (our assessment); Internet Archive item states no licence". Mahadevan's *Early Tamil Epigraphy* (Harvard Oriental Series 62, 2003) is in copyright. The Internet Archive copy was uploaded by a third party in 2023 with no licence. Record it as `rights-unverified` with the note "Copyright 2003, Cre-A and Harvard University; third-party upload with no licence; local-only, aggregates only in tracked files". Nothing from Mahadevan's text, tables, readings or translations may appear in any tracked file; tracked files may give table and entry numbers, page numbers and counts.

## Owned paths

- `experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/` (your code, plan, counts, retrospective; notes that quote no Mahadevan text)
- `experiments/2026-10-21-head-direction-corpora/acquisition/asi-ar-1909-10-*.json`, `asi-ar-1911-12-*.json` and `mahadevan-2003-*.json`
- `data/raw/2026-10-21-head-direction-corpora/src-asi-1909-10-*/`, `src-asi-1911-12-*/` and `src-mahadevan-2003-*/` (one new directory per downloaded file)
- `data/raw/2026-10-21-head-direction-corpora/pages-asi-1909-10/`, `pages-asi-1911-12/` and `pages-mahadevan-2003/`
- `data/raw/2026-10-21-head-direction-corpora/transcriptions/asi-ar-1911-12.*` and `mahadevan-2003.*`
- `data/raw/2026-10-21-head-direction-corpora/codex-a2/` (scratch)

## Sources to fetch

Fetch each file with `python -I experiments/2026-10-21-head-direction-corpora/fetch_source.py`, passing `--expect-sha1` and `--expect-bytes` from the values below (from the Internet Archive metadata API, `https://archive.org/metadata/<item>`), each into its own new directory. Download URLs have the form `https://archive.org/download/<item>/<file>` with the item and file names URL-encoded. Also save each item's metadata JSON the same way as its rights witness.

| Source id | Item | File | Bytes | SHA-1 |
|---|---|---|---:|---|
| `asi-ar-1909-10` | `in.ernet.dli.2015.35501` | `2015.35501.Archaeological-Survey-Of-India-Annual-Report-1909-10.pdf` | 15007114 | f243690ee494f2a70d1bd22dc97662c3c7ed22f0 |
| `asi-ar-1911-12` | `in.ernet.dli.2015.207521` | `2015.207521.Annual-Report.pdf` | 33076046 | 41dc237f927bd59036c96e8141d7974c5104dd5c |
| `asi-ar-1911-12` | `in.ernet.dli.2015.207521` | `2015.207521.Annual-Report_djvu.txt` | 725708 | 8c78308cf1c462de3b2e282393360d95ca09256c |
| `asi-ar-1911-12` | `in.ernet.dli.2015.35495` | `2015.35495.Archaeological-Survey-Of-India--Annual-Report-1911-12.pdf` | 18393279 | 38ea23a44a42ec76bb2900029514a066875e34a0 |
| `mahadevan-2003` | `iravatham-mahadevan-early-tamil-epigraphy-from-the-earliest-times-to-the-sixth-century-a.-d.` | `Iravatham Mahadevan - Early Tamil Epigraphy - From the Earliest Times to the Sixth Century A.D..pdf` | 233674839 | 38db2ae4be16ee3272a9e9824328365096dc6b1c |
| `mahadevan-2003` | same item | `Iravatham Mahadevan - Early Tamil Epigraphy - From the Earliest Times to the Sixth Century A.D._djvu.txt` | 1286552 | b92c6dc82a4dfa3a6003764d02cce656dddee30a |

## What to transcribe

1. *Annual Report 1909–10*, pp. 40–42 ("Exploration and research"): the Director-General's summary of Marshall's first season at Bhita. It states that a detailed account would appear in the next volume and that inscribed seals and sealings were found in considerable number. Record the PDF pages and whether any seal legend or list is printed there; transcribe any legend that is.
2. Marshall, "Excavations at Bhita", *Annual Report 1911–12*, pp. 29–94. The contents list "Seals and sealings": introductory remarks (p. 44), seals (p. 47), sealings that are religious (p. 49), of rulers (p. 50), of officials (p. 52), of guilds (p. 56), of private individuals (p. 56), with place names (p. 59), of doubtful character (p. 59), with devices only (p. 60), and an index of seals arranged according to their find-spots (p. 61); plates XVII–XXI show seals 1–13 and 115 and sealings 14–120. Transcribe every numbered entry (seal dies 1–13 and every sealing), with its class heading, the fields of `TRANSCRIPTION-BRIEF.md`, the findspot code exactly as printed (for example a house or chamber number, a room letter and a depth against a floor or the surface), and the editor's date from the letter forms. Entry 24 is a group of 45 sealings from one mould; record the count. Transcribe the index of find-spots (p. 61) into `transcriptions/asi-ar-1911-12.findspots.jsonl`. Then read the excavation account on pp. 29–44 only to record, in the notes, how Marshall numbers houses, chambers and strata and which levels he dates (Mauryan, Śuṅga, Kuṣāṇa, Gupta), with page references, so that each findspot code can later be given a level; do not transcribe the account.
3. Mahadevan 2003, chapter 1: Table 1.6 (coins with Tamil-Brahmi legends), Table 1.7 (seals) and Table 1.8 (rings), with the figures they cite (Figs. 1.23 and 1.24 among them) and the sections of chapter 6 they cross-reference (6.13.2 seals, 6.13.3 rings). The book's index gives the pages as about 50–51, 58–59 and 64–67. Transcribe every row of the three tables with: table and row number, object type, material, provenance (site and findspot as given), legend in Mahadevan's transliteration (and his letter-by-letter rendering where he gives both), his translation, script stage (TB-I, TB-II) and date where given, language (Tamil, Prakrit, Pali), the references he cites, the figure number, and the cross-referenced section. Where chapter 6.13 adds a reading or a note on orthography for a seal or ring, record it with its page. Book pages and PDF pages differ: record both.

Render every page you read at 300 dots per inch or more with PyMuPDF into the pages directories and read it with your image-viewing tool; the OCR text is only a draft.

## Deliverables

- Acquisition records for all files, and `codex/a2-bhita-tamil/SOURCES.md` (source id, item, file, bytes, SHA-256, pages, printed and PDF page ranges read, rights status).
- `transcriptions/asi-ar-1911-12.jsonl`, `transcriptions/asi-ar-1911-12.findspots.jsonl`, `transcriptions/mahadevan-2003.jsonl` and a `.notes.md` per source, all local. Mahadevan rows use the brief's fields with `object_kind` one of `seal`, `ring`, `coin`, and the extra fields `table`, `row`, `script_stage`, `literal_rendering`, `figure`, `section_refs`.
- `codex/a2-bhita-tamil/transcription-counts.json` (tracked, counts only): per source and, for Mahadevan, per table: entries, entries with a legend, with a stated line division, with a translation, with a site, with a findspot, with a depth or level, with a plate or figure reference, doubtful, restored or partly illegible entries, legends by language, uncertain fields by field name, pages read, and entries whose legend you corrected from the OCR draft.
- The render and helper scripts you wrote, each with a docstring giving its command line.

## Verification

1. Every acquisition record shows the expected SHA-1 and size, or the mismatch is reported.
2. Every JSONL line parses and has a `page_pdf` that exists in the named scan.
3. Bhita entry numbers run from 1 to the last number without unexplained gaps; Mahadevan rows run without gaps within each table.
4. Re-read ten entries chosen at random (seed `a2-check`, drawn across both sources) from the page images a second time, independently of your first transcription, and report the differing fields by name.
5. `grep` your tracked files for any legend, translation or table text from Mahadevan and confirm there is none; report the check.
6. `git status --porcelain` shows changes only inside your owned tracked paths.

## Final message

List every path you created, the acquisition checks, the counts, the re-read result, the Mahadevan leak check, every decision the coordinator must make (for example a ring whose findspot is only a river bed, or a legend Mahadevan marks as Prakrit), and the time the run took.
