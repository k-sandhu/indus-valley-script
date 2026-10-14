---
id: "F-0032"
title: "Shuffling an object's faces separately inflates false positives"
status_class: "synthetic"
area: "methods"
date: "2026-10-02"
registry_ids: ["NULL-05"]
evidence: ["experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json#/aggregate/noisy_faces~1face_vectors/rejections/0.05/rate", "experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json#/aggregate/noisy_faces~1record_columns/rejections/0.05/rate"]
population: "1,000 generated populations with two imperfect faces per object"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

In 1,000 simulated corpora of objects with two error-prone copies (faces) of one text, shuffling each object's faces together rejected the null hypothesis, true by construction, in 5% of corpora at the nominal 5% level, and shuffling records separately in 11%.

# Evidence

- [experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json](../../experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json), JSON field `/aggregate/noisy_faces~1face_vectors/rejections/0.05/rate`.
- [experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json](../../experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json), JSON field `/aggregate/noisy_faces~1record_columns/rejections/0.05/rate`.

# Scope

Face errors follow a stated process, independent between faces. Both references, whole face pairs (face vectors) and per-record shuffling, use the same saved statistic. The calibration holds for that known process.
