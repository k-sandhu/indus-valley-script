---
id: "Q-0009"
title: "Distinguish missing motif from no motif"
status: "open"
area: "data"
kind: "metadata"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["SIGN-CONTEXT-SEALS-01", "OBJECT-LEDGER-PILOT-01"]
related: ["F-0029"]
sources: ["knowledge/directions/context-data-plan.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can the held motif fields distinguish a catalogued absent motif from an unknown, damaged, unreported or unacquired motif?

# Why it matters

Text-only seals and missing animal observations have different roles in motif comparisons.

# What is needed

Inspect each placeholder type in the export and a fixed source sample. Retain the source’s label and a versioned mapping to value status and missingness reason. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Stop after all placeholder categories and the fixed sample have been reviewed. Kill any normalization that merges asserted absence with unknown observation.

# Prior attempts

[SIGN-CONTEXT-SEALS-01](../registry/attempts/SIGN-CONTEXT-SEALS-01.json); [OBJECT-LEDGER-PILOT-01](../registry/attempts/OBJECT-LEDGER-PILOT-01.json). Read their outcomes and `retry_when` before running this task.
