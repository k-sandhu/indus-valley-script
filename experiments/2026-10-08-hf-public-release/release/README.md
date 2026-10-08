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
- config_name: benchmark_rows_v3
  data_files:
  - split: test
    path: data/benchmark_rows_v3.parquet
- config_name: benchmark_readings
  data_files:
  - split: test
    path: data/benchmark_readings.parquet
- config_name: benchmark_readings_v3
  data_files:
  - split: test
    path: data/benchmark_readings_v3.parquet
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
- config_name: benchmark_count_pages_v3
  data_files:
  - split: train
    path: data/benchmark_count_pages_v3.parquet
- config_name: benchmark_count_readings_v3
  data_files:
  - split: train
    path: data/benchmark_count_readings_v3.parquet
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

This dataset contains 687 annotated Helsinki chart cells, three frozen row-reading benchmarks of 60, 80 and 80 rows, an evidence census and small metrology summaries. The chart and benchmark row tables have embedded image columns for the dataset viewer. Its 23 Parquet configurations contain 3,308 rows counting heterogeneous observations, images and readings.

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

`chart_reference.image`, `benchmark_rows_v1.context_image` and v2/v3 `context_image` and `exact_image` decode as Pillow images and can appear in the Hub viewer. Path columns retain logical PNG names for provenance; embedded PNGs are stored once in Parquet. Chart cards and count-page renders remain loose PNGs. Download a snapshot for those images, conventions and the scorer; pin `revision` to a chosen dataset commit for a repeatable analysis:

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
| `chart_reference` | 687 | 687 reviewed chart cells: 8 code and 2 class corrections, 16 settled ambiguities; 33 medium-confidence cells. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_rows_v1` | 60 | 60 numbered-section targets with context crops, initial reference and original template predictions. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_rows_v2` | 80 | 80 targets across three sections with context/exact crops and the second frozen template pipeline. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_rows_v3` | 80 | 80 fresh targets on previously unused target pages with context/exact crops and the third frozen template pipeline. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_readings` | 306 | Initial, repeated, independent and adjudicated readings; frozen endpoints remain distinct. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_readings_v3` | 240 | 240 v3 readings: two independent readers and adjudication for all 80 rows. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_chart_cards` | 33 | Original chart-only cards supplied to benchmark readers. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_count_pages` | 21 | 21 source-count pages: 18 random and 3 stress pages; geometric detections for recall. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_count_readings` | 42 | 42 independent page inventories from the two readers. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_count_pages_v3` | 21 | 21 v3 pages: 18 fresh count pages and 3 stress pages; numbered and physical-line geometry. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `benchmark_count_readings_v3` | 42 | 42 v3 independent numbered/physical-line page inventories. | CC BY 4.0 edition content; CC0 1.0 project additions |
| `evidence_sites` | 115 | 115 site/provenance entities in the reconciled census compilation; aggregate counts in distinct source frames. | CC0 1.0 |
| `evidence_publications` | 17 | 17 bibliographic register entries; historical catalogue coverage is documented separately. | CC0 1.0 |
| `evidence_collections` | 37 | 37 institution observations; null counts are unmeasured, zero counts are bounded queries. | CC0 1.0 |
| `evidence_datasets` | 15 | 15 dataset observations with dated count bases; no underlying corpora bundled. | CC0 1.0 |
| `evidence_catalogue_coverage` | 38 | Catalogue-to-export key coverage by site and publication, with explicit matched/absent denominators. | CC0 1.0 |
| `evidence_catalogue_sections` | 19 | 19 inspected Gujarat/north India CISI 1 sections, separating pottery/graffiti from other catalogue keys. | CC0 1.0 |
| `evidence_field_completeness` | 140 | Measured and assessed field availability by source register and bounded query frame. | CC0 1.0 |
| `evidence_museum_joins` | 49 | 49 independently cited museum-to-CISI identifier correspondences: 42 earlier pairs and seven supplement rows. | CC0 1.0 |
| `evidence_sources` | 111 | Bibliographic pointers and inherited access scopes; this packaging run did not reopen each archaeological source. | CC0 1.0 |
| `weight_mass_bands` | 4 | Four Dholavira mass-band fits with sample sizes, fitted units, signal estimates and intervals. | CC0 1.0 |
| `weight_chance_controls` | 9 | Nine western-screen control rows across three frames and three randomization rules, with observed and simulated hit counts. | CC0 1.0 |
| `image_assets` | 1142 | Licensed PNGs with logical names, storage, portable parent labels and SHA256. | CC BY 4.0 edition content; CC0 1.0 project additions |


`chart_reference` uses reviewed numeric reference version 2.1 and the original 687 atlas crops from PDF pages 20–21. Eight primary codes and two upper classes were corrected; all 16 earlier lower-code ambiguities are provisionally settled. Thirty-six records change numeric fields, including confidence: 33 cells are medium and 654 high on an uncalibrated qualitative scale. Previous-value columns and `change_note` record each change. Crops may include neighbouring ink. [Chart changes](provenance/chart-changes.json) preserves the exact field deltas and consumer impact; [chart review priorities](docs/CHART-REVIEW.md) identify drawings for expert inspection.

The row-reading task gives a system row context, a proposed target box and chart cards. It returns the printed inscription number, its five-position classification and a visual left-to-right sequence of units, each with ranked graphic-code candidate sets. The frozen baseline is a chart-only template matcher. Inventory codes are edition labels.

### Benchmark frames and reference provenance

| Frame | Targets and section quotas | Eligible detections | Exclusions | Readers |
|---|---|---|---|---|
| v1 | 60 numbered targets | 3,460, PDF pages 31–79 | Original development frame is documented in row locators | Three Claude Sonnet readers, 20 targets each; six convenience repeats |
| v2 | 80: 28 numbered, 26 end-sorted, 26 beginning-sorted | 3,596 / 3,228 / 3,496 | Development pages and v1 targets | Two Claude Sonnet readers and a Claude adjudicator; model version not recorded |
| v3 | 80: 28 numbered, 26 end-sorted, 26 beginning-sorted | 572 / 2,004 / 2,004 on 8 / 28 / 28 pages | All v1/v2 target pages and ten original development pages | Two Claude Sonnet 5.5 readers and a Claude adjudicator |

The three results compare pipeline versions on their selected samples. The v2 targets supported v3 development; v3 tests a fresh sample under the page exclusions above. The chart has **Exploratory** status: two AI readings and a pixel check, with the second reader reading 63 cells blind before a whole-chart pixel sweep. AI readers produced the benchmark references from shared conventions and chart cards. Neither the chart nor the benchmark references has expert review. The v3 readers agree on all 80 numbers, classifications, counts and line memberships, and on 357/369 strict unit sets.

Count-page readings use pixel scripts with a **field-block cue**, the printed number/classification margin block used to locate each row, and a printed-line-pitch cross-check. Recall measures agreement with those readings. V2 helpers briefly wrote to shared scratch filenames; the preserved returned readings record how those collisions were handled. Readers also disclosed seeing directory listings with withheld filenames and declared that they did not open withheld prediction payloads; v3 records directory exposure too. [Reader metadata](benchmark/reader-metadata.json) and adjudication notes retain these process disclosures. Wilson intervals and section-stratified row bootstraps do not cluster by source page; v3's 28 numbered rows span only eight pages.

An **exposed OCR locator** means the original v1 locator contained OCR strings before the blinding correction, affecting 22/60 targets. The **eleven-code overlay** records eleven later source-based corrections, is Exploratory, and preserves the frozen v1 endpoint. A **compatible whole row** has nonempty strict reference sets at every unit and zero candidate-set edit distance to the prediction, with intersections at each aligned position. **Aligned unit recall** maximizes matching intersections among minimum-edit alignments and divides by resolved reference units.

| Frozen outcome | v1, 60 rows | v2, 80 rows | v3, 80 fresh rows |
|---|---:|---:|---:|
| Accepted crop | 23/60 | 44/80 | 71/80 |
| Unit count agreement | 33/60 | 59/80 | 72/80 |
| Literal inscription number | 23/60 | 62/80 | 71/80 |
| Five-position classification | 19/60 | 55/80 | 72/80 |
| Strict top-one whole row | 13/60 | 20/80 | 38/80 |
| Strict top-five whole row | 24/60 | 40/80 | 62/80 |
| Aligned strict top-five units | 224/267 | 304/352 | 338/366 |
| Random-page numbered recall | Not evaluated | 1,242/1,286 | 1,289/1,289 |

The five v2/v3 pass criteria are crop correctness ≥90% (72/80), inscription-number accuracy ≥90% (72/80), unit-count agreement ≥95% (76/80), strict top-five whole rows ≥80% (64/80), and random-page numbered recall ≥95%. Both fail four of five criteria; only numbered recall passes. V1 reports the first four thresholds on 60 rows and fails all four. The full provisional transcription remains excluded.

V3 physical-line recall includes continuation lines and is a separate completeness measure: 1,296/1,296 random-page lines, against 1,289 numbered occurrences. Numbered and physical stress-page recall are both 561/561. Its 18 random count pages are fresh against earlier count pages; eight carried earlier recognition targets. Stress pages 62, 129 and 130 are reused. [Expected metrics](benchmark/expected-metrics.json) contains all three frozen row records, intervals, criteria and repair recall outputs.

V3 strict top five is 62/80 (77.5%; Wilson 95% 67.2–85.3%). Restricting the denominator to fully resolved references gives 62/77. The frozen shape-only score is 65/80 (81.3%; 71.3–88.3%). An Exploratory reading-choice sensitivity accepting {23} at 35:2 and 70:4 gives 64/80 and reaches the top-five threshold; count and number still fail. [Sensitivity](benchmark/v3-reading-choice-sensitivity.json) records the modified units separately.

### Chart-label vocabulary

All benchmark cards, references and predictions retain their original card labels, including earlier chart errors. Frozen scores therefore reproduce that historical vocabulary; `chart_reference` uses corrected version 2.1. Separate per-unit flag columns identify changed cells, affected prediction alternatives, possible candidate identities and the v3 58:0 locator conflict. An identifiable cell can have a class/confidence update without a code change. [Chart changes](provenance/chart-changes.json) records 11/0/8 directly changed reference units in v1/v2/v3, and 0/18/31 units needing candidate-identity review. A corrected-label rescoring is deferred until those identities and the locator conflict are reviewed; replacing numbers globally would conflate different drawings.

The [v2 reading convention](benchmark/CONVENTIONS.md) and [v3 convention](benchmark/CONVENTIONS-v3.md) describe independent reading before predictions were opened. Their `position-chart/` means that version's rows in `benchmark_chart_cards`; `page-count-source/` means the page PNGs in `benchmark_count_pages` or `benchmark_count_pages_v3`. The original `predictions.json` is represented by `prediction_json`; `frame.json` was the full detector frame and is excluded. Row locators and the v3 selection retain the benchmark geometry and sampling frame.

The census is an authored compilation of facts, citations, counts and project assessments: 115 site/provenance entities, 17 publications, 37 collections and 15 datasets. Its sixth consolidation reconciled register counts; the source registers were trimmed to remove copied search snippets and source prose. CISI means *Corpus of Indus Seals and Inscriptions*. `local_faces`, `local_families` and `local_cisi_identifiers` count the Lipi export pinned at commit `fc8813a52e183d19c441631dc26c33a4dccbea39`. That export has no licence; only aggregates are published. A **face** is one inscribed surface record. A **provisional family** groups related face records under the export's grouping rule; it is not a verified physical-object count. Catalogue entries have a separate denominator. In 19 inspected CISI 1 Gujarat/north India ranges, 327/493 keys match and 166 are absent under the matching rule: 75 in pottery/graffiti sections and 91 in other sections. A worldwide missing-object denominator was not established.

`evidence_museum_joins` has 49 independently cited accession-to-CISI correspondences: 42 earlier pairs and seven supplement rows. Identifier-source citations distinguish museum identifiers, printed CISI 1 concordances and the Marshall composite table. The supplement awaits the earlier pairs' complete field adjudication. Museum descriptions and photographs are excluded. Collection and field-completeness observations are bounded historical queries; null denotes unmeasured values. [FIELD-DEFINITIONS.md](FIELD-DEFINITIONS.md) documents every field and shared assumption.

The exact Frenez–Tosi 2005 title is *Lothal Sealings: Records from an Indus Civilization town at the eastern end of the maritime trade networks across the Arabian Sea*. The longer wording beginning “The Lothal Sealings” came from the earlier publication register; public tables use the [Zenodo record](https://zenodo.org/records/5514283).

The weight tables contain Exploratory fits and simulations. A **fitted unit** is a hypothesized common base mass under specified multiplier and noise rules. Dholavira's 5–100 g band has 90 weights and a 13.716 g unit; the 1.3–5 g band has 147 weights and a 14.280 g unit. The legacy western screen observes 136 geometric and 18 close hits. Mean geometric/close counts in its three nulls are 170.246/38.727 (±0.15 log jitter), 208.5675/50.3805 (±0.35 log jitter) and 193.9825/44.2695 (site log-uniform), with 2,000 draws each. All exceed the observations. [Methods](docs/METHODS.md#weight-metrology) describe the fit and controls. Excluded catalogue measurements and the full fitting pipeline are needed to repeat the original fit.

## Score a new row reader

Install scorer dependencies with `python -m pip install -r requirements.txt` from the snapshot. Supply one prediction for every sample as a JSON list, an object containing `rows`, or JSON Lines. Required row fields are `sample_index`, `occurrence_key`, `pdf_page`, `printed_inscription_id`, `classification_literal` and `units`. v2 and v3 require `section`: `number_order`, `end_sorted` or `beginning_sorted`. Copy frozen identifiers/section when preparing predictions. Preserve five classification positions, including blank spaces. Number and classification may be null. `printed_inscription_id` is a string preserving the printed number and suffix; `classification_literal` is a five-position string, including spaces. Frozen-format aliases `inscription_number` and `classification_code` are accepted. If both names are supplied, their values must agree.

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

The scorer rejects missing number/classification keys, conflicting aliases, missing unit confidence and missing/invalid v2/v3 section. Omit `--predictions` to reproduce the frozen baseline. Outputs include candidate widths, count/number/classification accuracy, alignments, calibration and 2,000-draw intervals. It refuses to overwrite an output. v2/v3 source-row recall uses preserved detector geometry; new row predictions do not evaluate a new detector. [Expected metrics](benchmark/expected-metrics.json) preserve the baseline targets.

## Provenance, rights and limitations

Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki, ISBN 951-45-1627-3. The [official final-version record](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/) supplies [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the persistent handle is [10138/342677](http://hdl.handle.net/10138/342677). Edition-derived crops, chart cells/cards, page renders, inscription numbers, classifications and sign numbering retain that licence. The project waives its rights in additions to mixed configurations under CC0 1.0. Own compilations, readings, annotations, aggregates and documentation use CC0 1.0; code uses the Unlicense. The component table, [LICENSE](LICENSE), official texts in `LICENSES/` and [NOTICE](NOTICE) specify the structure and changes.

AI assistance produced chart labels, independent benchmark readings/adjudication, the template pipeline, research code and documentation. `Frozen evaluation` identifies preserved evidence; `Exploratory` identifies annotations, later corrections and census/metrology interpretations. Reproduced arithmetic has `Verified computation` status; the baseline's criterion outcome is `Failed`. This dataset makes no decipherment claim.

The packaging sequence screen read `lipi_observed_faces.jsonl` and `mayig_faces.jsonl` for sequences of at least two units in both recorded directions: 3,506 distinct forward sequences and 6,878 distinct sequences counting both directions. It preserved Mayig's `P` namespace. The original v1/v2 screen tested 105 complete singleton reference rows, each with at least two units and exactly one strict candidate per unit. Version 0.3.0 adds 44 v3 rows, giving 149 tested rows; none equalled a whole indexed sequence in either direction. A broader reviewer scan normalized namespaces and tested runs of at least three positions across six derivatives, finding zero graphic-code runs and detecting all 200 planted controls. Its 12 generic integer-list hits are zero-based agreed-unit indices, repeated in the v3 reference and adjudication reading. These screens cover their input files and numbering; reuse after recoding is outside their reach. Text comparisons found no unexplained copied third-party prose; exact bibliography and official licence text are recorded separately.

[sources.json](sources.json) and `evidence_sources` give exact citations and access scopes, including inherited and snippet-only access. Portable `source-` labels identify original witnesses whose parent payloads are excluded. [EXCLUSIONS.md](EXCLUSIONS.md) lists omissions. The image manifest gives logical names, storage and PNG hashes; the file manifest lists every release file except itself.

## Citation and error reports

k-sandhu (2026). *Indus chart, row-reading benchmarks and evidence census*, version 0.3.1. [Dataset](https://huggingface.co/datasets/ksaw008/indus-reference-benchmarks). Cite Koskenniemi and Parpola (1979) when using edition-derived content.

```bibtex
@dataset{indus2026reference,
  author = {k-sandhu},
  title = {Indus chart, row-reading benchmarks and evidence census},
  year = {2026},
  version = {0.3.1},
  url = {https://huggingface.co/datasets/ksaw008/indus-reference-benchmarks}
}
```

Report errors through [GitHub issues](https://github.com/k-sandhu/indus-reference-benchmarks/issues) with the dataset revision, configuration, row/cell key and source observation. Preserve unresolved candidates and distinguish label corrections from changes to frozen evidence.
