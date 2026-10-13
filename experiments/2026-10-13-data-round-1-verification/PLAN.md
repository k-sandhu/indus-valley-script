# Data round 1 independent verification plan

13 October 2026. The verifier is the Codex primary agent using the GPT-6 harness. This review owns this directory and `data/raw/2026-10-13-data-round-1-verification/`. The coordinator reviews the result before committing.

Read the repository rules, both packages and the inventory definition of usable metadata. Snapshot the package files and hash each file before running their permitted offline commands. Inspect the scripts for network calls first. Exclude the museum reviewer's concurrently written `verification/` directory from mutation and comparison; record its presence separately.

Run the five specified museum scripts, then the CISI final builder, isolated join and both scoring commands. Save logs and changed outputs locally. Restore every changed starting file from its snapshot, remove only files created by these runs within the package output paths, and compare before and after hashes. Never refresh harvests, render pages, sample entries or parse pass files.

Recompute reported counts from local record rows, pass files and adjudications. Compute museum-number source sets under the inventory's usable-value rule, including separate CISI sets with and without bracketed digits. Save family membership locally and counts and identifiers in the report directory. Check holding-institution coverage only if that field is defined by the inventory.

Audit every proposed package file except `__pycache__` and the separate museum review for restricted source values, inscription sequences, record prose, private data and files over 1 MB. Keep detailed source evidence local. Run the prose scanner on both packages without fixing them.

Write the report, findings, combined counts and proposed registry record. Record the observable approach and limitations in a retrospective, scan this directory's prose, and verify restoration once more. Do not change shared files or Git state and make no network requests.
