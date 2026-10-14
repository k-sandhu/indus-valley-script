---
id: "Q-0003"
title: "Count metadata coverage per object as well as per face"
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

How do field availability and conflicts change when the export's face rows are grouped into provisional objects (faces the export numbers as one object, with physical identity unchecked)?

# Why it matters

Metadata repeated on every face can overstate coverage, and placeholder strings once inflated the count of objects with a depth.

# What is needed

List the fields that occur and their raw placeholder values; keep the states observed, catalogued, inferred, unknown, conflicting and not applicable apart. Report row and object denominators. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Account for every row and provisional object in the fixed input. Count a field as present only under a declared rule; have the counts replayed independently and inspect every uncommon placeholder.

# Prior attempts

[CONTEXT-01](../registry/attempts/CONTEXT-01.json); [DATASET-LANDSCAPE-01](../registry/attempts/DATASET-LANDSCAPE-01.json). Read their outcomes and `retry_when` conditions before running this task.

# Outcome

13 October 2026: the [data inventory](../../experiments/2026-10-12-data-inventory/README.md) recounted field coverage per object and per face, by object type and site ([summary.json](../../experiments/2026-10-12-data-inventory/run-2026-10-12/summary.json)); headline figures are in [DATA.md](../DATA.md) section 2.
