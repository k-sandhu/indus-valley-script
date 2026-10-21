# H-912 excavation links

The [report](REPORT.md) traces 8650c to its primary recovery frame, restores the 4–7 foot depth range, preserves layer and identifier conflicts, and joins fourteen objects to Belcher's fish-area plan. [Exact observations](source-observations-v1.json), [dispositions](run-v1/dispositions.csv), [summary](run-v1/summary.json) and [plan joins](run-v1/belcher-plan-joins.json) retain the limits of each association.

Run from the repository root with Python 3.13, choosing fresh paths:

```text
python experiments/2026-10-20-h912-excavation-links/build.py --out experiments/2026-10-20-h912-excavation-links/replay-NEW --local-out data/raw/2026-10-20-h912-excavation-links/replay-NEW
```

[Provenance](run-v1/provenance.json) gives source, image, code, protocol and annotation hashes. All acquired sources and detailed export metadata stay in the local raw directory. [Retrospective](RETROSPECTIVE.md) records the acquisition failures and source corrections. Authors: GPT-6 family; exact model identifier not exposed; Codex collaboration harness.

[Checks](CHECKS.md) and the [source and coverage manifest](source-coverage-manifest.json) record verification and the proposed data additions.
