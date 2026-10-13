---
id: "Q-0002"
title: "Audit completeness of object faces"
status: "open"
area: "data"
kind: "metadata"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["CONTEXT-01", "ARCH-01"]
related: ["F-0009"]
sources: ["knowledge/directions/context-data-plan.md", "knowledge/directions/decipherment-readiness-2026-10-02.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

Which objects in a fixed held-source block have all recorded faces represented, including plain and iconographic surfaces?

# Why it matters

A complete text-bearing export can still omit faces needed to test an object’s operation.

# What is needed

Compare object records with source plate captions and face drawings. Keep surface IDs, missingness reasons, orientation and line layout separate from normalized text rows. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [knowledge/directions/decipherment-readiness-2026-10-02.md](../directions/decipherment-readiness-2026-10-02.md).

# How to decide

Finish a frozen block and account for every source-captioned face. Mark completeness unknown where the publication does not enumerate sides. Do not infer a missing face from a missing text row alone.

# Prior attempts

[CONTEXT-01](../registry/attempts/CONTEXT-01.json); [ARCH-01](../registry/attempts/ARCH-01.json). Read their outcomes and `retry_when` before running this task.
