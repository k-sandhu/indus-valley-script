# Validation

The completed metadata audit passed its eight consistency checks. [verification-v1.json](verification-v1.json) records 32 passing checks of input and queue hashes, unique queue IDs, absence of inscription payload fields, synthetic scorer results and malformed-register rejection. The original script is preserved as [audit-v1.py](audit-v1.py). The later integration amendment consumes the register's identity warnings in each queue row; [verification-v2.json](verification-v2.json) checks the preserved first result and the current consumer.

Commands run from the repository root:

```text
python -X utf8 -B experiments/2026-10-22-unit-readiness/audit.py --out experiments/2026-10-22-unit-readiness/readiness-v1.json --local-out data/raw/2026-10-22-unit-readiness/run-v2
python -X utf8 -B -m bench segmentation --synthetic --out experiments/2026-10-22-unit-readiness/segmentation-synthetic.json
python -X utf8 -B -m bench shots --synthetic --directory experiments/2026-10-22-unit-readiness/shot-fixtures --out experiments/2026-10-22-unit-readiness/shots-synthetic.json
python -X utf8 -B experiments/2026-10-22-unit-readiness/verify.py --out experiments/2026-10-22-unit-readiness/verification-v2.json
python -X utf8 -B tools/review_prose.py --path experiments/2026-10-22-unit-readiness --no-write
python -X utf8 -B tools/kb.py check
python -X utf8 -B tools/verify_knowledge_repo.py --output experiments/2026-10-22-unit-readiness/repository-verification-v3.json
```

The first audit command used the preserved version-1 script before the register amendment. Reproduction now uses `audit-v1.py` and new output paths. The synthetic tasks both pass, and they create only generated confirmation reads. No real shots manifest or shared spending ledger was changed.

The prose check returns no flags. `kb.py check` passes with no errors or warnings; the two generated-file notes are for maintainers. The first whole-repository verification reported 59 broken links, including the then-unwritten `VALIDATION.md` in this package. A second run encountered its own not-yet-written output link. Both now resolve. [repository-verification-v3.json](repository-verification-v3.json) records 58 earlier broken links and none in this contribution.

This is author verification of source joins and saved computations. It does not replace an independent reading of source images or acceptance of a new segmentation result. Record-level queues remain under the ignored `data/raw/` directory. The tracked package contains our code, prose, generated fixtures, source hashes and aggregate counts.
