---
id: Q-1029
title: Identify every local PDF and complete the literature index
status: open
area: data
kind: tooling
priority: 4
data_access: local-only
compute: hours
difficulty: starter
claimed_by: ""
claim_expires: ""
prior_attempts: []
related: [Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/run-2026-10-12/holdings/holdings-summary.json, experiments/2026-10-12-data-inventory/run-2026-10-12/holdings/literature-harvest-summary.json]
---

# Question

For each of the 299 distinct local PDFs, what is its exact title, edition, page count and acquisition record, and which held files are duplicates, excerpts or misidentified?

# Why it matters

Earlier packages acquired 365 PDF files (299 distinct by SHA256, 2.7 GB of distinct content) and wrote source records in many schemas. A heuristic harvest of those records found 3,127 distinct titles but could link only 62 of them to a local PDF path, so contributors cannot easily see which reports are already on disk. At least one file is of uncertain identity: `rakhigarhi_inventory.pdf`, an image-only IGNCA scan whose catalogue page carried a different site name in a search result.

# What is needed

Read [DATA.md](../DATA.md). Inputs: `data/raw/2026-10-12-data-inventory/holdings-v1/pdf-hashes.jsonl` and `harvested-sources.jsonl`, and every package's `sources.json` and acquisition records. For each hash, read the title page and record title, authors, year, edition, pages and the acquisition record that produced it. Write the index locally and a tracked summary of counts by kind (excavation report, catalogue, article, book).

# How to decide

Done when every distinct PDF hash has a title-page identity or a recorded failure, and DATA.md's held-source table can be regenerated from the index.

# Prior attempts

None as a whole; individual packages recorded their own acquisitions.
