---
id: "F-0005"
title: "Estimating the number of lost signs does worse than always guessing one"
status_class: "failed"
area: "structure"
date: "2026-10-02"
registry_ids: ["ROOT-08", "METHODS-gap_design_matched"]
evidence: ["research/methods/results/gap_design_matched/gap_design_matched.json#/design_matched_models/local/exact_count_accuracy", "research/methods/results/gap_design_matched/gap_design_matched.json#/design_matched_models/local/constant_one_glyph_design_control_accuracy"]
population: "1,596 artificial missing-count queries, counts restricted to one through three"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Our estimate of how many signs were lost in an artificial gap was right in 46.30% of tests; always guessing one sign was right in 51.07%.

# Evidence

- [research/methods/results/gap_design_matched/gap_design_matched.json](../../research/methods/results/gap_design_matched/gap_design_matched.json), JSON field `/design_matched_models/local/exact_count_accuracy`.
- [research/methods/results/gap_design_matched/gap_design_matched.json](../../research/methods/results/gap_design_matched/gap_design_matched.json), JSON field `/design_matched_models/local/constant_one_glyph_design_control_accuracy`.

# Scope

Each test erased one to three signs inside a text. The estimator reads the signs on both sides through a sign-to-sign transition model, corrected for the rule that drew gap sizes. No physical evidence, such as gap width or traces, was available, and longer gaps were excluded.
