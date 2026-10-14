---
id: "F-0024"
title: "Indus stroke counts are more tied to the next sign than Ur III counts"
status_class: "frozen-evaluation"
area: "numerals"
date: "2026-10-12"
registry_ids: ["NUMERAL-BEHAVIOUR-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json#/ivs_clean/mean_distinct_values_per_item", "experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json#/ur3_subsampled_to_ivs/mean_distinct_values_per_item/p2_5", "experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json#/ur3_subsampled_to_ivs/mean_distinct_values_per_item/p97_5"]
population: "Clean Indus stroke tokens with the next sign treated as item; size-matched Ur III counts"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Indus stroke groups took 3.61 different values on average before each sign they precede at least five times; size-matched samples of Ur III accounts gave an interval of 4.53–5.15 values per counted item.

# Evidence

- [experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json), JSON field `/ivs_clean/mean_distinct_values_per_item`.
- [experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json), JSON field `/ur3_subsampled_to_ivs/mean_distinct_values_per_item/p2_5`.
- [experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step4-numerals/run-2026-10-12/summary.json), JSON field `/ur3_subsampled_to_ivs/mean_distinct_values_per_item/p97_5`.

# Scope

The sign after a stroke group is treated as the counted item, and stroke counts are compared with edited Ur III quantities. Direction, units and selection have separate sensitivity analyses. The result measures how fixed number–item combinations are in this representation.
