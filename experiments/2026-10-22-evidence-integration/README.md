# Reproduce the held-source integration

The final local output is `data/raw/2026-10-22-evidence-integration/run-v2/`. Read [REPORT.md](REPORT.md) for findings and [INTERFACE.md](INTERFACE.md) before consuming the review fields. The unchanged core schema version is 2.0. The `register_release` label names this review batch; the run directory and manifest hashes distinguish its builds. `run-v1` is preserved and superseded because its compact face-review pointers were wrong.

Run from the repository root with Python 3.13 and the existing `jsonschema` dependency. The detailed source packages must be present locally. Choose new output directories; the builder refuses to replace an existing run.

```text
python -X utf8 experiments/2026-10-22-evidence-integration/integrate.py --out data/raw/2026-10-22-evidence-integration/replay --summary experiments/2026-10-22-evidence-integration/replay --faces data/raw/2026-10-22-face-adjudication/face-reviews.jsonl --adjudications data/raw/2026-10-22-evidence-integration/face-adjudications.jsonl --candidates data/raw/2026-10-22-candidate-identity-exposure/run-v3/candidate-reviews.jsonl --events data/raw/2026-10-22-candidate-identity-exposure/run-v3/exposure-events.jsonl --senses data/raw/2026-10-22-lexical-source-review/run-v1/sense-review.jsonl --compounds data/raw/2026-10-22-lexical-source-review/run-v1/compound-review.jsonl
python -X utf8 -m unittest discover -s experiments/2026-10-22-evidence-integration -p test_integrate.py -v
```

The builder also reads this package's local first-pass visual record, supplemental review and supplemental adjudications. Their hashes and the two readers' sealed observations are checked before integration. It verifies the forty compound sample identifiers against the lexical freeze, retains its three diagnostics separately, and preserves all 358 candidate reviews. The output manifest hashes every detailed output. No confirmation statistic or substantive reading evaluation is run.

`integrate-v1.py` preserves the exact code of the superseded first build. The [retrospective](RETROSPECTIVE.md) records the failure, regression check and repair. Detailed outputs and source images remain local-only; this package adds no acquisition, publication or automation.
