# Data record for DATA.md and the manifest

This package adds true-north orientation to the settlement record of the [town-axes package](../2026-10-21-town-axes/DATA-RECORD.md) for towns whose walls are covered, by registering published plans to imagery, and it corrects two site coordinates that the settlement table used. The proposed manifest entry is in [manifest-additions.json](manifest-additions.json); maintainers fold it and the text below into `data/MANIFEST.json` and `knowledge/DATA.md` after merging.

## New sources

| Source | What we used | Location and rights |
|---|---|---|
| Esri World Imagery, current release, zoom 18 | Seven mosaics at Chanhu-daro, Dholavira, Harappa, Lothal and Shikarpur, read for control points | Local-only under `data/raw/2026-10-21-plan-registration/<agent>/mosaics/`; Esri terms, not redistributed; georeferencing tracked in `imagery-v1/mosaics.json` |
| Esri World Imagery Wayback, releases 4230, 8432, 11351, 16749 and 64776, zoom 17–18 | Nine mosaics where an older capture showed mound relief, terraces, water levels or walls better: Kalibangan (relief), Surkotada (walls), Farmana (2011 terraces), Chanhu-daro and Lothal | As above; release numbers recorded per mosaic |
| Gadekar, C., S. V. Rajesh and P. Ajithprasad 2014. "Shikarpur lithic assemblage: New questions regarding Rohri chert blade production". *Journal of Lithic Studies* 1(1), doi:10.2218/jls.v1i1.764, Figure 2 | The only Shikarpur plan found that draws the fortification with an arrow and scale bar; measured and registered | CC BY 2.5 Scotland; figure image retrieved from a Wayback Machine capture of the HTML galley, local-only under `data/raw/2026-10-21-plan-registration/S/`; acquisition records in `measure-S/sources.json` |
| Mackay 1943, Plate I (contour map of Chanhu-daro), and Shinde et al. 2008, Fig. 7 (contour map of Farmana's Main Mound) | Auxiliary plans that link the measured plans to features visible today | Pages of publications already held locally; renders local-only |
| Rakhigarhi search | Nath's ASI report, *Puratattva* 28, 29 and 31, *Indian Archaeology – A Review* 1997–98 to 2000–01, Shinde et al. 2018 (*PLoS ONE*), the 2023 Archaeopress volume's open sample | Examined; none has a plan of structures with an arrow; records in `measure-S/sources.json` and `measure-S/towns/rakhigarhi.json` |

## New fields and coverage

| Field | Towns before | Towns now | Where |
|---|---:|---:|---|
| True bearing of a published plan's north arrow, with error | 0 plans | 14 plans at 8 towns | `registration-v1/results.json`, `plans.*.arrow_true_bearing` |
| Control points linking a plan to imagery, with class and description | 0 | 43 control files (two registrars) for 22 plans | `control-R1/`, `control-R2/`, `control-S/` |
| Axis deviation from true north, any method | 5 towns | 10 towns | imagery: Mohenjo-daro, Harappa, Lothal, Dholavira, Sutkagen-dor; registration: Kalibangan, Surkotada, Chanhu-daro, Farmana, Shikarpur |
| Axis deviation from true north at a town with a layout date | 4 | 8 | as above, without Sutkagen-dor and Shikarpur |
| Plan-based wall systems converted to true north | 0 | 27 systems on 13 plans | `registration-v1/results.json`, `systems` |
| Shikarpur fortification lines measured on a plan | 0 | 8 lines, 1 system | `measure-S/towns/shikarpur.json` |

## Corrections to site coordinates

| Town | Coordinate used before | Found | Evidence |
|---|---|---|---|
| Surkotada | 23.6304 N, 70.8407 E (English Wikipedia, via plan-B; img-A searched here) | 23.6113 N, 70.9174 E, 8.1 km east-south-east | Exposed citadel walls matching Joshi's plans, found independently by two registrars; agrees with the GAZETTEER2018 entry in `experiments/2026-10-08-site-map-and-overview/data/sites-census.json` |
| Farmana | 29.0667 N, 76.5667 E (English Wikipedia, approximate) | about 29.040 N, 76.306 E, 25 km west | Shinde et al. 2008 give the site as 29°02′22″ N, 76°18′21″ E and Datum Point 2 as 29°02′26″ N, 76°18′30″ E; one registrar found the terraced mound 100–200 m from these points |
| Chanhu-daro | 26.1736 N, 68.3231 E | within about 60 m | One registrar placed the mounds 60 m west-south-west, the other at the published point |
| Gola Dhoro | 21.4833 N, 70.95 E | not found | The coordinate is that of the town of Bagasra; the report places the site in Rajkot district |

The town-axes horizon profiles for Surkotada and Farmana were computed at the old coordinates and should be recomputed; at 8 and 25 km the change matters only where hills are near.

## Gaps this leaves

Banawali and Kanmer have plans but no feature that both the plans and current or archived imagery show; a GNSS or drone survey of the exposed fortification remains the route to their true-north values. Rakhigarhi has no published plan of structures with an arrow that we could find openly. Surkotada's masonry is exposed at the corrected coordinates and can now be measured directly on imagery.
