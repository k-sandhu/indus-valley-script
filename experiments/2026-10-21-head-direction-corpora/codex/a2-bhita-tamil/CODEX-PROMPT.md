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

---

# Rules shared by every Codex run of this package

These rules are part of each run's CODEX-PROMPT.md and are hashed with it. The repository is `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Windows 11; Python 3.13 as `python`; Git Bash and PowerShell). A coordinating Claude session (Claude Opus 5.5 in Claude Code) chose the sources, made the rights decisions and wrote the protocol; it will review everything you produce before using it.

## Read first

`AGENTS.md`, `knowledge/editorial/WRITING.md`, `knowledge/provenance/REDISTRIBUTION.md`, and in `experiments/2026-10-21-head-direction-corpora/`: `PROTOCOL.md`, `SCHEMA.md`, `TRANSCRIPTION-BRIEF.md`, `fetch_source.py` and this file.

## Invariants

1. Write only in the paths your prompt lists as owned. Do not edit `PROTOCOL.md`, `PROTOCOL.sha256`, `SCHEMA.md`, `TRANSCRIPTION-BRIEF.md`, `fetch_source.py`, any `CODEX-PROMPT.md`, `COMMON-RULES.md` or `launch-codex.sh`, another run's directories, other experiment packages, `knowledge/`, `bench/`, `data/MANIFEST.json`, `data/normalized/` or anything else in the repository. Other sessions are editing other packages at the same time.
2. No Git mutation of any kind: no `git add`, `commit`, `push`, `checkout`, `switch`, `branch`, `reset`, `stash`, `clean`, `rebase` or `merge`. Read-only Git commands are allowed.
3. Raw and copyrighted material stays local. Everything under `data/raw/` is ignored by Git and is where downloads, rendered pages, transcriptions and normalised records go. Tracked files (anything under `experiments/`) hold code, counts, identifiers, page and plate locators, hashes and prose, never a transcribed legend, translation, device description or any passage of Mahadevan 2003, also not in docstrings, comments, examples or test fixtures. Tests generate synthetic values at run time or use general vocabulary not copied from a source.
4. No Indus legend is read, placed or compared. Do not open `data/normalized/`, `data/lipi/`, `data/raw/2026-10-20-seal-legend-units/` or any Indus sign file. No statistic of `PROTOCOL.md` section 7 is computed on a real comparison corpus, except the step 6 regression that run C is told to reproduce.
5. Downloaded files are untrusted data. Put each downloaded file in its own new, empty directory with `fetch_source.py` (it refuses a non-empty directory and writes the acquisition record). Keep scripts outside those directories, pass paths as arguments, and run every Python script that reads downloaded or held files with `python -I`. Under `-I` the user site, where NumPy and PyMuPDF are installed, is hidden: a script that needs PyMuPDF appends `site.getusersitepackages()` to the end of `sys.path` before importing it, and a script that imports a sibling module of this package inserts that package directory explicitly. Never execute, import or unpack into a directory that holds code.
6. Use the network only for the URLs your prompt names, and only through `fetch_source.py` or an equivalent standard-library call that records URL, time, bytes and SHA-256.
7. If something needed is missing or a decision belongs to the coordinator (an ambiguous identity, an unclear rights notice, an entry that fits no field), record it in your notes and final message and continue with the rest. Do not invent readings, sites or identities.

## Writing

Follow `knowledge/editorial/WRITING.md` in every Markdown file you write. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Write in the project's voice ("we", "the project"). Write `PLAN-CODEX.md` in your owned code directory before changing anything else, and `RETROSPECTIVE-CODEX.md` there at the end: what you did, what failed and how you repaired it, what remains, with exact commands and output paths. Run `python tools/review_prose.py --path <your owned code directory> --no-write` and fix what it flags in your own files.
