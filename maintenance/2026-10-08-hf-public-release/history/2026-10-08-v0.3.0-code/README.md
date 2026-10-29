# Package O: release version 0.3.0

The [release folder](release/README.md) contains **23 configurations, 3,308 rows and 1,142 images**. It adopts P's corrected chart reference 2.1 and adds the third frozen 80-row benchmark. Every local load, schema, source field and image check passes; v1/v2/v3 scoring has **zero mismatches**. [Final validation](validation-2026-10-08-v38.json), configurations, source_checks, images and benchmark_scores.

The chart has **687 cells, eight primary-code corrections, two class corrections and 16 provisionally settled ambiguities**. Previous-value fields document 36 changed numeric records; 33 cells have medium confidence. It remains Exploratory: two AI readings and a pixel check, no expert review. Benchmark payloads retain their earlier card labels. Separate unit flags preserve 11/0/8 direct candidate changes, 0/18/31 identity warnings and the v3 locator conflict. Corrected-label rescoring is deferred under [P's recommendation](../2026-10-08-chart-reference-audit/RECOMMENDED-USE.md).

Frozen strict top-five scores remain **24/60, 40/80 and 62/80**. V3 random-page physical-line recall is **1,296/1,296**; numbered recall is **1,289/1,289**. Both repair pipelines fail four of five criteria against AI references. The full transcription remains quarantined. [REPORT.md](REPORT.md) gives the frames, provenance and sensitivity.

The folder has **136 files and 25,287,707 bytes**, with 1,067 embedded PNGs and 75 loose PNGs. A fresh build matches **136/136 files byte for byte**. Privacy has zero hits. Rights screening finds zero graphic-code runs; twelve generic hits are agreed-unit index lists. [Reviewer rerun](review-rerun-2026-10-08-v35.json) and [rebuild comparison](rebuild-comparison-2026-10-08-v37.json).

## Repeat from the repository root

Use fresh short names. The builder reuses local parent files and official licence texts; it runs no recognition or Hub query. Validation uses datasets, PyArrow, NumPy, Pillow, PyYAML and jsonschema from the existing indus-ml environment.

```powershell
$releasePython = 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe'
$releasePackage = 'experiments/2026-10-08-hf-public-release'
& $releasePython -B "$releasePackage/build_release.py" --out "$releasePackage/check30"
& $releasePython -B "$releasePackage/validate_release.py" --release "$releasePackage/check30" --records "$releasePackage/build-records/check30" --out "$releasePackage/check30-validation.json" --raw-out data/raw/2026-10-08-hf-public-release/check30
& $releasePython -B "$releasePackage/check_review_fixes.py" --release "$releasePackage/check30" --out "$releasePackage/check30-input-check.json" --raw-out data/raw/2026-10-08-hf-public-release/check30-input
& $releasePython -B "$releasePackage/rerun_review.py" --release "$releasePackage/check30" --records "$releasePackage/build-records/check30" --out data/raw/2026-10-08-hf-public-release/check30-review
& $releasePython -B "$releasePackage/record_release_v3.py" --rebuild "$releasePackage/check30" --out "$releasePackage/check30-preservation.json"
python tools/review_prose.py --path $releasePackage --no-write
```

Reused inputs are P's current reference/comparison/impact, original atlas cells, M's frozen packets/crops/predictions/scorers, census synthesis v6 and trimmed registers, the independently cited museum supplement and reviewed metrology tables. No recognition, census query or mass fit was repeated. The standalone scorer uses only uploaded tables and NumPy/PyArrow; hosted examples are in the card.

The 0.2.0 folder and code are preserved in history/. Earlier validation files and review/ scripts are unchanged. [Changed-path inventory](created-paths-v0.3.0-2026-10-08-v2.json) enumerates new/changed files and preserved folders. [PROTOCOL.md](PROTOCOL.md), [RETROSPECTIVE.md](RETROSPECTIVE.md), [rights-audit.json](rights-audit.json), build-records/r35/ and [sources.json](sources.json) retain decisions, pins and access scope. The shared registry was not edited; [registry-entry.json](registry-entry.json) is the integration proposal.

Owner licences remain CC0 for project data/documentation/additions, Unlicense for code and CC BY 4.0 for edition content, with k-sandhu authorship. [Owner checklist](RELEASE-CHECKLIST.md) retains the issues repository, private-store Hub terms and final visibility decisions. The coordinator reports all 19 configurations and images loading for private 0.2.0. Hosted 0.3.0 checks follow its update; no upload occurred here. [Private-store card](private-store/README.md) retains restore and remote-verification instructions.

Repeat all 23 loads, three score/interval comparisons, 1,142 image hashes, correction joins, eight failing prediction cases, CFF/privacy checks and the 136-file rebuild. Sample medium chart cells and AI-reference disclosures. After updating the private preview, check v3 viewer images and the owner-selected issues link.

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

