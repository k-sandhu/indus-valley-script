# Town-axis register, 24 October 2026

We reconcile three earlier studies into a source-backed register of 34 candidate towns. Start with the [report](REPORT.md) and the [town table](TABLE.md). The [CSV](run-v5/town-axis-table.csv) indexes towns; the [measurement CSV](run-v5/measurements.csv) gives each line and system, its north reference, uncertainty, length, phase and source key. The [JSON table](run-v5/town-axis-table.json) links each town to the detailed records.

The current endpoint is `run-v5/`. It contains [source records](run-v5/sources.jsonl), [dated parts](run-v5/chronology-parts.jsonl), [radiocarbon assertions](run-v5/radiocarbon.jsonl), [horizon references](run-v5/horizons.jsonl), [town-field gaps](run-v5/missing-fields.csv), [measurement-field gaps](run-v5/measurement-field-gaps.csv), [coverage](run-v5/coverage.json) and the [input hashes](run-v5/input-manifest.json). The [audit](audit-v5.json) checks 3,009 record references. [CHECKS.json](CHECKS.json) records final validation and the pre-existing repository errors. The [source checks](source-checks.json) identify the primary pages inspected here.

The [protocol](PROTOCOL.md), [horizon repair](HORIZON-REPAIR.md), [retrospective](RETROSPECTIVE.md) and [data update](DATA-UPDATE.md) describe scope, repairs and remaining work. Run-v1 preserves a duplicate-ID validation failure. Run-v2 repairs the IDs. Run-v3 adds corrected horizons and geodesic checks. Run-v4 labels coordinate quality and records the Lothal discordance explicitly. Run-v5 exports stable acquisition URLs. Complete older source-use exports remain local-only on D:, with hashes in [source-export-preservation.json](source-export-preservation.json). Earlier evidence bytes remain unchanged.

Images, plans, rendered pages and 46 acquired DEM tiles are local-only under `D:/projects/indus_valley_script/data/raw/2026-10-24-q1032-town-axis-register/`. The [storage guide](../../LOCAL_STORAGE.md) explains the checkout links. No star-alignment statistic or conjecture is rescored. The synthetic [bench selftest](bench-selftest.json) checks the shared harness only.

From the repository root, write any reproduction to a new directory:

```text
python experiments/2026-10-24-q1032-town-axis-register/code/build_register.py --out experiments/2026-10-24-q1032-town-axis-register/reproduction-NEW
python experiments/2026-10-24-q1032-town-axis-register/code/verify_register.py --run experiments/2026-10-24-q1032-town-axis-register/reproduction-NEW --out experiments/2026-10-24-q1032-town-axis-register/audit-NEW.json
```

The horizon code uses the preserved Python environment at `data/raw/2026-10-21-town-orientations-verification/venv-infra/`, with rasterio 1.5.2 and NumPy 2.5.4. Its wrapper refuses an existing horizon endpoint. The [geodesic check](geodesic-check.json) used pyproj 3.8.0. Model disclosure: GPT-6, Codex desktop harness; verification tier submitted.
