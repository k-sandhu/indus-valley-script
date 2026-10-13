---
id: "Q-0005"
title: "Review museum field disagreements"
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

Which flagged site, material, dimension and sign-count disagreements in the held museum joins reflect aliases, terminology or conflicting source observations?

# Why it matters

A confirmed identifier join does not guarantee that the two catalogues describe an object consistently.

# What is needed

Read the saved paired-field comparisons and source witnesses. Keep museum and corpus assertions with independent locators and classify the reason for each disagreement. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [experiments/2026-10-06-evidence-census/synthesis/join-summary.json](../../experiments/2026-10-06-evidence-census/synthesis/join-summary.json).

# How to decide

Review all flagged disagreements in the chosen comparison block. Accept a correction only with a source witness; retain unresolved conflicts and separate incomparable measurements.

# Prior attempts

[EVIDENCE-CENSUS-COLLECTIONS-01](../registry/attempts/EVIDENCE-CENSUS-COLLECTIONS-01.json); [EVIDENCE-CENSUS-SYNTHESIS-01](../registry/attempts/EVIDENCE-CENSUS-SYNTHESIS-01.json). Read their outcomes and `retry_when` before running this task.
