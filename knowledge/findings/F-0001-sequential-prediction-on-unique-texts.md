---
id: "F-0001"
title: "The previous sign helps predict the next one"
status_class: "verified-computation"
area: "structure"
date: "2026-10-02"
registry_ids: ["ROOT-02"]
evidence: ["research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json#/observed/gain_bits_per_noninitial_sign", "research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json#/observed/records", "research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json#/observed/noninitial_tokens"]
population: "1,596 distinct complete right-to-left single-line strings, 6,413 noninitial signs"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Knowing the previous sign improved prediction of held-out texts by 0.848 bits per noninitial sign (each sign after the first), compared with a model using only position, site and object type, on 1,596 distinct texts with 6,413 noninitial signs.

# Evidence

- [research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json](../../research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json), JSON field `/observed/gain_bits_per_noninitial_sign`.
- [research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json](../../research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json), JSON field `/observed/records`.
- [research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json](../../research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json), JSON field `/observed/noninitial_tokens`.

# Scope

Records of one physical object were kept together in cross-validation. The chance comparison shuffled signs among texts of equal length, site and type, keeping positions and creating no duplicate texts, and refitted everything for each shuffle. This measures order in the selected transcriptions; dates follow UTC in the original work log.
