---
id: "Q-0013"
title: "Verify the Lothal and M-895 text match"
status: "done"
area: "seals"
kind: "verification"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "expert"
claimed_by: ""
claim_expires: ""
prior_attempts: ["SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12"]
related: ["C-0004", "F-0030"]
sources: ["knowledge/conjectures/C-0004-m895-office-text.md", "knowledge/directions/what-12-october-established.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Do the CISI plates we hold show the same four signs in the same order on the Lothal sealings L-161 to L-170 and the Mohenjo-daro seal M-895?

# Why it matters

This is the cheapest direct test that could kill conjecture C-0004, which reads the text as an office title.

# What is needed

Record every photographed impression, its damage and orientation, alternative fine sign forms and plate references. Have an independent reader inspect the same images without being told the proposed reading. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0004-m895-office-text.md](../conjectures/C-0004-m895-office-text.md); [knowledge/directions/what-12-october-established.md](../directions/what-12-october-established.md).

# How to decide

Use C-0004 P1: all four signs agree. A confirmed mismatch kills that prediction; an unreadable sign leaves it unresolved. Do not fill a damaged sign from the catalogue match.

# Prior attempts

[SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json). Read its outcome and `retry_when` condition before running this task.

# Outcome

13 October 2026: the [plate check](../../experiments/2026-10-13-plate-checks/README.md) found the same four signs in the same order on M-895 and every readable Lothal sealing (two AI readers; specialist confirmation pending).
