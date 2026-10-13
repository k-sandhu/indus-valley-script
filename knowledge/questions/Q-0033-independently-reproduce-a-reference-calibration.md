---
id: "Q-0033"
title: "Independently reproduce a reference calibration"
status: "open"
area: "methods"
kind: "verification"
priority: 3
data_access: "none-needed"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["NULL-08", "NULL-05"]
related: ["F-0031", "F-0032"]
sources: ["papers/002-conditional-reference-laws/methods.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can a new contributor independently reproduce a selected exact or generated reference-law calculation from tracked inputs?

# Why it matters

Verification by someone other than the author can raise a submitted result to reproduced.

# What is needed

Choose the bounded calculation from Paper 002’s methods, record environment and helper hashes, use a fresh endpoint and implement the statistic or finite enumeration independently where feasible. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [papers/002-conditional-reference-laws/methods.md](../../papers/002-conditional-reference-laws/methods.md).

# How to decide

Match the recorded exact counts or declared stochastic replay under its seeds. Preserve discrepancies and investigate them without replacing the old result; report the independence and reused code.

# Prior attempts

[NULL-08](../registry/attempts/NULL-08.json); [NULL-05](../registry/attempts/NULL-05.json). Read their outcomes and `retry_when` before running this task.
