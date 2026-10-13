---
id: "F-0035"
title: "Legends closing in 001, 595, 679 or 820 sit on larger seals in a held-out half"
status_class: "frozen-evaluation"
area: "seals"
date: "2026-10-13"
registry_ids: ["CONJECTURE-SHOT-A-SEAL-GRADE-2026-10-12"]
evidence: ["experiments/2026-10-12-conjecture-shots/shot-a-rank/confirmation/results.json#/P4", "experiments/2026-10-12-conjecture-shots/shot-a-rank/verification.json", "experiments/2026-10-12-conjecture-shots/review/shot-a-robustness.json#/confirmation/variants"]
population: "620 confirmation-half seals in 582 components with both face dimensions and a complete single-line legend of two or more signs"
authors: ["Claude Opus 5.5 in Claude Code (Shot A agent and coordinator)"]
---

# Finding

On the confirmation half, the 11 seals whose legend ends in sign 001, 595, 679 or 820, a set chosen on the discovery half before the confirmation half was read, average +0.346 in residual log face area against −0.007 for the other 571 seals of the same type, site class and length class (p = 0.021, frozen one-sided permutation test). Measured against the null mean of +0.056, the excess is ×1.35 in face area.

# Evidence

- [results.json](../../experiments/2026-10-12-conjecture-shots/shot-a-rank/confirmation/results.json), field `/P4`.
- [verification.json](../../experiments/2026-10-12-conjecture-shots/shot-a-rank/verification.json): independent recomputation, p = 0.0220.
- [shot-a-robustness.json](../../experiments/2026-10-12-conjecture-shots/review/shot-a-robustness.json), field `/confirmation/variants`: influence analysis.

# Scope

The result depends on three seals ending in 820 (M-6, M-16, M-649): dropping any one gives p between 0.066 and 0.138, and a rank version gives p = 0.087 to 0.093. A Holm correction over the shot's six scored predictions does not keep it. Sizes come from catalogue dimensions, mostly converted from inches. Report: [Shot A](../../experiments/2026-10-12-conjecture-shots/shot-a-rank/REPORT.md).
