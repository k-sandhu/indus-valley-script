---
id: "Q-0036"
title: "Specify a known-script seal-locality comparator"
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

Can the known-script editions already held support an object-level duplicate-locality comparator with the same eligibility rules?

# Why it matters

Impression records and edited texts supply different object denominators.

# What is needed

Audit object IDs, source groups, find sites, complete legends and aliases in the held comparison editions. Record acquisition gaps through DATA rather than filling them with text counts. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/what-12-october-established.md](../directions/what-12-october-established.md); [experiments/2026-10-12-seal-text-identity/REPORT.md](../../experiments/2026-10-12-seal-text-identity/REPORT.md).

# How to decide

The first endpoint is feasibility: every comparison record must join to an object and site. Freeze a matched test only if the object-level denominator and dependence graph are supported.

# Prior attempts

[SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json); [BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12](../registry/attempts/BRONZE-AGE-DOCUMENTARY-COMPARISON-2026-10-12.json). Read their outcomes and `retry_when` before running this task.
