---
id: "F-0016"
title: "Copper image prediction fails"
status_class: "failed"
area: "tablets"
date: "2026-10-12"
registry_ids: ["IMAGE-TEXT-TABLETS-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/copper/2c/accuracy", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/copper/2c/majority_rate", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/copper/2c/text_types"]
population: "26 text types in the copper tablet cohort"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Held-out image-class prediction reached 19.2% against a 26.9% majority comparator.

# Evidence

- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/copper/2c/accuracy`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/copper/2c/majority_rate`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/copper/2c/text_types`.

# Scope

The classifier predicts an image class from other text types in the same tablet genre. Class normalization and corrected populations follow the v3 endpoint. Recurrent-text purity is a separate measurement; this outcome is confined to the recorded genre.
