---
id: "Q-0023"
title: "Test rare-animal site concentration"
status: "open"
area: "seals"
kind: "analysis"
priority: 2
data_access: "local-only"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["SIGN-CONTEXT-SEALS-01", "SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12"]
related: ["C-0003", "F-0029"]
sources: ["knowledge/conjectures/C-0003-unicorn-affiliation.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Do rarer field animals concentrate at fewer sites than their counts and site totals predict, while unicorns follow site totals?

# Why it matters

This is the affiliation conjecture’s P1 and combined kill test.

# What is needed

Use square seals with known animal at sites meeting the card’s sample threshold, source-audit motifs and follow the two-stage design. Freeze HHI and the permutation strata. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0003-unicorn-affiliation.md](../conjectures/C-0003-unicorn-affiliation.md).

# How to decide

Apply C-0003 P1’s 95th-percentile and central-95% rules. Failure of both parts activates its kill condition; insufficient rare-animal counts stop the shot as underpowered.

# Prior attempts

[SIGN-CONTEXT-SEALS-01](../registry/attempts/SIGN-CONTEXT-SEALS-01.json); [SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json). Read their outcomes and `retry_when` before running this task.
