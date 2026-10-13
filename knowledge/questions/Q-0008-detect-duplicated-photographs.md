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

Which held photographs or scan panels are repeated witnesses of the same image rather than additional object observations?

# Why it matters

Duplicate images can inflate apparent photographic coverage and independent annotation counts.

# What is needed

Hash the held files and compare candidate crops with source captions. Keep full-file and crop matches separate and publish hashes, identifiers and aggregate counts under the rights rules. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [research/literature/cisi1_counting_and_errata.md](../../research/literature/cisi1_counting_and_errata.md).

# How to decide

Exact hashes establish identical files; near matches require visible crop and caption confirmation. Stop after the declared source block and retain doubtful pairs as candidates.

# Prior attempts

[ROOT-19](../registry/attempts/ROOT-19.json); [HARP-LOTHAL-SOURCE-02](../registry/attempts/HARP-LOTHAL-SOURCE-02.json). Read their outcomes and `retry_when` before running this task.
