---
id: "F-0009"
title: "Site frame coverage in the local export"
status_class: "source-review"
area: "data"
date: "2026-10-07"
registry_ids: ["EVIDENCE-CENSUS-SYNTHESIS-01"]
evidence: ["experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/represented_local_faces", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/local_all_faces", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/site_or_provenance_entities_after_aliases", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/raw_batch_rows"]
population: "5,680 local face rows compared with the census site-label frame"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

The census frame represented 5,652 of 5,680 local faces across 115 site/provenance entities assembled from 123 batch rows.

# Evidence

- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/represented_local_faces`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/local_all_faces`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/site_or_provenance_entities_after_aliases`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/raw_batch_rows`.

# Scope

Coverage refers to normalized export rows assigned to the source-label frame after overlap removal. Face rows and provisional object families have different denominators. Worldwide published-find coverage remains unknown.
