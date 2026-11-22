# Data update: Reconciled Indus site and survey-effort gazetteer

Date: 22 November 2026. Package: `experiments/2026-11-22-site-survey-gazetteer/`. For maintainer integration into `knowledge/DATA.md` and `data/MANIFEST.json` after review.

## What this package adds

This package adds the project's first cross-register reconciled site and survey-effort gazetteer (`v1`), integrating six held local packages without modifying upstream endpoints or acquiring external third-party bulk databases. It adds no new inscribed objects, face transcriptions, museum accessions, or radiocarbon determinations.

### Tracked CC0-safe derived tables

| File | Logical path | Bytes | SHA-256 | Contents |
|---|---|---:|---|---|
| `gazetteer-v1.json` | `experiments/2026-11-22-site-survey-gazetteer/gazetteer-v1.json` | 752,912 | `f7a85856ad767a698fe188c6652875218c6952aecf0dba58ff1b59e9bbd3a65d` | 144 reconciled entities separating `recorded_locality`, `physical_mound_or_scatter`, `phase_footprint`, and `excavated_deposit`, with 271 verbatim coordinate assertions, conflict spreads, excavation status, living-town overlap, and survey tags |
| `gazetteer-v1.csv` | `experiments/2026-11-22-site-survey-gazetteer/gazetteer-v1.csv` | 62,024 | `103bfbf72b096755668061411af18092092c845690c23ecf1737362a003d51cb` | Flat 144-row table matching `gazetteer-v1.json` |
| `aliases-v1.csv` | `experiments/2026-11-22-site-survey-gazetteer/aliases-v1.csv` | 53,967 | `4dfa0ca5722963ba98b0ff7c04887f75bc84146ad0d25bfd97730f51eae7ced8` | 443 alias rows (144 canonical names, 299 non-canonical aliases, 6 flagged ambiguous homonyms) |
| `survey-effort-v1.json` | `experiments/2026-11-22-site-survey-gazetteer/survey-effort-v1.json` | 48,152 | `6bd1f6fde51ef2b4e176ee5ca35427023a98c8abded9debe4c5bb45fa291d3d1` | 19 documented regional survey campaigns, 21 prospection-window effort profiles (`P01` to `P21`), and held spatial concordance summaries |
| `coverage-v1.json` | `experiments/2026-11-22-site-survey-gazetteer/coverage-v1.json` | tracked | see file | Exact counts, breakdowns, 24 coordinate-conflict summaries, and 21 upstream input SHA-256 digests |
| `verification-v1.json` | `experiments/2026-11-22-site-survey-gazetteer/verification-v1.json` | tracked | see file | Independent 8-check verification output (`8/8` passed) |

### Local-only raw concordance extract

| Logical path | Physical path | Bytes | SHA-256 | Rights handling |
|---|---|---:|---|---|
| `data/raw/2026-11-22-site-survey-gazetteer/raw-concordance-extract-v1.json` | `D:\projects\indus_valley_script\data\raw\2026-11-22-site-survey-gazetteer\raw-concordance-extract-v1.json` | 10,724 | `95e8b195555b5ce57cc1d068616d5e3cd62e0bac008130e6c18769bdad4fed0f` | Local-only (`mixed-assets` derivative of local MAHSA API responses, Orengo 2020 AOI polygon, Singh 2017 derived core table, and Rajesh et al. 2025 page 1 excerpt; kept out of Git per `knowledge/provenance/REDISTRIBUTION.md`) |

## Changes in coverage

1. **Entity coverage grows from 115 to 144 reconciled records** (137 `recorded_locality`, 2 `regional_provenance_label`, 5 `physical_mound_or_scatter`). The 29 newly integrated records comprise 14 non-overlapping living-town continuity references, 8 documented non-corpus Indus survey localities (`Padta Bet`, `Dwajagadh`, `Kotada (Lodrani)`, `Ghazi Shah`, `Lakhapar`, `Bahola`, `Kaj`, `Kanjetar`), 2 post-catalogue inscribed-find localities (`Dhalewan`, `Indiranagar (Kanpur)`), and 5 unverified remote-sensing mound proposals (`B01-T0115`, `B04-T0180`, `B04-T0257`, `Khundowala`, `Mulhiawala`).
2. **Previously unjoined cross-register records are now linked**: Q-1032 towns `desalpur` and `gola-dhoro` join `desalpar` and `gola-dhoro-bagasra` (bringing Q-1032 reconciliation from 32 of 34 to 34 of 34), Living Towns record `LT-11` (`Rupnagar / Ropar`) joins `ropar-rupar`, and 16 Evidence Census `site-register.json` spelling variants join their canonical IDs.
3. **Coordinate assertions and conflicts are quantified**: 271 coordinate assertions across 133 located records, exposing 22 material conflicts (`>= 1.0 km`), 2 documented unquantified locator conflicts (`Nindowari`, `Tell Abraq`), and 8 minor offsets (`0.1 to 1.0 km`). Banawali's primary coordinate is upgraded to the Q-1032 imagery-confirmed mound centre (`29.5984, 75.3923`), replacing a 13.90 km offset Getty TGN point that remains preserved as a competing assertion.
4. **Survey-effort coverage is structured for all 21 prospection windows (`P01` to `P21`)**: 46 records fall inside `P01` to `P21` and 47 carry regional survey-campaign tags, while `P04` and `P05` are explicitly documented as intensively surveyed corridors with zero locally held row-level site records.

## Remaining data gaps for `knowledge/DATA.md`

1. **Unlocated archaeological localities (11 records)**: `Wattoowala`, `Dhalewan`, `Indiranagar (Kanpur)`, `Lakhapar`, `Bahola`, `Kaj`, `Kanjetar`, `Khundowala`, `Mulhiawala`, plus regional labels `Dilmun` and `Luristan`. Nine of these are physical sites or proposals whose primary coordinates need acquisition from excavation reports or author supplements.
2. **Unresolved multi-kilometre coordinate conflicts (24 records)**: Top verification priorities are Rojdi (51.06 km), Desalpar (42.17 km), Gola Dhoro active report disagreement (10.43 km, separate from the 178.41 km excluded Bagasara town pin), Kunal (13.74 km), Ganweriwala (13.68 km), Allahdino (11.12 km), Mitathal (6.52 km), Nindowari (~78 km warning), and Tell Abraq (Tarut Island locator warning).
3. **Row-level regional survey tables not yet held**: Green et al. (2019) 779-feature field-check supplement (`P03` to `P06`), Orengo et al. (2020) 337-cluster Cholistan coordinates (`P01`, `P02`), Cambridge 127-location Rakhigarhi catchment table (`P07`), Garcia-Molsosa et al. (2023) 240 PAS sites (`P08`, `P09`), and bulk MAHSA site inventory (currently only 5 targeted API probes returning historic map sheets are held locally).
4. **Missing fieldwork campaign entries in inherited Gulf and Mesopotamian census rows**: Seven contact-zone localities (`Babylon`, `Saar`, `Tell Abraq`, `Karzakan`, `Janabiyah`, `Kalba`) plus three Cholistan DOAM points (`Derawar Ther`, `Guddal A`, `Rappwala Ther`) carry `excavation_status = unknown` because the inherited 8 October register stored catalogue citations or bare inventory points without structured excavation-campaign rows.
