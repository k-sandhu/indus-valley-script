---
id: "F-0021"
title: "Seal-legend segmentation rehearsal"
status_class: "frozen-evaluation"
area: "methods"
date: "2026-10-12"
registry_ids: ["REHEARSAL-SEGMENTATION-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/cohorts/sumerian_seals_all/scores/branching_entropy/boundary_f1", "experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/cohorts/sumerian_seals_all/scores/all_boundaries/boundary_f1", "experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/cohorts/sumerian_seals_all/texts"]
population: "309 distinct Ur III seal legends with complete edited word units"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

On Ur III seal legends, branching entropy reached boundary F1 0.692 against 0.557 for a boundary everywhere.

# Evidence

- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/cohorts/sumerian_seals_all/scores/branching_entropy/boundary_f1`.
- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/cohorts/sumerian_seals_all/scores/all_boundaries/boundary_f1`.
- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/cohorts/sumerian_seals_all/texts`.

# Scope

The input conceals word boundaries and retains the seal-legend genre. The comparison scores predicted boundaries against the edition’s divisions. Transfer to Indus boundaries needs observed divisions or spacing evidence.
