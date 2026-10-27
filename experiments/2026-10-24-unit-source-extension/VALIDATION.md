# Validation

`python -B experiments/2026-10-24-unit-source-extension/verify.py` passed thirteen author checks in `verification-v2.json`: input and output hashes, ten unique selected faces, eight provisional bridges on four objects, all 43 route entries, 31 remaining CISI3 routes, seven no-key object locators, one recovered face, 22 crop files with matching coordinate dimensions, the unresolved parts conflict and thirteen photograph bridges.

The first verification stopped at a crop-dimension mismatch caused by Windows case-insensitive paths. Version 1 is retained; version 2 repairs the filenames and passes. `results-v1.json` is superseded for crop use. The final source manifest hashes both runs and the preserved first builder. Repository-wide checks are performed by the coordinating contributor. No bench scorer is attached because this package submits source observations and acquisition routes without a new reading, segmentation predictor or confirmation result.
