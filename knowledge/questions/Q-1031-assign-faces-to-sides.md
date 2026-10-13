---
id: Q-1031
title: Assign the faces of the 881 multi-face objects to their sides
status: open
area: data
kind: metadata
priority: 2
data_access: local-only
compute: hours
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [IMAGE-INDEX-AND-UNITS-2026-10-13]
related: [Q-1004]
sources: [experiments/2026-10-13-image-index-and-units/README.md, experiments/2026-10-13-image-index-and-units/verified-sides.tsv, experiments/2026-10-13-image-index-and-units/AMENDMENT-2.md]
---

# Question

For each of the 881 objects with several faces in the local export, which face row corresponds to which physical side (A, B, C) of the object, as shown on the CISI photographs?

# Why it matters

Side-level metadata (which side carries the long text, which carries the image, which is the impression) is needed to read multi-face tablets as wholes. The face-level image index links these objects' files but leaves the side open, because placing face n on the n-th side letter was right in only 34 of 40 checked cases.

# What is needed

The face-level image index, the local crops and the CISI 1 and 2 page renders. View both sides of each object and record the assignment in the format of `verified-sides.tsv`, using each face's sign count as a check.

# How to decide

Done when every multi-face object has either a verified assignment or a recorded reason it cannot be made; a second reader checks a random 10% and agreement is reported.

# Prior attempts

The [image index and units package](../../experiments/2026-10-13-image-index-and-units/README.md) verified 43 faces of 21 objects and withdrew the ordinal rule ([amendment](../../experiments/2026-10-13-image-index-and-units/AMENDMENT-2.md)).
