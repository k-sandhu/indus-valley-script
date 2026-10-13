---
id: "Q-0022"
title: "Test same-tier find-context clustering"
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

Within a fixed descriptor class, do Harappa tablets of the same tier share find contexts more than tablets of different tiers?

# Why it matters

The comparison can distinguish issued series from arbitrary stroke assignments.

# What is needed

Use primary-joined find units, retain secondary deposits and unknown contexts, and freeze the comparison on the discovery half under the conjecture design. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0005-tablet-tiers.md](../conjectures/C-0005-tablet-tiers.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Use C-0005 P2’s one-sided permutation p below 0.05. Stop if context variation is absent or one dependence component exhausts the population.

# Prior attempts

[ADMINISTRATIVE-BUNDLES-2026-10-11](../registry/attempts/ADMINISTRATIVE-BUNDLES-2026-10-11.json). Read their outcomes and `retry_when` before running this task.
