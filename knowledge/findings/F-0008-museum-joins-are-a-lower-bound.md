---
id: "F-0008"
title: "At least 68 of 114 museum records match objects in our corpus"
status_class: "source-review"
area: "data"
date: "2026-10-07"
registry_ids: ["EVIDENCE-CENSUS-SYNTHESIS-01"]
evidence: ["experiments/2026-10-06-evidence-census/synthesis/join-summary.json#/museum_original_records", "experiments/2026-10-06-evidence-census/synthesis/join-summary.json#/confirmed_identifier_joins", "experiments/2026-10-06-evidence-census/synthesis/join-summary.json#/unconfirmed_records"]
population: "114 inspected inscription-confirmed original museum records"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Of 114 online museum records of original inscribed objects that we inspected, 68 could be linked with confidence to objects in our corpus; 46 remain unlinked.

# Evidence

- [experiments/2026-10-06-evidence-census/synthesis/join-summary.json](../../experiments/2026-10-06-evidence-census/synthesis/join-summary.json), JSON field `/museum_original_records`.
- [experiments/2026-10-06-evidence-census/synthesis/join-summary.json](../../experiments/2026-10-06-evidence-census/synthesis/join-summary.json), JSON field `/confirmed_identifier_joins`.
- [experiments/2026-10-06-evidence-census/synthesis/join-summary.json](../../experiments/2026-10-06-evidence-census/synthesis/join-summary.json), JSON field `/unconfirmed_records`.

# Scope

A link rests on a reviewed identifier or a published concordance. The first comparison pass found fewer links, and later links lack the full field-by-field comparison. The 68 is a minimum for the inspected records, and the 46 are unresolved within this selected set.
