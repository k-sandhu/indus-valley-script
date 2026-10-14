---
id: "Q-0021"
title: "Test whether the stroke tiers before sign W700 are stable over time"
status: "open"
area: "tablets"
kind: "analysis"
priority: 2
data_access: "local-only"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["NUMERAL-BEHAVIOUR-2026-10-12", "ADMINISTRATIVE-BUNDLES-2026-10-11"]
related: ["C-0005", "F-0024"]
sources: ["knowledge/conjectures/C-0005-tablet-tiers.md", "knowledge/directions/context-data-plan.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Are the proportions of two, three and four tall strokes before sign W700 stable across the Harappa periods the sources support?

# Why it matters

This is the standard-tier prediction of conjecture C-0005, which reads these counts as tiers of a standard unit.

# What is needed

Audit period labels and whole-object dependence first. Use the two-stage design (free exploration on a discovery half, then one frozen test on the confirmation half), and freeze exclusions, power and the period comparison before confirmation. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0005-tablet-tiers.md](../conjectures/C-0005-tablet-tiers.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Use C-0005 P1's rule and report the power to detect the prespecified shift. A strong period trend lowers the credence; sparse labels or wide uncertainty leave stability undecided.

# Prior attempts

[NUMERAL-BEHAVIOUR-2026-10-12](../registry/attempts/NUMERAL-BEHAVIOUR-2026-10-12.json); [ADMINISTRATIVE-BUNDLES-2026-10-11](../registry/attempts/ADMINISTRATIVE-BUNDLES-2026-10-11.json). Read their outcomes and `retry_when` conditions before running this task.
