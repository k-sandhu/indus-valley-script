# Codex assignment: organize the findings and the knowledge index

You are working in the Indus Valley script research knowledge base at `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Git repository, branch `main`, public on GitHub as `k-sandhu/indus-valley-script`). Model: GPT-6.1-Sol in the Codex CLI. Two other Codex runs work in the same checkout at the same time; their files are listed under "Parallel runs" and you must not edit them.

## Why this work exists

The project has 38 finding cards (`knowledge/findings/F-0001` to `F-0038`, the last dated 20 October 2026), 22 conjecture cards, about 680 indexed items, and more than fifty experiment packages from 13–27 October 2026 that were committed today. The findings are hard to read as a body of results. `knowledge/findings/` has no guide page; the generated `knowledge/MAP.md` lists cards only by a coarse `area` field; `knowledge/INDEX.md` is one long chronological narrative that stops at 12 October; `knowledge/TIMELINE.md` and `knowledge/retrospectives/README.md` also stop in mid-October; and `knowledge/WORKING-MODEL.md` links only eight of the 22 conjectures. A newcomer, or an agent arriving from `AGENTS.md`, cannot tell which results matter, how they relate, or what the 13–27 October work established.

Your job is to organize what already exists so that a reader can find each result, understand it in one sentence, and follow it to its exact evidence. This is editorial and indexing work. You add no new analysis, change no recorded number, and delete nothing.

## Read first

1. `AGENTS.md`, `knowledge/editorial/WRITING.md` (binding style rules), `knowledge/registry/VOCABULARY.md` (field vocabularies and status classes), `CONTRIBUTING.md`.
2. Every file in `knowledge/findings/`, `knowledge/conjectures/` (including `README.md`), `knowledge/WORKING-MODEL.md`, `knowledge/INDEX.md`, `knowledge/TIMELINE.md`, `knowledge/retrospectives/README.md`, `knowledge/MAP.md` (generated; read only), `knowledge/directions/novelty-audit-2026-10-22.md` and `knowledge/directions/what-12-october-established.md`.
3. The attempt records in `knowledge/registry/attempts/` (use `python tools/kb.py list --kind attempt --json` and `python tools/kb.py show <ID>`), and for each 13–27 October package the `REPORT.md` (or `README.md`), any `REVIEW.md`, `VALIDATION.md` or review package that checks it, and its `RETROSPECTIVE.md`. List them with `ls experiments | grep 2026-10-1[3-9]` and `ls experiments | grep 2026-10-2`.
4. `tools/kb.py` (`python tools/kb.py --help`, and the `new finding` template it writes) so that new cards match the parser.

## Owned paths (the only files you may create or edit)

- `knowledge/findings/README.md` (new).
- New finding cards `knowledge/findings/F-0039-*.md` onward.
- Existing finding cards `F-0001` to `F-0038`: frontmatter formatting and broken links only (see rule 4 below).
- `knowledge/INDEX.md`, `knowledge/TIMELINE.md`, `knowledge/retrospectives/README.md`.
- `knowledge/WORKING-MODEL.md`: one appended section and one changelog line only (see task 5).
- `knowledge/registry/attempts/FINDINGS-ORGANIZATION-2026-10-27.json` (new).
- Everything under `experiments/2026-10-27-findings-organization/` except this `PROMPT.md` and the launch files, which you must not edit.

## Parallel runs (do not edit their files)

- Documentation cleanup (GPT-6.1-Terra) owns `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `REPRODUCING.md`, `LOCAL_STORAGE.md`, `llms.txt`, `data/README.md`, `bench/README.md`, `templates/`, `.claude/skills/`, and `experiments/2026-10-27-documentation-cleanup/`. It will link to your `knowledge/findings/README.md` from the README.
- Website organization (GPT-6.1-Sol) owns `tools/build_site.py`, `site/`, and `experiments/2026-10-27-site-organization/`. Its findings page will parse your `knowledge/findings/README.md` using the format contract in task 2, so follow that contract exactly.

## Invariants

1. Delete no file and move no file. Paths are cited by frozen manifests, cards and external links.
2. Do not edit anything outside the owned paths: in particular no other experiment package, nothing in `research/`, `results/`, `output/`, `archive/`, `src/`, `papers/`, `bench/`, `data/`, and not `knowledge/DATA.md`, `knowledge/MAP.md` or `knowledge/experiments/registry.json`.
3. Do not run `python tools/kb.py build` (it regenerates shared generated files; the coordinator runs it after all three runs finish). `python tools/kb.py check`, `search`, `list` and `show` are read-only and fine.
4. Never change a recorded number, claim, status class, credence, evidence pointer or population in an existing card. In `F-0001`–`F-0038` you may only normalize frontmatter quoting so all cards use the same quoted form (for example `area: archaeology` becomes `area: "archaeology"`), and repair a link that does not resolve. Record every such edit in your report.
5. Do not run `git commit`, `git push`, `git checkout`, `git stash`, `git reset` or any command that changes branches, the index or history. Leave all changes in the working tree.
6. No network access is needed; do not download anything. Do not touch `D:\` or follow the `data/` junctions except to read a file that a report links.
7. Do not claim decipherment, sound values, meanings or novelty beyond what the cited evidence supports (see the hard rules in `AGENTS.md`).
8. Every statement you write about a result must be traceable to a specific file you read. When you summarize a package, take the numbers from its own report or attempt record, and link that file.

## Writing requirement

Maximize reader comprehension. Explain each idea directly in connected prose. Keep necessary shared assumptions together, stated once where the reader needs them. Avoid repeated corrective comparisons or warnings that interrupt the argument. Follow `knowledge/editorial/WRITING.md`: write in the project's voice ("we", "the project"), state results plainly with their numbers, and remove stock phrases, promotional adjectives, rhetorical contrast, repeated caveats and canned recaps. Preserve exact source titles and the original wording of frozen evidence.

## Tasks

### 1. Inventory

Build `experiments/2026-10-27-findings-organization/inventory.json` listing every finding card (id, title, area, status_class, date, registry_ids), every conjecture card (id, title, status, credence, whether WORKING-MODEL.md links it), and every attempt record dated 13–27 October 2026 (id, package, status_class, verification_tier, one-line outcome copied from the record, and whether any finding card cites it). Write the small script that builds it into the package (`inventory.py`, standard library only) so the inventory can be regenerated.

### 2. Findings guide: `knowledge/findings/README.md`

Write a themed guide to every finding card. It opens with one or two short paragraphs saying what a finding card is (a result with exact evidence, a population and a status class), how the status classes differ (link `../registry/VOCABULARY.md`), and that the conjectures and working model are where the project's interpretations live. Then group all cards, old and new, into about seven to ten themes that a reader would recognise. A starting point, to adjust after reading the cards: the corpus and its gaps; sign order and prediction; lines, units and segmentation; strokes and numbers; seals, sealings and where texts travel; tablets and images; fish signs and H-912; archaeological contexts of objects and towns; methods that failed or need care. Each card appears in exactly one theme.

Format contract (the website parser depends on it, so keep it exact):

```text
# Findings

<intro paragraphs>

## <Theme title>

<one short paragraph saying what this group of results shows together>

- [F-0001](F-0001-sequential-prediction-on-unique-texts.md) The previous sign helps predict the next one: <one sentence with the key number>. *verified-computation*
- [F-0002](...) ...

## <Next theme>
...

## Results recorded in packages but not yet carded

<one short paragraph>

- [<attempt ID>](../../experiments/<package>/REPORT.md) <one sentence result with its number>. *<status_class>*, <verification_tier>
```

Rules for the contract: every theme is a level-2 heading; every card line starts with `- [F-NNNN](` and the link target is the card file name; the italic status class is the last item on the line; no nested lists; no other level-2 headings except the final "Results recorded in packages but not yet carded" section, whose lines start with `- [` followed by an attempt ID.

### 3. New finding cards for 13–27 October results

Several 13–27 October packages report source-qualified results that a reader should find among the findings. Create finding cards only for results that meet all of these conditions:

- An attempt record exists for the package, and the result is the package's reported outcome, not an aside.
- The result has an exact evidence location: a JSON pointer into a tracked output file, or a named section or table of a tracked report that itself cites primary page locations.
- The status class is one the vocabulary allows for findings (`verified-computation`, `frozen-evaluation`, `failed`, `exploratory`, `source-review`, ...; check `VOCABULARY.md`). Source checks of primary pages use `source-review`.
- Prefer results that a separate review package or validation file has checked, and say in the card's Scope section which review checked it. Candidates to examine (verify each against its files; do not assume): the H-1657 floor context (`2026-10-24-harappa-context-pass2` and `-pass2-review`), the H-1688 field key (`2026-10-24-harappa-context-pass3`, `2026-10-24-source-review-pass3`), the L-164 support dispute and Rao's conflicting plate references (`2026-10-24-office-seal-*`, `2026-10-24-office-source-verification`), the Tell Brak catalogue resolution (`2026-10-24-readable-seal-pass3`), the shared cutting method of the H-2218–H-2239 tablet clump (`2026-10-24-tablet-use-evidence`), the base object register (`2026-10-22-object-register`), the Q-1032 town register (`2026-10-24-q1032-town-axis-register`) and the fourteen image-to-catalogue links of the object pilot (`2026-10-26-image-recovery`, `2026-10-26-object-pilot-review`).

Aim for six to twelve well-supported cards rather than many thin ones. Create each with `python tools/kb.py new finding --title "<plain title that states the result>" --area <area>` and then fill every field in the same shape as `F-0030`: frontmatter (`id`, `title`, `status_class`, `area`, `date` = the package date, `registry_ids`, `evidence`, `population`, `authors` = the authors of the original package as its attempt record gives them), then `# Finding`, `# Evidence` and `# Scope`. Results that do not meet the bar go into the guide's final section instead. Record in your report which candidates you carded and why the others were left uncarded.

### 4. Knowledge index: `knowledge/INDEX.md`

Restructure the index so that it works as a front door and a dated record:

1. A short opening: what the index is for, the four levels of claim (keep that paragraph's substance), and a "Start here" list linking the findings guide, working model, conjectures, open questions, `DATA.md`, `MAP.md`, the experiment registry, the retrospectives overview and the timeline.
2. A section "Programmes by date" with one table: date or date range, programme name linked to its main report, and one-sentence outcome. Cover the whole record from 1 October to 27 October 2026, including every 13–27 October programme. Group closely related passes (for example the three passes of the eight directions on 24 October) into one row with links to each pass.
3. The existing narrative sections, moved below the table under a heading such as "Programme summaries", in date order. Keep the substance of every existing paragraph and every link; you may fix broken links and remove an exact duplicate of a sentence that appears elsewhere on the page (for example the local-storage note, which belongs in `LOCAL_STORAGE.md`; keep one pointer to it). Add short summaries in the same register for the 13–27 October programmes, each linking its report, review and retrospective.
4. Keep the "Status vocabulary" section; it can move to the end.

### 5. Working model, timeline and retrospectives

- `knowledge/WORKING-MODEL.md`: append one section, "Conjectures outside the integrated model", that lists each conjecture card the model does not yet link, one line each: linked ID, the card's claim in one sentence, its status and its credence as the card states them. Do not edit any existing section. The website treats any level-2 section whose first paragraph matches the regular expression `\bCredence\s+[0-9]` as a model headline, so write "credence 0.20" in lower case inside this new section. Add one changelog line dated 2026-10-27 saying the list was added.
- `knowledge/TIMELINE.md`: add entries for 13–27 October in the existing style, each with links.
- `knowledge/retrospectives/README.md`: add sections linking the retrospectives of the 13–27 October packages (most packages keep a `RETROSPECTIVE.md` inside the package), in the existing style.

### 6. Checks

Run and save outputs into your package:

- `python tools/kb.py check` → `kb-check.txt`. It must pass with zero errors. Maintainer notes about generated files are expected.
- `python tools/review_prose.py --path <each changed or new Markdown file> --no-write` → `prose-review.txt`; fix what it flags in your own text.
- A link check of every Markdown file you changed or created: every relative link must resolve to an existing path in the checkout. Write a small standard-library script `check_links.py` into the package and save its output as `link-check.json`.
- Confirm that `knowledge/findings/README.md` follows the format contract: write `check_guide.py` that parses it with the rules above and verifies that every `F-*.md` card appears exactly once. Save `guide-check.json`.

### 7. Package records

In `experiments/2026-10-27-findings-organization/` write `REPORT.md` (what changed and why, with the list of new cards and the uncarded candidates), `RETROSPECTIVE.md` (the observable approach, problems met and how they were resolved), and `changed-paths.json` (every path you created or edited). Create `knowledge/registry/attempts/FINDINGS-ORGANIZATION-2026-10-27.json` in the shape of `LOCAL-STORAGE-MIGRATION-2026-10-24.json`, with `status_class` "record", `area` "methods", `authors` [{"model": "GPT-6.1-Sol", "harness": "Codex CLI"}] and `verification_tier` "submitted".

## Final message

End with a plain-text message (it is saved to `final.md`) containing: the list of changed and created paths; the themes of the findings guide with their card counts; the new cards with one line each; the uncarded candidates with the reason; the outputs of the checks in task 6 (pass/fail and counts); and anything you could not complete or that the coordinator should decide.
