---
id: "F-0014"
title: "Bas-relief tablet texts predict their image better than the majority guess"
status_class: "frozen-evaluation"
area: "tablets"
date: "2026-10-12"
registry_ids: ["IMAGE-TEXT-TABLETS-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/bas_relief/2c/accuracy", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/bas_relief/2c/majority_rate", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/bas_relief/2c/text_types"]
population: "149 text types in the bas relief tablet cohort"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Predicting each bas-relief tablet text's image class from the other texts was right in 24.8% of cases, against 21.5% for always guessing the commonest class.

# Evidence

- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/bas_relief/2c/accuracy`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/bas_relief/2c/majority_rate`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/bas_relief/2c/text_types`.

# Scope

Each distinct text receives the image class of the same-genre text sharing most sign pairs with it; classes and counts follow the corrected third run (v3). Whether copies of a text keep one image is measured separately. The result applies to this genre.
