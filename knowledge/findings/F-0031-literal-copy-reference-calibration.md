---
id: "F-0031"
title: "Copied records inflate false positives unless objects are shuffled"
status_class: "synthetic"
area: "methods"
date: "2026-10-02"
registry_ids: ["NULL-08"]
evidence: ["experiments/2026-10-02-six-hour/null-calibration/main/results.json#/aggregate/physical_copies~1block_columns/rejections/0.05/rate", "experiments/2026-10-02-six-hour/null-calibration/main/results.json#/aggregate/physical_copies~1record_columns/rejections/0.05/rate"]
population: "1,000 generated literal-copy populations under a known law"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

In 1,000 simulated corpora where every object appears as two identical records and sign order carries no information, shuffling whole objects rejected the null hypothesis, true by construction, in 5.4% of corpora at the nominal 5% level, and shuffling records in 15.9%.

# Evidence

- [experiments/2026-10-02-six-hour/null-calibration/main/results.json](../../experiments/2026-10-02-six-hour/null-calibration/main/results.json), JSON field `/aggregate/physical_copies~1block_columns/rejections/0.05/rate`.
- [experiments/2026-10-02-six-hour/null-calibration/main/results.json](../../experiments/2026-10-02-six-hour/null-calibration/main/results.json), JSON field `/aggregate/physical_copies~1record_columns/rejections/0.05/rate`.

# Scope

Both shuffling schemes (references) use the held-out gain from knowing the previous sign, refitted for every corpus. The copying process is invented, so this checks the implementation and estimates no archaeological copying.
