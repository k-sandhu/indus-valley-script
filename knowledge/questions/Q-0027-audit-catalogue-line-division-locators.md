---
id: "Q-0027"
title: "Audit catalogue line-division locators"
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

Which saved line divisions have source plate coordinates and reliable line-order evidence?

# Why it matters

A boundary training set needs independently inspectable layout labels.

# What is needed

Review held multi-line faces, source captions and orientation; keep numeral-only lines, wrapped text and spatially separate groups distinguishable. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [experiments/2026-10-12-structure-first/REPORT.md](../../experiments/2026-10-12-structure-first/REPORT.md); [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md).

# How to decide

Finish a fixed source block with all exclusions accounted for. Retain both line orders when unresolved and exclude them from a one-order gold set.

# Prior attempts

[LINE-BREAKS-SEGMENTATION-2026-10-12](../registry/attempts/LINE-BREAKS-SEGMENTATION-2026-10-12.json). Read their outcomes and `retry_when` before running this task.
