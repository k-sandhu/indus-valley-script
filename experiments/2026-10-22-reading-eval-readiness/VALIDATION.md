# Validation and commands

Python 3.13.5 was used from the repository root. The following commands produced the preserved results. A replay must select new output paths because the scripts preserve existing runs.

```text
python experiments/2026-10-22-reading-eval-readiness/code/audit_inputs.py --run run-v1
python -m bench key-calibration --synthetic --out experiments/2026-10-22-reading-eval-readiness/key-synthetic-v1.json
python -m bench meaning-map --synthetic --power-trials 30 --out experiments/2026-10-22-reading-eval-readiness/meaning-synthetic-v1.json
python -m bench shots --synthetic --directory experiments/2026-10-22-reading-eval-readiness/shot-fixtures-v1 --out experiments/2026-10-22-reading-eval-readiness/shots-synthetic-v1.json
python experiments/2026-10-22-reading-eval-readiness/code/verify.py --out experiments/2026-10-22-reading-eval-readiness/verification-v2.json
python -m unittest discover -s experiments/2026-10-22-reading-eval-readiness/code -p test_*.py -v
python tools/kb.py check
python tools/review_prose.py --path experiments/2026-10-22-reading-eval-readiness --no-write
python tools/verify_knowledge_repo.py --output experiments/2026-10-22-reading-eval-readiness/repository-verification-v1.json
git check-ignore data/raw/2026-10-22-reading-eval-readiness/run-v1/lexical-audit-detail.json
```

The package verifier passed: 21 focused tests, independent replay of all 24 diagnostic word counts, the 162,399-token denominator, pinned source hashes and all three bench smoke tests. The first verification file preserves the earlier 18-test result. The later preflight tests incorporate the coordinating review of required fields, participant identity and malformed input types. `verification-v2.json` records every current Python module's hash.

The knowledge-base check passed with 554 items, zero errors, zero warnings and two maintainer notes for the generated registry and map. The prose scan found no remaining flags after three slash constructions were rewritten. The full repository verifier returned 58 errors, all outside this package and its registry record; its detailed output is preserved. These include existing broken links and its distribution-rule flag for `data/MANIFEST.json`. They were not changed in this contribution.

The local lexical derivative is ignored by Git. No dictionary table, Sangam source text, source page, image or acquired corpus is proposed for tracking. The owned paths are listed in [CHANGED-PATHS.json](CHANGED-PATHS.json).

No real participant manifest was approved by preflight. Its passing fixture is generated data with invented review records, so it tests the checker rather than granting source or cohort readiness. No new real confirmation access occurred.
