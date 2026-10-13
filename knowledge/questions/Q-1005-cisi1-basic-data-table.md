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
prior_attempts: [EVIDENCE-CENSUS-SYNTHESIS-01, OBJECT-LEDGER-PILOT-01, CISI2-BASIC-DATA-PILOT-2026-10-13]
related: [Q-1006, Q-1007, Q-1013, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-06-evidence-census/synthesis/catalogue-coverage.csv, experiments/2026-10-06-evidence-census/synthesis/join-summary.json]
---

# Question

Transcribe every entry of the basic-data section of CISI 1 (Joshi and Parpola 1987, Collections in India) into one row per catalogue entry, keeping every printed column: CISI number, side and photograph suffixes, holding institution and museum number, FC concordance number, excavation number with its (o) and (t) markers, photograph sources, and any other column the pages print.

# Why it matters

The local export carries no museum number: only 274 of 4,695 objects (5.8%) gain one, through the older website export. CISI 1 pairs catalogue numbers with museum and excavation numbers for the Indian collections; the census used its p. 373 to confirm three Lothal museum joins. A complete table gives accession numbers for the Indian holdings of Mohenjo-daro, Harappa, Lothal, Kalibangan, Banawali and other sites, and a printed check on the export's excavation, findspot, material and dimension fields.

# What is needed

Read [DATA.md](../DATA.md). Input: `research/literature/sources/joshi_parpola_1987_cisi1.pdf` (862 PDF pages; one 431-page book scan repeated, so use the first copy and cite printed and PDF pages). Apply the corrigenda on printed p. 375 and the conventions in `knowledge/provenance/catalogue-caveats.md`. Transcription can be manual, OCR-assisted or model-assisted; whichever is used, a second pass must check a random sample. The transcribed table is a derivative of a rights-unverified volume: keep it under `data/` and track only counts, the schema and the verification record.

# How to decide

Done when every catalogue number in the volume's site ranges has a row or a recorded reason for absence, a 100-row random sample has been checked against the page images with an error rate stated by field, and a coverage table reports how many local objects gain a museum number, an FC number and an excavation number. If the sampled error rate for museum or excavation numbers exceeds 2%, revise the method before joining.

# Prior attempts

The evidence census read selected basic-data pages for site ranges and museum joins; the object ledger pilot used them for single objects. No complete transcription exists.

13 October 2026. The [CISI 2 pilot](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md)'s schema and procedure apply to CISI 1 unchanged: printed p. 366 (PDF 402) shows the same five columns, with (o) and (t) markers in column 3 for the number written on the object and the number in the excavation report's tabulation. CISI 1's basic data prints no findspot, depth, material or dimensions either, so this card's targets now name the museum, FC and excavation numbers. The basic data runs from printed p. 365 to p. 375 (PDF 401–411), about 1,533 entries by the census count, in about 20 half-column blocks. At the CISI 2 pilot's rate (5.7 seconds of agent time per entry for two blind readings, adjudication and cross-check) the section needs about 2.4 hours; a double-read pilot block should come first, since CISI 1's scan differs in resolution and type. The museum package of the same day read CISI 1 pp. 365–375 by eye for 46 museum records and confirmed 15 joins through it.
