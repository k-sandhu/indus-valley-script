---
id: "F-0022"
title: "Initial and final sign concentration differs"
status_class: "frozen-evaluation"
area: "structure"
date: "2026-10-12"
registry_ids: ["STRUCTURAL-TYPOLOGY-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json#/profiles/ivs_all_clean/edge_asymmetry/asymmetry_initial_minus_final", "experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json#/profiles/ivs_all_clean/edge_asymmetry/shuffle_p2_5", "experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json#/profiles/ivs_all_clean/edge_asymmetry/shuffle_p97_5"]
population: "1,859 distinct clean Indus texts"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Normalized initial-minus-final sign entropy was +0.260, against a shuffle range of −0.017 to +0.018.

# Evidence

- [experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json), JSON field `/profiles/ivs_all_clean/edge_asymmetry/asymmetry_initial_minus_final`.
- [experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json), JSON field `/profiles/ivs_all_clean/edge_asymmetry/shuffle_p2_5`.
- [experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json), JSON field `/profiles/ivs_all_clean/edge_asymmetry/shuffle_p97_5`.

# Scope

The statistic compares diversity at the two ends of complete texts with within-text shuffling. It describes concentration in the selected population. Genre and sign-versus-word units change the comparison statistic, so the frozen language rule leaves candidates tied.
