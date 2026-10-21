# Recorded commands and run order

All commands ran from the repository root on 20 October 2026, America/Toronto. Some UTC timestamps fall on 21 October. Python 3.13 and the exact NumPy version are in the output provenance. Reproduction uses fresh output paths because the original paths are frozen.

```powershell
python experiments/2026-10-20-script-variation/variation.py source
python experiments/2026-10-20-script-variation/variation.py synthetic
python -m bench shots --synthetic --directory experiments/2026-10-20-script-variation/shot-fixtures-v1 --out experiments/2026-10-20-script-variation/bench-shots-synthetic-v1.json
```

We then copied the bytes of `bench/spent.json` to `spent-private.json` using Python's `shutil.copyfile`, with the original SHA-256 in `ledger-copy.json`.

```powershell
python -m bench shots --action create --seed 2026-10-20-script-variation --split experiments/2026-10-20-script-variation/round.json --ledger experiments/2026-10-20-script-variation/spent-private.json --out experiments/2026-10-20-script-variation/bench-create-v1.json
python -m bench shots --action register --split experiments/2026-10-20-script-variation/round.json --ledger experiments/2026-10-20-script-variation/spent-private.json --shot variant-choice --predictions experiments/2026-10-20-script-variation/PREDICTIONS.json --out experiments/2026-10-20-script-variation/bench-register-v1.json
python -m bench shots --action freeze --split experiments/2026-10-20-script-variation/round.json --ledger experiments/2026-10-20-script-variation/spent-private.json --shot variant-choice --artifact experiments/2026-10-20-script-variation/variation.py --artifact experiments/2026-10-20-script-variation/PROTOCOL.md --artifact data/normalized/mayig_wells_class_crosswalk.json --artifact data/raw/2026-10-20-script-variation/source-v1/objects.jsonl --out experiments/2026-10-20-script-variation/bench-freeze-v1.json
python experiments/2026-10-20-script-variation/variation.py discovery
python experiments/2026-10-20-script-variation/variation.py confirmation
python experiments/2026-10-20-script-variation/audit.py
python experiments/2026-10-20-script-variation/verify.py
python -m bench shots --action inspect --split experiments/2026-10-20-script-variation/round.json --ledger experiments/2026-10-20-script-variation/spent-private.json --out experiments/2026-10-20-script-variation/bench-inspect-v1.json
```

`source` writes `source-v1/`; `synthetic` writes `synthetic-v1/`; discovery writes `discovery-v1.json` and local observations; confirmation writes `run-v1/`; the post-outcome audit writes `audit-v1/`. A reproduction can copy the package code into a new dated owned package and update its path constants and bench arguments. It must preserve the original source and output hashes, use a private ledger and state that this population is already examined. The author-side verifier recomputes probabilities without importing the fitted scorer.

The completion checks and their outputs are listed in `checks-v1/` once run. We do not build the website or generated knowledge indexes.
