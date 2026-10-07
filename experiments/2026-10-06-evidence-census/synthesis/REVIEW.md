# Review of the evidence census

Reviewer: Claude (Sonnet 5.5), 7 October 2026. The object of the review is the B3 synthesis in `experiments/2026-10-06-evidence-census/synthesis/`. The four site batches in `sites-deep/` and the collections census were read as its inputs and checked where the synthesis depends on them. Only this file and `review/` were written; [review/README.md](review/README.md) indexes the supporting files. Seven read-only subagents made the row, join and sample checks. Each wrote one notes file in `review/`, and I read all seven before using their results.

## Verdict

The main results stand. A fresh run of the builder reproduces eight of the ten top-level aggregates byte for byte, and the other two differ only because the coordinator trimmed five source ledgers after the endpoint was written. An independent recomputation from the corpus, the batch rows, the museum records and the CISI 1 scan confirms 55 of 57 headline numbers, among them 115 entities; 327 of 493 catalogue identifiers matching and 166 absent (Lothal 111, Kalibangan 26, Banawali 14); Rehman Dheri 268 of 270 absent; 114 museum records with 61 joins; the field percentages 38.57, 55.85 and 20.26 with four zeros; and the 14/6 sample record as written. The two numerical errors are small. Batch C records two IM77 objects for Tarkhanewala Dera where IM77 p. 6 prints one, so the north India IM77 total is 117, and the REPORT's "six selected CISI 1 ranges" in Pakistan are four. The most important problem is bookkeeping after the coordinator's trim. The package's replay claims no longer hold (two of ten aggregates differ, seven of 1,069 verification checks fail, two of batch D's three `--verify` commands fail), and 32 further source records still hold 165 to 310 characters of search-result prose that the 350-character audit rule could not flag. The 166 absent identifiers also need a split before they are read as missing objects: 75 stand in graffiti sections and 91 in sections of seals, impressions and tablets. At least seven of the 53 "unjoined" museum records can be joined with evidence the package already holds. In the eight sampled rows and eleven sampled joins every source-backed count matched, and the errors lie in descriptive fields and locators. The answer "No" is supported by the evidence.

## 1. Checked claims

Results use three words: confirmed, discrepancy, unverifiable. "Recomputed" means I rebuilt the number from the inputs with my own code in `review/`, without importing the builder.

| # | Claim | Evidence path | Result | Note |
|---|---|---|---|---|
| 1 | 123 rows join to 115 entities. The pooled 5,665 face mentions hold 13 repeats (5 Nuhato, 8 from six A/D sites). 5,652 faces and 4,668 families are represented, 28 faces and 27 families are labelled Unknown, and the corpus has 5,680 faces and 4,695 families. | `coverage.json` summary; `review/check_headline_numbers.py` | confirmed | Recomputed. A scan of all 123 rows found no shared entity beyond Nuhato/Gharo Bhiro and the six A/D sites. |
| 2 | Batch totals (rows, faces, families, site-level distinct CISI identifiers): A 37, 4,837, 3,908, 3,637; B 25, 496, 460, 199; C 25, 290, 271, 232; D 36, 42, 42, 9. Regional faces 4,837, 491, 290, 34. | REPORT table; `review/recompute_batch_totals.py` | confirmed | Every row's stored `local_corpus` figures equal a recount of the corpus under its own site label (0 mismatches in 123 rows). |
| 3 | 19 CISI 1 ranges hold 493 entries: 327 match local keys and 166 do not (66.33% and 33.67%). Gujarat 317/196/121; north India 176/131/45; Lothal 290/179/111; Kalibangan 122/96/26; Banawali 37/23/14. | `catalogue-coverage.csv`; `review/recompute_cisi_ranges.py` | confirmed | Recomputed from `source_cisi` and the batch endpoints. No absent key occurs under any other site label in the corpus. |
| 4 | The 19 ranges start at 1, end where the batches say, and are contiguous. | `review/cisi1-range-verification.csv` | confirmed | I read the page headers of CISI 1 printed pp. 238–297 (Lothal), 298–326, 344–349 and 350–364 on the local scan (PDF page = printed + 36). Lothal runs 1–3 ... 283–290 over 60 pages without a gap; Kalibangan and Banawali likewise. The census evidence strings place K65 on p. 312 and B22 on p. 347; the entries end on pp. 311 and 346. |
| 5 | Rehman Dheri: 270 entries, 2 matching keys, 268 absent. Sarai Khola: 10 entries, none matching. | CISI 2 contents pp. iii–iv; corpus | confirmed | The local label for Rehman Dheri is `Rahman-deri` (2 faces). |
| 6 | "A's six selected CISI 1 ranges contain 936 entries, of which 813 match". | REPORT, paragraph after the range table; `catalogue-coverage.csv` | discrepancy | The CSV holds four CISI 1 ranges: Amri 2, Chanhu-daro 50, Harappa 264, Mohenjo-daro 620. The builder reads only the first run of a multi-run string, so Harappa's printed CISI 1 run H278–382 is left out (104 further entries, 97 of them matching), as are the later runs of Harappa's CISI 2 string (H356, H383–1019). |
| 7 | IM77: 2,906 = 3,455 − 549; Harappa 985; Mohenjo-daro 1,540; Lothal 165, of which 75 sealings. Site sums A 2,596 (7 sites), B 175 (5), C 118 (7). | IM77 printed pp. 6–7 (image read); `coverage.json` sites | discrepancy | A and B sums are right. Tarkhanewala Dera is 1 in the IM77 table and 2 in batch C, so C sums to 117. The package's sum check passes because the batch row and the batch aggregate carry the same value. |
| 8 | ICIT: 4,665 objects, 5,650 texts, 17,966 legible sign occurrences, 16,015 photographs and drawings. | CAA 2023 abstract 76, p. 281 (PDF 281) | confirmed | Title, author and affiliation also match. The abstract adds 29 tables. |
| 9 | Lipi field completeness: site 99.51%; room/grid 38.57%; period or phase 55.85%; depth 49.47%; time code 54.00%; one positive dimension 78.19%; three 20.26%; material 82.85%; excavation id 90.62%; CISI key 88.36%; calendar date 0. | `field-completeness.csv`; `review/recompute_field_completeness.py` | confirmed | Recomputed with my own missing-value rule. The zeros for dating link, photograph and rights are fixed `False` in the builder because no such key exists in the face rows. The excavation-id figure counts 146 hyphen-led strings, about 25 of them figure or plate references; excluding all 146 gives 88.0%. Any of area/section, block/house or room/grid is present on 4,376 faces (77.04%). |
| 10 | Mayig: 179 faces, 1,003 tokens, all Mohenjo-daro. | `data/normalized/mayig_summary.json` | confirmed | |
| 11 | 114 museum records (New Delhi 76, Kolkata 18, British Museum 6, Penn 5, Louvre 4, Met 5). Field counts: accession and material 114, date 108, calendar date 68, dimensions 89, bibliography 13, image slots 105 of 108 measured. | `field-completeness.csv`; saved `focused-records.json` | confirmed | Recomputed from the records. |
| 12 | The museum frame has 104 named sites and 78 excavation or source-assisted registration keys. | `field-completeness.csv` | unverifiable | Both follow rules inherited from the collections package. The raw fields hold a non-empty `site` in 112 records and `excavation_raw` in 9, so I could not reproduce the two counts. |
| 13 | 61 joins (36 CISI concordance, 13 exact excavation number, 6 normalized, 5 field-and-plate, 1 Marshall composite) cover 61 families and 67 faces. Field disagreements: 1 site, 4 material, 5 dimension, 9 sign count. | `join-summary.json`; saved `paired-comparisons.json` | confirmed | Recomputed. Across all 61, each cited CISI key and each normalized excavation id resolves to exactly the joined family; no museum record and no family is used twice. Eleven joins were read against the museum record and the printed table (section 3). |
| 14 | 53 museum records remain unjoined. | `join-summary.json`; saved `unconfirmed-join-candidates.json` | discrepancy | The count is arithmetically right, but at least five of the 53 meet the package's own join standard and two more match as full strings (section 3), so 61 of 114 is a lower bound. 17 carry a key that was tried by string match and found no corpus face (14 National Museum, 3 British Museum), 2 Louvre records carry keys that were not tried, and 34 carry no usable key. |
| 15 | Register joins: 17 publication records, 32 publication-to-batch links, 15 dataset links, 37 collection links, with candidate links kept apart. | `register-joins.json` | confirmed | 27 links share a URL; 5 rest on title and year and are labelled candidates. |
| 16 | The 20-site sample records 14 supported and 6 qualified, five rows per batch. | `source-sample-audit.json`; `sample-selection.json` | confirmed | As recorded. My re-adjudication gives 18 supported and 2 qualified (section 3). |
| 17 | The title audit flagged 17 records in five files (13 prose payloads including one repeated, 4 bookseller metadata). | `source-title-audit.json`; `source-title-review.json` | confirmed | For the pre-trim state. 17 titles now end in the coordinator's marker. 32 other records hold search-result prose (section 5, point 8). |
| 18 | 728 computation checks, 1,069 verification checks, 94 package checks. | `checks.json`; `verification-2026-10-07-v2.json`; `package-checks-2026-10-07-v1.json` | confirmed | The counts are right. 920 of the 1,069 compare `coverage.csv` with `coverage.json`, and 42 pin input hashes. None reads a source page. |
| 19 | The top-level outputs are byte copies of `main-2026-10-07-v5`; the four authored ledgers reproduce. | `OUTPUT-MANIFEST.json`; `review/annotation-replay/` | confirmed | 10 of 10 hashes; 4 of 4 ledgers byte-identical on replay. |
| 20 | Nuhato and Gharo Bhiro are one site (CISI 2 p. xv). The 2018 report cites CISI 2 p. 390 for the 1973 seal, and the plate is on p. 392. | `conflicts.json`; CISI 2 pp. xv, 390, 392; Nuhato report p. 41 | confirmed | p. 390 is Amri 6–8; the p. 392 header names Gharo Bhiro. |
| 21 | Balakot: 28 published drawings not located for photography (CISI 2 p. xv n. 12). Sarai Khola: 68 graffiti attributed to a 1972 report, 10 photographed (p. xviii n. 46; pp. 410–411). | CISI 2 | confirmed | The text counts "graffiti on potsherds"; the REPORT writes "marked sherds". |
| 22 | Lothal: 91 sealings in the earlier report and 93 in Frenez and Tosi's 2005 reanalysis. | `conflicts.json`; Frenez and Tosi pp. 67–68, 70; Rao 1985 vol. 2 p. 305 | discrepancy | Frenez and Tosi credit the 93 to Rao's finds and present no recount. The 91 is Rao's own sentence on p. 305, which the package never saw; Rao 1985 is not in `sources.json`. |
| 23 | Dholavira: 225 seals recovered, 194 analysed, 139 inscription-positive, 60 or 61 sealings. | `conflicts.json`; saved mirror text; archive.org page scan | discrepancy | The figures occur in the mirror and on the scanned pages. The sealing sentence is on p. 233, not 232, and further inconsistent totals (a pie chart summing to 58, 130 against 136 in the motif table, 204 and 185 as analysed populations) are not recorded. |
| 24 | Eight priority pools; Harappa plus Mohenjo-daro hold 4,640 faces and 3,716 families. | `priority-gaps.json` | confirmed | The ranking basis states that the pools overlap and must not be summed. |
| 25 | `SCHEMA-AMENDMENTS.md` names existing October 2 entities and a 200-object pilot. | October 2 `SCHEMA.md`; table of strata | confirmed | The entity names exist and the strata sum to 200. The row on site authority cites `conflicts.json` for north-India coordinate conflicts; that file has none, and the one explicit case is batch C's Hulas row. |
| 26 | Contributing aggregates: batch C 6 final monographs, 9 post-1987 finds, 9 CISI 1 sections, 176 entries; collections 417 direct attempts (381 HTTP 200, 15 403, 12 404, 3 429, 6 unavailable), 4,007 portal record IDs, 154 candidates (94, 10, 44 and 6). | batch and collection aggregates, query log, portal CSVs | confirmed | Recomputed from rows and CSVs. C's 118 IM77 objects is claim 7. |
| 27 | Links and inventory are consistent. | 79 relative links; `created-paths.json` | confirmed | All links resolve. The inventory lists 223 files and matches the disk and every hash. |

## 2. Reproduction log

Deliverables: all six packages hold a README, PROTOCOL, REPORT, RETROSPECTIVE, `registry-entry.json`, `sources.json` and their code. The synthesis also holds the outputs its prompt names (`coverage.json` and `.csv`, `field-completeness.csv`, `priority-gaps.json`, `SCHEMA-AMENDMENTS.md`).

All commands ran from the repository root with `PYTHONIOENCODING=utf-8` and new output names under `review/` or the local raw directory.

| Command | Result |
|---|---|
| `build_synthesis.py --output-dir .../review/rerun-build --raw-dir data/raw/.../reviewer-rerun-2026-10-07` | Exit 0 in 0.7 s; 728 checks, none failed. Eight of ten outputs are byte-identical to `main-2026-10-07-v5`. `input-manifest.json` and `source-title-audit.json` differ: five pinned ledger hashes changed, and the audit now finds 0 titles over its threshold. |
| `verify_synthesis.py --compare .../review/rerun-build --output .../review/rerun-verification.json` | 1,069 checks, 1,062 pass, 7 fail: the five input pins for the trimmed ledgers and the two comparisons above. Exit 1. |
| `review_sources.py --output-dir data/raw/.../reviewer-sources-2026-10-07-rerun --render` | 31 page witnesses and three Dholavira passages regenerated in 4.5 s; used for the sample re-adjudication. |
| `write_annotations.py --output-dir .../review/annotation-replay` | 19 sources, 20 sample rows, 7 conflicts and 8 pools; all four files byte-identical to the top-level ledgers. |
| `tools/review_prose.py --no-write` on `synthesis`, `collections-and-datasets` and the four batch directories | 0 flags in each. Manual findings are in section 6. |
| `d-finds-abroad/verify.py --verify` | Passes (36 rows, 779 references, 8 PDF hashes). |
| `d-finds-abroad/build.py --verify` and `inventory.py --verify` | Both fail (`Reproduction mismatch: sources.json`; `Inventory differs`) because the trimmed ledger no longer matches the recorded bytes. Outputs in `review/d-*-verify.txt`. |
| Not run | The batch A, B and C builders and `focused_rerun.py` overwrite the packages' own tracked files. Their aggregates were recomputed from the saved rows instead (claims 1 to 3 and 26). |

## 3. Row, join and sample checks

### Eight site rows outside the synthesis sample

For each batch I took one row by a seeded draw (seed 20261007) among rows with at least two count assertions that are not in the sample, and one row chosen for size or relevance to the headline. In batch B the first draw was Nuhato, a cross-batch duplicate, and was skipped. Each subagent checked counts, local-corpus figures, CISI coverage, IM77 and site facts against the cited pages. Notes: `review/site-check-A.md` to `review/site-check-D.md`.

| Batch | Row (selection) | Assertions | Confirmed | Qualified | Discrepancy | Unverifiable |
|---|---|---|---|---|---|---|
| A | Rappwala Ther (draw) | 15 | 7 | 6 | 0 | 2 |
| A | Chanhu-daro (size) | 19 | 10 | 8 | 1 | 0 |
| B | Pabumath (draw) | 18 | 12 | 4 | 2 | 0 |
| B | Daimabad (relevance) | 23 | 17 | 5 | 1 | 0 |
| C | Chandigarh (draw) | 19 | 11 | 6 | 1 | 1 |
| C | Rakhigarhi (relevance) | 29 | 19 | 9 | 0 | 1 |
| D | Susa (draw) | 16 | 11 | 2 | 1 | 2 |
| D | Ur (relevance) | 20 | 9 | 7 | 4 | 0 |

The agents checked 159 assertions: 96 confirmed, 47 qualified, 10 discrepancies and 6 unverifiable. Every reported count that carries a source matched its page, and every `local_corpus` figure recomputes exactly. The discrepancies sit in descriptive fields and locators:

- Chanhu-daro: `latest_cisi_coverage_year` is 1991, but CISI 2 has no Chanhu-daro section. The verified range is C1–50 in CISI 1 (1987), and the 36 local keys from C-51 to C-94 belong to a later volume that no batch opened.
- Pabumath: `holdings` reads KC as the Kutch Museum, but CISI 1 p. 366 defines KC as the Department of Archaeology, Kuchchh Circle. The registration "PBM034" is PBM 024 in the CISI 1 table and is an excavation number.
- Daimabad: the ABD registrations "80/78" are 807A on CISI 1 p. 375, and the coordinates match Uesugi's table but lie about 14 km from two other listings.
- Chandigarh: `dimensions` is "photographic percentage scales", and all four CISI captions read "(? %)".
- Susa and Ur: `faces_with_period_or_time` is 0 although the faces carry `period`; the field counts the `time` code only, for all 78 labels of the coordinator file. Ur also has a wrong locator for Gadd no. 1 (pp. 5–6, not 3–5), an excavation number (U.7683) that no source in the batch contains, a sign described as "disputed" where Gadd calls it certain, and "drawings partial" that holds only for Laursen's figure.

Smaller issues in the ledgers and rows. Batch A has five entries marked `opened: true` without a witness file (Fuls 2022 and 2023, Mughal 1989, two Didier entries), two of which describe snippet-level or blocked access in their own scope text, and several rows hold strings with words run together ("2November1935-26March1936", "NewHaven"). Batch B marks FULS2022 an opened preview although its CISI 3.1 evidence is a search snippet, and two of its witness labels point to the wrong logs. Batch C records the Rakhigarhi inventory coordinates under no source id, and the matching ledger entry is mistitled and marked unopened. The dimension and excavation-number counts in the rows depend on tests the rows do not state; the excavation-number count treats a plate reference such as "-Pl. 62:2" as a number, as the synthesis builder does.

Two findings affect the synthesis directly. The Daimabad gap is real: five of the seven catalogue numbers absent from the corpus (Dmd-2, 3, 6, 7, 9) are objects that Sali reports with Indus signs, and Fuls's site list holds only the same two texts. Batch D found BM 123208 in the export twice, as Ur face 3898.1 and Dilmun face 6000.1, so the Ur and Dilmun counts probably include one object under two labels; the synthesis calls this a candidate identity, which fits. The same note infers that several local Gulf faces were built from Laursen's Table 1, which would make the comparison between those faces and the published counts partly circular.

### Museum joins

One subagent read ten of the 61 joins (two or more for each method except the Marshall composite, which has one join), one more join that rests on a concordance row alone, and two side checks, against the saved museum page, the Lipi rows and the printed table (notes: `review/museum-join-check.md`). I spot-checked its extra candidates in the corpus.

All eleven joins stand. In each, the museum record shows the stated accession and mentions an inscription; the Lipi rows carry the stated key, site and excavation id and form one family; the cited CISI 1 page and row (pp. 367, 369, 371, 372) or Marshall table row (p. 404, row 345) say what the package says; and no rival candidate exists. Eight of the ten sampled pairs are confirmed and two qualified. Pair 6 (`DHR 2617`) rests on the number alone, and the material (steatite against terracotta), type and sign count differ. Pair 7 (`dk-1023-55`) has a portal URL that reads 65 where the page and the CISI row read 55. The Marshall join (pair 10) agrees on 33 mm because the corpus size is Marshall's own, so that agreement is the same table read twice. The rejected collision (`dki-838-56`) was rejected correctly: a string match would have chosen M-1485 instead of M-543. The British Museum side rests on the saved provider text, because the live page returned HTTP 403.

Three points concern how the package describes its evidence. The CISI 1 basic-data table runs from p. 365 to p. 375, and the transcription stops at p. 372. Eight of the 61 joined records have a portal slug that differs from the displayed accession in at least one digit. The audit's `join_evidence` cell is blank for the exact-number joins.

The unjoined set holds joins that the package's own rules allow, so 61 of 114 is a lower bound. Three National Museum Lothal records (1878/1165, 6742/1174, 13051/1157) have both numbers printed in CISI 1 p. 373 (rows L-143, L-144, L-220), which the transcription did not cover; their keys were never queried, and Lipi holds the three rows (2085.1, 2086.1, 2136.1). Two British Museum seals (`Misc. VS 823`, `Hr 629`) follow the serial-plus-plate pattern of the accepted Marshall join; the subagent found them on Marshall p. 402, and Lipi carries `VS 823003` and `HR 629053` (2526.1 and 2484.1). Two Banawali records (`BNL-1-5026`, `BNL-1-170-84-1145`) equal Lipi B-3 and B-25 as full strings, but the key extractor cut them at `BNL-1`. The "tried and found absent" label for the 17 keyed records is therefore a failed string match.

### Re-adjudication of the 20-site sample

Two agents judged ten assertions each from the source pages before opening `source-sample-audit.json` (notes: `review/sample-recheck-AB.md`, `review/sample-recheck-CD.md`). Together they record 18 supported and 2 qualified; the package records 14 and 6.

- The package is more cautious on Kalibangan and Banawali (its qualifier describes its endpoint-only check; the contents and running heads support the full ranges), on Balakot and Sarai Khola (the unopened Dales and Halim articles are scope notes, since the assertions report what CISI 2 prints) and on Shortughai (the preface does not say that both seals carry script, which the assertion text omits).
- The package is more generous on Lothal (the 93 is credited to Rao, see claim 22) and arguably on Tepe Yahya, whose cited pages vi and xi show the range and TY-106 but not the other scripts.
- Locator defects inside supported rows: Dholavira p. 233 not 232; Nagwada pp. 19–20; Nippur's "p. 81 / PDF 151" is printed p. 113 (p. 81 is PDF 119); Karanpura's seal text is on pp. 114 and 117; Banawali's range omits the addendum p. 364; four census locators in `coverage.csv` are one page off (Kalibangan K65, Banawali B22, Shortughai preface, Gonur fig. 115). Bhagwanpura fig. 39 draws one tablet, not two.

## 4. Source checks

All 19 entries in `sources.json` were compared with a title page, front matter, a catalogue record or a saved witness. The 16 entries marked opened have saved page images or text whose SHA-256 matches; Harappa 2010, Laursen 2010 and Gadd 1932 are marked as not opened in B3, as they should be. Errors and qualifications:

| Entry | Finding |
|---|---|
| IM77, ICIT2023, CISI1, RANGPUR1963, IAR1963, NIPPUR1993, BHAGWANPURA1993, NUHATO2018, HARAPPA2010, LAURSEN2010, GADD1932 | Title, authors, year and venue are correct. The CISI 1 and Bhagwanpura URLs timed out (the accession numbers on the PDFs match their file names); Gadd and Laursen were confirmed by search records. Publisher and place are omitted for CISI 1 and CISI 2. |
| CISI2 | The archive.org URL is a second file in the item that holds IM77; the entry correctly names CISI 2. |
| SALUT2016 | The title omits "recent discoveries and". |
| IAR2013 | The volume reads "2013-14"; the entry has "2013-2014" and a corporate author where the title page names a chief editor and an editor. |
| CISI33 | The URL leads to an author postprint of Desset's essay, not the volume. The opened witness is a 40-page excerpt without the catalogue pages TY-1 to 112 and Sh-1 to 84. |
| GONUR2005 | The imprint note is still open although PDF 6 reads Aşgabat, Miras, 2005. |
| LOTHAL2005 | The printed title matches; Zenodo prints "networks" for "Circuits". The rights note is out of date: the record now lists CC BY 4.0. |
| DHOLAVIRA2015 | The title's date range is the uploader's label (the report says "1989–90 to 2004–05"). The URL is a user-upload mirror, so `saved_primary_content` is generous. An archive.org scan (938 pages) matches the mirror on the seven pages compared. |
| IAR1987 | A date note sits in the authors field. |
| Missing | Rao 1985 is used for the 91 sealings and has no entry. |

## 5. Method and scope findings

1. **Protocol before outcomes.** `sample-selection.json` (02:11) precedes the first builder run (02:17) and the sample audit (02:25). The protocol file's modification time (02:32) follows its dated amendments, and the package sits in one commit, so the original protocol text cannot be dated. The post-outcome corrections (alias spellings, field definitions, Amri prefix) are dated and labelled Exploratory, and the earlier endpoints are preserved.
2. **Not found and not queried.** The package keeps them apart in most places: `null` for ICIT counts and worldwide figures, `unmeasured` for ICIT, CISI and IM77 field denominators, British Museum image fields and museum findspot and dating fields. Five places blur the line. (a) Twelve rows of `field-completeness.csv` (the three fixed zeros for Lipi and nine for Mayig) are labelled `measured_export_presence`. (b) The abroad row of `region-coverage.csv` shows 0 in the IM77 and CISI 1 columns. For IM77 the zero means "not extracted", since p. 6 prints Ur 6, Kish 2, Telloh 2, Susa 1, Umma 1 and a West Asian subtotal of 17; for CISI 1 it means "not applicable". (c) A `null` IM77 count mixes "IM77 prints no count, so no selected object" with "not extracted". (d) The 53 unjoined records pool 17 whose keys failed a string match, 2 whose keys were not tried and 34 with no usable key. (e) Batch fields such as `post_1987_inscribed_find_documented` and the `counts_by_class` nulls say "not located in inspected sources" where, in the Chandigarh and Rakhigarhi rows, the draft report's graffiti chapter and later literature were not read.
3. **Count bases.** No figure from ICIT, IM77, CISI, Lipi or the museum frame is added to another. The face total is de-duplicated across batches with the 13 repeats shown, count assertions are stored with `additive: false` (230 of 230), and the pool ranking says the pools must not be summed.
4. **Wording of the answer.** "No" follows from the evidence. Three phrases claim more than the measure. "66.33% represented" is a match by identifier: the corpus can hold an object under no key (Lothal has 3 families and Banawali 3 without a CISI key, and Rakhigarhi has 9 beyond its three catalogue numbers), so at most that many absent numbers are present. "The measured local indexes" names one index, the Lipi derivative. The README and REPORT use "face", "provisional family", "local corpus" and "absent key" without defining them, and a new reader cannot tell that the local corpus is a pinned 5,680-face export whose numbering follows ICIT. The REPORT also says that ICIT objects and Lipi families "have different inclusion rules"; no file in the package documents the relation between the two.
5. **What the 166 absent identifiers contain.** By section of the catalogue, 75 are in graffiti or pottery-mark sections (Lothal L-221–290: 52 of 70 absent) and 91 in sections of seals, impressions, tablets and other objects (Lothal seals 34 of 123 and impressions 25 of 93; Kalibangan seals 12 of 65; Banawali seals 8 of 22). The Lothal impression section (L-124–216) has 93 entries, the number that Frenez and Tosi credit to Rao's finds. `review/cisi1-range-verification.csv` and `review/cisi1-class-split.csv` give the split.
6. **Frame gaps.** CISI 1 prints sections for Maski, Mehi and Shahi-Tump (1 entry each), and CISI 2 prints sections for Kalako-deray, Lewan-dheri (Dar Dariz), Loebanr, Periano-ghundai and Tarakai Qila (13 entries). None has a row in the 123-row frame, and the corpus has no label for any of them. Each batch prompt asked for same-region sites missing from its list, with an account of how they were found; the batches added Sibri, Rohira, Tigrana, Kanewal and Babylon but not these. Maski lies in Karnataka, which no batch covers. The REPORT calls the frame "a census selection" without naming the gap, and a CISI-based comparison cannot see these sites.
7. **Verification label.** "Verified computation" describes arithmetic. The IM77 error passes every check because the batch row and the batch aggregate share the value, and the sample did not include a batch C IM77 row. The sample outcomes are purposive and the package says so.
8. **Rights.** After the coordinator's trim, 32 distinct records (A 3, B 7, C 4, D 18) still hold 165 to 310 characters of search-result prose in `title` (museum object descriptions, news and blog text, mid-sentence fragments), and 22 more hold short fragments. The audit rule (over 350 characters or 55 words) was set above them, and the trim keeps 120 characters of each title. IDs only are in `review/residual-snippet-title-judgement.json` and `review/residual-snippet-title-ids.json`. No museum description, image, PDF or transcription payload is tracked; the tracked census files are JSON, CSV, Markdown and Python. The Dholavira URL points to a user-upload mirror.
9. **Scope.** The census prose contains no claim of decipherment, sound or meaning, novelty, or resemblance presented as fact.
10. **Manifests after the trim.** The batch manifests (`created-paths.json` for B, `file-manifest.json` for C and D) list the pre-trim hash of `sources.json`.
11. **Not checked or unavailable.** The original protocol text; Dales 1974, Halim 1972, Rao 1985 pp. 319 and 325–328, and the printed ASI Dholavira volume; the CISI 3.x entries behind the local keys C-51 to C-94, C-73, C-78 and M-1906; the live IGNCA, harappa.com and ResearchGate pages (403 or timeout, so only file existence was compared); and any current ICIT inventory.

## 6. Writing

The prose scanner finds nothing. Reading the README and REPORT turns up the following.

- About ten corrective contrasts in the REPORT ("not an additional 179 independent objects", "not complete institutional holdings", "not present-day coverage", "not the whole Pakistan catalogue", "not an enumeration of all archaeological sites"). Stating each population directly in the table cell removes most of them.
- The unknown worldwide total is restated in four places (README opening and closing, REPORT opening and closing).
- The README closes with a sentence about confined write paths that belongs in the retrospective, and opens its third paragraph with five verification counts in a row.
- The first sentence of the README bolds "not", and numbers are bolded throughout the first two paragraphs.
- "bounded" appears three times and "defensible" once; "clean bibliographic entries" in the retrospective has no stated meaning.
- The sentence on Dilmun and Ur ("separate candidate provenance/identity cases") is unclear.

## 7. Boundaries

`git status --porcelain` lists two changed paths inside the census package, `synthesis/REVIEW.md` and `synthesis/review/`, both mine. The other changed paths belong to concurrent work on other packages (backward-chronology, chronology-region, sign-context-and-seals, and `knowledge/retrospectives/2026-10-06-research-program.md`) and are expected program files. No tracked census file was edited. I removed my temporary directories under `data/raw/2026-10-06-evidence-census/synthesis/`; the subagents removed theirs and any file the fetch tool saved outside the repository.

## 8. Fixes

Required, in order of importance:

1. Trim or relabel the 32 search-result titles listed in `review/residual-snippet-title-judgement.json`, widen the audit rule (mid-sentence start, several sentences, length over 150), and shorten the retained stub to under 15 words.
2. Record the post-trim state. Add a dated amendment and a new endpoint (v6) with the five new ledger hashes, and update the README and RETROSPECTIVE statements on ten matching aggregates and 1,069 passing checks. Add the same note to batches B, C and D, whose manifests and `--verify` commands no longer match.
3. Correct batch C's Tarkhanewala Dera IM77 count to 1 and the derived sums (region C 117) in `coverage.json`, `region-coverage.csv` and the REPORT. Correct "six" to four and disclose the first-run-only range parse, or read all runs of Harappa's CISI 1 and CISI 2 strings.
4. Reword the answer: "match by identifier" for "represented"; one measured local index; define local corpus, face, provisional family and absent key at first use; name the eight CISI sections without a row; give the class split of the 166.
5. Add the seven joins in section 3 (five meet the package's own standard), or label 61 as a lower bound, and split the remaining unjoined records into failed string match, untried key and no usable key in the REPORT and priority pool 7. Relabel the twelve structural zeros in `field-completeness.csv`, and leave the abroad IM77 and CISI 1 cells empty with a status or fill the IM77 West Asian rows.
6. Correct the sample-audit locators and the `sources.json` entries listed in sections 3 and 4, and add Rao 1985.
7. Pass the row corrections in section 3 (Pabumath KC and PBM 024, Daimabad ABD 807A and coordinates, Chandigarh dimensions, Ur locator and U.7683, `faces_with_period_or_time`) to the batch authors.

Optional:

- Report the union of spatial fields (77.04%) beside the room/grid share, so that "findspot" does not read as 38.57%.
- Upgrade the Kalibangan, Banawali, Balakot and Sarai Khola sample labels, or state in the audit that qualifiers describe the endpoint-only check.
- Record the archive.org Dholavira scan and the extra Dholavira totals in `conflicts.json`; state Lothal's 91 (Rao 1985 p. 305), 93 (Rao's finds as cited by Frenez and Tosi; 93 sealing entries in CISI 1) and 75 (IM77 selection) as separate counts with sources.
- Cut the corrective contrasts and repeated caveats listed in section 6.
- Change `SCHEMA-AMENDMENTS.md` to cite batch C's Hulas row for coordinate conflicts.
