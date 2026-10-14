---
id: "F-0021"
title: "Branching entropy finds word boundaries in Ur III seal legends"
status_class: "frozen-evaluation"
area: "methods"
date: "2026-10-12"
registry_ids: ["REHEARSAL-SEGMENTATION-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/cohorts/sumerian_seals_all/scores/branching_entropy/boundary_f1", "experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/cohorts/sumerian_seals_all/scores/all_boundaries/boundary_f1", "experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/cohorts/sumerian_seals_all/texts"]
population: "309 distinct Ur III seal legends with complete edited word units"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

On Ur III seal legends with word divisions hidden, branching entropy, which places a boundary where the next sign becomes hard to predict, reached boundary F1 0.692, against 0.557 for a boundary everywhere.

# Evidence

- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/cohorts/sumerian_seals_all/scores/branching_entropy/boundary_f1`.
- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/cohorts/sumerian_seals_all/scores/all_boundaries/boundary_f1`.
- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/cohorts/sumerian_seals_all/texts`.

# Scope

These Sumerian seal inscriptions are the comparison genre closest to Indus seals. Predicted boundaries are scored against the edition's divisions. Transfer to Indus texts needs observed divisions or spacing evidence.
