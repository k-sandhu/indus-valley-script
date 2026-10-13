---
id: "F-0004"
title: "Loss selection returns first order"
status_class: "exploratory"
area: "structure"
date: "2026-10-02"
registry_ids: ["MARKOV-04"]
evidence: ["experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json#/folds", "experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json#/models/Markov2/top1"]
population: "8,009 artificial known-slot masks in 1,596 distinct strings"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

All five folds selected backoff-only when second-order smoothing was chosen by inner probability loss. The outcome reproduced first-order top-one recovery of 34.5861%.

# Evidence

- [experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json), JSON field `/folds`.
- [experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/loss-selected/main/results.json), JSON field `/models/Markov2/top1`.

# Scope

This comparison was specified after the earlier second-order endpoint and reuses its queries. The candidate family includes pure first-order backoff. The result concerns that family and loss criterion.
