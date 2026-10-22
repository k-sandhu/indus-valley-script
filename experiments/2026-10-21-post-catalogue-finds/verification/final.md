We independently checked the frozen revised snapshot of 503 object rows. All 540 cells of sites.csv reproduce, with no count-cell or applied-decision difference. The protocol main count is 10 matched, 272 candidate and 19 absent, with absent bounds 45–291. Accepting the separate context joins gives 77 matched and bounds 45–224. The revised locator audit has no failures. Source verification remains limited by one unresolved omission inventory, unassessed blind fields and the join findings below. We edited only verification outputs; the source list remains unchanged.

The original endpoint and the two coordinator revisions are kept separately. The initial arithmetic reproduced 459 cells: 77 matched, 205 candidate, 19 absent main rows and bounds 45–224. The first saved follow-up audit reproduced 540 cells: 11 matched, 271 candidate, 19 absent and bounds 45–290; accepting its context joins gave 77 matched and bounds 45–224. The second follow-up demotes the Khirsara plate-number join as well. Its four inputs are frozen in input-v2-2026-10-21/. The original count-check.json, coordinator-join-check.json, locator-check.json and content-check.json retain their recorded hashes. Earlier reports and the original omission endpoint are preserved in pre-v2-reports-2026-10-21/.

The blind sample contains 60 of 503 rows, drawn with seed 20261021: N 5, G 9, D 25, P 15, E 1 and F 5. Part E contains only one row. Source-only observations were frozen before comparison, and all 600 comparison slots remain unchanged. They contain 113 disagreements, 198 unassessed fields and 35 inapplicable registration checks. The agreement denominators below include assessed fields only. Exact two-sided Clopper–Pearson 95% intervals describe those comparisons; shared pages make observations dependent, and agreement on unknown values does not establish publication evidence. blind-summary.json also retains conservative rates across all applicable sampled rows.

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

The omission sample contains 40 unique candidate source-page pairs, drawn with seed 20261022. The first endpoint assessed 31 and left nine unresolved. The revisit assesses 39, with zero confirmed omitted objects and a conditional page omission rate of 0/39 (0.0%–9.0%). IAR 2003–04, PDF page 62, remains unresolved: its continuation and seal group cannot be fully enumerated from the permitted identity text. The full-sample observed fraction is bounded by 0–2.5%; its point estimate is unavailable. If the unresolved page is clear, the exact interval is 0.0%–8.8%; if it contains an omission, the rate is 1/40 with interval 0.1%–13.2%. The interval envelope is 0.0%–13.2%. No confirmed omitted-object description can be supplied. Farmana, PDF page 391, seal, is already identified from PDF page 385; the illustration page is a citation gap. No substitute page was drawn.

All 24 applied matched rows, including the uncertain rows outside the main count, identify exactly one family through a unique registration tie with no detected comparable context conflict. The 68 accepted context identities occur only as separate context_join_family values in applied candidate rows, with their own context_join_basis. No candidate set is empty among 307 candidate rows. Historical match columns remain in join-decisions.csv; protocol_local_match supplies their applied status. The independent Dholavira implementation reproduces all 210 historical grid decisions with zero differences.

The first saved coordinator audit recorded 76 historical objections and 74 objections to its then-current protocol decisions. Those records remain unchanged. The revised audit rechecks 121 selected decisions and retains 36 objections to candidate sets containing explicit context or object-class conflicts: PCF-DHV 017, 020, 022–023, 036, 038–040, 043, 046–048, 051, 056, 059, 063, 070–071, 078, 082–083, 103, 107, 110, 118, 121, 130, 132, 135, 141, 143, 148, 154; PCF-KNM 001–003. candidate-conflicts-v2.csv gives every conflicting family and the compared-field reason. The broad check of all candidate rows additionally flags 91 rows outside the selected decision bases: PCF-DHV 013–016, 018, 029, 031–032, 037, 049, 053, 057, 060, 062, 067, 073, 084, 088, 090, 093, 095, 097–098, 101, 106, 111, 113, 115–117, 119, 123, 134, 136, 139, 144–145, 147, 149–153, 155, 157–168, 171–176, 179–180, 182–183, 185–189, 193–199, 202–207; PCF-GNW 001–002; PCF-RGR 003–007. Across both groups, 127 candidate rows have a detected conflict; the pair-level reasons are named excavation area, material or object class. A relative location such as outside an area is not treated as that area's identity.

The five baseline-containment decisions remain independently unconfirmed: PCF-DSL-001, PCF-DSL-002, PCF-DSL-003, PCF-SKT-001 and PCF-SKT-002. The report groups agree in object count and class with the proposed baseline inventory. A documented identity of the complete excavation group could establish containment without pairing individual registrations; the first objection was too categorical on this point. The held catalogue text layer does not recover the relevant site sections, and the basic-data identities alone do not verify that complete-group premise. The Surkotada report registration also differs from both proposed baseline registrations. We therefore do not independently reach those five decisions from the available identity evidence. The Nuhato historical discovery remains supported by its explicit catalogue citation. containment-review-v2.json records this narrower basis for the remaining objections.

The earlier applied objection rows are PCF-DHV 005–006, 008, 017, 020, 022–023, 035–036, 038–040, 043, 046–048, 050–051, 054, 056, 059, 061, 063–064, 068, 070–072, 075, 077–078, 082–083, 085–086, 089, 092, 094, 100, 103–104, 107–110, 114, 118, 120–121, 124–125, 130–132, 135, 137–138, 141, 143, 148, 154; PCF-DSL 001–003; PCF-FRM 001–004; PCF-KHR 001; PCF-KNM 001–003; PCF-SKT 001–002. The earlier historical objections contain those rows and PCF-FRM 005; PCF-KRP 002. Their field-level reasons remain in coordinator-join-check.json and the original objection CSV files.

The revised locator audit checks 506 primary page locators, 21 secondary references, 7496 family memberships, 68 separate context-family memberships and 145 baseline rows. Every primary page has non-empty held text. Every family exists at its explicit local_site_label, each matched row names one family, and no unflagged pair of rows matches the same family. Baseline numbers are checked only in cisi_in_baseline or other_numbers. There are zero locator or identifier failures in both the preserved final first audit and v2.

Git lists 0 tracked files in this package. The supplementary revised working-tree scan covers 362 text artifacts and samples 200 distinct 13-word windows for each of 48 cited sources, 9600 windows total, using seed 20261023. Both the first and revised scans record 96 raw coordinates. The revised classification is 66 numeric-table coincidences, 24 publication-title citations in bibliographic identity metadata and six vocabulary hits in safety wording. These classifications distinguish raw matches from copied object prose; no sampled hit establishes copied object description. There is no numeric-unit or populated excluded-field hit. R01–R13 refer in order to check 6 of CODEX-PROMPT-4.md, R14 is its unit pattern, R15 an excluded populated field and R16 a 13-word match. Every coordinate is retained without its source text. This sampled check does not cover unsampled windows.

The revised content-hit locations are README.md:77, R10, safety wording; README.md:77, R11, safety wording; RETROSPECTIVE-CODEX.md:18, R10, safety wording; RETROSPECTIVE-CODEX.md:18, R11, safety wording; acquisition/bibliography-validation-1a.json:598, R16, publication-title citation ×6; acquisition/processing-summary-1a.json:2325, R16, publication-title citation ×6; acquisition/source-register-1a.csv:68, R16, publication-title citation ×6; matching/site-counts.csv:5, R16, numeric-table coincidence ×3; matching/site-counts.csv:8, R16, numeric-table coincidence ×3; matching/site-counts.csv:12, R16, numeric-table coincidence ×3; matching/site-counts.csv:20, R16, numeric-table coincidence ×3; matching/site-counts.csv:22, R16, numeric-table coincidence ×3; matching/site-counts.csv:24, R16, numeric-table coincidence ×3; matching/site-counts.csv:25, R16, numeric-table coincidence ×3; matching/site-counts.csv:40, R16, numeric-table coincidence ×3; matching/site-counts.csv:41, R16, numeric-table coincidence ×3; matching/site-counts.csv:47, R16, numeric-table coincidence ×3; matching/site-counts.csv:48, R16, numeric-table coincidence ×3; matching/site-counts.csv:49, R16, numeric-table coincidence ×3; matching/site-counts.csv:50, R16, numeric-table coincidence ×3; matching/site-counts.csv:54, R16, numeric-table coincidence ×3; matching/site-counts.csv:55, R16, numeric-table coincidence ×3; matching/site-counts.csv:56, R16, numeric-table coincidence ×3; matching/site-counts.csv:57, R16, numeric-table coincidence ×3; matching/site-counts.csv:58, R16, numeric-table coincidence ×3; matching/site-counts.csv:59, R16, numeric-table coincidence ×3; matching/site-counts.csv:60, R16, numeric-table coincidence ×3; matching/site-counts.csv:61, R16, numeric-table coincidence ×3; matching/site-counts.csv:62, R16, numeric-table coincidence ×3; matching/source-register.csv:181, R16, publication-title citation ×6; review/match_dholavira.py:6, R10, safety wording; review/side_by_side.py:4, R10, safety wording.

The first raw content-hit coordinates are identical to the revised coordinates above. Its original source-window classifications remain preserved; v2 classifies them by numeric or bibliographic use.

The unnamed-family search covers all 39 current rows, including 20 with registrations. V2 corrects punctuation handling in composite identifiers and yields 9 positive family searches with 70 occurrence coordinates, 11 negative searches and 19 rows without a registration. The first endpoint had eight positive family searches and 69 coordinates. The added complete composite registration is family 5255, NT18/T5/1479. Short bare numbers can coincide with pagination or tabular values, so a search occurrence does not establish an omitted physical object. Immediate-line classifications and page-read flags are preserved in unnamed-line-review-v2.csv and unnamed-read-status-v2.json. Negative results cover held text; candidate pages without text are listed per family in unnamed-summary-v2.json.

Registration-shaped occurrences on pages logged read by extraction: 4308 (DHR-2217), 5583 (DHR-488), 1202 (RIHN-Indus project170), 5421 (RIHN-Indus project09-1997), 276 (-160A), 1757 (-135), 5568 (-75), 5569 (-210), 5255 (NT18/T5/1479).

Positive searches confined to pages not logged read by extraction: none.

No occurrence found in the searched held text: 4304 (DHR-6506), 4310 (DHR-2617), 4312 (DHR-3557), 5580 (DHR-2395), 5581 (DHR-2394), 5584 (DHR-3053), 154 (DK2D909017), 155 (Q1-921ID509015), 5570 (-160B), 5249 (LJD2k10:Tr. 31(1) 27), 5250 (LJD2k10:Tr. 17(1) 8). No registration supplied: 49, 5544, 5234, 5235, 5236, 5239, 5241, 5242, 5243, 5244, 5245, 5246, 5247, 5248, 5253, 5254, 5560, 5563, 3872.

The first display filter exposed nonidentity fragments in tool output, and a follow-up vocabulary projection retained quantity words without safely retaining their object. Both failures are recorded in exposure-incidents.json and exposure-incidents-v2.json. The saved reports repeat no such fragment. This verification run cannot support a claim of zero source-content exposure. No page image was opened, no existing complete page text was re-OCRed, and no download or installation was made. Eight previously unrecovered catalogue-preface pages were OCRed to identity projections; each render was deleted as soon as its projection was saved. The contents page recovers the Dlp and Sktd catalogue ranges, but does not supply the excavation-group premise needed for containment. catalogue-locator-access-v2.json records these pages. The revised display projection withholds general source quantities.

All 41 implementation and record-integrity checks pass. The audit parses 216 CSV and JSON artifacts, confirms non-empty held text for 192 required source-page locators, validates the eight new catalogue identity projections, and checks the original endpoint and frozen-protocol hashes. integrity-check-v2.json records the individual files and source-page hashes.

Outputs are under experiments/2026-10-21-post-catalogue-finds/verification/: count-check-v2.json, coordinator-join-check-v2.json, coordinator-objections-v2.csv, candidate-conflicts-v2.csv, dholavira-grid-check-v2.json, containment-review-v2.json, locator-check-v2.json, content-check-v2.json, content-hits-v2.csv, omission-sample.csv, omission-summary.json, omission-revisit-v2.json, unnamed-search-v2.csv, unnamed-summary-v2.json, unnamed-line-review-v2.csv, unnamed-read-status-v2.json, input-manifest-v2.json, integrity-check-v2.json, selftest-v2.json, exposure-log-v2.csv, exposure-incidents-v2.json, catalogue-locator-access-v2.json, VERIFICATION.md, final.md and RETROSPECTIVE.md. Frozen blind outputs remain blind-assignments.csv, blind-observations-frozen.csv, blind-freeze.json, blind-sample.csv and blind-summary.json. Existing initial and revised snapshots remain in initial-results-2026-10-21/, revised-input-2026-10-21/ and prior-search-2026-10-21/. New inputs are in input-v2-2026-10-21/; the preceding reports are in pre-v2-reports-2026-10-21/. New reproduction scripts are verify_v2.py, content_v2.py, finish_v2.py, reports_v2.py, integrity_v2.py and ocr_catalogue_v2.py, with source access records in source-review-access-*-v2.json. The eight catalogue identity projections are under data/raw/2026-10-21-post-catalogue-finds/run4/cisi1-identity-review/.

| Family | Registration | Search result | On a page logged read |
|---|---|---|---|
| 49 | — | no registration supplied | not applicable |
| 4304 | DHR-6506 | not found | no |
| 4308 | DHR-2217 | found | yes |
| 4310 | DHR-2617 | not found | no |
| 4312 | DHR-3557 | not found | no |
| 5580 | DHR-2395 | not found | no |
| 5581 | DHR-2394 | not found | no |
| 5583 | DHR-488 | found | yes |
| 5584 | DHR-3053 | not found | no |
| 154 | DK2D909017 | not found | no |
| 155 | Q1-921ID509015 | not found | no |
| 1202 | RIHN-Indus project170 | found | yes |
| 5421 | RIHN-Indus project09-1997 | found | yes |
| 276 | -160A | found | yes |
| 1757 | -135 | found | yes |
| 5544 | — | no registration supplied | not applicable |
| 5568 | -75 | found | yes |
| 5569 | -210 | found | yes |
| 5570 | -160B | not found | no |
| 5234 | — | no registration supplied | not applicable |
| 5235 | — | no registration supplied | not applicable |
| 5236 | — | no registration supplied | not applicable |
| 5239 | — | no registration supplied | not applicable |
| 5241 | — | no registration supplied | not applicable |
| 5242 | — | no registration supplied | not applicable |
| 5243 | — | no registration supplied | not applicable |
| 5244 | — | no registration supplied | not applicable |
| 5245 | — | no registration supplied | not applicable |
| 5246 | — | no registration supplied | not applicable |
| 5247 | — | no registration supplied | not applicable |
| 5248 | — | no registration supplied | not applicable |
| 5249 | LJD2k10:Tr. 31(1) 27 | not found | no |
| 5250 | LJD2k10:Tr. 17(1) 8 | not found | no |
| 5253 | — | no registration supplied | not applicable |
| 5254 | — | no registration supplied | not applicable |
| 5255 | NT18/T5/1479 | found | yes |
| 5560 | — | no registration supplied | not applicable |
| 5563 | — | no registration supplied | not applicable |
| 3872 | — | no registration supplied | not applicable |

The arithmetic and identifiers reproduce for the recorded snapshot. A complete identity-only inventory of IAR 2003–04 PDF page 62, recoverable catalogue site-section evidence for the five containment decisions, and removal or explanation of the remaining candidate conflicts would decide the outstanding review points.
