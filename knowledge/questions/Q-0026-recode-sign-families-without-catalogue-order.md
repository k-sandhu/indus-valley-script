---
id: "Q-0026"
title: "Recode sign families without catalogue order"
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

Does an independent human coding of shuffled glyph sheets retain the family prediction gain?

# Why it matters

Both original coders saw the Wells order, which already groups graphics.

# What is needed

Prepare shuffled sheets without codes or counts, retain a keyed local crosswalk and specify adjudication before the human coding. Check low-agreement families and the twelve-stroke grid against held photographs. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [experiments/2026-10-12-structure-first/REPORT.md](../../experiments/2026-10-12-structure-first/REPORT.md).

# How to decide

Freeze the grouping before rerunning the recorded prediction assay. Compare it with both random groups and contiguous-order cuts. Stop interpretation where the feature cannot be seen reliably.

# Prior attempts

[SIGN-FAMILIES-2026-10-12](../registry/attempts/SIGN-FAMILIES-2026-10-12.json). Read their outcomes and `retry_when` before running this task.
