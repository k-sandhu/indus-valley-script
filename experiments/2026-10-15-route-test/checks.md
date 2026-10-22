# Commands and their output

Run on 15 October 2026 from the root of a Git worktree at commit `0c23046d`, with Python 3.13.5 on Windows 11, after both packages and `knowledge/registry/attempts/ATTEMPT-0001.json` were written. Output is copied here as Markdown because Git ignores `.txt` and `.log` files (obstacle 20 of the [report](REPORT.md)).

## Knowledge-base check

Before any change, in the clean worktree:

```text
> python tools/kb.py check
ERROR knowledge/registry/attempts/REPO-RESTRUCTURE-2026-10-12.json evidence: missing path: experiments/2026-10-12-repo-restructure/kb-check-final.txt
kb.py check: FAIL; 469 items; 1 errors; 0 warnings; 0 maintainer notes; 12 reviewed local-only targets; 132 Markdown files.

> git check-ignore -v experiments/2026-10-12-repo-restructure/kb-check-final.txt
.gitignore:30:*.txt	experiments/2026-10-12-repo-restructure/kb-check-final.txt
```

The same command in the maintainer's checkout, where the ignored file exists, printed `kb.py check: PASS; 469 items; 0 errors`.

With both packages in place:

```text
> python tools/kb.py check
ERROR knowledge/registry/attempts/REPO-RESTRUCTURE-2026-10-12.json evidence: missing path: experiments/2026-10-12-repo-restructure/kb-check-final.txt
MAINTAINER knowledge/experiments/registry.json: differs from a fresh build; run python tools/kb.py build
MAINTAINER knowledge/MAP.md: differs from a fresh build; run python tools/kb.py build
kb.py check: FAIL; 472 items; 1 errors; 0 warnings; 2 maintainer notes; 12 reviewed local-only targets; 132 Markdown files.
```

With the ignored log copied in from the maintainer's checkout, to show that the packages add no error (the copy was removed afterwards and `git status` showed no change in that directory):

```text
> python tools/kb.py check
MAINTAINER knowledge/experiments/registry.json: differs from a fresh build; run python tools/kb.py build
MAINTAINER knowledge/MAP.md: differs from a fresh build; run python tools/kb.py build
kb.py check: PASS; 472 items; 0 errors; 0 warnings; 2 maintainer notes; 12 reviewed local-only targets; 132 Markdown files.
```

The three new items are `ATTEMPT-0001` and the two retrospectives. The maintainer notes are the expected drift of the generated files, which contributors leave to maintainers.

## Prose scan

```text
> python tools/review_prose.py --path experiments/2026-10-15-route-test --path experiments/2026-10-15-route-test-metadata --no-write
10 files scanned; 24 flags, all slash_compound
```

Every flag is a file path such as `knowledge/DATA.md` or `analysis.py:251–252` in a heading or table cell; none is prose.

## Repository integrity

```text
> python tools/verify_knowledge_repo.py --output experiments/2026-10-15-route-test/verify-knowledge-repo.json
> python tools/verify_knowledge_repo.py --public-checkout --output experiments/2026-10-15-route-test/verify-knowledge-repo-public.json
```

The full check reports 207 errors in this worktree, almost all evidence and links that live only in the maintainer's local files; the public-checkout check reports 64. Neither set includes an error in the two packages or in `ATTEMPT-0001`. The outputs are `verify-knowledge-repo.json` and `verify-knowledge-repo-public.json` in this directory; they are named in code rather than linked, because the full check reads this file before its own output exists. The verifier refuses to overwrite an earlier output and exits with status 1; a first rerun here had its output redirected, so the refusal went unnoticed and a stale file was read until the outputs were deleted and regenerated.

## Data and issue routes

```text
> python tools/fetch_data.py --verify lipi
verifying canonical local copy of lipi (read-only)
  MISSING data/lipi/src/assets/data/inscriptions.csv
  MISSING data/lipi/src/assets/data/seal_id_and_image_mapping.json

> python tools/fetch_data.py --fetch lipi --dry-run
[dry run] git clone --no-checkout https://github.com/yajnadevam/lipi <worktree>\data\raw\2026-10-15-fetch\lipi
[dry run] git -C <worktree>\data\raw\2026-10-15-fetch\lipi checkout --detach fc8813a52e183d19c441631dc26c33a4dccbea39
[dry run] verify sha256 of src/assets/data/inscriptions.csv
[dry run] verify sha256 of src/assets/data/seal_id_and_image_mapping.json

> gh issue list --state all --limit 100 --json number,title,state,updatedAt
[]
```

## Analysis commands

```text
> python experiments/2026-10-15-route-test-metadata/sample.py --faces ../../../data/normalized/lipi_observed_faces.jsonl --out experiments/2026-10-15-route-test-metadata/run-2026-10-15
{"sample_rows": 38, "eligible": {"A": 49, "B": 39, "C": 268, "D": 28, "E": 2, "K": 1105}}

> python experiments/2026-10-15-route-test-metadata/score.py --faces ../../../data/normalized/lipi_observed_faces.jsonl --run experiments/2026-10-15-route-test-metadata/run-2026-10-15
seal objects by status: recorded 1652, asserted-absent 361, missing-unknown 226
seal motif coverage: inventory rule 2110 (94.24%), mapping v1 2013 (89.91%)

> python experiments/2026-10-15-route-test/reproduce-f0027/recount.py --faces ../../../data/normalized/lipi_observed_faces.jsonl --out experiments/2026-10-15-route-test/reproduce-f0027/run-2026-10-15
protocol_text 1430 445 0 27 differs at lengths []
protocol_text_without_code_000 1430 445 0 27 differs at lengths []
frozen 445 0

> python experiments/2026-10-15-route-test/reproduce-f0027/sensitivity.py --faces ../../../data/normalized/lipi_observed_faces.jsonl --out experiments/2026-10-15-route-test/reproduce-f0027/run-2026-10-15/sensitivity.json
all faces, South Asia: 495 distinct texts of six or more signs on 496 objects; 1 text on two objects (families 71 and 74)
```

`../../../data/` is the maintainer's checkout seen from the worktree; the faces file there has SHA-256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`, the hash DATA.md records.
