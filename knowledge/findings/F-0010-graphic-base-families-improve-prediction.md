---
id: "F-0010"
title: "Grouping sign variants by base shape improves prediction"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["SIGN-FAMILIES-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/B_coder1/gain_bits", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/B_coder1/p_value"]
population: "1,859 distinct clean texts, 8,535 signs, held out by dependence component"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Grouping sign codes into families with a shared base shape, as drawn up by coder 1 of two, improved held-out prediction by 0.0219 bits per sign over the ungrouped model, more than random groupings of the same sizes (p = 0.005).

# Evidence

- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/B_coder1/gain_bits`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/B_coder1/p_value`.

# Scope

The model predicts codes in Wells's sign list and falls back on the family for rare codes. Both coders were instances of one AI model working from sheets in Wells code order. A later exploratory check found that cuts of the Wells number line, which already groups similar shapes, carry much of the gain.
