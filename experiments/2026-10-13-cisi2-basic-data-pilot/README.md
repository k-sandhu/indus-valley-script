# CISI 2 basic-data pilot: Mohenjo-daro M-621 to M-947

13 October 2026. Question card Q-1006, with the method written for Q-1005. Independently verified the same day; the corrections that followed are listed in [REVIEW-CHANGES.md](REVIEW-CHANGES.md). Protocol [PROTOCOL.md](PROTOCOL.md) and [Amendment 1](AMENDMENT-1.md), both hashed in [PROTOCOL.sha256](PROTOCOL.sha256). The transcribed values are local only, in `data/raw/2026-10-13-cisi2-basic-data-pilot/`, pending a rights decision on CISI; this directory holds the schema, the procedure, the accuracy and coverage counts and per-object flags.

## Result

The basic-data section of CISI 2 (Shah and Parpola 1991, *Corpus of Indus Seals and Inscriptions. 2. Collections in Pakistan*) occupies printed pp. 434–447 (PDF 469–482) and prints five columns: the CISI number, the FC number of the Helsinki concordance, the excavation number, the holding museum with its registration numbers, and the sources of the photographs. It prints no findspot, depth, material or dimensions, although the manifest and the question cards expected them. The same five columns appear in CISI 1 (printed p. 366, PDF 402).

The pilot transcribed all 327 entries from M-621 to M-947, the whole of printed pp. 435 (after M-595) and 436. Every entry was read twice by independent readers working from the page renders alone, and every disagreement was adjudicated against the page. The two readings agree on 90.5% of the 1,635 cells (column 1 100%, FC number 92.7%, excavation number 91.4%, museum number 85.6%, photographs 82.6%). Of the 156 disagreements, 48 were decided from the page and 108 could not be. The final table brackets 119 cells (7.3%) in 101 rows: 112 that the blind comparisons left undecided, 6 that a cross-check against the Lipi metadata reopened, and 1 that both readers bracketed alike. The blur of the scan, not the reading, sets this limit: the digit pairs 3/5, 6/8, 0/9 and 1/7 in the italic accession numbers cannot be separated at its resolution.

Joined to the local corpus, the block adds a museum number to 202 objects that had none, 179 of them without an uncertain digit, and raises museum coverage for the 283 joined objects from 26.1% to 97.5% and for the whole corpus from 274 objects (5.8%) to 476 (10.1%). The block supplies a holding institution for all 283 joined objects, adding that field to 209 of them, and an FC number to all 283, which the local corpus lacks. The excavation numbers add nothing new, since Lipi already has one for the 278 objects whose CISI 2 entry prints one, but they explain Lipi's `excavation-idno` field: for 182 objects with four-digit FC numbers it is the printed excavation number followed by the FC number without its first digit, while the 32 objects with FC numbers below 1000 and 7 UPM/MD finds of a later excavation series carry the printed number unchanged. Six objects carry a Lipi number that differs in substance from the page: two pairs whose excavation records are crossed between Lipi and CISI 2, and two whose printed number the page confirms. Measuring the four crossed seals on the CISI 2 plates afterwards showed that CISI 2's basic data, not Lipi, has the two pairs crossed ([swap check](../2026-10-13-data-round-1-verification/swap-check.md)).

## Columns as printed

The key on printed p. 434 defines the columns. The full schema with the abbreviations is [schema.json](schema.json).

| Column | Content as printed | Parsed fields |
|---|---|---|
| 1 | CISI number; piece numbers (1), (2) on separate lines when the pieces of a broken object have different museum or excavation numbers | `cisi`, `pieces` |
| 2 | Four-digit FC number, the object's number in the Finnish concordance (Koskenniemi and Parpola 1979–1982); for Mohenjo-daro and Harappa the FC numbers are keyed to object numbers in the excavation reports' plates | `fc_number` |
| 3 | Excavation number or corresponding data: an area code and number (DK, DK-A to DK-H, DK-i, HR, VS, SD, DM, MN, UPM/MD, RWTH and others); `???` where data are not available or the object carries a wrong number; a surface-find mark and layers in parentheses where given; bold for an indistinct number | `excavation` (printed, status, area code, surface find, layer) |
| 4 | Holding museum and registration numbers: MD and MM (Moenjo-daro Museum, old and new accession numbers), NMP (National Museum of Pakistan, Karachi), L (Lahore Museum), HM (Harappa Museum), EXB (Excavation Branch, Karachi), KHP (Khairpur University) and others; italic numbers beginning with a two-digit year (50 for 1950) are National Museum of Pakistan accession numbers; a bracketed holding followed by "now" records a transfer | `museum_holdings` (code, number, NMP accession, former, current), `holding_institutions` |
| 5 | Photograph sources: JL, AV, EL (CISI project photographers), P (Department of Archaeology and Museums, Pakistan), Si. and Pu. (Sind and Punjab series of the ASI photo archive), Aachen, FEM (Mackay 1938) and others, with side letters (A object, a impression, bis second photograph) | `photo_sources` |

Findspot, depth, material and dimensions take the value `not-printed`, so that tables from CISI 1 and CISI 2 merge under one schema. Material and form are coded instead by symbols in the plate captions (Table 2, printed p. 433), and dimensions can be measured on the plates, which print inscribed sides at 2:1; neither was attempted here.

The scan's page order holds for the catalogue: printed page = PDF page − 35 at both ends of printed pp. 1–447, and 418 of the 447 pages show the expected number in the corner header of the scan's text layer (independent count, [verification](../2026-10-13-data-round-1-verification/REPORT.md)); the other 29 headers are unreadable and those pages were not inspected, so a missing page offset by a repeated one is not yet excluded. The basic data runs to about 160 entries a page, in two half-columns.

## Accuracy

### Sampled check (protocol endpoint)

After the first pass was frozen by hash, a random sample of 33 entries (10% of 327, seed 20261013; [sample.json](sample.json)) was read again by a separate Claude instance that saw only the page renders. The comparison is cell by cell after normalizing whitespace ([accuracy.json](accuracy.json)).

| Column | Cells | Agreement | Disagreements | First-pass errors | Undecidable | First-pass error rate |
|---|---:|---:|---:|---:|---:|---|
| CISI number | 33 | 100% | 0 | 0 | 0 | 0% |
| FC number | 33 | 84.8% | 5 | 2 | 2 | 6.1% (up to 12.1%) |
| Excavation number | 33 | 90.9% | 3 | 1 | 0 | 3.0% (95% interval 0.5–15.3%) |
| Museum number | 33 | 72.7% | 9 | 0 | 1 | 0% (up to 3.0%) |
| Photographs | 33 | 84.8% | 5 | 0 | 1 | 0% (up to 3.0%) |
| All | 165 | 86.7% | 22 | 3 | 4 | 1.8% (up to 4.2%) |

A first-pass error is a cell where the adjudicated reading is not among the first pass's candidates. The upper figure also counts the undecidable cells in which the first pass gave a definite reading the page cannot confirm. Most museum-column disagreements are one reader bracketing an italic digit that the other read definitely. The excavation error rate of 3.0% exceeds the 2% that Q-1005 sets for museum and excavation numbers, so the protocol's rule applies: every row is read twice.

### Full second reading (Amendment 1)

Before the sampled results were known, a second Claude instance read all 327 entries under the same isolation rules ([accuracy-full.json](accuracy-full.json)).

| Column | Cells | Agreement | Disagreements | Decided for first pass | Decided for second pass | Undecidable | First-pass error rate |
|---|---:|---:|---:|---:|---:|---:|---|
| CISI number | 327 | 100% | 0 | 0 | 0 | 0 | 0% |
| FC number | 327 | 92.7% | 24 | 2 | 7 | 15 | 0.6% (up to 4.9%) |
| Excavation number | 327 | 91.4% | 28 | 3 | 3 | 22 | 0.6% (up to 7.0%) |
| Museum number | 327 | 85.6% | 47 | 7 | 5 | 35 | 0% (up to 9.5%) |
| Photographs | 327 | 82.6% | 57 | 10 | 11 | 36 | 0% (up to 9.5%) |
| All | 1,635 | 90.5% | 156 | 22 | 26 | 108 | 0.2% (up to 6.2%) |

The second reader made 5 errors that adjudication decided (2 excavation, 3 photograph cells), the first reader 4. On the 33 sampled rows the full reading acts as a third reading: it agrees with the sampled second reading on 145 of 165 cells and confirms each of the three first-pass errors found in the sample. With two readers, a cell that one of them reads wrongly is caught by disagreement; the residual risk is a misreading both share. The Lipi cross-check gives an estimate of that: among the 299 excavation cells on which both blind readers agreed, 5 (1.7%) turned out, on re-reading, to be equally compatible with Lipi's different digit and were bracketed.

### Lipi cross-check

The first pass was also compared with the Lipi `excavation-idno` field and the older website export's `MUSEUM` values, and the 50 cells that disagreed after allowing for Lipi's appended FC digits were re-read against the page (local `recheck/recheck.json`). This re-reading was not blind, so it could only confirm, correct or bracket a cell and is not part of the error rates. It confirmed 4 printed readings that differ from Lipi, found 9 Lipi defects, corrected 7 first-pass cells (6 FC numbers, 1 museum number) and bracketed 30.

## Coverage for the pilot objects

All 327 catalogue numbers in the block have a row; none is missing from the pages. 283 join one Lipi family each by the printed CISI number, and 44 have no Lipi family (listed in [object-flags.csv](object-flags.csv) with `join = no-lipi-family`). Each joined family has a single face, so the side plays no part in the join. Before means the Lipi export and the older website export under the data inventory's usable-value rules; after adds a usable CISI 2 value ([coverage.json](coverage.json)).

| Field | Before | After | CISI 2 supplies |
|---|---:|---:|---:|
| Museum number | 74 (26.1%) | 276 (97.5%) | 275, of which 241 without an uncertain digit |
| Holding institution | 74 (26.1%) | 283 (100%) | 283 |
| FC number | 0 | 283 (100%) | 283 |
| Excavation number | 278 (98.2%) | 278 (98.2%) | 278, of which 252 without an uncertain digit |
| Findspot (area, block or room) | 269 (95.1%) | 269 | not printed |
| Depth | 231 (81.6%) | 231 | not printed |
| Material | 235 (83.0%) | 235 | not printed |
| Any dimension | 271 (95.8%) | 271 | not printed |
| All three dimensions | 126 (44.5%) | 126 | not printed |

The new holdings of the joined objects are the Moenjo-daro Museum (227 objects with old accession numbers, 39 with new ones, often both), the Lahore Museum (21), the National Museum of Pakistan (17), the Excavation Branch in Karachi (11), the Harappa Museum (4) and Khairpur University (3). 75 joined objects carry a National Museum of Pakistan accession number, either as their current registration or as the number under which they were held before transfer to another museum. Across the corpus, objects with a museum number rise from 274 to 476 of 4,695.

### Disagreements with the local metadata

The excavation number is the only field that both sources record; the museum number can be checked against the older website export.

| Excavation comparison, 278 objects with both values | Objects |
|---|---:|
| Equal after removing spaces and hyphens | 40 |
| Lipi = printed number followed by the FC number without its first digit | 182 |
| Area code differs: Lipi adds a DK subarea letter (DK-B, DK-C) that CISI 2 does not print | 9 |
| Area code differs: Lipi drops the DK- prefix | 3 |
| Values crossed between two entries (two pairs); plate measurements put the error in CISI 2 | 4 |
| Number differs; the page confirms the CISI 2 reading | 2 |
| Lipi drops a letter suffix of the printed number | 1 |
| Lipi string incomplete (FC digits only) | 1 |
| Lipi appends a plate reference in place of the FC digits | 1 |
| Not comparable: CISI 2 excavation or FC cell uncertain | 35 |

Of the 73 objects that have a museum number in both sources, 71 agree and 2 are not comparable because the CISI 2 cell is uncertain; none disagrees. CISI 2 prints no findspot, depth, material or dimensions, so the pilot neither confirms nor contradicts those Lipi fields. Per-object categories are in [object-flags.csv](object-flags.csv) (`excavation_comparison`, `museum_comparison`); the values behind them are in the local `join-detail.jsonl`.

## Effort and projection

The times below are an AI agent's wall-clock times; a human reader's time was not measured. The first reading of 327 entries took 6.9 minutes (01:41:50 to 01:48:43), the full second reading 13.7 minutes (02:01:01 to 02:14:42), adjudication of 156 disagreements 5.7 minutes (02:16:23 to 02:22:04), and the Lipi cross-check of 50 cells about 5 minutes (not logged); the sampled second reading of 33 entries took 13 minutes, mostly spent testing digit templates. Double reading with adjudication and cross-check therefore costs about 31 minutes per 327 entries, 5.7 seconds an entry, plus a few minutes per page to render and cut strips.

| Section | Entries | Status | Projected agent time | Projected uncertain cells after double reading |
|---|---:|---|---|---|
| CISI 2 basic data, printed pp. 435–447 | 2,087 (census count) | 327 done, 1,760 remaining | about 2.8 hours for the rest, about 8 minutes per half-column block | about 150 excavation and 195 museum cells among the remaining entries (8.6% and 11.0%) |
| CISI 1 basic data, printed pp. 366–375 | 1,533 (census count) | not started | about 2.4 hours at the CISI 2 rate | unknown until a pilot block is double-read; CISI 1's embedded page images are about 815 × 1,147 px against CISI 2's 3,252 × 4,542 px foreground layer, but its type looked sharper at zoom 2 |

A single reading would leave definite values in about 6% of cells that the page cannot confirm (the upper error figure above), which is why the procedure requires two blind readings. Bracketed cells are the residue that only a better scan or the printed volume can resolve.

## Continuing the work

[PROCEDURE.md](PROCEDURE.md) divides the rest of CISI 2 into 22 half-column blocks of about 80 entries and CISI 1 into about 20, gives the file names for each block, the double-reading rule and the merge step ([merge.py](merge.py)), which refuses duplicate CISI numbers and lists every number in the given ranges that has no row.

## Method

Pages were rendered at zoom 8.34, the pixel size of the scan's 3,252 × 4,542 px foreground layer, with [render.py](render.py), and read in 1:1 strips of about fourteen lines; enlarging and sharpening added no detail. The first pass was typed into a pass file per page, parsed with [parse.py](parse.py), frozen and hashed, and sampled with [sample.py](sample.py). Each second reader was a separate Claude instance given only copies of the three page renders, the column descriptions and the bracket convention, and told not to open any other file in the package's local directory, Lipi, the website export or the PDF's text layer. [score.py](score.py) compares passes and scores the adjudications; [build_final.py](build_final.py) applies the sample adjudication, then the full-reading adjudication, then the Lipi cross-check (only for cells no blind adjudication decided) to the frozen first pass; [join.py](join.py) joins the final table to the Lipi families with the data inventory's usable-value rules imported from its `coverage.py`.

Commands, from the repository root:

```text
python experiments/2026-10-13-cisi2-basic-data-pilot/render.py page 470
python experiments/2026-10-13-cisi2-basic-data-pilot/parse.py data/raw/2026-10-13-cisi2-basic-data-pilot/pass1.jsonl data/raw/2026-10-13-cisi2-basic-data-pilot/pass1-p435.txt data/raw/2026-10-13-cisi2-basic-data-pilot/pass1-p436.txt
python experiments/2026-10-13-cisi2-basic-data-pilot/sample.py
python experiments/2026-10-13-cisi2-basic-data-pilot/score.py disagreements [--full]
python experiments/2026-10-13-cisi2-basic-data-pilot/score.py score [--full]
python experiments/2026-10-13-cisi2-basic-data-pilot/build_final.py
python -I experiments/2026-10-13-cisi2-basic-data-pilot/join.py data/raw/2026-10-13-cisi2-basic-data-pilot/final.jsonl
```

The readings and adjudications themselves (`pass1-*.txt`, `pass2/pass2.txt`, `pass2b/pass2b.txt`, `adjudication*.json`, `recheck/recheck.json`) are local and cannot be regenerated by script.

## Sources and licences

| Source | File | Licence or status |
|---|---|---|
| Shah and Parpola 1991, CISI 2 | `data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf`, SHA256 `5258071b08898ce4bb9e9a5ee675d182fbe4c1eb22ed2822f6838fdbd5f7e54b` (archive.org; manifest entry `cisi-2`) | Copyright 1991 Finnish Academy of Science and Letters; reuse unverified ([REDISTRIBUTION.md](../../knowledge/provenance/REDISTRIBUTION.md)); renders and values local |
| Joshi and Parpola 1987, CISI 1 | `research/literature/sources/joshi_parpola_1987_cisi1.pdf` (manifest `cisi-1`), printed p. 366 viewed for the column layout | Copyright 1987; reuse unverified; local |
| Lipi export, normalized | `data/normalized/lipi_observed_faces.jsonl`, SHA256 `1220f559…`, matching the data inventory | No licence at the pinned commit; local |
| Older website export, normalized | `data/normalized/indus_website_observed.jsonl` | GPL-3.0 repository, data coverage unresolved; local |

Tracked files in this package are the project's own work (CC0 for prose and data, Unlicense for code, per [LICENSE](../../LICENSE)). They hold column descriptions, counts, CISI numbers and Lipi family ids with field flags, but no transcribed value. Four places that did quote CISI values, among them two code examples in the protocol, were rewritten after the independent verification ([REVIEW-CHANGES.md](REVIEW-CHANGES.md)).

## Limits

The readings are AI readings of a blurred scan of a printed table; nobody consulted the printed volume. The two second readers and the first reader are instances of the same model, so their errors may be correlated in ways that two people's would not; the Lipi cross-check suggests that about 1.7% of the agreed excavation cells are still open. The first reader had seen the scan's text layer for p. 436 and the Lipi metadata of about 28 objects in the range before transcription began, although no value was taken from them. Coverage gains count a museum number with one bracketed digit as usable; the counts without bracketed digits are given beside them. The FC numbers have not yet been linked to the Helsinki 1979 text numbers, which would make them useful for the identifier crosswalk (Q-1013).

## Files

[PROTOCOL.md](PROTOCOL.md), [AMENDMENT-1.md](AMENDMENT-1.md), [PROTOCOL.sha256](PROTOCOL.sha256), [PROTOCOL-public.sha256](PROTOCOL-public.sha256), [REVIEW-CHANGES.md](REVIEW-CHANGES.md), [schema.json](schema.json), [PROCEDURE.md](PROCEDURE.md), [render.py](render.py), [tiles.py](tiles.py), [parse.py](parse.py), [sample.py](sample.py), [score.py](score.py), [build_final.py](build_final.py), [join.py](join.py), [merge.py](merge.py), [renders.json](renders.json), [sample.json](sample.json), [accuracy.json](accuracy.json), [accuracy-full.json](accuracy-full.json), [coverage.json](coverage.json), [object-flags.csv](object-flags.csv), [DATA-UPDATE.md](DATA-UPDATE.md), [manifest-additions.json](manifest-additions.json), [question-updates.md](question-updates.md), [registry-entry.json](registry-entry.json), [RETROSPECTIVE.md](RETROSPECTIVE.md).
