---
id: "F-0009"
title: "The census site list covers 5,652 of 5,680 corpus faces"
status_class: "source-review"
area: "data"
date: "2026-10-07"
registry_ids: ["EVIDENCE-CENSUS-SYNTHESIS-01"]
evidence: ["experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/represented_local_faces", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/local_all_faces", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/site_or_provenance_entities_after_aliases", "experiments/2026-10-06-evidence-census/synthesis/coverage.json#/summary/raw_batch_rows"]
population: "5,680 local face rows compared with the census site-label frame"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

The census site list covers 5,652 of the 5,680 faces (inscribed sides) in our corpus. Its 123 entries, compiled in separate batches, name 115 sites or provenance labels once aliases are merged.

# Evidence

- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/represented_local_faces`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/local_all_faces`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/site_or_provenance_entities_after_aliases`.
- [experiments/2026-10-06-evidence-census/synthesis/coverage.json](../../experiments/2026-10-06-evidence-census/synthesis/coverage.json), JSON field `/summary/raw_batch_rows`.

# Scope

Coverage counts normalized corpus rows whose site label falls in the census list, with overlapping entries counted once; the other faces have no known site. Faces and provisional objects have different totals. Worldwide coverage of published finds remains unknown.
