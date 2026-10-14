---
id: "F-0011"
title: "Two codings of the signs into families agree closely"
status_class: "verified-computation"
area: "images"
date: "2026-10-12"
registry_ids: ["SIGN-FAMILIES-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/coder_agreement/ari_unweighted", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/coder_agreement/ari_token_weighted", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/coder_agreement/codes_compared"]
population: "577 attested codes coded by two instances of one model"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

Two codings of 577 sign codes into graphic families agreed with adjusted Rand index 0.884 unweighted and 0.975 weighted by occurrences; the index is one for identical groupings and near zero for chance.

# Evidence

- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/coder_agreement/ari_unweighted`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/coder_agreement/ari_token_weighted`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/coder_agreement/codes_compared`.

# Scope

Both coders were instances of the same AI model working from sheets in code order, so a human coding from shuffled sheets is the proposed independent check.
