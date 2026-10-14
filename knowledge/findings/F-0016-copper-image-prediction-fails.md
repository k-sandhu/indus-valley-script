---
id: "F-0016"
title: "Copper tablet texts do not predict their image"
status_class: "failed"
area: "tablets"
date: "2026-10-12"
registry_ids: ["IMAGE-TEXT-TABLETS-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/copper/2c/accuracy", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/copper/2c/majority_rate", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/copper/2c/text_types"]
population: "26 text types in the copper tablet cohort"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Predicting each copper tablet text's image class from the other texts was right in 19.2% of cases, below the 26.9% for always guessing the commonest class.

# Evidence

- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/copper/2c/accuracy`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/copper/2c/majority_rate`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/copper/2c/text_types`.

# Scope

Each distinct text receives the image class of the same-genre text sharing most sign pairs with it; classes and counts follow the corrected third run (v3). Whether copies of a text keep one image is measured separately. The result applies to this genre.
