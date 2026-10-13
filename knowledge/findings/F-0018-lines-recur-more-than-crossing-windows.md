---
id: "F-0018"
title: "Lines recur more than crossing windows"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["LINE-BREAKS-SEGMENTATION-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/conservative_best_order/faces_line_higher", "experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/conservative_best_order/faces_straddle_higher", "experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/conservative_best_order/ties", "experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/conservative_best_order/sign_test_two_sided_p", "experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json#/faces_used"]
population: "69 usable faces with catalogue line divisions"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Under the conservative line order, 23 faces had higher line recurrence, 4 had higher crossing-window recurrence and 42 tied; p = 0.0003.

# Evidence

- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/conservative_best_order/faces_line_higher`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/conservative_best_order/faces_straddle_higher`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/conservative_best_order/ties`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/conservative_best_order/sign_test_two_sided_p`.
- [experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json](../../experiments/2026-10-12-structure-first/step3-segmentation/run-linebreaks-2026-10-12-v3/summary.json), JSON field `/faces_used`.

# Scope

Lines are sought in clean single-line texts from another object. Crossing windows have matching lengths, and the better crossing order per face supplies the conservative comparator. The outcome uses the eligible catalogue-divided faces, mostly square seals.
