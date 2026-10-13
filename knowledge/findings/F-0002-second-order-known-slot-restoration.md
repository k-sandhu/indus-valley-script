---
id: "F-0002"
title: "Second-order known-slot restoration"
status_class: "verified-computation"
area: "structure"
date: "2026-10-02"
registry_ids: ["MARKOV-03"]
evidence: ["experiments/2026-10-02-six-hour/markov-order2/main/results.json#/models/Markov2/top1", "experiments/2026-10-02-six-hour/markov-order2/main/results.json#/models/Markov1/top1", "experiments/2026-10-02-six-hour/markov-order2/main/results.json#/correspondence/verified_queries_per_model"]
population: "8,009 artificial known-slot masks in 1,596 distinct strings"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Second-order context reached 37.27% exact top-one recovery, against 34.59% for first order, on the same 8,009 masks.

# Evidence

- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/models/Markov2/top1`.
- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/models/Markov1/top1`.
- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/correspondence/verified_queries_per_model`.

# Scope

The benchmark hides one known position, holds physical aliases and repeated texts together and tunes on training folds. First order is the matched comparator. A known position and count are supplied; physical damage recovery requires additional observations.
