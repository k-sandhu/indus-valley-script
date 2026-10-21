# Basarh acquisition and transcription retrospective

We acquired the six pinned files and four Internet Archive metadata witnesses. All six SHA-1 and byte-count checks passed. We recomputed SHA-256 and bytes for all ten files at handoff; each matched its acquisition record. The records carry the required `rights-unverified` assessment. Each download occupies a new directory under the owned raw paths.

We read the complete Bloch list on printed pp. 101–120, its postscript continuation on p. 121, and the complete Spooner list on pp. 124–154 and register on pp. 154–185. We rendered pages at 300 dpi with PyMuPDF and displayed them with the image-viewing tool. The larger Bloch scan supplies the list. Its missing Plate XLII is present at PDF 206 of the IGNCA scan. The smaller Spooner scan is sharper and supplies the list and register. `SOURCES.md`, `pages-read.json` and `plate-locators.json` give the page witnesses.

The local outputs contain 140 Bloch rows, 286 Spooner rows representing 235 numbered parents and 51 explicit sub-entries, and 233 register rows. All 659 JSONL rows parse and carry the required fields. Every record points to an existing 300 dpi render in the named scan. The numbering audit accounts for every absent list number against the field register, including the unresolved 266/268 conflict and the register’s omission of 732 and 733. Seventeen errata remain separate from the printed plate labels.

The seed `a1-check` selected ten numbered parents. We saved the first-pass records before the second image reading. Fourteen fields differ literally: object text 7, device 3, duplicates 1, translation 1, impressions 1 and legend 1. The descriptive differences reflect independent condensation. We corrected the missing translation period and explicit single-impression count. We retained the quoted duplicate shorthand and cross-page duplicate link after reviewing the source. The two passes and detailed differences remain local. This second reading uses the same agent and harness.

We did not journal first-pass OCR correction events. Their historical count remains null in `transcription-counts.json`. The separate post-collation comparison finds 103 Bloch entries and 85 Spooner entries whose legends are not preserved verbatim in the OCR page text after whitespace folding. It preserves case, punctuation and diacritics in that comparison. These are coverage checks, not linguistic statistics or a reconstruction of the missing event log.

The PDF text layers were empty. We used Tesseract drafts and read the printed images directly. Some printed diacritics and damaged text remain uncertain; `REVIEW-DECISIONS.md` lists every group requiring review, and the local source notes give field-specific reasons. Earlier descriptions cited by Spooner are outside the supplied source set. We recorded those references without filling the missing contents.

Git initially rejected the worktree as having dubious ownership. Read-only commands with `-c safe.directory=C:/Users/sandh/OneDrive/Projects/indus_valley_script` worked without changing Git configuration. The worktree already contained other contributions, and they continued to change during A1. We wrote only owned paths and made no Git mutation. The global status-only-owned condition cannot hold in this shared worktree; the entry and final snapshots remain local.

The disk filled during the final checks. We removed four empty PDF text-index scratch files (`1903-index.json`, `1913-index.json`, `1903-alt-index.json`, `1913-alt-index.json`) and 59 explicitly unread scratch renders, releasing 29,521,413 bytes from the renders. `clear_unused_renders.py` verifies every target lies in an owned page directory. Its local journal records each removed PNG. We retained all displayed pages, acquisitions and transcriptions. The created-path manifest retains the paths of the discarded scratch files as history.

We used these commands from the repository root:

```text
python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/acquire.py
python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/pages.py render --pdf <owned source PDF> --pages <page specification> --out <owned pages directory> --scan <scan identifier>
python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/ocr_pages.py --pages <owned pages directory> --out <local OCR directory>
python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/records.py --input data/raw/2026-10-21-head-direction-corpora/codex-a1/bloch-manual.jsonl --output data/raw/2026-10-21-head-direction-corpora/transcriptions/asi-ar-1903-04.jsonl --source asi-ar-1903-04 --scan dli207529
python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/records.py --input data/raw/2026-10-21-head-direction-corpora/codex-a1/spooner-manual.jsonl --output data/raw/2026-10-21-head-direction-corpora/transcriptions/asi-ar-1913-14.jsonl --source asi-ar-1913-14 --scan dli35545
python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/assemble.py --raw data/raw/2026-10-21-head-direction-corpora
python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/finish.py --raw data/raw/2026-10-21-head-direction-corpora
python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/package_check.py --raw data/raw/2026-10-21-head-direction-corpora
python tools/review_prose.py --path experiments/2026-10-21-head-direction-corpora/codex/a1-basarh --no-write
```

The helper docstrings give their command lines. The acquisition wrapper invokes `fetch_source.py` with each expected SHA-1 and byte count. Render journals contain the exact PDF path, page, resolution and PNG hash for every render. The scripts read source files under `python -I`; PyMuPDF is imported after appending its installed package directory. No source directory contains code.

The prose checker initially flagged empty-cell em dashes in `SOURCES.md`; we changed them to `n/a`. Flags in the supplied `CODEX-PROMPT.md` and `TASK.md` concern frozen instructions and remain untouched. Final counts, validation and file paths are in `transcription-counts.json`, `validation.json` and `created-paths.txt`.

We recorded no Indus observations, ran no corpus statistic and changed no shared protocol or knowledge-base file. The agent was Codex (GPT-6) in the Codex Windows workspace harness, without subagents. The strongest supported conclusion is complete numbered-list coverage with explicit source gaps. Independent collation of the flagged readings and acquisition of the earlier descriptions will decide corpus eligibility.
