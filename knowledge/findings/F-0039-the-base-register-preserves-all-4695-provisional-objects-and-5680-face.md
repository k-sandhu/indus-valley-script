---
id: "F-0039"
title: "The base register preserves all 4695 provisional objects and 5680 faces"
status_class: "exploratory"
area: "data"
date: "2026-10-22"
registry_ids: ["OBJECT-REGISTER-BUILD-01", "RESEARCH-LAUNCH-2026-10-22"]
evidence: ["experiments/2026-10-22-object-register/run-v2/coverage.json#/population", "experiments/2026-10-22-object-register/run-v2/coverage.json#/tables", "experiments/2026-10-22-object-register/run-v2/coverage.json#/exposure"]
population: "All 4,695 provisional Lipi families and 5,680 exported faces in register run-v2"
authors: [{"model": "GPT-6 family; exact backend identifier not exposed", "harness": "Codex desktop", "agent": "object-register worker"}]
---

# Finding

The base register preserves all 4,695 provisional objects and 5,680 exported faces, with 225,223 attributed assertions, 16,434 identifier rows and 11,993 measurement rows. All 4,695 objects retain unreviewed exposure status; zero are certified fresh.

# Evidence

- [experiments/2026-10-22-object-register/run-v2/coverage.json](../../experiments/2026-10-22-object-register/run-v2/coverage.json#/population), JSON Pointer `/population`.
- [experiments/2026-10-22-object-register/run-v2/coverage.json](../../experiments/2026-10-22-object-register/run-v2/coverage.json#/tables), JSON Pointer `/tables`.
- [experiments/2026-10-22-object-register/run-v2/coverage.json](../../experiments/2026-10-22-object-register/run-v2/coverage.json#/exposure), JSON Pointer `/exposure`.

# Scope

Families are provisional corpus identities. Source aliases do not merge them into adjudicated physical objects. The register preserves uncertain readings and excludes disputed cells from accepted fields. The [validation record](../../experiments/2026-10-22-object-register/VALIDATION.md) reports seven output files replaying byte for byte and 232,837 direct source-value comparisons with zero mismatches. The [coordinator's validation](../../experiments/2026-10-22-research-launch/VALIDATION.md) separately checks population and parent relationships. Those checks cover the stated source adapters and structural rules; physical identity and exposure review remain unfinished.
