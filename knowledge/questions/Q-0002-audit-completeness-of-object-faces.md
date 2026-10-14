---
id: "Q-0002"
title: "Check that every recorded face of each object is present"
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

In a fixed block of objects from sources we hold, which objects have every recorded face present, including uninscribed faces and faces with images?

# Why it matters

An export can include every text-bearing face yet omit faces needed to study how an object was used.

# What is needed

Compare object records with source plate captions and face drawings. Keep surface IDs, reasons a face is missing, orientation and line layout separate from the normalized text rows. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [knowledge/directions/decipherment-readiness-2026-10-02.md](../directions/decipherment-readiness-2026-10-02.md).

# How to decide

Finish a fixed block and account for every face named in a source caption. Mark completeness unknown where the publication does not list an object's sides. A missing text row alone does not show a missing face.

# Prior attempts

[CONTEXT-01](../registry/attempts/CONTEXT-01.json); [ARCH-01](../registry/attempts/ARCH-01.json). Read their outcomes and `retry_when` conditions before running this task.
