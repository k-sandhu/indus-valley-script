---
id: "Q-0001"
title: "Review a 30-object identity block"
status: "open"
area: "data"
kind: "metadata"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["ROOT-19", "OBJECT-LEDGER-PILOT-01"]
related: []
sources: ["knowledge/directions/research-roadmap.md", "knowledge/directions/context-data-plan.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can a 30-object block from the held source collection be joined across catalogue, excavation and museum identifiers without forcing uncertain matches?

# Why it matters

Physical identity determines which faces belong together and which observations are independent.

# What is needed

Use the roadmap’s observation block and held images/registers. Retain source namespaces, all aliases, locators, competing matches and a disagreement ledger in a new package. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Stop after the fixed 30 objects. Every asserted same-object edge must have an accession, excavation or plate witness; retain unsupported edges as possible matches. Report resolved, conflicting and unresolved counts.

# Prior attempts

[ROOT-19](../registry/attempts/ROOT-19.json); [OBJECT-LEDGER-PILOT-01](../registry/attempts/OBJECT-LEDGER-PILOT-01.json). Read their outcomes and `retry_when` before running this task.
