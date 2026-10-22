We completed the saved verification checks, with unresolved source coverage and join objections. The revised snapshot has 503 rows, including 301 main rows: 11 matched, 271 candidate and 19 absent. Its absent bounds are 45–290. All 540 site-table cells recompute exactly, including the three added context sensitivity columns. Those give 77 matched main rows and bounds 45–224. The current locator and identifier audit has no failures. The remaining objections are recorded below; the source list was not edited by this run.

The object list, join decisions and site counts were revised externally during the audit. We preserved the initial results and captured four revised input CSV files in revised-input-2026-10-21/. The initial arithmetic also reproduced exactly, with 77 matched main rows, 205 candidates and bounds of 45–224. No sampled blind field changed between revisions. input-revision.json gives both hashes; the revised object table is SHA256 e8babef6e4fb1d3df2c5f00c955b1376d9c7a6d8df88d6d89c7e075e38336037.

The blind sample contains 60 of 503 rows, selected with seed 20261021: N 5, G 9, D 25, P 15, E 1, F 5. Part E contains only one row, which was included. The allocation starts with the minimum available per part and fills the largest remaining raw-quota deficit. The source-only observations were frozen before comparison. There are 113 field disagreements, 198 unassessed field slots and 35 inapplicable registration slots. Unassessed fields were retained. When both entries say unknown, agreement records missing evidence; it does not confirm that an illustration or transcription exists.

Per-field agreement among assessed comparisons is shown below. Intervals are two-sided exact binomial 95% intervals. They are descriptive and unweighted; shared source pages make rows dependent. blind-summary.json also gives conservative rates using every applicable sampled row.

| Field | Agreement | Exact 95% interval | Unassessed |
|---|---:|---:|---:|
| season | 26/43 (60.5%) | 44.4%–75.0% | 17 |
| object_type | 39/39 (100.0%) | 91.0%–100.0% | 21 |
| findspot | 9/35 (25.7%) | 12.5%–43.3% | 25 |
| page | 39/57 (68.4%) | 54.8%–80.1% | 3 |
| plate_or_figure | 29/35 (82.9%) | 66.4%–93.4% | 25 |
| photo_published | 35/43 (81.4%) | 66.6%–91.6% | 17 |
| drawing_published | 40/43 (93.0%) | 80.9%–98.5% | 17 |
| transcription_published | 9/43 (20.9%) | 10.0%–36.0% | 17 |
| inscription_status | 3/4 (75.0%) | 19.4%–99.4% | 56 |
| registration_present | 25/25 (100.0%) | 86.3%–100.0% | 0 |

The 40 omission pages were drawn with seed 20261022 from unique source-page pairs listed with purpose candidate. We could assess 31 inventories and found no confirmed omitted object. Their conditional omission rate is 0/31, with exact 95% interval 0.0%–11.2%. The full-sample omission rate is unavailable because nine inventories remain unresolved. If all nine were clear, the full-sample interval would be 0.0%–8.8%; if all nine contained an omission, the rate would be 9/40 with interval 10.8%–38.5%. There is no confirmed omitted-object description to list. Farmana, PDF page 391, seal, is already represented from PDF page 385; its illustration page is an explicit page-citation gap.

Unresolved omission pages are iar-2013-14 PDF 106; chanhu-surface2017-held PDF 155; iar-2003-04-asi PDF 62; chanhu-surface2017-held PDF 195; iar-1997-98-archive PDF 329; puratattva-33 PDF 188; puratattva-35-held PDF 85; chanhu-surface2017-held PDF 187; chanhu-surface2017-held PDF 203. No substitute pages were drawn.

No count cell differs, and no applied decision differs after using protocol_local_match for the revised register. The 131 literal differences from its historical columns are documented separately: 67 status cells and 64 family-set cells. Historical context identities are preserved in context_join_family.

We re-derived 121 coordinator decisions in the requested basis classes. We would not reach 76 historical decisions: 70 context decisions, five catalogue-containment decisions and one plate-citation decision. The historical context matches lack the identifier required by the frozen protocol. The five containment decisions do not establish individual membership from the cited identities, and the plate reference does not identify its publication. The independent basic-data check found all ten cited entries across the six containment decisions; entry presence does not supply the missing identity tie. The revised table demotes 67 historical context matches to candidates. Its current candidate sets still produce 74 decision objections, principally explicit registration, type, grid, area or trench conflicts. Every family-level reason is retained in coordinator-join-check.json. The independent Dholavira algorithm reproduces all 210 historical decisions with zero differences.

Historical decisions we would not reach, with every row stated explicitly:

PCF-DHV-005 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-006 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-008 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-017 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-020 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-022 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-023 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-035 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-036 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-038 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-039 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-040 [context]: named excavation area conflicts

PCF-DHV-043 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-046 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-047 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-048 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-050 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-051 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-054 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-056 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-059 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-061 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-063 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-064 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-068 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-070 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-071 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-072 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-075 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-077 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-078 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-082 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-083 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-085 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-086 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-089 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-092 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-094 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-100 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-103 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-104 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-107 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-108 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-109 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-110 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-114 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-118 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-120 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-121 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-124 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-125 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-130 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-131 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-132 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-135 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-137 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-138 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-141 [context]: named excavation area conflicts

PCF-DHV-143 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-148 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-DHV-154 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-FRM-001 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-FRM-002 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-FRM-003 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-FRM-004 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-FRM-005 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-KRP-002 [context]: The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-KHR-001 [plate-citation]: The family cites a plate identifier without identifying its publication. The numbered plate cannot be tied uniquely to this source.

PCF-DSL-001 [catalogue-containment]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-DSL-002 [catalogue-containment]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-DSL-003 [catalogue-containment]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-SKT-001 [catalogue-containment]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-SKT-002 [catalogue-containment]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-KNM-001 [context]: object type conflicts

PCF-KNM-002 [context]: object type conflicts; The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

PCF-KNM-003 [context]: object type conflicts; The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.

Current protocol decisions we would not reach:

PCF-DHV-005 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-006 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 98.

PCF-DHV-008 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-017 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 94.

PCF-DHV-020 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 99.

PCF-DHV-022 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-023 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 99.

PCF-DHV-035 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-036 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 99.

PCF-DHV-038 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 101.

PCF-DHV-039 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-040 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 1.

PCF-DHV-043 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-046 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 100.

PCF-DHV-047 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 99.

PCF-DHV-048 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 98.

PCF-DHV-050 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-051 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 94.

PCF-DHV-054 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-056 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 98.

PCF-DHV-059 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-061 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-063 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-064 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-068 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-070 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-071 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-072 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-075 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-077 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-078 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 99.

PCF-DHV-082 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 101.

PCF-DHV-083 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-085 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-086 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-089 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-092 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-094 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-100 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-103 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 100.

PCF-DHV-104 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-107 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 100.

PCF-DHV-108 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-109 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-110 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 99.

PCF-DHV-114 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-118 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-120 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-121 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 99.

PCF-DHV-124 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-125 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 90.

PCF-DHV-130 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 94.

PCF-DHV-131 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-132 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-135 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-137 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-138 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 91.

PCF-DHV-141 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 2.

PCF-DHV-143 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-148 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 95.

PCF-DHV-154 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 94.

PCF-FRM-001 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 3.

PCF-FRM-002 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 2.

PCF-FRM-003 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 2.

PCF-FRM-004 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 2.

PCF-KHR-001 [plate-citation, matched]: The family cites a plate identifier without identifying its publication. The numbered plate cannot be tied uniquely to this source.

PCF-DSL-001 [catalogue-containment, in-baseline-catalogue]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-DSL-002 [catalogue-containment, in-baseline-catalogue]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-DSL-003 [catalogue-containment, in-baseline-catalogue]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-SKT-001 [catalogue-containment, in-baseline-catalogue]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-SKT-002 [catalogue-containment, in-baseline-catalogue]: The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.

PCF-KNM-001 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 1.

PCF-KNM-002 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 1.

PCF-KNM-003 [context, candidate]: The current candidate set contains families with explicit identity or context conflicts. Conflicting candidate families: 1.

The revised locator audit checks 506 primary page locators, 21 secondary references, all named family identifiers and sites, the one-family matched rule, duplicate links and baseline CISI identifiers. It reports zero failures and no empty primary page text. The initial missing baseline identifiers are present in the revised cisi_in_baseline column. Declared site aliases are used.

The content audit found no tracked package file at the time of the Git inventory, so it additionally scanned the working package. It scanned 318 files and 200 windows for each of 48 cited sources, 9,600 windows in total. It found 96 coordinate-level hits: R10 4, R11 2, R16 90. R01–R13 follow the ordered vocabulary in check 6 of CODEX-PROMPT-4.md; R14 is the numeric-unit pattern, R15 an excluded populated data field and R16 a sampled 13-word source-window match. No R14 or R15 hit occurred. The raw hit text is withheld. Every coordinate, including overlapping windows, follows and is also in content-hits.csv.

Hit 1: README.md:77 [R10]; column 138.

Hit 2: README.md:77 [R11]; column 145.

Hit 3: RETROSPECTIVE-CODEX.md:18 [R10]; column 748.

Hit 4: RETROSPECTIVE-CODEX.md:18 [R11]; column 626.

Hit 5: review/match_dholavira.py:6 [R10]; column 54.

Hit 6: review/side_by_side.py:4 [R10]; column 58.

Hit 7: acquisition/bibliography-validation-1a.json:598 [R16]; source khirsara-2017-held PDF 1 window 747.

Hit 8: acquisition/bibliography-validation-1a.json:598 [R16]; source khirsara-2017-held PDF 1 window 229.

Hit 9: acquisition/bibliography-validation-1a.json:598 [R16]; source khirsara-2017-held PDF 1 window 230.

Hit 10: acquisition/bibliography-validation-1a.json:598 [R16]; source khirsara-2017-held PDF 1 window 234.

Hit 11: acquisition/bibliography-validation-1a.json:598 [R16]; source khirsara-2017-held PDF 1 window 236.

Hit 12: acquisition/bibliography-validation-1a.json:598 [R16]; source khirsara-2017-held PDF 1 window 16.

Hit 13: acquisition/processing-summary-1a.json:2325 [R16]; source khirsara-2017-held PDF 1 window 747.

Hit 14: acquisition/processing-summary-1a.json:2325 [R16]; source khirsara-2017-held PDF 1 window 229.

Hit 15: acquisition/processing-summary-1a.json:2325 [R16]; source khirsara-2017-held PDF 1 window 230.

Hit 16: acquisition/processing-summary-1a.json:2325 [R16]; source khirsara-2017-held PDF 1 window 234.

Hit 17: acquisition/processing-summary-1a.json:2325 [R16]; source khirsara-2017-held PDF 1 window 236.

Hit 18: acquisition/processing-summary-1a.json:2325 [R16]; source khirsara-2017-held PDF 1 window 16.

Hit 19: acquisition/source-register-1a.csv:68 [R16]; source khirsara-2017-held PDF 1 window 747.

Hit 20: acquisition/source-register-1a.csv:68 [R16]; source khirsara-2017-held PDF 1 window 229.

Hit 21: acquisition/source-register-1a.csv:68 [R16]; source khirsara-2017-held PDF 1 window 230.

Hit 22: acquisition/source-register-1a.csv:68 [R16]; source khirsara-2017-held PDF 1 window 234.

Hit 23: acquisition/source-register-1a.csv:68 [R16]; source khirsara-2017-held PDF 1 window 236.

Hit 24: acquisition/source-register-1a.csv:68 [R16]; source khirsara-2017-held PDF 1 window 16.

Hit 25: matching/site-counts.csv:5 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 26: matching/site-counts.csv:5 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 27: matching/site-counts.csv:5 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 28: matching/site-counts.csv:8 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 29: matching/site-counts.csv:8 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 30: matching/site-counts.csv:8 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 31: matching/site-counts.csv:12 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 32: matching/site-counts.csv:12 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 33: matching/site-counts.csv:12 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 34: matching/site-counts.csv:20 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 35: matching/site-counts.csv:20 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 36: matching/site-counts.csv:20 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 37: matching/site-counts.csv:22 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 38: matching/site-counts.csv:22 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 39: matching/site-counts.csv:22 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 40: matching/site-counts.csv:24 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 41: matching/site-counts.csv:24 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 42: matching/site-counts.csv:24 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 43: matching/site-counts.csv:25 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 44: matching/site-counts.csv:25 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 45: matching/site-counts.csv:25 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 46: matching/site-counts.csv:40 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 47: matching/site-counts.csv:40 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 48: matching/site-counts.csv:40 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 49: matching/site-counts.csv:41 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 50: matching/site-counts.csv:41 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 51: matching/site-counts.csv:41 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 52: matching/site-counts.csv:47 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 53: matching/site-counts.csv:47 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 54: matching/site-counts.csv:47 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 55: matching/site-counts.csv:48 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 56: matching/site-counts.csv:48 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 57: matching/site-counts.csv:48 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 58: matching/site-counts.csv:49 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 59: matching/site-counts.csv:49 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 60: matching/site-counts.csv:49 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 61: matching/site-counts.csv:50 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 62: matching/site-counts.csv:50 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 63: matching/site-counts.csv:50 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 64: matching/site-counts.csv:54 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 65: matching/site-counts.csv:54 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 66: matching/site-counts.csv:54 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 67: matching/site-counts.csv:55 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 68: matching/site-counts.csv:55 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 69: matching/site-counts.csv:55 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 70: matching/site-counts.csv:56 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 71: matching/site-counts.csv:56 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 72: matching/site-counts.csv:56 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 73: matching/site-counts.csv:57 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 74: matching/site-counts.csv:57 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 75: matching/site-counts.csv:57 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 76: matching/site-counts.csv:58 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 77: matching/site-counts.csv:58 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 78: matching/site-counts.csv:58 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 79: matching/site-counts.csv:59 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 80: matching/site-counts.csv:59 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 81: matching/site-counts.csv:59 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 82: matching/site-counts.csv:60 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 83: matching/site-counts.csv:60 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 84: matching/site-counts.csv:60 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 85: matching/site-counts.csv:61 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 86: matching/site-counts.csv:61 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 87: matching/site-counts.csv:61 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 88: matching/site-counts.csv:62 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 89: matching/site-counts.csv:62 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 90: matching/site-counts.csv:62 [R16]; source farmana-2006-08 PDF 729 window 278.

Hit 91: matching/source-register.csv:181 [R16]; source khirsara-2017-held PDF 1 window 747.

Hit 92: matching/source-register.csv:181 [R16]; source khirsara-2017-held PDF 1 window 229.

Hit 93: matching/source-register.csv:181 [R16]; source khirsara-2017-held PDF 1 window 230.

Hit 94: matching/source-register.csv:181 [R16]; source khirsara-2017-held PDF 1 window 234.

Hit 95: matching/source-register.csv:181 [R16]; source khirsara-2017-held PDF 1 window 236.

Hit 96: matching/source-register.csv:181 [R16]; source khirsara-2017-held PDF 1 window 16.

The unnamed-family search covered all 39 rows. Twenty supplied a registration: eight produced 69 registration-shaped occurrences and twelve produced none. Nineteen supplied no registration. The immediate-line review did not establish these broad search hits as object identities; short numbers can be pagination or unrelated references. The result for every family follows; every source, page and matching line is in unnamed-search.csv.

Family 49 (Bhirrana): no registration supplied.

Family 4304 (Dholavira): DHR-6506; not found; occurrence on a page logged read by extraction: no.

Family 4308 (Dholavira): DHR-2217; found (2 occurrences); occurrence on a page logged read by extraction: yes.

Family 4310 (Dholavira): DHR-2617; not found; occurrence on a page logged read by extraction: no.

Family 4312 (Dholavira): DHR-3557; not found; occurrence on a page logged read by extraction: no.

Family 5580 (Dholavira): DHR-2395; not found; occurrence on a page logged read by extraction: no.

Family 5581 (Dholavira): DHR-2394; not found; occurrence on a page logged read by extraction: no.

Family 5583 (Dholavira): DHR-488; found (11 occurrences); occurrence on a page logged read by extraction: yes.

Family 5584 (Dholavira): DHR-3053; not found; occurrence on a page logged read by extraction: no.

Family 154 (Farmana): DK2D909017; not found; occurrence on a page logged read by extraction: no.

Family 155 (Farmana): Q1-921ID509015; not found; occurrence on a page logged read by extraction: no.

Family 1202 (Kanmer): RIHN-Indus project170; found (4 occurrences); occurrence on a page logged read by extraction: yes.

Family 5421 (Kanmer): RIHN-Indus project09-1997; found (1 occurrences); occurrence on a page logged read by extraction: yes.

Family 276 (Karanpura): -160A; found (1 occurrences); occurrence on a page logged read by extraction: yes.

Family 1757 (Karanpura): -135; found (4 occurrences); occurrence on a page logged read by extraction: yes.

Family 5544 (Karanpura): no registration supplied.

Family 5568 (Karanpura): -75; found (9 occurrences); occurrence on a page logged read by extraction: yes.

Family 5569 (Karanpura): -210; found (37 occurrences); occurrence on a page logged read by extraction: yes.

Family 5570 (Karanpura): -160B; not found; occurrence on a page logged read by extraction: no.

Family 5234 (Lakhanjo-daro): no registration supplied.

Family 5235 (Lakhanjo-daro): no registration supplied.

Family 5236 (Lakhanjo-daro): no registration supplied.

Family 5239 (Lakhanjo-daro): no registration supplied.

Family 5241 (Lakhanjo-daro): no registration supplied.

Family 5242 (Lakhanjo-daro): no registration supplied.

Family 5243 (Lakhanjo-daro): no registration supplied.

Family 5244 (Lakhanjo-daro): no registration supplied.

Family 5245 (Lakhanjo-daro): no registration supplied.

Family 5246 (Lakhanjo-daro): no registration supplied.

Family 5247 (Lakhanjo-daro): no registration supplied.

Family 5248 (Lakhanjo-daro): no registration supplied.

Family 5249 (Lakhanjo-daro): LJD2k10:Tr. 31(1) 27; not found; occurrence on a page logged read by extraction: no.

Family 5250 (Lakhanjo-daro): LJD2k10:Tr. 17(1) 8; not found; occurrence on a page logged read by extraction: no.

Family 5253 (Nuhato): no registration supplied.

Family 5254 (Nuhato): no registration supplied.

Family 5255 (Nuhato): NT18/T5/1479; not found; occurrence on a page logged read by extraction: no.

Family 5560 (Rakhigarhi): no registration supplied.

Family 5563 (Rakhigarhi): no registration supplied.

Family 3872 (Rupar): no registration supplied.

An initial display filter exposed nonidentity source fragments in tool output. exposure-incidents.json records the affected display set. This run therefore fails the tool-output exposure restriction, although the saved audit records omit those source fragments. No page images were opened. The service interruption left complete saved records; no download, installation, OCR or render was needed. The original frozen observations remain unchanged.

Outputs are in experiments/2026-10-21-post-catalogue-finds/verification/: blind-assignments.csv, blind-observations-frozen.csv, blind-freeze.json, blind-sample.csv, blind-summary.json, omission-assignments.csv, omission-sample.csv, omission-summary.json, count-check.json, coordinator-join-check.json, catalogue-containment-check.json, dholavira-grid-check.json, historical-join-objections.csv, current-join-objections.csv, locator-check.json, content-check.json, content-hits.csv, unnamed-search.csv, unnamed-summary.json, unnamed-read-status.json, unnamed-line-review.csv, input-revision.json, resume-integrity.json, selftest-4.json, exposure-log.csv, exposure-mechanical.csv, exposure-incidents.json, RETROSPECTIVE.md, VERIFICATION.md, final.md. The initial results are in initial-results-2026-10-21/, the revised inputs in revised-input-2026-10-21/, and the first search endpoint in prior-search-2026-10-21/. Reproduction scripts are in the same verification directory. No list file, frozen protocol or file outside the owned paths was changed by this run.

The reproducible result is the site arithmetic for the recorded snapshot. Acceptance still requires resolving the source inventories and the listed family conflicts. A further source-only review of those exact pages and candidate sets would decide those points.
