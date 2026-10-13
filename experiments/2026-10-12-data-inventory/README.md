# Data inventory, 12 October 2026

This package measures what data the project holds and how complete each inscribed object's metadata is, records the sources it does not hold, and writes the project's data page, manifest and fetch tool. Status: inventory with verified computation on hash-checked local inputs; web checks are source reviews.

| Read or reuse | File |
|---|---|
| The data page for contributors and agents | [knowledge/DATA.md](../../knowledge/DATA.md) |
| Machine-readable source list | [data/MANIFEST.json](../../data/MANIFEST.json), built by [build_manifest.py](build_manifest.py) and [not_held.py](not_held.py) |
| Fetch, list and verify tool | [tools/fetch_data.py](../../tools/fetch_data.py) |
| Protocol, written before computing | [PROTOCOL.md](PROTOCOL.md) |
| Coverage code and outputs | [coverage.py](coverage.py), [run-2026-10-12/](run-2026-10-12/) |
| Holdings code and outputs | [holdings.py](holdings.py), [run-2026-10-12/holdings/](run-2026-10-12/holdings/) |
| Web pages consulted | [sources.json](sources.json), built by [make_sources.py](make_sources.py) |
| Question cards | [Q-1001](../../knowledge/questions/Q-1001-cisi-plates-l161-m895.md) to [Q-1030](../../knowledge/questions/Q-1030-object-register-build.md) |
| Approaches, problems and fixes | [RETROSPECTIVE.md](RETROSPECTIVE.md) |
| Proposed registry entry | [registry-entry.json](registry-entry.json) |

## Results

The local corpus has 5,680 faces and 4,695 provisional objects. Object-level coverage of usable values: site 99.4%, CISI number 86.8%, excavation string 89.6%, material 82.5%, any spatial unit 76.3%, any dimension 76.6%, all three dimensions 28.8%, depth 50.6%, chronology label 55.8%, local image 53.4%, museum value 5.8%, calendar date 0% ([summary.json](run-2026-10-12/summary.json)). Seals and Mohenjo-daro are the best described; tags, sealings, pottery and Dholavira the worst ([compact-object-table.csv](run-2026-10-12/compact-object-table.csv)). Faces of one object never disagree on an object field ([conflicts.json](run-2026-10-12/conflicts.json)). The millimetre sizes are conversions from inch records for 5,206 of 5,434 paired values ([cross-source.json](run-2026-10-12/cross-source.json)). The input hashes match the values recorded in `knowledge/provenance/SOURCES.md` ([input-hashes.json](run-2026-10-12/input-hashes.json)).

Local holdings under `data/` and the literature folders total 91,170 files and 13.06 GB, with 365 PDF files (299 distinct by SHA256) and 44,823 image files ([holdings-summary.json](run-2026-10-12/holdings/holdings-summary.json)). Complete scans of CISI 1 and CISI 2 are held, so the plate check for conjecture C-0004 needs no acquisition. The manifest lists 85 sources: 33 held, 9 partly held, 9 project outputs and 34 not held.

The web checks of 12 October (61 entries from a background agent and 3 direct checks, [sources.json](sources.json)) found a public CC BY 4.0 transcription of the Mackay 1938 and Marshall 1931 seal tables; open museum routes with CC0 or CC BY data at the Metropolitan, Cleveland and Penn museums; public scans of Mackay 1938, Rao's Lothal volumes, the 2003 Kalibangan volume, Farmana, Rakhigarhi (Nath) and Surkotada; and no open edition of any CISI volume. ICIT remains closed to anonymous access, the RMRL expanded concordance is announced without a date, and no new inscribed-object corpus for 2024–2026 was found. Both project Hugging Face datasets return HTTP 401 to anonymous requests.

## Reproduce

From the repository root, with new output directories:

```text
python -I experiments/2026-10-12-data-inventory/coverage.py --out experiments/2026-10-12-data-inventory/run-<date>
python -I experiments/2026-10-12-data-inventory/holdings.py --out experiments/2026-10-12-data-inventory/run-<date>/holdings --raw-out data/raw/2026-10-12-data-inventory/holdings-<date>
python -I experiments/2026-10-12-data-inventory/make_sources.py
python -I experiments/2026-10-12-data-inventory/build_manifest.py --check-only
python tools/fetch_data.py --list
python tools/fetch_data.py --fetch lipi --dry-run
```

Coverage needs the local normalized files and the Lipi image index; holdings walks the local data folders and hashes every PDF (a few minutes). Development runs are preserved under `data/raw/2026-10-12-data-inventory/dev-*`. The full file list, PDF hash table, harvested source index and saved web pages stay local under `data/raw/2026-10-12-data-inventory/`.
