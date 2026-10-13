---
id: "Q-0006"
title: "Check source coordinates in an object block"
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

Do the saved page, plate, figure and caption locators lead to the stated objects in one held source block?

# Why it matters

Reliable coordinates let another contributor inspect the same observation without repeating source discovery.

# What is needed

Use the original held edition and its hash. Distinguish printed pages from PDF pages and photograph identifiers from object identifiers. Read [DATA.md](../DATA.md) for the gaps this task depends on.

Sources: [knowledge/directions/context-data-plan.md](../directions/context-data-plan.md); [knowledge/directions/research-roadmap.md](../directions/research-roadmap.md).

# How to decide

Check every locator in a fixed block and record edition-specific corrections in a new ledger. Stop when each resolves or has a recorded access or identity failure.

# Prior attempts

[ARCH-01](../registry/attempts/ARCH-01.json); [ARCH-02](../registry/attempts/ARCH-02.json). Read their outcomes and `retry_when` before running this task.
