# Review of Package O: public Hugging Face candidate and private-store card

Reviewed 8 October 2026 against the committed state of `experiments/2026-10-08-hf-public-release/` (commit 3024ada). Scripts and outputs of this review are in [review/](review/).

## Verdict

The technical results stand. All 19 configurations load with `datasets` from the local `release/` folder, row counts equal the card, all 949 PNGs resolve and equal their parents byte for byte, and the staged scorer reproduces Package M's frozen metrics with zero mismatches (24/60 top-five whole rows for v1, 40/80 for v2, and every summary, per-row, bootstrap, criteria, sensitivity and source-row-recall field in both metrics files). A fresh build of the tables, images and scorer reproduces the staged bytes. My own scans found no Lipi, Mayig or website sign sequence in any staged table (zero runs of three or more positions, with a planted-sequence control that detects 200 of 200), no copied third-party prose at an 8-word window against 0.4 GB of local text (matches are bibliographic strings and licence text), and no image outside the CC BY 4.0 Helsinki derivatives. The release is not ready to become public, for three reasons. First, the `evidence_museum_joins` table is described as 68 accession-to-CISI joins, but 14 rows carry the Lipi placeholder `cisi = "-"`, 19 rows rest only on a comparison with the Lipi `excavation-idno` field (14 exact or normalized excavation matches, 5 Penn shared-field matches), and five `join_evidence` strings name "Lipi metadata.excavation-idno"; these are identifier-level overlaps that need an explicit owner decision and corrected wording. Second, the "Score a new row reader" instructions place `confidence` in the wrong object and omit `section` for v2, which I reproduced as silently dropped calibration and NaN bootstrap intervals. Third, the folder to be uploaded contains owner-facing and private material (the private backup's repository ID, a link to the private GitHub repository, and a 1.5 MB audit that lists the private backup's file paths and hashes). The private-store card is accurate on counts and restore scope, and it omits one fact that matters for recovery: the 1,034 restoration files no longer exist locally, so the Hub copy is their only copy and `hf_host.py verify` now compares nothing.

## Checked claims

| Claim | Evidence | Result | Note |
|---|---|---|---|
| 19 configurations, 2,739 table rows | `review/load-check.json` | Confirmed | Library names equal the YAML names; per-configuration rows equal the card table (19 of 19). |
| Card loading snippets work | `review/readme_snippets.py` | Confirmed | The three snippets run verbatim from the repository root; `rows[0]["context_image_path"]` opens a 1378x280 image. |
| YAML `configs` block valid | `huggingface_hub.DatasetCard` parse, `datasets` load, [Manual Configuration](https://huggingface.co/docs/hub/datasets-manual-configuration) | Confirmed locally | `config_name` plus `data_files` with `split` and `path`; names unique. The Hub's server-side validator was not run, because that would transmit the unreleased card. |
| 949 PNGs resolve, decode and match hashes | `review/image-audit.json`, `review/load-check.json` | Confirmed | 1,898 path references opened across six tables; 949 equal their parent files; all 949 come from `output/chart_atlas/cells`, `blind/`, `blind/chart_sheets` and the v2 `blind/` folders; no colour pixels; PNG metadata holds only `dpi`. |
| v1 scores 24/60 top-five, 13/60 top-one, 33/60 counts, 23/60 numbers, 19/60 classifications, 10/52 exact singleton rows | `review/score-comparison.json` | Confirmed | Staged scorer against Package M `evaluation/2026-10-07-frozen-v1/metrics.json`: 3,528 numeric and 1,101 discrete leaves compared, 0 mismatches, including bootstrap intervals and the three sensitivities. |
| v2 scores 40/80, 20/80, 44/80, 59/80, 62/80, 55/80, 19/66, 304/352 aligned unit recall, 1,242/1,286 random-page recall, 561/561 stress recall | same file | Confirmed | 4,470 numeric and 1,376 discrete leaves, 0 mismatches. Four of five criteria fail, as the card says (crop, number, count, top-five rows; random-page recall passes). |
| Fresh build reproduces payload | `review/rebuild-comparison.json` | Confirmed | 984 of 987 rebuilt files equal the staged files: 19 Parquet, 949 PNG, 3 scorer, 9 benchmark files and 4 others. The three unequal files (`README.md`, `provenance/input-manifest.json`, `provenance/rights-audit.json`) are written by the later documentation and audit steps, which I did not run. |
| Manifests | `review/manifest-check.json` | Confirmed | 995 of 995 file hashes and 19 of 19 table hashes match; only `file-manifest.json` is absent from itself, as documented. |
| Field definitions describe the schemas | `review/field-definitions-check.json` | Confirmed | Every column of all 19 tables is documented with the right Arrow type. |
| Chart: 687 cells, 16 ambiguities | `data/chart_reference.parquet` | Confirmed | 16 rows have `alternatives`, all `numeric_confidence = medium`; p20_c4_r21 lists 465 with 485, 486. |
| v1: 22 of 60 exposed locators, 20 rows per reader, six repeats; v2 quotas 28/26/26; 18 random plus 3 stress pages; 306 readings; 11 overlay changes | staged tables, `benchmark/*.json` | Confirmed | Reading counts: 60 + 6 + 160 + 80 = 306. The v1 frame is PDF 31-79; sampled rows span pages 31-78. |
| Source PDF hash, ISBN, 179 pages, CC BY 4.0, handle | `research/corpus/primary/koskenniemi_parpola1979.pdf` | Confirmed | SHA256 matches NOTICE; the PDF cover sheet prints the handle 10138/342677; the portal page shows ISBN 951-45-1627-3, 179 pages and links CC BY 4.0. |
| CISI 1 ranges 493/327/166 with 75/91 split | `data/evidence_catalogue_sections.parquet`, `evidence_catalogue_coverage.parquet` | Confirmed | Sums over the 19 CISI1-1987 rows. |
| Weight tables (13.716 g over 90 weights; 14.280 g over 147; 136/18 against 170.246/38.727) | `data/weight_*.parquet` | Confirmed | The 170.246/38.727 means belong to the jitter-0.15 null; the 0.35 and site-log-uniform nulls have larger means, which the report does not mention. |
| Sequence screen: 105 rows, 6,878 distinct sequences, zero matches | `validate_release.py` `sequence_scan` | Confirmed with a description error | The numbers reproduce, but 6,878 counts both reading directions of 3,506 distinct sequences, and the screen reads only the two `*_faces.jsonl` files. Mayig codes keep a `P` prefix, so they cannot equal numeric benchmark codes. |
| "68 accession-to-CISI joins" | `data/evidence_museum_joins.parquet` | Discrepancy | 54 rows carry a CISI key; 14 rows carry `cisi = "-"` (13 `exact_excavation`, 1 `normalized_excavation`). |
| Private card: 1,038 files, 3,406,008,409 bytes, manifest SHA256, per-set counts | `hf-hosting-manifest.json` | Confirmed | `checksums-manifest.json` is byte-identical to the hosting manifest. Every one of the 1,038 paths has an `exclude` decision in `rights-audit.json`. |
| Private card: restore, verify and upload scope | `hf_host.py` | Confirmed, one omission | `restore` fetches only the two restoration directories; `verify` covers only those; `upload` rewrites `README.md`. The card does not say the local copies are gone (see fixes). |
| No personal data or local paths in the release | `review/privacy-scan.json` | Two hits | `README.md` links `github.com/k-sandhu/indus-valley-script` (private); `RELEASE-CHECKLIST.md` names `ksaw008/indus-research-data`. |

## Rights findings

**Sign sequences.** `review/rights_scan_sequences.py` builds an index of every `signs_visual_ltr` sequence in the three Lipi files, the two Mayig files and the website export (5,759 distinct sequences, 11,518 with both directions), then scans 4,189 staged sequences: strict and shape-only candidate sets and top-one and top-five template sets from every `reference_json`, `prediction_json` and `reading_json`, chart codes and ranks in column, row and global order, and every list of three or more integers in any parquet or JSON file. Candidate sets match by intersection, the most permissive rule. Result: no run of three or more positions in any category, and no whole-sequence equality for the 88 complete singleton reference rows of length three or more. Shuffled controls expect 0.0 to 1.1 sequences per category, and planted Lipi sequences are found 200 of 200 times, including with ambiguous positions. The scan separates copying with a shared code numbering from independence, and cannot see copying after recoding. The stronger evidence is provenance: Package M's pipeline, protocol, report and freeze files do not mention Lipi, the references are readings of CC BY page images, and the Helsinki edition prints drawn signs without numeric sequences (provenance record, `machine_readable_status`). Hit details would go to `data/raw/2026-10-08-hf-public-release/review-scan/`; there were none, so no Lipi sequence appears under `review/`.

**Field values.** `review/rights_scan_fields.py` compares string cells with Lipi `cisi` and `excavation-idno` values. Only the museum-joins table matches: all 54 non-placeholder `cisi` values occur in Lipi, and 26 rows carry an excavation-style join method, which compares the museum number with Lipi's `excavation-idno` (13 exact, 8 normalized, 5 shared-field; `synthesis/build_synthesis.py` line 371 shows the comparison). Seven of those 26 also cite a printed CISI 1 row, so 19 rest on the Lipi comparison alone: the 14 rows with `cisi = "-"` and the 5 Penn rows. Exact whole-cell equality with a Lipi `excavation-idno` value holds for 15 `museum_accession` cells and 19 `shared_identifier` cells; the other rows differ by punctuation or carry composite text. No cell equals a Mayig description. The census tables carry aggregate counts derived from the Lipi export (`local_faces`, `local_families`, `local_cisi_identifiers`, the Lipi rows of `evidence_field_completeness`), which `REDISTRIBUTION.md` allows as aggregates.

**Museum joins, field by field.**

| Field | Source | Assessment |
|---|---|---|
| `institution`, `join_method`, `status`, `source_locator` | Project labels and pointers | Own work. `source_locator` exposes local-only paths such as `data/raw/.../museum-join-supplement.json#/0`. |
| `museum_record_id`, `museum_accession`, `museum_url` | Museum catalogue identifiers and the object-page URL (National Museum Delhi, Indian Museum, Penn, British Museum) | Identifiers and a pointer; no description, photograph or other museum-authored prose is copied. Museum terms of use were not opened by Package O or by me. |
| `cisi` | 54 keyed rows: 39 from the printed CISI 1 concordance, 3 from the Marshall composite table, 5 normalized-excavation rows and 2 supplement rows that also cite a CISI 1 row, 5 Penn rows whose evidence is Lipi `excavation-idno`; 14 rows hold Lipi's missing-value marker `-` | Published catalogue keys are facts, and they also equal Lipi `cisi` values. The `-` is a Lipi placeholder, not a CISI key. |
| `shared_identifier` | Museum "other number" fields, the CISI concordance row, the Marshall table, or the Lipi `excavation-idno` | Identifier text. For the 14 rows with `cisi = "-"` the value is the museum accession itself, so it adds nothing beyond the museum record except the fact that a Lipi record carries the same identifier. |
| `join_evidence` | Project citation strings ("CISI 1 (1987), printed p. 367, row M-197; raw/cisi1-data-403.png") | Pointers; the `raw/...png` names refer to third-party page scans that are not shipped. Five strings name "Lipi metadata.excavation-idno". 14 are empty. |

No field is museum-authored descriptive text. The residual issues are identifier-level: the table reveals which museum objects match Lipi excavation identifiers, and the concordance rows come from a copyrighted book (CISI 1, 1987) as identifier pairs. I recommend the owner decide explicitly and describe the table honestly: 54 CISI-keyed joins, 14 excavation-number joins with a null `cisi`, and the source of each identifier.

**Prose.** `review/rights_scan_prose.py` extracts 57,380 staged strings (251,298 words; bibliographic fields excluded) and compares 8-word windows with 3,414 text files (422 MB) in `research/literature` and 14 local raw directories; the package's own screen used 15-word windows and 496 witnesses. My scan finds 8,880 matching windows. They come from project-authored copies (Package N manifests, the object ledger, census join files), from the 1979 edition's title and publisher strings in `NOTICE`, `README.md` and `CITATION.cff`, from the Creative Commons and MIT licence text, and from file paths. None is museum, catalogue or book prose. A scan cannot cover text never saved locally or paraphrase.

**Images.** All 949 PNGs are crops, chart cards or full page renders from the 1979 edition. I viewed a chart cell, a chart card and a count page: printed drawings, our numeric labels and page furniture only.

**Excluded material.** No Lipi or Mayig records, Ascalone catalogue rows, third-party PDFs, museum images or the provisional transcription are staged. The two weight tables are aggregates. Page 6 of Ascalone (2022) says its open access was funded by the ERC grant and no licence statement appears in the first eight pages; the owner could check the DOI landing page (10.23797/9783529035425) if catalogue-level data are wanted later.

## Reproduction log

| Step | Command (from repository root, `indus-ml` Python) | Result |
|---|---|---|
| Load and image check | `review/load_check.py` | Passed. First attempt failed with Windows error 206 because my cache path made the lock filename too long; a relative `cache_dir` fixed it. The same limit applies to any user with a long cache path. |
| Card snippets | `review/readme_snippets.py` | Passed |
| Scoring | `release/code/score_benchmark.py --benchmark v1\|v2 --out data/raw/.../review-scores/staged-vN.json`, then `review/compare_scores.py` | Zero mismatches against Package M |
| Standalone scoring | copy `code/` and `data/` to a new root, `python -B code/score_benchmark.py --benchmark v2 --no-bootstrap --out my-score.json` | Equal to the repository-run summary |
| New-prediction format | `--predictions minimal-vN.jsonl` built from the documented fields only | v1 and v2 run, but calibration is empty and v2 intervals are NaN (see fixes) |
| Fresh build | `build_release.py --out review/rebuild`, `review/rebuild_compare.py` | 984 of 987 equal; copy deleted after comparison |
| Manifests, field definitions, images, privacy | `manifest_check.py`, `field_definitions_check.py`, `image_audit.py`, `privacy_scan.py` | As in the table above |
| Rights scans | `rights_scan_sequences.py`, `rights_scan_fields.py`, `rights_scan_prose.py` | As above; about 25 seconds in total |
| Private-store checker | `verify_private_store.py --root . --out review/private-store-local-check.json` | 4 of 1,038 present: the four Helsinki files. The 1,034 restoration files are absent locally. |
| Prose scan | `python -B tools/review_prose.py --path experiments/2026-10-08-hf-public-release --no-write` | 13 files before this review was added and 14 after; no flags. The tool matches phrases only, so the manual findings are below. |

I created an empty `release/review/` directory by mistake while starting and removed it at once; the manifest check afterwards shows 996 files, as before. Not run: any Hub call (upload, validator, `hf_host.py verify`), a remote restore, a human reading of benchmark rows.

## Source checks

| Source | Check | Result |
|---|---|---|
| Koskenniemi and Parpola 1979, Helsinki research portal | Opened, plus the cached 2 October copy and the PDF cover sheet | Title, authors, year, Research Reports 1, ISBN, 179 pages and CC BY 4.0 link confirmed. The portal does not print the handle; the PDF cover sheet does. The handle redirects to `helda.helsinki.fi`, which returned an access-denied page to my fetch. |
| Creative Commons Attribution 4.0 deed | Opened | Attribution of creator, licence notice, link to material, indication of changes, no implied endorsement. NOTICE gives each element the source supplies; the PDF cover sheet supplies no copyright or warranty notice. |
| Hub "Manual Configuration" | Opened | The `configs`, `config_name`, `data_files`, `split`, `path` structure matches the card. |
| Hub "Upload files to the Hub" | Opened | `upload_folder` usage matches. `HfApi.create_repo(..., private=True, exist_ok=False)` exists in the installed `huggingface_hub` 2.1.1. |
| Hub "Repository Settings" | Opened | Visibility toggles in the Settings tab, as the checklist says. |
| Hub "Load" (datasets) | Opened | Local folder loading and Parquet guidance consistent with the card. |
| Frenez and Tosi 2005, Zenodo 5514283 | Opened | Year and authors match, and the record shows CC BY 4.0. Zenodo's title ends "maritime trade networks across the Arabian Sea"; `evidence_sources` (`synthesis:LOTHAL2005`) says "Circuits" and `evidence_publications` says "Networks". The variants come from the parent census registers. |
| CISI 3.1 (2010) and CISI 3.2 (2019), Helsinki portal | Opened | Titles, editors, years and series match `evidence_sources` and `evidence_publications`. |
| Marshall 1931, archive.org item | Opened | Title, editor, year match. |
| Lipi repository | Opened | No LICENSE file at the root, supporting the exclusion. |
| Ascalone 2022 | Opened the PDF front matter | Title, Weight & Value 3, Wachholtz, 2022, Tavernier contribution match `sources.json`. |

The Package O `sources.json` records seven sources and marks Ascalone as not opened by this package; the 111 archaeological pointers inherit their access scopes, and at least 25 carry the label "Search-result excerpt reviewed", so snippet-only sources are flagged.

## Method and scope

The protocol (09:33) precedes the first build (09:39) and every validation run (09:49 onward). The package fixed checker faults after seeing failures (cache path, an encoding name, list-child naming, the `CISI1-1987` filter) and recorded them in the retrospective and in preserved reports, but `PROTOCOL.md` carries no dated amendment, which its own rule asks for. Counts keep their bases. Status labels follow the vocabulary. No claim of decipherment, sound or meaning appears; the card states the contrary. The metrology rows say "Exploratory" and link to a method report in a private repository that public readers cannot open.

## Card as a first-time reader

What works: the first paragraph says what the files are, the licence structure and attribution paragraph are complete (author names, title, series, publisher, official record, handle, licence link, stated changes, no endorsement), AI assistance and the absence of expert review are stated, and `FIELD-DEFINITIONS.md` covers every column accurately.

What does not work yet:

1. The benchmark task is never stated as a task. A reader has to infer that a system receives a row crop and returns an inscription number, a five-position classification and an ordered list of candidate-code sets, and that "the frozen pipeline" is a chart-only template matcher. "Four of five pipeline criteria failed" names no criteria; the thresholds (90% crop, 90% number, 95% count, 80% top-five rows, 95% random-page recall) are only in the scorer. "Compatible whole row", "aligned unit recall", "exposed OCR locator" and "eleven-code overlay" are used before or without definition. `benchmark/CONVENTIONS.md` is not linked from the card, covers only v2, and refers to folders (`position-chart/`, `page-count-source/`) and files (`predictions.json`, `frame.json`) that are not in the release.
2. The prediction format is wrong in the one place a user relies on it (required fix 2).
3. `local_faces`, `local_families` and "a pinned export" in the census sections are never identified; the Lipi export is named only in `evidence_datasets`. A reader cannot interpret the columns, and the card cannot say why the export is not redistributed without naming it.
4. The first-time reader flow is local. Snippets use `experiments/2026-10-08-hf-public-release/release`, the scorer examples use PowerShell paths under `data/raw`, and the hosted forms sit in comments. `README.md` begins with "This locally staged candidate" and carries TODO placeholders in five files.
5. "Fitted unit" for the weight tables is not explained (a common base mass hypothesised for a set of weights).
6. Writing: no stock phrases, and the paragraphs read in connected prose, but several paragraphs carry six or more figures with no definitions, and caveats recur. The absence of expert certification appears in the chart paragraph, the status section, two field definitions and the checklist. `FIELD-DEFINITIONS.md` repeats "Repository paths are evidence pointers, not public URLs" eight times and the same `status` sentence 15 times, and uses "is not" or "not a" 15 times; per `WRITING.md` these belong in one shared-notes block. The `status` definition does not list its two values.

## Required fixes

1. **Museum joins.** Correct the description (README table row, `FIELD-DEFINITIONS.md` `cisi`, package README and REPORT) to 54 CISI-keyed joins and 14 excavation-number joins; replace `cisi = "-"` with null; reword the five `join_evidence` strings that name Lipi; state the source of each identifier; record the owner's decision on the 19 joins that rest on Lipi's `excavation-idno` alone and on the CISI concordance pairs.
2. **Scoring instructions.** State that `confidence` is a unit-level field (the template-one confidence in 0-1), not a property of each alternative, and that `section` (one of the three section names) is required in v2 predictions or the bootstrap intervals are NaN. I confirmed both: with documented fields only, calibration `n` is 0 instead of 252 and every v2 interval is NaN; with unit-level `confidence` and `section`, summary and bootstrap equal the staged run exactly. A validation check on the prediction file would prevent the silent case.
3. **Folder contents.** Remove or rewrite what must not be public: `RELEASE-CHECKLIST.md` (private backup ID, upload recipe, owner decisions), the private GitHub link in `README.md`, and `provenance/rights-audit.json` (1.5 MB; 1,036 private-store paths and hashes). Keep these in the package directory and ship a short exclusions list.
4. **Private-store card.** Add that the 1,034 restoration files (3,214,711 + 3,083,272,144 bytes) were removed locally by `free-local`, so the Hub copy is the only one; that `hf_host.py verify` now enumerates no local files and cannot detect a missing or damaged Hub file; and a Hub-side check (download then `verify_private_store.py`, or compare the Hub's LFS hashes with the manifest). Consider whether Hugging Face's rights terms for private repositories sit comfortably with Lipi-derived files, which `hf_host.py` itself says it avoids.
5. **Card content.** Add a short task definition, the criteria and thresholds, definitions of the metrics used in the card, a link to `CONVENTIONS.md` with its v2-only scope and the dangling folder names explained, and a sentence naming the local export (Lipi, pinned commit, not redistributed). Describe the sequence screen accurately (3,506 distinct sequences, 6,878 with both directions).
6. **Release-state text.** Put hosted `load_dataset("NAMESPACE/NAME", ...)` and `snapshot_download` examples first, drop the local-path scaffolding and "locally staged" wording, and fill or remove TODO fields before upload.

## Optional improvements

- Rename the `null` column of `weight_chance_controls` (for example `null_model`); the name is an SQL keyword and the hosted viewer was not tested.
- Reconcile the Lothal sealings title variants ("Circuits" and "Networks").
- Consolidate the repeated caveats in `FIELD-DEFINITIONS.md` into one notes block and list the `status` values.
- Add embedded image columns (or a small embedded subset) so the hosted viewer displays crops; add `language: en` and a BibTeX block to the card.
- Loosen the exact pins in `requirements.txt` (the scorer needs NumPy and PyArrow only).
- Add a dated amendment to `PROTOCOL.md` for the checker fixes.
- Report the other two jitter nulls beside 170.246/38.727, which the report quotes alone.
- Recount "105 complete singleton rows" with its basis (rows of two or more units), since 88 rows have three or more.

## Boundaries

`git status --porcelain` shows 20 untracked paths and one modified file under `experiments/2026-10-07-helsinki1979-digitization/` (Package M's ongoing v3 work) and my `review/` directory. Nothing changed in Package O's committed files or in any other directory. Temporary files are under `data/raw/2026-10-08-hf-public-release/` (`review-cache`, `hfc`, `review-scores`, `review-scan`, `review-standalone`, `tmp-review`).
