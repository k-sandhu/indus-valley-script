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

Can measured impression dimensions or carving features tell the seal that stamped the Lothal sealings apart from M-895?

# Why it matters

If a different seal carried the same legend, the competing explanations of how the text moved change.

# What is needed

Use scaled views we hold, bounds on impression distortion and a feature protocol frozen before comparing. Keep the uncertainty from missing scales and damaged edges. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0004-m895-office-text.md](../conjectures/C-0004-m895-office-text.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Use C-0004 P3: width differs by more than 10% or the carved forms differ. If scale or contact distortion makes the test impossible, stop and record the observation gap.

# Prior attempts

[SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json). Read its outcome and `retry_when` condition before running this task.

# Outcome

13 October 2026: the [plate check](../../experiments/2026-10-13-plate-checks/README.md) found an impressing seal of the same face width (23.4 against 23.3 mm) with different sign spacing and carving (two AI readers; specialist confirmation pending).
