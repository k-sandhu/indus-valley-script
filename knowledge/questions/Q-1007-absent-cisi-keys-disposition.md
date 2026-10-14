---
id: Q-1007
title: Classify every CISI catalogue entry that has no match in the local corpus
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

For each number in volumes 1 and 2 of the *Corpus of Indus Seals and Inscriptions* (CISI 1 and CISI 2) that matches no identifier exactly in the Lipi export, our local transcription corpus, is the entry an alias (a second number for an object we hold), an extra photograph or impression of a held object, a non-script mark, an object the local corpus lacks, or unresolved?

# Why it matters

The project's evidence census measured 3,620 entries in the CISI 1 and CISI 2 site ranges; 2,588 match a local identifier and 1,032 do not (166 in the Gujarat, Kutch, Maharashtra and north Indian ranges of CISI 1, 130 in the Pakistani-site ranges of CISI 1 and 736 in CISI 2). Several catalogue numbers can name one object, so 1,032 counts entries, and some of them are aliases. Rehman Dheri, Pirak, Mehrgarh and Sarai Khola contribute 344 of the absent entries, and the census describes Rehman Dheri's 270 as a mixed catalogue of marked objects. Sorting the entries gives the first measured count of script-bearing objects that the published catalogues contain and the project lacks.

# What is needed

Read [DATA.md](../DATA.md). Inputs: the census coverage tables; the CISI 1 and CISI 2 scans; the basic-data tables from Q-1005 and Q-1006 once available (CISI's lists of each entry's excavation, museum and concordance numbers); the Lipi image index for visual identity checks. Use the identity relations in `knowledge/provenance/catalogue-caveats.md` (same-object, extra-photo, impression-of, possible-match) and keep candidate matches separate from confirmed ones.

# How to decide

Done when all 1,032 entries carry one classification with a page locator and the reason, and a summary counts the classifications by site and catalogue section. A second contributor checks 50 randomly chosen classifications; if the two disagree on more than five, the disagreements are adjudicated before the counts are reported as current.

# Prior attempts

The evidence census counted the absent entries and split them by catalogue section without resolving individual entries.

13 October 2026. In M-621 to M-947 the CISI 2 basic data has rows for all 327 numbers; 44 of them have no Lipi family (the export's group of records for one object). Their excavation, museum and FC numbers (numbers in the Helsinki concordance of Indus texts) are now in the local table of the CISI 2 transcription pilot and can be used to look for them in other sources. The CISI numbers are listed in the pilot's [object-flags.csv](../../experiments/2026-10-13-cisi2-basic-data-pilot/object-flags.csv) with `join = no-lipi-family`.
