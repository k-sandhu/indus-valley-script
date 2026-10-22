# BIRTH-STAR-NAMES-2026-10-21

Study 3 of the [Parpola direction note](../../knowledge/directions/parpola-forward-2026-10-20.md), run to frozen predictions on 21 October 2026 by Claude Opus 5.5 (`claude-opus-5-5`) in the Claude Code desktop app, for k-sandhu. Status: frozen prediction, unscored. Start with the [report](REPORT.md); the claim is card [C-0013](../../knowledge/conjectures/C-0013-fish-runs-are-birth-star-names.md).

## Files

| Path | Content |
|---|---|
| [PROTOCOL.md](PROTOCOL.md), [MARKING-RULE.md](MARKING-RULE.md), [PROTOCOL.sha256.txt](PROTOCOL.sha256.txt) | Design and asterism rule, hashed before any data were used |
| [SOURCES.md](SOURCES.md), [DATA-UPDATE.md](DATA-UPDATE.md), [manifest-additions.json](manifest-additions.json) | Lüders source provenance and rights; proposed DATA.md and manifest entries |
| [extract_luders.py](extract_luders.py), [make_donor_rows.py](make_donor_rows.py), [mark_a.py](mark_a.py), [resolve.py](resolve.py), [calibrate.py](calibrate.py) | Donor extraction, marker A, resolution and calibration statistics |
| [calibration-v1/](calibration-v1/) | Calibration output and the tracked donor table with both markings |
| [birthstar.py](birthstar.py), [explore.py](explore.py), [discovery_checks.py](discovery_checks.py) | Shared definitions and the discovery exploration |
| [discovery-v1/](discovery-v1/), [discovery-v2/](discovery-v2/) | Discovery statistics, fish-run inventories and the later checks |
| [power.py](power.py), [build_reference.py](build_reference.py), [power-v1/](power-v1/), [power-v2/](power-v2/) | Power simulations; v1 is the superseded upward-bootstrap design |
| [PREDICTIONS.json](PREDICTIONS.json), [PREDICTIONS.sha256](PREDICTIONS.sha256), [FREEZE-NOTES.md](FREEZE-NOTES.md), [freeze-v1.json](freeze-v1.json) | Frozen predictions, hashes, the record of post-result choices and the bench freeze |
| [score_fresh.py](score_fresh.py), [frozen-reference.json](frozen-reference.json), [SCORING.md](SCORING.md) | Frozen scorer, its reference data and instructions for fresh material |
| [round.json](round.json), [round.access.jsonl](round.access.jsonl), [split-summary.json](split-summary.json) | Split manifest and read log; no confirmation read |
| [PREDICTIONS-draft-v0.json](PREDICTIONS-draft-v0.json) | Draft registered before discovery, replaced at freeze |
| [verify.py](verify.py), [verification-v1.json](verification-v1.json), [shots-synthetic.json](shots-synthetic.json), [synthetic-fresh-check/](synthetic-fresh-check/) | Checks |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Approach, repairs and outcome |

Local only, in `data/raw/2026-10-21-birth-star-names/`: the downloaded scans (`sources/`), the aligned clauses, donor rows, both markings with marker A's earlier versions and the resolved marking (`luders-v1/`), and synthetic test inputs.

## Commands

Run from the repository root with Python 3.13 and NumPy. Output paths must be new; the scripts refuse to overwrite.

```text
python -I experiments/2026-10-21-birth-star-names/extract_luders.py --scan-a data/raw/2026-10-21-birth-star-names/sources/luders1912_dli49008_djvu.txt --scan-b data/raw/2026-10-21-birth-star-names/sources/luders1912_asi14283_djvu.txt --out data/raw/2026-10-21-birth-star-names/luders-v1/aligned-clauses.csv --summary data/raw/2026-10-21-birth-star-names/luders-v1/extract-summary.json
python -I experiments/2026-10-21-birth-star-names/make_donor_rows.py --aligned data/raw/2026-10-21-birth-star-names/luders-v1/aligned-clauses.csv --out data/raw/2026-10-21-birth-star-names/luders-v1/donor-rows.csv
python -I experiments/2026-10-21-birth-star-names/mark_a.py --rows data/raw/2026-10-21-birth-star-names/luders-v1/donor-rows.csv --out data/raw/2026-10-21-birth-star-names/luders-v1/marking-A.csv
python -I -X utf8 experiments/2026-10-21-birth-star-names/resolve.py --rows data/raw/2026-10-21-birth-star-names/luders-v1/donor-rows.csv --marking-a data/raw/2026-10-21-birth-star-names/luders-v1/marking-A.csv --marking-b data/raw/2026-10-21-birth-star-names/luders-v1/marking-B.csv --out data/raw/2026-10-21-birth-star-names/luders-v1/marking-resolved.csv
python -X utf8 experiments/2026-10-21-birth-star-names/calibrate.py --rows data/raw/2026-10-21-birth-star-names/luders-v1/donor-rows.csv --marking-a data/raw/2026-10-21-birth-star-names/luders-v1/marking-A.csv --marking-b data/raw/2026-10-21-birth-star-names/luders-v1/marking-B.csv --resolved data/raw/2026-10-21-birth-star-names/luders-v1/marking-resolved.csv --out experiments/2026-10-21-birth-star-names/calibration-v1/calibration.json
python -X utf8 -m bench shots --synthetic --directory experiments/2026-10-21-birth-star-names/synthetic-shots --out experiments/2026-10-21-birth-star-names/shots-synthetic.json
python -X utf8 -m bench shots --action create --input data/normalized/lipi_observed_faces.jsonl --seed 2026-10-21-birth-star-names --split experiments/2026-10-21-birth-star-names/round.json --out experiments/2026-10-21-birth-star-names/split-summary.json
python -X utf8 -m bench shots --action register --split experiments/2026-10-21-birth-star-names/round.json --shot birthstar --predictions experiments/2026-10-21-birth-star-names/PREDICTIONS.json
python -X utf8 experiments/2026-10-21-birth-star-names/explore.py --out discovery-v1 --draws 9999
python -X utf8 experiments/2026-10-21-birth-star-names/discovery_checks.py --out discovery-v2
python -X utf8 experiments/2026-10-21-birth-star-names/build_reference.py --brahmi-variant broad --out experiments/2026-10-21-birth-star-names/power-v2/reference-broad.json
python -X utf8 experiments/2026-10-21-birth-star-names/power.py --reference experiments/2026-10-21-birth-star-names/power-v2/reference-broad.json --out experiments/2026-10-21-birth-star-names/power-v2/power-broad.json --trials 400
python -X utf8 experiments/2026-10-21-birth-star-names/build_reference.py --brahmi-variant broad --out experiments/2026-10-21-birth-star-names/frozen-reference.json
python -X utf8 -m bench shots --action freeze --split experiments/2026-10-21-birth-star-names/round.json --shot birthstar --artifact experiments/2026-10-21-birth-star-names/score_fresh.py --artifact experiments/2026-10-21-birth-star-names/birthstar.py --artifact experiments/2026-10-21-birth-star-names/frozen-reference.json --artifact experiments/2026-10-21-birth-star-names/PROTOCOL.md --artifact experiments/2026-10-21-birth-star-names/MARKING-RULE.md --artifact experiments/2026-10-21-birth-star-names/FREEZE-NOTES.md --artifact experiments/2026-10-21-birth-star-names/discovery-v1/inventories.json --artifact experiments/2026-10-21-birth-star-names/calibration-v1/calibration.json --artifact experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv --out experiments/2026-10-21-birth-star-names/freeze-v1.json
python -X utf8 experiments/2026-10-21-birth-star-names/verify.py
```

`donor-rows.csv` comes from the aligned clauses through [make_donor_rows.py](make_donor_rows.py), which keeps rows with a named donor in either scan and numbers them D0001–D0819 (the script reproduces the file byte for byte); marker B was a separate agent given only the marking rule and that file. The split and freeze commands write to `bench/spent.json` and can be run only once per seed; reproduce them in a copy with a copied ledger. Rerunning the calibration or discovery scripts into the frozen paths is refused by design.
