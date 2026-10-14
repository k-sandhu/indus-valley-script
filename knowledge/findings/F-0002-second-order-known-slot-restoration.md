---
id: "F-0002"
title: "Two-sign context restores hidden signs better than one-sign context"
status_class: "verified-computation"
area: "structure"
date: "2026-10-02"
registry_ids: ["MARKOV-03"]
evidence: ["experiments/2026-10-02-six-hour/markov-order2/main/results.json#/models/Markov2/top1", "experiments/2026-10-02-six-hour/markov-order2/main/results.json#/models/Markov1/top1", "experiments/2026-10-02-six-hour/markov-order2/main/results.json#/correspondence/verified_queries_per_model"]
population: "8,009 artificial known-slot masks in 1,596 distinct strings"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

In 8,009 tests each hiding one sign of an intact text, a second-order model (each sign depends on the two before it) ranked the correct sign first in 37.27% of cases, against 34.59% for a first-order model (one sign before).

# Evidence

- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/models/Markov2/top1`.
- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/models/Markov1/top1`.
- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/correspondence/verified_queries_per_model`.

# Scope

Each test (a known-slot mask) tells the model where the gap is and that one sign is missing. Copies of one object and repeated texts stayed in the same fold, and tuning used training folds only. Restoring signs lost to real damage needs further observations.
