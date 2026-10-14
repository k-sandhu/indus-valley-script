---
id: "F-0004"
title: "Choosing by probability loss returns the one-sign model"
status_class: "exploratory"
area: "structure"
date: "2026-10-02"
registry_ids: ["MARKOV-04"]
evidence: ["experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json#/folds", "experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json#/models/Markov2/top1"]
population: "8,009 artificial known-slot masks in 1,596 distinct strings"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

When the smoothing of the second-order (two-sign) restoration model was chosen by probability loss on inner validation folds, all five folds chose the backoff-only setting, which is the first-order model, so top-one accuracy stayed at the first-order 34.5861%.

# Evidence

- [experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json), JSON field `/folds`.
- [experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json), JSON field `/models/Markov2/top1`.

# Scope

We specified this comparison after the earlier second-order result and reused its tests. The candidate settings include pure first-order backoff. The result concerns these settings and this loss criterion.
