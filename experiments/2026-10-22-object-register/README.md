# Object register from the held sources

The current build records all **4,695 provisional Lipi families and 5,680 exported faces**, with **225,223 source assertions**. It joins the complete CISI basic-data tables, excavation-table records, museum accessions, image pointers, earlier export, Mayig identities and corrected pilot metadata. The [report](REPORT.md), [coverage](run-v2/coverage.json) and [interface](INTERFACE.md) define what each count means. Physical identities remain provisional, and exposure is unreviewed for every object.

Detailed records stay in local `data/raw/2026-10-22-object-register/run-v2/`. `objects.jsonl` and `faces.jsonl` are the compact inputs for the parallel unit and reading-evaluation audits. `register-v2.json` follows the unchanged [pilot schema](schema-v2.json). `assertion-values.jsonl`, `missing-values.jsonl`, `join-queue.jsonl` and `cisi-reader-decisions.jsonl` preserve raw values, source uncertainty and unresolved work. The tracked package contains code and aggregates.

From the repository root, with Python 3.13 and the already installed `jsonschema`:

```text
python experiments/2026-10-22-object-register/build_register.py --out data/raw/2026-10-22-object-register/reviewer-v1 --summary-dir experiments/2026-10-22-object-register/reviewer-v1
python experiments/2026-10-22-object-register/verify_sources.py --run data/raw/2026-10-22-object-register/reviewer-v1 --output experiments/2026-10-22-object-register/reviewer-source-check.json
python experiments/2026-10-22-object-register/selftest.py
```

Use new directory and output names for each run. The builder refuses an existing output directory and restricts detailed output to this package's local data directory. Inputs are listed with hashes in [source-manifest.json](run-v2/source-manifest.json); inherited source titles, acquisition routes and rights are in [SOURCE-LINEAGE.json](SOURCE-LINEAGE.json). The 7 October pilot helper code is reused in place for excavation-string splitting and measurement checks. No installation, download, source contact or statistical confirmation read is part of the build.

The first successful exploratory build is preserved as `run-v1`. The current `run-v2` adds the original CISI reader decisions and withholds uncertain cells from accepted object fields. The exact source candidates remain available in both versions.
