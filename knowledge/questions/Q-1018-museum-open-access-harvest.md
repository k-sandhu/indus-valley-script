---
id: Q-1018
title: Harvest open museum records and images for Indus inscribed objects
status: open
area: data
kind: data-acquisition
priority: 2
data_access: public
compute: hours
difficulty: starter
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-COLLECTIONS-01]
related: [Q-1004, Q-1019, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/sources.json, experiments/2026-10-06-evidence-census/synthesis/join-summary.json]
---

# Question

Which Indus inscribed objects are published in museum collections with open data or image terms, and what accession, dimension, findspot, bibliography and image fields does each record add?

# Why it matters

Museum records supply accession numbers, measured dimensions and photographs taken by the holding institution, which the local corpus lacks for most objects. The 12 October checks found open routes not used by the census: the Metropolitan Museum's API (v1 search retired on 1 October 2026, v1.1 live) with five Indus seals flagged public domain (49.40.1–4, 1984.482); the Cleveland Museum of Art's CC0 API with three inscribed seals (1964.104, 1973.160, 1973.161); the Penn Museum's full collections CSV under CC BY 4.0 (144 MB, updated 7 October 2026), with 34 records tagged Indus Script, many of them Chanhu-daro material on loan from the Museum of Fine Arts, Boston; the Victoria and Albert Museum API with three Mohenjo-daro seal records; and British Museum records such as 1947,0416.7, with CC BY-NC-SA 4.0 applying only to images marked for it.

# What is needed

Read [DATA.md](../DATA.md). Query each API or download with a dated, hashed record of every response under a new `data/raw/` directory: Met v1.1 search and object records, Cleveland open-access API, Penn CSV (filter locally), V&A API, British Museum object pages. Record per object the accession, title, inscription flag, site, dimensions, material, bibliography, image URL and the image licence. Join to CISI numbers through bibliography, field numbers and the CISI basic data (Q-1005), keeping candidates separate. Images with CC0 or CC BY terms may later be tracked with attribution; keep the rest local.

# How to decide

Done when each listed institution has a dated harvest record, every inscribed Indus object found has a row with its licence, and joins to local objects are counted beside the census's 68 confirmed joins. Casts and plaster impressions are recorded as such and not counted as originals.

# Prior attempts

The museum census inspected 114 original records at six institutions and confirmed 68 joins; it did not use the Cleveland, V&A or Penn bulk routes.
