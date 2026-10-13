---
id: "F-0020"
title: "Mean segmentation accuracy at Indus scale"
status_class: "frozen-evaluation"
area: "methods"
date: "2026-10-12"
registry_ids: ["REHEARSAL-SEGMENTATION-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/mean_boundary_f1/dp_unigram", "experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/cohorts"]
population: "Four readable cohorts with word boundaries hidden and lengths matched where feasible"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

The best mean boundary F1 was 0.531 for the Dirichlet-process segmenter, against 0.485 for a boundary everywhere.

# Evidence

- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/mean_boundary_f1/dp_unigram`.
- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/cohorts`.

# Scope

F1 combines boundary precision and recall against edited word divisions. The mean weights the four cohorts equally; it does not estimate Indus word-boundary accuracy. The recorded cohorts omit the acquired Linear B sample.
