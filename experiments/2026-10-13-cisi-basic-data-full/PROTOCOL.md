# Protocol: the complete CISI 1 and CISI 2 basic data

Written 13 October 2026, before any entry outside the pilot block was transcribed. Question cards Q-1005 (CISI 1) and Q-1006 (CISI 2). This package continues the [CISI 2 pilot](../2026-10-13-cisi2-basic-data-pilot/README.md) under its [procedure](../2026-10-13-cisi2-basic-data-pilot/PROCEDURE.md), with the changes stated here. To set it up I rendered the pages, cut the strips, looked at one strip of CISI 2 p. 438 and two views of CISI 1 p. 366 to check legibility and layout, and ran the calibration described under Readers. No entry was recorded.

## Question

What does the basic-data table of each volume print for every catalogue entry outside the pilot block, read twice blind and adjudicated against the page, and what does the whole table add to the local object record? The two tables give each catalogue number its FC concordance number, excavation number, holding museum and registration numbers, and photograph sources. They print no findspot, depth, material or dimensions.

## Sources and blocks

CISI 2 (Shah and Parpola 1991) is the archive.org scan held as manifest entry `cisi-2` (SHA256 `5258071b…`), printed page = PDF page − 35, rendered at zoom 8.34. CISI 1 (Joshi and Parpola 1987) is the IGNCA scan held as `cisi-1`, PDF pages 1–431 only, printed page = PDF page − 36, rendered at zoom 4 from embedded page images of about 817 × 1131 px. A block is one half-column of one printed page: CISI 2 pp. 437–447 (22 blocks), CISI 1 pp. 366–375 (20 blocks), and the single entry M-595 at the head of CISI 2 p. 435, which the pilot left out. [make_strips.py](make_strips.py) renders the pages and cuts each block into windows of about fourteen lines with about two lines of overlap; [blocks.json](blocks.json) lists the blocks, render hashes and strip counts. The corrigenda that follow the last entries of each volume (CISI 2 p. 447, CISI 1 p. 375) are transcribed as their own text, line by line, by both readers of those blocks.

## Readers

Every block is read twice, by two separate Claude instances (Claude Opus 5.5 subagents) that each receive only [READER-BRIEF.md](READER-BRIEF.md), their block identifiers, the strip images and the output path. The second reader of a block never sees the first reading: pass 1 is written to `data/raw/2026-10-13-cisi-basic-data-full/pass1/` and pass 2 to `.../pass2/`, and each reader is told not to open the other directory, the local corpus, the older website export, the PDF text layer or the pilot's files. A reader may crop and enlarge its strips. Each reader records start and finish times in comment lines.

A second model was considered for the second reading, since two instances of one model can share misreadings. Codex CLI with GPT-6.1-Sol (reasoning effort high) read three calibration strips of the pilot block (CISI 2 p. 436, M-788 to M-817, 30 entries) under the same brief. Against the pilot's adjudicated readings it gave a confident wrong value in 7 of 30 FC cells, 12 excavation cells, 13 museum cells and 25 photograph cells, including systematic misreadings of two museum codes and of the accession-year form, where the pilot's two Claude readers gave none on the same rows. The comparison favours the Claude readers, because the adjudicated reference was built from their readings, but the size of the gap rules the second model out as a reader for this scan. Codex instead writes the pipeline code.

## Comparison and adjudication

The two passes of a block are compared cell by cell after normalizing whitespace (column 1 by its CISI number, so a row present in one pass only is itself a disagreement). Each disagreement goes to an adjudicator, a third Claude instance that sees both readings and crops of the page at the entry, and records one outcome: first-pass right, second-pass right, both wrong (with the adjudicated reading), or undecidable (the cell is bracketed with the candidates the page allows). Cells on which the two passes agree are final as read. The final block applies the adjudications to pass 1.

Reported per volume and per column: cells, agreement between the passes, adjudication outcomes, and the first- and second-pass error rates (an adjudicated error over cells; a bracket whose candidates include the adjudicated reading is not an error), with an upper figure counting undecidable cells in which a pass gave a definite reading. CISI 1 rates are reported separately from CISI 2 rates; CISI 1 has no earlier measurement.

## Cross-checks after adjudication

These checks are not blind. They may confirm a final cell, correct it after re-reading the page, or bracket it; they never fill a cell from another source, and they are reported apart from the error rates.

1. Lipi: the excavation number is compared with Lipi's `excavation-idno` after allowing for an appended FC tail and for area prefixes, and the museum number with the older website export's `MUSEUM`, as in the pilot.
2. FC rule: for Mohenjo-daro entries that join a row of the Mackay 1938 or Marshall 1931 seal tables, the FC number should be 2000 plus Mackay's catalogue number or 1000 plus Marshall's ([fc-crosswalk.json](../2026-10-13-data-round-1-verification/fc-crosswalk.json)). Every cell that breaks the rule is re-read against the page.

Each re-read cell is recorded as `confirmed`, `corrected`, `ambiguous` (bracketed) or `source-defect` (the page is clear and the other source differs).

## Predictions, frozen before any reading

1. The FC rule holds for at least 95% of the Mohenjo-daro entries outside M-621 to M-947 that join a Mackay or Marshall table row and whose final FC cell is unbracketed, and every exception is either a crossed record of the kind found at M-653/M-655 and M-656/M-707 or a cell the cross-check corrects. If fewer than 90% hold, the rule is wrong outside the pilot range.
2. Long shot: Harappa follows the same construction. For Harappa entries whose Lipi `excavation-idno` extends the printed excavation number, the appended digits are the FC number without its first digit in at least 80% of cases, which would make the Harappa FC numbers keyed to Vats's 1940 catalogue numbers as the CISI 2 key implies. Fewer than 50% kills it.
3. The double-read cell agreement for CISI 1 is at least as high as the pilot's 90.5% for CISI 2, because CISI 1's type is visibly sharper on the renders despite the lower native resolution.

## Merge, join and coverage

The final blocks of each volume are merged with a duplicate check and a list of every number in the volume's ranges that has no row; each listed number is looked for on the page and recorded as an absence or added. The merged tables (with the pilot block for CISI 2) are joined to Lipi families by CISI base number, as in the pilot, and coverage is measured with the data inventory's rules: museum number, holding institution, FC number and excavation number, before and after, by volume, object type and site, and combined with the museum joins of the same day.

## Rights and outputs

CISI 1 and CISI 2 are under copyright with reuse unverified, so renders, strips, readings, adjudications and the merged tables stay in `data/raw/2026-10-13-cisi-basic-data-full/`. Tracked files hold the brief, the scripts, the block list, counts, accuracy and coverage figures, and per-object field flags keyed by CISI number and Lipi family, with no transcribed value and no value in an example. Results go to `README.md`, with `RETROSPECTIVE.md`, `DATA-UPDATE.md`, `manifest-additions.json`, `question-updates.md` and `registry-entry.json`.
