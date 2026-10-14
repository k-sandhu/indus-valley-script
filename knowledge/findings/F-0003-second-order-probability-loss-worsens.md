---
id: "F-0003"
title: "The two-sign model gives the correct sign less probability"
status_class: "verified-computation"
area: "structure"
date: "2026-10-02"
registry_ids: ["MARKOV-03"]
evidence: ["experiments/2026-10-02-six-hour/markov-order2/main/results.json#/models/Markov1/bucket_cross_entropy_bits", "experiments/2026-10-02-six-hour/markov-order2/main/results.json#/models/Markov2/bucket_cross_entropy_bits"]
population: "8,009 artificial known-slot masks in 1,596 distinct strings"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

On the 8,009 hidden-sign tests of F-0002, the second-order model (two signs of context) gave the correct sign less probability: the loss rose from 5.1194 bits per hidden sign for first order to 5.2472 for second order.

# Evidence

- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/models/Markov1/bucket_cross_entropy_bits`.
- [experiments/2026-10-02-six-hour/markov-order2/main/results.json](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json), JSON field `/models/Markov2/bucket_cross_entropy_bits`.

# Scope

Loss is the negative log probability of the correct sign, with signs unseen in training pooled in one unknown bucket. It measures assigned probability; F-0002 scores only whether the correct sign ranks first. It is conditional on the recorded tests and fitted models.
