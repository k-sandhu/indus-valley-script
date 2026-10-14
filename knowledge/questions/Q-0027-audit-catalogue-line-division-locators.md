---
id: "Q-0027"
title: "Check catalogue line divisions against the source plates"
status: "open"
area: "data"
kind: "metadata"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["LINE-BREAKS-SEGMENTATION-2026-10-12"]
related: ["F-0018"]
sources: ["experiments/2026-10-12-structure-first/REPORT.md", "knowledge/directions/context-data-plan.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Which saved line divisions have source plate references and reliable evidence of line order?

# Why it matters

A training set for boundaries needs layout labels others can inspect.

# What is needed

Review the multi-line faces we hold, their captions and orientation; keep numeral-only lines, wrapped text and spatially separate sign groups distinguishable. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [experiments/2026-10-12-structure-first/REPORT.md](../../experiments/2026-10-12-structure-first/REPORT.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Finish a fixed source block, accounting for every exclusion. Where line order is unresolved, keep both orders and leave the face out of any single-order reference set.

# Prior attempts

[LINE-BREAKS-SEGMENTATION-2026-10-12](../registry/attempts/LINE-BREAKS-SEGMENTATION-2026-10-12.json). Read its outcome and `retry_when` condition before running this task.
