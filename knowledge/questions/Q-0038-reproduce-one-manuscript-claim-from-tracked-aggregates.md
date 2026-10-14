---
id: "Q-0038"
title: "Recompute one Paper 001 result from its tracked summary outputs"
status: "open"
area: "methods"
kind: "verification"
priority: 2
data_access: "none-needed"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["MARKOV-03"]
related: ["F-0002", "F-0003"]
sources: ["papers/001-artifact-aware-prediction/claim-evidence-map.md", "papers/001-artifact-aware-prediction/methods.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can a contributor independently recover one headline comparison of Paper 001 from its tracked summary outputs and recorded definitions?

# Why it matters

A short verification can check the claims on the project's front page without access to the local corpus.

# What is needed

Choose one summary claim, record the input hashes and recompute the displayed quantity. If a paired replay needs local audit files, document that limit and use the summary result only. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [papers/001-artifact-aware-prediction/claim-evidence-map.md](../../papers/001-artifact-aware-prediction/claim-evidence-map.md); [papers/001-artifact-aware-prediction/methods.md](../../papers/001-artifact-aware-prediction/methods.md).

# How to decide

Match the displayed value and denominator. Stop after the chosen claim and report exactly which inputs and calculations you inspected independently.

# Prior attempts

[MARKOV-03](../registry/attempts/MARKOV-03.json). Read its outcome and `retry_when` condition before running this task.
