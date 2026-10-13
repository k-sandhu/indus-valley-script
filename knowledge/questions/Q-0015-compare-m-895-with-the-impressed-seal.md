---
id: "Q-0015"
title: "Compare M-895 with the impressed seal"
status: "done"
area: "seals"
kind: "analysis"
priority: 2
data_access: "local-only"
compute: "hours"
difficulty: "expert"
claimed_by: ""
claim_expires: ""
prior_attempts: ["SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12"]
related: ["C-0004"]
sources: ["knowledge/conjectures/C-0004-m895-office-text.md", "knowledge/directions/context-data-plan.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can measured impression dimensions or carving features distinguish the seal that made the Lothal group from M-895?

# Why it matters

A different die carrying the same legend would change the competing movement explanations.

# What is needed

Use held scaled views, impression distortion bounds and a feature protocol frozen before comparison. Retain missing scale and damaged-edge uncertainty. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0004-m895-office-text.md](../conjectures/C-0004-m895-office-text.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Use C-0004 P3: width differs by more than 10% or carved forms differ. If scale or contact distortion makes that test impossible, stop with an observation-gap record.

# Prior attempts

[SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json). Read their outcomes and `retry_when` before running this task.

# Outcome

13 October 2026: the [plate check](../../experiments/2026-10-13-plate-checks/README.md) found an impressing seal of the same face width (23.4 against 23.3 mm) with different sign spacing and carving (two AI readers; specialist confirmation pending).
