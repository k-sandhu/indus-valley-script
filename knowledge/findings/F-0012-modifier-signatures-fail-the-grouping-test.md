---
id: "F-0012"
title: "Grouping signs by their added marks does not improve prediction"
status_class: "failed"
area: "structure"
date: "2026-10-12"
registry_ids: ["SIGN-FAMILIES-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/modifier_signature/p_value", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/modifier_signature/passes"]
population: "1,859 distinct clean texts, 8,535 signs, held out by dependence component"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Grouping signs by modifier signature, the added marks (such as inner marks, doubling or hatching) a sign carries on any base shape, did no better than random groupings of the same sizes (p = 0.11).

# Evidence

- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/modifier_signature/p_value`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/modifier_signature/passes`.

# Scope

The test predicts codes in Wells's sign list on held-out texts. The failure concerns this coding scheme and population.
