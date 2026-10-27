# Codex assignment: clean up the entry documentation

You are working in the Indus Valley script research knowledge base at `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Git repository, branch `main`, public on GitHub as `k-sandhu/indus-valley-script`). Model: GPT-6.1-Terra in the Codex CLI. Two other Codex runs work in the same checkout at the same time; their files are listed under "Parallel runs" and you must not edit them.

## Why this work exists

The entry documents are what a newcomer, a contributor and an arriving AI agent read first. They have drifted:

- `README.md` was last substantially revised around 13 October 2026. Its "Where things stand" and "What we currently think" sections describe the work up to then, while the record now runs to 27 October (object register, town-axis register, Harappa and Lothal source contexts, the object pilot, the living atlas, conjectures C-0011 to C-0022). The project website's home page renders the README's opening paragraphs and its "Where things stand" section directly, so the README is also the public front page.
- On 24 October a storage migration pasted nearly the same paragraph about `D:\projects\indus_valley_script` into fifteen documents (`AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `REPRODUCING.md`, `bench/README.md`, `data/README.md`, `llms.txt`, `templates/EXPERIMENT.md`, all seven `.claude/skills/*/SKILL.md`, and others). Run `git show 5f734446 --stat` and `git show 5f734446` to see exactly what was added. Most readers of a public repository do not use this workstation, and `LOCAL_STORAGE.md` itself says the D: location is this workstation's choice and not a condition for reproducing the research.
- Commands, links and file counts in the entry documents may no longer match the tools and the tree.

Your job is to make the entry documentation current, accurate and readable, without deleting any file and without changing any project rule.

## Read first

1. `knowledge/editorial/WRITING.md` (binding style rules) and `knowledge/editorial/prose-review.json`.
2. `AGENTS.md`, `CLAUDE.md` (it includes `AGENTS.md` and `LOCAL_STORAGE.md` by reference), `README.md`, `CONTRIBUTING.md`, `REPRODUCING.md`, `REUSE.md`, `LOCAL_STORAGE.md`, `LOCAL_STORAGE.json`, `llms.txt`, `data/README.md`, `bench/README.md`, `templates/*.md`, `.claude/skills/*/SKILL.md`.
3. For current state: `knowledge/WORKING-MODEL.md`, the conjecture cards in `knowledge/conjectures/`, `bench/spent.json` and `bench/README.md`, the finding cards in `knowledge/findings/`, `knowledge/DATA.md`, and the `REPORT.md` of each package dated 13–27 October (`ls experiments | grep 2026-10-1[3-9]`, `ls experiments | grep 2026-10-2`).
4. `python tools/kb.py --help`, `python tools/build_site.py --help`, `python -m bench --help` so that every command you document is real.

## Owned paths (the only files you may create or edit)

`README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `REPRODUCING.md`, `LOCAL_STORAGE.md`, `llms.txt`, `data/README.md`, `bench/README.md`, `templates/*.md`, `.claude/skills/*/SKILL.md`, `knowledge/registry/attempts/DOCUMENTATION-CLEANUP-2026-10-27.json` (new), and everything under `experiments/2026-10-27-documentation-cleanup/` except this `PROMPT.md` and the launch files, which you must not edit.

## Parallel runs (do not edit their files)

- Findings organization (GPT-6.1-Sol) owns `knowledge/findings/`, `knowledge/INDEX.md`, `knowledge/TIMELINE.md`, `knowledge/WORKING-MODEL.md`, `knowledge/retrospectives/README.md` and `experiments/2026-10-27-findings-organization/`. It is writing `knowledge/findings/README.md`, a themed guide to every finding card, and may add finding cards `F-0039` onward. Link to `knowledge/findings/README.md` from the README and AGENTS.md as the place to read the findings; the file may not exist yet when you start, and that is expected.
- Website organization (GPT-6.1-Sol) owns `tools/build_site.py`, `site/` and `experiments/2026-10-27-site-organization/`. It may add the Indus living atlas (`experiments/2026-10-26-indus-living-atlas/index.html`) to the website's Explore page.

## Invariants

1. Delete no file and move no file.
2. Keep every rule in `AGENTS.md` and `CONTRIBUTING.md` in force. You may reword a rule for clarity, merge duplicates and reorder, but its meaning must not change, and the "Hard rules" list keeps every item. The sentence "For agents: Clone https://github.com/k-sandhu/indus-valley-script, read AGENTS.md and follow it." in the README must remain a line starting with `For agents:`; the website extracts it. The README's first paragraph before the first `## ` heading and its section titled exactly `## Where things stand` are rendered on the website home page, so keep that heading text.
3. `AGENTS.md` keeps the sentence requiring every subagent assignment to include the writing requirement, and the "Repository skills" section keeps its heading (the website extracts it).
4. Never change a recorded number. Every number or result you add must be copied from a finding card, conjecture card, attempt record or package report that you link next to it.
5. Do not edit anything outside the owned paths, in particular nothing in `knowledge/` other than the attempt record named above, nothing in other experiment packages, `research/`, `results/`, `output/`, `archive/`, `src/`, `papers/`, `site/`, `tools/` or `data/` (other than `data/README.md`).
6. Do not run `python tools/kb.py build`. Do not run `git commit`, `git push`, `git checkout`, `git stash`, `git reset` or any command that changes branches, the index or history. Leave all changes in the working tree.
7. No network access is needed. Do not touch `D:\`.
8. Do not claim decipherment, sound values, meanings or novelty beyond what the cited evidence supports.

## Writing requirement

Maximize reader comprehension. Explain each idea directly in connected prose. Keep necessary shared assumptions together, stated once where the reader needs them. Avoid repeated corrective comparisons or warnings that interrupt the argument. Follow `knowledge/editorial/WRITING.md`: write in the project's voice ("we", "the project"); state each rule or priority directly, without attributing it to an owner or user; remove stock phrases, promotional adjectives, rhetorical contrast, repeated caveats and canned recaps.

## Tasks

### 1. Local storage text

Consolidate the storage paragraph added on 24 October. The full description stays in `LOCAL_STORAGE.md`, which `CLAUDE.md` loads for every Claude session, and in the "Local data storage" section of `AGENTS.md` (you may tighten it; keep the rule to write new raw inputs under `data/raw/YYYY-MM-DD-slug/`, keep them local-only, and record logical and physical paths). Elsewhere, replace the pasted paragraph with what each reader needs:

- `README.md`: in the Data section, one sentence for public readers saying that acquired inputs stay outside Git and that `REPRODUCING.md` and `LOCAL_STORAGE.md` explain how to obtain or restore them. The D: path of this workstation does not belong in the README.
- `REPRODUCING.md` and `data/README.md`: one short pointer to `LOCAL_STORAGE.md`, written so it makes sense on another machine.
- `.claude/skills/add-data/SKILL.md` and `.claude/skills/start-study/SKILL.md` (the skills that acquire data): one sentence with the rule and a link to `LOCAL_STORAGE.md`. The other five skills: remove the pasted section if it adds nothing to that skill's task, or reduce it to a one-line link if it does.
- `templates/EXPERIMENT.md`: keep a field asking for the logical `data/raw/...` path and the physical path of any new local input.
- `CONTRIBUTING.md`, `bench/README.md`, `llms.txt`: one sentence or less each.

### 2. README

Bring `README.md` up to date for a newcomer:

- Keep the opening paragraphs; correct anything no longer true.
- "Where things stand": keep the existing bullets (their numbers are verified), open the section with a link to the findings guide `knowledge/findings/README.md`, and add at most four bullets on the most significant results recorded since 13 October, each taken from a finding card or package report that you link. Prefer source-reviewed results about the objects (for example the H-1657 floor context, the object register base population, the Q-1032 town register) over process milestones.
- "What we currently think": make it current with the conjecture cards and the bench ledger. Name the tests run since 13 October and their outcomes as the cards record them (for example C-0011 passing its frozen rule and being held at 0.20 after review), each with a link. Keep it short; the working model and conjecture cards hold the detail.
- "Start exploring": keep the existing links; add the Indus living atlas (`experiments/2026-10-26-indus-living-atlas/index.html`) with one sentence on what it shows, taken from its `README.md`.
- "Repository layout": correct the table against the actual top-level directories (`ls`), and mention `LOCAL_STORAGE.md` among the top-level documents if the table or text lists them.
- Check every link resolves.

### 3. AGENTS.md, CONTRIBUTING.md, REPRODUCING.md, skills, templates, llms.txt

- Verify every command and flag against `--help` output and fix any that is wrong. Record each correction in your report.
- Verify every relative link resolves; fix or report.
- Remove exact or near-exact duplicate passages between these documents where one document can link the other, keeping each rule stated fully in one place. Keep `AGENTS.md` the agent entry point and keep its orientation table.
- In `AGENTS.md`'s "How to orient" table, point "Understand where things stand" to the findings guide as well.
- `llms.txt`: make its entry points current (README, AGENTS.md, findings guide, working model, conjectures, questions, DATA.md, MAP.md, registry). Keep it short.

### 4. Checks

Run and save outputs into your package:

- `python tools/kb.py check` → `kb-check.txt`. It must report zero errors. A broken link to `knowledge/findings/README.md` is acceptable only if that file does not exist yet when you finish; say so in your final message.
- `python tools/review_prose.py --path <each changed Markdown file> --no-write` → `prose-review.txt`; fix what it flags in text you wrote.
- A standard-library link checker `check_links.py` in your package that resolves every relative Markdown link in the owned documents → `link-check.json`.
- `before-after.md`: for each owned document, a short note of what changed and why.

### 5. Package records

In `experiments/2026-10-27-documentation-cleanup/` write `REPORT.md`, `RETROSPECTIVE.md` (observable approach, problems and repairs) and `changed-paths.json`. Create `knowledge/registry/attempts/DOCUMENTATION-CLEANUP-2026-10-27.json` in the shape of `knowledge/registry/attempts/LOCAL-STORAGE-MIGRATION-2026-10-24.json`, with `status_class` "record", `area` "methods", `authors` [{"model": "GPT-6.1-Terra", "harness": "Codex CLI"}] and `verification_tier` "submitted".

## Final message

End with a plain-text message (saved to `final.md`) containing: changed paths; a one-line summary per document; every command or link you corrected; the README results you added with their sources; the check outputs (pass/fail and counts); and anything the coordinator should decide.
