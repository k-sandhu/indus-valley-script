# Candidate identity and exposure audit

We reviewed all 358 rows selected by the unit-readiness queue against held identity metadata and exposure records. The final output is `run-v3`. It verifies 24 existing links to provisional Lipi families, preserves 306 candidate-only rows and 28 unlinked rows, and attaches page-level access evidence to every row. Confirmation eligibility remains false for all rows.

[REPORT.md](REPORT.md) explains the results. [PROTOCOL.md](PROTOCOL.md) records the plan before outcomes; [REVISION-NOTES.md](REVISION-NOTES.md) and [RETROSPECTIVE.md](RETROSPECTIVE.md) explain the repairs. [INTERFACE.md](INTERFACE.md) describes the exports. Source-derived detail remains local under `data/raw/2026-10-22-candidate-identity-exposure/run-v3/`.

Run from the repository root with Python 3.13:

```text
python -B experiments/2026-10-22-candidate-identity-exposure/test_audit.py
python -B experiments/2026-10-22-candidate-identity-exposure/audit.py --out data/raw/2026-10-22-candidate-identity-exposure/new-run --summary-dir experiments/2026-10-22-candidate-identity-exposure/new-run
```

Both output directories must be new children of this package's owned directories. The final run and replay used `run-v3` and `replay-v3` in these positions. `verify_outputs.py` checked their closure, source links, input hashes and byte equality, writing [source-and-replay-verification.json](source-and-replay-verification.json). That verification command also refuses an existing result file.

The package creates no new reading, sign interpretation or confirmation score. Its next use is to enrich the register with reviewed relations and explicit evidence gaps.
