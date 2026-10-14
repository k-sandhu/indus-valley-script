---
id: "Q-0036"
title: "Design a duplicate-locality comparison from seals in readable scripts"
status: "open"
area: "comparative"
kind: "analysis"
priority: 3
data_access: "local-only"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12", "BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12"]
related: ["F-0026", "F-0028"]
sources: ["knowledge/directions/what-12-october-established.md", "experiments/2026-10-12-seal-text-identity/REPORT.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can the editions of readable-script seals we already hold support an object-level comparison of where duplicate texts are found, under the same eligibility rules as the Indus test?

# Why it matters

Counting impressions and counting edited texts give different numbers of objects.

# What is needed

Audit object IDs, source groups, find sites, complete legends and aliases in the comparison editions we hold. Record acquisition gaps in DATA.md instead of filling them with text counts. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/what-12-october-established.md](../directions/what-12-october-established.md); [experiments/2026-10-12-seal-text-identity/REPORT.md](../../experiments/2026-10-12-seal-text-identity/REPORT.md).

# How to decide

The first result is feasibility: every comparison record must link to an object and a site. Freeze a matched test only if the object count and the dependence graph are supported.

# Prior attempts

[SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json); [BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12](../registry/attempts/BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12.json). Read their outcomes and `retry_when` conditions before running this task.
