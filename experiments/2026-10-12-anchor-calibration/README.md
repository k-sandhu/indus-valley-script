# Calibrating the project's semantic sign assignments

Read the [report](REPORT.md). The [protocol](PROTOCOL.md) was frozen before any permutation, bound or transfer outcome ([hash and time](PROTOCOL-FREEZE.json)); the [post-outcome diagnostic](roles/diagnostics-post-outcome.json) and [Amendment 1](AMENDMENT-1.md), written after an independent review, are labelled as such. The package tests three frozen assignments made by other contributors and changes none of them: the anchor-expansion family map of 12 October, the leading positional codes of the 11 October adversarial review, and the lexical seed map of the 9 October Bonta extension search.

## Reproduce

The scripts read the tested packages and the local corpora from the repository that contains them, or from the main checkout when run from a git worktree without those files (set `IVS_INPUT_ROOT` to override). Every stage refuses to overwrite an existing output, so rerun in a copy of this directory. Python needs NumPy, SciPy and Matplotlib.

```bash
python -X utf8 roles.py --workers 6
python -X utf8 positional.py
python -X utf8 verify_lexical.py
python -X utf8 lexical.py nulls --workers 14
python -X utf8 lexical.py anneal --workers 4 --steps 10000
python -X utf8 lexical.py summary
python -X utf8 diagnostics.py
python -X utf8 amendment.py
python -X utf8 verify.py
python -X utf8 make_figures.py
```

`roles/summary.json` and `verification.json` were produced by the run versions kept in `history/roles-v1.py` and `history/verify-v1.py`. The current `roles.py` contains the Amendment 1 correction to the family-count annealer, which changes only that bound, and the current `verify.py` writes `verification-v2.json`.

Null draws, per-string arrays and anything containing inscription strings or dictionary witnesses are written to `data/raw/2026-10-12-anchor-calibration/`, which Git ignores. Fitted and permuted code-to-family maps and seed-value rearrangements are project-generated and kept here.
