---
id: "F-0022"
title: "Indus texts begin with many different signs and end with few"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["STRUCTURAL-TYPOLOGY-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json#/profiles/ivs_all_clean/edge_asymmetry/asymmetry_initial_minus_final", "experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json#/profiles/ivs_all_clean/edge_asymmetry/shuffle_p2_5", "experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json#/profiles/ivs_all_clean/edge_asymmetry/shuffle_p97_5"]
population: "1,859 distinct clean Indus texts"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Indus texts start with more varied signs than they end with: normalized initial-minus-final sign entropy is +0.260 in 1,859 distinct texts, against a range of −0.017 to +0.018 when signs are shuffled within texts.

# Evidence

- [experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json), JSON field `/profiles/ivs_all_clean/edge_asymmetry/asymmetry_initial_minus_final`.
- [experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json), JSON field `/profiles/ivs_all_clean/edge_asymmetry/shuffle_p2_5`.
- [experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json), JSON field `/profiles/ivs_all_clean/edge_asymmetry/shuffle_p97_5`.

# Scope

Entropy here measures how varied the signs at one position are. The statistic describes this population. In readable corpora it changes with genre and with counting signs or words, so the language rule fixed in advance leaves every candidate language tied.
