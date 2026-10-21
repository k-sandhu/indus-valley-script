# Harappa sealing and vessel settings

The [report](REPORT.md) traces 47 objects to explicit marking operations and recovers primary drawings and individual excavation keys for H-1734 and H-1745. The goblet stamps were applied before firing; their published fills record later deposition. The [protocol](PROTOCOL.md), [observations](source-observations.json), [complete disposition](run-v1/target-dispositions.csv) and [retrospective](RETROSPECTIVE.md) preserve the source chain and unresolved objects.

Run from the repository root with Python 3.13, choosing unused output paths:

```text
python experiments/2026-10-20-archaeological-setting/build.py --out experiments/2026-10-20-archaeological-setting/replay-NEW --local-out data/raw/2026-10-20-archaeological-setting/replay-NEW
python experiments/2026-10-20-archaeological-setting/verify.py --out experiments/2026-10-20-archaeological-setting/check-NEW.json
```

Required local inputs are the pinned normalized Lipi export, the earlier ARCH-01 target ledger, the 1997 and 2010 source PDFs and the acquired author-hosted witnesses in this package's raw directory. [Provenance](run-v1/provenance.json) records their exact hashes. `acquire.py` makes fresh HTTPS acquisitions and refuses its existing manifest. The two image acquisition attempts have separate manifests.

The [shared bench output](shots-synthetic-v1.json) verifies only the generated loader exercise. The small sealing class prevented the planned real-data context comparison. No sign meaning or sound was scored. [Integration proposal](INTEGRATION-PROPOSAL.md) lists the source and coverage changes for maintainers.

[Checks](CHECKS.md), [source and coverage manifest](source-coverage-manifest.json), [search record](search-log.json) and [authorship correction](AUTHORSHIP.md) complete the package.
