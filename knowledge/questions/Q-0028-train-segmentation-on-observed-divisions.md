---
id: "Q-0028"
title: "Train segmentation on observed divisions"
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

Does a segmenter trained on catalogue divisions improve boundary prediction on a reserved physical-family block?

# Why it matters

Unsupervised rehearsal gives limited average accuracy; recorded divisions provide positive boundary evidence.

# What is needed

Use reviewed line layouts and spacing measurements already held. Keep positive boundaries distinct from positions without boundary labels and split complete object families. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [experiments/2026-10-12-structure-first/REPORT.md](../../experiments/2026-10-12-structure-first/REPORT.md).

# How to decide

Freeze a held-out boundary-recall endpoint and any independently justified precision labels. Pass requires improvement over the saved segmenter with stated coverage; stop if only positive labels permit no claimed precision estimate.

# Prior attempts

[LINE-BREAKS-SEGMENTATION-2026-10-12](../registry/attempts/LINE-BREAKS-SEGMENTATION-2026-10-12.json); [REHEARSAL-SEGMENTATION-2026-10-12](../registry/attempts/REHEARSAL-SEGMENTATION-2026-10-12.json). Read their outcomes and `retry_when` before running this task.
