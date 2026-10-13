# Mackay 1938 and Marshall 1931 seal tables: acquisition, check and join

Package `2026-10-13-mackay-marshall-tables`, data round 1, 13 October 2026. Question cards [Q-1002](../../knowledge/questions/Q-1002-acquire-mackay-marshall-seal-tables.md) and [Q-1003](../../knowledge/questions/Q-1003-join-mackay-marshall-to-cisi.md). Rules: [PROTOCOL.md](PROTOCOL.md), with three amendments made after development runs.

## Result

The repository `epachayan/indus-script` is now held locally at commit `5c14a01f44296a01256a34e7e5e5e9fd82d9a67f`. Its `LICENSE-DATA` places the transcribed Mackay and Marshall tables under CC BY 4.0 and its `LICENSE` places the code under MIT. The Mackay table has 709 rows (Nos. 1-704 and addenda) and the Marshall table 560 rows (Nos. 1-557 with 526b, 528b and 557b). Hashes of every file used are in [acquisition.json](acquisition.json).

Against the printed tables, a random sample of 30 Mackay rows had no error and a sample of 30 Marshall rows had three rows with an error, in a size, a serial number and a seal type (Marshall 10%, Wilson 95% interval 3.5-25.6%; Mackay 0%, 0-11.4%). The join check and rows read beside sampled rows found eleven more differences from the print, seven of them in Marshall's serial numbers and one in a Mackay field number ([print-corrections.csv](verification/print-corrections.csv)).

Of the 1,269 table rows, 1,146 are joined to a Lipi object family: 1,108 exactly and 38 confirmed through a variant key or an adjudicated conflict. Two rows are ambiguous and 121 are unmatched, each with its reason. The joined rows cover 1,134 Lipi families at Mohenjo-daro, 1,122 of them seals, which is 85.1% of the 1,318 Mohenjo-daro seals in the export. Eleven families are joined to more than one row because the excavator listed the same object twice and the export's registration names both numbers. In a random sample of 30 joins, 29 were correct by the printed table and, for 23 of them, also by the excavation number printed in the CISI 1 or CISI 2 basic data; none was wrong, and one is unresolved (precision 96.7%, Wilson 83.3-99.4%; exact joins 20 of 20, 83.9-100%).

The joins add few values the export lacked. Lipi already carries a size, material, level and findspot for almost every joined object, and these agree with the tables: of the comparable pairs, 98.6% agree on size, 99.5% on material, 99.0% on block, house and room, and 99.7% on level. Mohenjo-daro objects gain both face dimensions for 12 more objects, a material for 5, an area or locus for 10 and a level for 2. What the tables do add, for 1,134 objects, is a field number separated from the excavator's catalogue number (the export writes them run together, as in `DK343942` for DK 3439, No. 42), a publication reference to the excavator's own table and catalogue number, a size traced to a printed page in its unit of record (inches, 1,091 objects), and a level with its datum (1,101 objects: Mackay's DK datum or SD bench mark, Marshall's depth below the modern surface). The local depth strings carried no datum before.

Where both sources have a value they disagree for 27 objects on the field number, 15 on size, 14 on object type, 5 on material, 5 on findspot, 3 on level and 3 on thickness. The field-number differences are mostly transcription errors: of eight sampled joins made through a variant field number, six had the print agreeing with the export (and with CISI, where held) against the transcription, one had the export wrong, and one (Mackay No. 181) has the printed table and CISI giving different numbers. The ten material and size conflicts examined against the print are real differences between the excavators' tables and the Lipi record; Mackay prints silver for Nos. 16 and 533 where the export has steatite, and Marshall prints red pottery for Nos. 431 and 450.

### Coverage before and after

Object level, with the data inventory's usable-value rule. Before is the Lipi export alone; after counts a value from Lipi or from a joined row. Full table: [coverage.csv](run-2026-10-13/coverage.csv).

| Field | Mohenjo-daro seals (1,318) | Mohenjo-daro objects (1,795) | All objects (4,695) |
|---|---|---|---|
| Any size | 94.39 → 94.61 (+3) | 86.91 → 87.13 (+4) | 76.63 → 76.72 (+4) |
| Both face dimensions | 82.93 → 83.84 (+12) | 75.93 → 76.60 (+12) | 61.13 → 61.38 (+12) |
| All three dimensions | 49.47 → 49.70 (+3) | 41.00 → 41.17 (+3) | 28.75 → 28.82 (+3) |
| Size with its printed source and unit | 0 → 81.94 (+1,080) | 0 → 60.78 (+1,091) | 0 → 23.24 (+1,091) |
| Material | 88.32 → 88.69 (+5) | 88.91 → 89.19 (+5) | 82.45 → 82.56 (+5) |
| Any spatial unit (area, block or room) | 95.90 → 96.66 (+10) | 91.03 → 91.59 (+10) | 76.32 → 76.53 (+10) |
| Block, house, room or street | 79.59 → 80.27 (+9) | 68.91 → 69.42 (+9) | 47.24 → 47.43 (+9) |
| Level or depth | 84.37 → 84.52 (+2) | 72.42 → 72.53 (+2) | 50.59 → 50.63 (+2) |
| Level with a stated datum | 0 → 82.63 (+1,089) | 0 → 61.34 (+1,101) | 0 → 23.45 (+1,101) |
| Registration string (raw) | 99.01 → 99.01 | 95.71 → 95.71 | 89.58 → 89.58 |
| Field number separated from catalogue number | 0 → 85.13 (+1,122) | 0 → 63.18 (+1,134) | 0 → 24.15 (+1,134) |
| Excavator's catalogue number (publication reference) | 0 → 85.13 (+1,122) | 0 → 63.18 (+1,134) | 0 → 24.15 (+1,134) |

Percentages of objects; the number of objects gaining the field is in brackets. For all seals at all sites (2,239) the changes are the same counts: both face dimensions 79.28 → 79.81%, material 81.73 → 81.96%, any spatial unit 85.62 → 86.07%, level 72.26 → 72.35%, separated field number and catalogue number 0 → 50.11%.

## Method

The repository was cloned and checked out at the pinned commit; nothing in it was executed. The Mackay vol. I scan (Internet Archive item `in.ernet.dli.2015.70071`) was downloaded once for its table pages, printed pp. 369-391. Marshall vol. II pp. 402-405 were read on the scan the evidence census had saved (`in.ernet.dli.2015.62023`) and, because that scan is binarized and loses letter strokes, on a second copy (`OLMh_mohenjo-daro-and-the-indus-civilization-edited-by-sir-john-marshall-vol.-2-1931-`, eight page images through the Internet Archive IIIF service). Apart from the git clone, eleven HTTP requests were made, all with the project User-Agent.

The join reads each Lipi `excavation-idno` as a field number followed, without a separator, by one or more catalogue numbers. A row joins exactly when the export's registration is the row's field number, or its field number followed by its own catalogue number, and no type, material or size contradicts. Marshall's area letters appear under other prefixes in the export (C as DK-C, E as DK-E, his DK as DK-B or DK-C), and these aliases were fixed after development runs (Amendment 1). Variant keys tolerate up to two edits in the field number when the catalogue number agrees, one edit in the catalogue number when the field number agrees, or a single trailing letter, and need at least two agreeing attributes (Amendment 2). Eleven exact-key candidates contradicted on material or size were read against the print and accepted when the print confirmed the table value and at least two other attributes agreed; one was left ambiguous, and two weaker candidates, one through a variant key and one through a letter suffix, were rejected ([contradiction-adjudication.csv](verification/contradiction-adjudication.csv), Amendment 3). Every row's disposition, candidates and reason are in [row-dispositions.csv](run-2026-10-13/row-dispositions.csv).

The transcription sample (seed 20261013) compared every column of 30 rows per table with the page image. The join sample (seed 20261014) drew 20 exact and 10 confirmed joins and checked each against the printed row and the CISI basic-data excavation number for the joined M-number; CISI 1 covers M-1 to M-620 and CISI 2 M-621 to M-1659, and six sampled objects numbered above M-1659 belong to CISI 3.1, which is not held, so they were judged on the print and the export's registration alone ([join-verification.csv](verification/join-verification.csv), [summary.json](verification/summary.json)).

Agreement between the tables and the Lipi record is not independent confirmation of either. The export's values for these objects descend, through CISI and ICIT, largely from the same printed tables: its size, locus and level for Mackay No. 181 repeat the table exactly although CISI gives the object a different excavation number. Agreement shows that a join links the record the export built from a table row back to that row; the CISI excavation number and the print are the independent checks. The comparison tolerances were 0.06 in for size agreement, 0.15 in on the larger dimension for a contradiction and 0.2 ft for level agreement. Lipi type codes were read as `SEAL:S` square, `SEAL:R` rectangular, `SEAL:C` circular and `SEAL:CY` cylinder. Most of the 14 type differences are differences of classification: the excavators give type B (square with a perforated boss) to some rectangular seals, call small two-sided pieces type D where the export has incised tablets, and list inscribed ivory rods as type A.

Of the 121 unmatched rows, 106 carry a field number that appears nowhere in the export's registrations, 10 share their field number with a joined row and are duplicate listings or misprints recorded in the transcription notes, 3 Marshall rows print no field number, and 2 had their only candidate rejected. Of the unmatched rows, 34 are of types E and G, which the transcription notes describe as buttons with linear designs (type E), and 28 of these are faience or paste; 61 are type B. The export holds only inscribed objects, so the unmatched rows are probably a mix of uninscribed pieces and inscribed seals the export lacks. The two ambiguous rows are Mackay No. 434, where two Lipi families carry the same registration, and Marshall No. 483, where only the registration links the row to the export.

## Sources and licences

| Source | Where | Licence or rights | Use |
|---|---|---|---|
| Koshy, `epachayan/indus-script` at `5c14a01` | `data/raw/2026-10-13-mackay-marshall-tables/epachayan-indus-script/` (local) | Transcribed tables CC BY 4.0 (`LICENSE-DATA`, seen at the pinned commit); code MIT (`LICENSE`); `docs/DATA_NOTICE.md` says MIT covers `scripts/` only | Tables joined; values reproduced in the tracked join table |
| Mackay 1938, *Further Excavations at Mohenjo-daro*, vol. I (archive.org DLI 2015.70071) | `data/raw/2026-10-13-mackay-marshall-tables/mackay1938/` (local) | The item's DLI record states "Out_of_copyright"; status of the 1938 Government of India publication not settled here | Printed table check |
| Marshall 1931, *Mohenjo-daro and the Indus Civilization*, vol. II, two scans | Census copy and `data/raw/2026-10-13-mackay-marshall-tables/marshall1931/olmh/` (local) | Rights unverified | Printed table check |
| CISI 1 and CISI 2 basic data | Held scans (local) | Copyright 1987 and 1991 Finnish Academy | Excavation numbers for the join check |
| Lipi export, `data/normalized/lipi_observed_faces.jsonl` | Local | No licence at the pin | Family ids, CISI numbers, registrations and attributes; only identifiers are tracked |

**Attribution for the tracked table values.** The columns `field_no`, `seal_type`, `size_in_as_printed`, `material`, `area`, `locus` and `level_ft` in [join-table.csv](run-2026-10-13/join-table.csv) are taken from Nitin Stephen Koshy, "Indus script: seal catalogues and text-structure analysis" (2026), https://github.com/epachayan/indus-script, commit `5c14a01`, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). This package selected and renamed the columns, combined block, house, room and street into one locus, and keyed the rows to Lipi family ids and CISI numbers; the values themselves are unchanged, including the transcription errors listed in [print-corrections.csv](verification/print-corrections.csv). The join keys, dispositions, checks and counts are this project's work under CC0. Lipi field values, page images and the clone stay local, except for the few Lipi materials, sizes and registration strings quoted as evidence in [contradiction-adjudication.csv](verification/contradiction-adjudication.csv) and [join-verification.csv](verification/join-verification.csv).

## Limits and what remains

Mackay's plate volume (vol. II) is not held, so a join cannot be checked against Mackay's photographs, and the CISI 3.1 objects (M-1660 and above, 6 of the 30 sampled joins) have no catalogue entry here. Mackay No. 181 needs that photograph comparison. The transcription error rate rests on 60 rows; the Marshall serial column shows more errors than the sample alone suggests, since 20 of the 492 joined Marshall rows needed a variant field number. Thickness is compared only for Mackay, which prints it, and findspot only for Mackay's block, house and room. The join table carries the transcription's values; the 14 print corrections are listed separately and not applied.

## Files and commands

Tracked: [PROTOCOL.md](PROTOCOL.md), this README, [RETROSPECTIVE.md](RETROSPECTIVE.md), [acquisition.json](acquisition.json), the run directory [run-2026-10-13/](run-2026-10-13/) (join table, row dispositions, coverage, summary), [verification/](verification/) (transcription check, join check, contradiction adjudication, print corrections, summary), the scripts, and the proposals [DATA-UPDATE.md](DATA-UPDATE.md), [manifest-additions.json](manifest-additions.json), [question-updates.md](question-updates.md) and [registry-entry.json](registry-entry.json). Local only, under `data/raw/2026-10-13-mackay-marshall-tables/`: the clone, the scans and page images, crops, the join detail with Lipi values (`run-2026-10-13/join-detail-with-lipi-values.csv`), ambiguous candidates and development runs.

Commands, from the repository root after cloning the repository into the local directory and checking out the pin:

```text
python -P experiments/2026-10-13-mackay-marshall-tables/acquisition_record.py
python -P experiments/2026-10-13-mackay-marshall-tables/render_pages.py
python -P experiments/2026-10-13-mackay-marshall-tables/join_tables.py --out experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13 --local data/raw/2026-10-13-mackay-marshall-tables/run-2026-10-13
python -P experiments/2026-10-13-mackay-marshall-tables/summarize_verification.py
python -P experiments/2026-10-13-mackay-marshall-tables/crop_rows.py mackay 20 49      # page crops for checking by eye
python -P experiments/2026-10-13-mackay-marshall-tables/crop_cisi.py out.png 1:403:M-120
```

`join_tables.py` refuses to overwrite an existing output directory and checks the hashes of its three inputs.
