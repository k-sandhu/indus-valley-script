---
id: "Q-0009"
title: "Distinguish a missing motif record from a seal with no motif"
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

Can the motif fields we hold distinguish a catalogued absence of motif from a motif that is unknown, damaged, unreported or not acquired?

# Why it matters

Seals bearing only text and seals whose animal was not observed play different roles in motif comparisons.

# What is needed

Inspect each placeholder type in the export and in a fixed source sample. Keep the source's label and a versioned mapping to a value status and a reason for the missing value. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Stop once every placeholder category and the fixed sample are reviewed. Reject any normalization that merges a recorded absence with an unknown observation.

# Prior attempts

[SIGN-CONTEXT-SEALS-01](../registry/attempts/SIGN-CONTEXT-SEALS-01.json); [OBJECT-LEDGER-PILOT-01](../registry/attempts/OBJECT-LEDGER-PILOT-01.json). Read their outcomes and `retry_when` conditions before running this task.
