# A 200-record Indus object ledger

The pilot contains **200 carrier records at 34 sites**, including **180 corpus-linked records and 20 catalogue-only Lothal sealings**. It connects 256 Lipi faces and three Mayig transcriptions to source-qualified identifiers, archaeological assertions and asset rights. The annotations are Exploratory. Schema and reconstruction checks have status Verified computation. [Summary](analysis-2026-10-07-v3/summary.json), fields `objects`, `site_count`, `corpus_matched_objects`, `catalogue_only_objects` and `transcriptions`.

On the matched 180 carriers, the ledger adds 26 museum accessions, 22 excavation unit/item pairs, 62 attributed calendar intervals and dimensions for two additional carriers. It adds no object-associated dating-sample links. There are 26 confirmed museum joins and 34 candidate search-bucket links; no candidate fields enter the accepted view. The review queue has 134 questions covering 82 records. [Completeness](analysis-2026-10-07-v3/completeness.csv), [joins](analysis-2026-10-07-v3/join-report.json), [review queue](analysis-2026-10-07-v3/review-queue.json).

The build uses local sources. It preserves the 22 Harappa tablet caption joins, applies 25 site-review qualifications as overlays, and gives every requested empty field a reason. All sequence payloads stay in the local raw register. Image records contain pointers; 48 point to a catalogue section whose individual photograph page remains unverified. [Report](REPORT.md), [public metadata tables](run-2026-10-07-v4/ledger-public.json), [source register](sources.json).

## Files and reading order

Read [PROTOCOL.md](PROTOCOL.md) and the ordered [selection](selection-2026-10-07-v1/selection.json) before interpreting coverage. [schema.json](schema.json) defines the public tables; [schema.py](schema.py) generates that definition. [validate.py](validate.py) checks schema, provenance ownership, references, missingness, units, BCE intervals and sequence exclusion. [common.py](common.py), [select_pilot.py](select_pilot.py), [build.py](build.py), [analyze.py](analyze.py) and [check_pilot.py](check_pilot.py) implement selection, enrichment, descriptive comparisons and source recounts.

[HELSINKI-INTERFACE.md](HELSINKI-INTERFACE.md), [interface-schema.json](interface-schema.json) and [import_helsinki1979.py](import_helsinki1979.py) prepare a reviewed 1979 transcription layer. No actual Package M payload or historical text-number concordance was imported. [RETROSPECTIVE.md](RETROSPECTIVE.md) records failures and repairs; [registry-entry.json](registry-entry.json) is the proposed shared-registry entry. [FILES.json](FILES.json) lists every created path and hash.

The current ledger is `run-2026-10-07-v4`. Its [source amendment](AMENDMENT-2026-10-07-lothal-source.md) carries L174?s one-versus-two impression counts and a located photograph pointer. V3 completed eight field-alias entries and 34 candidate accession entries; [the amendment](AMENDMENT-2026-10-07-alias-table.md) records this Exploratory repair after v2. V1 failed 68 edition-provenance checks and is preserved with its [validation result](validation-2026-10-07-v1.json) and [repair record](AMENDMENT-2026-10-07-provenance.md). The frozen selection and protocol were not revised after population.

## Rerun from the repository root

Python and `jsonschema` are required; this run used the versions in [environment.json](environment.json). All named output directories must be new. Change the reviewer suffix if these names have already been used. No network access or new installation is needed.

```powershell
$taskTmp = 'data/raw/2026-10-07-object-ledger/tmp'
New-Item -ItemType Directory -Path $taskTmp -Force | Out-Null
$env:TMP = (Resolve-Path $taskTmp).Path
$env:TEMP = $env:TMP
$env:MPLCONFIGDIR = $env:TMP
$env:PYTHONDONTWRITEBYTECODE = '1'

python experiments/2026-10-07-object-ledger/select_pilot.py --output-dir experiments/2026-10-07-object-ledger/reviewer-selection-2026-10-07-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-selection-2026-10-07-v1
python experiments/2026-10-07-object-ledger/build.py --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --lothal-assertions experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json --output-dir experiments/2026-10-07-object-ledger/reviewer-ledger-2026-10-07-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-ledger-2026-10-07-v1
python experiments/2026-10-07-object-ledger/analyze.py --ledger-dir experiments/2026-10-07-object-ledger/reviewer-ledger-2026-10-07-v1 --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --lothal-assertions experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json --output-dir experiments/2026-10-07-object-ledger/reviewer-analysis-2026-10-07-v3
python experiments/2026-10-07-object-ledger/check_pilot.py --ledger-dir experiments/2026-10-07-object-ledger/reviewer-ledger-2026-10-07-v1 --analysis-dir experiments/2026-10-07-object-ledger/reviewer-analysis-2026-10-07-v3 --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --lothal-assertions experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json --output-dir experiments/2026-10-07-object-ledger/reviewer-checks-2026-10-07-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-checks-2026-10-07-v1
python experiments/2026-10-07-object-ledger/validate.py --ledger experiments/2026-10-07-object-ledger/reviewer-ledger-2026-10-07-v1/ledger-public.json --scan-dir experiments/2026-10-07-object-ledger --output experiments/2026-10-07-object-ledger/reviewer-validation-2026-10-07-v1.json
python tools/review_prose.py --path experiments/2026-10-07-object-ledger --no-write
```

The builder uses the original selection path so assertion locators reproduce exactly. Compare the replayed selection with the frozen selection. Compare `ledger-public.json`, `museum-comparisons.json`, `source-lookups.json` and the six analysis files named in [replay-comparison-2026-10-07-v3.json](replay-comparison-2026-10-07-v3.json). Input hashes and code snapshots are in each build manifest. Gzip headers and code manifests can change between runs; compare the decompressed full register when checking payload equality.

The local full register is `data/raw/2026-10-07-object-ledger/run-2026-10-07-v4/ledger-full.json.gz`. It contains the public tables plus all selected source transcription rows, including restricted sequence data. Do not move it into the tracked layer. The tracked and raw directories are the only write destinations used by this package.
