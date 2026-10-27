# Validation record

The numerical endpoint passes 52 checks in [run-v2/validation.json](run-v2/validation.json). A second extraction with pdfplumber rereads the published cells used by the PyMuPDF audit. Fraction arithmetic reproduces the millet denominators and Bahola differences. These checks were written and run by the same contributor; the review tier remains `submitted`.

The source PDF's SHA-256 matches the 11 October copy. The dated protocol's SHA-256 is preserved in [protocol-freeze-v1.json](protocol-freeze-v1.json). Run-v1 and its code snapshot remain available. Run-v2 changes the detailed-output naming so a new result directory can be used without overwriting an earlier local extraction. The numerical values are unchanged.

Visual checks inspected the comparison tables on PDF pp. 81, 83, 85, 88, 89, 91 and 92 and a PNG rendering of the resulting seasonal plot. The focal paper's figures were not available as usable local images. Its source-count replication is explicitly uncomputed.

Commands run from the repository root:

```text
python experiments/2026-10-25-crop-continuity/audit.py --raw D:/projects/indus_valley_script/data/raw/2026-10-25-crop-continuity --out experiments/2026-10-25-crop-continuity/run-v2
python experiments/2026-10-25-crop-continuity/validate.py --raw D:/projects/indus_valley_script/data/raw/2026-10-25-crop-continuity --summary experiments/2026-10-25-crop-continuity/run-v2/summary.json --out experiments/2026-10-25-crop-continuity/run-v2/validation.json
python tools/kb.py check
python tools/review_prose.py --path experiments/2026-10-25-crop-continuity --path knowledge/questions/Q-0041-crop-retention-after-urban-decline.md --no-write
python tools/verify_knowledge_repo.py --output experiments/2026-10-25-crop-continuity/repository-check-v2.json
```

`kb.py check` passes with zero errors and warnings. Its two maintainer notes concern the generated registry and map, which contributors leave for maintainer regeneration. The prose scan's first pass identified ordinary prose to simplify; those passages were edited. Two slash phrases in the frozen protocol are preserved to retain its hash. A frontmatter path list is valid metadata.

The first repository-wide integrity result is [repository-check-v1.json](repository-check-v1.json). It found 58 errors outside the owned paths and one link to this validation document before it had been written. [repository-check-v2.json](repository-check-v2.json) also ran before its own output and the package-check output existed. The completed [repository-check-v3.json](repository-check-v3.json) has zero errors in this contribution and 58 outside it. Those older broken links were left unchanged. All 64 [package checks](package-checks.json) pass, covering source hashes, protocol preservation, output consistency, local links and the proposed file list. [final-check-summary.json](final-check-summary.json) records the outcome. The global check must not be described as passing.

No shared bench scorer was changed and no script-reading claim was submitted. No confirmation population or spending ledger was opened. No independent archaeological replication, peer review, publication or maintainer acceptance is claimed.
