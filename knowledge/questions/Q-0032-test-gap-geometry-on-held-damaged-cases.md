---
id: "Q-0032"
title: "Use gap width and traces to count lost signs in damaged texts"
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

On a newly reserved block of images we hold, can measured gap width and surviving traces improve prediction of how many signs are missing?

# Why it matters

Without physical evidence, the statistical count estimator did worse than always guessing one sign.

# What is needed

Before opening the independent counts that serve as answers, freeze rules for crop, scale, segmentation and physical span using the source images only. Keep acquisition separate from count outcomes. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md); [knowledge/directions/decipherment-readiness-2026-10-02.md](../directions/decipherment-readiness-2026-10-02.md).

# How to decide

A pass requires the declared improvement over always guessing one, matched to the case sampling, on cases with withheld answers. Stop where a gap has no clear edges or a count cannot be independently resolved.

# Prior attempts

[ROOT-08](../registry/attempts/ROOT-08.json); [ROOT-17](../registry/attempts/ROOT-17.json). Read their outcomes and `retry_when` conditions before running this task.
