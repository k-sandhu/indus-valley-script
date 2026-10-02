# Choose a mapping model from the reference

The reference-only selector recovers 309 of 384 fresh generated mappings, compared with 283 for fixed graph search and 168 for fixed length/slot assignment. The supplied-family diagnostic recovers 310. The selector sees reference records and inventory size, then chooses between the two models by three-fold held-out conditional likelihood. [Protocol](PROTOCOL.md), [independent report](review/REPORT.md), [manuscript](../../../papers/004-reference-model-selection/manuscript.md).

Both models score records conditional on their observed length. The graph normalizer is `start × transition^(L−1) × end`; the slot model multiplies its normalized cell probabilities. The reference choice is made before mapping truth is opened. [Frozen main](main/results.json) and [worlds](main/worlds.json) preserve all four returned-map comparisons, including the supplied-family diagnostic.

The [independent review](review/main-v1/verification.json) passes 6,489 checks and verifies every reference choice and held-out score. Its [additional analysis](review/additional-v1/verification.json) gives paired system intervals and 32 exact equal-likelihood alternatives across eleven slot conditions. Five tied administrative conditions enter selected maps. Point recovery and compatible alternatives are kept together.

The first pilot fitted before JSON serialization failed on a NumPy boolean. Its [source and failure](pilot/failure.json) remain available; [pilot-v2](pilot-v2/results.json) uses an ordinary Python boolean. The model, seeds and selection rule are unchanged. [Retrospective](RETROSPECTIVE.md).
