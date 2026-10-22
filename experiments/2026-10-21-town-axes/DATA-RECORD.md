# Data record for DATA.md and the manifest

This package adds the project's first table of settlement fields. Until now the object record stopped at the site name: [DATA.md](../../knowledge/DATA.md) lists a census site register of 115 entities and the settlement-prospection sources, but no site carried coordinates checked on imagery, an axis bearing, a horizon or a dated layout phase. The proposed manifest entries are in [manifest-additions.json](manifest-additions.json); maintainers fold them and the text below into `data/MANIFEST.json` and DATA.md after merging.

## New sources

| Source | What we used | Location and rights |
|---|---|---|
| Esri World Imagery, zoom 18 | Mosaics of 21 site areas measured by two imagery agents; tile ranges, acquisition metadata and SHA-256 per mosaic in each measurer's `sources.json` | Local-only, 309 MB under `data/raw/2026-10-21-town-axes/img-A/` and `img-B/`; Esri terms, not redistributed |
| Copernicus DEM GLO-30 and GLO-90 | Horizon profiles from 2 to 250 km; tiles read into memory, each URL and SHA-256 listed in `horizon-v1/horizons.json` | Not stored; derived altitudes tracked |
| Published site plans | 25 plan sources for plan-B (Marshall 1931 and Mackay 1938 plate volumes, Vats 1940, Mackay 1943, Wheeler 1947, Rao 1963 and 1979, Joshi 1990, Possehl and Raval 1989, *Indian Archaeology – A Review* 1955–2001, Kharakwal et al. on Kanmer, Shinde et al. 2008 on Farmana, the ASI's 2020 Dholavira dossier) and the plans plan-A rendered | Local-only, 865 MB; URLs and hashes in `measure-plan-B/sources.json` and `downloads.json` |
| Dating literature | 199 sources: the *Radiocarbon* date lists of the TF, PRL, BS and Pennsylvania laboratories, Ramachandran 1975, Mandal 1972, the Lothal, Surkotada and Kalibangan memoirs, HARP reports and recent papers | Local-only, 2.0 GB under `data/raw/2026-10-21-town-axes/dating/`, each file logged with URL, time and SHA-256 |
| SIMBAD | J2000 astrometry of Alcyone, Aldebaran, Procyon and Thuban | Tracked as `stars-v1.json`, with the SIMBAD acknowledgement |
| IntCal20 | Calibration of layout-phase radiocarbon ages for a sensitivity check | Local-only |
| Vahia and Menon 2013 | Dholavira's orientation, "inclined 6° to the west of north" | Local-only |

## New fields and coverage

| Field | Towns before | Towns now | Where |
|---|---:|---:|---|
| Site coordinates checked on imagery | 0 | 21 | `horizon-v1/coordinates.json`, `table-v1/` |
| Apparent horizon east and west (0.1° steps) | 0 | 21 | `horizon-v1/horizons.json` |
| Axis deviation from true north, two independent imagery measurements | 0 | 4 | `table-v1/` (Mohenjo-daro, Harappa, Lothal, Dholavira) |
| Axis deviation from true north, one imagery measurement | 0 | 1 | Sutkagen-dor |
| Axis deviation relative to a published plan's arrow, with the arrow's label | 0 | 13 | `table-v1/`, `plans` field |
| Layout phase per part of town, with the excavator's description and page | 0 | 29 | `dating-v1/towns/` |
| Radiocarbon determinations by phase (382 entries, printed and 5568-year ages) | 0 | 20 | `dating-v1/towns/` |
| Layout start with evidence tier and error | 0 | 11 | `dates-v1/dates.json` |

The layout dates also serve [Q-1021](../../knowledge/questions/Q-1021-chronology-calendar-ranges.md): the dating records give calibrated or cross-dated calendar ranges, with pages, for the period labels of Harappa (Periods 2, 3A, 3B), Kalibangan (Periods I and II), Lothal (Phases I to IV), Dholavira (Stages I to III), Surkotada (Sub-periods IA to IC), Kanmer (KMR I to III), Rojdi (A to C) and others.

## Gaps this leaves

Nine towns have no measurable Harappan line in current imagery because their excavations are backfilled, roofed or overgrown (Kalibangan, Banawali, Rakhigarhi, Chanhu-daro, Kanmer, Shikarpur, Bhirrana, Kot Diji, Nausharo), and the mounds of Surkotada, Juni Kuran and Kotada Bhadli were not confirmed at their published positions. Of the 13 towns with plans, only one plan (the ASI's 2020 Dholavira survey, drawn on a graticule) states that its north is true; Mackay's Chanhu-daro plan states magnetic north with its date. No published Bayesian model of a layout boundary exists for any town, and Dholavira, Mohenjo-daro's lower town, Chanhu-daro, Shikarpur and Rangpur have no radiocarbon from their layout phases. The cheapest next acquisition is a set of true-north bearings at the backfilled towns from published plans registered to ground control points, followed by a GNSS or drone survey where walls are exposed.

## Ledger

This test used no inscriptions and spent nothing in the corpus. We propose the statistic family `settlement_axis_orientation` on the population "planned Harappan towns" for `bench/spent.json`; maintainers add it, since the ledger is a shared file.

## A source locator to correct

The coordinating brief gave the Wanzke scan's page offset as printed page = PDF page index + 2. On `research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf` it is printed page = PDF page index − 2: printed p. 33 is PDF page index 35.
