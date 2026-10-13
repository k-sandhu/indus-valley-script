---
id: "F-0024"
title: "Stroke values are tied to following items"
status_class: "frozen-evaluation"
area: "numerals"
date: "2026-10-12"
registry_ids: ["NUMERAL-BEHAVIOUR-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json#/ivs_clean/mean_distinct_values_per_item", "experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json#/ur3_subsampled_to_ivs/mean_distinct_values_per_item/p2_5", "experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json#/ur3_subsampled_to_ivs/mean_distinct_values_per_item/p97_5"]
population: "Clean Indus stroke tokens with the next sign treated as item; size-matched Ur III counts"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Indus had 3.61 distinct values per qualifying item, against 4.53–5.15 in the size-matched Ur III interval.

# Evidence

- [experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json), JSON field `/ivs_clean/mean_distinct_values_per_item`.
- [experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json), JSON field `/ur3_subsampled_to_ivs/mean_distinct_values_per_item/p2_5`.
- [experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json), JSON field `/ur3_subsampled_to_ivs/mean_distinct_values_per_item/p97_5`.

# Scope

The endpoint treats the following sign as the item and compares observed stroke counts with edited Ur III quantities. Direction, units and selection have separate sensitivities. The result measures fixity of combinations under that representation.
