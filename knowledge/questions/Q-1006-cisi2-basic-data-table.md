---
id: Q-1006
title: Transcribe the CISI 2 basic-data pages for the Pakistan collections
status: open
area: data
kind: metadata
priority: 1
data_access: local-only
compute: days
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-SITES-PAK-AFG-01, EVIDENCE-CENSUS-SYNTHESIS-01]
related: [Q-1005, Q-1007, Q-1013, Q-1027, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-06-evidence-census/synthesis/catalogue-coverage.csv]
---

# Question

Transcribe the basic-data section of CISI 2 (Shah and Parpola 1991, Collections in Pakistan) into one row per catalogue entry with every printed column, following the same schema as Q-1005.

# Why it matters

CISI 2 covers Mohenjo-daro M-621 to M-1659, Harappa H-266 to H-1019 and the Pakistani collections from Amri, Allahdino, Balakot, Kot Diji, Mehrgarh, Nausharo, Pirak, Rehman Dheri and Sarai Khola. Mohenjo-daro and Harappa together hold 3,716 of the 4,695 local objects. The census measured 2,087 CISI 2 entries in these ranges, of which 736 have no exact identifier match in the local index; the basic data is the route to resolve them and to add museum numbers for objects in Karachi, Lahore, Mohenjo-daro, Harappa and other Pakistani museums, none of which has an online catalogue the census could query.

# What is needed

Read [DATA.md](../DATA.md). Input: `data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf` (archive.org scan, SHA256 `5258071b…`). Check the scan's page order and completeness against the volume's contents pages first. Use the schema and verification rule of Q-1005 so the two tables can be merged. Keep the transcription under `data/`.

# How to decide

Done when every catalogue number in the CISI 2 ranges has a row or a recorded absence, a 100-row sample has field-level error rates, and the coverage table reports gains in museum number, excavation number, findspot and dimensions for local objects. Missing scan pages are recorded as a separate acquisition gap.

# Prior attempts

The Pakistan/Afghanistan census batch and the synthesis parsed site ranges and counted matches; they did not transcribe the basic data.
