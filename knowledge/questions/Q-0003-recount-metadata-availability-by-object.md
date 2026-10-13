---
id: "Q-0003"
title: "Recount metadata availability by object"
status: "done"
area: "data"
kind: "metadata"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["CONTEXT-01", "DATASET-LANDSCAPE-01"]
related: ["F-0009"]
sources: ["knowledge/directions/context-data-plan.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

How do field availability and conflicts change when the held export’s face rows are collapsed to provisional object families?

# Why it matters

Repeated face metadata can overstate coverage, and placeholder strings previously inflated depth availability.

# What is needed

Inventory the actual fields and raw placeholder values; preserve observed, catalogued, inferred, unknown, conflicting and not-applicable states. Report row and object denominators. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Account for every row and provisional family in the pinned input. A field is present only under a declared rule; independently replay the counts and inspect every uncommon placeholder.

# Prior attempts

[CONTEXT-01](../registry/attempts/CONTEXT-01.json); [DATASET-LANDSCAPE-01](../registry/attempts/DATASET-LANDSCAPE-01.json). Read their outcomes and `retry_when` before running this task.

# Outcome

13 October 2026: the [data inventory](../../experiments/2026-10-12-data-inventory/README.md) recounted field coverage per object and per face, by object type and site ([summary.json](../../experiments/2026-10-12-data-inventory/run-2026-10-12/summary.json)); headline figures are in [DATA.md](../DATA.md) section 2.
