# Package O: staged dataset and private-backup description

The local [release candidate](release/README.md) has **19 Hugging Face configurations, 2,739 table rows and 949 PNGs**. All configurations load with `datasets`; every image resolves, decodes and matches its source hash. The two staged benchmarks reproduce Package M’s published metrics, row outcomes, sensitivities and bootstrap intervals. [validation.json](validation.json), `configurations`, `images`, `benchmark_scores`; [fresh-build comparison](build-replay-comparison.json), 971/971 files equal.

The candidate retains the **687-cell chart and 16 lower-code ambiguities**, **60 original and 80 repaired benchmark rows**, **306 reader records**, **68 museum-to-CISI joins**, **115 site/provenance entities** and the other tables listed below. The original references and the exploratory correction overlay remain separate. The [private-store card](private-store/README.md) describes **1,038 backed-up files and 3,406,008,409 bytes**, including the restore helper’s limited scope. Nothing was uploaded, no repository was created, no visibility changed and no Git history operation ran.

The underlying Helsinki source is CC BY 4.0. Our data CC BY 4.0 and code MIT licences are proposals awaiting the owner’s confirmation. Author, affiliation and contact remain marked placeholders in the candidate. [RELEASE-CHECKLIST.md](release/RELEASE-CHECKLIST.md) lists those decisions and the future private-review upload and visibility steps. Public release also needs a hosted-viewer check and the owner’s final decision.

## Files and repeat commands

[PROTOCOL.md](PROTOCOL.md) records selection and failure rules before packaging. [REPORT.md](REPORT.md) gives results and scope; [RETROSPECTIVE.md](RETROSPECTIVE.md) records the observed problems and fixes. [rights-audit.json](rights-audit.json), [sources.json](sources.json), [registry-entry.json](registry-entry.json) and [created-paths.json](created-paths.json) supply rights, source access, integration proposal and every created/changed path. The release’s [file-manifest.json](release/provenance/file-manifest.json) hashes every other staged file; it excludes itself to avoid a circular checksum. [Environment installation record](environment-installation.json) names the authorized venv additions.

Run from the repository root with the supplied `indus-ml` Python. `requirements.txt` inside the release records the validated packages. Set temporary/cache locations under Package O’s raw directory; the scripts do so themselves. They never call a Hub upload or repository API. Choose fresh names for output folders/files:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-hf-public-release/build_release.py --out experiments/2026-10-08-hf-public-release/reviewer-build
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-hf-public-release/write_documents.py --release experiments/2026-10-08-hf-public-release/reviewer-build
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-hf-public-release/finalize_audit.py --release experiments/2026-10-08-hf-public-release/reviewer-build
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-hf-public-release/validate_release.py --release experiments/2026-10-08-hf-public-release/reviewer-build --out experiments/2026-10-08-hf-public-release/reviewer-validation.json --raw-out data/raw/2026-10-08-hf-public-release/reviewer-validation
python -B tools/review_prose.py --path experiments/2026-10-08-hf-public-release --no-write
```

The builder needs the pinned local parent files, including Package M’s portable predictions and the seven-join supplement. The staged scorer needs only this candidate’s tables and NumPy/PyArrow. Run `release/code/score_benchmark.py --benchmark v1` or `v2` with a fresh `--out` filename. The dataset card gives examples for each configuration, images and new predictions. `verify_private_store.py` is a read-only checksum comparator for a separately restored backup; no remote restore was tested here.

## Table inventory

| Configuration | Rows |
|---|---:|
| `chart_reference` | 687 |
| `benchmark_rows_v1` | 60 |
| `benchmark_rows_v2` | 80 |
| `benchmark_readings` | 306 |
| `benchmark_chart_cards` | 21 |
| `benchmark_count_pages` | 21 |
| `benchmark_count_readings` | 42 |
| `evidence_sites` | 115 |
| `evidence_publications` | 17 |
| `evidence_collections` | 37 |
| `evidence_datasets` | 15 |
| `evidence_catalogue_coverage` | 38 |
| `evidence_catalogue_sections` | 19 |
| `evidence_field_completeness` | 140 |
| `evidence_museum_joins` | 68 |
| `evidence_sources` | 111 |
| `weight_mass_bands` | 4 |
| `weight_chance_controls` | 9 |
| `image_assets` | 949 |


## Reviewer checks

Repeat the local configuration loads, all 949 image hashes and both full score comparisons. Sample chart cells with retained alternatives, including PDF20 column4 row21’s three candidates, and inspect benchmark source boxes, underlines and invalid targets. Review the first benchmark’s 22 exposed OCR locators and v2’s reader disclosures. Compare the 19 CISI 1 ranges yielding 493/327/166 with v6 and inspect the seven new museum joins. Check proposed licences and placeholders before any upload. Raw prose/sequence scan details stay in [the local validation directory](../../data/raw/2026-10-08-hf-public-release/validation-2026-10-08-v6/); the final validation records the exact paths if its run suffix changes.
