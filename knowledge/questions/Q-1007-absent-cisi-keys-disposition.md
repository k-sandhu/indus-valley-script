---
id: Q-1007
title: Give every CISI catalogue entry missing from the local index a disposition
status: open
area: data
kind: metadata
priority: 2
data_access: local-only
compute: days
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-SYNTHESIS-01, CISI2-BASIC-DATA-PILOT-2026-10-13]
related: [Q-1005, Q-1006, Q-1027, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-06-evidence-census/synthesis/catalogue-coverage.csv, experiments/2026-10-06-evidence-census/synthesis/catalogue-section-split.csv]
---

# Question

For each CISI 1 and CISI 2 catalogue number that has no exact identifier match in the local export, is it an alias of a held object, an extra photograph or impression of one, a non-script mark, an object the local corpus lacks, or unresolved?

# Why it matters

The census measured 3,620 entries in CISI 1 and CISI 2 site ranges; 2,588 match a local identifier and 1,032 do not (166 in the Gujarat, Kutch, Maharashtra and north Indian ranges of CISI 1, 130 in the Pakistani-site ranges of CISI 1 and 736 in CISI 2). These are catalogue keys, not counted objects: some are aliases, and Rehman Dheri, Pirak, Mehrgarh and Sarai Khola contribute 344 of the absent entries, with Rehman Dheri's 270 described by the census as a mixed catalogue of marked objects. Separating them gives the first measured count of script-bearing objects the project lacks within published catalogues.

# What is needed

Read [DATA.md](../DATA.md). Inputs: the census coverage tables; the CISI 1 and CISI 2 scans; the basic-data tables from Q-1005 and Q-1006 once available; the Lipi image index for visual identity checks. Use the identity relations in `knowledge/provenance/catalogue-caveats.md` (same-object, extra-photo, impression-of, possible-match) and keep candidate joins separate from confirmed ones.

# How to decide

Done when all 1,032 entries carry one disposition with a page locator and the reason, and a summary counts dispositions by site and catalogue section. A second contributor checks 50 randomly chosen dispositions; disagreement on more than five requires adjudication before the counts are reported as current.

# Prior attempts

The evidence census counted the absent keys and split them by catalogue section without resolving individual entries.

13 October 2026. In M-621 to M-947 the CISI 2 basic data has rows for all 327 numbers; 44 of them have no Lipi family. Their excavation, museum and FC numbers are now in the local pilot table and can be used to look for them in other sources. The CISI numbers are listed in the pilot's [object-flags.csv](../../experiments/2026-10-13-cisi2-basic-data-pilot/object-flags.csv) with `join = no-lipi-family`.
