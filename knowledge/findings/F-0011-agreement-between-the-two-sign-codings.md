---
id: "F-0011"
title: "Agreement between the two sign codings"
status_class: "verified-computation"
area: "images"
date: "2026-10-12"
registry_ids: ["SIGN-FAMILIES-2026-10-12"]
evidence: ["experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/coder_agreement/ari_unweighted", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/coder_agreement/ari_token_weighted", "experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json#/coder_agreement/codes_compared"]
population: "577 attested codes coded by two instances of one model"
authors: ["Codex CLI (GPT-6.1-Sol)"]
---

# Finding

The two codings had adjusted Rand agreement 0.884 unweighted and 0.975 token-weighted across 577 codes.

# Evidence

- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/coder_agreement/ari_unweighted`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/coder_agreement/ari_token_weighted`.
- [experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json](../../experiments/2026-10-12-structure-first/step1-signs/run-2026-10-12/summary.json), JSON field `/coder_agreement/codes_compared`.

# Scope

The statistic compares assignments to graphic families, with token weighting favoring common codes. Both coders worked from code-ordered sheets, so a human coding from shuffled sheets is the proposed independent check.
