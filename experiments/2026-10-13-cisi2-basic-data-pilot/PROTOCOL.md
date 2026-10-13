# Protocol: CISI 2 basic-data pilot, Mohenjo-daro M-621 onward

Written 13 October 2026 at 01:45 (UTC-4), before any data row was transcribed. To fix the column schema I had already read the column key on printed p. 434 (PDF 469) and one strip of printed p. 435 (PDF 470) covering M-595 to M-630, and I had counted Lipi families and older-export museum values for M-621 to M-947. No row was recorded before this file was written.

## Question

Can the basic-data section of CISI 2 (Shah and Parpola 1991, *Corpus of Indus Seals and Inscriptions. 2. Collections in Pakistan*) be transcribed from the held archive.org scan into one row per catalogue entry at a measured cell-level error rate, and what does a block of it add to the local object record? This is a pilot for question card Q-1006, and its procedure is meant to serve Q-1005 (CISI 1) as well.

## Source

`data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf`, 486 PDF pages, SHA256 `5258071b…` as recorded in the manifest (recomputed in `renders.json` provenance). The basic-data section is printed pp. 434–447 (PDF 469–482), "Basic data for the objects illustrated", as listed on the contents page (printed p. IV, PDF 7). Rights: copyright 1991 Finnish Academy of Science and Letters; reuse status unverified. All renders and every transcribed value stay in `data/raw/2026-10-13-cisi2-basic-data-pilot/`.

The key on p. 434 defines five printed columns: (1) the CISI number, with piece numbers (1), (2) inserted between columns 1 and 2 when the pieces of a broken object carry different museum or excavation numbers; (2) the object's number in the FC, the Finnish concordance of Koskenniemi and Parpola; (3) the excavation number or corresponding data, where a surface-find mark and numbers in parentheses (layers) can appear, `???` means not available, and bold face marks an indistinct or uncertain number; (4) the holding museum and registration numbers, where italic numbers that begin with a two-digit year refer to the accession catalogue of the National Museum of Pakistan; (5) the sources of the photographs.

## Pilot block

The block starts at M-621, the first entry after M-595 on printed p. 435, and runs through consecutive entries. The target is the whole of pp. 435 (from M-621) and 436, M-621 to M-947; the minimum is 200 consecutive entries (M-621 to M-820). Every catalogue number in the block gets a row; a number that the page skips is recorded as an absence with the page on which it would fall.

## Transcription rules

Pages are rendered at zoom 8.34 (the pixel size of the scan's 3252 × 4542 foreground layer) by `render.py` and read in strips of about fourteen lines at 1:1, with enlarged crops for doubtful cells. One record per catalogue entry. Each printed column is kept as printed in its own cell: continuation lines in the same column are joined with a single space, and when an entry is printed as several piece lines, the piece lines are joined with ` // ` in their printed order. Spelling, punctuation, spacing of codes (for example `DK-C nnnn`, `L, P-nnnn`) and abbreviations are kept.

A character that cannot be read with confidence is written in brackets: `[3/5]` for two candidates, `[?]` for an unreadable character, `[??]` for an unreadable stretch. The cell is then flagged uncertain. Bold or italic type is recorded only where it is visibly distinct; the blur of the scan means an unmarked cell is not evidence of roman type. Nothing is filled from another source.

Parsed fields are derived from the printed cells by `parse.py`, not typed by hand: holding institution and museum number pairs (prefix code and number) and any National Museum of Pakistan accession in year.number form from column 4; the excavation number, its leading area code, a surface-find flag and any parenthesized layer from column 3; the FC number from column 2; and the photograph source codes from column 5. Findspot, depth, material and dimensions have no column in this section; their parsed fields take the value `not-printed`, so that the schema stays aligned with Q-1005.

## Accuracy

After the first pass is complete its file is hashed and frozen. A random sample of max(25, ceil(10% of rows)) entries is drawn with Python's `random.Random(20261013)` from the frozen row list. A second reader, a separate Claude instance that is given the page renders, the column key, these transcription rules and the list of sampled CISI numbers, but no access to the first pass, transcribes the sampled entries. Agreement is computed cell by cell for the five printed columns after normalizing whitespace only. Every disagreement is adjudicated by me against an enlarged crop of the page, with one of four outcomes: first pass right, second pass right, both wrong (corrected value recorded), or not decidable from the scan. The error rate of the first pass by column is the number of adjudicated first-pass errors over sampled cells. An uncertain-marked cell counts as an error only if its bracketed candidates exclude the adjudicated reading.

If the adjudicated first-pass error rate for column 3 or column 4 exceeds 2%, the rule of Q-1005 applies: the method is revised (for example, double reading of every row) before the block's values are used for joins, and the join statistics are reported as provisional.

## Join and coverage

Rows are joined to Lipi faces in `data/normalized/lipi_observed_faces.jsonl` (hash checked against the data inventory's recorded SHA256) by the CISI base number: the Lipi `source_cisi` stripped of whitespace and any side or photograph suffix must equal the printed CISI number. CISI 2 basic data is per object, so all faces of a family inherit the row; the face side is reported but plays no part in the match. A family whose faces carry two different base numbers, or a number that matches two families, is reported as ambiguous and excluded from coverage counts.

Coverage before is measured with the data inventory's rules: excavation number is a usable Lipi `excavation-idno`; museum is a `MUSEUM` value in the older website export for the same CISI key; findspot is any usable Lipi area, block or room; depth, material and dimensions follow the inventory. Coverage after adds a field when the CISI 2 row supplies a usable value (not `???`, not empty). New identifiers that the local corpus lacks (FC number, photograph archive numbers) are counted separately.

Disagreements are counted by field. Excavation number: the printed number and the Lipi string are compared after removing spaces, hyphens and case; exact equality, the Lipi string beginning with the printed number, and other cases are counted separately. Museum: the printed column 4 and the website `MUSEUM` value are compared after mapping institution codes (MD and MJD, L and LHR, NMP and NMK or "National Museum, Karachi"); the numbers must match. Each disagreement is listed by CISI number with its type in a tracked file; the values stay local.

## Projection

Effort is measured as wall-clock minutes per entry for the first pass, the second pass and adjudication, from time stamps recorded in the run log. The full-section estimates multiply these by the entry counts of each section (CISI 2 printed pp. 435–447; CISI 1 basic data as located in its contents page), and the expected error count multiplies the measured error rates by the cell counts.

## Outputs

Tracked: this protocol, `render.py`, `parse.py`, `sample.py`, `score.py`, `join.py`, `renders.json`, `schema.json`, `accuracy.json`, `coverage.json`, `object-flags.csv` (per CISI number and Lipi family: which fields the row supplies, no values), `PROCEDURE.md` for parallel continuation, `README.md`, `RETROSPECTIVE.md`, `DATA-UPDATE.md`, `manifest-additions.json`, `question-updates.md`, `registry-entry.json`. Local only: renders, strips, `pass1.jsonl`, `pass2.jsonl`, adjudication notes with values, parsed rows.
