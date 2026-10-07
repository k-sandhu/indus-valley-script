# Two 200-object ledger selections

The original pilot has **200 carriers, 180 corpus-linked and 20 catalogue-only**, but its alphabetical 74-slot fill drew only from Eastern Headwaters, Gujarat/Kutch and Harappa. Its percentages cannot represent the corpus. The preserved first selection covers 34 export site labels; the new hash-ordered selection covers **39**, including **10 Kalibangan carriers**. Both corrected registers are Exploratory. [Coverage comparison](revision-2026-10-07-v4/coverage-comparison.json), `original`, `hash_ordered`; [report](REPORT.md).

The corrected original selection has **26 confirmed museum joins**, **34 candidate links**, **62 attributed calendar intervals** and **130 dimension-bearing carriers**, a gain of **three** over its 127-carrier corpus baseline. The hash-ordered selection has 25 confirmed museum joins, 15 candidate links, 57 intervals and 130 dimension-bearing carriers. Both have zero dating-sample links. Their queues contain 156 questions on 85 carriers and 138 questions on 81 carriers. [Original summary](revision-2026-10-07-v4/corrected-original/summary.json), [hash-ordered summary](revision-2026-10-07-v4/hash-ordered/summary.json), `joins`, `review_questions`, `review_objects`; each directory's `completeness.json` gives field denominators.

Read the [dated amendment](AMENDMENT-2026-10-07-review-response.md) and appended [protocol](PROTOCOL.md), then the [new selection](revision-2026-10-07-v4/selection.json). The first selection and every earlier endpoint remain unchanged. The revised files are named `ledger-without-transcription-payloads-or-images.json`, in the two selection directories under `revision-2026-10-07-v4/`. They contain attributed metadata, identifiers, pointers and missingness reasons. Lipi record-level metadata needs a reuse basis before public release. Full registers and every new replay copy stay in local `data/`.

[Schema version 2](revision-2026-10-07-v4/schema-v2.json), [builder](revision_builder.py) and [validator](validate_v2.py) implement the corrections. The sequence guard is a heuristic with numeric-metadata exclusions. The [Helsinki interface](HELSINKI-INTERFACE.md) and [importer](import_helsinki1979_v2.py) accept occurrence IDs, suffixed text numbers and reviewed new surfaces. No real Helsinki transcription entered either ledger.

## Rerun from the repository root

Python and `jsonschema` are required; no download or installation is needed. Every output directory must be new. The first command below writes substantive owned outputs; the replay writes only to raw. Change suffixes after using these names.

```powershell
$taskTmp = 'data/raw/2026-10-07-object-ledger/tmp'
New-Item -ItemType Directory -Path $taskTmp -Force | Out-Null
$env:TMP = (Resolve-Path $taskTmp).Path
$env:TEMP = $env:TMP
$env:MPLCONFIGDIR = $env:TMP
$env:PYTHONDONTWRITEBYTECODE = '1'

python experiments/2026-10-07-object-ledger/revise_pilot.py --output-dir experiments/2026-10-07-object-ledger/reviewer-revision-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-registers-v1
python experiments/2026-10-07-object-ledger/check_revision.py --run-dir experiments/2026-10-07-object-ledger/revision-2026-10-07-v4 --output-dir experiments/2026-10-07-object-ledger/reviewer-verification-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-verification-v1
python experiments/2026-10-07-object-ledger/revise_pilot.py --output-dir data/raw/2026-10-07-object-ledger/reviewer-replay-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-replay-registers-v1 --canonical-selection-path experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/selection.json
python experiments/2026-10-07-object-ledger/summarize_revision.py --run-dir experiments/2026-10-07-object-ledger/revision-2026-10-07-v4 --replay-dir data/raw/2026-10-07-object-ledger/reviewer-replay-v1 --output-dir experiments/2026-10-07-object-ledger/reviewer-comparison-v1
python experiments/2026-10-07-object-ledger/validate_v2.py --ledger experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/hash-ordered/ledger-without-transcription-payloads-or-images.json --scan-dir experiments/2026-10-07-object-ledger/revision-2026-10-07-v4
python tools/review_prose.py --path experiments/2026-10-07-object-ledger --no-write
```

For the original pipeline, `replay_original.py` verifies the preserved protocol prefix, supplies its hash in memory and permits output only under raw. These corrected `analyze.py` and `check_pilot.py` lines have no `--lothal-assertions` argument:

```powershell
python experiments/2026-10-07-object-ledger/replay_original.py select_pilot.py --output-dir data/raw/2026-10-07-object-ledger/reviewer-old-selection-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-old-exclusions-v1
python experiments/2026-10-07-object-ledger/replay_original.py build.py --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --lothal-assertions experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json --output-dir data/raw/2026-10-07-object-ledger/reviewer-old-ledger-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-old-register-v1
python experiments/2026-10-07-object-ledger/replay_original.py analyze.py --ledger-dir data/raw/2026-10-07-object-ledger/reviewer-old-ledger-v1 --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --output-dir data/raw/2026-10-07-object-ledger/reviewer-old-analysis-v1
python experiments/2026-10-07-object-ledger/replay_original.py check_pilot.py --ledger-dir data/raw/2026-10-07-object-ledger/reviewer-old-ledger-v1 --analysis-dir data/raw/2026-10-07-object-ledger/reviewer-old-analysis-v1 --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --output-dir data/raw/2026-10-07-object-ledger/reviewer-old-checks-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-old-fixtures-v1
```

## Required local inputs

A fresh checkout lacks the following data. [local-inputs.json](review-response-2026-10-07-v3/local-inputs.json) gives exact paths and hashes for all twenty reused inputs and the supplements. [common.py](common.py), `PATHS`, is the adapter map.

- `data/normalized/lipi_observed_faces.jsonl` and `mayig_faces.jsonl`.
- `data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/{focused-records,paired-comparisons}.json`.
- `data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/{confirmed-object-joins,candidate-object-joins,absent-catalogue-identifiers}.json`.
- `data/six-hour/lothal/table-coding/reviewed-pass.csv` and `data/six-hour/lothal/independent-review/independent-first-pass.csv`.
- `data/raw/2026-10-07-object-ledger/review-response-2026-10-07/source-observations.json`, fourteen located correction observations. The parent scans are `research/literature/sources/joshi_parpola_1987_cisi1.pdf` and `data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/gadd1932.pdf`.
- Original replay also requires `data/raw/2026-10-07-object-ledger/review-response-2026-10-07/original-root/PROTOCOL.md`.

The interface check additionally reads Package M's tracked `integration/2026-10-07-v1/ledger-import.jsonl` in place. Other tracked source frames and period tables are listed in the input manifest. Compare decompressed raw registers rather than gzip headers. [FILES-REVIEW-RESPONSE-2026-10-07.json](FILES-REVIEW-RESPONSE-2026-10-07.json) lists every created or changed path.
