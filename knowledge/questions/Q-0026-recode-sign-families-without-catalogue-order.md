---
id: "Q-0026"
title: "Recode sign families from sheets in shuffled order"
status: "open"
area: "images"
kind: "verification"
priority: 2
data_access: "local-only"
compute: "days"
difficulty: "expert"
claimed_by: ""
claim_expires: ""
prior_attempts: ["SIGN-FAMILIES-2026-10-12"]
related: ["F-0010", "F-0011"]
sources: ["experiments/2026-10-12-structure-first/REPORT.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Does an independent human coding of glyph sheets in shuffled order keep the family prediction gain?

# Why it matters

Both original coders saw the signs in Wells's catalogue order, which already groups similar shapes.

# What is needed

Prepare shuffled sheets without codes or counts, keep a local key to the codes and specify how disagreements are settled before coding. Check low-agreement families and the twelve-stroke grid against photographs we hold. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [experiments/2026-10-12-structure-first/REPORT.md](../../experiments/2026-10-12-structure-first/REPORT.md).

# How to decide

Freeze the grouping before rerunning the recorded prediction test. Compare it with random groupings and with contiguous cuts of the Wells order. Do not interpret features that cannot be seen reliably.

# Prior attempts

[SIGN-FAMILIES-2026-10-12](../registry/attempts/SIGN-FAMILIES-2026-10-12.json). Read its outcome and `retry_when` condition before running this task.
