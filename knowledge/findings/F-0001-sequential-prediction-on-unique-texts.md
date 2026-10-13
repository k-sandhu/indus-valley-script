---
id: "F-0001"
title: "Sequential prediction on unique texts"
status_class: "verified-computation"
area: "structure"
date: "2026-10-02"
registry_ids: ["ROOT-02"]
evidence: ["research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json#/observed/gain_bits_per_noninitial_sign", "research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json#/observed/records", "research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json#/observed/noninitial_tokens"]
population: "1,596 distinct complete right-to-left single-line strings, 6,413 noninitial signs"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Previous-sign information improved held-out log score by 0.848 bits per noninitial sign on 1,596 distinct strings and 6,413 noninitial signs.

# Evidence

- [research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json](../../research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json), JSON field `/observed/gain_bits_per_noninitial_sign`.
- [research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json](../../research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json), JSON field `/observed/records`.
- [research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json](../../research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json), JSON field `/observed/noninitial_tokens`.

# Scope

The comparator is the selected independent position/site/type baseline, with physical aliases retained in grouping. The uniqueness-conditioned reference repeats nested fitting. This measures order in the selected transcriptions; the measurement date follows UTC in the original work log.
