---
id: Q-1028
title: Establish a reuse basis for the Lipi export's record-level metadata
status: open
area: data
kind: data-acquisition
priority: 2
data_access: acquire
compute: hours
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [DATASET-LANDSCAPE-01, GITHUB-PUBLIC-RELEASE-2026-10-11]
related: [Q-1011, Q-1030]
sources: [knowledge/DATA.md, knowledge/provenance/REDISTRIBUTION.md, REUSE.md]
---

# Question

Under what terms may the project publish record-level metadata (site, context, material, dimensions, identifiers) derived from the Lipi export, and through which upstream source (ICIT, CISI, the Lipi maintainer) does that right run?

# Why it matters

The Lipi export is the base of the local object register: every percentage in DATA.md's coverage table is measured on it. It has no licence at the pinned commit, and the census found that its numbering follows the ICIT-derived export. Until a reuse basis exists, the register built in Q-1030 can be published only as aggregates and identifiers, and contributors without the owner's local copy cannot reproduce the measurements.

# What is needed

Read [DATA.md](../DATA.md) and [REDISTRIBUTION.md](../provenance/REDISTRIBUTION.md). Check the current upstream repository for a licence or data notice and record the commit. Trace each metadata field to its probable origin (ICIT, CISI basic data, excavation reports) using the field definitions and a sample of objects. Draft, for the owner, a short permission request to the Lipi maintainer and, if the data are ICIT-derived, to the ICIT maintainer. Sending any request is the owner's decision; this task prepares and records it.

# How to decide

Done when the upstream status is recorded with a dated witness, the field provenance sample is written up, and either a permission record exists or the owner has decided not to ask. The decision and its scope go into REDISTRIBUTION.md through its owner.

# Prior attempts

The dataset landscape found no licence at the pin and none reported by GitHub metadata; the October 11 public release kept the bulk export local and published twenty short attributed excerpts.
