# Navigation and tooling fixes from the 14 October review, 15 October 2026

We applied the low-risk fixes on which reports A and B of the [14 October outside review](../2026-10-14-muse-review/README.md) agree: one ownership rule for coverage records, a shorter generated map built from a fixed directory list, three gaps in `tools/kb.py`, the licence line in `CITATION.cff`, and labels on the four directories frozen before the 12 October restructure. No tracked file was moved or deleted, no experiment package other than this one was edited, and every imported and selected evidence file still matches its recorded hash. The changes are left uncommitted for the maintainer. Claude Opus 5.5 in Claude Code (desktop app) made them, working from a brief written by the session that ran the review.

Each numbered change below can be committed on its own. Three of them touch `tools/kb.py`, so committing them separately needs `git add -p`; the hunks are named under each change.

## 1. Who records coverage changes

`AGENTS.md:5` told contributors to record every new source, field and coverage change in `knowledge/DATA.md` and `data/MANIFEST.json`, while `CONTRIBUTING.md:17` told them to propose shared-document changes inside their own package. Two more sentences carried the first rule: `CONTRIBUTING.md:11` and section 6 of `knowledge/DATA.md` ("update this page's tables and numbers in the same change"). All three now say what `CONTRIBUTING.md:17` and the [add-data skill](../../.claude/skills/add-data/SKILL.md) already said: the contributor records the source, its manifest fields and the coverage change in their own package, and a maintainer folds them into `DATA.md` and the manifest after merging. The `DATA-UPDATE.md` files in the 13 October data packages already follow this pattern.

Files: `AGENTS.md` (paragraph at line 5), `CONTRIBUTING.md` (line 11), `knowledge/DATA.md` (section 6, the acquisition paragraph).

## 2. `tools/kb.py`

`map_document()` now lists a fixed set of sixteen tracked top-level directories instead of scanning whichever directories exist on the building machine, so `tmp/` and `.playwright-cli/` can no longer enter the committed map. `bench/`, `site/` and `LICENSES/` gained descriptions, and `research/`, `results/`, `src/` and `output/` are described as frozen. `kb.py new conjecture` copies `knowledge/conjectures/TEMPLATE.md` and fills in the ID, title, area and date. `kb.py new question --data` takes the next free ID from Q-1001, sets `kind: data-acquisition` and defaults the area to `data`; `--data` with another kind is refused.

`kb.py check` now prints a `WARNING` for any open or claimed question whose `claim_expires` date has passed. Warnings do not fail the check. Generated-file drift is printed as a `MAINTAINER` note and the check still passes, so a contributor whose new card leaves `MAP.md` out of date can paste a passing summary. `kb.py check --strict` counts drift as an error, for maintainers after a build. The command list in `AGENTS.md` and the pull-request paragraph in `CONTRIBUTING.md` describe both options.

Files: `tools/kb.py` (the `descriptions` dict and loop in `map_document()`, the claim-expiry and drift hunks and the `strict` parameter in `check()`, `create()`, and the `new` and `check` parsers in `main()`), `AGENTS.md` (Commands section), `CONTRIBUTING.md` (line 44).

## 3. A shorter map

`knowledge/MAP.md` now holds the top-level directories, the entry documents, findings by area, open and claimed questions by priority, conjectures and papers. A closing section gives the count of each remaining kind with the command that lists it: 181 registry attempts, 159 retrospectives, 14 direction memos and 9 completed questions. We chose command pointers over companion generated files, which keeps the generated set at two files. The map went from 603 lines with 494 list entries to 198 lines with 135. Three sentences that described the map as a full inventory were updated: `knowledge/INDEX.md:3`, `knowledge/experiments/README.md:3` and `llms.txt:8`.

Files: `tools/kb.py` (the end of `map_document()` from the Conjectures section, and the joined header paragraph), `knowledge/MAP.md` (regenerated), `knowledge/INDEX.md`, `knowledge/experiments/README.md`, `llms.txt`.

## 4. Citation licence

`CITATION.cff` gave `CC0-1.0` alone. It now lists `Unlicense`, `CC0-1.0` and `CC-BY-4.0`, which the Citation File Format 1.2.0 allows as a list of SPDX identifiers, and a comment states which material each covers, following `LICENSE` and `REUSE.md`. The format cannot attach a licence to part of the work, so `LICENSE` remains the statement of scope. The file parses with PyYAML; `cffconvert` is not installed here, so it was not validated against the CFF schema.

Files: `CITATION.cff`.

## 5. Frozen layers

New `README.md` stubs in [research/](../../research/README.md), [results/](../../results/README.md), [src/](../../src/README.md) and [output/](../../output/README.md) state what each holds, when it was last changed according to `git log`, and that new outputs go in a new dated package and new reusable code in `bench/` or `tools/`. `research/` ends with the 8 October literature notes committed on 11 October. `results/` and `src/` have not changed since 2 October. `output/` received two items on 13 October: the 11 October settlement-survey report and the layout record of the 12 October key-calibration report. The four stubs were added to the files whose links `kb.py check` verifies, which raised its Markdown count from 128 to 132.

We did not edit the top-level `PLAN.md`. Its bytes are hashed in `archive/2026-10-01-investigation/import-manifest.json` and `output/evidence_manifest.json` (SHA-256 `a497d9a8…f34300`), so a note added in place would make `verify_knowledge_repo.py --verify-import` report changed evidence. The map's top-level list marks it instead as the superseded plan of the first investigation. Marking the file itself needs a maintainer decision: add the note and a mapped exception in `tools/verify_knowledge_repo.py`, as was done when the original `README.md` was archived.

Files: `research/README.md`, `results/README.md`, `src/README.md`, `output/README.md` (all new), `tools/kb.py` (the `new_markdown()` list and the `PLAN.md` line in `map_document()`).

## Checks

| Check | Before | After |
|---|---|---|
| `python tools/kb.py check` | [PASS; 468 items; 0 errors; 128 Markdown files](check-before.txt) | [PASS; 469 items; 0 errors; 0 warnings; 0 maintainer notes; 132 Markdown files](check-after.txt) |
| `python tools/kb.py check --strict` | option did not exist | [PASS, same counts](check-after-strict.txt) |
| `knowledge/MAP.md` | 603 lines, 494 list entries, `tmp/` and `.playwright-cli/` listed | 198 lines, 135 list entries, no local directories |

The after count of 469 items includes this package's retrospective, which `kb.py` indexes; the four new stubs account for the four added Markdown files.

[dry-run.txt](dry-run.txt) records the dry runs. `new conjecture` created `C-0006` with the template's fields, and `new question --data` created `Q-1032`, the first free data ID. A third question, `Q-0039`, was edited to `status: claimed` with an expiry of 1 October, and `check` printed the lapsed-claim warning while passing; `check --strict` failed on the stale map. `new finding --data` was refused. All three cards were then deleted, `kb.py build` changed no file and `check --strict` passed on 468 items.

`python tools/verify_knowledge_repo.py` fails with 55 errors, none in a file this package touched. Fifty-four are broken links in seven packages from 11 to 13 October: 29 in the `DATA-UPDATE.md` proposals of five 13 October data packages, whose links are written relative to `knowledge/`, 17 in the settlement-prospection review drafts and 8 in the transmission-hypothesis package. The other is the tracked `data/MANIFEST.json` under the verifier's distribution rule ([verify-knowledge-repo.json](verify-knowledge-repo.json)). The `--verify-import` run hashed 16,284 imported files and 1,568 selected evidence files with no changed or missing file and the same 55 errors ([verify-knowledge-repo-import.json](verify-knowledge-repo-import.json)). `tools/review_prose.py` raised no flags on the four stubs, `CITATION.cff` or this package.

## Left for maintainers

The layout table in `README.md` still describes `output/` and `src/` without saying they are frozen; "Reports, the chart atlas and summaries from 1 to 13 October, kept unchanged" and "Analysis code of 1 and 2 October, kept unchanged" would match the stubs. `kb.py next` still hides a question whose claim has lapsed, because it filters on an empty `claimed_by`; `check` now reports such claims, and `next` could list them with a marker. The verifier's 55 link and distribution errors predate this package. The review's other recommendations, including a one-page contract, required `authors` fields, the scope of the bench requirement and the subagent writing sentence, were outside this brief.

The boldest reading these fixes support is that a contributor who starts from `AGENTS.md` alone can now find a data task, create its card and submit a passing check without meeting a contradictory rule. The route test proposed in the [12 October restructure retrospective](../2026-10-12-repo-restructure/RETROSPECTIVE.md) decides it: one fresh session completes a Priority 1 metadata question and one reproduction, recording every point where the instructions failed.
