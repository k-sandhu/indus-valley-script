---
pretty_name: Indus chart, row-reading benchmarks and evidence census
license:
- cc-by-4.0
- mit
tags:
- indus-script
- epigraphy
- archaeology
- undeciphered-script
- image-to-text
- research-data
task_categories:
- image-to-text
size_categories:
- 1K<n<10K
configs:
- config_name: chart_reference
  data_files:
  - split: train
    path: data/chart_reference.parquet
- config_name: benchmark_rows_v1
  data_files:
  - split: test
    path: data/benchmark_rows_v1.parquet
- config_name: benchmark_rows_v2
  data_files:
  - split: test
    path: data/benchmark_rows_v2.parquet
- config_name: benchmark_readings
  data_files:
  - split: test
    path: data/benchmark_readings.parquet
- config_name: benchmark_chart_cards
  data_files:
  - split: train
    path: data/benchmark_chart_cards.parquet
- config_name: benchmark_count_pages
  data_files:
  - split: train
    path: data/benchmark_count_pages.parquet
- config_name: benchmark_count_readings
  data_files:
  - split: train
    path: data/benchmark_count_readings.parquet
- config_name: evidence_sites
  data_files:
  - split: train
    path: data/evidence_sites.parquet
- config_name: evidence_publications
  data_files:
  - split: train
    path: data/evidence_publications.parquet
- config_name: evidence_collections
  data_files:
  - split: train
    path: data/evidence_collections.parquet
- config_name: evidence_datasets
  data_files:
  - split: train
    path: data/evidence_datasets.parquet
- config_name: evidence_catalogue_coverage
  data_files:
  - split: train
    path: data/evidence_catalogue_coverage.parquet
- config_name: evidence_catalogue_sections
  data_files:
  - split: train
    path: data/evidence_catalogue_sections.parquet
- config_name: evidence_field_completeness
  data_files:
  - split: train
    path: data/evidence_field_completeness.parquet
- config_name: evidence_museum_joins
  data_files:
  - split: train
    path: data/evidence_museum_joins.parquet
- config_name: evidence_sources
  data_files:
  - split: train
    path: data/evidence_sources.parquet
- config_name: weight_mass_bands
  data_files:
  - split: train
    path: data/weight_mass_bands.parquet
- config_name: weight_chance_controls
  data_files:
  - split: train
    path: data/weight_chance_controls.parquet
- config_name: image_assets
  data_files:
  - split: train
    path: data/image_assets.parquet
---

# Indus chart, row-reading benchmarks and evidence census

This locally staged candidate contains the 687-cell Helsinki sign chart, two frozen row-reading benchmarks of 60 and 80 rows, and selected evidence-census and metrology tables. It is awaiting the owner’s licensing and authorship decisions in [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md). The underlying 1979 source has an explicit CC BY 4.0 licence; CC BY 4.0 for our annotations and compilations and MIT for our code are proposals. The YAML licence list describes the intended component licences after confirmation.

The Indus script is a set of signs found on seals, sealings, tablets, pottery and other objects associated with the Indus civilization in South Asia. Most inscriptions are short. Its language, sound values and readings remain unresolved. This dataset records printed drawings, graphic inventory labels, annotation judgments and measurements that can be inspected without assigning meanings to the signs. The 1979 edition is an interim corpus and omits later discoveries; its printed occurrences and sorted repetitions are different units from independently excavated objects.

## Configurations and construction

| Configuration | Rows | Contents |
|---|---:|---|
| `chart_reference` | 687 | 687 chart cells and 16 retained lower-code ambiguities. |
| `benchmark_rows_v1` | 60 | 60 source rows with immutable references and frozen predictions. |
| `benchmark_rows_v2` | 80 | 80 source rows with immutable references and frozen predictions. |
| `benchmark_readings` | 306 | Initial, repeated, independent and adjudicated readings; frozen endpoints remain distinct. |
| `benchmark_chart_cards` | 21 | Original chart-only cards supplied to benchmark readers. |
| `benchmark_count_pages` | 21 | 21 source-count pages: 18 random and 3 stress pages; geometric detections for recall. |
| `benchmark_count_readings` | 42 | 42 independent page inventories from the two readers. |
| `evidence_sites` | 115 | 115 site/provenance entities from synthesis v6; aggregate counts in distinct source frames. |
| `evidence_publications` | 17 | 17 bibliographic register entries; historical catalogue coverage is documented separately. |
| `evidence_collections` | 37 | 37 institution observations; null counts are unmeasured, zero counts are bounded queries. |
| `evidence_datasets` | 15 | 15 dataset observations with dated count bases; no underlying corpora bundled. |
| `evidence_catalogue_coverage` | 38 | Synthesis v6 authored aggregate table; frame and measurement columns define denominators. |
| `evidence_catalogue_sections` | 19 | Synthesis v6 authored aggregate table; frame and measurement columns define denominators. |
| `evidence_field_completeness` | 140 | Synthesis v6 authored aggregate table; frame and measurement columns define denominators. |
| `evidence_museum_joins` | 68 | 68 authored museum-accession to published CISI identifier joins; local corpus record contents excluded. |
| `evidence_sources` | 111 | Bibliographic pointers and inherited access scopes; this packaging run did not reopen each archaeological source. |
| `weight_mass_bands` | 4 | Aggregate metrology results after review; no Ascalone catalogue records included. |
| `weight_chance_controls` | 9 | Aggregate metrology results after review; no Ascalone catalogue records included. |
| `image_assets` | 949 | Every staged licensed PNG with relative path, parent path and SHA256. |


`chart_reference` combines the project’s retained numeric-label reference with the atlas crops from PDF pages 20–21. AI models read the upper ranks and lower codes and rechecked disagreements. Sixteen lower-code ambiguities remain in `alternatives`. Crops can contain neighbouring ink. No expert has certified these labels or the glyph inventory.

`benchmark_rows_v1` selects 60 numbered-section occurrences on PDF pages 31–79, using a saved random sample from 3,460 detected occurrences. Three AI readers supplied disjoint initial groups. Six convenience repeat readings and a later exploratory eleven-code correction overlay are included separately; the original references remain the scoring endpoint. OCR locator strings were exposed for 22 of 60 rows. The original frozen evaluation reports 33/60 matching unit counts, 23/60 correct inscription numbers and 24/60 top-five compatible whole rows.

`benchmark_rows_v2` selects 80 fresh rows across the numbered, end-sorted and beginning-sorted sections with quotas 28/26/26, excluding development pages and the first targets. Two AI readers read every row, and a third AI reader adjudicated against source images and the chart. Their initial readings, page inventories and adjudication notes are retained. Shared scratch-directory collisions and directory-list observations reduced process isolation; [reader-metadata.json](benchmark/reader-metadata.json) preserves the recorded disclosures. The frozen pipeline has 44/80 accepted crops, 59/80 matching counts, 62/80 correct numbers, 55/80 correct classifications, 20/80 top-one and 40/80 top-five compatible whole rows. Top-five aligned unit recall is 304/352. Random-page row recall is 1,242/1,286 across 18 pages, with 561/561 on three stress pages. Four of five pipeline criteria failed. The full provisional transcription remains excluded.

The evidence tables select facts, bibliographic identifiers, aggregate counts and authored assessments from the census synthesis v6 and trimmed registers. `evidence_sites` uses v6’s 115 reconciled site/provenance entities. The 17-entry publication register remains a bibliographic register; its earlier site census was superseded by the regional synthesis. `evidence_museum_joins` gives 68 accession-to-CISI correspondences, comprising 61 earlier audited joins and seven v6 additions. The seven additions have not received the earlier pairs’ full field adjudication. Corpus record contents and museum descriptions/images are absent. Catalogue keys, faces and provisional object families have different denominators: 327 of 493 keys match in 19 inspected CISI 1 Gujarat/north India ranges, leaving 166 absent under the matching rules. Seventy-five absent keys occur in pottery/graffiti sections and 91 in other sections. These counts cannot be added into a worldwide missing-object total.

`evidence_field_completeness` retains measured presence, structural schema absences and inherited assessments as separate `measurement` values. Null is unmeasured. The museum registers describe bounded queries on 7 October 2026; they are historical observations, not current inventories. `weight_mass_bands` and `weight_chance_controls` contain aggregate results from the corrected exploratory metrology study. The 5–100 g Dholavira band has 90 weights and a fitted unit of 13.716 g; the 1.3–5 g band has 147 and a unit of 14.280 g. Catalogue-level weight records are excluded. The private metrology [method report](https://github.com/k-sandhu/indus-valley-script/blob/research/2026-10-06-program/experiments/2026-10-06-weight-metrology/REPORT.md) is an evidence pointer; public access and complete analysis-code distribution require an owner decision.

## Load tables and images

The configuration list follows Hugging Face’s [manual configuration documentation](https://huggingface.co/docs/hub/datasets-manual-configuration). Every table is one Parquet file with a stable schema. Benchmark row configurations use the `test` split; other `train` split names are loader labels for whole tables and do not define a machine-learning training split.

```python
from datasets import load_dataset

# From the repository root, before any upload:
repo = "experiments/2026-10-08-hf-public-release/release"
# After the owner uploads and supplies the new ID, replace repo with it.
chart = load_dataset(repo, "chart_reference", split="train")
rows = load_dataset(repo, "benchmark_rows_v2", split="test")
sites = load_dataset(repo, "evidence_sites", split="train")
```

The same call loads every named configuration in the table. This loop loads all configurations with their correct splits:

```python
from datasets import get_dataset_config_names, load_dataset
tables = {name: load_dataset(repo, name)
          for name in get_dataset_config_names(repo)}
```

Nested readings and predictions are lossless JSON strings so varying optional observation fields do not destabilize the table schema. Parse them with `json.loads`. PNG paths are relative to the dataset root and intentionally remain strings. The table viewer can show every table; image paths require a downloaded snapshot to open. The hosted viewer has not been tested because this task made no upload.

```python
import json
from pathlib import Path
from PIL import Image

reference = json.loads(rows[0]["reference_json"])
image = Image.open(Path(repo) / rows[0]["context_image_path"])
# For a hosted repository, obtain the PNGs and code first:
# from huggingface_hub import snapshot_download
# folder = Path(snapshot_download(repo, repo_type="dataset"))
# image = Image.open(folder / rows[0]["context_image_path"])
```

## Score a new row reader

Install [requirements.txt](requirements.txt). Start with the archived pipeline scores:

```powershell
python -B experiments/2026-10-08-hf-public-release/release/code/score_benchmark.py --benchmark v1 --out data/raw/2026-10-08-hf-public-release/my-v1-score.json
python -B experiments/2026-10-08-hf-public-release/release/code/score_benchmark.py --benchmark v2 --out data/raw/2026-10-08-hf-public-release/my-v2-score.json
```

For a downloaded standalone dataset, run `python -B code/score_benchmark.py --benchmark v2 --out my-score.json` from its root. To score your reader, supply `--predictions your-predictions.jsonl`. Give exactly one row per `sample_index`, with `occurrence_key`, `pdf_page`, `inscription_number` (string or null), `classification_code` (literal five positions or null), and `units` in visual left-to-right order. Each unit has `alternatives`: a ranked list of objects with `codes` (integer candidate list), and optional `confidence`. Copy locator keys from the benchmark, and provide your own recognition outputs. The stored `prediction_json` objects show the complete accepted format. Keep a new evaluation output path on every run.

The scorer preserves Package M’s candidate-set edit alignment, Wilson intervals, equal-count calibration and seeded bootstrap. Top one/five means one/five ranked image templates; a template can retain several numeric candidates. A unit matches when its candidate set intersects the reference set. Whole-row compatibility requires zero edits and a fully resolved reference. This measures compatibility with retained candidates; singleton exactness is reported separately. V2 invalid printed targets count as row failures. Row-recall uses source-column geometry with a nine-PDF-point matching tolerance. The default includes 2,000 bootstrap draws; `--no-bootstrap` provides a faster summary. [expected-metrics.json](benchmark/expected-metrics.json) records the published targets. New model scoring retains the archived crop judgments and row-detection geometry; a new crop/detector requires source-based judgments before its segmentation or recall can be evaluated.

## Fields, provenance and licences

[FIELD-DEFINITIONS.md](FIELD-DEFINITIONS.md) defines every table field, nulls, inventory labels and nested row objects. [table-manifest.json](provenance/table-manifest.json) records schemas, row counts and hashes. [input-manifest.json](provenance/input-manifest.json) pins the parent files, and [rights-audit.json](provenance/rights-audit.json) records each selection. Repository paths identify the private research record; they are not promised public downloads. [evidence_sources](data/evidence_sources.parquet) and [sources.json](sources.json) provide bibliographic pointers and access scopes.

Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki. [Official final-version record](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [persistent handle](http://hdl.handle.net/10138/342677), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The chart, row crops, chart cards, count-page images and source-derived readings carry this attribution. Changes consist of raster cropping, arranging chart cards, reading numeric labels, annotating candidate sets and computing recognition scores. No endorsement by the source authors is implied. The original PDF is not included.

Our compilations, protocols, annotation contributions and aggregate results are proposed under CC BY 4.0; our scorer is proposed under MIT. Those grants await the owner’s confirmation. External catalogues are cited for facts and identifiers; their source text, scans and images are not covered by these proposed terms. [LICENSE](LICENSE), [NOTICE](NOTICE) and [LICENSE-MIT](LICENSE-MIT) state component scopes and pending decisions.

## Status, AI assistance, citation and corrections

Chart labels and source readings were produced with AI assistance. AI agents prepared crops, recognition proposals, independent readings, adjudication, census assessments, code and this packaging documentation. Numerical reproduction can verify those outputs; it does not replace expert epigraphic review. Census and metrology findings remain Exploratory. The benchmark predictions and reference sets are Frozen evaluation records from two failed pipeline tests. This release contains no authenticated sounds, meanings or decipherment.

Author: **TODO: owner-confirmed author name**. Affiliation: **TODO: affiliation or none**. Contact: **TODO: error-report address**. Candidate date: 8 October 2026. Cite the dataset version and repository revision using [CITATION.cff](CITATION.cff), and cite Koskenniemi and Parpola’s 1979 edition when using its derivatives. No DOI or public repository ID has been assigned. Error reports should give configuration, cell ID or benchmark/index, source page/box, observed problem and a source-based correction. Use the future dataset’s discussion page or the owner’s confirmed contact; the owner has not yet supplied either public destination.
