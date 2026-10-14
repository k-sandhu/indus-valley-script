---
id: "Q-0022"
title: "Test whether tablets of the same tier were found together"
status: "open"
area: "tablets"
kind: "analysis"
priority: 2
data_access: "local-only"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["ADMINISTRATIVE-BUNDLES-2026-10-11"]
related: ["C-0005"]
sources: ["knowledge/conjectures/C-0005-tablet-tiers.md", "knowledge/directions/context-data-plan.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Among Harappa tablets sharing a descriptor (the face naming what the tablet is for), are tablets of the same tier found together more often than tablets of different tiers?

# Why it matters

The comparison can separate tablets issued in series from arbitrary stroke assignments.

# What is needed

Use find units joined to primary records, keep secondary deposits and unknown contexts, and freeze the comparison on the discovery half under the conjecture's two-stage design. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0005-tablet-tiers.md](../conjectures/C-0005-tablet-tiers.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Use C-0005 P2: one-sided permutation p below 0.05. Stop if contexts do not vary or one linked group makes up the whole population.

# Prior attempts

[ADMINISTRATIVE-BUNDLES-2026-10-11](../registry/attempts/ADMINISTRATIVE-BUNDLES-2026-10-11.json). Read its outcome and `retry_when` condition before running this task.
