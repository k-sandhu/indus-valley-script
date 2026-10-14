---
id: "Q-0008"
title: "Detect duplicated photographs"
status: "open"
area: "images"
kind: "tooling"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["ROOT-19", "HARP-LOTHAL-SOURCE-02"]
related: []
sources: ["knowledge/directions/context-data-plan.md", "research/literature/cisi1_counting_and_errata.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Which photographs or scan panels we hold are repeat copies of one image rather than further views of an object?

# Why it matters

Duplicate images can inflate apparent photographic coverage and independent annotation counts.

# What is needed

Hash the files and compare candidate crops with source captions. Keep whole-file and crop matches separate, and publish hashes, identifiers and aggregate counts as the rights rules allow. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [research/literature/cisi1_counting_and_errata.md](../../research/literature/cisi1_counting_and_errata.md).

# How to decide

Identical hashes establish identical files; near matches need a visual check of crop and caption. Stop after the declared source block and keep doubtful pairs as candidates.

# Prior attempts

[ROOT-19](../registry/attempts/ROOT-19.json); [HARP-LOTHAL-SOURCE-02](../registry/attempts/HARP-LOTHAL-SOURCE-02.json). Read their outcomes and `retry_when` conditions before running this task.
