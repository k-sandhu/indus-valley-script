---
id: Q-1019
title: Resolve the 46 museum records that have no checked join to a local object
status: open
area: data
kind: metadata
priority: 3
data_access: local-only
compute: hours
difficulty: starter
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-COLLECTIONS-01, EVIDENCE-CENSUS-SYNTHESIS-01]
related: [Q-0005, Q-1005, Q-1018]
sources: [knowledge/DATA.md, experiments/2026-10-06-evidence-census/synthesis/join-summary.json, experiments/2026-10-06-evidence-census/synthesis/review/museum-join-check.md]
---

# Question

Which local object, if any, does each of the 46 unresolved museum records describe?

# Why it matters

The census saved 114 original-object records from six museums and confirmed 68 joins. The remaining 46 split into 13 failed string matches, 2 records with a usable key that was never tried and 31 records without a usable key in the first pass. Each new join adds an accession number, a museum photograph and often dimensions to an object that lacks them.

# What is needed

Read [DATA.md](../DATA.md). Inputs: the saved records under `data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/` and the candidate list in `data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/candidate-object-joins.json`; the CISI 1 basic data (Q-1005) for accession concordances; Marshall's p. 402 tabulation for British Museum seals. Start with the two untried keys and the 13 failed strings, then look for concordance routes for the 31 keyless records. Record each decision with its basis.

# How to decide

Done when each of the 46 records is joined, has a candidate set, or is recorded as unjoinable with the sources searched. Report the new lower bound of confirmed joins beside the census's 68.

# Prior attempts

The museum census and the synthesis review produced the 68 confirmed joins and left these 46 open.
