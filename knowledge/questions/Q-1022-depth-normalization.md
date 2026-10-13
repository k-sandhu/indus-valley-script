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
prior_attempts: [CONTEXT-01]
related: [Q-1003, Q-1021]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/run-2026-10-12/summary.json]
---

# Question

What is each local depth value in metres, measured from which datum, and how reliable is the conversion?

# Why it matters

Depth is present for 50.6% of objects and is the main stratigraphic proxy for Mohenjo-daro (72.4% of its objects). The 2,810 usable face values mix feet (2,557), metres (72) and other forms (181, including 50 surface finds). Mackay measured from the DK datum, Marshall below the modern surface; the same number therefore means different heights in the two excavations, and a cross-site or cross-season comparison needs both the unit and the datum.

# What is needed

Read [DATA.md](../DATA.md). Input: the `depth` field of `data/normalized/lipi_observed_faces.jsonl`, with site, area and excavation number. Parse each string into value, unit, sign and qualifiers; assign the datum by site, excavation season and excavator, using Marshall 1931 and Mackay 1938 (via Q-1003) for Mohenjo-daro and Vats 1940 for Harappa. Keep the original string beside every converted value.

# How to decide

Done when every usable depth string has a parsed value and unit, a datum or an explicit `datum-unknown`, and a converted metre value where the datum allows. Report the share of objects with a datum-anchored depth by site.

# Prior attempts

The October context audit separated the `- -` placeholder from informative depths but did not parse units or datums.
