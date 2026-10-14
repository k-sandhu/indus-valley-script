---
id: "F-0028"
title: "Planned test finds no site concentration of identical seal texts"
status_class: "frozen-evaluation"
area: "seals"
date: "2026-10-12"
registry_ids: ["SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12"]
evidence: ["experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json#/S1_all/text_weighted/observed", "experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json#/S1_all/text_weighted/null_mean", "experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json#/S1_all/text_weighted/p_one_sided", "experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json#/S1_all/text_weighted/ratio_to_null_mean"]
population: "65 recurring texts among the 1,430 eligible seals"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

For texts on two or more seals, the share of seal pairs from the same site averaged 0.473, against 0.448 with site labels shuffled (p = 0.31; ratio to chance 1.06).

# Evidence

- [experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json](../../experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json), JSON field `/S1_all/text_weighted/observed`.
- [experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json](../../experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json), JSON field `/S1_all/text_weighted/null_mean`.
- [experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json](../../experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json), JSON field `/S1_all/text_weighted/p_one_sided`.
- [experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json](../../experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json), JSON field `/S1_all/text_weighted/ratio_to_null_mean`.

# Scope

The statistic, fixed before the outcome was seen, weights each recurring text equally and shuffles sites among all eligible seals. A later null that holds text length fixed and a site breakdown give different results and remain exploratory. This card records the original primary test.
