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

Do the held CISI plates confirm the same four signs in the same order on L-161 to L-170 and M-895?

# Why it matters

This is the cheapest direct kill test for the office-text conjecture.

# What is needed

Record all photographed impressions, damage, orientation, fine-form alternatives and source coordinates. Have an independent reader inspect the same images without the proposed reading. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/conjectures/C-0004-m895-office-text.md](../conjectures/C-0004-m895-office-text.md); [knowledge/directions/what-12-october-established.md](../directions/what-12-october-established.md).

# How to decide

Use C-0004 P1: all four signs agree. A confirmed mismatch kills that prediction; an unreadable sign leaves it unresolved. Do not fill a damaged sign from the catalogue match.

# Prior attempts

[SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12](../registry/attempts/SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12.json). Read their outcomes and `retry_when` before running this task.

# Outcome

13 October 2026: the [plate check](../../experiments/2026-10-13-plate-checks/README.md) found the same four signs in the same order on M-895 and every readable Lothal sealing (two AI readers; specialist confirmation pending).
