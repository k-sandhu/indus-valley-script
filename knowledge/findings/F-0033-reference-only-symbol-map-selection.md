---
id: "F-0033"
title: "Reference-based model choice recovers most simulated symbol maps"
status_class: "synthetic"
area: "methods"
date: "2026-10-02"
registry_ids: ["CRYPTO-08"]
evidence: ["experiments/2026-10-02-six-hour/reference-selector/main/results.json#/rows"]
population: "384 generated mapping conditions in 48 fresh systems"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

In 48 simulated scripts, choosing the mapping method by how well it predicted held-out reference records recovered the hidden one-to-one symbol map in 309 of 384 conditions, against 283 for graph mapping alone and 168 for slot mapping alone.

# Evidence

- [experiments/2026-10-02-six-hour/reference-selector/main/results.json](../../experiments/2026-10-02-six-hour/reference-selector/main/results.json), JSON field `/rows`.

# Scope

Graph mapping matches symbol successions, slot mapping symbol frequencies by position; the selector sees only the reference records and inventory size. A diagnostic run given each system's generator is reported separately. Recovery depends on the supplied reference process.
