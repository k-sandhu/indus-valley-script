# Review of Package L, the pilot object ledger

Reviewer: Claude (Sonnet 5.5), 7 October 2026, after commit 6710c68. Scripts and small outputs are in [review/](review/). Temporary files were deleted, and the raw directory holds only the package's own outputs.

## Verdict

The main results stand. The stated pipeline reproduces the frozen selection and ten result files byte for byte, the 158 checks pass again, and every headline count in README.md and REPORT.md matches the saved outputs except one: the museum dimension gain is three carriers, not two. An independent resolver matched 5,611 of the 6,490 assertion values to their cited source locators with no mismatch, and more than 30 records checked against CISI 1 scan pages, Table 1 of the Lothal chapter, the Harappa Figure 4 caption, Gadd (1932) and saved museum records agree with the ledger wherever it copied a clean source value. The most important problem is the sample design. The 74-slot "stratified" fill visits 313 strata in alphabetical order and stops inside Harappa, so it draws only from Eastern Headwaters, Gujarat/Kutch and Harappa. Lower Indus holds 46% of the 4,104 frame carriers and enters only through 18 museum-joined carriers, and Kalibangan (197 carriers) does not enter. Neither the protocol nor the report states the order. The external group is affected in the same way: four of its five Iranian Plateau carriers lie in Pakistan by the census's own country field, and Susa and Tepe Yahya were skipped. Two of the six README commands fail as written, and two accepted cells (PBM-1's registration and BM-123208's site) contradict sources the package held locally.

## Checked claims

| # | Claim | Evidence | Result | Note |
|---|---|---|---|---|
| 1 | Frozen selection reproduces exactly | `selection-2026-10-07-v1/selection.json`, `review/reproduction-log.json` | confirmed | SHA-256 41fffd57...; the protocol hash stored in it equals the current PROTOCOL.md |
| 2 | Ledger, museum comparisons, source lookups and supplemental manifest replay exactly | `run-2026-10-07-v4/` | confirmed | The decompressed raw register is also identical |
| 3 | Six analysis files replay exactly | `analysis-2026-10-07-v3/` | confirmed | `analysis-manifest.json` differs only through the embedded hash of `build-manifest.json`, which records output paths |
| 4 | 158 checks pass | `checks-2026-10-07-v4/checks.json` | confirmed | The 158 are 37 distinct checks; 48 are per-row Lothal comparisons and 20 are input hashes |
| 5 | README commands run as written | README, rerun section | discrepancy | `analyze.py` and `check_pilot.py` reject `--lothal-assertions` (exit code 2) |
| 6 | 200 carriers, 180 corpus-linked, 20 catalogue-only, 34 sites, 8 regions | `analysis-2026-10-07-v3/summary.json` | confirmed | 34 counts export site labels. Girsu and Tello are one site in the census rows, and Dilmun, Luristan and Ornach area are regional or area labels |
| 7 | 256 Lipi faces, 3 Mayig, 259 surfaces, 6,490 assertions, 430 measurements, 356 rights, 97 images (22 + 26 + 48 + 1) | same | confirmed | |
| 8 | Assertion values equal their cited locators | `ledger-public.json`, `review/assertion-check.json` | confirmed | 5,611 resolved and equal, 228 present but not compared, 651 not resolved by the script (rights rules, Harappa frame and caption ledgers, join evidence, selection file). The 22 tablet locators were checked programmatically (row 20) and six museum joins by eye (record table) |
| 9 | Matched gains: 26 accessions, 22 unit/item pairs, 62 intervals | `completeness.json` | confirmed | Interval widths: median 550 years, 35 of 62 at least 500 years |
| 10 | Dimensions for two more carriers | `completeness.json`, `museum-comparisons.json` | discrepancy | H-221's museum string "0.8x1.8 cms." is not parsed ("cms." is outside the unit pattern) and the export has no H-221 dimension, so the gain is three and the pilot count 130. Seven of the 26 joined museum records carry a dimension string the parser skips (labelled axes, "cms.", inches) |
| 11 | Completeness table, 16 fields in three columns | `completeness.json` | confirmed | "Excavation identifier 149" includes 23 values that are not registrations (accepted-view values, below) |
| 12 | 26 confirmed museum joins (16/5/3/1/1 by method), 22 caption joins, 3 Mayig links, 51 in all | `join-report.json` | confirmed | |
| 13 | 34 candidate links, 9 museum records, 10 carriers, none in accepted fields | `join-report.json`, ledger | confirmed | 36 candidate assertions (34 plus 2 for BM-123208); no accepted cell cites one |
| 14 | Museum comparisons on 21 pairs, 5 unadjudicated | `disagreements.json` | confirmed | Every sub-count in REPORT agrees |
| 15 | Distinct-value groups 55, 52, 46, 22, 22, 22, 18 | same | confirmed | |
| 16 | 134 questions on 82 carriers | `review-queue.json` | confirmed | By reason: 34 + 22 + 22 + 20 + 13 + 9 + 6 + 5 + 1 + 1 + 1 |
| 17 | 1,095 lookups, mean 5.475, median 4, range 3 to 12 | `source-lookups.json` | confirmed | 283 are rights-rule rows and 20 are the ledger's own selection file; without them 792, mean 3.96, median 3 |
| 18 | Selection: 22, 1, 8, 8, 24, 25, 20, 18, 74 | `selection.json` | confirmed | Sums to 200 with 200 unique keys |
| 19 | Required strata present | same | confirmed as counted | 26 museum-joined; 3A, 3B and 3C picks reproduce under my own re-ranking; 22 tablets; 25 joined plus 20 catalogue-only Lothal sealings; 18 external. The quality of the external and fill groups is in the sampling section |
| 20 | 22 tablet registrations, units and items | `ledger-public.json` | confirmed | 22 of 22 equal the Figure 4 caption ledger, and the export's "Figure 12.NN" suffix equals the specimen number in all 22 |
| 21 | FILES.json lists every created path | `FILES.json` | confirmed | 154 owned and 22 raw files, hashes match, nothing unlisted |
| 22 | Failed first build preserved | `validation-2026-10-07-v1.json` | confirmed | 68 identifier-edition errors |
| 23 | Protocol preceded outcomes | file times | confirmed | PROTOCOL.md last written 10:03:25, selection.json 10:04:48, first register 10:12:57; amendments follow and are labelled Exploratory. `select_pilot.py` dates from 10:05:10, after the selection, and the retrospective says it was renamed; my rerun reproduces the selection |

## Reproduction log

Run from the repository root with Python 3.13.5 and jsonschema 4.26.0 (the versions in `environment.json`), writing into `review/` and a temporary raw subdirectory. Total compute was under two minutes.

| Step | Result |
|---|---|
| `select_pilot.py` | identical `selection.json` and exclusion list |
| `build.py` with the README arguments | identical ledger, comparisons, lookups, supplemental manifest and decompressed full register |
| `analyze.py` and `check_pilot.py` with the README arguments | argparse error, exit 2 |
| the same two without `--lothal-assertions` | six analysis files identical; 158 of 158 checks pass, with results equal to the package's `checks.json` |
| `validate.py --scan-dir` over the whole package directory | no errors on 96 JSON files, including the files I added |
| `tools/review_prose.py --no-write` | no flags in the package Markdown files |

The reviewer scripts run from the repository root without arguments and read local-only inputs under `data/`. `review/verify_selection.py` re-derives the selection and analyses the fill, `review/verify_assertions.py` resolves assertion locators, `review/negative_tests.py` applies the validator mutations and sequence fixtures, `review/scan_tracked_files.py` scans for sequences and copied prose, and `review/verify_helsinki_interface.py` tests the importer on Package M's staged rows. Each writes one JSON file into `review/`, and `negative_tests.py` also writes the five small slices.

## Records checked against sources

| Record | Source checked | Result |
|---|---|---|
| OL-0001 H-2218 | Meadow and Kenoyer 2000, PDF 16, author p. 15, book p. 335 (caption, specimen 11, H97-3319/8040-13); drawing PDF 15; deposition text PDF 14 | registration, unit 8040, item 13 and pages confirmed. "late Period 3B" is the ledger's paraphrase of a deposit after wall 296 and before Period 3C. The accepted interval is 2600-1900 BCE, from the export label "Period 3", while the accepted label is "late Period 3B". The export string is "H97-3319Figure 12.11", which REPORT shortens to "H97-3319" |
| OL-0023 H-1688 | Lipi row; Kenoyer and Meadow 2010 (CISI 3.1 introduction), printed p. liii | label "Period 3A" confirmed by the export. The introduction describes H-1688 as a broken steatite seal from street deposits on Mound E dated to about 2600 BC. The ledger cites that volume only for Table 1, so its review question can be narrowed |
| OL-0094 L-174 | Frenez and Tosi 2005, Table 1 (PDF 32, printed 94), prose (PDF 18, printed 80), Figure 7 (PDF 40, printed 102); CISI 1 printed pp. 279 and 375 | table 1, prose 2 and a Figure 7 view of L-174 confirmed. CISI 1's plate shows two square impressions, and its corrigenda place L-174 A among the tags with several impressions. Three witnesses favour two, yet the accepted cell holds the table's 1 |
| OL-0109 BM-123208 | Gadd 1932, printed pp. 13-14 (no. 16) | Gadd gives BM 123208, excavation number U. 17649, found at Ur in 1931-32 in a tomb-shaft filling. The accepted `site` is "Dilmun"; the Ur findspot is a candidate assertion, and `reported_production_place` is empty although a candidate "Dilmun" assertion exists |
| OL-0045 M-197 | CISI 1 printed p. 367; saved Indian Museum record | the data row lists museum number A 7703, matching accession 10376/A7703; "1.9X1X1.9 centimeter" becomes 19, 10, 19 mm. The 3000-1500 BCE interval comes from the museum's culture string |
| OL-0055 M-155, OL-0049 M-167 | CISI 1 printed p. 367 | museum numbers A 7704 and NS 6048 / A 7808 match the joined records |
| OL-0053 L-143, OL-0088 L-144 | CISI 1 printed p. 373; Table 1 | the data rows give 1878 / SRG 1165 and 6742 / SRG 1174, which match museum accessions 1878/1165 and 6742/1174; the Table 1 rows agree |
| OL-0128 B-25 | CISI 1 printed p. 375; saved museum record | BNL1 170/84 matches; "3.7x2.0x0.7cm" becomes 37, 20, 7 mm |
| OL-0056 H-221 | saved museum record | dimension not parsed (row 10) |
| OL-0089 L-160, OL-0103 L-175, OL-0106 L-215 | Table 1 images (PDF 31, 32); CISI 1 plates, printed pp. 276, 279, 289 | table cells agree and the plates exist. The page header over L-174 to L-176 labels them geometric designs without iconography |
| all 20 catalogue-only carriers | Table 1 images; Lipi and Mayig | all 20 rows agree with the CSV, none occurs in either export, and CISI 1 page headers locate each entry |
| OL-0166 L-141 | Table 1 (1 impression); CISI 1 corrigenda for p. 272 | the corrigendum relabels the two photographs as (1) and (2) of L-141 A, which by the catalogue's captions for other sealings (for example L-213 A 1-2) marks two impressions where the table gives one. The ledger does not flag it |
| OL-0169 PBM-1 | CISI 1 printed p. 375 data row; census correction B3-V6-016 | the row gives excavation number PBM 024 and holder KC. The accepted identifier is the export's "PMB 024", a transposition; the holder is not recorded, and the correction is attached only as a site overlay |
| OL-0136 B-24 | Lipi row | the accepted excavation identifier is "-Figure 4.4", a figure citation with no registration |
| OL-0120 MQ-11, OL-0114 Girsu, OL-0118 Tello | census `d-finds-abroad/site-rows.json` | Miri Qalat is Pakistan (`south_asian_cross_reference`); Girsu/Tello is one site |

## Source checks

| Source | Check | Result |
|---|---|---|
| Joshi and Parpola, CISI 1 (1987) | title page, data tables and corrigenda in the local scan | title, year and series match. The register lists Joshi and Parpola as authors, and the title page names them as editors |
| Meadow and Kenoyer, "The 'Tiny Steatite Seals'..." (2000) | local PDF | title, authors and volume match; the pagination is internally consistent (author p. 15 is book p. 335) |
| Kenoyer and Meadow, "Inscribed Objects from Harappa Excavations 1986-2007" (2010) | local PDF, Table 1 at printed p. xlv | period limits match `period_mapping.json` |
| Frenez and Tosi, "The Lothal Sealings..." (2005) | local PDF; Zenodo record 5514283 | the register keeps the printed "Circuits" title, while the Zenodo deposit says "networks". The record states CC BY 4.0, which the ledger's rights rows for this source do not record |
| Gadd (1932) | local OCR, printed pp. 13-14 | supports the BM-123208 row |
| Koskenniemi and Parpola (1979) | local provenance manifest | title, authors, series and CC BY 4.0 match. The handle redirects to a page that returned an access-denied notice, so the online record was not reopened |
| Koskenniemi and Parpola (1980) | local provenance manifest | two authors (the frozen protocol names three, which the retrospective notes); licence unverified |
| mayig/indus-valley-script-corpus | GitHub licence file and commit API | MIT licence with a 2024 copyright to Michael Carlson; the pinned commit exists |
| yajnadevam/lipi | GitHub | the pinned commit exists and no licence file is visible, which supports keeping its sequences local. The repository frames its transliterations and translations as following a claimed 2022 decipherment, a framing the ledger does not adopt |
| saved museum records | `focused-records.json` | 152 compared values match, and the remaining museum assertions are parsed fields |

`sources.json` marks no source as snippet-only, which fits a package that ran no searches.

## Method and scope findings

**Sampling.** The frozen fill reproduces exactly when strata are visited in alphabetical order and already-selected carriers are skipped (`review/selection-check.json`). The frame has 313 strata and the fill has 74 slots, so it reached only the first 90 strata. It drew 17 carriers from Eastern Headwaters, 31 from Gujarat/Kutch (18 at Lothal) and 26 from Harappa. Mohenjo-daro has 1,745 frame carriers and 13 selected, all through the museum group. Kalibangan has 197 and none, Nausharo 38 and none, and 26 of the 60 frame sites are absent. A hash-ordered visit, which the protocol equally permits, would draw 33 Lower Indus carriers and cover 24 sites in the fill. The order changes the tables. On the 180 matched carriers the export's own presence rates are 15.6% for room/grid, 52.2% for area and 38.3% for period label, against 39.7%, 73.9% and 50.7% over all 4,695 export families. Lower Indus families show 58.7% room/grid in the export and Gujarat/Kutch families 0.7%, and the pilot's mix leans toward the latter. The frame also excludes 591 families with no catalogue base (Dholavira 228, Kanmer 8, Farmana 7 and others), so no Kanmer object is in the pilot and the Kanmer frame was not exercised. The package uses no resampling, and its counts carry their bases (200 pilot, 180 matched, 21 adjudicated museum pairs, 93 Table 1 rows).

**External group.** The pools hold 17 Gulf, 11 Mesopotamian, 11 Iranian Plateau and 3 Central Asian families. Round-robin by site name took the first five sites alphabetically in each region. Skipped sites were Karzakan, Qala'at al-Bahrain, Ra's al-Junayz, Saar and Salut (Gulf), Ur (Mesopotamia), and Sibri, Susa and Tepe Yahya (Iranian Plateau). Among the five Iranian Plateau carriers only Luristan, a regional label, is Iranian. BM-123208 is a Gulf-type seal excavated at Ur.

**Accepted-view values.** The export attaches figure or plate citations to excavation numbers. Forty-two carriers have such strings (35 Harappa, 5 Chanhu-daro, 1 Banawali, 1 Lothal); 20 accepted cells still hold one, and five begin with a hyphen, including a lot number ("-Lot 22021") that the protocol assigns to a separate field. Of the 149 present identifiers, 126 are registrations. The identifiers table stores 42 distinct contaminated strings as confirmed `excavation_registration` aliases, which cannot serve as join keys. The tablets' accepted label and interval differ in scope (record table, first row). For the 20 catalogue-only carriers the `region` assertion cites the ledger's own selection file, and `object_type` and `material` come from the carrier class of the source table; all three carry confidence "source-reported", and the schema has no level for derived values.

**Census corrections.** The brief asks that corrections affecting a selected object be applied. The 25 overlays are attached to every selected object at the named sites, and apart from B3-V6-050 and B3-V6-035 their action text is "site_scope_qualification_preserved; no_object_field_inferred". B3-V6-016 does affect PBM-1 (record table). CISI 1's holder column gives KM, KC or DAH (?) for KRS-1, KRS-2, PBM-1 and RGR-1, whose `holding` is empty. The package read no CISI 1 pages itself.

**Catalogue-only entries.** The 25 absent Lothal keys in L124-L216 all appear in the 93-row Table 1. CISI 1 page headers for printed pp. 279 to 281 label the impressions as geometric designs or as lacking iconography, and Frenez and Tosi describe L-173 to L-175 as geometric patterns, so absence from an inscription export may reflect content. The review queue asks the eligibility question for all 20 without using this evidence.

**Missingness.** All 5,448 empty cells among 10,047 carry a reason, with 12 distinct reasons. The protocol's "not applicable" is never used, so `impression_count`, `context_code` and `physical_contact_category` read "not recorded" for 152 carriers that have no Table 1 row.

**Rights and scope.** No run of three or more signs from either export occurs in the 169 text files of the package directory (35,864 runs indexed in both directions, in hyphen, comma, space, plus and array forms). The commonest runs of three-digit numbers in those files are page ranges and table counts (one page pair alone occurs 161 times), and no plus-delimited two-sign text code occurs. The only overlaps of eight words with a source text are three bibliographic titles in the `sources` table. No claim of decipherment, sound or meaning, or novelty appears. The file name `ledger-public.json` and the phrase "public-safe layer" refer to sequences only. The Lipi export has no licence, and the file holds record-level Lipi metadata, which REDISTRIBUTION.md says needs a documented basis before a public release.

## Validator and schema

`schema.json` regenerates byte for byte from `schema.py`. Each mutation below was applied to the full ledger, whose baseline has no errors (`review/negative-tests-results.json`). Small bad examples are in `review/negative-tests/`.

| Category | Caught | Missed |
|---|---|---|
| Referential | context pointing to a missing object; identifier or cell citing a missing assertion; transcription on another object's surface; relationship to a missing source; missing locator file | a measurement or identifier row whose value differs from its assertion; a locator naming a record absent from an existing file; a relationship relabelled confirmed over a candidate-confidence assertion |
| Unit | unit outside the enum, negative value, NaN, mass unit on a length | a row unit changed from mm to cm; inches inside an accepted cell and its assertion; a seal 12.5 m wide |
| Interval | reversed, string endpoints, zero endpoint, extra key | an interval inconsistent with the period label; 50000-40000 BCE; a museum range re-sourced to the HARP table |
| Sequence in a tracked file (10 JSON fixtures) | a `sign_sequence` key, a three-token string under a new key, a two-code string array, three space-separated P-codes | a two-token string, a plus-delimited two-sign code, a sequence inside a sentence, an integer array, a comma-separated string, grapheme dictionaries under a new key |

The directory scan reads only `*.json` files, so the same sequences in CSV, Markdown or JSONL files pass unseen, as does any file named `schema.json`. Texts of one or two signs make up 39% of export faces (two is the commonest length) and 63 of the 200 pilot carriers. The schema lists the units g and kg but no dimension that can use them, so a mass such as the 15 g of the Kanmer pendants cannot be recorded.

## Helsinki 1979 import interface

Package M's staged rows now exist (`experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl`, 11,369 rows, written after this package's commit). Results are in `review/helsinki-interface-check.json`.

- All rows carry the twelve required fields, integer pages and a valid CC BY rights block. With an invented crosswalk row the importer accepts a row, and `build.py --helsinki-layer` produces a ledger that passes validation and holds no payload keys.
- 944 rows have no text number, which the schema rejects as it should. 65 rows have a letter suffix (57 values such as "669S" and "2Z"), and the numeric-only rule rejects them even with a complete crosswalk.
- 2,616 of 4,472 text numbers occur more than once, and Package M gives each occurrence its own `segment_id`. A concordance row keyed by text number, as a concordance supplies it, does not match; it must be repeated for every occurrence.
- The ledger has one surface per transcription (259 of 259). The 20 catalogue-only carriers have none, and the importer demands an existing surface, so no 1979 text can be added to the carriers where it would add most.
- A crosswalk target must name the ledger's scheme exactly. Corpus-linked carriers hold CISI strings under `reported_catalogue_reference` and the 20 catalogue-only carriers under `CISI`; "CISI" with "H-2218", or "H 2218" under the right scheme, does not resolve. HELSINKI-INTERFACE.md lists no schemes.
- Package M's crosswalk format (`source_edition`, `target_scheme`, `surface_relation`, `rights_status`) differs from this package's (`edition_id`, a `target_identifier` object, `surface_id`, `surface_review_status`, `relation`, `status`), and nothing converts between them.
- The brief asks which concordance joins a 1979 number to an object. CISI 1, printed p. 365, says column 2 of its basic-data table gives each object's Finnish Concordance number (M-197 is 2371 on p. 367). Package M's row numbered 2371 has 2 units and one of its two rows numbered 1187 has 3, equal to the Lipi lengths of M-197 and M-155; the row numbered 1297 has 5 units against 4 for M-167. This is a lead to test, and the interface document does not mention it.

## Writing and boundaries

The scanner reports no flags. Five apostrophes were replaced by question marks (README line 15, RETROSPECTIVE line 25, and three in REPORT on lines 38 and 62). Most REPORT paragraphs end with three to six links and field paths, which interrupts the reading, and the fill order is described nowhere.

`git status --porcelain` at the end lists three untracked paths: `REVIEW.md` and `review/` in this package, and `experiments/2026-10-07-helsinki1979-digitization/review/reviewer-check/`, which belongs to another contributor. No tracked or staged file differs from HEAD, and commit 6710c68 touches only this package's directory. Two stray `grep.exe.stackdump` files that my own shell commands created in the repository root were deleted.

## Required fixes, in order

1. State the fill's visiting order and coverage in REPORT.md: strata reached, regions and sites unreached, and the field-rate comparison above. If a regionally balanced pilot is wanted, add a second dated selection with a hash-ordered visit and keep the frozen one.
2. Report the external group by site and country, not by export region. Reselect or relabel the Iranian Plateau group, merge Girsu and Tello, and give the site count with its alias caveat.
3. Correct README: drop `--lothal-assertions` from the `analyze.py` and `check_pilot.py` lines, and list the local-only `data/` inputs the rerun needs.
4. Parse "cms.", the labelled forms and inches, or state the parser's scope, and update the dimension gain to three.
5. Split figure and plate citations from excavation identifiers for the 42 affected carriers, keep lot numbers in a lot field, and restate the 149 as 126 registrations.
6. Apply B3-V6-016 to OL-0169 (PBM 024, holder KC, with "PMB 024" kept as a variant). For OL-0109, put Gadd's Ur findspot in the accepted view and move Dilmun to production place, as the census row does, or annotate the `site` cell.
7. Record the CISI 1 corrigenda and plate evidence for L-141 and L-174, and check the other Lothal carriers' captions for the same pattern.
8. Describe the sequence guard as a heuristic and extend it to one- and two-sign texts, other delimiters and non-JSON files. Add row-to-assertion equality and cell-level unit checks.
9. Before the first real 1979 import, accept string text numbers and text-level crosswalk rows, allow a new surface, list the target schemes, and reconcile the two crosswalk formats.
10. Replace the five question marks.

## Optional improvements

- Cite Kenoyer and Meadow 2010, printed p. liii, for H-1688.
- Replace the section pointers with plate pages. The headers give L-135 p. 270, L-151 and L-152 p. 274, L-154 to L-156 p. 275, L-158 to L-160 p. 276, L-171 p. 278, L-174 and L-175 p. 279, L-185 and L-186 p. 281, L-194 and L-195 p. 284, L-203 p. 285, L-209 p. 287, and L-214 and L-215 p. 289.
- Transcribe CISI 1's data columns (Finnish Concordance number, excavation number, holder, photograph source) for the CISI 1 carriers.
- Add a "not applicable" reason and a "derived" confidence level, record the periodization scheme beside each period label, and derive the tablets' interval from the caption.
- Count lookups without rights-rule rows, record the Zenodo CC BY 4.0 licence for the Lothal chapter, label the CISI 1 editors as editors, and add a mass dimension.
- Replace the three replay directories (about 19 MB of ledger copies that equal their originals) with hash records.
