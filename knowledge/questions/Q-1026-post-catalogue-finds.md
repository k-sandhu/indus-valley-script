---
id: Q-1026
title: List inscribed objects published after the catalogues, 1987 to 2026
status: open
area: data
kind: literature
priority: 2
data_access: public
compute: days
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-SITES-NORTH-INDIA-01, EVIDENCE-CENSUS-SITES-GUJARAT-01, EVIDENCE-CENSUS-SITES-PAK-AFG-01, PUBLIC-IMAGE-REASONING-SOURCE-AUDIT-01]
related: [C-0003, Q-1011, Q-1014, Q-1016]
sources: [knowledge/DATA.md, experiments/2026-10-06-evidence-census/synthesis/REPORT.md, experiments/2026-10-12-data-inventory/sources.json]
---

# Question

Which inscribed Indus objects have been reported since the relevant CISI volume closed its site range, by which excavation and in which publication, and which of them are absent from the local corpus?

# Why it matters

The local corpus mirrors catalogue coverage, so later finds are where it is most incomplete. The census found nine north Indian sites with post-1987 inscribed finds, Dholavira's 225 recovered seals outside CISI, and site reports for Farmana, Rakhigarhi, Kanmer, Shikarpur, Nuhato, Masudpur and others. The 12 October searches found no new inscribed-object corpus for 2024–2026, but they also found excavation reports now scanned on the Internet Archive (Farmana 2006–08; Rakhigarhi 1997–2000 by Nath; Surkotada; chapter 6 of the Kanmer report) that have not been read for objects. Conjecture C-0003 predicts the motif mix of the next published seal assemblage.

# What is needed

Read [DATA.md](../DATA.md). Use *Indian Archaeology – A Review* volumes (several held), the excavation reports listed in the manifest's not-held entries, Pakistani journal reports and the census site rows. Record per object the site, season, registration, publication and page, and whether a photograph is published. Acquire the archive.org reports with `tools/fetch_data.py` once their entries carry identifiers and hashes.

# How to decide

Done when each site with reported post-catalogue finds has a row count from its best publication and each object row is matched to a local object or marked absent. Report the total of absent objects by site with the publication basis.

# Prior attempts

The regional census batches identified the sites and reports and counted finds where publications gave counts; no object list exists.
