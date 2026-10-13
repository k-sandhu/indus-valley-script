---
id: "Q-0032"
title: "Test gap geometry on held damaged cases"
status: "open"
area: "images"
kind: "analysis"
priority: 2
data_access: "local-only"
compute: "days"
difficulty: "expert"
claimed_by: ""
claim_expires: ""
prior_attempts: ["ROOT-08", "ROOT-17"]
related: ["F-0005"]
sources: ["knowledge/directions/research-roadmap.md", "knowledge/directions/decipherment-readiness-2026-10-02.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Can measured gap width and surviving traces improve missing-count prediction on a newly reserved block of held images?

# Why it matters

The statistical count estimator lost to constant one without physical geometry.

# What is needed

Freeze source-only crop, scale, segmentation and physical span rules before independent count references are opened. Keep acquisition and count outcomes separate. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md); [knowledge/directions/decipherment-readiness-2026-10-02.md](../directions/decipherment-readiness-2026-10-02.md).

# How to decide

Pass requires the declared improvement over a sampling-matched constant control on reference-withheld cases. Stop when gap boundaries are unbounded or a count cannot be independently resolved.

# Prior attempts

[ROOT-08](../registry/attempts/ROOT-08.json); [ROOT-17](../registry/attempts/ROOT-17.json). Read their outcomes and `retry_when` before running this task.
