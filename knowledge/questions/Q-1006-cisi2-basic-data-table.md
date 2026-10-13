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
prior_attempts: [EVIDENCE-CENSUS-SITES-PAK-AFG-01, EVIDENCE-CENSUS-SYNTHESIS-01, CISI2-BASIC-DATA-PILOT-2026-10-13]
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

Done when every catalogue number in the CISI 2 ranges has a row or a recorded absence, a 100-row sample has field-level error rates, and the coverage table reports gains in museum number, NMP accession, excavation number and FC number for local objects; the basic data prints no findspot or dimensions. Missing scan pages are recorded as a separate acquisition gap.

# Prior attempts

The Pakistan/Afghanistan census batch and the synthesis parsed site ranges and counted matches; they did not transcribe the basic data.

13 October 2026, [CISI 2 basic-data pilot](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md). The basic data occupies printed pp. 434–447 (PDF 469–482) and prints five columns: CISI number, FC number, excavation number, museum and registration numbers, and photograph sources. It has no findspot, depth, material or dimension column. The scan's page order holds at both ends of the catalogue (printed page = PDF − 35 for pp. 1–447; 418 of 447 page headers confirm it, the other 29 have not been inspected). The pilot transcribed M-621 to M-947, 327 entries on pp. 435–436, read twice in full by independent readers and adjudicated against the page. The readings agree on 90.5% of cells (excavation numbers 91.4%, museum numbers 85.6%); the sampled first-pass error rate for excavation numbers was 3.0% (1 of 33), above the 2% limit of Q-1005, so double reading of every row is the rule; 119 of 1,635 cells stay bracketed because the scan cannot separate some digits. Joined to 283 Lipi families, the block adds a museum number to 202 objects and an FC number to all 283, and shows that Lipi's `excavation-idno` appends the excavator's catalogue number to the printed excavation number for 182 objects with four-digit FC numbers (the FC number is 1000 plus Marshall's or 2000 plus Mackay's catalogue number), with two pairs of objects whose records are crossed between Lipi and CISI 2; measured on the plates, the four seals fit the sizes of Lipi's pairing, so the error is in CISI 2's table ([swap check](../../experiments/2026-10-13-data-round-1-verification/swap-check.md)). An independent verification reproduced every count and led to four rights redactions and three count corrections ([REVIEW-CHANGES.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/REVIEW-CHANGES.md)). Values are local. The remaining 22 half-column blocks and the double-reading rule are in the package's [PROCEDURE.md](../../experiments/2026-10-13-cisi2-basic-data-pilot/PROCEDURE.md).
