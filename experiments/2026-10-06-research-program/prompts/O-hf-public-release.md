# Package O: prepare a public Hugging Face dataset and document the private store

Owned directory: `maintenance/2026-10-08-hf-public-release/`. Local raw directory: `data/raw/2026-10-08-hf-public-release/`. Python environments: the system Python and `C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe`; you may install the `datasets` and `pyarrow` libraries into the venv with `pip --no-cache-dir` to validate loading.

## Request

The user asked for much better descriptions and usage instructions for the project's Hugging Face dataset and for it to be made ready for public release. The existing dataset, `ksaw008/indus-research-data` (private), holds package A's per-query predictions and model files and backups of large digitization outputs (see `experiments/2026-10-06-research-program/hf-hosting-manifest.json` and `hf_host.py`). Package A's predictions and models are derived from the Lipi corpus export, which has no licence, so that dataset must stay private. The coordinator therefore asks for two deliverables: a public-release candidate built only from material that can be redistributed, staged locally for review, and a clear description for the private store. Do not upload anything, create repositories or change any visibility; the coordinator will upload the staged folder to a new private repository for the user to inspect, and the user decides on public release.

Read first: `AGENTS.md`, `knowledge/editorial/WRITING.md`, `knowledge/provenance/REDISTRIBUTION.md`, `knowledge/provenance/SOURCES.md`, `REUSE.md`, `knowledge/INDEX.md` and `experiments/2026-10-06-research-program/REPORT.md`. Packages M (`experiments/2026-10-07-helsinki1979-digitization/`) and N (`experiments/2026-10-08-helsinki1979-row-verification/`) are running; read their files but do not write to them.

## Candidate content

Assess each candidate file by file, record a decision and its basis in `rights-audit.json` (status vocabulary from `REDISTRIBUTION.md`: own-work, explicit-license, permission-recorded, rights-unverified, mixed-assets), and include only what passes:

1. **Sign chart reference.** The 687-cell annotated chart from the CC BY 4.0 1979 Helsinki edition (`research/chart_reference/manual_numeric_reference.json`, `output/chart_atlas/`, and the corpus records in `research/corpus/primary/chart_complete/`), with crops, numeric labels, the 16 retained lower-code ambiguities, and the fact that AI models read the labels without expert certification.
2. **Row-reading benchmark.** The blind evaluation sets for the 1979 edition: the first 60-row set and the v2 80-row set, with their crops, chart cards, the independent readings and the adjudicated references, the `CONVENTIONS.md` reading rules and the scoring code (package M's `evaluate.py` and `evaluate_repair.py`, or a self-contained scorer you write and validate against their outputs). Include the v2 pipeline's predictions for those rows so others can reproduce the reported scores. All of this derives from the CC BY 4.0 edition and the project's own readings.
3. **Evidence census tables.** Site, publication, collection and dataset registers, the CISI 1 coverage comparison, field-completeness tables and the museum-to-corpus joins from `experiments/2026-10-06-evidence-census/` (use the synthesis v6 endpoint and the trimmed source files). Include only facts, identifiers, counts, citations and the project's own assessments; exclude any copied third-party prose, any record-level content from the Lipi export, and any museum text or images whose licence does not permit it.
4. **Aggregate study results** where useful and clearly derived (for example the tests of the Frenez lecture statements and the weight-metrology summaries), as small tables with links to the method descriptions; no record-level third-party content.

Exclude package A's predictions and models, any sign sequence or record from the Lipi or Mayig derivatives (Mayig is MIT, but include it only if you also include its notice and the CISI photo rights question is resolved), the quarantined provisional 1979 transcription (it will be added after verification), third-party PDFs, page images other than CC BY-derived crops, and catalogue rows from Ascalone 2022.

## Staged release

Build `release/` in the owned directory with the exact layout of the future Hugging Face repository:
- `README.md`: the dataset card, with YAML metadata (license per component, pretty name, tags such as indus-script, epigraphy, archaeology, undeciphered-script, task categories that fit, size category) and a `configs` section with one named configuration per component and its `data_files`, so `load_dataset(repo, config_name)` works and the dataset viewer shows each table. The card explains in plain, connected prose what the Indus script is in one paragraph, what each configuration contains and how it was made, the field definitions, how to load each configuration in Python with short examples, how to score a new row reader against the benchmark, provenance and licences per component with the required attribution to Kimmo Koskenniemi and Asko Parpola's *Corpus of Texts in the Indus Script* (1979), University of Helsinki, CC BY 4.0, known limitations and statuses (exploratory results, AI-read labels, no expert review yet, no decipherment claim), the role of AI assistance in producing the work, how to cite it, and how to report errors. Follow `WRITING.md`.
- Data in Parquet or JSON Lines with stable schemas, images as PNG referenced by relative path or embedded in Parquet image columns, small and documented.
- `LICENSE` and `NOTICE` files covering each component, and `CITATION.cff`. Use CC BY 4.0 for components derived from the 1979 edition. For the project's own compilations and code, prepare CC BY 4.0 for data and MIT for code as a proposal and mark both as awaiting the user's confirmation in `RELEASE-CHECKLIST.md`; leave author and contact fields as clearly marked placeholders for the user to fill.
- `RELEASE-CHECKLIST.md`: the decisions the user must make (licences for own work, author name and affiliation, contact, whether to make the GitHub code repository public or include code here), the exact upload and visibility steps, and a list of what was excluded and why.

Validate: load every configuration with the `datasets` library from the local `release/` folder, check row counts and schemas against the sources, check that every image path resolves, recompute the benchmark scores from the staged files and confirm they match the published package M metrics, and scan every staged file for sign sequences from unlicensed sources and copied third-party prose. Record the results in `validation.json`.

## Private store description

Write `private-store/README.md`: a clear card for `ksaw008/indus-research-data` stating that it is a private backup, listing what it holds by path (from `hf-hosting-manifest.json`), why it is private, how to restore each part with `hf_host.py restore` or `huggingface_hub`, the checksums manifest, and how it relates to the GitHub repository and the public dataset.

Also write `PROTOCOL.md`, `README.md`, `RETROSPECTIVE.md` and `registry-entry.json` in the owned directory as for other packages.
