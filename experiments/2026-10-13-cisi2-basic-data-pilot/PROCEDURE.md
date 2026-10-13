# Procedure for transcribing the CISI basic-data sections in parallel blocks

This procedure continues the pilot of 13 October 2026 (M-621 to M-947 of CISI 2) to the rest of CISI 2 and to CISI 1. It lets several people or agents work at once without overlapping, and it produces tables that merge into one schema ([schema.json](schema.json)). The pilot's measured error rates and effort are in [README.md](README.md); the rule below follows from them.

## Sources and page map

CISI 2 (Shah and Parpola 1991, *Corpus of Indus Seals and Inscriptions. 2. Collections in Pakistan*) is the archive.org scan `data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf` (SHA256 `5258071b…`). Its printed page is PDF page minus 35 throughout the catalogue: printed pp. 1–447 are PDF 36–482, and 418 of the 447 pages show the expected number in the corner header of the scan's text layer (the other 29 headers are unreadable; those pages have not been inspected). The basic data runs from printed p. 434 (key and abbreviations, PDF 469) to p. 447 (PDF 482), where the corrigenda follow the last entries.

CISI 1 (Joshi and Parpola 1987, *Corpus of Indus Seals and Inscriptions. 1. Collections in India*) is `research/literature/sources/joshi_parpola_1987_cisi1.pdf`; use PDF pages 1–431 only (the scan repeats them). Its basic data runs from printed p. 365 (PDF 401, key) to p. 375 (PDF 411, last entries and the corrigenda); printed p. 366 opens with M-1 to M-100. The five columns are the same as in CISI 2, and CISI 1's column 3 adds the markers (o), number written on the object, and (t), number in the tabulation of the excavation report, which must be kept as printed. CISI 1's scan has no text layer and its embedded page images are about 815 × 1147 px, so render at zoom 4 (the plate-check package found that legible) and expect a lower error rate than CISI 2 only if a pilot block shows it.

## Blocks

A block is one half-column of one printed page: the left (L) or right (R) column of entries. Each holds about 80 entries, which one reader can finish in one sitting. Block identifiers are `cisi2-p437L`, `cisi2-p437R`, and so on; `cisi1-p366L` for CISI 1.

| Block | Printed page (PDF) | First and last entry | Status |
|---|---|---|---|
| cisi2-p435L | 435 (470) | M-595, M-621 to M-704 | pilot done, M-595 not transcribed |
| cisi2-p435R | 435 (470) | M-705 to M-787 | pilot done |
| cisi2-p436L, p436R | 436 (471) | M-788 to M-869; M-870 to M-947 | pilot done |
| cisi2-p437L, p437R | 437 (472) | M-948 to M-1032; M-1033 to M-1119 | open |
| cisi2-p438L, p438R | 438 (473) | M-1120 to M-1197; M-1198 to M-1277 | open |
| cisi2-p439L, p439R | 439 (474) | M-1278 to M-1355; M-1356 to M-1436 | open |
| cisi2-p440L, p440R | 440 (475) | M-1437 to M-1519; M-1520 to M-1611 | open |
| cisi2-p441L, p441R | 441 (476) | M-1612 to H-411; H-412 to H-496 | open |
| cisi2-p442L, p442R | 442 (477) | H-497 to H-586; H-587 to H-665 | open |
| cisi2-p443L, p443R | 443 (478) | H-666 to H-750; H-751 to H-837 | open |
| cisi2-p444L, p444R | 444 (479) | H-838 to H-917; H-918 to H-988 | open |
| cisi2-p445L, p445R | 445 (480) | H-989 to Rhd-66; Rhd-67 to Rhd-156 | open |
| cisi2-p446L, p446R | 446 (481) | Rhd-157 to Rhd-251; Rhd-252 to Ai-8 | open |
| cisi2-p447L, p447R | 447 (482) | Blk-1 to Mr-15; Mr-16 to ?-6, then corrigenda | open |
| cisi1-p366L … cisi1-p375R | 366–375 (402–411) | M-1 onward | open |

The first and last entries of each half-column were read from the page headers and the first line of each right-hand column (checked at higher zoom for pp. 437, 438 and 441); the last entry of a left-hand column is the entry before the first of the right-hand one. A contributor confirms both ends on the page before starting and corrects this table in the report if they differ.

## Claiming

Claim a block by adding your name and the date to the block's row in the shared block register (the coordinator copies the table above into question card Q-1006, and a matching one into Q-1005). Work in your own dated package, `data/raw/YYYY-MM-DD-<slug>/` for values and `experiments/YYYY-MM-DD-<slug>/` for tracked records. Never edit another contributor's block files.

## Files for each block

All value files are local (the catalogue's rights are unresolved). For block `cisi2-p437L` read by contributor `<slug>`:

| File | Content |
|---|---|
| `data/raw/<date>-<slug>/cisi2-p437L.pass1.txt` | first reading |
| `data/raw/<date>-<slug>/cisi2-p437L.pass2.txt` | second reading, by a different reader who has not seen pass 1 |
| `data/raw/<date>-<slug>/cisi2-p437L.adjudication.json` | one record per disagreeing cell: both readings, the adjudicated reading, and the outcome (`first-pass-right`, `second-pass-right`, `both-wrong`, `undecidable`) |
| `data/raw/<date>-<slug>/cisi2-p437L.final.txt` | the adjudicated block, in the pass format |
| `experiments/<date>-<slug>/cisi2-p437L.accuracy.json` | tracked: cells per column, agreement, adjudication outcomes, reading times; no values |

The pass format is the one in [PROTOCOL.md](PROTOCOL.md): a first comment line `# <pass> , CISI <n> printed p. NNN (PDF NNN), block <id>`, then one line per entry with the five printed columns separated by ` | `. Keep the printed text: continuation lines of a column joined by a space, piece lines joined by ` // `, and unreadable characters written `[a/b]`, `[?]` or `[??]`. Do not fill a cell from Lipi, the older website export, the scan's text layer or any other source.

## Reading

Render the page with `python experiments/2026-10-13-cisi2-basic-data-pilot/render.py page <pdfpage>` (zoom 8.34 for CISI 2) and cut 1:1 strips of fourteen lines with `render.py strip <pdfpage> <y0> <y1> <x0> <x1>`; the left half-column spans x 150–1500 and the right x 1700–3150 on CISI 2 renders. Enlarging or sharpening does not add detail to this scan. A crop of columns 1 to 4 only, 880 px wide and about 23 lines tall, is a useful second view for digits.

## Double reading

Every block is read twice. In the pilot the sampled first-pass error rate for excavation numbers was 3.0% (1 of 33), above the 2% that Q-1005 allows for museum and excavation numbers, and in the full comparison a single reading gave a definite value that the page could not confirm in 7.0% of excavation cells and 9.5% of museum cells. A sampled check therefore cannot stand in for the second reading. The second reader works from the page renders alone, without the first pass; for agents, start a separate instance and give it only the render paths, the block's entry range and this procedure. Compare the two passes cell by cell with `score.py` (adapted to the block's file names), adjudicate each disagreement against the page, and bracket the cell when the scan cannot decide.

After adjudication, run the cross-check of the pilot: join the block to Lipi and the older export with `join.py` and re-read against the page every cell where the excavation number differs from Lipi's `excavation-idno` once the appended FC tail and area prefix are allowed for, or where the museum number differs from the older export. Record each recheck as `confirmed`, `corrected`, `ambiguous` (bracket the cell) or `lipi-defect`. This step is not blind, so it may only resolve or bracket cells; it does not count towards the error rate.

## Merge

When all blocks of a volume are final, merge them:

```text
python experiments/2026-10-13-cisi2-basic-data-pilot/merge.py --out data/raw/<date>-<slug>/cisi2-basic-data.jsonl \
    --range M-621:M-1659 --range H-383:H-1019 --range Rhd-1:Rhd-270 ... <all block .final.txt files>
```

The merge refuses duplicate CISI numbers and lists every number in the given ranges that has no row. Each listed number is checked on the page and recorded as an absence with its page, or added to the block that missed it. The merged table is then joined to the local corpus with `join.py`, which writes coverage counts and per-object flags that can be tracked.
