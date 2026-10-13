---
id: "F-0003"
title: "Second-order probability loss worsens"
status_class: "verified-computation"
area: "structure"
date: "2026-10-02"
registry_ids: ["MARKOV-03"]
evidence: ["experiments/2026-10-02-six-hour/markov-order2/main/results.json#/models/Markov1/bucket_cross_entropy_bits", "experiments/2026-10-02-six-hour/markov-order2/main/results.json#/models/Markov2/bucket_cross_entropy_bits"]
population: "8,009 artificial known-slot masks in 1,596 distinct strings"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Bucket probability loss rose from 5.1194 bits per slot for first order to 5.2472 for second order.

# Evidence

- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/models/Markov1/bucket_cross_entropy_bits`.
- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/models/Markov2/bucket_cross_entropy_bits`.

# Scope

The models use the same held-out masks and the saved alphabet with an unknown-target bucket. This endpoint measures assigned probability, whereas the preceding card measures the highest-ranked graphic. It is conditional on the recorded masks and fitted models.
