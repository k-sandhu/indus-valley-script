---
id: "F-0032"
title: "Imperfect-face reference calibration"
status_class: "synthetic"
area: "methods"
date: "2026-10-02"
registry_ids: ["NULL-05"]
evidence: ["experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json#/aggregate/noisy_faces~1face_vectors/rejections/0.05/rate", "experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json#/aggregate/noisy_faces~1record_columns/rejections/0.05/rate"]
population: "1,000 generated populations with two imperfect faces per object"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

At nominal 5%, matched face-vector references rejected 5% of populations, against 11% for record-wise references.

# Evidence

- [experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json](../../experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json), JSON field `/aggregate/noisy_faces~1face_vectors/rejections/0.05/rate`.
- [experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json](../../experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json), JSON field `/aggregate/noisy_faces~1record_columns/rejections/0.05/rate`.

# Scope

The generated observation law uses the specified paired-error mechanism. Whole vectors and individual-record columns are competing references for the saved statistic. The calibration is conditional on that known mechanism.
