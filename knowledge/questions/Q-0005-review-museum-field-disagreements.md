---
id: "Q-0005"
title: "Explain disagreements between museum records and the corpus"
status: "open"
area: "data"
kind: "verification"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["EVIDENCE-CENSUS-COLLECTIONS-01", "EVIDENCE-CENSUS-SYNTHESIS-01"]
related: ["F-0008"]
sources: ["knowledge/directions/context-data-plan.md", "experiments/2026-10-06-evidence-census/synthesis/join-summary.json"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Among the museum-to-corpus links we hold, which flagged disagreements in site, material, dimensions and sign count come from aliases, terminology or conflicting observations in the sources?

# Why it matters

A confirmed identifier link does not guarantee that the two catalogues describe the object consistently.

# What is needed

Read the saved field-by-field comparisons and their source records. Keep museum and corpus statements apart, each with its own reference, and classify the reason for each disagreement. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [experiments/2026-10-06-evidence-census/synthesis/join-summary.json](../../experiments/2026-10-06-evidence-census/synthesis/join-summary.json).

# How to decide

Review every flagged disagreement in the chosen comparison block. Accept a correction only with source support; keep unresolved conflicts and set aside incomparable measurements.

# Prior attempts

[EVIDENCE-CENSUS-COLLECTIONS-01](../registry/attempts/EVIDENCE-CENSUS-COLLECTIONS-01.json); [EVIDENCE-CENSUS-SYNTHESIS-01](../registry/attempts/EVIDENCE-CENSUS-SYNTHESIS-01.json). Read their outcomes and `retry_when` conditions before running this task.
