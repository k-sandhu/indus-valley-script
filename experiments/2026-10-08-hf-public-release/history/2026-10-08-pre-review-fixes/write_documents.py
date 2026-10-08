"""Write documentation for a new local build. No Hub calls."""
import argparse
import json
from pathlib import Path
import shutil
import yaml
from build_release import HERE, ROOT, M, B, RAW, read, sha, dump

ATTRIBUTION = "Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki."
SOURCE = 'https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/'
CC = 'https://creativecommons.org/licenses/by/4.0/'

DEFINITIONS = {
 'cell_id':'Stable chart coordinate key, using one-based PDF page and zero-based chart column/row.',
 'pdf_page':'One-based page of the acquired PDF, including the repository cover. It differs from book pagination.',
 'column':'Zero-based chart column; a printed layout coordinate.',
 'row':'Zero-based chart row; a printed layout coordinate.',
 'rank':'Preferred upper printed rank label; repeated ranks do not identify unique drawings.',
 'code':'Preferred lower printed graphic code. It is an inventory label, with no assigned sound or meaning.',
 'alternatives':'Other retained readings of the lower numeric label. Empty means no additional label candidate was retained.',
 'rank_alternatives':'Other retained upper-label readings.',
 'numeric_confidence':'Qualitative AI label-reading judgment inherited from the reference; it is not a calibrated probability.',
 'dashed_auxiliary':'Whether the chart cell was annotated as a dashed auxiliary drawing; null preserves an unrecorded judgment.',
 'source_crop_pdf_points':'Chart crop [left, top, right, bottom] in PDF points.',
 'image_path':'PNG path relative to the dataset root. Use snapshot_download to obtain image files.',
 'image_paths':'List of licensed count-page PNGs relative to the dataset root.',
 'annotation_method':'Authored description of how numeric chart labels were read.',
 'source_url':'Official source or licence attribution URL.',
 'source_pdf_sha256':'SHA256 of the unchanged acquired 1979 PDF, which is not bundled.',
 'status':'Research status, preserving the difference between Exploratory findings and Frozen evaluation records.',
 'sample_index':'Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate.',
 'occurrence_key':'Pipeline locator for a printed occurrence; it does not establish a physical-object identity.',
 'section':'number_order, end_sorted or beginning_sorted section of the edition.',
 'context_image_path':'Relative PNG showing the selected row with wider printed context.',
 'exact_image_path':'Relative PNG of the frozen proposed glyph box in v2. Null for v1, whose box is recorded in locator_json.',
 'locator_json':'JSON object with sample coordinates, crop hashes and selection fields. See the nested-field notes below.',
 'reference_json':'Lossless JSON of the original scoring reference. See the nested-field notes below.',
 'prediction_json':'Lossless JSON of the frozen chart-only row prediction. It includes ranked templates and graphic-code candidate sets.',
 'reference_kind':'Initial disjoint AI reading in v1 or adjudication following two AI readings in v2.',
 'original_ocr_locator_exposed':'Whether v1 locator metadata contained OCR strings before the blinding correction; false in v2.',
 'benchmark':'v1 or v2 benchmark identifier.',
 'reader':'A/B/C research-role label. These references were produced by AI readers; no human expert certification is recorded.',
 'kind':'primary, convenience_repeat, independent or adjudicated reading. Repeats were fixed convenience selections.',
 'reading_json':'Lossless returned row or count-page reading JSON, including candidate ambiguity and source observations.',
 'source_file':'Repository-relative parent file. Parent content is not necessarily distributed with the public candidate.',
 'card_id':'Original chart-card sheet stem; sheet sequence is not a train/test split.',
 'frame':'For benchmark_count_pages, random or stress page frame. For weight_chance_controls, the legacy/canonical metrological multiplier rule named in the method report. Evaluate each frame separately.',
 'detections_json':'JSON list containing only row_anchor_y_2x and margin_xyxy_2x, the geometry used for row-recall matching.',
 'site':'Site or provenance entity label reconciled by synthesis v6. An entity can denote a provenance group.',
 'assigned_region':'Census work-batch region, not a claim of an ancient administrative division.',
 'local_faces':'Aggregate face-record count in the pinned local export.',
 'local_families':'Aggregate provisional object-family count in the pinned local export.',
 'local_cisi_identifiers':'Count of distinct local CISI identifiers for this site/provenance entity.',
 'IM77_main_selected_objects':'Count in Mahadevan 1977 printed p.6, under that edition’s selection rules. Null is unmeasured or unlisted.',
 'IM77_count_status':'Whether the IM77 value comes from the printed table or the entity is not listed there.',
 'ICIT_object_count':'Site-level ICIT count if established; retained null when unmeasured.',
 'worldwide_missing_objects':'Retained null: the census did not establish a worldwide object denominator.',
 'source_locator':'Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs.',
 'publication_id':'Stable identifier in the authored publication register.',
 'title':'Exact bibliographic source title as recorded; title trimming is retained in source metadata.',
 'authors_editors':'Named publication authors or editors in the source register.',
 'year':'Publication year; string or null in the heterogeneous source bibliography.',
 'venue':'Publisher, journal, series or institutional venue as recorded.',
 'url':'Source access URL, not a grant of rights to its payload.',
 'access_record':'Inherited record of opening/search scope. The packaging run did not reopen every archaeological source.',
 'institution':'Museum or collection institution label.',
 'region':'Register’s modern regional grouping.',
 'confirmed_record_minimum':'Minimum original inscription-confirmed records in a bounded query. Null is unmeasured; zero is a query outcome.',
 'count_basis':'Authored definition of the reported count and its source/time frame.',
 'record_fields_json':'JSON of field-availability assessments for an institution; these are assessments, not copied object records.',
 'source_ids':'IDs in the collections source register, prefixed collections: in evidence_sources.',
 'query_date':'Recorded date of the bounded collection query.',
 'name':'Dataset-register name.',
 'size_json':'JSON of historical aggregate size measures and units; missing size remains null inside JSON.',
 'reported_reuse_terms':'Recorded licence or unresolved-rights assessment of the external dataset; that dataset is not included here.',
 'version_basis':'Recorded version/time scope of the external dataset observation.',
 'batch':'Contributing site-census batch.',
 'edition':'CISI1/CISI2 source edition identifier, including the inherited CISI1-1987 spelling.',
 'prefix':'Printed catalogue identifier prefix.',
 'first':'First number of the inspected catalogue run.',
 'last':'Last number of the inspected catalogue run.',
 'pages':'Printed catalogue page/range locator.',
 'input_pointer':'Parent register pointer used by synthesis v6.',
 'matching_prefix':'Local comparison prefix, including documented aliases.',
 'prefix_basis':'Authored evidence for prefix correspondence.',
 'printed_number_slots':'Number slots before named duplicate-caption exclusions.',
 'exclusions':'JSON text listing source-number exclusions, including the H356 caption correction where relevant.',
 'catalogue_entries':'Catalogue base keys in the defined run after exclusions.',
 'local_matching_entries':'Exact or recorded-alias catalogue keys found in the pinned local export.',
 'local_absent_entry_keys':'Keys absent under the matching rules; their objects may exist under other identifiers.',
 'fraction':'local_matching_entries divided by catalogue_entries.',
 'scope':'Authored definition of the count frame and its limitations.',
 'range':'Inspected printed CISI 1 identifier range; retained as source-table text.',
 'entries':'Catalogue entries in the inspected range; retained as source-table numeric text.',
 'matching_keys':'Catalogue keys matched to the local export; retained as source-table numeric text.',
 'absent_keys':'Catalogue keys absent under the comparison rule; retained as source-table numeric text.',
 'absent_graffiti_or_pottery_sections':'Absent keys in the pottery/graffiti section frame; retained as source-table numeric text.',
 'absent_seal_impression_tablet_other_sections':'Absent keys in the other carrier sections; retained as source-table numeric text.',
 'printed_pages':'Printed-page locators supporting the section split.',
 'classification_basis':'Authored rule assigning catalogue keys to section frames; a section does not establish an object’s linguistic status.',
 'index':'Dataset, museum or schema frame being assessed.',
 'unit':'Unit counted, such as face records or museum records.',
 'denominator':'Count in the stated measurement frame; null where no measured denominator exists.',
 'field':'Metadata field being assessed.',
 'present':'Count with field presence under basis; null for unmeasured/schema assessments.',
 'missing':'Count without field presence under basis; null for unmeasured/schema assessments.',
 'percent':'100 times present/denominator where measured; structural absence does not receive a measured percentage.',
 'measurement':'Measured export presence, inherited rule, structural schema absence or other stated measurement class.',
 'basis':'Exact authored operational presence rule or source-frame qualification.',
 'evidence':'Parent file/field citation for the aggregate observation.',
 'museum_record_id':'Published museum catalogue identifier.',
 'museum_accession':'Published accession string; formatting is preserved.',
 'museum_url':'Published museum object page, if recorded or recoverable from its identifier.',
 'cisi':'Published CISI key linked to the museum accession. Local corpus rows and sign sequences are omitted.',
 'join_method':'Authored identifier/concordance method supporting the join.',
 'shared_identifier':'Public excavation/plate identifier used to support the join; null when only the supplement evidence is retained.',
 'join_evidence':'Authored source/page/identifier observation supporting the join.',
 'source_id':'Namespaced bibliography ID: synthesis: or collections:.',
 'authors':'JSON string containing the recorded author list/string.',
 'opened_by_packager':'False for archaeological sources inherited from census registers; consult access_record for the contributing package’s scope.',
 'component':'Configuration or image component served by this PNG.',
 'role':'chart_cell, row_context, exact_proposal_crop, chart_card or page_count_context.',
 'source_path':'Repository-relative PNG parent path.',
 'sha256':'SHA256 of the staged PNG bytes.',
 'bytes':'PNG byte count.',
 'license':'Source image licence, CC BY 4.0.',
 'group':'Dholavira mass band in grams: below-1.3, 1.3-to-5, 5-to-100 or above-100.',
 'n':'Number of weights in the stated band.',
 'unit_g':'Fitted metrological unit in grams under the cited model and multiplier rules.',
 'signal_cv_percent':'Fitted relative signal variation expressed as a percentage.',
 'signal_probability':'Fitted signal-mixture probability; not a probability of an archaeological interpretation.',
 'within_3_percent_n':'Weights within the method’s 3% proximity rule.',
 'unit_ci95_low_g':'Lower endpoint of the fitted-unit bootstrap interval, grams.',
 'unit_ci95_high_g':'Upper endpoint of the fitted-unit bootstrap interval, grams.',
 'method_path':'Repository-relative method/report citation. Its code repository is presently private.',
 'null':'Mass-randomization rule used to generate the comparison, named in the metrology method.',
 'draws':'Number of simulated comparison draws.',
 'observed_geometric_n':'Observed matches under the method’s geometric rule.',
 'observed_close_n':'Observed matches under the method’s close rule.',
 'geometric_mean':'Mean geometric-rule matches in the simulated comparison.',
 'close_mean':'Mean close-rule matches in the simulated comparison.',
 'geometric_simulation_interval95':'JSON text giving the central 95% simulation interval for geometric matches.',
 'close_simulation_interval95':'JSON text giving the central 95% simulation interval for close matches.',
 'fraction_ge_observed_geometric':'Fraction of simulated draws with at least the observed geometric match count.',
 'fraction_ge_observed_close':'Fraction of simulated draws with at least the observed close match count.',
}

def main():
    p=argparse.ArgumentParser();p.add_argument('--release',type=Path,default=HERE/'release');args=p.parse_args()
    release=args.release.resolve()
    if not release.is_relative_to(HERE):raise ValueError('Use a Package O build.')
    tables=read(release/'provenance/table-manifest.json');meta=read(release/'provenance/metadata.json')
    overview='| Configuration | Rows | Contents |\n|---|---:|---|\n'+''.join(f"| `{name}` | {s['rows']} | {s['description']} |\n" for name,s in tables.items())
    card=f'''# Indus chart, row-reading benchmarks and evidence census

This locally staged candidate contains the 687-cell Helsinki sign chart, two frozen row-reading benchmarks of 60 and 80 rows, and selected evidence-census and metrology tables. It is awaiting the owner’s licensing and authorship decisions in [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md). The underlying 1979 source has an explicit CC BY 4.0 licence; CC BY 4.0 for our annotations and compilations and MIT for our code are proposals. The YAML licence list describes the intended component licences after confirmation.

The Indus script is a set of signs found on seals, sealings, tablets, pottery and other objects associated with the Indus civilization in South Asia. Most inscriptions are short. Its language, sound values and readings remain unresolved. This dataset records printed drawings, graphic inventory labels, annotation judgments and measurements that can be inspected without assigning meanings to the signs. The 1979 edition is an interim corpus and omits later discoveries; its printed occurrences and sorted repetitions are different units from independently excavated objects.

## Configurations and construction

{overview}

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
tables = {{name: load_dataset(repo, name)
          for name in get_dataset_config_names(repo)}}
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

{ATTRIBUTION} [Official final-version record]({SOURCE}), [persistent handle](http://hdl.handle.net/10138/342677), [CC BY 4.0]({CC}). The chart, row crops, chart cards, count-page images and source-derived readings carry this attribution. Changes consist of raster cropping, arranging chart cards, reading numeric labels, annotating candidate sets and computing recognition scores. No endorsement by the source authors is implied. The original PDF is not included.

Our compilations, protocols, annotation contributions and aggregate results are proposed under CC BY 4.0; our scorer is proposed under MIT. Those grants await the owner’s confirmation. External catalogues are cited for facts and identifiers; their source text, scans and images are not covered by these proposed terms. [LICENSE](LICENSE), [NOTICE](NOTICE) and [LICENSE-MIT](LICENSE-MIT) state component scopes and pending decisions.

## Status, AI assistance, citation and corrections

Chart labels and source readings were produced with AI assistance. AI agents prepared crops, recognition proposals, independent readings, adjudication, census assessments, code and this packaging documentation. Numerical reproduction can verify those outputs; it does not replace expert epigraphic review. Census and metrology findings remain Exploratory. The benchmark predictions and reference sets are Frozen evaluation records from two failed pipeline tests. This release contains no authenticated sounds, meanings or decipherment.

Author: **TODO: owner-confirmed author name**. Affiliation: **TODO: affiliation or none**. Contact: **TODO: error-report address**. Candidate date: 8 October 2026. Cite the dataset version and repository revision using [CITATION.cff](CITATION.cff), and cite Koskenniemi and Parpola’s 1979 edition when using its derivatives. No DOI or public repository ID has been assigned. Error reports should give configuration, cell ID or benchmark/index, source page/box, observed problem and a source-based correction. Use the future dataset’s discussion page or the owner’s confirmed contact; the owner has not yet supplied either public destination.
'''
    header='---\n'+yaml.safe_dump(meta,sort_keys=False,allow_unicode=True)+'---\n\n'
    (release/'README.md').write_text(header+card,encoding='utf8')
    fields='# Field definitions\n\nPNG paths are relative to the dataset root. Null means unmeasured or unrecorded unless a field definition supplies a narrower meaning. JSON columns are UTF-8 JSON strings; decode them with `json.loads`. Numeric inventory codes follow the 1979 chart and must not be conflated with Wells, ICIT or Mahadevan code namespaces.\n\n'
    missing=[]
    for name,spec in tables.items():
        fields+=f'## {name}\n\n| Field | Arrow type | Definition |\n|---|---|---|\n'
        for field in spec['schema']:
            key=field['name'];definition=DEFINITIONS.get(key)
            if definition is None:
                missing.append((name,key));definition='Exact authored field from the pinned parent table; consult source_locator and the source-table scope.'
            fields+=f"| `{key}` | `{field['type']}` | {definition} |\n"
        fields+='\n'
    fields+='''## Nested benchmark fields

`reference_json` and row `reading_json` retain `sample_index`, `printed_inscription_id`, `classification_literal`, `crop_correct`, `drawn_unit_count` and the ordered `units`. A unit’s `strict_candidate_codes` combines drawing, underline and vertical-position observations; `shape_only_candidate_codes` is a broader diagnostic set. An empty strict set means unresolved. `unit_kind` records a glyph or modern editorial drawing such as damage/hatching; loss drawings do not imply a known original number of signs. Unit indices and source extents remain as returned by each reader. `valid_printed_target=false` is a false detection in v2. Optional crop explanations, underlines, blank gaps and source-window observations preserve the reader’s own record. The JSON objects can differ in optional fields across readers; the tabular outer schema is fixed.

`prediction_json.units[*].alternatives` is ranked in template order and retains `template_key`, `codes`, `ranks`, distances/costs and synthetic template scores. `confidence` is the development logistic confidence when present. A synthetic softmax score is not a probability over authenticated readings. The original template order and confidences are needed to reproduce candidate widths, alignment and calibration. Each prediction’s number and classification can be null or wrong. `serialization` describes visual ordering, not a linguistic reading direction or physical-object surface concordance.

`locator_json` gives PDF coordinates, target/context boxes, crop paths/hashes and the frozen sample’s section. Zero-based pipeline `pdf_column`/`row_index` values are detector coordinates; reader source-column indices may use their original conventions. Field names ending `_2x` are pixels at two pixels per PDF point. Boxes ending `_pdf_box` or `_pdf_points` use PDF points. `source_crop` is the wider context filename; v2 `exact_crop` is the proposed glyph-box filename. Use the outer relative image paths to open the staged copies.

Count-page `reference_json` and count `reading_json` contain `columns`, `x_extent_pdf`, `row_count`, `row_centers_pdf`, and continuation-line coordinates where recorded. A numbered printed occurrence counts once, while an unnumbered continuation adds a physical line without adding an occurrence. `detections_json` contains detector centers/field boxes only. The recall scorer greedily matches the nearest eligible source/detection centers within nine PDF points and counts unmatched detections as false positives.

`benchmark/reader-metadata.json` preserves original notes, timing and blinding disclosures; returned rows are in the reading tables. `benchmark/v1-exploratory-adjudication-overlay.json` is a post-outcome correction record and is not applied to the frozen v1 score. `benchmark/v2-adjudication-notes.json` preserves the source-only adjudicator’s decisions. PNGs and their source hashes are listed in `image_assets`.
'''
    (release/'FIELD-DEFINITIONS.md').write_text(fields,encoding='utf8')
    dump(release/'provenance/field-documentation-check.json',dict(missing_specific_definitions=missing))
    licence=f'''Component licence record for a staged candidate, 8 October 2026

Helsinki 1979 source-derived chart images, row crops, chart cards, count-page images and source readings: Creative Commons Attribution 4.0 International (CC BY 4.0).
Legal terms: https://creativecommons.org/licenses/by/4.0/legalcode.en
Attribution and transformations: NOTICE.

Project-authored annotations, data compilations, numerical results and documentation: proposed CC BY 4.0, awaiting the owner's confirmation. No grant for these contributions is activated by this staging record.

Project-authored code in code/: proposed MIT, awaiting the owner's confirmation and copyright name. Proposed text: LICENSE-MIT.

TODO: confirmed copyright holder, author, affiliation and contact.
These terms do not cover excluded source PDFs, museum photographs/descriptions, Lipi/Mayig records or Ascalone catalogue records. See RELEASE-CHECKLIST.md and provenance/rights-audit.json.
'''
    (release/'LICENSE').write_text(licence,encoding='utf8')
    (release/'NOTICE').write_text(f'''Source attribution

Kimmo Koskenniemi and Asko Parpola. Corpus of Texts in the Indus Script. 1979. Research Reports 1. Department of Asian and African Studies, University of Helsinki. ISBN 951-45-1627-3.
Official final-version record: {SOURCE}
Persistent handle: http://hdl.handle.net/10138/342677
Source licence: CC BY 4.0, {CC}
Source PDF SHA256: 7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27

Changes: raster cropping of the printed chart and benchmark rows/count pages, chart-card arrangement, AI-assisted numeric label reading, candidate-set source annotation, chart-only recognition and scoring. Unresolved labels and editorial markers are retained. The source authors have not certified these changes or endorsed this dataset.

Project attribution: TODO: owner-confirmed author name, affiliation and contact. Project-created data/documentation CC BY 4.0 and code MIT are proposals pending confirmation. Archaeological bibliographic sources are named in sources.json and evidence_sources; their payloads have not been assigned a project licence.
''',encoding='utf8')
    (release/'LICENSE-MIT').write_text('''PROPOSED MIT License: awaiting owner confirmation

Copyright (c) 2026 TODO: confirmed copyright holder

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''',encoding='utf8')
    (release/'CITATION.cff').write_text('''cff-version: 1.2.0
message: "Candidate citation. Fill authors and repository URL before release; cite Koskenniemi and Parpola 1979 for source derivatives."
type: dataset
title: "Indus chart, row-reading benchmarks and evidence census"
version: "0.1.0-candidate-2026-10-08"
date-released: "2026-10-08"
authors:
  - name: "TODO: owner-confirmed author name"
    affiliation: "TODO: affiliation or none"
license:
  - CC-BY-4.0
  - MIT
references:
  - type: book
    title: "Corpus of Texts in the Indus Script"
    authors:
      - family-names: Koskenniemi
        given-names: Kimmo
      - family-names: Parpola
        given-names: Asko
    year: 1979
    publisher:
      name: "Department of Asian and African Studies, University of Helsinki"
    url: "https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/"
''',encoding='utf8')
    checklist='''# Release decisions and manual steps

This is a local candidate. No repository was created, no file was uploaded and no visibility changed. The owner must complete these decisions before public release.

- [ ] Confirm CC BY 4.0 for the project’s annotations, compilations, documentation and aggregates.
- [ ] Confirm MIT for the project’s code and fill the copyright holder in LICENSE-MIT.
- [ ] Fill author name, affiliation (or none), contact and the final repository ID in README, NOTICE and CITATION.cff. The candidate citation date/version must be updated to the actual release.
- [ ] Decide whether to include the scorer here, as currently staged, and whether to publish a reviewed subset of the GitHub code repository. The current GitHub source links require private access. Public dataset release does not require changing the existing GitHub repository’s visibility.
- [ ] Decide whether to include the weight aggregates while their full method/code remains behind private links, or supply a separately reviewed public methods supplement. Those aggregates alone cannot replay the original fit.
- [ ] Review the file-by-file rights audit, table fields, all prose-overlap dispositions and source samples. Confirm the 1979 CC BY attribution and retained numeric ambiguities.
- [ ] Repeat local validation and benchmark scoring. Inspect hosted configurations and image retrieval after private upload.
- [ ] Approve the exact final candidate revision and make the final visibility decision.

## Upload for private review, after coordinator authorization

Choose a **new** dataset ID such as `NAMESPACE/indus-reference-benchmarks`; replace the example with the owner’s choice. Keep `ksaw008/indus-research-data` private. The following is a future manual recipe, not an action performed by Package O. It follows the official [upload guide](https://huggingface.co/docs/huggingface_hub/guides/upload).

```python
from huggingface_hub import HfApi
api = HfApi()  # Use the owner’s authenticated session; do not put a token in this folder.
repo_id = "NAMESPACE/indus-reference-benchmarks"
api.create_repo(repo_id, repo_type="dataset", private=True, exist_ok=False)
assert api.repo_info(repo_id, repo_type="dataset").private
api.upload_folder(
    repo_id=repo_id, repo_type="dataset",
    folder_path="experiments/2026-10-08-hf-public-release/release",
    commit_message="Stage attributed reference tables for private review",
)
```

Upload only the contents of `release/`, not this package’s local raw folder, private-store folder or the repository root. Download the new private snapshot at its returned commit revision, check it against `provenance/file-manifest.json`, and rerun local table loading/scoring. Verify all 19 configuration choices in the hosted viewer. Relative PNG paths are strings; obtain their files with `snapshot_download` and open them with Pillow.

When the owner approves public release, finish the placeholders and pending licence statements, update manifests and validation, upload that final revision to the new repository while it is still private, then inspect it. The owner can change **the new dataset** to public in its Settings tab’s visibility control, as described in [Repository Settings](https://huggingface.co/docs/hub/repositories-settings). Record the released revision. No visibility change for the private backup or GitHub repository follows from that decision.

## Exclusions

| Excluded material | Basis |
|---|---|
| Package A per-query predictions, model weights/counts and training register | Lipi-derived record-level content; no source licence found. Existing private backup stays private. |
| Lipi records/sign sequences and Mayig derivatives | Lipi redistribution basis unresolved; Mayig’s MIT notice does not resolve separate CISI photograph rights. Neither payload is included. |
| Full provisional 1979 transcription, ledger import and repair frames | Recognition criteria failed and the full transcription remains quarantined; carrier/surface concordances remain unresolved. |
| Package N’s future verified rows | Only a proposed protocol was available at the initial source inspection; completed results require a later audited addition. |
| Third-party PDFs and non-CC-BY page images | Only attributed 1979 source-derived PNGs pass the image allowlist. |
| Museum descriptions, photographs, raw API responses and corpus record contents | Unresolved payload rights; accession/CISI identifiers, count aggregates and our join assessments suffice for these tables. |
| Ascalone 2022 catalogue records | Aggregate metrology summaries only; the catalogue rows are not distributed. |
| Lecture transcript and record-level Frenez-test inputs | Not selected; current aggregates here are the small metrology tables. |

The source images and label candidates are available for inspection, but expert review is still pending. The two frozen benchmarks reproduce failed pipeline outcomes; their inclusion does not release the quarantined corpus.
'''
    (release/'RELEASE-CHECKLIST.md').write_text(checklist,encoding='utf8')
    sources=read(HERE/'sources.json') if (HERE/'sources.json').exists() else dict(sources=[])
    dump(release/'sources.json',sources)
    for src,dest in [(release/'provenance/rights-audit.json',HERE/'rights-audit.json')]:
        if release==HERE/'release':shutil.copyfile(src,dest)
    write_private()
    print(json.dumps(dict(field_definition_gaps=missing)))

def write_private():
    private=HERE/'private-store';private.mkdir(exist_ok=True)
    path=ROOT/'experiments/2026-10-06-research-program/hf-hosting-manifest.json'
    manifest=read(path);dump(private/'checksums-manifest.json',manifest)
    groups={}
    for record in manifest['files']+manifest['backed_up_files_kept_locally']:
        group=groups.setdefault(record['set'],dict(files=0,bytes=0));group['files']+=1;group['bytes']+=record['bytes']
    overview='| Set | Repository-relative path | Files | Bytes |\n|---|---|---:|---:|\n'
    for name,g in groups.items():
        p=manifest['sets'][name]['path']+'/' if name in manifest['sets'] else next(r['path'] for r in manifest['backed_up_files_kept_locally'] if r['set']==name)
        overview+=f"| {name} | `{p}` | {g['files']} | {g['bytes']} |\n"
    text=f'''---
pretty_name: Indus research private backup
tags:
- indus-script
- private-backup
- research-outputs
---

# Indus research private backup

`ksaw008/indus-research-data` is a private backup for large outputs from the private `k-sandhu/indus-valley-script` research repository. It stores 1,038 manifest-listed files totaling {sum(g['bytes'] for g in groups.values()):,} bytes. The inventory below comes from the locally preserved hosting manifest, SHA256 `{sha(path)}`. Its `verified` flags describe the earlier upload verification; Package O did not query the remote backup again.

{overview}

The 1,029 restoration-prediction files include per-fold/query JSONL, probability arrays, fitted counts and neural checkpoints. The five frozen-model files hold counts, three seed weights and a training register. These depend on the pinned Lipi export, whose licence was not found, and must remain private. The four Helsinki files are large backup copies of provisional occurrences, a provisional ledger import and the v1/v2 repair frames. Their 1979 source is CC BY 4.0, but the transcription failed its evaluations and remains quarantined. No third-party PDF scans are listed in this backup manifest.

The GitHub repository preserves code, protocols, aggregate results and research documentation. This backup preserves large generated payloads omitted from Git. Its path layout mirrors the local repository; it is not a set of `load_dataset` configurations. The separate public-release candidate selects licensed source derivatives and authored tables. Making that new dataset public would not change this backup’s rights or status.

## Restore and verify

Use an authenticated owner session with `huggingface_hub`. Do not embed tokens in research files. Run from the repository root:

```powershell
python -B experiments/2026-10-06-research-program/hf_host.py restore --repo ksaw008/indus-research-data
```

The existing `restore` implementation downloads **only** `data/raw/2026-10-06-modern-restoration/main/**` and `data/raw/2026-10-06-modern-restoration/frozen-model/**`. It does not restore the four Helsinki backups. It writes into the original repository paths and uses the current remote revision. Use a separate restore folder and a chosen revision with `snapshot_download` when checking a backup before replacing local files:

```python
from huggingface_hub import snapshot_download
snapshot_download(
    "ksaw008/indus-research-data", repo_type="dataset",
    revision="COMMIT_SHA_FROM_OWNER", local_dir="RESTORE_DIRECTORY",
    allow_patterns=[
        "data/raw/2026-10-06-modern-restoration/main/**",
        "data/raw/2026-10-06-modern-restoration/frozen-model/**",
        "experiments/2026-10-07-helsinki1979-digitization/runs/2026-10-07-full-v1/occurrences.jsonl",
        "experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl",
        "experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v1/frame.json",
        "experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-07-v2/frame.json",
    ],
)
```

To restore one part, retain only its path/pattern in `allow_patterns`. Restore paths must preserve their repository-relative layout. The local manifest does not record a remote commit SHA; obtain it from the backup repository before a pinned restore. The above example deliberately requires the owner to supply it.

[checksums-manifest.json](checksums-manifest.json) lists every file’s path, byte count and SHA256, including `backed_up_files_kept_locally`. After downloading, verify all 1,038 files against it with the read-only checker:

```powershell
python -B experiments/2026-10-08-hf-public-release/verify_private_store.py --root RESTORE_DIRECTORY --out experiments/2026-10-08-hf-public-release/private-restore-check.json
```

Missing or mismatched files fail that check. The original `hf_host.py verify --repo ksaw008/indus-research-data` checks the two restoration directories against the Hub; it does not check the four Helsinki backup files. Its `upload` command also regenerates a short README, so a coordinator installing this fuller card should do so after any such upload. No restore, verification against the Hub, upload or file deletion was performed during this documentation task.

Author/contact: TODO: owner-confirmed details. Keep this card and checksum manifest attached to the private backup. Source provenance and public-release exclusions are documented in the GitHub repository’s `knowledge/provenance/REDISTRIBUTION.md` and Package O’s rights audit.
'''
    (private/'README.md').write_text(text,encoding='utf8')
    dump(private/'inventory-summary.json',dict(source_manifest=path.relative_to(ROOT).as_posix(),source_sha256=sha(path),sets=groups,total_files=sum(g['files'] for g in groups.values()),total_bytes=sum(g['bytes'] for g in groups.values()),remote_rechecked=False))

if __name__=='__main__':main()
