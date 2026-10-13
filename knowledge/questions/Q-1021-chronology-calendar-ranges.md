---
id: Q-1021
title: Map site period, phase and stratum labels to cited calendar ranges
status: open
area: data
kind: metadata
priority: 2
data_access: public
compute: days
difficulty: expert
claimed_by: ""
claim_expires: ""
prior_attempts: [CHRONOLOGY-REGION-01, BACKWARD-CHRONOLOGY-01]
related: [Q-0007, Q-1014, Q-1016, Q-1017, Q-1022, C-0005]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/run-2026-10-12/field-coverage-by-site.csv]
---

# Question

For every distinct chronology label in the local export (`time`, `period`, `phase`), what calendar interval does the excavator's dating model give, on what basis, and with what uncertainty?

# Why it matters

No local object has a calendar date: the `time`, `period` and `phase` fields carry 21, 57 and 38 distinct site-specific labels (HARP periods such as `Period 3C`, Mohenjo-daro levels such as `Late`, strata such as `Stratum IV`), and 55.8% of objects have at least one of them. A mapping table converts these into intervals that can be compared across sites, while keeping each label's own sequence and datum. Tests of change over time, including C-0005's prediction about tablet tiers across Harappa periods, depend on it.

# What is needed

Read [DATA.md](../DATA.md). List each distinct label with its site and object count from the local export. For each, find the excavator's phasing and its published radiocarbon or comparative dating: HARP publications for Harappa (Kenoyer and Meadow; Meadow and Kenoyer), Marshall, Mackay and the Aachen work for Mohenjo-daro, Bisht for Dholavira, the Kalibangan and Lothal reports. Record interval, basis, citation with page, and whether the label is a deposit, a building level or a cultural period. Labels with the same name at different sites stay separate.

# How to decide

Done when every label carrying at least five objects has an interval with a citation or a recorded reason why none exists, and the table reports how many objects gain a calendar interval. Rare labels can stay unmapped with a reason.

# Prior attempts

The chronology-region study compared periods inside Harappa without calendar mapping; the backward-chronology assembly dated later continuity evidence, not the Indus objects themselves.
