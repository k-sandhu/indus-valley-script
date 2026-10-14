---
id: "Q-0001"
title: "Link 30 objects across catalogue, excavation and museum numbers"
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

Can 30 objects from sources we hold locally be linked across catalogue, excavation and museum numbers without forcing uncertain matches?

# Why it matters

Knowing which records are one physical object shows which faces belong together and which observations are independent.

# What is needed

Use the roadmap's 30-object observation block and the images and registers we hold. In a new package, keep each identifier's source numbering, all aliases, page or plate references, competing matches and a ledger of disagreements. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Stop after the 30 objects. Every link asserting that two records are one object must rest on an accession number, excavation number or plate; keep unsupported links as possible matches. Report resolved, conflicting and unresolved counts.

# Prior attempts

[ROOT-19](../registry/attempts/ROOT-19.json); [OBJECT-LEDGER-PILOT-01](../registry/attempts/OBJECT-LEDGER-PILOT-01.json). Read their outcomes and `retry_when` conditions before running this task.
