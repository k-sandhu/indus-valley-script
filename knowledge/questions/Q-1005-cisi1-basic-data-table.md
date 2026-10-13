---
id: Q-1005
title: Transcribe the CISI 1 basic-data pages into an object table with museum and excavation numbers
status: open
area: data
kind: metadata
priority: 1
data_access: local-only
compute: days
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-SYNTHESIS-01, OBJECT-LEDGER-PILOT-01]
related: [Q-1006, Q-1007, Q-1013, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-06-evidence-census/synthesis/catalogue-coverage.csv, experiments/2026-10-06-evidence-census/synthesis/join-summary.json]
---

# Question

Transcribe every entry of the basic-data section of CISI 1 (Joshi and Parpola 1987, Collections in India) into one row per catalogue entry, keeping every printed column: CISI number, side and photograph suffixes, holding institution and museum number, excavation number, findspot, depth, material and dimensions, and any other column the pages print.

# Why it matters

The local export carries no museum number: only 274 of 4,695 objects (5.8%) gain one, through the older website export. CISI 1 pairs catalogue numbers with museum and excavation numbers for the Indian collections; the census used its p. 373 to confirm three Lothal museum joins. A complete table gives accession numbers for the Indian holdings of Mohenjo-daro, Harappa, Lothal, Kalibangan, Banawali and other sites, and a printed check on the export's excavation, findspot, material and dimension fields.

# What is needed

Read [DATA.md](../DATA.md). Input: `research/literature/sources/joshi_parpola_1987_cisi1.pdf` (862 PDF pages; one 431-page book scan repeated, so use the first copy and cite printed and PDF pages). Apply the corrigenda on printed p. 375 and the conventions in `knowledge/provenance/catalogue-caveats.md`. Transcription can be manual, OCR-assisted or model-assisted; whichever is used, a second pass must check a random sample. The transcribed table is a derivative of a rights-unverified volume: keep it under `data/` and track only counts, the schema and the verification record.

# How to decide

Done when every catalogue number in the volume's site ranges has a row or a recorded reason for absence, a 100-row random sample has been checked against the page images with an error rate stated by field, and a coverage table reports how many local objects gain a museum number, an excavation number and dimensions. If the sampled error rate for museum or excavation numbers exceeds 2%, revise the method before joining.

# Prior attempts

The evidence census read selected basic-data pages for site ranges and museum joins; the object ledger pilot used them for single objects. No complete transcription exists.
