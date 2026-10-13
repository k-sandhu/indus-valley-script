---
id: Q-1020
title: Record the unit, precision and source of every dimension value
status: open
area: data
kind: metadata
priority: 3
data_access: local-only
compute: hours
difficulty: starter
claimed_by: ""
claim_expires: ""
prior_attempts: [CONTEXT-01]
related: [Q-0004, Q-1003, Q-1005, Q-1030]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/run-2026-10-12/cross-source.json, experiments/2026-10-12-data-inventory/run-2026-10-12/placeholders.csv]
---

# Question

For each local dimension value, what unit and precision was it recorded in, which source does it come from, and where do the local sources disagree?

# Why it matters

The export's millimetre fields are mostly conversions: where both are present, 5,206 of 5,434 millimetre values equal the inch field times 25.4 within 0.6 mm, so their real precision is a tenth or a twentieth of an inch. Another 228 differ from the conversion, 452 inch values have no millimetre value, 530 thickness values are printed ranges such as `5 - 9`, and zeros stand for missing values in 1,810 horizontal, 1,681 vertical and 3,586 thickness fields. Against the older website export, 2,018 objects agree and 206 disagree. Size comparisons, such as the seal-dimension test in conjecture C-0004, need the precision and the source of each number.

# What is needed

Read [DATA.md](../DATA.md). Inputs: `data/normalized/lipi_observed_faces.jsonl`, `data/normalized/indus_website_observed.jsonl`, and the coverage outputs cited above. Classify each value as converted-from-inch, metric, range or placeholder; list the 228 conversion mismatches and the 206 cross-export disagreements with both values; check 30 of them against CISI basic data or the excavation tables once Q-1005 or Q-1003 is available.

# How to decide

Done when every dimension value has a unit class and a precision, and the mismatch lists carry a likely cause (transcription, rounding, different measurement) with the sample checks reported.

# Prior attempts

The October context audit separated placeholder zeros from measurements; this inventory measured the conversion pattern and the cross-export agreement.

# Outcome

13 October 2026, [image index and units](../../experiments/2026-10-13-image-index-and-units/README.md): each of 17,040 face-axis size values has a source, unit of record, precision, conversion fit and flags (the record-level table is local; counts are in [summary.json](../../experiments/2026-10-13-image-index-and-units/run-2026-10-13/dimensions/summary.json)). 5,643 values were recorded in inches (2,295 to 0.1 in, 3,298 to 0.01 in), 389 in millimetres and 102 in centimetres, 4,250 exist only in millimetres, and 6,656 are empty or zero. In Shot A's size population, 135 of 590 discovery seals and 146 of 582 confirmation seals have both face sizes rounded to 0.1 in. The check against an independent source waits for the Mackay and Marshall tables ([Q-1003](Q-1003-join-mackay-marshall-to-cisi.md)).
