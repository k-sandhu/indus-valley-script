# Plan registration: true-north bearings of plan arrows at Harappan towns

This package registers excavators' published plans of Harappan towns to satellite imagery, measures the true bearing of each plan's north arrow, and converts the wall directions that the [town-axes package](../2026-10-21-town-axes/REPORT.md) measured relative to those arrows into true-north deviations. It serves study 4 of the [direction note of 20 October](../../knowledge/directions/parpola-forward-2026-10-20.md), whose kill condition needs true-north values at eight dated towns. Read the [report](REPORT.md) for the results and the [retrospective](RETROSPECTIVE.md) for how the work went. The registry entry is [PLAN-REGISTRATION-2026-10-21](../../knowledge/registry/attempts/PLAN-REGISTRATION-2026-10-21.json).

## Files

| What | Where |
|---|---|
| Frozen protocol and its hash | [PROTOCOL.md](PROTOCOL.md), `PROTOCOL.sha256` |
| Briefs for the registrars and the search agent | [REGISTRATION-BRIEF.md](REGISTRATION-BRIEF.md), [SEARCH-BRIEF.md](SEARCH-BRIEF.md) |
| Plans given to the registrars | [plans-v1.json](plans-v1.json), written by `code/make_plans.py` |
| Hashes before any control point (protocol, briefs, plans, code, self-test) | [FREEZE.json](FREEZE.json) |
| Synthetic self-test of the fit and error model | [selftest-v1/selftest.json](selftest-v1/selftest.json) |
| Control points, one file per plan and registrar | `control-R1/`, `control-R2/`, `control-S/` |
| Search agent's measurements of Shikarpur and the Rakhigarhi search record | `measure-S/` (towns/, sources.json, line fits, code/) |
| Hashes of the control and town files before the run | [CONTROL-FREEZE.json](CONTROL-FREEZE.json) |
| Georeferencing of the 16 imagery mosaics the control points refer to | [imagery-v1/mosaics.json](imagery-v1/mosaics.json) |
| Registration results: per-plan fits, arrow bearings, converted systems, town values, validation | [registration-v1/results.json](registration-v1/results.json), [towns.csv](registration-v1/towns.csv) |
| Post-outcome diagnostics: magnetic-arrow check, Dholavira systems, registrar agreement, planning power | [diagnostics-v1/diagnostics.json](diagnostics-v1/diagnostics.json) |
| Records for DATA.md and the manifest | [DATA-RECORD.md](DATA-RECORD.md), [manifest-additions.json](manifest-additions.json) |
| Code | `code/regfit.py` (fit and error model), `code/cptools.py` (registrars' tools), `code/register.py` (the frozen run), `code/selftest.py`, `code/diagnostics.py` |

Imagery mosaics and tiles, rendered auxiliary plans, crops, overlays and the search agent's downloads are local-only under `data/raw/2026-10-21-plan-registration/`, one folder per agent; the plan renders and publications come from `data/raw/2026-10-21-town-axes/plan-B/` and `research/literature/sources/`.

## Reproduction

Run from the repository root with Python 3.13 and NumPy, Pillow and requests (OpenCV for overlays, PyMuPDF for page renders). The diagnostics' planning-power step imports the town-axes astronomy, which needs pyerfa and SciPy (`experiments/2026-10-21-town-axes/requirements.txt`). Every script refuses to overwrite an existing output.

```bash
python experiments/2026-10-21-plan-registration/code/selftest.py --out experiments/2026-10-21-plan-registration/selftest-new/selftest.json
python experiments/2026-10-21-plan-registration/code/register.py --registrars experiments/2026-10-21-plan-registration/control-R1 experiments/2026-10-21-plan-registration/control-R2 experiments/2026-10-21-plan-registration/control-S --extra-towns experiments/2026-10-21-plan-registration/measure-S/towns --out experiments/2026-10-21-plan-registration/registration-new/results.json
python experiments/2026-10-21-plan-registration/code/diagnostics.py --results experiments/2026-10-21-plan-registration/registration-v1/results.json --out experiments/2026-10-21-plan-registration/diagnostics-new/diagnostics.json
```

The registration reads the georeferencing JSON of each mosaic named in the control files, which is local-only beside the imagery; the same records, with service, Wayback release, zoom, tile range, origin and SHA-256, are tracked in `imagery-v1/mosaics.json`, from which the mosaics can be rebuilt with `code/cptools.py mosaic`. The self-test and the power simulation use the fixed seed 20261021.
