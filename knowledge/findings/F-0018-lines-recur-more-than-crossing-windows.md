---
id: "F-0018"
title: "Text lines recur elsewhere more often than stretches crossing the line break"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["LINE-BREAKS-SEGMENTATION-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/conservative_best_order/faces_line_higher", "experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/conservative_best_order/faces_straddle_higher", "experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/conservative_best_order/ties", "experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/conservative_best_order/sign_test_two_sided_p", "experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/faces_used"]
population: "69 usable faces with catalogue line divisions"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

On 69 faces where the catalogue splits the text into lines, lines recurred elsewhere more often than equal-length stretches crossing the break: under the conservative line order, 23 faces favoured lines, 4 favoured crossing stretches and 42 tied (p = 0.0003).

# Evidence

- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/conservative_best_order/faces_line_higher`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/conservative_best_order/faces_straddle_higher`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/conservative_best_order/ties`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/conservative_best_order/sign_test_two_sided_p`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/faces_used`.

# Scope

Recurrence means appearing within a clean single-line text on another object. Crossing stretches (crossing windows) are built under both possible line orders, and the conservative comparison takes, for each face, the order that favours them. The faces are eligible catalogue-divided faces, mostly square seals.
