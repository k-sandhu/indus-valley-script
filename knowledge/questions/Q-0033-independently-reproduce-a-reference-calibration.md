---
id: "Q-0033"
title: "Reproduce one of Paper 002's chance-comparison calibrations"
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

Can a new contributor independently reproduce one of Paper 002's reference-law calculations, exact or simulated, from tracked inputs? A reference is the set of shuffled corpora an observed score is ranked against; its law says which shuffles are drawn and how often.

# Why it matters

Verification by someone other than the author can raise a submitted result to the status reproduced.

# What is needed

Choose a bounded calculation from Paper 002's methods, record the environment and helper-code hashes, write to a new result directory and implement the statistic or finite enumeration independently where feasible. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [papers/002-conditional-reference-laws/methods.md](../../papers/002-conditional-reference-laws/methods.md).

# How to decide

Match the recorded exact counts or the declared simulation replay under its seeds. Keep discrepancies and investigate them without replacing the old result; report how independent the work was and what code was reused.

# Prior attempts

[NULL-08](../registry/attempts/NULL-08.json); [NULL-05](../registry/attempts/NULL-05.json). Read their outcomes and `retry_when` conditions before running this task.
