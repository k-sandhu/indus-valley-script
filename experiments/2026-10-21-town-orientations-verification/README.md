# Town orientations: blind verification of the town-axes study

Status class: frozen evaluation (comparison rules frozen before outcomes) with verified computation (astronomy and scoring reproduced). Verification of [experiments/2026-10-21-town-axes/](../2026-10-21-town-axes/): review with discrepancies.

Contributors: coordinating session and measurer B by Claude Opus 5.5 (`claude-opus-5-5`) in the Claude Code desktop app; tools, imagery, astronomy, dating evidence and measurer A by the Codex CLI with `gpt-6.1-sol`. Dates: 20–21 October 2026.

We repeated the town-axes study's measurements, dating and astronomy blind, with open imagery and independent code, and applied its frozen rules to our numbers. Its frozen outcome (undecided, credence 0.10, Pleiades version failed) and its astronomy and scoring are reproduced; its bearings at Lothal and two of its dates are not, and open 10 m imagery cannot check its discovery towns. The findings are in [REPORT.md](REPORT.md).

## Reading order

1. [REPORT.md](REPORT.md): results, verdict, boldest reading and the deciding test.
2. [PROTOCOL.md](PROTOCOL.md) and [MEASUREMENT-RULES.md](MEASUREMENT-RULES.md), frozen at 03:28 UTC (`PROTOCOL.sha256`); [READ-LOG.json](READ-LOG.json) for what we read of the other package and when; [BLIND-FREEZE.sha256](BLIND-FREEZE.sha256) for the hashes of every blind output before its report was opened.
3. [RETROSPECTIVE.md](RETROSPECTIVE.md), [RETROSPECTIVE-CODEX.md](RETROSPECTIVE-CODEX.md) and [DATA-UPDATE.md](DATA-UPDATE.md).

## Contents

| Path | What it holds |
|---|---|
| `tools/`, `infra-v1/` | Measurement tools and guide; site coordinates, imagery manifest, plan library, selftest, runway validation |
| `astronomy/`, `analysis/`, `astro-v1/` | Independent astronomy and horizons; scoring of the frozen rules, comparison and IntCal20 scripts; validation and prediction tables |
| `dating-v1/`, `dates-v1/` | Dating evidence (Codex run); strict and liberal layout dates frozen at 05:38 UTC (`DATES.sha256`). `JUDGEMENT.md` says the strict table dates eleven towns; it dates seventeen parts in ten towns |
| `measure-A/`, `measure-B/` | The two blind measurers' town files, picks, logs and sources |
| `coordinator/` | Date building, town combination, part assignment, plan pairing, comparisons |
| `table-v1/`, `agreement-v1/` | Town deviations under the frozen rule; agreement of our measurers |
| `comparison-v3/` | Comparison with the town-axes package and the frozen rules on our numbers (`comparison-v1/` and `comparison-v2/` are superseded, see the retrospective) |
| `CODEX-PROMPT-*.md`, `MEASURE-B-BRIEF-*.md`, `launch-codex-*.sh` | Every delegated assignment; hashes of the measurer prompts in `MEASURER-PROMPTS.sha256` |
| `shots-synthetic-v2.json` | `python -m bench shots --synthetic`, documenting the freeze workflow (v1 failed on a OneDrive rename) |
| `notes/` | How the package became a verification |

## Reproducing

Raw inputs are local under `data/raw/2026-10-21-town-orientations-verification/` and are listed with hashes in the manifests. From the repository root, with the package environment (`data/raw/2026-10-21-town-orientations-verification/venv-infra/Scripts/python.exe -I`, rebuilt from `infra-v1/environment.txt` if absent): `coordinator/build_dates.py` rebuilds the date tables, `coordinator/combine_towns.py --parts coordinator/part-assignment-v1.json --out <new dir>` the town table and measurer agreement, `coordinator/plan_agreement.py` the plan agreement, and `coordinator/compare_town_axes.py` and `coordinator/compare_dates.py` the comparison (edit the output directory first; every script refuses to overwrite). `analysis/score_frozen.py --selftest` and `tools/selftest.py` run the synthetic checks.
