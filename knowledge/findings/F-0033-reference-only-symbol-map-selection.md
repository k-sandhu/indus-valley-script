---
id: "F-0033"
title: "Reference-only symbol-map selection"
status_class: "synthetic"
area: "methods"
date: "2026-10-02"
registry_ids: ["CRYPTO-08"]
evidence: ["experiments/2026-10-02-six-hour/reference-selector/main/results.json#/rows"]
population: "384 generated mapping conditions in 48 fresh systems"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

The reference-only selector recovered 309 of 384 symbol maps, against 283 for fixed graph mapping and 168 for fixed slot mapping.

# Evidence

- [experiments/2026-10-02-six-hour/reference-selector/main/results.json](../../experiments/2026-10-02-six-hour/reference-selector/main/results.json), JSON field `/rows`.

# Scope

The generated systems supply a known reference whose held-out score chooses the mapping objective. The source-family diagnostic is separate. Recovery measures the hidden generated bijection and depends on the supplied reference process.
