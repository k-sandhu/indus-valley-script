---
id: "Q-0028"
title: "Train a segmenter on the catalogue's line divisions"
status: "open"
area: "structure"
kind: "analysis"
priority: 2
data_access: "local-only"
compute: "hours"
difficulty: "standard"
claimed_by: ""
claim_expires: ""
prior_attempts: ["LINE-BREAKS-SEGMENTATION-2026-10-12", "REHEARSAL-SEGMENTATION-2026-10-12"]
related: ["F-0018", "F-0020"]
sources: ["experiments/2026-10-12-structure-first/REPORT.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Does a segmenter trained on catalogue line divisions predict boundaries better on a reserved block of object families?

# Why it matters

Unsupervised segmentation was only modestly accurate in the readable-script rehearsal, while recorded divisions are direct evidence of boundaries.

# What is needed

Use reviewed line layouts and spacing measurements we already hold. Keep known boundaries distinct from unlabelled positions, and split by whole object families. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [experiments/2026-10-12-structure-first/REPORT.md](../../experiments/2026-10-12-structure-first/REPORT.md).

# How to decide

Freeze a held-out boundary-recall measure and any independently justified precision labels. A pass requires improvement over the saved segmenter with coverage stated; with only boundary labels, claim no precision estimate.

# Prior attempts

[LINE-BREAKS-SEGMENTATION-2026-10-12](../registry/attempts/LINE-BREAKS-SEGMENTATION-2026-10-12.json); [REHEARSAL-SEGMENTATION-2026-10-12](../registry/attempts/REHEARSAL-SEGMENTATION-2026-10-12.json). Read their outcomes and `retry_when` conditions before running this task.
