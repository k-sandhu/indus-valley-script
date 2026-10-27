# Integration validation

The final `run-v2` passes the unchanged version 2 core schema, reference checks, unchanged object and face populations, preservation of inherited assertions, image hashes, frozen visual-record hashes, source alignment inputs, all 358 candidate rows and exposure-event references. The [build record](run-v2/validation.json) and [manifest](run-v2/source-manifest.json) identify its exact outputs.

Eight integration tests pass. They reject duplicate populations, unsupported confirmation eligibility, missing exposure events and unsupported source-segment promotion. They preserve unlinked rows and candidate confidence, prevent page-image display from becoming exact object exposure, and verify that compact face-review links survive image and font source checks. The last regression failed against the original code and passed after the repair.

The first independent integration review verified candidate semantics, parent preservation and all 5,420 inventory-to-family relationships, and found the compact face-review link bug. Its [record](../2026-10-22-candidate-identity-exposure/INTEGRATION-REVIEW.json) remains unchanged. The first integrated output and its exact producing code remain preserved.

The [independent review of the repair](../2026-10-22-candidate-identity-exposure/INTEGRATION-REVIEW-V2.json) passes. Of fifteen detailed output files, only `faces.jsonl` changes. Exactly twenty-nine rows differ, each solely in `layout_review.review_path`. Every repaired pointer resolves to the original review file and agrees with the copied file's hash. Manifest hashes and parent hashes match. Candidate semantics carry forward through the unchanged substantive files.

The face package passes seven artifact checks. The lexical package passes thirteen source tests and its synthetic shots check. The candidate package passes nine synthetic tests and 2,526 output checks, with six files reproduced byte for byte. These checks establish source and computation accounting; archaeological or linguistic expert acceptance remains separate.

`python tools/kb.py check` passes with 566 items, zero errors, zero warnings and two maintainer notes for generated files. Those files are left unchanged. The prose scan's remaining slash expression is in `claim-update.md`, the preserved text sent to the question issues; its original wording remains intact. The report's new prose was edited after inspection.

The [repository verifier](repository-verification.json) reports the same 58 diagnostics as the face-review package and no error in this integration package. These include existing broken links and the existing distribution flag for `data/MANIFEST.json`; the contribution does not change that file. Raw outputs remain ignored, and tracked additions contain code, protocols, aggregate results and hashes.
