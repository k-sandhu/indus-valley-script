---
id: "F-0015"
title: "Incised tablet texts predict their image better than the majority guess"
status_class: "frozen-evaluation"
area: "tablets"
date: "2026-10-12"
registry_ids: ["IMAGE-TEXT-TABLETS-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/incised/2c/accuracy", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/incised/2c/majority_rate", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/incised/2c/text_types"]
population: "54 text types in the incised tablet cohort"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Predicting each incised tablet text's image class from the other texts was right in 57.4% of cases, against 48.1% for always guessing the commonest class.

# Evidence

- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/incised/2c/accuracy`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/incised/2c/majority_rate`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/incised/2c/text_types`.

# Scope

Each distinct text receives the image class of the same-genre text sharing most sign pairs with it; classes and counts follow the corrected third run (v3). Whether copies of a text keep one image is measured separately. The result applies to this genre.
