---
pretty_name: Indus chart, row-reading benchmarks and evidence census
license:
- cc0-1.0
- cc-by-4.0
- unlicense
language:
- en
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

This dataset contains 687 annotated Helsinki chart cells, two frozen row-reading benchmarks of 60 and 80 rows, an evidence census and small metrology summaries. The chart and benchmark row tables have embedded image columns for the dataset viewer. Its 19 Parquet configurations contain 2,720 rows counting heterogeneous observations, images and readings.

The Indus script is a set of signs found on seals, sealings, tablets, pottery and other objects associated with the Indus civilization in South Asia. Most inscriptions are short; their language and sound values remain unresolved. This dataset supports reading printed drawings and comparing graphic inventory labels without assigning meanings to the signs. The 1979 edition is an interim corpus that omits later discoveries. Its numbered and sorted printed occurrences can repeat a text or object.

## Load tables and images

Install `datasets`, `huggingface_hub` and Pillow. Choose one named configuration for each table:

```python
from datasets import load_dataset, get_dataset_config_names
repo = "ksaw008/indus-reference-benchmarks"
chart = load_dataset(repo, "chart_reference", split="train")
rows = load_dataset(repo, "benchmark_rows_v2", split="test")
sites = load_dataset(repo, "evidence_sites", split="train")
print(chart[0]["image"].size, rows[0]["context_image"].size)
tables = {name: load_dataset(repo, name) for name in get_dataset_config_names(repo)}
```

`chart_reference.image`, `benchmark_rows_v1.context_image` and v2 `context_image` and `exact_image` decode as Pillow images and can appear in the Hub viewer. Path columns retain logical PNG names for provenance; embedded PNGs are stored once in Parquet. Chart cards and count-page renders remain loose PNGs. Download a snapshot for those images, conventions and the scorer; pin `revision` to a chosen dataset commit for a repeatable analysis:

```python
from huggingface_hub import snapshot_download
from pathlib import Path
from PIL import Image
snapshot = Path(snapshot_download("ksaw008/indus-reference-benchmarks", repo_type="dataset"))
cards = load_dataset(repo, "benchmark_chart_cards", split="train")
card_image = Image.open(snapshot / cards[0]["image_path"])
```

For a cloned snapshot, substitute its folder for `repo` in `load_dataset`. Run `python code/extract_images.py --release . --out extracted` from its root if a tool needs loose chart/row PNGs. The scorer uses Parquet and needs no image extraction. `test` contains benchmark rows/readings; `train` on other configurations is a whole-table loader label.

## Components and construction

| Configuration | Rows | Contents | Licence |
|---|---:|---|---|
| `chart_reference` | 687 | 687 chart cells and 16 retained lower-code ambiguities. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_rows_v1` | 60 | 60 source rows with immutable references and frozen predictions. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_rows_v2` | 80 | 80 source rows with immutable references and frozen predictions. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_readings` | 306 | Initial, repeated, independent and adjudicated readings; frozen endpoints remain distinct. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_chart_cards` | 21 | Original chart-only cards supplied to benchmark readers. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_count_pages` | 21 | 21 source-count pages: 18 random and 3 stress pages; geometric detections for recall. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_count_readings` | 42 | 42 independent page inventories from the two readers. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `evidence_sites` | 115 | 115 site/provenance entities from synthesis v6; aggregate counts in distinct source frames. | CC0 1.0 |
| `evidence_publications` | 17 | 17 bibliographic register entries; historical catalogue coverage is documented separately. | CC0 1.0 |
| `evidence_collections` | 37 | 37 institution observations; null counts are unmeasured, zero counts are bounded queries. | CC0 1.0 |
| `evidence_datasets` | 15 | 15 dataset observations with dated count bases; no underlying corpora bundled. | CC0 1.0 |
| `evidence_catalogue_coverage` | 38 | Synthesis v6 authored aggregate table; frame and measurement columns define denominators. | CC0 1.0 |
| `evidence_catalogue_sections` | 19 | Synthesis v6 authored aggregate table; frame and measurement columns define denominators. | CC0 1.0 |
| `evidence_field_completeness` | 140 | Synthesis v6 authored aggregate table; frame and measurement columns define denominators. | CC0 1.0 |
| `evidence_museum_joins` | 49 | 49 independently cited museum-to-CISI identifier correspondences: 42 earlier pairs and seven supplement rows. | CC0 1.0 |
| `evidence_sources` | 111 | Bibliographic pointers and inherited access scopes; this packaging run did not reopen each archaeological source. | CC0 1.0 |
| `weight_mass_bands` | 4 | Aggregate metrology results after review; no Ascalone catalogue records included. | CC0 1.0 |
| `weight_chance_controls` | 9 | Aggregate metrology results after review; no Ascalone catalogue records included. | CC0 1.0 |
| `image_assets` | 949 | 949 licensed PNGs with logical names, storage, portable parent labels and SHA256. | CC BY 4.0 edition content; CC0 1.0 project additions |


`chart_reference` combines atlas crops from PDF pages 20–21 with numeric-label annotations. AI models read upper ranks and lower graphic codes and rechecked disagreements. Sixteen lower-code ambiguities remain in `alternatives`; crops can contain neighbouring ink. These AI-read labels await expert certification.

The row-reading task gives a system row context, a proposed target box and chart cards. It returns the printed inscription number, its five-position classification and a visual left-to-right sequence of units, each with ranked graphic-code candidate sets. The frozen baseline is a chart-only template matcher. Inventory codes are edition labels.

v1 samples 60 numbered-section occurrences from 3,460 detections on PDF pages 31–79. Three AI readers supplied disjoint initial groups; six convenience repeat readings are separate records. An **exposed OCR locator** means the original locator metadata contained OCR strings before the blinding correction, affecting 22/60 targets. The **eleven-code overlay** records eleven later source-based code corrections; it is Exploratory and does not alter the frozen v1 endpoint. That endpoint matches 33/60 unit counts, reads 23/60 inscription numbers and produces 24/60 top-five compatible whole rows.

v2 selects 80 fresh targets in `number_order`, `end_sorted` and `beginning_sorted`, with quotas 28/26/26, excluding development pages and v1 targets. Two AI readers read every row; a third adjudicated against source images and the chart. Independent readings, page inventories and adjudication notes are preserved. Shared scratch collisions and directory observations reduced process isolation; [reader metadata](benchmark/reader-metadata.json) retains the disclosures.

The v2 baseline accepts 44/80 crops, matches 59/80 counts, reads 62/80 numbers and 55/80 classifications, and produces 20/80 top-one and 40/80 top-five compatible whole rows. A **compatible whole row** has nonempty strict reference sets at every unit and zero candidate-set edit distance to the prediction, with intersections at each aligned position. **Aligned unit recall** maximizes matching intersections among minimum-edit alignments and divides by resolved reference units. Top-five recall is 304/352. Random-page recall is 1,242/1,286 across 18 pages; three stress pages give 561/561.

The five v2 pass criteria are crop correctness ≥90% (72/80), inscription-number accuracy ≥90% (72/80), unit-count agreement ≥95% (76/80), top-five compatible whole rows ≥80% (64/80), and random-page recall ≥95%. Only the last passes. The full provisional transcription is excluded.

The [reading convention](benchmark/CONVENTIONS.md) applies to v2. Its `position-chart/` means the v2 cards in `benchmark_chart_cards`; `page-count-source/` means the count-page PNGs in `benchmark_count_pages.image_paths`. Its withheld `predictions.json` is represented here by `prediction_json`; `frame.json` was the full detector frame and is excluded. The convention describes independent reading before predictions were opened.

The census selects facts, citations, counts and project assessments from synthesis v6 and trimmed registers: 115 site/provenance entities, 17 publications, 37 collections and 15 datasets. `local_faces`, `local_families` and `local_cisi_identifiers` count the Lipi export pinned at commit `fc8813a52e183d19c441631dc26c33a4dccbea39`. That export has no licence; only aggregates are published. Faces, provisional families and catalogue entries have distinct denominators. In 19 inspected CISI 1 Gujarat/north India ranges, 327/493 keys match and 166 are absent under the matching rule: 75 in pottery/graffiti sections and 91 in other sections. A worldwide missing-object denominator was not established.

`evidence_museum_joins` has 49 independently cited accession-to-CISI correspondences: 42 earlier pairs and seven supplement rows. Identifier-source citations distinguish museum identifiers, printed CISI 1 concordances and the Marshall composite table. The supplement awaits the earlier pairs' complete field adjudication. Museum descriptions and photographs are excluded. Collection and field-completeness observations are bounded historical queries; null denotes unmeasured values. [FIELD-DEFINITIONS.md](FIELD-DEFINITIONS.md) documents every field and shared assumption.

The exact Frenez–Tosi 2005 title is *Lothal Sealings: Records from an Indus Civilization town at the eastern end of the maritime trade networks across the Arabian Sea*. The longer wording beginning “The Lothal Sealings” came from the earlier publication register; public tables use the [Zenodo record](https://zenodo.org/records/5514283).

The weight tables contain Exploratory fits and simulations. A **fitted unit** is a hypothesized common base mass under specified multiplier and noise rules. Dholavira's 5–100 g band has 90 weights and a 13.716 g unit; the 1.3–5 g band has 147 weights and a 14.280 g unit. The legacy western screen observes 136 geometric and 18 close hits. Mean geometric/close counts in its three nulls are 170.246/38.727 (±0.15 log jitter), 208.5675/50.3805 (±0.35 log jitter) and 193.9825/44.2695 (site log-uniform), with 2,000 draws each. All exceed the observations. [Methods](docs/METHODS.md#weight-metrology) describe the fit and controls. Excluded catalogue measurements and the full fitting pipeline are needed to repeat the original fit.

## Score a new row reader

Install scorer dependencies with `python -m pip install -r requirements.txt` from the snapshot. Supply one prediction for every sample as a JSON list, an object containing `rows`, or JSON Lines. Required row fields are `sample_index`, `occurrence_key`, `pdf_page`, `printed_inscription_id`, `classification_literal` and `units`. v2 requires `section`: `number_order`, `end_sorted` or `beginning_sorted`. Copy frozen identifiers/section when preparing predictions. Preserve five classification positions, including blank spaces. Number and classification may be null.

Each unit requires `confidence`, the template-one confidence as a finite number in [0, 1], and ranked `alternatives`, each containing `codes`, an integer list. Confidence belongs to the unit and supplies top-one strict-intersection calibration. An alternative may contain several codes. This is an illustrative format example:

```json
{"confidence": 0.7, "alternatives": [{"codes": [25]}, {"codes": [2]}]}
```

```python
import subprocess, sys
subprocess.run([
    sys.executable, str(snapshot / "code/score_benchmark.py"),
    "--release", str(snapshot), "--benchmark", "v2",
    "--predictions", "my-predictions.jsonl", "--out", "my-scores.json"
], check=True)
```

The scorer rejects missing unit confidence and missing/invalid v2 section. Omit `--predictions` to reproduce the frozen baseline. Outputs include candidate widths, count/number/classification accuracy, alignments, calibration and 2,000-draw intervals. It refuses to overwrite an output. v2 source-row recall uses preserved detector geometry; new row predictions do not evaluate a new detector. [Expected metrics](benchmark/expected-metrics.json) preserve the baseline targets.

## Provenance, rights and limitations

Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki, ISBN 951-45-1627-3. The [official final-version record](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/) supplies [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the persistent handle is [10138/342677](http://hdl.handle.net/10138/342677). Edition-derived crops, chart cells/cards, page renders, inscription numbers, classifications and sign numbering retain that licence. The project waives its rights in additions to mixed configurations under CC0 1.0. Own compilations, readings, annotations, aggregates and documentation use CC0 1.0; code uses the Unlicense. The component table, [LICENSE](LICENSE), official texts in `LICENSES/` and [NOTICE](NOTICE) specify the structure and changes.

AI assistance produced chart labels, independent benchmark readings/adjudication, the template pipeline, research code and documentation. The chart and benchmark await expert epigraphic certification. `Frozen evaluation` identifies preserved evidence; `Exploratory` identifies annotations, later corrections and census/metrology interpretations. Reproduced arithmetic has `Verified computation` status; the baseline's criterion outcome is `Failed`. This dataset makes no decipherment claim.

The packaging sequence screen read `lipi_observed_faces.jsonl` and `mayig_faces.jsonl` for sequences of at least two units in both recorded directions: 3,506 distinct forward sequences and 6,878 distinct sequences counting both directions. It preserved Mayig's `P` namespace. The 105 complete singleton benchmark reference rows each have at least two units and exactly one strict candidate per unit; none equalled a whole indexed sequence in either direction. A broader reviewer scan normalized namespaces and tested runs of at least three positions across six derivatives, finding zero sequence runs and detecting all 200 planted controls. These screens cover their input files and numbering; reuse after recoding is outside their reach. Text comparisons found no unexplained copied third-party prose; exact bibliography and official licence text are recorded separately.

[sources.json](sources.json) and `evidence_sources` give exact citations and access scopes, including inherited and snippet-only access. Portable `source-` labels identify original witnesses whose parent payloads are excluded. [EXCLUSIONS.md](EXCLUSIONS.md) lists omissions. The image manifest gives logical names, storage and PNG hashes; the file manifest lists every release file except itself.

## Citation and error reports

k-sandhu (2026). *Indus chart, row-reading benchmarks and evidence census*, version 0.2.0. [Dataset](https://huggingface.co/datasets/ksaw008/indus-reference-benchmarks). Cite Koskenniemi and Parpola (1979) when using edition-derived content.

```bibtex
@dataset{indus2026reference,
  author = {k-sandhu},
  title = {Indus chart, row-reading benchmarks and evidence census},
  year = {2026},
  version = {0.2.0},
  url = {https://huggingface.co/datasets/ksaw008/indus-reference-benchmarks}
}
```

Report errors through [GitHub issues](https://github.com/k-sandhu/indus-reference-benchmarks/issues) with the dataset revision, configuration, row/cell key and source observation. Preserve unresolved candidates and distinguish label corrections from changes to frozen evidence.
