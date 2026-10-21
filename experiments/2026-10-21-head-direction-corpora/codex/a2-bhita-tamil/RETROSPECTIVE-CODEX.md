# A2 acquisition and transcription retrospective

We acquired all six requested source files and four metadata witnesses. All six supplied sizes and SHA-1 values match. A second digest pass checked SHA-256, SHA-1 and size for all ten files. Each download remains in its own local directory, with its acquisition record under `acquisition/`. `SOURCES.md` lists the files, hashes, rights decisions and inspected page ranges.

We read 300 dpi page images and wrote 120 Bhita catalogue rows, 25 findspot-index rows and 32 Mahadevan table rows. Bhita numbers run from 1 through 120. Tables 1.6, 1.7 and 1.8 have 13, five and 14 rows, respectively, without gaps. The 1909–10 summary contributes zero catalogue entries. We kept the Bhita excavation account as notes with page references, preserving its distinctions between building numbers, chamber letters, floors and depth reference points. Entry 24 retains the group count of 45. The local JSONL adds source scan paths, grouped impressions, source-reading notes and orthography notes to the brief's fields.

`transcription-counts.json` gives the required aggregates for each source and table. It distinguishes a reported legend from a transcribed reading, and a stated line count from a supplied transliteration. The OCR difference count searches the complete image-checked legend in the OCR after removing whitespace and normalizing Unicode to NFC. Diacritic and punctuation differences count. It does not measure semantic OCR errors.

## Commands and outputs

We ran the acquisition wrapper from the repository root:

```text
python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/acquire.py --root .
```

It calls the frozen `fetch_source.py` for every URL and passes the supplied pins. The wrapper's six file specifications and four metadata requests retain the exact inputs. Downloads and page images are under `data/raw/2026-10-21-head-direction-corpora/`. The raw directory is ignored by Git.

We rendered pages with `render_pages.py --pdf <downloaded-pdf> --out <pages-directory> --pages <one-based-pages>`. The scan paths and page lists are in the local render manifests; `SOURCES.md` gives their printed-page counterparts. The 1911–12 primary range is `1,8,70-123`; the alternate range is `1,7,60,70`. The 1909–10 range is `1,60,69-71,73-75`. The Mahadevan range is `1,75,90,93-111,198,244,252,279-281`, with p. 252 read through figure crops. We used `--rotate 90 --label upright --pages 106-111` for the six landscape table pages. Crops retain the same 300 dpi scale. Every source-reading Python invocation used `-I`; the renderer appends the local site-packages path before importing PyMuPDF.

We expanded the local image annotations and ran the checks:

```text
python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/build_records.py --annotations data/raw/2026-10-21-head-direction-corpora/codex-a2 --output data/raw/2026-10-21-head-direction-corpora/transcriptions --acquisitions experiments/2026-10-21-head-direction-corpora/acquisition
python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/verify_records.py --root .
python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/audit_package.py --root .
python tools/review_prose.py --path experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil --no-write
```

`verification.json` records the acquisition checks and JSONL validation. All 152 catalogue rows contain the brief's fields, point to existing scans and rendered pages within the scan bounds, and pass the sequence checks. The separate findspot file parses and points to PDF p. 121. Device fields satisfy the fifteen-word limit. Counts and verification files contain no source readings.

## Repairs and reread

Printed pages and PDF pages differ, and the primary Bhita scan interleaves plates and blank leaves. We used the printed page numbers in the images and retained both page systems. An initial manifest lookup used the wrong separator in its filename; the saved manifests use `-manifest.json`. A process launch briefly failed with a disk-space error and succeeded on retry. No source file was removed or replaced. An initial Git ignore audit sent text paths through Windows newline conversion, causing Git to retain a carriage return in each path. We repaired the check with binary NUL-separated input and output. One figure crop extended into the following symbol panel. We made no sign identification or legend reading there; the local notes record the exposure. A later 300 dpi crop restricted to the relevant figure and caption is named `primary-p0252-figure514-limited.png`.

We drew ten rows with `random.Random('a2-check').sample` over the ordered 152-row catalogue. We reread their page images, entered separate observations and then froze and compared the first-pass JSONL with `verify_records.py --root . --freeze-reread`. That flag ran once. Bhita entry 80 required a correction to `legend_as_printed`. Other literal differences concerned capitalization, location shorthand, punctuation and figure-locator spacing. We retained the fuller first-pass metadata after adjudication. The local scratch directory preserves both first-pass files, the selection, observations, comparison and resolutions. `reread-summary.json` reports identifiers and field names. This same-transcriber check covered selected fields; it does not provide independent contributor verification.

## Rights and remaining decisions

All ten acquisition records have the prescribed `rights-unverified` status and exact rights note. Mahadevan readings, translations, table text, descriptions and detailed notes remain local. The leak audit uses local patterns from those fields and six-word sequences. `leak-check.json` reports the pattern count, checked file count and matches. The final audit includes all A2-created tracked files and acquisition records. The prose review flags supplied prompt files, which remain unchanged; flags in our generated inventory were repaired.

The local source notes contain the complete decision list. Bhita requires review of conflicts between the catalogue and index, grouped impressions, missing locations, general language assignments, uncertain readings and depth units. The affected entry identifiers are 17, 24, 25, 33, 36, 41, 45, 58, 68, 73, 80, 84, 86, 90, 110, 115 and 120, with additional grouped impressions identified in the JSONL. Mahadevan review locators are Table 1.6 rows 1, 9–10 and 13; Table 1.7 rows 1–2, 4–5; and Table 1.8 rows 2–4 and 7–14. We have retained unresolved fields for review. Before corpus inclusion, we must set the rule for rows without individual excavation contexts, script stages or identifiable individual objects. Detailed source-derived reasons remain in the local notes.

The repository already had changes from other sessions, and its status continued to change during this run. `status-check.json` reports that the complete repository status is not exclusive to A2. We made no Git mutations. Local start and end snapshots retain the read-only status, and `created-paths.json` lists every file we created within the assigned paths. `run-timing.json` gives the measured plan-to-final duration; orientation began several minutes before the plan.

The acquisition closes the requested catalogue coverage: 120 Bhita rows and all 32 rows in the three Mahadevan tables are available locally with scan locators. An independent page-image review of the flagged entries is the next check before any corpus inclusion or language-direction test.
