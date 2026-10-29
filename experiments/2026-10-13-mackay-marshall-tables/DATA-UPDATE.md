# Proposed changes to knowledge/DATA.md

From package `2026-10-13-mackay-marshall-tables` ([README](README.md)). Each item gives the section, the text to replace or add, and the numbers that change. Coverage numbers are object-level percentages with the data inventory's rules, from [coverage.csv](run-2026-10-13/coverage.csv).

## Opening paragraphs

In the second paragraph, the manifest counts change from "85 sources (33 held, 9 partly held, 9 project outputs and 34 not held)" to "86 sources (33 held, 11 partly held, 10 project outputs and 32 not held)", if no other package changes the manifest in the same round ([manifest-additions.json](manifest-additions.json)).

## Section 1, "Inscribed-object corpora and catalogues": add a row after the Mayig row

| Source | Version and size | Where | Rights | Identifiers and fields | Known defects |
|---|---|---|---|---|---|
| [Koshy, machine-readable Mackay 1938 and Marshall 1931 seal tables](https://github.com/epachayan/indus-script) | Commit `5c14a01`; Mackay "Tabulation of Seals" 709 rows (Nos. 1-704 and addenda), Marshall "Tabulation of Seals" 560 rows (Nos. 1-557, 526b, 528b, 557b) | Local-only `data/raw/2026-10-13-mackay-marshall-tables/epachayan-indus-script/` | Transcribed tables CC BY 4.0 (`LICENSE-DATA`); code MIT | Excavator's catalogue number, field number, seal type, size in inches, material, Mackay block/house/room or street and level against the DK datum, Marshall area and depth below the surface | AI transcription: 0 of 30 sampled Mackay rows and 3 of 30 Marshall rows differ from the print; Marshall serials carry further errors ([print corrections](verification/print-corrections.csv)) |

## Section 1, "Excavation reports, comparison corpora and context data held locally"

In the first sentence, replace "The local copies include Marshall 1931 (*Mohenjo-daro and the Indus Civilization*, with the seal tabulation on vol. II pp. 402–405)," with:

> The local copies include Marshall 1931 (*Mohenjo-daro and the Indus Civilization*: vol. I as a government scan and vol. II, with the seal tabulation on pp. 402–405, as an Internet Archive scan, plus eight page images of a clearer vol. II copy), Mackay 1938 (*Further Excavations at Mohenjo-daro*, vol. I, with the seal tabulation on pp. 369–391; the plate volume is not held),

The local PDF counts (365 files, 299 distinct) predate the Mackay vol. I download and are left to the next holdings run.

## Section 2, "Metadata coverage": rows and a paragraph

The table is the 12 October measurement. If it is kept as the measured baseline, add the paragraph below after the "Source:" line. If the coordinator prefers current values in the table, the changed cells are: Mohenjo-daro row, Spatial unit 91.0 → 91.6, Depth 72.4 → 72.5, Material 88.9 → 89.2, Any size 86.9 → 87.1, All 3 sizes 41.0 → 41.2; Seals row, Spatial unit 85.6 → 86.1, Depth 72.3 → 72.4, Material 81.7 → 82.0, Any size 92.5 → 92.7, All 3 sizes 43.0 → 43.1; All objects row, Spatial unit 76.3 → 76.5, Material 82.5 → 82.6, Any size 76.6 → 76.7 (Depth stays 50.6, All 3 sizes stays 28.8, Excav. no. unchanged everywhere).

> **Excavation tables joined (13 October).** Koshy's transcriptions of the Mackay 1938 and Marshall 1931 seal tables were joined to the local objects through the registration strings, which the export writes as the field number followed by the excavator's catalogue number (`DK343942` is DK 3439, Mackay No. 42). Of 1,269 table rows, 1,146 joined (1,108 exact, 38 confirmed), 2 are ambiguous and 121 unmatched with reasons; the joins cover 1,134 Mohenjo-daro objects, including 1,122 of the 1,318 Mohenjo-daro seals (85.1%). A random sample of 30 joins had 29 correct against the print and the CISI basic-data excavation number, none wrong and one unresolved. The export already carried most of the tables' values, and they agree on 98.6% of comparable sizes, 99.5% of materials and 99.7% of levels, so coverage of those fields rises only slightly (Mohenjo-daro: both face dimensions +12 objects, material +5, spatial unit +10, depth +2). The tables add, for 1,134 objects, a field number separated from the catalogue number, a reference to the excavator's table and number, a size traced to a printed page in inches (1,091) and a level with its datum (1,101: Mackay's DK datum or SD bench mark, Marshall's depth below the modern surface). The table and the export disagree for 27 objects on the field number (mostly transcription errors in the table), 15 on size, 14 on object type, 5 on material, 5 on findspot, 3 on level and 3 on thickness. [Join report](README.md), [coverage](run-2026-10-13/coverage.csv).

## Section 3, "Corpora, concordances and databases": remove the Koshy row

Delete the row beginning "Koshy, machine-readable seal catalogues from Mackay (1938) and Marshall (1931)", since the source is now held (section 1).

## Section 3, "Excavation reports and archives": replace the Mackay 1938 row

| Source (check) | Contents | Access and terms | Adds per object | Effort | Card |
|---|---|---|---|---|---|
| Mackay 1938, *Further Excavations at Mohenjo-daro*, vol. II plates (W30) | Seal photographs on plates LXXXII-XCIX, numbered with Mackay's catalogue numbers; vol. I is now held | Internet Archive scans (`furtherexcavationsatmohenjodaro192731vol2ejhmackay_191_N`, `in.gov.ignca.9954`); the uploaders' CC0 tags do not settle copyright | A photograph check of the Mackay joins, including No. 181, whose field number differs between the table and CISI | Hours | [Q-1003](../../knowledge/questions/Q-1003-join-mackay-marshall-to-cisi.md) |

## Section 4, "Target object record": cells to change

| Field | Current coverage (replace with) | Best source to fill it (replace with) |
|---|---|---|
| `excavation_registration` | 89.6% raw strings, mixed with citations; field number separated from the excavator's catalogue number for 1,134 Mohenjo-daro objects (24.2% of all objects) | CISI basic data; excavation tables (Q-1014, Q-1016) |
| `publications` | Excavator's table and catalogue number (Mackay 1938 No., Marshall 1931 plate number) for 1,134 objects (24.2%); otherwise not recorded per object | Excavation reports, CISI, M77 (Q-1013) |
| `dimensions` | Any 76.7%; all three 28.8%; size traced to a printed table in its unit of record for 1,091 objects (23.2%) | CISI basic data; museum (Q-1020) |
| `findspot` | Any unit 76.5%; room or grid 39.7% | Excavation tables (Q-1014, Q-1016, Q-1017) |
| `depth` | 50.6% (strings, mixed units); datum stated for 1,101 Mohenjo-daro objects (23.5%) from the excavators' tables | Excavation tables (Q-1022) |

## Section 5, "Acquisition and enrichment priorities"

Rank 2 (Q-1002, Q-1003) is done. Replace the row's last two cells with "Done 13 October" and "1,146 of 1,269 rows joined to 1,134 objects; registrations separated, levels given a datum, 72 object-field disagreements listed". The follow-up check against Mackay's plate volume belongs with Q-1003's remaining items (see [question-updates.md](question-updates.md)).

## Section 7, "Rights": replace the epachayan row

| Source | Status | Handling |
|---|---|---|
| epachayan Mackay and Marshall tables | Explicit licence: transcribed data CC BY 4.0 (`LICENSE-DATA` at `5c14a01`), code MIT | Clone local; the join table's table values tracked with attribution to Nitin Stephen Koshy, "Indus script: seal catalogues and text-structure analysis" (2026), https://github.com/epachayan/indus-script, CC BY 4.0 |

Add to the row "CISI volumes, Mahadevan 1977, excavation reports, author PDFs": Mackay 1938 vol. I (archive.org DLI copy; its record states "Out_of_copyright", not verified here) and the Marshall vol. II page images are local.
