---
id: "F-0031"
title: "Literal-copy reference calibration"
status_class: "synthetic"
area: "methods"
date: "2026-10-02"
registry_ids: ["NULL-08"]
evidence: ["experiments/2026-10-02-six-hour/null-calibration/main/results.json#/aggregate/physical_copies~1block_columns/rejections/0.05/rate", "experiments/2026-10-02-six-hour/null-calibration/main/results.json#/aggregate/physical_copies~1record_columns/rejections/0.05/rate"]
population: "1,000 generated literal-copy populations under a known law"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

At nominal 5%, matched object references rejected 5.4% of literal-copy populations, against 15.9% for record-wise references.

# Evidence

- [experiments/2026-10-02-six-hour/null-calibration/main/results.json](../../experiments/2026-10-02-six-hour/null-calibration/main/results.json), JSON field `/aggregate/physical_copies~1block_columns/rejections/0.05/rate`.
- [experiments/2026-10-02-six-hour/null-calibration/main/results.json](../../experiments/2026-10-02-six-hour/null-calibration/main/results.json), JSON field `/aggregate/physical_copies~1record_columns/rejections/0.05/rate`.

# Scope

The same nested prediction statistic is calibrated under an invented literal-copy process. The comparison changes the reference unit while retaining observations. It tests implementation under that law and supplies no archaeological estimate of copying.
