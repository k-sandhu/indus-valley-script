---
id: "F-0019"
title: "Indus alternation has few stems"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["LINE-BREAKS-SEGMENTATION-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json#/ivs_chosen_alternation/stems", "experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json#/ivs_chosen_alternation/alternating_stems", "experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json#/ivs_chosen_alternation/alternation_rate", "experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json#/comparisons"]
population: "68 stems from Dirichlet-process segments of the distinct clean texts"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Only 2 of 68 segment-derived stems alternated, a rate of 0.029. The rate lay inside all four matched comparison ranges.

# Evidence

- [experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json), JSON field `/ivs_chosen_alternation/stems`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json), JSON field `/ivs_chosen_alternation/alternating_stems`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json), JSON field `/ivs_chosen_alternation/alternation_rate`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json), JSON field `/comparisons`.

# Scope

The selected segmenter was chosen on the readable-corpus rehearsal. Comparison words are subsampled to the Indus unit-length profile. The protocol treats this rate as descriptive because alternation fails to separate known systems at this scale.
