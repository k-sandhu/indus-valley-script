---
id: "Q-0024"
title: "Test different-animal cross-site pairs"
status: "open"
area: "seals"
kind: "analysis"
priority: 2
data_access: "local-only"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12"]
related: ["C-0003", "F-0029"]
sources: ["knowledge/conjectures/C-0003-unicorn-affiliation.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Do identical texts on different non-unicorn animals cross sites more often than identical texts on the same animal?

# Why it matters

C-0003 P2 tests whether a legend transfers across affiliations.

# What is needed

Keep exact and variant-merged text definitions separate, use the held object registry and freeze a pair-weighting rule on discovery before confirmation. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0003-unicorn-affiliation.md](../conjectures/C-0003-unicorn-affiliation.md).

# How to decide

Apply C-0003 P2’s one-sided permutation p below 0.05. Report every eligible pair and stop if there is no supported same-animal comparator.

# Prior attempts

[SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json). Read their outcomes and `retry_when` before running this task.
