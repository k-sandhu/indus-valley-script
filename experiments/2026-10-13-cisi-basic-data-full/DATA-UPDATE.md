# Proposed changes to knowledge/DATA.md

From this package ([README](README.md)). The transcribed values are local; every number below is a count from [coverage.json](coverage.json), [combined-coverage.json](combined-coverage.json), [accuracy-summary.json](accuracy-summary.json) or [predictions.json](predictions.json). Links are written relative to `knowledge/DATA.md`.

## Opening paragraph

In the sentence on the 13 October gains, replace the museum figure with: "objects with a museum number to 52.2% (2,450, counting uncertain digits in the CISI tables; 42.5% when the whole cell is free of brackets)", and add: "and every catalogue entry of the CISI 1 and CISI 2 basic data now has a row ([full transcription](README.md))."

## Section 1, "Project registers, frames and releases": add a row

| [CISI basic data, full transcription](README.md) (13–14 October) | CISI 1: 1,543 rows; CISI 2: 2,139 rows; 2,602 joined to Lipi families | Values local (rights unverified); counts, accuracy, coverage and per-object field flags tracked | CISI 1 double-read and adjudicated (98.6% agreement); CISI 2 double-read, three blocks adjudicated and the rest kept as the union of both readings (65.3% agreement) |

## Section 2, "Metadata coverage": replace the "Museum numbers (13 October)" paragraph

**Museum numbers (13 and 14 October).** The museum harvest joined 87 museum records, and the full transcription of the CISI 1 and CISI 2 basic data gives a museum number to every catalogue entry that prints one. Objects with a museum number from any source rise from 274 (5.8%, the older export) and 340 (7.2%, with the census and museum joins) to 2,450 of 4,695 (52.2%) when CISI cells with an uncertain digit count, 2,079 (44.3%) when at least one number in the cell is definite, and 1,994 (42.5%) when the whole cell is free of brackets. Among the 2,602 objects that join a CISI entry, holding institution rises from 226 to 2,560 and FC concordance number from 0 to 2,599 ([coverage](coverage.json), [combined](combined-coverage.json)). The CISI values are local until the rights in CISI are settled.

## Section 2, "Conflicts": add

The FC concordance number encodes the excavators' catalogue numbers: for Mohenjo-daro entries outside the pilot block that join a Mackay or Marshall table row, FC = 2000 + Mackay No. or 1000 + Marshall No. for 560 of 573 (97.7%), and for Harappa the digits that Lipi appends to a registration equal the FC number without its first digit for 221 of 226 scorable entries ([predictions](predictions.json)).

## Section 4, "Target object record"

`identifiers`: "FC concordance number for 2,599 objects (CISI basic data, values local)". `museum`: "5.8% in the older export; 52.2% counting uncertain digits, 42.5% bracket-free, with the CISI basic data and the museum joins (CISI values local)".

## Section 5, "Acquisition and enrichment priorities"

Rank 3 (Q-1005, Q-1006): "Done 13–14 October for CISI 1 and for the rows of CISI 2; remaining: adjudicate about 2,870 bracketed CISI 2 cells and re-read 1,206 cross-check flags ([package](README.md))".
