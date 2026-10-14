---
id: "Q-0004"
title: "Convert object dimensions without losing units or source wording"
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

Can the dimension strings of an already reviewed block of objects be converted to standard values without losing units, axes, approximations or conflicting measurements?

# Why it matters

Seal-area tests need comparable measurements and a source for each conversion.

# What is needed

Use the source tables we hold and the object-ledger pilot's statements. Keep the raw text locally with converted values, axis meanings, units, page or plate references and conversion rules; publish aggregate checks and the metadata we may share. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md).

# How to decide

Stop at the chosen block. Every conversion must be reversible from its recorded rule; keep uncertain axes and unitless values out of the seal-area measure. Report the change in coverage.

# Prior attempts

[OBJECT-LEDGER-PILOT-01](../registry/attempts/OBJECT-LEDGER-PILOT-01.json); [SIGN-CONTEXT-SEALS-01](../registry/attempts/SIGN-CONTEXT-SEALS-01.json). Read their outcomes and `retry_when` conditions before running this task.
