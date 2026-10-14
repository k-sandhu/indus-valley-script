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

The Lipi export is our local transcription corpus: the data files of the public Lipi repository at one pinned commit. Under what terms may the project publish the metadata of individual records (site, context, material, dimensions, identifiers) derived from it, and through which upstream source does that right run: the Interactive Corpus of Indus Texts (ICIT), the *Corpus of Indus Seals and Inscriptions* (CISI) or the Lipi maintainer?

# Why it matters

The Lipi export is the base of the local object register: every percentage in DATA.md's coverage table is measured on it. It has no licence at the pinned commit, and the project's evidence census found that its numbering follows the ICIT-derived export. Until the project has a basis for reuse, such as a licence or a recorded permission, the register built in Q-1030 can be published only as aggregates and identifiers, and contributors without their own copy of the export cannot reproduce the measurements.

# What is needed

Read [DATA.md](../DATA.md) and [REDISTRIBUTION.md](../provenance/REDISTRIBUTION.md). Check the current upstream repository for a licence or data notice and record the commit. Trace each metadata field to its probable origin (ICIT, CISI basic data, excavation reports) using the field definitions and a sample of objects. Draft a short permission request to the Lipi maintainer and, if the data are ICIT-derived, to the ICIT maintainer. The maintainers decide whether to send it; this task prepares and records it.

# How to decide

Done when the upstream status is recorded with a dated saved copy of the upstream page as evidence, the field provenance sample is written up, and either a permission record exists or the maintainers have decided not to ask. The maintainers record the decision and its scope in REDISTRIBUTION.md.

# Prior attempts

The dataset landscape survey found no licence at the pinned commit and none reported by GitHub metadata; the October 11 public release kept the bulk export local and published twenty short attributed excerpts.
