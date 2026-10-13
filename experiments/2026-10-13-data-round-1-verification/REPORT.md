# Data round 1 independent verification

13 October 2026. **Museum package: ready after the rights redactions, harvest-flag corrections and named report fixes below, subject to the separate join review. CISI 2 pilot: ready after removing catalogue values from public files and correcting the two report statements below. Its final-builder parser stage remains unverified because the instructions both require the builder and prohibit its internal parser call.** Neither package is ready to commit as found.

The audit found 19 issues: 9 blocking publication findings, 6 should-fix findings and 4 minor findings. The principal agreement and object-coverage totals reproduce. The combined museum-number count is **541 of 4,695 families (11.52%)**, including bracketed readings. Under the pilot's conservative rule that the whole museum cell contains no bracket, it is **518 (11.03%)**. A separate number-level rule gives 533 (11.35%). The definitions and overlaps are below.

This is an independent computation and payload review by the Codex primary agent, identified in the harness instructions as GPT-6. The request named GPT-6.1-Sol; the runtime did not expose an independently verifiable model identifier. Python was 3.13.5. The museum reviewer's `verification/` directory was excluded from copying, reading, mutation and hash comparison. No join was checked again by eye, and no network request or Git mutation was made.

## Findings, ordered by severity

### F01: blocking: museum-open-access

File: [experiments/2026-10-13-museum-open-access/joins/decisions.py](../../experiments/2026-10-13-museum-open-access/joins/decisions.py), lines 70, 117, 119 and 134; evidence strings.

The evidence strings reproduce restricted museum record prose. Exact description fragments match the Indian Museum records and the National Museum record 1713 DHR; line 70 copies V&A record titles. Source fields: description and title.

Recommended fix: Replace the copied descriptions and titles with project-written classifications and locators. For 1713 DHR record inscription_status=uninscribed and the local source locator. For the two Indian Museum records use material, object class and face-count flags. For the V&A impression use originality=modern-impression and its relation to IS.8:1-1951. Preserve the starting witness locally and rebuild both join CSVs.

### F02: blocking: museum-open-access

File: [experiments/2026-10-13-museum-open-access/joins/join-table.csv](../../experiments/2026-10-13-museum-open-access/joins/join-table.csv), evidence column; lines 20, 54, 56 and 63.

Copied description and title text from decisions.py propagates into the proposed public join table.

Recommended fix: After redacting decisions.py, regenerate this CSV from the corrected decisions and confirm the evidence cells contain classifications and source locators only. Keep the original table locally.

### F03: blocking: museum-open-access

File: [experiments/2026-10-13-museum-open-access/joins/q1019-decisions.csv](../../experiments/2026-10-13-museum-open-access/joins/q1019-decisions.csv), evidence column; lines 14, 16 and 23.

Copied Indian Museum and National Museum description text propagates into the Q-1019 table.

Recommended fix: Regenerate this CSV from the redacted decisions.py and retain only project-written classifications and locators in evidence.

### F04: blocking: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/PROTOCOL.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/PROTOCOL.md), line 21, the two numeric code examples.

The first example reproduces the excavation reading of M-626. The second is an unattributed museum-registration example; it does not match a pilot value exactly and its apparent source above the pilot block was not authenticated. The tracked protocol therefore fails its stated rule that transcribed values stay local.

Recommended fix: Preserve the frozen protocol and its original hash locally. Publish a clearly labelled redacted protocol with the two examples replaced by DK-C nnnn and L, P-nnnn. Record a separate public-file hash and retain the original freeze hash as identifying the local original.

### F05: blocking: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/join.py](../../experiments/2026-10-13-cisi2-basic-data-pilot/join.py), docstrings at lines 56-57, 77 and 92-93.

The docstring examples contain a museum accession from M-631, an older-export alias of a registration from M-626, a bracketed FC reading from M-655, and FC numbers from M-625 and M-636. These are source values, although they occur only in examples.

Recommended fix: Replace the website_pairs, expand and fc_tails docstring examples with explanations using variable names or n placeholders. Preserve the original file locally. No change to the executable comparison logic is needed for this finding.

### F06: blocking: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/schema.json](../../experiments/2026-10-13-cisi2-basic-data-pilot/schema.json), transcription_conventions.uncertain_character.

The whole-cell alternative example contains the two excavation readings recorded in the M-634 recheck. One is the final CISI reading and the other comes from the local corpus.

Recommended fix: Replace the numeric whole-cell example with [candidate_a/candidate_b] and explain that alternatives can span several characters. Preserve the source-derived example only in the local recheck record.

### F07: blocking: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/README.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md), line 11, observed FC range endpoints.

The result paragraph prints observed FC number endpoints for the appended-tail group and the later excavation group. Those endpoints are transcribed CISI values rather than counts.

Recommended fix: Remove the observed FC endpoints. Retain the counts 182, 32 and 7 and explain the suffix rule using its algorithmic threshold or excavation-series labels. Keep the exact group bounds local.

### F08: blocking: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/DATA-UPDATE.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/DATA-UPDATE.md), line 51, observed FC range endpoints.

The proposed DATA.md paragraph includes observed FC number endpoints that the package promises to keep local.

Recommended fix: Delete the observed FC endpoints from this proposal. Retain the count 182 and the description of removing the first FC digit.

### F09: blocking: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/question-updates.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/question-updates.md), line 9, observed FC range endpoints.

The proposed Q-1006 note includes observed FC number endpoints that would propagate restricted catalogue values into the knowledge layer.

Recommended fix: Remove the observed endpoints before integrating the note. Retain the count 182 and the suffix rule.

### F10: should-fix: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/README.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md), excavation comparison table, lines 91-92.

The DK subarea and dropped-prefix counts are 9 and 3, rather than 8 and 4. The 12-family combined count is correct. Independent normalization identifies nine DK-B/DK-C additions and three removals of DK-.

Recommended fix: Change the subarea row to 9 and the dropped-DK-prefix row to 3. Source: this verification package independent-counts.json, cisi2.excavation_comparison_table; local independent-excavation-detail.json lists the families and comparisons.

### F11: should-fix: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/README.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md), line 11, holding-institution gain sentence.

The sentence says all 283 objects gain a holding institution. The package before table already counts 74, so the gain is 209. All 283 gain an FC number.

Recommended fix: Replace the sentence with: The block supplies a holding institution for all 283 joined objects, adding that field to 209, and adds an FC number to all 283. Source: coverage.json coverage_gain and the independently recomputed before/after counts.

### F12: should-fix: museum-open-access

File: [experiments/2026-10-13-museum-open-access/harvest/met-records.json](../../experiments/2026-10-13-museum-open-access/harvest/met-records.json), records 49.40.6 and 49.40.10; indus_attributed and in_scope.

Both later-period objects are flagged as Indus and in scope because their geographic label contains Indus. Their CC0 records date them to the second century CE and first century BCE. They are excluded by the report but remain included in the machine-readable flags.

Recommended fix: Set indus_attributed=false and in_scope=false for these two records with an explicit later-period exclusion. Save the manual override in a reproducible classification record or revise the classifier to account for the dates, then rebuild the derived harvest counts.

### F13: should-fix: museum-open-access

File: [experiments/2026-10-13-museum-open-access/harvest/vam-records.json](../../experiments/2026-10-13-museum-open-access/harvest/vam-records.json), IS.8:2-1951 originality; IS.8:1-1951 object_class.

The modern impression is flagged original, and the original seal is classified sealing-or-impression. The decisions table and README give the intended distinctions, but the harvest flags do not carry them.

Recommended fix: Set IS.8:2-1951 originality=modern-impression and IS.8:1-1951 object_class=seal. Store and apply these manual overrides before calculating originals and casts/impressions.

### F14: should-fix: museum-open-access

File: [experiments/2026-10-13-museum-open-access/harvest/aic-records.json](../../experiments/2026-10-13-museum-open-access/harvest/aic-records.json), records 1920.711 and 1920.712; indus_attributed.

The two later coins are flagged Indus-attributed although the harvest summary and report say zero Indus objects. Their geographic relation to the Indus region does not establish Harappan attribution.

Recommended fix: Set indus_attributed=false for both coins and preserve the later-period exclusion in the classification record. Derive the zero count from those reviewed flags.

### F15: should-fix: museum-open-access

File: [experiments/2026-10-13-museum-open-access/harvest/summary.csv](../../experiments/2026-10-13-museum-open-access/harvest/summary.csv), V&A row, indus_attributed_records; harvest_summary.py line 60.

The summary hard-codes 4 Indus-attributed records, but vam-records.json has 12 flags set to true. The two-original/one-impression result is a separate count and is supported by the three decided records.

Recommended fix: Derive indus_attributed_records from the reviewed record flags. With the frozen flags the count is 12. If those geographic matches need exclusions, record the overrides first and publish the resulting count consistently in the JSON and CSV.

### F16: minor: museum-open-access

File: [experiments/2026-10-13-museum-open-access/coverage_museum.py](../../experiments/2026-10-13-museum-open-access/coverage_museum.py), group() and coverage/museum-coverage.json by_type.

The type grouping misses family 609 with a mixed-case pottery code. It reports pottery denominators of 629 and other denominators of 188, while the inventory gives 630 and 187. The overall museum-number totals are unaffected.

Recommended fix: Use the inventory type_group() rule, including whitespace/case normalization and the POST: alias. Regenerate the by-type fractions with pottery denominators 630 and other denominators 187; the numerators stay 5/6/8 and 2/3/3 across the three stages.

### F17: minor: museum-open-access

File: [experiments/2026-10-13-museum-open-access/README.md](../../experiments/2026-10-13-museum-open-access/README.md), line 20.

The draft still contains the precision-paragraph placeholder.

Recommended fix: Replace the placeholder with the separate museum reviewer's final checked numerator, denominator and disposition counts after that review is finished. Do not infer a precision score from this numerical audit.

### F18: minor: cisi2-basic-data-pilot

File: [experiments/2026-10-13-cisi2-basic-data-pilot/README.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md), line 27; PROCEDURE.md line 7; manifest-additions.json changed[cisi-2].replace.notes.

The stated text-layer page-number count of 412 was not reproduced. The retained PDF has 418 expected page numbers in corner headers and 29 headers unverified by this check, rather than 35. The source SHA256 matches the package.

Recommended fix: Replace the OCR header count with 418 and the unreadable-header count with 29, naming the counting rule: exact expected printed-page token in the top 5 percent and outer 16 percent of page width. Keep full catalogue completeness separate from the header count; inspect the remaining 29 pages before claiming this check proves every page is present.

### F19: minor: museum-open-access

File: [experiments/2026-10-13-museum-open-access/registry-entry.json](../../experiments/2026-10-13-museum-open-access/registry-entry.json), outcome dimension-gain wording; also DATA-UPDATE.md line 23.

The phrase six further dimensions can be read as six additional families beyond the two with no prior dimension. The six-family axis-gain set already includes those two, leaving four families that add axes to existing dimensions.

Recommended fix: Write: Six newly joined families gain an axis, including two that previously had no dimension. The other four already had at least one axis. Source: coverage/summary.json and this verification independent-counts.json museum.more_axes_families.

## Reproduction and preservation

Before executing any package script, the verifier copied 75 starting files to `data/raw/2026-10-13-data-round-1-verification/snapshot/` and wrote `before-hashes.json` there. They comprise 49 museum files and 26 pilot files, including six existing bytecode files. The proposed public payload has 44 museum files and 25 pilot files after excluding `__pycache__`. One concurrent museum-review file already existed and was explicitly excluded in `snapshot-exclusions.json`; subsequent review files remain outside this audit.

The following commands ran from repository root with bytecode writing disabled:

```text
python experiments/2026-10-13-museum-open-access/build_joins.py
python experiments/2026-10-13-museum-open-access/coverage_museum.py
python experiments/2026-10-13-museum-open-access/harvest_summary.py
python experiments/2026-10-13-museum-open-access/acquisition_record.py
python experiments/2026-10-13-museum-open-access/write_manifest_additions.py
python -I experiments/2026-10-13-cisi2-basic-data-pilot/join.py data/raw/2026-10-13-cisi2-basic-data-pilot/final.jsonl
python experiments/2026-10-13-cisi2-basic-data-pilot/score.py score
python experiments/2026-10-13-cisi2-basic-data-pilot/score.py score --full
```

All eight exited successfully. Every regenerated package output was byte-identical to the snapshot. The pilot's local `join-detail.jsonl` was also identical. The museum scripts' imports and call paths were inspected before execution; none of the permitted steps calls the network. No other harvest, render, sample or parser command ran.

The builder was attempted through `runpy` with a guard on subprocess execution, rather than presented as an exact command replay. It regenerated `final-p435.txt`, `final-p436.txt` and `changes.json` identically, then the guard stopped its internal `parse.py` invocation at `build_final.py:69`. The existing `final.jsonl` supplied the join command. Independently applying the sample adjudication, full adjudication and eligible recheck changes produces the same five printed cells for every final row. A complete builder byte replay still needs authorization for the internal parser dependency or instructions for another permitted route.

`PROTOCOL.sha256` matches both `PROTOCOL.md` and `AMENDMENT-1.md`. The three frozen first-pass hashes in `sample.json` match their local files, and the seeded sample selects the same 33 entries. No regenerated file differed, so no corrective restoration was needed. `after-hashes.json` equals `before-hashes.json` for all 75 files. Logs, command status and raw-output comparisons are in the local `logs/`, `museum-reproduction.json` and `cisi-reproduction.json`. The normalized Lipi and website inputs match the inventory's recorded hashes.

## Museum numbers checked

The table separates the number of inspected or scanned records from the smaller set of selected originals. Original/cast classifications were counted from the saved records and decisions. Photographic inscription judgments and the truth of the identity joins belong to the separate museum review.

| Source | Counts checked | Result and evidence |
|---|---|---|
| Met | 20 queries, 176 records read, 199 requests; 5 selected inscribed originals | Counts trace to query logs, extracted rows and five decisions. Two later objects retain incorrect harvest flags, F12. |
| Cleveland | 13 queries, 23 records read, 43 requests; 3 inscribed originals | Pass from rows and request logs. |
| AIC | 13 queries, 3 saved hits, 23 requests; 0 selected Indus originals | Selection count passes; two coin flags need correction, F14. |
| Smithsonian | 770 files, 1,204,328,192 bytes, 539,615 scanned records, 22 matches, 20 Indus casts, 5 seal casts, 0 originals | Counts pass against bulk logs and retained matching rows. The full bulk stream was not retained for independent recounting. |
| Penn | 151,266,760 bytes, 430,871 CSV rows, 942 pattern matches, 47 seal-like selected rows; 5 inscribed originals, 4 other originals, 38 casts/impressions | CSV size/hash, row total and filter counts recomputed independently. Classification counts pass from retained rows. |
| V&A | 14 queries, 199 records read; 2 originals and 1 modern impression | Decision counts pass. Harvest flags and the summary's attributed-record count disagree, F13 and F15. |
| British Museum | 59 listing rows, 30 attributed flags, 27 in-scope original stamp-seals, 2 cast sets; 7 stated inscriptions and 20 without reachable inscription prose | Listing and saved flags support the counts. The 7 inscriptions depend on six saved census observations and one saved object page, rather than 27 accessible full records. |

Request counts, byte totals, dates and Penn's full hash in the source proposals trace to the saved acquisition logs. The Met and Cleveland photograph counts of five and three are supported by the saved image records; this audit did not recount their signs. The CC BY Penn attribution appears in both the README and DATA-UPDATE.md. AIC records here contain no description field requiring CC BY attribution.

| Join or coverage claim | Independent result | Status |
|---|---:|---|
| Records decided | 86 | Pass |
| All classes | confirmed 24; exact 2; ambiguous 29; unmatched 25; uninscribed 5; impression 1 | Pass, sums to 86 |
| Q-1019 classes | confirmed 15; ambiguous 22; unmatched 8; uninscribed 1 | Pass, sums to 46 |
| Failed string matches | 6 confirmed, 1 ambiguous, 6 unmatched | Pass, 13 records |
| Untried usable keys | 2 ambiguous | Pass |
| Keyless records | 9 confirmed, 19 ambiguous, 2 unmatched, 1 uninscribed | Pass, 31 records |
| Exact/confirmed joins in this package | 26, including 18 new and 8 reproduced census joins | Pass |
| Census lower bound and expanded record total | 68 before; 83 within the census after review; 86 including 3 outside it | Pass as counts of assigned joins |
| Older website museum-number coverage | 274 / 4,695 = 5.84% | Pass |
| Website plus census | 324 / 4,695 = 6.90% | Pass |
| Website, census and museum package | 339 / 4,695 = 7.22% | Pass |
| First museum numbers from this package | 15 families | Pass |
| New joins gaining dimensions | 2 first-dimension families; 6 axis-gain families, including those 2 | Pass; clarify overlapping categories, F19 |
| Finer provenance and open-image gain | 1 family and 0 families | Pass as saved field/gain counts |
| Candidate additions | 5 | Pass as declared candidate additions |

The two first-dimension families are 2098 (L-166) and 3070 (M-614). The six axis-gain families among new joins are 118, 2098, 2553, 2816, 3070 and 3984. Two reproduced census joins also have more museum axes than Lipi; they are outside the reported new-join gain. Printed dimension strings were read from the saved museum extraction, and missing local axes follow the inventory's positive-number/range rule. Axis alignment and physical object identity were not re-adjudicated.

The five candidate-addition identifiers are H-224, Banawali 3714 and DHR-22198, DHR-6032 and DHR-7860. The candidate-search counts for the eight CC0 seals span 10–102 under the automated specifications. Cleveland 1964.104 separately has eight manually named Chanhu-daro candidates. The after-coverage percentages quoted for seals (11.0%), copper tablets (19.5%), tags/sealings (6.1%) and pottery (1.3%) pass. F16 corrects one type-group denominator without changing those rounded percentages.

## CISI 2 numbers checked

There are 327 distinct consecutive entries, 283 one-family joins and 44 absent Lipi keys, with no ambiguous join and no missing row within the pilot range. Every joined family has one face. Independent counts from the final printed cells and raw metadata reproduce the before/after table:

| Field | Before | After | Supplied by pilot |
|---|---:|---:|---:|
| Museum number | 74 | 276 | 275; 241 cells without brackets |
| Holding institution | 74 | 283 | 283; gain 209 |
| FC number | 0 | 283 | 283 |
| Excavation number | 278 | 278 | 278; 252 cells without brackets |
| Spatial unit | 269 | 269 | 0 |
| Depth | 231 | 231 | 0 |
| Material | 235 | 235 | 0 |
| Any dimension | 271 | 271 | 0 |
| All three dimensions | 126 | 126 | 0 |

The percentage table passes: museum 26.1%→97.5%, excavation 98.2%, spatial unit 95.1%, depth 81.6%, material 83.0%, any dimension 95.8% and all three 44.5%. Museum gain is 202 including bracketed cells and 179 with whole cells free of brackets. On the website-only baseline, the corpus count rises 274→476 (5.8%→10.1%), or to 453 (9.6%) under the whole-cell certainty rule. DATA-UPDATE.md's seal figures are 212→414 of 2,239 (9.5%→18.5%) and Mohenjo-daro figures 216→418 of 1,795 (12.0%→23.3%).

Current holding-code counts independently match the report: MD 227, MM 39, L 21, NMP 17, EXB 11, HM 4 and KHP 3. They overlap because an object can have several codes. The year-form accession rule identifies 75 joined objects with an NMP accession, including former holdings. Two source tables share a museum number on 73 objects: 71 comparable agreements and 2 uncertain comparisons.

### Accuracy tables

Whitespace normalization, bracket alternatives and adjudication outcomes were reimplemented without importing score.py. Every disagreeing cell has exactly one adjudication record whose two pass values match the corresponding frozen readings. These results match both saved accuracy JSON files and every cell in the README accuracy tables:

| Sample column | Cells | Agreement | Disagreements | First-pass errors | Undecidable | Error %, upper % |
|---|---:|---:|---:|---:|---:|---|
| CISI | 33 | 100.0% | 0 | 0 | 0 | 0.0, 0.0 |
| FC | 33 | 84.8% | 5 | 2 | 2 | 6.1, 12.1 |
| Excavation | 33 | 90.9% | 3 | 1 | 0 | 3.0, 3.0 |
| Museum | 33 | 72.7% | 9 | 0 | 1 | 0.0, 3.0 |
| Photographs | 33 | 84.8% | 5 | 0 | 1 | 0.0, 3.0 |
| All | 165 | 86.7% | 22 | 3 | 4 | 1.8, 4.2 |

The stated 95% Wilson interval for 1 error in 33 cells is 0.5–15.3% after rounding.

| Full column | Cells | Agreement | Disagreements | First-pass right | Second-pass right | Undecidable | First errors | Error %, upper % |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| CISI | 327 | 100.0% | 0 | 0 | 0 | 0 | 0 | 0.0, 0.0 |
| FC | 327 | 92.7% | 24 | 2 | 7 | 15 | 2 | 0.6, 4.9 |
| Excavation | 327 | 91.4% | 28 | 3 | 3 | 22 | 2 | 0.6, 7.0 |
| Museum | 327 | 85.6% | 47 | 7 | 5 | 35 | 0 | 0.0, 9.5 |
| Photographs | 327 | 82.6% | 57 | 10 | 11 | 36 | 0 | 0.0, 9.5 |
| All | 1,635 | 90.5% | 156 | 22 | 26 | 108 | 4 | 0.2, 6.2 |

The full second reader has five adjudicated errors. The two second readings agree on 145 of 165 sampled cells (87.9%). The final rows have 119 bracketed cells in 101 rows (7.3% of cells): 112 in blind-adjudicated comparisons, 6 from eligible rechecks, and 1 inherited shared bracket. Five of 299 agreed excavation cells were reopened (1.7%). The recheck has 50 items: 4 confirmed, 9 Lipi defects, 7 corrected and 30 ambiguous. All these counts pass. These computations verify consistency of the readings and adjudications, rather than their accuracy against a sharper source witness.

### Excavation comparison

| Category | Reported | Independent |
|---|---:|---:|
| Equal normalized strings | 40 | 40 |
| Printed number plus FC tail | 182 | 182 |
| DK subarea letter added | 8 | **9** |
| DK prefix dropped | 4 | **3** |
| Swapped values | 4 | 4 |
| Different number | 2 | 2 |
| Letter suffix dropped | 1 | 1 |
| Incomplete string | 1 | 1 |
| Plate-reference suffix | 1 | 1 |
| Uncertain excavation or FC cell | 35 | 35 |
| Total | 278 | 278 |

The nine subarea cases are M-673, M-712, M-722, M-734, M-754, M-755, M-756, M-903 and M-920. The three prefix removals are M-626, M-672 and M-674. The two swapped pairs are M-653/M-655 and M-656/M-707. The 32 equal cases in the earlier FC series include three bracketed FC cells whose leading zero fixes their magnitude; the seven equal cases in the named later excavation series also pass. The printed-number disagreements and suffix findings are retained as source comparisons, without publishing their values.

### Source and effort claims

The PDF has 486 pages and its full hash matches the source manifest. Expected printed-page numbers appear in 418 corner headers under the explicit geometric rule in F18; 29 remain unverified by that test. A header test alone does not inspect all catalogue contents. The representative embedded foreground images and saved render hashes support the stated zoom and approximate image dimensions; the two pilot foreground images occupy 64,021 and 50,382 bytes.

Census CSV rows sum to 2,087 CISI 2 and 1,533 CISI 1 entries. Subtracting the pilot leaves 1,760; the procedure lists 22 remaining CISI 2 half-columns and 20 CISI 1 half-columns. These are census-based workload counts, not a new complete transcription of both sections. The projection arithmetic at 5.7 seconds per entry gives 2.8 and 2.4 hours. The approximate uncertain-cell projections follow 28/327 excavation and 36/327 museum cells. The first-pass run log confirms 413 seconds, or 6.9 minutes. The full-reader completion, adjudication start and five-minute recheck duration do not all have independently retained timestamps, so the claimed 13.7-, 5.7- and approximately 5-minute components remain author estimates or incompletely logged measurements. The protocol timestamp discrepancy is already disclosed in the author's retrospective; its historical freeze time was not authenticated by this hash check.

## Combined museum-number coverage

The unit is the Lipi family, and the denominator is 4,695. Website membership uses the inventory's exact whitespace-normalized CISI key and usable-value rule. The census set is the 68 confirmed families the museum package used. The museum set contains its 26 exact/confirmed families with a usable accession. Pilot membership was independently read from the printed museum cells of the 283 joined entries. Brackets count as usable in the main count, as in the pilot.

| Source set | Families |
|---|---:|
| Older website | 274 |
| October 6 census | 68 |
| Museum package | 26 |
| CISI pilot, including bracketed cells | 275 |
| CISI pilot, whole museum cell has no bracket | 241 |
| CISI pilot, at least one museum-number token has no bracket | 266 |

| Pairwise overlap | Including brackets | No bracket anywhere in pilot cell | At least one definite pilot number |
|---|---:|---:|---:|
| Website ∩ census | 18 | 18 | 18 |
| Website ∩ museum package | 6 | 6 | 6 |
| Census ∩ museum package | 8 | 8 | 8 |
| Website ∩ pilot | 73 | 62 | 72 |
| Census ∩ pilot | 0 | 0 | 0 |
| Museum package ∩ pilot | 0 | 0 | 0 |

The three older-source sets intersect on three families. Website plus census gives 324, and adding the museum package gives 339. The pilot adds 202 first museum numbers to that common baseline, while the museum package adds 15. The two new sets do not overlap, so order does not change either gain. Combined coverage is 324 + 15 + 202 = **541 (11.52%)**. The whole-cell certainty version is 339 + 241 − 62 = **518 (11.03%)**. The number-level version is 339 + 266 − 72 = **533 (11.35%)**; it retains a definite registration even if another registration in the same cell is bracketed.

[combined-coverage.json](combined-coverage.json) holds every source set, all pairwise intersections, gains and family identifiers. The local `combined-museum-coverage.csv` has one membership row for each of the 4,695 families. The inventory has no separate holding-institution coverage field, so no corpus-wide institution union was invented. The pilot's institution counts were verified separately above.

The coordinator should use 541 with its bracketed-reading definition in the combined data-page update, and can publish 518 alongside it to preserve the pilot's conservative comparison. If the intended question is whether a family has any definite museum number, 533 is the appropriate alternative. Standalone after-figures 339 and 476 remain valid for their stated source sets.

## Rights, privacy and size audit

All 69 proposed package files were inspected from the snapshot, including Python comments and docstrings, JSON strings, CSV evidence and prose. Existing bytecode and the concurrently written museum verification directory were outside the proposed payload scope. The audit followed COMMON.md and the repository's source-specific rules; no new rights ruling was inferred from public access.

The CISI leak findings are in PROTOCOL.md, join.py, schema.json, README.md, DATA-UPDATE.md and question-updates.md. Their exact source-value matches remain local in `payload-audit-detail-fast.json`. The first protocol example matches M-626. The second does not match a pilot row exactly; the saved page shows a registration of the same form above the pilot at M-595, but this review did not authenticate the disputed digit. parse.py and PROCEDURE.md contain field vocabularies, structural notation, project keys and image coordinates, with no detected per-object transcribed number. Registry and aggregate JSON files contain counts and identifiers. General code vocabularies and numeric algorithm thresholds were distinguished from record values. Date strings and Q-IDs that happen to match an FC number were rejected as false positives.

The museum harvest files `vam-records.json` and `bm-records.json` retain identifiers, field-name lists, classifications, flags and source locators. No description or title field is copied in either. Restricted prose occurs instead in `evidence` in decisions.py and its two CSV exports, F01–F03. The source fields are `description` and `title`. A six-word match to the V&A `bibliography` is a publication/page/identifier citation, which is an allowed locator. Descriptive paraphrases and short classification labels were distinguished from copied record sentences; README.md contains no detected prohibited record-prose copy. The Met, Cleveland and Smithsonian record content follows the CC0 basis supplied for this review. Penn attribution is present; AIC's saved records do not contain a description field.

The sequence scan compared candidate numeric runs against 8,980 distinct four-sign windows in both directions from the local Lipi faces. No matching run was detected in either proposed payload. No owner name, email address, credential, token or absolute user-profile path was detected. No proposed tracked file exceeds 1 MB; the largest is met-records.json at 90,040 bytes. Detailed CISI readings, acquisition responses, the protocol-example crop and value-level comparison evidence stay under the ignored verification data directory.

The two package prose scans both returned zero flags: 5 museum Markdown files and 7 pilot Markdown files. They used `python tools/review_prose.py --path <package> --no-write`. The literal draft placeholder still requires F17 despite the scanner's zero result. The verifier's own prose scan also returned zero flags after review.

## Scope and remaining decisions

This review reused the authors' saved inputs and programs for reproduction, and independently implemented agreement, adjudication consistency, joining, coverage, source-set unions and excavation categories in [check_counts.py](check_counts.py). Detailed source audits and the Penn CSV recount used local verification helpers. The public numerical evidence is [independent-counts.json](independent-counts.json), [combined-coverage.json](combined-coverage.json) and [findings.json](findings.json). [ARTIFACTS.json](ARTIFACTS.json) lists every created path.

The exact builder parser stage, museum identity truth and precision, original acquisition completeness beyond the saved caches/logs, the independence of reader sessions, every catalogue page's visual completeness and incompletely logged effort durations were not verified. Live terms were not refreshed. Those limits concern the named claims; the reproduced counts remain usable with their source-set definitions.

The data support a register with museum-number evidence for 541 provisional families, and the two packages fill different gaps. The deciding source checks are the separate museum join review and rereading bracketed catalogue numbers from a better witness. Before commit, the coordinator must apply the publication redactions, resolve the named numeric and flag discrepancies, choose the certainty definition for DATA.md, and resolve whether the final builder may run its internal parser.
