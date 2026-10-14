---
id: Q-1018
title: Harvest open museum records and images for Indus inscribed objects
status: done
area: data
kind: data-acquisition
priority: 2
data_access: public
compute: hours
difficulty: starter
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-COLLECTIONS-01, MUSEUM-OPEN-ACCESS-2026-10-13]
related: [Q-1004, Q-1019, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/sources.json, experiments/2026-10-06-evidence-census/synthesis/join-summary.json]
---

# Question

Which Indus inscribed objects are published in museum collections with open data or image terms, and what accession, dimension, findspot, bibliography and image fields does each record add?

# Why it matters

Museum records supply accession numbers, measured dimensions and photographs taken by the holding institution, which the local corpus lacks for most objects. The 12 October checks found open routes that the project's evidence census had not used: the Metropolitan Museum's API (v1 search retired on 1 October 2026, v1.1 live) with five Indus seals flagged public domain (49.40.1–4, 1984.482); the Cleveland Museum of Art's CC0 API with three inscribed seals (1964.104, 1973.160, 1973.161); the Penn Museum's full collections CSV under CC BY 4.0 (144 MB, updated 7 October 2026), with 34 records tagged Indus Script, many of them Chanhu-daro material on loan from the Museum of Fine Arts, Boston; the Victoria and Albert Museum API with three Mohenjo-daro seal records; and British Museum records such as 1947,0416.7, with CC BY-NC-SA 4.0 applying only to images marked for it.

# What is needed

Read [DATA.md](../DATA.md). Query each API or download with a dated, hashed record of every response under a new `data/raw/` directory: Met v1.1 search and object records, Cleveland open-access API, Penn CSV (filter locally), V&A API, British Museum object pages. Record per object the accession, title, inscription flag, site, dimensions, material, bibliography, image URL and the image licence. Join each record to its CISI number, its entry in the *Corpus of Indus Seals and Inscriptions*, which means recording that both describe the same object and on what basis. Use the bibliography, field numbers and the CISI basic data (Q-1005), the catalogue's table of excavation and museum numbers, and keep candidate joins separate. Images with CC0 or CC BY terms may later be tracked in Git with attribution; keep the rest local.

# How to decide

Done when each listed institution has a dated harvest record, every inscribed Indus object found has a row with its licence, and joins to local objects are counted beside the census's 68 confirmed joins. Casts and plaster impressions are recorded as such and not counted as originals.

# Prior attempts

The museum batch of the census inspected 114 records of original objects at six institutions and confirmed 68 joins; it did not use the Cleveland, V&A or Penn bulk routes.

13 October 2026, outcome: Seven institutions have a dated harvest record ([package](../../experiments/2026-10-13-museum-open-access/README.md)). Inscribed Indus originals found: Metropolitan 5 and Cleveland 3 (CC0, with photographs, no findspot or number), Penn 5 (CC BY 4.0 data; plus 4 uninscribed seal-amulets and 38 casts or impressions), V&A 2 inscribed originals among 4 reviewed attributed records (plus a modern impression and figurine head IS.9-1951 outside inscription scope), British Museum 7 with a stated inscription among 27 listed Indus stamp-seals, Art Institute of Chicago 0, Smithsonian 0 (20 casts in 539,615 bulk records). Every record has a row with its data and image licence in `harvest/` and `joins/join-table.csv`. Joins beside the census's 68: 27 exact or confirmed records in this package, 19 new, so 87 museum records are joined. Casts and impressions are recorded and not counted as originals. Left open: the British Museum's object pages are behind a Cloudflare challenge, so 20 of its Indus seals lack a reachable description and five cannot yet be joined; reading their Miscellaneous numbers in a browser would settle them. Raw V&A responses must be deleted by 10 November 2026 under the V&A API terms.
