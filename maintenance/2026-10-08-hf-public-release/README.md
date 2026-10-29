# Package O: release version 0.3.1

The [release folder](release/README.md) contains **23 configurations, 3,308 rows and 1,142 images**. All loads, schemas, source values and images pass; the scorer reproduces v1/v2/v3 with **zero mismatches**. A fresh build matches **137/137 files**, totaling **25,292,479 bytes**. [Final validation](validation-2026-10-08-v45.json), configurations, images, benchmark_scores, review_checks and rebuild.

Prediction files can use the card's `printed_inscription_id` and `classification_literal` keys or the frozen aliases. The scorer rejects missing keys, conflicting values and numeric values supplied where strings are required; null is allowed. Minimal card-only files reproduce **23/19 of 60, 62/55 of 80 and 71/72 of 80** correct numbers/classifications. All **27 new format cases** pass: nine valid files and eighteen rejected files. [Prediction-format check](prediction-format-2026-10-08-v41.json), cases.

The independent readings now flag P's **26 definite changes**: six v1 A, five v1 B and fifteen v2 A units. V3 has **eight per reader**. V2 reader B's 20 corrected-cell units include eight additional shape-only-location joins; its class-metadata count is seven rather than the strict-location count six. [Flag check](reading-flags-2026-10-08-v41.json), group_counts and v2_reader_b_additional_shape_only_units. Frozen payloads and default scores remain unchanged.

The card distinguishes Claude Sonnet in earlier evaluations from Claude Sonnet 5.5 in v3, explains the frames and census/process terms, and includes public chart review priorities. CFF version 0.3.1 validates against the official schema without an alternative-licence list. Licences remain CC BY 4.0 for edition content, CC0 for project additions/data/documentation and Unlicense for code; author alias k-sandhu. [REPORT.md](REPORT.md) gives the results and their limits.

## Repeat from the repository root

Choose unused short names for outputs and caches. The builder reuses local parent files and official licence texts; it repeats no recognition, census query or mass fit. Ordinary builds write their public folder and separate build records. `--update-owner-records` explicitly refreshes the checklist, private-store card and root audit; it is unnecessary for a review rebuild.

```powershell
$releasePython = 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe'
$releasePackage = 'maintenance/2026-10-08-hf-public-release'
& $releasePython -B "$releasePackage/build_release.py" --out "$releasePackage/check31"
& $releasePython -B "$releasePackage/validate_release.py" --release "$releasePackage/check31" --records "$releasePackage/build-records/check31" --out "$releasePackage/check31-validation.json" --raw-out data/raw/2026-10-08-hf-public-release/check31
& $releasePython -B "$releasePackage/check_prediction_format.py" --release "$releasePackage/check31" --out "$releasePackage/check31-format.json" --raw-out data/raw/2026-10-08-hf-public-release/check31-format
& $releasePython -B "$releasePackage/check_reading_flags.py" --release "$releasePackage/check31" --out "$releasePackage/check31-flags.json"
& $releasePython -B "$releasePackage/check_review_fixes.py" --release "$releasePackage/check31" --out "$releasePackage/check31-rights-cff.json" --raw-out data/raw/2026-10-08-hf-public-release/check31-cff
& $releasePython -B "$releasePackage/compare_release_v031.py" --rebuild "$releasePackage/check31" --out "$releasePackage/check31-preservation.json" --review-out data/raw/2026-10-08-hf-public-release/check31-rebuild-review.json
& $releasePython -B "$releasePackage/rerun_review_v031.py" --out data/raw/2026-10-08-hf-public-release/check31-review
python tools/review_prose.py --path $releasePackage --no-write
```

The reviewer rerun reads the working release folder. Its Hub loader/snapshot calls use local substitutes; it makes no network request. The coordinator's private **0.3.0** preview was verified at commit **541766d5ea8a4c3b3ec5fcc416ee764af8763afb**: 23 configurations, 3,308 rows and 136 matching files. [REVIEW-0.3.0.md](REVIEW-0.3.0.md). Hosted 0.3.1 and the public viewer remain coordinator checks after upload; the private viewer returned HTTP 501.

Reused inputs are chart audit reference/comparison/impact 2.1, original atlas crops, M's three frozen packets/scorers, census consolidation and trimmed registers, independently cited museum supplements, metrology aggregates and protected reviewer scripts. The full reviewed folder and code are preserved in history/. Earlier validations, review/ and review-0.3.0/ remain unchanged. [Changed-path inventory](created-paths-v0.3.1-2026-10-08.json) enumerates every created/changed file. [PROTOCOL.md](PROTOCOL.md), [RETROSPECTIVE.md](RETROSPECTIVE.md), [rights-audit.json](rights-audit.json), build-records/r41/ and [sources.json](sources.json) retain decisions, hashes and access scope. The shared registry is unchanged; [registry-entry.json](registry-entry.json) is the proposal.

The [owner checklist](RELEASE-CHECKLIST.md) retains three decisions: public issues repository, private-store Hub terms and final visibility. No upload, repository creation, visibility change or other package edit occurred. The [private-store card](private-store/README.md) retains recovery instructions.

Reviewers should repeat the 23 loads, 1,142 image checks, three score/interval comparisons, card-only prediction tests, 26 earlier and 16 v3 independent flags, CFF/privacy scans and 137-file rebuild. Inspect the eight additional v2 reader B joins and chart expert-review priorities. After private upload, repeat hosted loads and snippets; check all image-bearing viewer tables and 23 selectors after approved public visibility.

## Configuration counts

| Configuration | Rows |
|---|---:|
| `chart_reference` | 687 |
| `benchmark_rows_v1` | 60 |
| `benchmark_rows_v2` | 80 |
| `benchmark_rows_v3` | 80 |
| `benchmark_readings` | 306 |
| `benchmark_readings_v3` | 240 |
| `benchmark_chart_cards` | 33 |
| `benchmark_count_pages` | 21 |
| `benchmark_count_readings` | 42 |
| `benchmark_count_pages_v3` | 21 |
| `benchmark_count_readings_v3` | 42 |
| `evidence_sites` | 115 |
| `evidence_publications` | 17 |
| `evidence_collections` | 37 |
| `evidence_datasets` | 15 |
| `evidence_catalogue_coverage` | 38 |
| `evidence_catalogue_sections` | 19 |
| `evidence_field_completeness` | 140 |
| `evidence_museum_joins` | 49 |
| `evidence_sources` | 111 |
| `weight_mass_bands` | 4 |
| `weight_chance_controls` | 9 |
| `image_assets` | 1142 |

