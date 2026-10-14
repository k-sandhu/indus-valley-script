---
id: "F-0019"
title: "Few Indus segments show alternating final signs"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["LINE-BREAKS-SEGMENTATION-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json#/ivs_chosen_alternation/stems", "experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json#/ivs_chosen_alternation/alternating_stems", "experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json#/ivs_chosen_alternation/alternation_rate", "experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json#/comparisons"]
population: "68 stems from Dirichlet-process segments of the distinct clean texts"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Of 68 stems (segments minus their last sign) from Dirichlet-process segments of the Indus texts, only 2 occur with more than one final sign, a rate of 0.029, inside all four matched comparison ranges.

# Evidence

- [experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json), JSON field `/ivs_chosen_alternation/stems`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json), JSON field `/ivs_chosen_alternation/alternating_stems`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json), JSON field `/ivs_chosen_alternation/alternation_rate`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-alternation-2026-10-12/summary.json), JSON field `/comparisons`.

# Scope

The segmenter, a Bayesian model that favours reused units, was chosen in the rehearsal on readable scripts. Comparison words from four readable corpora are subsampled to the Indus unit lengths. The protocol treats the rate as descriptive, because alternation fails to separate known writing systems at this scale.
