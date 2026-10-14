---
id: Q-1022
title: Convert depth strings to metres against a named datum
status: open
area: data
kind: metadata
priority: 3
data_access: local-only
compute: hours
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [CONTEXT-01, MACKAY-MARSHALL-TABLES-2026-10-13]
related: [Q-1003, Q-1021]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/run-2026-10-12/summary.json]
---

# Question

What is each local depth value in metres, measured from which datum (the fixed reference height from which an excavator measured depths or levels), and how reliable is the conversion?

# Why it matters

Depth is present for 50.6% of objects. At Mohenjo-daro, where 72.4% of objects have one, it is the main evidence for an object's place in the sequence of deposits. The 2,810 usable values, counted per face (the local corpus records each inscribed side as a face), mix feet (2,557), metres (72) and other forms (181, including 50 surface finds). Mackay measured levels from a fixed point, the DK datum, while Marshall measured depth below the modern surface; the same number therefore means different heights in the two excavations, and a cross-site or cross-season comparison needs both the unit and the datum.

# What is needed

Read [DATA.md](../DATA.md). Input: the `depth` field of `data/normalized/lipi_observed_faces.jsonl`, with site, area and excavation number. Parse each string into value, unit, sign and qualifiers; assign the datum by site, excavation season and excavator, using Marshall 1931 and Mackay 1938 (via Q-1003) for Mohenjo-daro and Vats 1940 for Harappa. Keep the original string beside every converted value.

# How to decide

Done when every usable depth string has a parsed value and unit, a datum or an explicit `datum-unknown`, and a converted metre value where the datum allows. Report the share of objects with a datum-anchored depth by site.

# Prior attempts

The October context audit separated the `- -` placeholder from informative depths but did not parse units or datums.

13 October 2026: the Mackay and Marshall join gives 1,101 Mohenjo-daro objects a level with its datum (Mackay: DK datum, or the SD bench mark 2.2 ft above it for the SD area; Marshall: below the modern surface), keyed by Lipi family (the local corpus's group of records for one object) in [join-table.csv](../../experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv). The export's depth strings agree with the table levels for 1,107 of 1,110 comparable rows.
