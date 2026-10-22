# Proposed edits to shared files

These are the fixes for the obstacles in [REPORT.md](REPORT.md), written as replacement text so a maintainer can apply them directly. Paths are given from the repository root in code spans, so that this file's own links stay valid. Line numbers refer to commit `0c23046d`. The obstacle number of each edit is given in brackets.

## Maintainer actions that are not text edits

1. Make `experiments/2026-10-12-repo-restructure/kb-check-final.txt` reach Git, either by renaming it to `kb-check-final.md` and updating `knowledge/registry/attempts/REPO-RESTRUCTURE-2026-10-12.json:15`, or by adding `!/experiments/2026-10-12-repo-restructure/kb-check-final.txt` to `.gitignore`. Do the same for the four logs of `experiments/2026-10-15-process-fixes/` and `experiments/2026-10-13-bench/kb-check.log`. Until then, `kb.py check` fails on every clean checkout. [19, 20]
2. Set `knowledge/questions/Q-1020-dimension-units-audit.md` to `status: done` and narrow Q-1004 to its remaining part, which Q-1031 already holds. [9]
3. When folding the Q-0009 package, apply `experiments/2026-10-15-route-test-metadata/DATA-UPDATE.md`, `manifest-additions.json` and `question-updates.md`, and rename `ATTEMPT-0001` if the slug-and-date scheme is kept. [16]

## AGENTS.md

Line 10, replace the second sentence ("Read `README.md`, …") with: [1]

> Read `README.md`, `knowledge/INDEX.md` and the relevant retrospective before conducting research, and read each prior attempt the card names with `python tools/kb.py show <ID>`. Search for other attempts with `python tools/kb.py search <terms>` before rerunning a failed or superseded path, and check its `retry_when` condition.

Line 30, the data row of the table: keep the two links in the "Read or run" cell and append: [6]

> ; inputs are not in Git, so restore them with `python tools/fetch_data.py --show <id>` and `--fetch <id>`

Line 57, replace the first two sentences with: [10]

> Claim a question on its GitHub issue, with the Q-ID in the title; if the question has no issue, open one with the [Claim a question](https://github.com/k-sandhu/indus-valley-script/issues/new?template=claim-question.yml) form. Claims lapse after seven days without an update; maintainers record merged claims in cards.

## CONTRIBUTING.md

Line 7, replace the first sentence with the AGENTS.md line 10 text above. [1]

Line 11, replace the second sentence with: [13, 15]

> Record new sources, metadata fields and coverage changes in your own package in three files: `DATA-UPDATE.md` (the text you propose for `knowledge/DATA.md`), `manifest-additions.json` (changed and new entries, using the fields of `data/MANIFEST.json`) and `question-updates.md` (status and dated notes for the cards you advanced). In text proposed for a shared file, write paths from the repository root in code spans, so the links in your package stay valid. Maintainers fold these records into the manifest and `knowledge/DATA.md` after merging.

Line 21, add after the first sentence: [10]

> If the question has no issue, open one with the "Claim a question" form.

"During a run", step 3, add: [20]

> Save command output as `.md` or `.json`; Git ignores `.txt` and `.log` files, so a link to one is broken on every clone.

Line 44, replace "`python tools/verify_knowledge_repo.py --output <your new verification path>`" with: [21]

> `python tools/verify_knowledge_repo.py --public-checkout --output <your new verification path>` (it reports errors that predate your work; compare against the maintainer's last recorded run and fix only those in your own files)

Line 54, replace "record such sources in `knowledge/DATA.md` and keep them local" with: [14]

> record such sources in your package's `DATA-UPDATE.md` and keep them local

## templates/EXPERIMENT.md

Line 9, replace with: [14]

> Data dependencies and gaps: read `knowledge/DATA.md`; record source, metadata and coverage changes in this package's `DATA-UPDATE.md`, `manifest-additions.json` and `question-updates.md`, which maintainers fold into `knowledge/DATA.md` and `data/MANIFEST.json` after merging.

"Protocol before outcome", add: [26]

> List every exclusion set in full (sites, codes, object types), not only the rule that produced it.

## templates/FINDING.md

Add to the frontmatter, after `authors: []`: [27]

> `verification: []` (dated package paths with their tier, for example `"experiments/2026-10-15-route-test/reproduce-f0027/README.md#reproduced"`)

Add after "# Evidence": [24, 25]

> # Reproduce
>
> The command that produced the evidence, its input manifest IDs and hashes, and whether the script writes to a fixed path that a rerun would overwrite.

## README.md

Line 36, replace the last sentence with the text below, keeping the existing link on "repository map": [2]

> The repository map indexes the findings, open questions, conjectures and papers, and gives the commands that list attempts and retrospectives.

## REPRODUCING.md

"Inputs and environment", after the list of pinned repositories (line 23), add: [7]

> `python tools/fetch_data.py --fetch <id>` clones or downloads a source with a public pinned location into a new dated directory and checks its hashes; `--list` shows every source in the manifest.

Add a section after "Fast checks": [23]

> ## Reproduce a finding
>
> Start from the finding card. Its evidence field names the output; the package's REPORT and PROTOCOL give the population and the command. Do not run the package's own script as it is: many write to their frozen run directory. Either re-implement the count from the protocol or copy the script and redirect its output, recording the copy's hash, and write to a new `experiments/YYYY-MM-DD-slug/` directory. Record the outcome as a `reproduced` tier in the card's `verification` field.

## knowledge/registry/VOCABULARY.md

Add a section: [17]

> ## Attempt fields
>
> `id` (slug in capitals and the date, for example `CISI2-BASIC-DATA-PILOT-2026-10-13`), `theme` (a short title), `status` (the author's free-text status, preserved), `question`, `outcome` (the result with its numbers), `challenge` (what limited the result), `remedy` (what was done about it), `evidence` (repository-root paths), `retry_when` (the new evidence that would justify a rerun), `status_class`, `area`, `package` and `authors`. Review-queue items in the 7 October object ledger use their own `Q-NNNNN` numbering, unrelated to question cards.

## knowledge/provenance/REDISTRIBUTION.md

Line 13, add to the "Current handling" cell: [18]

> Tracked files may hold Lipi identifiers, 0/1 coverage or placeholder flags per object and the project's own observations of each object; field values and sign sequences stay local.

Line 41, replace "remain user decisions" with "remain maintainer decisions". [4]

## Question cards

Replace the generic sentence that sends the reader to DATA.md "for the gaps this task depends on" with one naming the section and field, for example on Q-0009: "DATA.md, section 2, 'Fields not in the table' (`symbol`), and the 12 October inventory rule in `experiments/2026-10-12-data-inventory/PROTOCOL.md`." [3, 8]

## tools/kb.py

These are behaviour changes for a maintainer to implement; no code is proposed here.

- `next` and `list`: print priority, difficulty and data access in the plain output; add `--priority`. [5]
- `search`: rank items containing every term first; index experiment protocols. [12]
- `check`: report an evidence path matched by `git check-ignore` as an error even when the file exists locally; add `--path <dir>` to check the links of a contributor's own package. [19, 22]
- `new attempt`: take `--package experiments/YYYY-MM-DD-slug`, derive the ID from the slug and the date, and fill `package`. [16]
