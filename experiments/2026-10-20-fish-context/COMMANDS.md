# Reproduction record

Run from the repository root with Python 3.13 and the local sources identified in [manifest-additions.json](manifest-additions.json), [sources-v1.json](sources-v1.json) and [register coverage](register-v1/coverage.json). The package's [environment record](environment-v1.json) gives the installed versions. The study date is 20 October in `America/Toronto`; the freeze and read occurred on 21 October UTC.

The commands below record the scoring sequence and its parameters. They are reproduction instructions assembled from the scripts and saved outputs, rather than a transcript of every shell call. Run them in a disposable copy with empty study output directories and a copy of the spending ledger. Several helpers deliberately write fixed versioned paths, and the shared writers refuse existing outputs. Preserve this package and its freeze. Reproduction does not create fresh evidence.

## Guards and discovery

```powershell
python -X utf8 -m bench shots --synthetic --directory experiments/2026-10-20-fish-context/synthetic-shots --out experiments/2026-10-20-fish-context/shots-synthetic.json
python -X utf8 -m bench meaning-map --synthetic --permutations 199 --power-trials 8 --power-effects 0,.25,.5,1 --out experiments/2026-10-20-fish-context/meaning-synthetic.json
python -X utf8 -m bench shots --action create --input data/normalized/lipi_observed_faces.jsonl --seed 2026-10-20-fish-context --split experiments/2026-10-20-fish-context/round.json --out experiments/2026-10-20-fish-context/split-summary.json
python -X utf8 -m bench shots --action register --split experiments/2026-10-20-fish-context/round.json --shot fish --predictions experiments/2026-10-20-fish-context/PREDICTIONS.json
python -X utf8 experiments/2026-10-20-fish-context/acquire_sources.py --run sources-v1
python -X utf8 experiments/2026-10-20-fish-context/study.py discovery --out discovery-v2
python -X utf8 experiments/2026-10-20-fish-context/check_methods.py
python -X utf8 -m bench meaning-map --objects data/raw/2026-10-20-fish-context/discovery-v2/discovery-objects.jsonl --map experiments/2026-10-20-fish-context/discovery-v2/map.json --predictions experiments/2026-10-20-fish-context/discovery-v2/bench-predictions.json --discovery data/raw/2026-10-20-fish-context/discovery-v2/discovery-objects.jsonl --permutations 199 --seed 20261013 --alpha 0.0166666666666667 --power-trials 12 --power-effects 0,.25,.5,1 --out experiments/2026-10-20-fish-context/discovery-v2/bench-diagnostics.json
python -X utf8 experiments/2026-10-20-fish-context/discovery_diagnostics.py
```

Discovery v1 and its source snapshots remain under `discovery-v1/`. That run omitted seal subtypes and supplies no result used for confirmation. The repaired scorer is `study.py`; [Amendment 1](AMENDMENT-1.md) records the repair before freezing. The original v1 model cannot be regenerated with the repaired scorer. The current PREDICTIONS file incorporates that pre-freeze amendment.

## Freeze and confirmation

```powershell
python -X utf8 -m bench shots --action freeze --split experiments/2026-10-20-fish-context/round.json --shot fish --artifact experiments/2026-10-20-fish-context/study.py --artifact experiments/2026-10-20-fish-context/PROTOCOL.md --artifact experiments/2026-10-20-fish-context/AMENDMENT-1.md --artifact experiments/2026-10-20-fish-context/FREEZE-NOTES.md --artifact experiments/2026-10-20-fish-context/discovery-v2/model.json --artifact experiments/2026-10-20-fish-context/discovery-v2/map.json --artifact experiments/2026-10-20-fish-context/discovery-v2/bench-predictions.json --artifact experiments/2026-10-20-fish-context/discovery-v2/power-audit.json --artifact experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv --artifact experiments/2026-10-12-structure-first/step1-signs/second-coder/components_coder2.tsv --artifact bench/meaning_map.py --artifact bench/common.py --out experiments/2026-10-20-fish-context/freeze-v1.json
python -X utf8 experiments/2026-10-20-fish-context/study.py confirmation --out confirmation-v1
python -X utf8 -m bench meaning-map --objects data/raw/2026-10-20-fish-context/confirmation-v1/confirmation-objects.jsonl --map experiments/2026-10-20-fish-context/discovery-v2/map.json --predictions experiments/2026-10-20-fish-context/discovery-v2/bench-predictions.json --discovery data/raw/2026-10-20-fish-context/discovery-v2/discovery-objects.jsonl --permutations 9999 --seed 20261020 --alpha 0.0166666666666667 --out experiments/2026-10-20-fish-context/confirmation-v1/meaning-map.json
```

The scorer calls `bench.shots.load_half` and records the sole confirmation access. The later meaning-map command uses that saved half. Its score cannot restore freshness. The split and freeze records carry the exact code and input hashes, and the access log carries UTC timestamps.

## Source register and post-outcome checks

```powershell
python -X utf8 experiments/2026-10-20-fish-context/study.py register --out register-v1
python -X utf8 experiments/2026-10-20-fish-context/adversarial.py
python -X utf8 experiments/2026-10-20-fish-context/make_source_packet.py
python -X utf8 experiments/2026-10-20-fish-context/enrich_register.py
python -X utf8 experiments/2026-10-20-fish-context/register_coverage_v3.py
python -X utf8 experiments/2026-10-20-fish-context/verify_results.py
```

The source packet contains local image sheets. [Source observations](source-observations-v1.json) also include full-page checks of H-902, H-912 and M-478 against the primary CISI scans. Those observations require visual inspection; rerunning a crop generator does not verify them. The source locator, page number and decision for each inspection are preserved.

The [verification output](verification-v1.json) is already complete. For a separate replay, change only the verification destination in a copied helper and record the copied helper's hash. Do not rerun a fixed-path helper over a preserved output. The [retrospective](RETROSPECTIVE.md) records the scope and repairs; repository checks are recorded separately in `completion-v1.json`.
