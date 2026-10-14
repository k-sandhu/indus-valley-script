---
id: "Q-0006"
title: "Check that page and plate references lead to the right objects"
status: "open"
area: "data"
kind: "verification"
priority: 1
data_access: "local-only"
compute: "hours"
difficulty: "starter"
claimed_by: ""
claim_expires: ""
prior_attempts: ["ARCH-01", "ARCH-02"]
related: []
sources: ["knowledge/directions/context-data-plan.md", "knowledge/directions/research-roadmap.md"]
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Question

In one block of sources we hold, do the saved page, plate, figure and caption references lead to the stated objects?

# Why it matters

Reliable references let another contributor inspect the same observation without searching the sources again.

# What is needed

Use the original edition we hold and its file hash. Distinguish printed pages from PDF pages, and photograph numbers from object numbers. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md).

# How to decide

Check every reference in a fixed block and record edition-specific corrections in a new ledger. Stop when each resolves or has a recorded failure of access or identification.

# Prior attempts

[ARCH-01](../registry/attempts/ARCH-01.json); [ARCH-02](../registry/attempts/ARCH-02.json). Read their outcomes and `retry_when` conditions before running this task.
