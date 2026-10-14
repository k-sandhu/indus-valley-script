---
id: "Q-0023"
title: "Test whether rarer seal animals are concentrated at fewer sites"
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

Are rarer seal animals concentrated at fewer sites than their counts and the site totals predict, while unicorns follow the site totals?

# Why it matters

This is prediction P1 and the combined kill test of conjecture C-0003, which reads the animal as the holder's affiliation.

# What is needed

Use square seals with a known animal from sites meeting the card's sample threshold, check motifs against the sources and follow the two-stage design. Freeze the concentration index (Herfindahl–Hirschman, HHI) and the permutation strata. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0003-unicorn-affiliation.md](../conjectures/C-0003-unicorn-affiliation.md).

# How to decide

Apply C-0003 P1's 95th-percentile and central-95% rules. If both parts fail, the kill condition applies; too few rare animals stop the test as underpowered.

# Prior attempts

[SIGN-CONTEXT-SEALS-01](../registry/attempts/SIGN-CONTEXT-SEALS-01.json); [SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json). Read their outcomes and `retry_when` conditions before running this task.
