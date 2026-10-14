---
id: "F-0034"
title: "A class-and-gloss map of 118 signs fails to predict seal site and size"
status_class: "failed"
area: "meaning"
date: "2026-10-13"
registry_ids: ["CONJECTURE-SHOT-B-WORKING-READING-2026-10-12"]
evidence: ["experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json#/primary", "experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json#/components", "experiments/2026-10-12-conjecture-shots/shot-b-reading/verification.json", "experiments/2026-10-12-conjecture-shots/review/shot-b-reliability.json"]
population: "Confirmation-half seals of the 12 October split: 1,086 site units and 846 size units"
authors: ["Claude Opus 5.5 in Claude Code (Shot B agent and coordinator)"]
---

# Finding

We built a map assigning the 118 commonest signs to seven classes (numerals, links, households, name elements, commodities, offices, closing determinatives) without seeing site, size, animal, material or period. On the confirmation half of the seals, read once after the predictions were frozen, the map predicted where seals were found and how large they were no better than rearrangements of its own labels within frequency and position bands. Its score S, the sum of the standardised site and size contrasts, was −0.567, at the 33.0th percentile of 10,000 rearrangements and 0.44 standard deviations below their mean; a pass required the 95th percentile. On the discovery half, used for exploration, the same code with the real withheld fields gives +0.88 standard deviations, also a fail.

# Evidence

- [results.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json), fields `/primary` and `/components`.
- [verification.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/verification.json): independent recomputation, S = −0.525, fail.
- [shot-b-reliability.json](../../experiments/2026-10-12-conjecture-shots/review/shot-b-reliability.json): per-sign site concentration correlates at r = −0.092 between halves.

# Scope

The test detects only large effects: a size effect planted in the discovery data at 1.2 times the face area fails, and 1.5 times passes. It scores class contrasts against object properties, not the grammar of the texts or individual glosses. Report: [Shot B](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/REPORT.md).
