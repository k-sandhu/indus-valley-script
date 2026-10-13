---
id: "F-0012"
title: "Modifier signatures fail the grouping test"
status_class: "failed"
area: "structure"
date: "2026-10-12"
registry_ids: ["SIGN-FAMILIES-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/modifier_signature/p_value", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/modifier_signature/passes"]
population: "1,859 distinct clean texts, 8,535 signs, held out by dependence component"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Grouping by modifier signature failed the random-grouping test, with p = 0.11.

# Evidence

- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/modifier_signature/p_value`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/modifier_signature/passes`.

# Scope

The endpoint groups added elements across different graphic bases and predicts Wells codes. The comparator randomizes groups of the same sizes. Failure concerns the declared signature scheme and population.
