# Source and coverage audit

The six original Puruchuco accounts have complete identifier joins between the OKR master list and the SQLite object records. Together they contain 388 pendant records after excluding five marker records, nine subsidiary cords, 498 knot rows and 331 knot-cluster rows. Every pendant attachment-position value is zero. The [machine-readable audit](coverage-audit.json) gives counts for each field and object.

| Earlier ID | Stable OKR ID | Pendants | Subsidiaries | Markers | Recorded primary clusters |
|---|---|---:|---:|---:|---:|
| UR063 | KH0300 | 111 | 0 | 0 | 8 |
| UR064 | KH0301 | 71 | 3 | 0 | 7 |
| UR066 | KH0303 | 32 | 3 | 0 | 6 |
| UR067 | KH0304 | 32 | 3 | 0 | 4 |
| UR068 | KH0305 | 73 | 0 | 0 | 17 |
| UR073 | KH0310 | 69 | 0 | 5 | 16 |

The five extra level-one rows in UR073 have classification `M`. Excluding them reproduces the guide's 69 preserved pendants. Pendant numbering is unique after this exclusion. Every recorded parent link resolves to a primary or subsidiary cord within its object, and colour fields cover every selected pendant. The source states that UR073 is broken. It also reports that UR066 and UR067 were wrapped together. [KFG replication](https://khipufieldguide.com/notebook/appendix/notebooks/12%20-%20Replicating%20Purucucho.html), bounded SQLite witness at the hash below.

## Available physical fields

`CORD_LEVEL`, `PENDANT_FROM`, `CORD_ORDINAL`, `INVESTIGATOR_CORD_NUM`, `CLUSTER_ID` and colour codes preserve cord structure and order. The individual `ATTACH_POS` field supplies zero for all 388 pendants. Recorded cluster `START_POSITION` and `END_POSITION` fields preserve interval geometry at a coarser level. The eight recorded UR063 clusters differ from its six published accounting subunits; the 17 UR068 clusters include its introductory cords and smaller groups within the three twenty-cord rows. A group label therefore needs its source and scale recorded beside it.

All 331 selected knot clusters store zero in `TOTAL_VALUE`. Summing that field would assign zero to cords that the guide reads as positive quantities. The proposed extraction from this field stopped at coverage. The database also contains `knot_value_type` and knot-turn fields, but a separate documented aggregation route is needed to compare those recorded numerical codes with the guide's edition.

The next useful collection step is an object- and cord-specific witness for the numerical readings and finer attachment positions. It should identify the stable KH number, investigator cord number, parent ID, measured position or interval, colour components, termination and ambiguous reading. The saved source records can then be joined without replacing the current edition. The guide's [recording instructions](https://www.khipufieldguide.com/databook/ReadingKhipu.html) describe measurement and recording fields; its [file specification](https://www.khipufieldguide.com/databook/KFGExcelSpecification.html) includes an alternative-value field.

## CM009 and source editions

CM009 has no row in the acquired OKR database or master concordance. Its [KFG record](https://khipufieldguide.com/sketchbook/khipus/CM009/html/CM009_sketch.html) describes extraction from Mackey's 1970 thesis, pages 251-254. Knot locations and cord lengths were conjectured or taken from drawings; pale blue was changed to grey green to match other Puruchuco recordings. The reconstruction remains a distinct author witness.

The guide describes substantial cleaning and reconstruction of earlier data in [Building The Khipu Field Guide (KFG) Database](https://www.khipufieldguide.com/databook/DatabaseBuild.html). Its published Puruchuco notebook explicitly preserves numerical differences between its readings and the earlier article. Our source calculation retains that notebook's readings and alignment unchanged. Urton's 2005 [Khipu Archives: Duplicate Accounts and Identity Labels in the Inka Knotted String Records](https://dash.harvard.edu/server/api/core/bitstreams/7312037e-6b09-6bd4-e053-0100007fdf3b/content) supplies an accessible author manuscript for the archive and duplicate-account context.

## Versions, hashes and rights

The [OKR repository](https://github.com/khipulab/open-khipu-repository) was pinned to commit `4039ca51f4de661d80d0160596309c983a62a9c7`, dated August 4, 2026. Its 39,170,048-byte SQLite file has SHA256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`. The database Git blob equals the blob in release v2.1.0. The [Zenodo record](https://zenodo.org/records/18025748) dates that release to December 22, 2025; its API labels the license `other-open` and access `open`.

The repository license is MIT and describes software and associated documentation. The acquired database, concordance, HTML pages, manuscript and source-derived vectors stay local under the project's source policy. The Zenodo metadata did not supply a named data license. [Initial acquisition](acquisition.json) and [supplement](acquisition-supplement-01.json) preserve URLs, retrieval times, byte counts, hashes and observed notices. Our protocols, code, summaries, generated worlds and aggregate scores form the shareable package.
