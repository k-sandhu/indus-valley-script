"""Generate public documentation and separate owner records; no Hub mutations."""
from pathlib import Path
import shutil
import yaml
from build_release import HERE, ROOT, RAW, read, sha, dump, SOURCE, CC
from release_policy import DATASET_ID, ISSUES_URL, AUTHOR, LIPI_COMMIT
from field_definitions import DEFINITIONS

TITLE='Indus chart, row-reading benchmarks and evidence census'
LOTHAL='Lothal Sealings: Records from an Indus Civilization town at the eastern end of the maritime trade networks across the Arabian Sea'

def generate(release,builder):
    tables=read(release/'provenance/table-manifest.json');meta=read(release/'provenance/metadata.json')
    overview='| Configuration | Rows | Contents | Licence |\n|---|---:|---|---|\n'+''.join(f"| `{n}` | {s['rows']} | {s['description']} | {s['license']} |\n" for n,s in tables.items())
    total_rows=sum(s['rows'] for s in tables.values())
    card=f'''# {TITLE}

This dataset contains 687 annotated Helsinki chart cells, three frozen row-reading benchmarks of 60, 80 and 80 rows, an evidence census and small metrology summaries. The chart and benchmark row tables have embedded image columns for the dataset viewer. Its {len(tables)} Parquet configurations contain {total_rows:,} rows counting heterogeneous observations, images and readings.

The Indus script is a set of signs found on seals, sealings, tablets, pottery and other objects associated with the Indus civilization in South Asia. Most inscriptions are short; their language and sound values remain unresolved. This dataset supports reading printed drawings and comparing graphic inventory labels without assigning meanings to the signs. The 1979 edition is an interim corpus that omits later discoveries. Its numbered and sorted printed occurrences can repeat a text or object.

## Load tables and images

Install `datasets`, `huggingface_hub` and Pillow. Choose one named configuration for each table:

```python
from datasets import load_dataset, get_dataset_config_names
repo = "{DATASET_ID}"
chart = load_dataset(repo, "chart_reference", split="train")
rows = load_dataset(repo, "benchmark_rows_v2", split="test")
sites = load_dataset(repo, "evidence_sites", split="train")
print(chart[0]["image"].size, rows[0]["context_image"].size)
tables = {{name: load_dataset(repo, name) for name in get_dataset_config_names(repo)}}
```

`chart_reference.image`, `benchmark_rows_v1.context_image` and v2/v3 `context_image` and `exact_image` decode as Pillow images and can appear in the Hub viewer. Path columns retain logical PNG names for provenance; embedded PNGs are stored once in Parquet. Chart cards and count-page renders remain loose PNGs. Download a snapshot for those images, conventions and the scorer; pin `revision` to a chosen dataset commit for a repeatable analysis:

```python
from huggingface_hub import snapshot_download
from pathlib import Path
from PIL import Image
snapshot = Path(snapshot_download("{DATASET_ID}", repo_type="dataset"))
cards = load_dataset(repo, "benchmark_chart_cards", split="train")
card_image = Image.open(snapshot / cards[0]["image_path"])
```

For a cloned snapshot, substitute its folder for `repo` in `load_dataset`. Run `python code/extract_images.py --release . --out extracted` from its root if a tool needs loose chart/row PNGs. The scorer uses Parquet and needs no image extraction. `test` contains benchmark rows/readings; `train` on other configurations is a whole-table loader label.

## Components and construction

{overview}

`chart_reference` uses reviewed numeric reference version 2.1 and the original 687 atlas crops from PDF pages 20–21. Eight primary codes and two upper classes were corrected; all 16 earlier lower-code ambiguities are provisionally settled. Thirty-six records change numeric fields, including confidence: 33 cells are medium and 654 high on an uncalibrated qualitative scale. Previous-value columns and `change_note` record each change. Status: **Exploratory, two AI readings and a pixel check, no expert review**. The second reader read 63 cells blind, followed by a whole-chart pixel sweep; it did not independently eye-read every cell. Crops may include neighbouring ink. [Chart changes](provenance/chart-changes.json) preserves the exact field deltas and consumer impact.

The row-reading task gives a system row context, a proposed target box and chart cards. It returns the printed inscription number, its five-position classification and a visual left-to-right sequence of units, each with ranked graphic-code candidate sets. The frozen baseline is a chart-only template matcher. Inventory codes are edition labels.

### Benchmark frames and reference provenance

v1 contains 60 numbered-section occurrences from 3,460 detections on PDF pages 31–79. Three AI readers supplied disjoint initial groups; six convenience repeat readings are separate records. v2 contains 80 targets across `number_order`, `end_sorted` and `beginning_sorted`, with quotas 28/26/26 and eligible pools 3,596/3,228/3,496; it excludes development pages and v1 targets. v3 contains 80 fresh targets with the same quotas from pools 572/2,004/2,004 on 8/28/28 eligible pages. It excludes every page carrying a v1 or v2 target and the ten original development pages. The 80 v2 targets were used for v3 development and are excluded from the v3 test. These frames differ; the reported changes are comparisons across samples, rather than paired repair effects or edition-wide rates.

Two Claude Sonnet 5.5 readers and a Claude adjudicator produced each repair reference from shared conventions and chart cards, with no human check. The v3 readers agree on all 80 numbers, classifications, counts and line memberships, and on 357/369 strict unit sets. Count-page readings use pixel scripts with the field-block cue also used by the pipeline and a printed-line-pitch cross-check; recall measures agreement with this reference. Shared scratch collisions and directory observations in v2 and declared directory exposure in v3 are retained in [reader metadata](benchmark/reader-metadata.json) and adjudication notes. Wilson intervals and section-stratified row bootstraps do not cluster by source page; v3's 28 numbered rows span only eight pages.

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

V3 strict top five is 62/80 (77.5%; Wilson 95% 67.2–85.3%). Restricting the denominator to fully resolved references gives 62/77. The frozen shape-only score is 65/80 (81.3%; 71.3–88.3%). An Exploratory reading-choice sensitivity accepting {{23}} at 35:2 and 70:4 gives 64/80 and reaches the top-five threshold; count and number still fail. [Sensitivity](benchmark/v3-reading-choice-sensitivity.json) records the modified units separately.

### Chart-label vocabulary

All benchmark cards, references and predictions retain their original card labels, including earlier chart errors. Frozen scores therefore reproduce that historical vocabulary; `chart_reference` uses corrected version 2.1. Separate per-unit flag columns identify changed cells, affected prediction alternatives, possible candidate identities and the v3 58:0 locator conflict. An identifiable cell can have a class/confidence update without a code change. [Chart changes](provenance/chart-changes.json) records 11/0/8 directly changed reference units in v1/v2/v3, and 0/18/31 units needing candidate-identity review. A corrected-label rescoring is deferred until those identities and the locator conflict are reviewed; replacing numbers globally would conflate different drawings.

The [v2 reading convention](benchmark/CONVENTIONS.md) and [v3 convention](benchmark/CONVENTIONS-v3.md) describe independent reading before predictions were opened. Their `position-chart/` means that version's rows in `benchmark_chart_cards`; `page-count-source/` means the page PNGs in `benchmark_count_pages` or `benchmark_count_pages_v3`. The original `predictions.json` is represented by `prediction_json`; `frame.json` was the full detector frame and is excluded. Row locators and the v3 selection retain the benchmark geometry and sampling frame.

The census selects facts, citations, counts and project assessments from synthesis v6 and trimmed registers: 115 site/provenance entities, 17 publications, 37 collections and 15 datasets. `local_faces`, `local_families` and `local_cisi_identifiers` count the Lipi export pinned at commit `{LIPI_COMMIT}`. That export has no licence; only aggregates are published. Faces, provisional families and catalogue entries have distinct denominators. In 19 inspected CISI 1 Gujarat/north India ranges, 327/493 keys match and 166 are absent under the matching rule: 75 in pottery/graffiti sections and 91 in other sections. A worldwide missing-object denominator was not established.

`evidence_museum_joins` has 49 independently cited accession-to-CISI correspondences: 42 earlier pairs and seven supplement rows. Identifier-source citations distinguish museum identifiers, printed CISI 1 concordances and the Marshall composite table. The supplement awaits the earlier pairs' complete field adjudication. Museum descriptions and photographs are excluded. Collection and field-completeness observations are bounded historical queries; null denotes unmeasured values. [FIELD-DEFINITIONS.md](FIELD-DEFINITIONS.md) documents every field and shared assumption.

The exact Frenez–Tosi 2005 title is *{LOTHAL}*. The longer wording beginning “The Lothal Sealings” came from the earlier publication register; public tables use the [Zenodo record](https://zenodo.org/records/5514283).

The weight tables contain Exploratory fits and simulations. A **fitted unit** is a hypothesized common base mass under specified multiplier and noise rules. Dholavira's 5–100 g band has 90 weights and a 13.716 g unit; the 1.3–5 g band has 147 weights and a 14.280 g unit. The legacy western screen observes 136 geometric and 18 close hits. Mean geometric/close counts in its three nulls are 170.246/38.727 (±0.15 log jitter), 208.5675/50.3805 (±0.35 log jitter) and 193.9825/44.2695 (site log-uniform), with 2,000 draws each. All exceed the observations. [Methods](docs/METHODS.md#weight-metrology) describe the fit and controls. Excluded catalogue measurements and the full fitting pipeline are needed to repeat the original fit.

## Score a new row reader

Install scorer dependencies with `python -m pip install -r requirements.txt` from the snapshot. Supply one prediction for every sample as a JSON list, an object containing `rows`, or JSON Lines. Required row fields are `sample_index`, `occurrence_key`, `pdf_page`, `printed_inscription_id`, `classification_literal` and `units`. v2 and v3 require `section`: `number_order`, `end_sorted` or `beginning_sorted`. Copy frozen identifiers/section when preparing predictions. Preserve five classification positions, including blank spaces. Number and classification may be null.

Each unit requires `confidence`, the template-one confidence as a finite number in [0, 1], and ranked `alternatives`, each containing `codes`, an integer list. Confidence belongs to the unit and supplies top-one strict-intersection calibration. An alternative may contain several codes. This is an illustrative format example:

```json
{{"confidence": 0.7, "alternatives": [{{"codes": [25]}}, {{"codes": [2]}}]}}
```

```python
import subprocess, sys
subprocess.run([
    sys.executable, str(snapshot / "code/score_benchmark.py"),
    "--release", str(snapshot), "--benchmark", "v2",
    "--predictions", "my-predictions.jsonl", "--out", "my-scores.json"
], check=True)
```

The scorer rejects missing unit confidence and missing/invalid v2/v3 section. Omit `--predictions` to reproduce the frozen baseline. Outputs include candidate widths, count/number/classification accuracy, alignments, calibration and 2,000-draw intervals. It refuses to overwrite an output. v2/v3 source-row recall uses preserved detector geometry; new row predictions do not evaluate a new detector. [Expected metrics](benchmark/expected-metrics.json) preserve the baseline targets.

## Provenance, rights and limitations

Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki, ISBN 951-45-1627-3. The [official final-version record]({SOURCE}) supplies [CC BY 4.0]({CC}); the persistent handle is [10138/342677](http://hdl.handle.net/10138/342677). Edition-derived crops, chart cells/cards, page renders, inscription numbers, classifications and sign numbering retain that licence. The project waives its rights in additions to mixed configurations under CC0 1.0. Own compilations, readings, annotations, aggregates and documentation use CC0 1.0; code uses the Unlicense. The component table, [LICENSE](LICENSE), official texts in `LICENSES/` and [NOTICE](NOTICE) specify the structure and changes.

AI assistance produced chart labels, independent benchmark readings/adjudication, the template pipeline, research code and documentation. The chart and benchmark await expert epigraphic certification. `Frozen evaluation` identifies preserved evidence; `Exploratory` identifies annotations, later corrections and census/metrology interpretations. Reproduced arithmetic has `Verified computation` status; the baseline's criterion outcome is `Failed`. This dataset makes no decipherment claim.

The packaging sequence screen read `lipi_observed_faces.jsonl` and `mayig_faces.jsonl` for sequences of at least two units in both recorded directions: 3,506 distinct forward sequences and 6,878 distinct sequences counting both directions. It preserved Mayig's `P` namespace. The original v1/v2 screen tested 105 complete singleton reference rows, each with at least two units and exactly one strict candidate per unit. Version 0.3.0 adds 44 v3 rows, giving 149 tested rows; none equalled a whole indexed sequence in either direction. A broader reviewer scan normalized namespaces and tested runs of at least three positions across six derivatives, finding zero graphic-code runs and detecting all 200 planted controls. Its 12 generic integer-list hits are zero-based agreed-unit indices, repeated in the v3 reference and adjudication reading. These screens cover their input files and numbering; reuse after recoding is outside their reach. Text comparisons found no unexplained copied third-party prose; exact bibliography and official licence text are recorded separately.

[sources.json](sources.json) and `evidence_sources` give exact citations and access scopes, including inherited and snippet-only access. Portable `source-` labels identify original witnesses whose parent payloads are excluded. [EXCLUSIONS.md](EXCLUSIONS.md) lists omissions. The image manifest gives logical names, storage and PNG hashes; the file manifest lists every release file except itself.

## Citation and error reports

{AUTHOR} (2026). *{TITLE}*, version 0.3.0. [Dataset](https://huggingface.co/datasets/{DATASET_ID}). Cite Koskenniemi and Parpola (1979) when using edition-derived content.

```bibtex
@dataset{{indus2026reference,
  author = {{{AUTHOR}}},
  title = {{{TITLE}}},
  year = {{2026}},
  version = {{0.3.0}},
  url = {{https://huggingface.co/datasets/{DATASET_ID}}}
}}
```

Report errors through [GitHub issues]({ISSUES_URL}) with the dataset revision, configuration, row/cell key and source observation. Preserve unresolved candidates and distinguish label corrections from changes to frozen evidence.
'''
    (release/'README.md').write_text('---\n'+yaml.safe_dump(meta,sort_keys=False)+'---\n\n'+card,encoding='utf8')
    d=dict(DEFINITIONS)
    d.update(image='Embedded PNG, exposed as a datasets Image feature.',context_image='Embedded wider-context PNG, exposed as a datasets Image feature.',exact_image='Embedded proposed target-box PNG in v2/v3, exposed as a datasets Image feature.',image_path='Logical PNG name; image_assets gives storage. Extract embedded images with code/extract_images.py.',context_image_path='Logical context PNG name corresponding to context_image.',exact_image_path='Logical target-box PNG name, null in v1.',source_file='Portable original reader/card witness label.',source_path='Portable original parent-image witness label.',source_locator='Portable source label with exact row/field pointer.',method_path='Relative public method link in docs/METHODS.md.',null_model='Randomization rule: jitter-0.15, jitter-0.35 or site-log-uniform.',identifier_sources_json='JSON mapping each identifier field to its museum URL or printed catalogue citation.',storage='embedded or loose_png; each PNG is stored once.',cisi='Published CISI key in one of the 49 independently cited joins; placeholder values are null.',status='Exploratory or Frozen evaluation; see shared notes.',reader='A, B or C research-role label.',reference_json='Frozen reference JSON with portable source pointers.',prediction_json='Frozen chart-only prediction JSON with ranked alternatives and unit-level confidence.',reading_json='Original returned reading JSON with portable source pointers.',unit_g='Hypothesized common base mass under the public method description, grams.')
    d.update(reference_version='Reviewed chart numeric-reference version; 2.1 in this release.',
        sample_index='Zero-based index within v1, v2 or v3; each benchmark has a separate index space.',
        benchmark='v1, v2 or v3 frozen benchmark identifier.',
        reference_kind='Initial disjoint AI reading in v1, or adjudication following two AI readings in v2/v3.',
        original_ocr_locator_exposed='Whether v1 locator metadata contained OCR strings before the blinding correction; false in v2/v3.',
        previous_code='Original chart code when changed, otherwise null.',previous_rank='Original upper class when changed, otherwise null.',
        previous_alternatives='Original lower-code alternatives when changed; an empty list differs from null.',
        previous_rank_alternatives='Original upper-class alternatives when changed, otherwise null.',
        previous_numeric_confidence='Original qualitative confidence when changed, otherwise null.',
        changed_fields='Names of changed numeric fields relative to the original reference.',change_note='Short old-to-new numeric change description; null when unchanged.',
        chart_correction_flags_json='Per-unit chart-change flags for this reading, separate from the frozen reading JSON.',
        reference_chart_correction_flags_json='Per-reference-unit flags from the chart impact: corrected cells, field changes, candidate-identity warnings and locator conflict.',
        prediction_chart_correction_flags_json='Per-predicted-unit flags for alternatives whose template_key points to a changed chart cell.')
    fields='''# Field definitions

## Shared notes

Outer schemas are fixed; nested JSON retains optional reader fields and ambiguity. Null means unrecorded or unmeasured under the stated frame; zero is a measured outcome. Portable source labels identify original parent witnesses that are excluded. URLs are access pointers, rather than payload licences. Edition codes, printed occurrences, catalogue entries, face records and provisional families have separate namespaces and denominators. Chart and benchmark readings were AI-assisted and await expert certification.

Table `status` values are `Exploratory` and `Frozen evaluation`. Arithmetic validation uses `Verified computation`; the baseline criterion outcome is `Failed`. Mixed chart/benchmark components retain CC BY 4.0 for edition content and CC0 1.0 for project additions. Census/metrology compilations and documentation use CC0 1.0.

'''
    gaps=[]
    for name,spec in tables.items():
        fields+=f'## {name}\n\n| Field | Arrow type | Definition |\n|---|---|---|\n'
        for f in spec['schema']:
            if f['name'] not in d:gaps.append([name,f['name']])
            definition=d.get(f['name'],'Definition missing.').replace('â€™',"'").replace('Repository paths are evidence pointers, not public URLs.','')
            if f['name']=='frame':
                definition='random or stress source-count page frame.' if name.startswith('benchmark_count_pages') else 'Legacy or canonical metrological reference/multiplier rule in docs/METHODS.md.'
            fields+=f"| `{f['name']}` | `{f['type'].replace('item:','element:')}` | {definition} |\n"
        fields+='\n'
    fields+='''## Nested benchmark fields

References contain sample_index, printed_inscription_id, classification_literal, crop_correct, drawn_unit_count and ordered units. A unit's strict_candidate_codes combines drawing, underline and vertical-position evidence; shape_only_candidate_codes is a broader diagnostic set. Empty strict sets are unresolved. Damage/hatching is a modern editorial drawing unit with unknown ancient sign extent. valid_printed_target=false is scored as a false detection in v2/v3.

Prediction units contain confidence in [0, 1] and ranked alternatives, each with codes. Original template order, costs and confidence reproduce alignment/calibration. v2/v3 section supplies stratified bootstrap membership. Classifications preserve five positions, including spaces. serialization records visual ordering; confidence and template scores describe model output.

Locator coordinates ending _2x use two pixels per PDF point; _pdf_box/_pdf_points use PDF points. Original crop filenames are locator observations; outer logical paths and image columns locate assets. Count references give columns, extents, counts and centers. Recall greedily matches nearest eligible centers within nine PDF points; continuation lines do not add numbered occurrences. V3 numbered recall uses the numbered anchor, while physical-line recall uses glyph-box centers and includes continuations. Per-unit correction flags never change frozen codes: corrected_cell identifies a linked changed record; candidate_identity_review flags possible unlocated identities; locator_conflict retains conflicting witnesses. Reader metadata retains process disclosures, and the v1 overlay is separate from frozen scoring.
'''
    (release/'FIELD-DEFINITIONS.md').write_text(fields,encoding='utf8');dump(release/'provenance/field-documentation-check.json',dict(missing_specific_definitions=gaps))
    if gaps:raise ValueError(gaps)
    (release/'LICENSE').write_text('''Component licences, confirmed by k-sandhu on 8 October 2026

CC BY 4.0: Helsinki 1979 edition-derived images, crops, chart cells/cards, page renders, inscription numbers, classifications and sign numbering. Preserve NOTICE attribution and changes.
CC0 1.0: project data, compilations, readings, annotations, aggregates and documentation. In mixed configurations this waives project rights in additions; the edition-derived content retains CC BY 4.0.
Unlicense: project code in code/.

The README component table specifies each configuration. Official texts are in LICENSES/CC0-1.0.txt, LICENSES/CC-BY-4.0.txt and LICENSES/Unlicense.txt. Excluded third-party payloads receive no project licence.
''',encoding='utf8')
    (release/'LICENSES').mkdir(exist_ok=True)
    for name in ['CC0-1.0.txt','CC-BY-4.0.txt','Unlicense.txt']:shutil.copyfile(RAW/'review-fixes-2026-10-08-sources'/name,release/'LICENSES'/name)
    (release/'NOTICE').write_text(f'''Source attribution

Kimmo Koskenniemi and Asko Parpola. Corpus of Texts in the Indus Script. 1979. Research Reports 1. Department of Asian and African Studies, University of Helsinki. ISBN 951-45-1627-3.
Official final version: {SOURCE}
Handle: http://hdl.handle.net/10138/342677
Source licence: CC BY 4.0, {CC}

Changes: raster crops, arranged chart cards, count-page renders, AI-assisted numeric-label readings, candidate-set annotations, chart-only recognition/scoring, portable provenance labels and embedded PNG packaging. Version 0.3.0 adopts reviewed chart labels and previous-value columns, retains the original frozen benchmark card vocabulary and editorial markers, and adds a third frozen evaluation and per-unit chart-impact flags. Source authors have not certified these changes or endorsed the dataset.

Project author: {AUTHOR}. Project rights in data, compilations, readings, annotations, aggregates and documentation are waived under CC0 1.0; code is under the Unlicense. Edition-derived content retains CC BY 4.0. Bibliographic sources appear in sources.json and evidence_sources; other payloads are excluded.
''',encoding='utf8')
    cff={'cff-version':'1.2.0','message':f'Cite this dataset and Koskenniemi and Parpola 1979 for edition-derived content. Report errors through {ISSUES_URL}.','type':'dataset','title':TITLE,'version':'0.3.0','date-released':'2026-10-08','authors':[{'alias':AUTHOR}],'license':['CC0-1.0','CC-BY-4.0','Unlicense'],'url':f'https://huggingface.co/datasets/{DATASET_ID}','references':[{'type':'book','title':'Corpus of Texts in the Indus Script','authors':[{'family-names':'Koskenniemi','given-names':'Kimmo'},{'family-names':'Parpola','given-names':'Asko'}],'year':1979,'publisher':{'name':'Department of Asian and African Studies, University of Helsinki'},'url':SOURCE}]}
    (release/'CITATION.cff').write_text(yaml.safe_dump(cff,sort_keys=False),encoding='utf8')
    (release/'EXCLUSIONS.md').write_text('''# Excluded material

Lipi exports, record-level predictions and models lack a redistribution licence. Mayig derivatives are excluded while separate CISI photograph rights remain unresolved. Nineteen museum joins rest only on the Lipi excavation-number comparison; the public table retains independently cited catalogue facts.

The full provisional 1979 transcription failed recognition criteria and remains quarantined. Only the 60/80/80 frozen evaluation subsets are included. Future verified full-corpus rows require a separate addition. Corrected-label rescoring awaits candidate identity and locator review. Third-party PDFs, other page images, museum descriptions/photographs, raw API responses, Ascalone 2022 catalogue rows and lecture transcript/record-level inputs are excluded. Metrology tables contain aggregate values only. Owner decisions and full local audits are kept outside the dataset.
''',encoding='utf8')
    (release/'docs').mkdir(exist_ok=True)
    (release/'docs/METHODS.md').write_text('''# Aggregate-table methods

## Evidence census

Synthesis v6 reconciles site labels and counts separately for face records, provisional families, catalogue entries and bounded collection queries. CISI 1 coverage compares base keys in inspected ranges, with recorded prefix aliases and duplicate-caption exclusions. Field completeness distinguishes measured presence, structural schema absence and inherited assessments. Museum joins are small factual extracts of identifier pairs, with citations per identifier to museum records, CISI 1 concordances or Marshall composite tables.

## Weight metrology

The primary frame selects preserved, weighed, complete objects classified as weights under the source eligibility rules. A fitted base mass is multiplied by specified denominations; the signal model uses proportional log-mass noise and a background component. Dholavira bands are below-1.3, 1.3–5, 5–100 and above-100 g. Aggregate rows retain sample sizes, fitted unit, signal dispersion/probability, within-3% counts and bootstrap unit limits.

The western screen compares nearest absolute log residuals to an Indus reference and competing local standards. A geometric hit means the Indus reference has a smaller absolute log residual than the best local standard. A close hit also requires at most 3% Indus residual and at least one percentage-point advantage over the best local residual. The legacy frame preserves its original rule/reference; canonical frames use 13.65 g or the 13.716 g mass-band reference and explicit local rivals.

Each null has 2,000 draws. Jitter multiplies masses by exp(U[-j,j]), with j=0.15 or 0.35. Site log-uniform draws independently within each site's observed log-mass range. These retain broad ranges while removing fine structure. weight_chance_controls gives central simulation intervals and fractions at least as large as observations. Results are Exploratory and conditional on selected objects/denominations. Excluded record-level measurements and the fitting implementation are needed for full replay.

Source: Enrico Ascalone (2022), Bronze Age Weights from Mesopotamia, Iran & Greater Indus Valley, Weight & Value 3, Wachholtz; Dholavira classification pp.135–136 and metrology pp.166–172, as recorded by the contributing analysis. Exact bibliography and access scope are in sources.json. Catalogue rows are excluded.
''',encoding='utf8')
    public_sources=read(HERE/'sources.json')
    for key in ['failed_downloads','failed_searches','searches','licence_downloads']:public_sources.pop(key,None)
    dump(release/'sources.json',builder.portable.value(public_sources))
    dump(HERE/'rights-audit.json',read(builder.records/'rights-audit.json'))
    write_owner_records()

def write_owner_records():
    checklist=f'''# Owner checklist and upload steps

The owner confirmed own data/documentation CC0 1.0 and code Unlicense on 8 October 2026. Edition content retains CC BY 4.0. Author: {AUTHOR}, no affiliation or other personal details. The scorer and public methods are included. The coordinator uploaded version 0.2.0 privately and reports all 19 configurations (2,720 rows) and images loading. Package O performs no upload, repository creation or visibility change.

Three decisions remain open:

- [ ] Confirm the public issues repository and `{ISSUES_URL}`. Update the single ISSUES_URL constant in release_policy.py and rebuild if another repository is chosen. The issue link must open before public release.
- [ ] Decide whether Hugging Face's rights terms permit the Lipi-derived files to remain in the private backup.
- [ ] Approve the final revision and visibility switch after private hosted review.

## Upload privately first

Use an authenticated owner session; upload only release/, excluding this checklist, rights-audit.json, build records, history, review/, private-store/ and raw records. This is a future manual recipe:

```python
from huggingface_hub import HfApi
api = HfApi()
repo_id = "{DATASET_ID}"
# The private preview repository already exists; inspect it before updating.
assert api.repo_info(repo_id, repo_type="dataset").private
commit = api.upload_folder(
    repo_id=repo_id, repo_type="dataset",
    folder_path="experiments/2026-10-08-hf-public-release/release",
    commit_message="Update reference benchmarks to 0.3.0 for private owner review",
)
print(commit.oid)
```

The existing private preview holds 0.2.0. Record the updated uploaded commit, download that private revision, compare every file against provenance/file-manifest.json and repeat loading/scoring. Inspect all configurations, including v3 and the corrected chart, and embedded images. Confirm the issues URL and CFF citation while still private. Hosted 0.3.0 checks remain for the coordinator after this local handoff.

After owner approval, use the dataset Settings visibility control to make **ksaw008/indus-reference-benchmarks** public and record its released commit. Keep ksaw008/indus-research-data and the current GitHub research repository private. Instructions follow https://huggingface.co/docs/huggingface_hub/guides/upload and https://huggingface.co/docs/hub/repositories-settings.

The public EXCLUSIONS.md lists omitted material. Full decisions/hashes remain in rights-audit.json and build-records/. The 19 removed joins are local raw records. Review the new dated validation and reviewer reruns before upload.
'''
    (HERE/'RELEASE-CHECKLIST.md').write_text(checklist,encoding='utf8')
    p=HERE/'private-store';p.mkdir(exist_ok=True)
    source=ROOT/'experiments/2026-10-06-research-program/hf-hosting-manifest.json';m=read(source);dump(p/'checksums-manifest.json',m)
    groups={}
    for r in m['files']+m['backed_up_files_kept_locally']:
        g=groups.setdefault(r['set'],dict(files=0,bytes=0));g['files']+=1;g['bytes']+=r['bytes']
    table='| Set | Repository-relative path | Files | Bytes |\n|---|---|---:|---:|\n'
    for n,g in groups.items():
        path=m['sets'][n]['path']+'/' if n in m['sets'] else next(r['path'] for r in m['backed_up_files_kept_locally'] if r['set']==n)
        table+=f"| {n} | `{path}` | {g['files']} | {g['bytes']} |\n"
    patterns=['data/raw/2026-10-06-modern-restoration/main/**','data/raw/2026-10-06-modern-restoration/frozen-model/**']+[r['path'] for r in m['backed_up_files_kept_locally']]
    text=f'''---
pretty_name: Indus research private backup
tags:
- indus-script
- private-backup
---

# Indus research private backup

`ksaw008/indus-research-data` backs up large outputs from the private `k-sandhu/indus-valley-script` research repository. The manifest lists 1,038 files totaling 3,406,008,409 bytes. The 1,034 restoration files were removed locally with free-local after verification; the Hub now holds their only copy. The prediction/model groups total 3,083,272,144 and 3,214,711 bytes respectively. The four Helsinki backups remain locally.

{table}

The 1,029 restoration files include query/fold JSONL, arrays, fitted counts and checkpoints; five frozen-model files hold counts, three seed weights and a training register. They derive from the Lipi export, for which no licence was found, and remain private. Four Helsinki outputs hold provisional occurrences, a ledger import and v1/v2 repair frames. Their 1979 source is CC BY 4.0; the full transcription failed evaluation and remains quarantined. No third-party PDF scans appear in the manifest.

GitHub holds code, protocols and aggregate research outputs; this backup holds large payloads omitted from Git, in matching repository-relative paths. It is a restore layout. The separate {DATASET_ID} dataset selects licensed edition derivatives and own compilations; its release leaves this backup's rights and visibility unchanged.

## Restore and verification

From the private repository root, use an authenticated owner session:

```powershell
python -B experiments/2026-10-06-research-program/hf_host.py restore --repo ksaw008/indus-research-data
```

restore downloads only the two restoration directories. For the four Helsinki files or a pinned restore to a separate folder:

```python
from huggingface_hub import snapshot_download
snapshot_download(
    "ksaw008/indus-research-data", repo_type="dataset",
    revision="OWNER_SELECTED_COMMIT", local_dir="RESTORE_DIRECTORY",
    allow_patterns={patterns!r},
)
```

Retain only the needed pattern to restore one part. Obtain the remote commit before a pinned restore; the local manifest does not record one. [checksums-manifest.json](checksums-manifest.json) lists all paths, sizes and SHA-256 values, including four locally retained backups. After downloading, check all 1,038 files:

```powershell
python -B experiments/2026-10-08-hf-public-release/verify_private_store.py --root RESTORE_DIRECTORY --out experiments/2026-10-08-hf-public-release/private-restore-check.json
```

hf_host.py verify checks local restoration copies against the Hub. Since those files were removed, it currently finds nothing to check. The coordinator added verify-remote, which compares every manifest entry with Hub-reported size/SHA-256 and downloads/hashes the 122 small non-LFS files:

```powershell
python -B experiments/2026-10-06-research-program/hf_host.py verify-remote --repo ksaw008/indus-research-data
```

The coordinator reports that this matched 1,038/1,038 files on 8 October 2026. Package O read the implementation and manifest but did not repeat the remote check. The coordinator's new publish-card command uploads this README:

```powershell
python -B experiments/2026-10-06-research-program/hf_host.py publish-card --repo ksaw008/indus-research-data --card experiments/2026-10-08-hf-public-release/private-store/README.md
```

## Owner note

Whether Hugging Face's rights terms permit continued private storage of Lipi-derived files is an open owner decision. This card records recovery steps without resolving that question.

Author: {AUTHOR}. Full source/rights decisions remain in the private research provenance records. This documentation revision performed no restore, upload, repository creation or visibility change.
'''
    (p/'README.md').write_text(text,encoding='utf8')
    dump(p/'inventory-summary.json',dict(source_manifest=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),sets=groups,total_files=1038,total_bytes=3406008409,restoration_local_copies_removed=1034,remote_verification=dict(date='2026-10-08',matched=1038,total=1038,non_lfs_downloaded=122,evidence='Coordinator report; implementation inspected, not rerun by Package O')))
