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

A map assigning the 118 commonest signs to seven classes (numerals, links, households, name elements, commodities, offices, closing determinatives), built without seeing site, size, animal, material or period, did not predict where confirmation-half seals were found or how large they were better than rearrangements of its own labels within frequency and position bands: S = −0.567, 33.0th percentile of 10,000 rearrangements, 0.44 standard deviations below their mean (pass required the 95th percentile). The same code on the discovery half's real withheld fields gives +0.88 standard deviations, also a fail.

# Evidence

- [results.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json), fields `/primary` and `/components`.
- [verification.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/verification.json): independent recomputation, S = −0.525, fail.
- [shot-b-reliability.json](../../experiments/2026-10-12-conjecture-shots/review/shot-b-reliability.json): per-sign site concentration correlates at r = −0.092 between halves.

# Scope

The test detects large effects only: a planted size effect of 1.2 times the face area fails and 1.5 times passes. It scores class contrasts against object properties; it does not test the grammar of the texts or individual glosses. Report: [Shot B](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/REPORT.md).
