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
    card=f'''# {TITLE}

This dataset contains 687 annotated Helsinki chart cells, two frozen row-reading benchmarks of 60 and 80 rows, an evidence census and small metrology summaries. The chart and benchmark row tables have embedded image columns for the dataset viewer. Its 19 Parquet configurations contain 2,720 rows counting heterogeneous observations, images and readings.

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

`chart_reference.image`, `benchmark_rows_v1.context_image` and v2 `context_image` and `exact_image` decode as Pillow images and can appear in the Hub viewer. Path columns retain logical PNG names for provenance; embedded PNGs are stored once in Parquet. Chart cards and count-page renders remain loose PNGs. Download a snapshot for those images, conventions and the scorer; pin `revision` to a chosen dataset commit for a repeatable analysis:

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

`chart_reference` combines atlas crops from PDF pages 20–21 with numeric-label annotations. AI models read upper ranks and lower graphic codes and rechecked disagreements. Sixteen lower-code ambiguities remain in `alternatives`; crops can contain neighbouring ink. These AI-read labels await expert certification.

The row-reading task gives a system row context, a proposed target box and chart cards. It returns the printed inscription number, its five-position classification and a visual left-to-right sequence of units, each with ranked graphic-code candidate sets. The frozen baseline is a chart-only template matcher. Inventory codes are edition labels.

v1 samples 60 numbered-section occurrences from 3,460 detections on PDF pages 31–79. Three AI readers supplied disjoint initial groups; six convenience repeat readings are separate records. An **exposed OCR locator** means the original locator metadata contained OCR strings before the blinding correction, affecting 22/60 targets. The **eleven-code overlay** records eleven later source-based code corrections; it is Exploratory and does not alter the frozen v1 endpoint. That endpoint matches 33/60 unit counts, reads 23/60 inscription numbers and produces 24/60 top-five compatible whole rows.

v2 selects 80 fresh targets in `number_order`, `end_sorted` and `beginning_sorted`, with quotas 28/26/26, excluding development pages and v1 targets. Two AI readers read every row; a third adjudicated against source images and the chart. Independent readings, page inventories and adjudication notes are preserved. Shared scratch collisions and directory observations reduced process isolation; [reader metadata](benchmark/reader-metadata.json) retains the disclosures.

The v2 baseline accepts 44/80 crops, matches 59/80 counts, reads 62/80 numbers and 55/80 classifications, and produces 20/80 top-one and 40/80 top-five compatible whole rows. A **compatible whole row** has nonempty strict reference sets at every unit and zero candidate-set edit distance to the prediction, with intersections at each aligned position. **Aligned unit recall** maximizes matching intersections among minimum-edit alignments and divides by resolved reference units. Top-five recall is 304/352. Random-page recall is 1,242/1,286 across 18 pages; three stress pages give 561/561.

The five v2 pass criteria are crop correctness ≥90% (72/80), inscription-number accuracy ≥90% (72/80), unit-count agreement ≥95% (76/80), top-five compatible whole rows ≥80% (64/80), and random-page recall ≥95%. Only the last passes. The full provisional transcription is excluded.

The [reading convention](benchmark/CONVENTIONS.md) applies to v2. Its `position-chart/` means the v2 cards in `benchmark_chart_cards`; `page-count-source/` means the count-page PNGs in `benchmark_count_pages.image_paths`. Its withheld `predictions.json` is represented here by `prediction_json`; `frame.json` was the full detector frame and is excluded. The convention describes independent reading before predictions were opened.

The census selects facts, citations, counts and project assessments from synthesis v6 and trimmed registers: 115 site/provenance entities, 17 publications, 37 collections and 15 datasets. `local_faces`, `local_families` and `local_cisi_identifiers` count the Lipi export pinned at commit `{LIPI_COMMIT}`. That export has no licence; only aggregates are published. Faces, provisional families and catalogue entries have distinct denominators. In 19 inspected CISI 1 Gujarat/north India ranges, 327/493 keys match and 166 are absent under the matching rule: 75 in pottery/graffiti sections and 91 in other sections. A worldwide missing-object denominator was not established.

`evidence_museum_joins` has 49 independently cited accession-to-CISI correspondences: 42 earlier pairs and seven supplement rows. Identifier-source citations distinguish museum identifiers, printed CISI 1 concordances and the Marshall composite table. The supplement awaits the earlier pairs' complete field adjudication. Museum descriptions and photographs are excluded. Collection and field-completeness observations are bounded historical queries; null denotes unmeasured values. [FIELD-DEFINITIONS.md](FIELD-DEFINITIONS.md) documents every field and shared assumption.

The exact Frenez–Tosi 2005 title is *{LOTHAL}*. The longer wording beginning “The Lothal Sealings” came from the earlier publication register; public tables use the [Zenodo record](https://zenodo.org/records/5514283).

The weight tables contain Exploratory fits and simulations. A **fitted unit** is a hypothesized common base mass under specified multiplier and noise rules. Dholavira's 5–100 g band has 90 weights and a 13.716 g unit; the 1.3–5 g band has 147 weights and a 14.280 g unit. The legacy western screen observes 136 geometric and 18 close hits. Mean geometric/close counts in its three nulls are 170.246/38.727 (±0.15 log jitter), 208.5675/50.3805 (±0.35 log jitter) and 193.9825/44.2695 (site log-uniform), with 2,000 draws each. All exceed the observations. [Methods](docs/METHODS.md#weight-metrology) describe the fit and controls. Excluded catalogue measurements and the full fitting pipeline are needed to repeat the original fit.

## Score a new row reader

Install scorer dependencies with `python -m pip install -r requirements.txt` from the snapshot. Supply one prediction for every sample as a JSON list, an object containing `rows`, or JSON Lines. Required row fields are `sample_index`, `occurrence_key`, `pdf_page`, `printed_inscription_id`, `classification_literal` and `units`. v2 requires `section`: `number_order`, `end_sorted` or `beginning_sorted`. Copy frozen identifiers/section when preparing predictions. Preserve five classification positions, including blank spaces. Number and classification may be null.

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

The scorer rejects missing unit confidence and missing/invalid v2 section. Omit `--predictions` to reproduce the frozen baseline. Outputs include candidate widths, count/number/classification accuracy, alignments, calibration and 2,000-draw intervals. It refuses to overwrite an output. v2 source-row recall uses preserved detector geometry; new row predictions do not evaluate a new detector. [Expected metrics](benchmark/expected-metrics.json) preserve the baseline targets.

## Provenance, rights and limitations

Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki, ISBN 951-45-1627-3. The [official final-version record]({SOURCE}) supplies [CC BY 4.0]({CC}); the persistent handle is [10138/342677](http://hdl.handle.net/10138/342677). Edition-derived crops, chart cells/cards, page renders, inscription numbers, classifications and sign numbering retain that licence. The project waives its rights in additions to mixed configurations under CC0 1.0. Own compilations, readings, annotations, aggregates and documentation use CC0 1.0; code uses the Unlicense. The component table, [LICENSE](LICENSE), official texts in `LICENSES/` and [NOTICE](NOTICE) specify the structure and changes.

AI assistance produced chart labels, independent benchmark readings/adjudication, the template pipeline, research code and documentation. The chart and benchmark await expert epigraphic certification. `Frozen evaluation` identifies preserved evidence; `Exploratory` identifies annotations, later corrections and census/metrology interpretations. Reproduced arithmetic has `Verified computation` status; the baseline's criterion outcome is `Failed`. This dataset makes no decipherment claim.

The packaging sequence screen read `lipi_observed_faces.jsonl` and `mayig_faces.jsonl` for sequences of at least two units in both recorded directions: 3,506 distinct forward sequences and 6,878 distinct sequences counting both directions. It preserved Mayig's `P` namespace. The 105 complete singleton benchmark reference rows each have at least two units and exactly one strict candidate per unit; none equalled a whole indexed sequence in either direction. A broader reviewer scan normalized namespaces and tested runs of at least three positions across six derivatives, finding zero sequence runs and detecting all 200 planted controls. These screens cover their input files and numbering; reuse after recoding is outside their reach. Text comparisons found no unexplained copied third-party prose; exact bibliography and official licence text are recorded separately.

[sources.json](sources.json) and `evidence_sources` give exact citations and access scopes, including inherited and snippet-only access. Portable `source-` labels identify original witnesses whose parent payloads are excluded. [EXCLUSIONS.md](EXCLUSIONS.md) lists omissions. The image manifest gives logical names, storage and PNG hashes; the file manifest lists every release file except itself.

## Citation and error reports

{AUTHOR} (2026). *{TITLE}*, version 0.2.0. [Dataset](https://huggingface.co/datasets/{DATASET_ID}). Cite Koskenniemi and Parpola (1979) when using edition-derived content.

```bibtex
@dataset{{indus2026reference,
  author = {{{AUTHOR}}},
  title = {{{TITLE}}},
  year = {{2026}},
  version = {{0.2.0}},
  url = {{https://huggingface.co/datasets/{DATASET_ID}}}
}}
```

Report errors through [GitHub issues]({ISSUES_URL}) with the dataset revision, configuration, row/cell key and source observation. Preserve unresolved candidates and distinguish label corrections from changes to frozen evidence.
'''
    (release/'README.md').write_text('---\n'+yaml.safe_dump(meta,sort_keys=False)+'---\n\n'+card,encoding='utf8')
    d=dict(DEFINITIONS)
    d.update(image='Embedded PNG, exposed as a datasets Image feature.',context_image='Embedded wider-context PNG, exposed as a datasets Image feature.',exact_image='Embedded proposed target-box PNG in v2, exposed as a datasets Image feature.',image_path='Logical PNG name; image_assets gives storage. Extract embedded images with code/extract_images.py.',context_image_path='Logical context PNG name corresponding to context_image.',exact_image_path='Logical target-box PNG name, null in v1.',source_file='Portable original reader/card witness label.',source_path='Portable original parent-image witness label.',source_locator='Portable source label with exact row/field pointer.',method_path='Relative public method link in docs/METHODS.md.',null_model='Randomization rule: jitter-0.15, jitter-0.35 or site-log-uniform.',identifier_sources_json='JSON mapping each identifier field to its museum URL or printed catalogue citation.',storage='embedded or loose_png; each PNG is stored once.',cisi='Published CISI key in one of the 49 independently cited joins; placeholder values are null.',status='Exploratory or Frozen evaluation; see shared notes.',reader='A, B or C research-role label.',reference_json='Frozen reference JSON with portable source pointers.',prediction_json='Frozen chart-only prediction JSON with ranked alternatives and unit-level confidence.',reading_json='Original returned reading JSON with portable source pointers.',unit_g='Hypothesized common base mass under the public method description, grams.')
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
                definition='random or stress source-count page frame.' if name=='benchmark_count_pages' else 'Legacy or canonical metrological reference/multiplier rule in docs/METHODS.md.'
            fields+=f"| `{f['name']}` | `{f['type'].replace('item:','element:')}` | {definition} |\n"
        fields+='\n'
    fields+='''## Nested benchmark fields

References contain sample_index, printed_inscription_id, classification_literal, crop_correct, drawn_unit_count and ordered units. A unit's strict_candidate_codes combines drawing, underline and vertical-position evidence; shape_only_candidate_codes is a broader diagnostic set. Empty strict sets are unresolved. Damage/hatching is a modern editorial drawing unit with unknown ancient sign extent. valid_printed_target=false is scored as a false detection in v2.

Prediction units contain confidence in [0, 1] and ranked alternatives, each with codes. Original template order, costs and confidence reproduce alignment/calibration. v2 section supplies stratified bootstrap membership. Classifications preserve five positions, including spaces. serialization records visual ordering; confidence and template scores describe model output.

Locator coordinates ending _2x use two pixels per PDF point; _pdf_box/_pdf_points use PDF points. Original crop filenames are locator observations; outer logical paths and image columns locate assets. Count references give columns, extents, counts and centers. Recall greedily matches nearest eligible centers within nine PDF points; continuation lines do not add numbered occurrences. Reader metadata retains process disclosures, and the v1 overlay is separate from frozen scoring.
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

Changes: raster crops, arranged chart cards, count-page renders, AI-assisted numeric-label readings, candidate-set annotations, chart-only recognition/scoring, portable provenance labels and embedded PNG packaging. Unresolved labels and editorial markers are retained. Source authors have not certified these changes or endorsed the dataset.

Project author: {AUTHOR}. Project rights in data, compilations, readings, annotations, aggregates and documentation are waived under CC0 1.0; code is under the Unlicense. Edition-derived content retains CC BY 4.0. Bibliographic sources appear in sources.json and evidence_sources; other payloads are excluded.
''',encoding='utf8')
    cff={'cff-version':'1.2.0','message':f'Cite this dataset and Koskenniemi and Parpola 1979 for edition-derived content. Report errors through {ISSUES_URL}.','type':'dataset','title':TITLE,'version':'0.2.0','date-released':'2026-10-08','authors':[{'alias':AUTHOR}],'license':['CC0-1.0','CC-BY-4.0','Unlicense'],'url':f'https://huggingface.co/datasets/{DATASET_ID}','references':[{'type':'book','title':'Corpus of Texts in the Indus Script','authors':[{'family-names':'Koskenniemi','given-names':'Kimmo'},{'family-names':'Parpola','given-names':'Asko'}],'year':1979,'publisher':{'name':'Department of Asian and African Studies, University of Helsinki'},'url':SOURCE}]}
    (release/'CITATION.cff').write_text(yaml.safe_dump(cff,sort_keys=False),encoding='utf8')
    (release/'EXCLUSIONS.md').write_text('''# Excluded material

Lipi exports, record-level predictions and models lack a redistribution licence. Mayig derivatives are excluded while separate CISI photograph rights remain unresolved. Nineteen museum joins rest only on the Lipi excavation-number comparison; the public table retains independently cited catalogue facts.

The full provisional 1979 transcription failed recognition criteria and remains quarantined. Future verified rows require a separate addition. Third-party PDFs, other page images, museum descriptions/photographs, raw API responses, Ascalone 2022 catalogue rows and lecture transcript/record-level inputs are excluded. Metrology tables contain aggregate values only. Owner decisions and full local audits are kept outside the dataset.
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

The owner confirmed own data/documentation CC0 1.0 and code Unlicense on 8 October 2026. Edition content retains CC BY 4.0. Author: {AUTHOR}, no affiliation or other personal details. The scorer and public methods are included. No upload, repository creation or visibility change was performed.

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
api.create_repo(repo_id, repo_type="dataset", private=True, exist_ok=False)
assert api.repo_info(repo_id, repo_type="dataset").private
commit = api.upload_folder(
    repo_id=repo_id, repo_type="dataset",
    folder_path="experiments/2026-10-08-hf-public-release/release",
    commit_message="Prepare reference benchmarks for private owner review",
)
print(commit.oid)
```

If that ID exists, inspect its contents/visibility before selecting an update; this recipe refuses an existing ID. Record the uploaded commit, download that private revision, compare every file against provenance/file-manifest.json and repeat loading/scoring. Inspect all 19 viewer configurations and embedded chart/row images. Confirm the issues URL and CFF citation, then upload the final reviewed revision while still private.

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
