# Codex run A1: acquire and transcribe the Basarh seal lists (Bloch 1903–04, Spooner 1913–14)

Today is 21 October 2026 (UTC). The project is building comparison corpora of seal legends in head-final and head-initial languages for a test written in `experiments/2026-10-21-head-direction-corpora/PROTOCOL.md`. Your part is the Indo-Aryan seals and sealings found at Basarh (ancient Vaiśālī, Bihar) and published in two Archaeological Survey of India annual reports. Both reports are Government of India publications of 1906 and 1917, public domain by age; the Internet Archive items record no licence. Record their rights status as `rights-unverified` with the note "Government of India publication of <year>; public domain by age in India and the United States (our assessment); Internet Archive item states no licence".

## Owned paths

- `experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/` (your code, plan, notes, counts, retrospective)
- `experiments/2026-10-21-head-direction-corpora/acquisition/asi-ar-1903-04-*.json` and `asi-ar-1913-14-*.json` (acquisition records written by `fetch_source.py`)
- `data/raw/2026-10-21-head-direction-corpora/src-asi-1903-04-*/` and `src-asi-1913-14-*/` (one new directory per downloaded file)
- `data/raw/2026-10-21-head-direction-corpora/pages-asi-1903-04/` and `pages-asi-1913-14/` (rendered page images)
- `data/raw/2026-10-21-head-direction-corpora/transcriptions/asi-ar-1903-04.*` and `asi-ar-1913-14.*`
- `data/raw/2026-10-21-head-direction-corpora/codex-a1/` (scratch)

## Sources to fetch

Fetch each file with `python -I experiments/2026-10-21-head-direction-corpora/fetch_source.py`, passing `--expect-sha1` and `--expect-bytes` from the values below (they come from the Internet Archive metadata API, `https://archive.org/metadata/<item>`), into its own directory such as `data/raw/2026-10-21-head-direction-corpora/src-asi-1903-04-dli207529-pdf/`. Download URLs have the form `https://archive.org/download/<item>/<file>` with the file name URL-encoded. A failed check is recorded and reported, never overwritten.

| Source id | Item | File | Bytes | SHA-1 |
|---|---|---|---:|---|
| `asi-ar-1903-04` | `in.ernet.dli.2015.207529` | `2015.207529.Archaeological-Survey.pdf` | 204293478 | 2d952c7a8a9be1065d425bd5ddaa16f017eeae10 |
| `asi-ar-1903-04` | `in.ernet.dli.2015.207529` | `2015.207529.Archaeological-Survey_djvu.txt` | 971300 | f95663462e6b136b3651536940e8a7115c8255ea |
| `asi-ar-1903-04` | `in.gov.ignca.21816` | `21816.pdf` | 38614635 | 9275652c9ad17af56a38e11050f1592c9ad45950 |
| `asi-ar-1913-14` | `dli.ministry.09311` | `17178.55107.pdf` | 50488078 | b304e4ef9197109894fc5f9ba1132531022d7fea |
| `asi-ar-1913-14` | `dli.ministry.09311` | `17178.55107_djvu.txt` | 992428 | 2dd167f2e4f9717130dede795d7eb039c5db657a |
| `asi-ar-1913-14` | `in.ernet.dli.2015.35545` | `2015.35545.Annual-Report-Of-The-Archaeological-Survey-Of-India-1913-14.pdf` | 24146577 | a32a0c2621ccea5dea587fd9b32a87cf6676cd93 |

Also save each item's metadata JSON (`https://archive.org/metadata/<item>`) with `fetch_source.py` into its own directory; it is the observed rights witness. Record the title page of each scan (printed title, year, printer) in your notes.

## What to transcribe

1. Bloch, "Excavations at Basarh", *Annual Report 1903–04*. The contents list the section "Inscribed clay seals", p. 101, with seals of Dhruvasvāminī and Ghaṭotkacagupta (p. 107), seals of officials, guilds and corporations (p. 107), seals of temples and religious legends (p. 110), seals of private individuals (p. 112), seals with single letters, without inscription, broken or illegible (p. 119), an appendix and a postscript (p. 120). Bloch counts about 720 clay pieces with somewhat over 1,100 impressions of about 120 varieties; his numbered entries are varieties (seal dies), several with an impression count. The list of plates names three or more plates "Excavations at Basarh: Inscribed clay seals". Transcribe every numbered entry of pp. 101–120 with the fields of `TRANSCRIPTION-BRIEF.md`, including the impression count, the plate and figure number, and Bloch's remarks on where the few seals found outside the hoard chamber lay. Where Bloch prints a legend in Nāgarī type as well as in transliteration, record the Nāgarī form in an extra field `legend_nagari_as_printed`.
2. Spooner, "Excavations at Basarh", *Annual Report 1913–14*, pp. 98–185, "List of Seals (Found at Basarh in 1912)" from p. 124, numbered by the Unclassified Register of Finds, with plates XLVI–L. An entry is a clay lump (or token) with one or more impressions; sub-entries such as 8 A and 8 B are the separate impressions. Transcribe every entry and sub-entry, its findspot (square and depth), its duplicates by register number, its references to Bloch's numbers ("A. S. R. 1903–1904, p. 114, No. 73"), and the plate figure. Then, as a second priority, read the Unclassified Field Register that follows the list and record, for every register number that is a seal or a duplicate of one ("See special List of Seals"), its square and depth, in `transcriptions/asi-ar-1913-14.register.jsonl`. Check the corrigenda at the front of the volume (they include "for 557 read 557 A") and apply none silently: record each corrigendum that touches the list.
3. Locate the plate pages for both lists and record, per plate, the PDF page and the figure numbers it shows. Do not crop or describe the images beyond that.

Render every page you read at 300 dots per inch or more with PyMuPDF into the pages directories, read it with your image-viewing tool, and use the OCR text only as a draft. Each entry's `page_pdf` is the PDF page you read it from, in the scan you name in `scan`; use the larger scan by default and the other where it is more legible, and say which.

## Deliverables

- Acquisition records for all files, and a short `codex/a1-basarh/SOURCES.md` table: source id, item, file, bytes, SHA-256, pages, printed page range read, PDF page range read, rights status.
- `transcriptions/asi-ar-1903-04.jsonl`, `transcriptions/asi-ar-1913-14.jsonl`, `transcriptions/asi-ar-1913-14.register.jsonl` and a `.notes.md` per source, all local.
- `codex/a1-basarh/transcription-counts.json` (tracked, counts only): per source, entries, sub-entries, entries with a legend, with a stated line division, with a translation, with a findspot, with a depth, with an impression count, with a plate reference, entries marked doubtful, restored or partly illegible, uncertain fields by field name, pages read, and the number of entries whose legend you corrected from the OCR draft.
- The render and helper scripts you wrote, each with a docstring giving its command line.

## Verification

1. Every acquisition record shows `sha1_matches_expected: true` and `bytes_match_expected: true`, or the mismatch is reported.
2. Every JSONL line parses, carries the fields of the brief, and has a `page_pdf` that exists in the named scan.
3. The entry numbers of each list run without unexplained gaps; list every gap and say whether the edition skips the number.
4. Re-read ten entries chosen at random (seed `a1-check`) from the page images a second time, independently of your first transcription, and report how many fields differ, by field name, in `transcription-counts.json`.
5. `git status --porcelain` shows changes only inside your owned tracked paths.

## Final message

List every path you created, the acquisition checks, the counts from `transcription-counts.json`, the result of the ten-entry re-read, every decision the coordinator must make (for example an entry whose identity with a Bloch number is unclear, or a legend you could not read), and the time the run took.

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
