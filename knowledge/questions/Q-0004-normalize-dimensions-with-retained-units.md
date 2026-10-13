---
id: "Q-0004"
title: "Normalize dimensions with retained units"
status: "open"
area: "data"
kind: "metadata"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["OBJECT-LEDGER-PILOT-01", "SIGN-CONTEXT-SEALS-01"]
related: []
sources: ["knowledge/directions/context-data-plan.md", "knowledge/directions/research-roadmap.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can the dimension strings in an existing reviewed object block be normalized without losing units, axes, approximations or conflicting measurements?

# Why it matters

Seal-area tests require comparable measurements and a source for each conversion.

# What is needed

Use held source tables and pilot assertions. Record raw text locally, normalized values, axis meanings, units, source coordinates and conversion rules; publish aggregate checks and permitted metadata. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md).

# How to decide

Stop at the chosen block. Every conversion must be reversible from its recorded rule; keep uncertain axes and unitless values outside the area endpoint. Report the coverage change.

# Prior attempts

[OBJECT-LEDGER-PILOT-01](../registry/attempts/OBJECT-LEDGER-PILOT-01.json); [SIGN-CONTEXT-SEALS-01](../registry/attempts/SIGN-CONTEXT-SEALS-01.json). Read their outcomes and `retry_when` before running this task.
