# Codex run 1A: acquire, hash and sweep the printed sources for post-catalogue Indus finds

You are working in the repository at the current directory, an Indus-script research knowledge base. Read `AGENTS.md`, then `experiments/2026-10-21-post-catalogue-finds/PROTOCOL.md` (the protocol for this package; do not edit it), `knowledge/provenance/REDISTRIBUTION.md` (section "Asset record to keep") and `tools/fetch_data.py`. Your job is mechanical: fetch and hash the sources listed below, extract per-page text, and mark the pages that later readers must look at. You do not extract objects, you do not judge which finds are post-catalogue, and you do not write prose for the knowledge base.

Writing requirement for any prose you do write (comments, notes, the final message): maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.

## Owned paths and invariants

You may create and edit files only in:

- `experiments/2026-10-21-post-catalogue-finds/acquisition/` (your scripts and tracked records)
- `data/raw/2026-10-21-post-catalogue-finds/run1a/` (downloads, page text, local working files)

Everything else in the repository is read-only for you. In particular, do not edit `data/MANIFEST.json`, `knowledge/`, `tools/`, other experiment directories, or `data/raw/2026-10-20-fresh-test-collection/` (another agent's active work; do not read from it either). Make no git commit, branch, stash or reset. Do not install packages. A parallel Codex run (1B) owns `experiments/2026-10-21-post-catalogue-finds/acquisition-web/` and `data/raw/2026-10-21-post-catalogue-finds/run1b/`; leave them alone.

Downloaded files are untrusted data. Keep every script in `experiments/2026-10-21-post-catalogue-finds/acquisition/`, never inside `data/raw/`; pass file paths as arguments; run any Python that reads downloaded or held files with `python -I`; never execute, import or unpack anything you download.

**The inscriptions stay unread.** These objects are reserved for frozen predictions. No tracked file you write may contain text copied from a source beyond bibliographic fields (title, authors, editor, year, volume, publisher, page numbers), and no tracked or local file, log or final message you write may transcribe a sign, count signs, give a text length or writing direction, name a motif, animal or scene on an object, or give an object's dimensions or weight. Keyword hit counts are allowed; snippets of source text are allowed only in local files under `data/raw/2026-10-21-post-catalogue-finds/run1a/`. Do not open page images unless a step below says so.

## Tools available

Python 3.13 (standard library, PyMuPDF as `fitz`, `pypdf`), poppler (`pdftotext`, `pdfinfo`, `pdfimages`), Tesseract OCR at `C:\Program Files\Tesseract-OCR\tesseract.exe`, and network access. Use `https://archive.org/metadata/<identifier>` for item metadata and file lists (each file has `size`, `md5`, `sha1`, `source`), and `https://archive.org/download/<identifier>/<file name, URL-encoded>` for downloads. Send the User-Agent string that `tools/fetch_data.py` uses.

## Step 1. Proposed manifest entries, then fetch with fetch_data

For every source in the tables below that is not held, write a proposed manifest entry in the shape of `data/MANIFEST.json` `sources[]` items: `id`, `title` (archive title until you confirm the title page), `kind` (`excavation-report`, `annual-review`, `journal-issue`, `journal-issue-ocr`), `fetch` with `method: "http"`, `url`, `filename`, `bytes`, and for Internet Archive files `archive_md5` and `archive_sha1` from the item metadata; `identifiers` (the archive identifier), `rights` with `status: "rights-unverified"` and the observed licence field of the item (`licenseurl` if any), `status: "not-held"` before download, `questions: ["Q-1026"]`. Save them as `acquisition/manifest-proposals-1a.json`.

Then acquire each file by calling the `fetch_http(src, dest, dry_run)` function of `tools/fetch_data.py` on the proposed entry. Load that module from its file path with `importlib.util.spec_from_file_location` (do not modify `sys.path` and do not modify the tool). Use a new destination directory per file, `data/raw/2026-10-21-post-catalogue-finds/run1a/sources/<source id>/`; `fetch_http` refuses an existing directory, which is intended. After each download, compute MD5 and SHA1 and compare them with the archive's values; record SHA256 (from the `acquisition.json` that `fetch_http` writes) into the proposed entry, set `status: "held"`, `location: "local-only"`, `local_paths`, and `hashes`. A mismatch or failure keeps the file and is recorded, not retried more than twice. Write a wrapper script `acquisition/fetch_proposed.py` that does this from the proposals file, so the acquisition is reproducible.

### 1a. Excavation reports on the Internet Archive (fetch the PDF and the `_djvu.txt`)

| Source id | Identifier | File to fetch |
|---|---|---|
| `farmana-2006-08` | `excavationsatfarmana200608vshindeetal_212_v` | `Excavations at Farmana, 2006-08 - V Shinde et al.pdf` |
| `farmana-2007-08-report` | `farmanaexcavationreport200708vasantshindeetal_254_F` | `Farmana Excavation Report 2007-08 - Vasant Shinde et al.pdf` |
| `farmana-necropolis` | `harappannecropolisatfarmanainghaggarbasinvshindeetal_464_U` | `_djvu.txt` only; fetch the PDF only if the sweep marks candidate pages |
| `rakhigarhi-nath` | `excavationsatrakhigarhi19972000amarendranath_457_Z` | `Excavations at Rakhigarhi, 1997-2000 - Amarendra Nath.pdf` |
| `surkotada-1990` | `masi87excavationsatsurkotadaandkutchjagatpatijoshi_841_t` | the `original` PDF |
| `kanmer-ch6` | `excavationsatkanmer200509ch6auesugismeena_648_B` | `Excavations at Kanmer, 2005-09, ch 6 - A Uesugi & S Meena.pdf` |
| `tarkhanewala-2009` | `excavationsattar00triv` | `excavationsattar00triv.pdf` |

### 1b. *Indian Archaeology – A Review* (IAR)

Held copies, used in place (verify by SHA256, do not copy):

| Source id | Local path |
|---|---|
| `iar-1987-88` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/IAR1987-1988-ALT.pdf` |
| `iar-1988-89` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/IAR1988-1989-ALT.pdf` |
| `iar-1989-90` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/IAR1989-1990-ALT.pdf` |
| `iar-1990-91` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/IAR1990-1991-ALT.pdf` |
| `iar-1991-92` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/IAR1991-92.pdf` |
| `iar-1999-00` | `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/iar1999.pdf` |
| `iar-2007-08` | `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/iar2007_alt.pdf` |
| `iar-2009-10` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/IAR2009-10.pdf` |
| `iar-2013-14` | `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/iar2013_alt.pdf` |

To fetch from the ASI Aurangabad Circle mirror, `https://www.asiaurangabadcircle.com/assets/files/publications/<YYYY>-<YYYY+1>.pdf`: 1992-93, 1993-94, 1994-95, 1995-96, 1996-97, 1997-98, 1998-99, 2000-01, 2006-07, 2010-11, 2012-13 (source ids `iar-1992-93` and so on). A HEAD request on 21 October gave the same byte count for the 1996-1997 and 1997-1998 files; if their SHA256 values are equal, record the 1997-98 mirror file as a duplicate of 1996-97 and fetch 1997-98 from the Internet Archive item `indianarchaeology199798areview_830_j` instead. Confirm the volume year of every IAR file from its title or contents page and record it; a file whose contents belong to another year is recorded as such.

For 2003-04 the only copy found is the Internet Archive item `tdl.49427-indian-archaeology-2003-2004-a-review`; fetch its `_djvu.txt` and its per-page OCR file (`_djvu.xml`, or `_hocr.html` if no XML exists), not its PDF. Run 1B searches for the volumes not found (2001-02, 2002-03, 2004-05, 2005-06, 2008-09, 2011-12, 2014-15 onward); do not search for them.

### 1c. Journal issues on the Internet Archive (text sweep first)

*Puratattva* (Bulletin of the Indian Archaeological Society), issues 18 (1987–88) to 37 (2007), and any later issue you find on the Internet Archive. Several copies exist per issue; take one per issue, preferring an item whose `_djvu.txt` exists, and record the alternates. Known identifiers: 18 `dli.ministry.29975`; 19 `dli.ministry.29976`; 20 `dli.ministry.29977`; 21 `dli.ministry.29978`; 22 `dli.ministry.29979`; 23 `dli.ministry.29980`; 24 `dli.ministry.29981`; 25 `dli.ministry.29982`; 26 `dli.ministry.29983`; 27 `dli.ministry.29984`; 28 `in.gov.ignca.84853` or `puratattvano28indianarchaeologicalsocietybhu_511_M`; 29 `dli.ministry.29986`; 30 `dli.ministry.29987`; 31 `dli.ministry.29988`; 32 `dli.ministry.29989`; 33 `dli.ministry.29990`; 34 `in.gov.ignca.87942` or `puratattvano34indianarchaeologicalsocietybhu_20_W`; 35 `dli.ministry.29994`; 36 `dli.ministry.29992`; 37 `dli.ministry.29993`. Check the issue number and year of each from its metadata or text.

*Man and Environment* (Indian Society for Prehistoric and Quaternary Studies), every volume from 1987 onward on the Internet Archive. Known identifiers: `dli.calcutta.06850` (vols 10–11), `06851` (13–14), `06852` (16), `06855` (24), `06856` (26), `06857` (27), `06858` (28), `06859` (31), `06860` (32), `06861` (33), `06862` (35), `06863` (36); check `dli.calcutta.06853`, `06854` and neighbouring numbers for the missing volumes.

For each issue fetch only the `_djvu.txt` first (source ids `puratattva-<n>`, `man-environment-<vol>`). After the sweep (step 3), fetch the per-page OCR file (`_djvu.xml` or `_hocr.html`) for each issue that has candidate pages, so that later readers can cite PDF leaf numbers. Do not fetch journal PDFs.

### 1d. Held reports used in place (verify SHA256; do not copy)

| Source id | Local path |
|---|---|
| `bisht-2015-held` | `data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf` (manifest id `bisht-2015`, SHA256 `f1c23210…`) |
| `nuhato-2018-held` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/NUHATO2018.pdf` |
| `shikarpur-2009-held` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/SHIKARPUR2009.pdf` |
| `kanmer-ch8-held` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/KANMER2012CH8.html` |
| `khirsara-2017-held` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/KHIRSARA2017.html` |
| `nagwada-2018-held` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/NAGWADA2018.pdf` |
| `binjor2017-held` | `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/binjor2017.pdf` |
| `puratattva-35-held` | `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/puratattva35_retry.pdf` |
| `puratattva-36-held` | `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/puratattva36_retry.pdf` |
| `rakhigarhi-inventory-held` | `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/rakhigarhi_inventory.pdf` |
| `chanhu-surface2017-held` | `data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/major-revision/chanhu-surface2017.pdf` |
| `juna-khatiya-2021-held` | `data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/JUNAKHATIYA2021.pdf` |

Also list, without sweeping them, the Kanmer witnesses named in `experiments/2026-10-02-six-hour/kanmer-physical-use/SOURCES.md` and `source-register.json` in that directory: record their local paths and SHA256 values as `kanmer-frame-<n>` so later runs can read them.

## Step 2. Per-page text

For every PDF, write one UTF-8 text file per page under `data/raw/2026-10-21-post-catalogue-finds/run1a/text/<source id>/p<NNNN>.txt` using the PDF text layer (`pdftotext -layout -f N -l N` or PyMuPDF). A page with fewer than 15 words is image-only; when more than a fifth of a source's pages are image-only, OCR those pages with Tesseract (English, 300 dpi rendering) unless an Internet Archive per-page OCR file exists, in which case split that file into pages instead. For journal issues, split the per-page OCR file into pages once fetched; until then the sweep reads the `_djvu.txt` whole. For HTML sources, strip tags into one text file. Record per source the page count, the text basis (`pdf-text-layer`, `archive-page-ocr`, `tesseract`, `djvu-txt-unpaged`, `html`), the number of image-only pages and, where you can detect it, the printed page number of each PDF page (from running heads or footers; record `printed_page_map.json` locally and its success rate in the register).

## Step 3. Keyword sweep

Read `experiments/2026-10-21-post-catalogue-finds/selection/sites-seed.csv`. For every page of every source, record a candidate page when the page names a seed site or alias (case-insensitive, tolerant of OCR hyphenation and spacing; also count "Harappan" with any of the keywords as a generic hit) and contains at least one inscription keyword: `seal`, `sealing`, `tablet`, `inscri` (inscribed, inscription), `script`, `sign`, `character`, `letter`, `legend`, `graffit`, `tag`, `impression`. Also mark the page before and after each candidate page as context pages. Additionally, flag every page anywhere in the IAR volumes that contains `Harappan` and (`seal` or `inscri` or `script`) even when no seed site is named, with the excavation heading under which it falls (IAR entries are headed by site and district); these pages reveal sites missing from the seed list. Write:

- `acquisition/candidate-pages-1a.csv` (tracked): `source_id, pdf_page, printed_page, site_code, generic_harappan_hit, n_site_terms, n_keywords, keyword_classes, context_only`. No source text.
- `acquisition/new-site-leads-1a.csv` (tracked): site names found under IAR headings with Harappan inscription keywords that are not in the seed list, with `source_id, pdf_page, printed_page, heading_as_printed`. The heading is a site and district name, which is allowed.
- `data/raw/2026-10-21-post-catalogue-finds/run1a/snippets/<source id>.jsonl` (local): for each candidate page, the page text, for the extraction run.
- `acquisition/sweep-summary-1a.json` (tracked): per source and per site, the number of candidate pages; per site, the total.

## Step 4. Source register and exposure log

Write `acquisition/source-register-1a.csv` (tracked) with one row per source: `source_id, title, authors_or_editors, year_or_volume, kind, route` (`archive.org`, `asi-mirror`, `held`), `identifier, url, local_path, file_name, bytes, sha256, archive_md5, archive_sha1, md5_match, sha1_match, pdf_pages, text_basis, image_only_pages, printed_page_detected_share, rights_notice_observed, status` (`acquired`, `held-verified`, `failed`, `duplicate`, `wrong-volume`), `notes`. Take the title, authors and year from the source's own title page where the text shows it, and say in `notes` when they come only from archive metadata.

Write `acquisition/exposure-log-1a.csv` (tracked): `source_id, agent, access, pages, purpose`. For this run the agent is `codex gpt-6.1-sol run 1A`; the access for each source is `text layer read by script` (and `page image viewed` with the page list if you opened any image).

Keep `acquisition/acquisition-log-1a.jsonl` (tracked) with one line per network request outcome (url, time UTC, status, bytes); do not include response bodies.

## Step 5. Verification

Write `acquisition/selftest-1a.py` and run it; save its output as `acquisition/selftest-1a.json`. It must check that every acquired file's SHA256 equals its recorded value and its MD5 and SHA1 equal the archive's; every held file's SHA256 equals the value in `data/MANIFEST.json` where the manifest records one; every source in the register has a text directory with as many page files as PDF pages (or a recorded reason); every candidate-page row points to an existing page file; and no tracked file in `acquisition/` contains a run of more than 12 consecutive words copied from any page file (sample at least 200 random 12-word windows per source and search the tracked files for them). Report the counts.

## Final message

End with a plain message (it is saved to `final.md`) giving: the number of sources acquired, held and verified, failed and duplicated, with the failed ones named; total bytes downloaded; the text basis counts; the number of candidate pages per site code (a compact table); the number of new site leads; the selftest results; any deviation from these instructions and why; and the paths of the tracked outputs. Do not include any source text, object description or inscription content.
