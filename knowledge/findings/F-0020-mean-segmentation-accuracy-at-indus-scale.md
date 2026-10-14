---
id: "F-0020"
title: "At Indus scale, the best segmenter only slightly beats cutting everywhere"
status_class: "frozen-evaluation"
area: "methods"
date: "2026-10-12"
registry_ids: ["REHEARSAL-SEGMENTATION-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/mean_boundary_f1/dp_unigram", "experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json#/cohorts"]
population: "Four readable cohorts with word boundaries hidden and lengths matched where feasible"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

With word divisions hidden in four readable corpora at Indus scale, the best segmenter (Dirichlet process) reached mean boundary F1 0.531, against 0.485 for a boundary between every pair of signs.

# Evidence

- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/mean_boundary_f1/dp_unigram`.
- [experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json), JSON field `/cohorts`.

# Scope

Boundary F1 combines precision and recall against the editions' word divisions in Ur III seal legends, Sumerian lines, Egyptian sentences and Akkadian letters. The mean weights the four equally and does not estimate Indus accuracy. The acquired Linear B sample was not included.
