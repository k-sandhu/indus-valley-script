---
id: "Q-0034"
title: "Repair retained mixture search misses"
status: "open"
area: "methods"
kind: "analysis"
priority: 3
data_access: "none-needed"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["CRYPTO-10", "CRYPTO-11"]
related: []
sources: ["knowledge/directions/research-roadmap.md", "papers/004-reference-model-selection/methods.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can a different optimizer close the retained mixture-map score gaps without changing the declared objective or supplied component count?

# Why it matters

Population identification and finite-sample search success are distinct measurements.

# What is needed

Use tracked generated worlds or their lossless package, the exact truth scores and failed-map diagnostics. Freeze the optimizer and budget before a fresh generated comparison. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md); [papers/004-reference-model-selection/methods.md](../../papers/004-reference-model-selection/methods.md).

# How to decide

Pass requires the declared search improvement on the frozen objective plus a fresh control grid. Stop if gains come only from tuning on the saved misses; retain tied objectives and wrong optima.

# Prior attempts

[CRYPTO-10](../registry/attempts/CRYPTO-10.json); [CRYPTO-11](../registry/attempts/CRYPTO-11.json). Read their outcomes and `retry_when` before running this task.
