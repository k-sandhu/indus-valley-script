# Town axes: bearings, horizons and layout dates of Harappan towns

This package builds the project's first settlement table and uses it to test study 4 of the [direction note of 20 October](../../knowledge/directions/parpola-forward-2026-10-20.md), the claim that Harappan towns were laid out on the setting point of a star. Read the [report](REPORT.md) for the results and the [retrospective](RETROSPECTIVE.md) for how the work went. The table answers the data card [Q-1032](../../knowledge/questions/Q-1032-town-axis-table.md); the tested claim is [C-0015](../../knowledge/conjectures/C-0015-towns-laid-out-on-star-settings.md) and the reading it led to is [C-0016](../../knowledge/conjectures/C-0016-plains-cities-on-true-north.md). The registry entry is [TOWN-AXES-2026-10-21](../../knowledge/registry/attempts/TOWN-AXES-2026-10-21.json).

## Files

| What | Where |
|---|---|
| Briefs given to the agents, with hashes | [MEASUREMENT-BRIEF.md](MEASUREMENT-BRIEF.md), [DATING-BRIEF.md](DATING-BRIEF.md), [towns-v1.json](towns-v1.json), `briefs.sha256` |
| Frozen protocol and amendment | [PROTOCOL.md](PROTOCOL.md) with `PROTOCOL.sha256`; [AMENDMENT-1.md](AMENDMENT-1.md) with `AMENDMENT-1.sha256`; [FREEZE.json](FREEZE.json) |
| Measurements, one file per town and measurer | `measure-img-A/`, `measure-img-B/`, `measure-plan-B/` (each with METHOD.md, sources.json, towns/ and code/); `measure-plan-A/towns/` (incomplete: no main systems declared, no METHOD.md, and an empty `specs/kanmer_kharakwal_fig5.json` left when the agent was stopped) |
| Dating records | `dating-v1/` (METHOD.md, sources.json with 199 sources, towns/, code/) |
| Settlement-axis table | [table-v1/settlement-axes.json](table-v1/settlement-axes.json), [CSV](table-v1/settlement-axes.csv) |
| Layout dates under the frozen rule | [dates-v1/dates.json](dates-v1/dates.json) |
| Coordinates and horizon profiles | [horizon-v1/](horizon-v1/) |
| Star data and validation gate | [stars-v1.json](stars-v1.json), [validation-v1/validation.json](validation-v1/validation.json) |
| Synthetic controls | [synthetic-v1/](synthetic-v1/) |
| Stage 1 and stage 2 | [discovery-v1/choice.json](discovery-v1/choice.json) with its hash, [confirmation-v1/results.json](confirmation-v1/results.json) |
| Secondary analysis of Amendment 1 | [exploratory-v1/](exploratory-v1/) |
| Sensitivity checks and planning power | [sensitivity-v1/](sensitivity-v1/), [planning-v1/power-true-north.json](planning-v1/power-true-north.json) |
| Figure | [figures-v1/deviation-vs-date.svg](figures-v1/deviation-vs-date.svg) |
| Records for DATA.md and the manifest | [DATA-RECORD.md](DATA-RECORD.md), [manifest-additions.json](manifest-additions.json) |
| Bench harness check | [bench-selftest.json](bench-selftest.json) |

Imagery mosaics, rendered plans, downloaded publications, the IntCal20 curve and the raw SIMBAD response are local-only under `data/raw/2026-10-21-town-axes/`. DEM tiles were read into memory and not stored; their URLs and hashes are in the horizon output.

## Reproduction

Run from this directory. The astronomy, horizon, combination and scoring steps need Python 3.13 with the packages in [requirements.txt](requirements.txt) (pyerfa for the long-term precession, rasterio for the DEM, ppigrf for magnetic declination); `dates.py` and `coordinates.py` need only the standard library and NumPy. Every script refuses to overwrite an existing output, so write to new paths.

```bash
python validate.py --out validation-new/validation.json
python synth_controls.py --dir synthetic-new
python dates.py --intcal ../../data/raw/2026-10-21-town-axes/coordinator/intcal20.14c --out dates-new/dates.json
python coordinates.py --out horizon-new/coordinates.json
python horizon.py --towns horizon-new/coordinates.json --out horizon-new/horizons.json
python combine.py --dates dates-v1/dates.json --horizons horizon-v1/horizons.json --out table-new/settlement-axes.json
python score.py stage1 --table table-v1/settlement-axes.json --horizons horizon-v1/horizons.json --out discovery-new/choice.json
python score.py stage2 --table table-v1/settlement-axes.json --horizons horizon-v1/horizons.json --choice discovery-new/choice.json --out confirmation-new/results.json
python exploratory.py --table table-v1/settlement-axes.json --out exploratory-new/table.json
python sensitivity.py --table table-v1/settlement-axes.json --horizons horizon-v1/horizons.json --out sensitivity-new/primary.json
python planning_power.py --table exploratory-v1/table.json --horizons horizon-v1/horizons.json --out planning-new/power.json
python figure.py --table exploratory-v1/table.json --out figures-new/deviation-vs-date.svg
```

The permutation tests and bootstraps use the fixed seed 20261021, so a rerun on the same inputs reproduces the numbers. The horizon run makes 403 tile downloads (3.1 GB, held in memory; some tiles are fetched again after the cache is cleared) and takes about twenty minutes.
