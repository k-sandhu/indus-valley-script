---
id: "Q-0010"
title: "Check data splits using every recorded face, including excluded ones"
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

Do existing training and test splits keep an object's aliases and repeated whole texts together when grouping uses the full register of faces, including excluded ones?

# Why it matters

An excluded short or damaged face can link an otherwise eligible object to a training object.

# What is needed

Treat confirmed physical identity separately from shared-text dependence. Build the complete linked groups before eligibility filtering and compare them with a chosen saved split. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md).

# How to decide

Pass only if no linked group (dependence component) crosses the training–evaluation boundary. Report every changed group and keep the old result; any leakage needs a separately dated rerun.

# Prior attempts

[ROOT-03](../registry/attempts/ROOT-03.json); [CONTEXT-01](../registry/attempts/CONTEXT-01.json). Read their outcomes and `retry_when` conditions before running this task.
