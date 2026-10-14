---
id: "F-0017"
title: "Copper-tablet sign groups do not recur on seals with the same animal"
status_class: "failed"
area: "seals"
date: "2026-10-12"
registry_ids: ["IMAGE-TEXT-TABLETS-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/2d_copper_to_seals/matching_hits", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/2d_copper_to_seals/null_mean", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/2d_copper_to_seals/p_value", "experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json#/2d_copper_to_seals/seal_text_animal_pairs"]
population: "1,209 seal text/animal pairs in classes shared with copper tablets"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Sign groups found with only one image class on copper tablets appeared 3 times on seals showing the matching animal, against 3.01 expected (p = 0.62).

# Evidence

- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/2d_copper_to_seals/matching_hits`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/2d_copper_to_seals/null_mean`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/2d_copper_to_seals/p_value`.
- [experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step2-image-text/run-2026-10-12-v3/summary.json), JSON field `/2d_copper_to_seals/seal_text_animal_pairs`.

# Scope

The chance comparison shuffles animal labels across 1,209 distinct pairings of seal text and animal. The test has more power for fivefold than twofold enrichment, so smaller effects remain unresolved.
