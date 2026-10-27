---
id: "F-0047"
title: "Fourteen catalogue-view relations recovered from existing image assets"
status_class: "source-review"
area: "images"
date: "2026-10-26"
registry_ids: ["IMAGE-RECOVERY-2026-10-26", "OBJECT-PILOT-REVIEW-2026-10-26"]
evidence: ["experiments/2026-10-26-image-recovery/aggregate-v2.json#/new_asset_catalogue_view_joins", "experiments/2026-10-26-image-recovery/aggregate-v2.json#/newly_available_pilot_photographs", "experiments/2026-10-26-object-pilot-review/REPORT-v2.md#image-evidence"]
population: "Twenty-four inspected assets and twenty source pages, compared with the 13 October image-files.csv assignments"
authors: [{"model": "gpt-6.1-sol", "harness": "Codex collaboration"}]
---

# Finding

The image review supports fourteen new asset-to-catalogue view relations across thirteen existing assets and twelve catalogue keys. L-163 and L-207 gain their first keys in the 13 October image-file index. The L-163 A and C photographs were already held in source-page records, so the pilot gains zero newly available photographs.

# Evidence

- [experiments/2026-10-26-image-recovery/aggregate-v2.json](../../experiments/2026-10-26-image-recovery/aggregate-v2.json#/new_asset_catalogue_view_joins), JSON Pointer `/new_asset_catalogue_view_joins`.
- [experiments/2026-10-26-image-recovery/aggregate-v2.json](../../experiments/2026-10-26-image-recovery/aggregate-v2.json#/newly_available_pilot_photographs), JSON Pointer `/newly_available_pilot_photographs`.
- [experiments/2026-10-26-object-pilot-review/REPORT-v2.md](../../experiments/2026-10-26-object-pilot-review/REPORT-v2.md#image-evidence).

# Scope

The [independent object-pilot review v2](../../experiments/2026-10-26-object-pilot-review/REPORT-v2.md), Image evidence section, checked all fourteen claimed relations against crop pixels, complete labelled plates and the prior index. It recreated twelve page renders and checked the 209 source and output bindings used in that review. The result is reviewed within that scope. The [corrected author report](../../experiments/2026-10-26-image-recovery/REPORT-v2.md) preserves the exact index baseline. This establishes index coverage without a new primary image file or physical-identity merge; thirty-four unresolved anonymous crops remain outside the selected block.
