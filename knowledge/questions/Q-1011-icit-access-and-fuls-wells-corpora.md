---
id: Q-1011
title: Seek access to ICIT and record the Fuls and Wells printed corpora
status: open
area: data
kind: data-acquisition
priority: 2
data_access: acquire
compute: hours
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [DATASET-LANDSCAPE-01, EVIDENCE-CENSUS-SYNTHESIS-01]
related: [Q-1013, Q-1026, Q-1028]
sources: [knowledge/DATA.md, data/MANIFEST.json, experiments/2026-10-12-data-inventory/sources.json]
---

# Question

Can the project obtain read access to, or an export from, the Interactive Corpus of Indus Texts (ICIT), and what do the current printed derivatives of it contain: Fuls, *Corpus of Indus Inscriptions* (Mathematica Epigraphica 3, second edition 2023) and *A Catalog of Indus Signs* (Mathematica Epigraphica 4, 2023), and Wells, *Epigraphic Approaches to Indus Writing* (2011) and *The Archaeology and Epigraphy of Indus Writing* (2015)?

# Why it matters

ICIT is the most complete object database: its 2023 report gives 4,665 inscribed objects, 5,650 texts and 16,015 photographs or drawings in 29 tables, with excavation numbers, findspots, material, type, preservation and iconography (CAA 2023 abstract 76). The Lipi export, our local transcription corpus, appears to derive from data exported from ICIT, but its relation to the current database is unknown. ICIT's count is the total against which local completeness should be measured, and its field values are the cheapest source for many gaps in section 2 of DATA.md.

# What is needed

Read [DATA.md](../DATA.md). The database at `indus.epigraphica.de` returned HTTP 401; the landing page asks users to request access from the administrator, and its 2010 help gives guest access limited to ten records. The Fuls volumes are self-published in print and Kindle; the Wells books are commercial print (2015 also as PDF eBook). Draft a request to the ICIT maintainer stating the fields needed, the intended use and the project's redistribution rules; the project maintainers decide whether to send it. If access is granted, record the version and terms, and measure overlap with the local corpus without copying records into files tracked in Git.

# How to decide

Done when the access request has an outcome recorded in the project's data manifest (granted with terms, declined, or not sent by maintainer decision), and the four printed works have bibliographic entries with acquisition status.

# Prior attempts

The dataset landscape survey verified the 2023 counts and the access route; the project's evidence census used the counts as a historical point of comparison.
