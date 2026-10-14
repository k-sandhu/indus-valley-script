---
id: "Q-0024"
title: "Test whether identical texts with different animals cross sites more often"
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

Do identical texts on seals with different non-unicorn animals occur at different sites more often than identical texts on seals with the same animal?

# Why it matters

Prediction P2 of conjecture C-0003, which reads the seal animal as the holder's affiliation, tests whether a legend crosses affiliations.

# What is needed

Keep exact and variant-merged text definitions separate, use the object register we hold, and freeze a pair-weighting rule on the discovery half before confirmation. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0003-unicorn-affiliation.md](../conjectures/C-0003-unicorn-affiliation.md).

# How to decide

Apply C-0003 P2's one-sided permutation p below 0.05. Report every eligible pair, and stop if no supported same-animal comparison exists.

# Prior attempts

[SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json). Read its outcome and `retry_when` condition before running this task.
