---
id: "Q-0035"
title: "Audit completeness for a quantity inventory"
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

Can a held physical inventory establish whether an associated count or pool is complete, with units and commodity scope?

# Why it matters

The numerical controls show that a partial pool called complete can accept wrong values.

# What is needed

Choose one held source-defined inventory and trace membership, missing fragments, measurement uncertainty and publication selection. List the absent independent count through DATA. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md); [knowledge/directions/decipherment-readiness-2026-10-02.md](../directions/decipherment-readiness-2026-10-02.md).

# How to decide

Pass requires source-supported completeness and an independently recorded quantity. Stop with a partial or unknown-completeness ledger when the publication cannot establish membership.

# Prior attempts

[REGIONNUM-01](../registry/attempts/REGIONNUM-01.json); [KHI-04](../registry/attempts/KHI-04.json). Read their outcomes and `retry_when` before running this task.
