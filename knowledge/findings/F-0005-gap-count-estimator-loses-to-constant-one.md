---
id: "F-0005"
title: "Gap-count estimator loses to constant one"
status_class: "failed"
area: "structure"
date: "2026-10-02"
registry_ids: ["ROOT-08", "METHODS-gap_design_matched"]
evidence: ["research/methods/results/gap_design_matched/gap_design_matched.json#/design_matched_models/local/exact_count_accuracy", "research/methods/results/gap_design_matched/gap_design_matched.json#/design_matched_models/local/constant_one_glyph_design_control_accuracy"]
population: "1,596 artificial missing-count queries, counts restricted to one through three"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

The sampling-matched local estimator recovered the count in 46.30% of queries, below the constant-one control’s 51.07%.

# Evidence

- [research/methods/results/gap_design_matched/gap_design_matched.json](../../research/methods/results/gap_design_matched/gap_design_matched.json), JSON field `/design_matched_models/local/exact_count_accuracy`.
- [research/methods/results/gap_design_matched/gap_design_matched.json](../../research/methods/results/gap_design_matched/gap_design_matched.json), JSON field `/design_matched_models/local/constant_one_glyph_design_control_accuracy`.

# Scope

The adjustment matches the artificial sampling law while retaining models and queries. The comparator always predicts one erased sign. Physical gap geometry and surviving traces were absent, and the declared candidate counts exclude larger gaps.
