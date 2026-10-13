---
id: "F-0010"
title: "Graphic base families improve prediction"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["SIGN-FAMILIES-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/B_coder1/gain_bits", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/grouping_tests/B_coder1/p_value"]
population: "1,859 distinct clean texts, 8,535 signs, held out by dependence component"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Coder 1’s base families improved prediction by 0.0219 bits per sign beyond the ungrouped model, with p = 0.005 against size-matched random groupings.

# Evidence

- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/B_coder1/gain_bits`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/grouping_tests/B_coder1/p_value`.

# Scope

The endpoint predicts original Wells codes using a family backoff feature. Both coders used ordered glyph sheets and were instances of one model. A later contiguous-cut comparison found that Wells ordering carries much of the gain; it remains a separate exploratory check.
