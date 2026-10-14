---
id: "Q-0029"
title: "Test stroke-number fixity with the preceding and the following sign"
status: "open"
area: "numerals"
kind: "analysis"
priority: 2
data_access: "local-only"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["NUMERAL-BEHAVIOUR-2026-10-12"]
related: ["F-0024", "F-0025"]
sources: ["experiments/2026-10-12-structure-first/REPORT.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Does stroke-value fixity survive stratification by site and period when both the preceding and the following sign are treated as the counted item?

# Why it matters

Direction changes which combinations appear near-fixed.

# What is needed

Retain the short–tall stroke distinction, objects with several faces, and the uncertainty in site and period. Freeze strata and comparisons before confirmation; keep the original result that treats the following sign as the item. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [experiments/2026-10-12-structure-first/REPORT.md](../../experiments/2026-10-12-structure-first/REPORT.md).

# How to decide

Report both directions under the same sample-size and unit controls. Drop strata with too little support; any interpretation must predict a new relation between objects beyond these conditional counts.

# Prior attempts

[NUMERAL-BEHAVIOUR-2026-10-12](../registry/attempts/NUMERAL-BEHAVIOUR-2026-10-12.json). Read its outcome and `retry_when` condition before running this task.
