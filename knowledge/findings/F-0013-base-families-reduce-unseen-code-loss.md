---
id: "F-0013"
title: "Base-shape families improve prediction of signs unseen in training"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["SIGN-FAMILIES-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/B_coder1/by_training_frequency/seen0/tokens", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/B_coder1/by_training_frequency/seen0/baseline_bits", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/B_coder1/by_training_frequency/seen0/class_bits"]
population: "267 held-out signs with no training occurrence of their Wells code"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

For held-out signs whose code never occurs in training, falling back on the base-shape family lowered loss from 14.60 to 14.19 bits per sign.

# Evidence

- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/B_coder1/by_training_frequency/seen0/tokens`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/B_coder1/by_training_frequency/seen0/baseline_bits`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/B_coder1/by_training_frequency/seen0/class_bits`.

# Scope

These are held-out signs whose exact Wells code is absent from the training fold. The comparison is the ungrouped Kneser–Ney bigram baseline. The published Parpola and Mahadevan groupings are scored separately in the same output.
