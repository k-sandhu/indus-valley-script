---
id: "Q-0034"
title: "Find an optimizer that closes the recorded mixture-map search failures"
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

Some recorded mixture-model mapping failures returned maps scoring below the true map. Can a different optimizer close those score gaps without changing the declared objective or the supplied number of components?

# Why it matters

Whether the model identifies the true map in principle and whether a finite search finds it are separate measurements.

# What is needed

Use the tracked simulated systems or their lossless package, the true maps' exact scores and the failed-map diagnostics. Freeze the optimizer and budget before a fresh simulated comparison. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md); [papers/004-reference-model-selection/methods.md](../../papers/004-reference-model-selection/methods.md).

# How to decide

A pass requires the declared search improvement on the frozen objective plus a fresh control grid. Stop if gains come only from tuning on the saved failures; keep tied objectives and wrong optima on record.

# Prior attempts

[CRYPTO-10](../registry/attempts/CRYPTO-10.json); [CRYPTO-11](../registry/attempts/CRYPTO-11.json). Read their outcomes and `retry_when` conditions before running this task.
