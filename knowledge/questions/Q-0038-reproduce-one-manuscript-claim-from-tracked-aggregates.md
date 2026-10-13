---
id: "Q-0038"
title: "Reproduce one manuscript claim from tracked aggregates"
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

Can a contributor independently recover one Paper 001 headline comparison from its tracked aggregate outputs and recorded definitions?

# Why it matters

A short verification contribution can check the human entry page’s claims without requiring local corpus access.

# What is needed

Choose one aggregate claim, record the input hashes and recompute the displayed quantity. If a paired replay needs local audits, document that boundary and use the aggregate endpoint only. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [papers/001-artifact-aware-prediction/claim-evidence-map.md](../../papers/001-artifact-aware-prediction/claim-evidence-map.md); [papers/001-artifact-aware-prediction/methods.md](../../papers/001-artifact-aware-prediction/methods.md).

# How to decide

Match the source’s displayed value and denominator. Stop after the selected claim and report exactly which inputs and calculations were independently inspected.

# Prior attempts

[MARKOV-03](../registry/attempts/MARKOV-03.json). Read their outcomes and `retry_when` before running this task.
