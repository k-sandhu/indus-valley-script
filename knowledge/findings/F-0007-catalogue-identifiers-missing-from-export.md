---
id: "F-0007"
title: "Catalogue identifiers missing from export"
status_class: "source-review"
area: "data"
date: "2026-10-07"
registry_ids: ["EVIDENCE-CENSUS-SYNTHESIS-01"]
evidence: ["experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/CISI1_BC_entries", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/CISI1_BC_matching_keys", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/CISI1_BC_absent_keys", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/CISI1_BC_absent_graffiti_or_pottery_sections", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/CISI1_BC_absent_seal_impression_tablet_other_sections"]
population: "493 identifiers across 19 CISI volume 1 ranges in Gujarat and north India"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Of 493 catalogue identifiers, 327 matched local keys and 166 were absent. The absent keys comprised 75 in pottery/graffiti sections and 91 in other sections.

# Evidence

- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/CISI1_BC_entries`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/CISI1_BC_matching_keys`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/CISI1_BC_absent_keys`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/CISI1_BC_absent_graffiti_or_pottery_sections`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/CISI1_BC_absent_seal_impression_tablet_other_sections`.

# Scope

The reviewed source census compares selected catalogue ranges with the pinned export and source-attested aliases. An absent key is an unresolved object join. This denominator covers those ranges and supplies no worldwide recall estimate.
