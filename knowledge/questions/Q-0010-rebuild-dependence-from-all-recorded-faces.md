---
id: "Q-0010"
title: "Rebuild dependence from all recorded faces"
status: "open"
area: "corpus"
kind: "verification"
priority: 2
data_access: "local-only"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["ROOT-03", "CONTEXT-01"]
related: []
sources: ["knowledge/directions/context-data-plan.md", "knowledge/directions/research-roadmap.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Do existing analysis splits preserve aliases and repeated whole texts when grouping uses the full observational register, including excluded faces?

# Why it matters

An excluded short or damaged face can connect an otherwise eligible object to a training object.

# What is needed

Use confirmed physical identity separately from repeated-text dependence. Reconstruct group closure before eligibility filtering and compare it with a chosen saved split. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md).

# How to decide

Pass only if no declared dependence component crosses its evaluation boundary. Report every changed group and preserve the old endpoint; any leakage requires a separately dated rerun.

# Prior attempts

[ROOT-03](../registry/attempts/ROOT-03.json); [CONTEXT-01](../registry/attempts/CONTEXT-01.json). Read their outcomes and `retry_when` before running this task.
