---
id: "Q-0035"
title: "Find a physical inventory whose count is known to be complete"
status: "open"
area: "data"
kind: "metadata"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "expert"
claimed_by: ""
claim_expires: ""
prior_attempts: ["REGIONNUM-01", "KHI-04"]
related: ["F-0006"]
sources: ["knowledge/directions/research-roadmap.md", "knowledge/directions/decipherment-readiness-2026-10-02.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can a physical inventory we hold establish whether an associated count or pool is complete, with its units and commodity scope?

# Why it matters

Our simulated numeral tests show that a partial pool treated as complete can accept wrong values.

# What is needed

Choose one inventory defined in a source we hold and trace membership, missing fragments, measurement uncertainty and publication selection. Record the missing independent count in DATA.md. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md); [knowledge/directions/decipherment-readiness-2026-10-02.md](../directions/decipherment-readiness-2026-10-02.md).

# How to decide

A pass requires source-supported completeness and an independently recorded quantity. Stop with a partial or unknown-completeness ledger when the publication cannot establish membership.

# Prior attempts

[REGIONNUM-01](../registry/attempts/REGIONNUM-01.json); [KHI-04](../registry/attempts/KHI-04.json). Read their outcomes and `retry_when` conditions before running this task.
