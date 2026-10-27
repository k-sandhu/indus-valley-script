# Validation record

Run from the repository root on 22 October 2026 with Python 3.13.

| Check | Result and saved evidence |
|---|---|
| Independent base-population and interface check | Pass. Source IDs reproduce 4,695 provisional objects, 5,680 faces and every parent relationship. Canonical value statuses and unreviewed exposure states pass. [Result](register-interface-v2.json). |
| Completed-artifact hash comparison | Pass. The object, face and assertion-value exports checked independently match the builder's final output hashes. [Result](register-hash-crosscheck.json). |
| Unit audit with final register | Pass. All 118 divided faces joined; three image-identity review flags propagated. [Result](../2026-10-22-unit-readiness/readiness-register-v2.json). |
| Independent reading-input test rerun | Pass, 21 tests. [Command, code hashes and output](reading-tests-reproduced.json). |
| Knowledge-base check | Pass: 558 items, zero errors, zero warnings and two maintainer notes for generated registry and map updates. [Saved output](knowledge-check-final.json). |
| Prose review | The current report and retrospective were edited after review. Two flags remain in the scope-hashed plan and exact posted claim body; those historical records are preserved. |
| Source-data handling | `git check-ignore` confirms the detailed register and integrated unit queues remain local. New tracked candidates contain code, protocols, hashes, generated fixtures and aggregate results. |

Commands used for the two integration runs:

```text
python -X utf8 experiments/2026-10-22-research-launch/check_register_interface.py --register-dir data/raw/2026-10-22-object-register/run-v2 --out experiments/2026-10-22-research-launch/register-interface-v2.json
python -X utf8 -B experiments/2026-10-22-unit-readiness/audit.py --out experiments/2026-10-22-unit-readiness/readiness-register-v2.json --local-out data/raw/2026-10-22-unit-readiness/run-register-v2 --register-dir data/raw/2026-10-22-object-register/run-v2
python -m unittest discover -s experiments/2026-10-22-reading-eval-readiness/code -p test_*.py -v
python tools/kb.py check
python tools/review_prose.py --path experiments/2026-10-22-research-launch --no-write
```

The whole-repository verifier reports the same 58 link-error diagnostics, representing 48 distinct messages, before and after this work. There are zero new diagnostics and zero errors in the four owned packages or their cards. The [comparison](repository-check-comparison-v2.json) distinguishes total and unique counts; the [final source report](repository-final.json) retains the complete output. We do not treat the global baseline failure as a successful repository-wide verification.

No shared harness code, spending ledger, raw source or earlier frozen result was changed. The three previously untracked files outside the owned packages remain untouched. No commit, push, publication or recurring process was created.
