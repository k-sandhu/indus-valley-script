---
id: Q-1023
title: Acquire specimen-level records of the Tamil Nadu graffiti corpus
status: open
area: data
kind: data-acquisition
priority: 4
data_access: public
compute: hours
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [TN-STROKE-01, TN-SOURCE-02]
related: [Q-1029]
sources: [knowledge/DATA.md, experiments/2026-10-02-connections-and-priority/south-india/REPORT-reviewed-v1.md, experiments/2026-10-12-data-inventory/sources.json]
---

# Question

Can the Tamil Nadu graffiti corpus be held at specimen level (one row per graffiti-bearing sherd, with site, context, depth, ware and sign class), rather than as the aggregate margins the project snapshotted on 2 October?

# Why it matters

The portal tngraffiti.in, maintained by the Indus Research Centre with the Tamil Nadu State Department of Archaeology, states 15,184 graffiti-bearing potsherds from 140 sites, 2,107 unique signs and a classification of 42 base signs, 544 variants and 1,521 composites from 9,486 recognised graffiti. The project's snapshot gives aggregate counts whose site and depth margins cannot be combined into specimen rows. This is a comparative collection of later South Indian marks, not Indus inscriptions, so it ranks below the Indus object work.

# What is needed

Read [DATA.md](../DATA.md). Held locally: the 2 October API snapshot and both volumes of Rajan and Sivanantham, *Inscribed Potsherds of Tamil Nadu: Graffiti and Tamiḻi* (2026), and the 2025 morphological study. The 12 October check found the portal's client and base-sign response unchanged since the snapshot and no stated licence. Test whether the API exposes specimen-level routes; otherwise extract the volume II concordance tables into a local specimen table with page locators.

# How to decide

Done when a specimen-level table exists locally with its source route and coverage, or when the absence of a specimen route is recorded and the printed concordance is tabulated instead.

# Prior attempts

The South Indian stroke study and the original-source audit used the aggregate API and selected specimens.
