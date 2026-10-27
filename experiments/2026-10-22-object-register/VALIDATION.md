# Validation record

The current `run-v2` contains 4,695 provisional objects, 5,680 faces and 225,223 assertions. The unchanged pilot JSON schema and the adapted semantic checks pass. [Build validation](run-v2/validation.json).

- All seven detailed output files replay byte for byte in a second fresh build. [Comparison](replay-comparison.json).
- The direct source-value check passes 232,837 comparisons, with zero mismatches, and verifies that 6,226 uncertain CISI assertions are absent from accepted fields. It records the skipped derived and inherited fields explicitly. [Source check](source-verification-v2.json).
- All twelve synthetic mutation and parsing checks pass. [Synthetic checks](synthetic-validation.json).
- `python tools/review_prose.py --path experiments/2026-10-22-object-register --no-write` reports seven prose files scanned and zero flags before this validation note was added.
- `python tools/kb.py check` passes with 558 items, zero errors, zero warnings and two maintainer notes for generated registry and map files. Those shared files were left unchanged.
- `git check-ignore -v data/raw/2026-10-22-object-register/run-v2/objects.jsonl` confirms the record-level export is excluded by `/data/**`.

The first attempted build stopped before writing because one dimension exceeded the inherited size plausibility bound. The source value was preserved and quarantined before the successful builds. `run-v1` is preserved as the first successful exploratory output; `run-v2` adds explicit reader-decision lineage and conservative acceptance of CISI values. The recorded output hashes and [source-code snapshots](code-provenance-v2.json) identify the current reproducible result.
