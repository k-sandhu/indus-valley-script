# Repository restructure, phase 1: instructions for GPT-6.1-Sol

You are restructuring a public research repository so that many people and hundreds of AI agents can contribute in parallel without colliding, and so that every agent starts from one entry point and finds what it needs in one to three steps. The repository root is `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Windows, Python 3.13 as `python`, Git Bash and PowerShell available). Today is 12 October 2026. A coordinating Claude session wrote these instructions and will review your work before anything is committed.

Work carefully and completely. This restructure is infrastructure that every later contributor will rely on, so correctness, preserved content and working links matter more than speed. Expect several hours of work.

## 1. What the repository is

It is a knowledge base on the undeciphered Indus Valley script: preserved experiments (about 160 dated packages under `experiments/`), manuscripts under `papers/`, an experiment registry, retrospectives, research-direction memos, source and rights records, and reusable code. It is public on GitHub at `k-sandhu/indus-valley-script`. Acquired corpora stay local and are excluded from Git. The owner now wants to invite outside contributors, many of them AI agents, and to put the project's effort first into complete data with rich metadata.

Read these before changing anything: `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `REPRODUCING.md`, `REUSE.md`, `knowledge/INDEX.md`, `knowledge/editorial/WRITING.md`, `knowledge/experiments/README.md`, the structure of `knowledge/experiments/registry.json`, `knowledge/retrospectives/README.md`, `knowledge/directions/research-roadmap.md`, `knowledge/directions/what-12-october-established.md`, `knowledge/research-contributions.md`, `knowledge/WORKING-MODEL.md`, `knowledge/conjectures/README.md` and `TEMPLATE.md`, `experiments/2026-10-12-conjecture-shots/DESIGN.md`, `templates/`, and every script in `tools/`.

## 2. Invariants you must not break

1. **No loss and no moves.** Do not move, rename or delete any existing file. Do not change evidence files, experiment outputs, manuscripts, retrospectives or source records. You add layers on top of them. Every link that works today must still work.
2. **Working tree is the truth.** `README.md`, `knowledge/INDEX.md`, `knowledge/experiments/registry.json` and `knowledge/retrospectives/README.md` contain uncommitted edits from earlier sessions. Those edits are current content. Never run `git checkout`, `git restore`, `git reset`, `git stash`, `git clean`, `git commit` or `git push`, and never change repository history or settings.
3. **No CI/CD, no deployment, no licence.** Do not add `.github/workflows`, deployment configuration, scheduled automation or any licence file. The owner has not yet chosen a project licence; describe the current state accurately from `REUSE.md`.
4. **Rights.** Do not copy acquired corpus texts, sign sequences, source images or third-party passages into tracked files. Cards may cite object identifiers, counts and aggregate statistics. Read `knowledge/provenance/REDISTRIBUTION.md`.
5. **No new claims.** Findings cards restate measured results with their exact numbers and links. Do not round differently, generalize or add interpretation. Do not claim decipherment, sound values, meanings or a language.
6. **Parallel contributors.** Others are writing these paths now; do not create, edit or delete anything in them, but do link to them:
   - `experiments/2026-10-12-conjecture-shots/**`, `data/raw/2026-10-12-conjecture-shots/**`, `knowledge/conjectures/**` and `knowledge/WORKING-MODEL.md` (conjecture shots and the coordinator).
   - `knowledge/DATA.md`, `knowledge/data/**`, `data/MANIFEST.json`, `tools/fetch_data.py`, `experiments/2026-10-12-data-inventory/**`, `.gitignore`, and question cards numbered `Q-1001` and above (a data-inventory contributor). `knowledge/DATA.md` may not exist yet when you start; link to it anyway.

## 3. Files you own

You may create or edit only these paths:

- `AGENTS.md`, `CLAUDE.md` (new), `README.md`, `CONTRIBUTING.md`, `llms.txt` (new)
- `knowledge/INDEX.md` (light edits only, section 4.9), `knowledge/MAP.md` (new, generated), `knowledge/TIMELINE.md` (new)
- `knowledge/registry/**` (new), `knowledge/experiments/registry.json` (regenerated, section 4.3), `knowledge/experiments/README.md`
- `knowledge/findings/**` (new), `knowledge/questions/**` (new, IDs `Q-0001` to `Q-0999` only)
- `tools/kb.py` (new); `tools/register_experiment.py` only if it writes `registry.json` directly and must be adapted
- `templates/FINDING.md`, `templates/QUESTION.md` (new), `templates/EXPERIMENT.md` (update)
- `.claude/skills/**` (new)
- `.github/ISSUE_TEMPLATE/**` (new; issue forms only)
- `maintenance/2026-10-12-repo-restructure/**` (your record; this prompt file is already there and must stay unchanged)

## 4. Deliverables

### 4.1 Record first

Before editing anything else, write `maintenance/2026-10-12-repo-restructure/PLAN.md`: what you will build, in what order, and how you will verify it. Keep `CHANGES.json` there as you go: every path created or modified, with a one-line reason. Finish with `RETROSPECTIVE.md` (approaches, problems, fixes, outcomes; no invented reasoning transcript) and the verification outputs from section 5.

### 4.2 Controlled vocabularies

Write `knowledge/registry/VOCABULARY.md` defining the following. Every new card and the registry use them.

**Areas** (one per item): `corpus`, `data`, `structure`, `seals`, `tablets`, `numerals`, `images`, `meaning`, `language`, `archaeology`, `comparative`, `methods`. Give each a one-sentence definition. `data` covers acquisition, metadata, joins and completeness.

**Status classes for registry attempts and findings:** the seven terms already defined in `knowledge/INDEX.md` (`proposed`, `synthetic`, `exploratory`, `frozen-evaluation`, `failed`, `superseded`, `verified-computation`), plus `source-review` (an audit, survey, census or literature review whose output is a source record rather than a computation) and `record` (coordination, release or preservation records). Copy the INDEX definitions exactly for the seven.

The registry currently has 165 entries with 112 distinct free-text `status` strings and 126 `theme` strings. Map every entry to one `status_class` and one `area`. Do this by reading each entry's status, question and outcome, not by keyword rules alone; where an entry mixes a frozen evaluation with exploratory checks, choose the class of its primary endpoint and say so. Put the complete mapping (each original status string, the entries using it, the chosen class and a short reason) in `knowledge/registry/STATUS-MAPPING.md`.

### 4.3 One file per registry entry

Split the registry so contributors never edit a shared file:

- Write each existing entry to `knowledge/registry/attempts/<ID>.json`, keeping every original field and value exactly, and adding `status_class`, `area` and `registry_order` (its current index, so the generated file keeps today's order). New entries omit `registry_order` and sort after the existing ones by `id`.
- `python tools/kb.py build` regenerates `knowledge/experiments/registry.json` from those files. It must keep the top-level keys (`schema_version`, `scope`, `experiments`) and every original field and value of every entry. The added fields may appear in the generated file.
- Prove the regeneration preserves content: write `maintenance/2026-10-12-repo-restructure/registry-preservation.json` comparing the pre-split registry (save its SHA-256 and a copy under `data/raw/2026-10-12-repo-restructure/` first) with the regenerated one: entry count, IDs and order, and field-by-field equality of the original fields.
- If `tools/register_experiment.py` or `tools/build_knowledge_registry.py` write `registry.json`, adapt `register_experiment.py` to write a per-entry file and call the build. Leave `build_knowledge_registry.py` unchanged; document in `knowledge/experiments/README.md` that it reconstructs the original root entries and is superseded for new entries.
- Many packages contain a proposed `registry-entry.json` or `registry-entries.json` that was integrated earlier. Do not change them.

### 4.4 Findings cards

Create `templates/FINDING.md` and `knowledge/findings/F-NNNN-short-slug.md`. Frontmatter:

```yaml
---
id: F-0001
title: one line
status_class: verified-computation
area: structure
date: 2026-10-12            # date of the measurement
registry_ids: [ROOT-02]
evidence:                   # exact paths, with JSON field names where relevant
  - research/methods/FINDINGS.md
population: one line describing what was measured on
---
```

Body sections: `# Finding` (the result in one to three sentences with exact numbers), `# Evidence` (links and fields), `# Scope` (one paragraph: population, comparator and what the result does not cover). Seed 25 to 40 findings from the README's "Current empirical position", `knowledge/research-contributions.md`, `knowledge/directions/what-12-october-established.md` and the reports they link. Include failed and negative results; they are findings. Check every number against the linked source output, not only against summaries. Do not duplicate conjectures: a finding is a measurement, a conjecture is a claim about meaning or function.

### 4.5 Open questions

Create `templates/QUESTION.md` and `knowledge/questions/Q-NNNN-short-slug.md` (IDs `Q-0001` to `Q-0999`). Frontmatter:

```yaml
---
id: Q-0001
title: one line
status: open                # open | claimed | done | dropped
area: seals
kind: analysis              # analysis | data-acquisition | metadata | verification | literature | fieldwork | tooling
priority: 2                 # 1 highest, 5 lowest
data_access: local-only     # none-needed | public | local-only | acquire | fieldwork
compute: hours              # minutes | hours | days
difficulty: standard        # starter | standard | expert
claimed_by: ""
claim_expires: ""
prior_attempts: []          # registry IDs
related: []                 # F-, Q-, C- IDs
sources: []                 # repository paths
---
```

Body sections: `# Question`, `# Why it matters`, `# What is needed`, `# How to decide` (pass, kill or stopping rule), `# Prior attempts`. Seed 30 to 45 questions from the ranked table in `knowledge/directions/research-roadmap.md`, "Where effort now pays" in `what-12-october-established.md`, "What changes next" in `experiments/2026-10-12-structure-first/REPORT.md`, `knowledge/directions/decipherment-readiness-2026-10-02.md`, `knowledge/directions/context-data-plan.md`, the predictions in `knowledge/conjectures/C-0003*` to `C-0005*`, and the `retry_when` fields of the registry. Prefer questions a contributor can act on. Give the owner's new priority its weight: questions about complete objects, joins between catalogues and museum records, images and metadata fields belong at priority 1 or 2. The data-inventory contributor writes the acquisition cards for specific external datasets (`Q-1001` onward); your cards may cover analysis, verification, tooling and metadata work that uses data already held, and may reference `knowledge/DATA.md` for gaps. Mark at least eight as `difficulty: starter`.

### 4.6 `tools/kb.py`

A single-file command-line tool using the Python standard library only, deterministic output, runnable from the repository root on Windows (reuse the long-path handling in `tools/verify_knowledge_repo.py` where needed). Frontmatter parsing must handle the YAML subset used by the templates: scalars, flow lists `[a, b]`, block lists of scalars, and block lists of flow mappings (`- {date: ..., value: ...}`); keep unrecognized structures as raw strings rather than failing.

Commands:

- `kb.py search <terms...> [--kind finding|question|conjecture|attempt|direction|retrospective|paper] [--json]`: rank items by term matches, weighting IDs and titles above bodies; print ID, kind, status, title and path.
- `kb.py show <ID>`: print a card or a registry entry.
- `kb.py list [--kind ...] [--status ...] [--area ...] [--json]`.
- `kb.py next [--area ...] [--kind ...] [--data-access ...] [--difficulty ...]`: open, unclaimed questions sorted by priority then ID.
- `kb.py new question|finding|attempt --title "..." [--area ...]`: create a file from the template with the next free ID in the contributor range (`Q-0001`–`Q-0999` for general questions).
- `kb.py build`: regenerate `knowledge/experiments/registry.json` and `knowledge/MAP.md`.
- `kb.py check`: validate frontmatter against the vocabularies and required fields, ID uniqueness and filename agreement, that every path in `evidence`, `sources` and registry `evidence` exists (report missing paths; distinguish the reviewed local-only omissions listed in `maintenance/2026-10-11-public-release/public-omissions.json` if that file exists), that `registry.json` and `MAP.md` match a fresh build, and that relative links in the new-layer Markdown files resolve. Exit non-zero on errors. Print a short summary.

Index conjectures (`knowledge/conjectures/C-*.md`), findings, questions, registry attempts, direction memos (`knowledge/directions/*.md`, title from the first heading), retrospectives and papers (`papers/*/manuscript.md`).

### 4.7 `knowledge/MAP.md` (generated)

The second layer of the entry path: one line per item, grouped, each with ID or path, status and a short title, so an agent can see everything the repository holds in one read. Sections: how to use this map (three sentences); top-level directories (one line each); entry documents (README, AGENTS, DATA, WORKING-MODEL, INDEX, TIMELINE, CONTRIBUTING, REPRODUCING); findings by area; open questions by priority; conjectures with credence; registry attempts grouped by area with status class; direction memos; papers; retrospectives. Mark it as generated by `kb.py build` and not to be edited by hand. Keep each line short.

### 4.8 `AGENTS.md`: the single entry point

Rewrite `AGENTS.md` as the first file any agent reads, under about 150 lines. It must keep every rule now in the file, in substance and where possible in wording, including the no-CI rule, preservation rules, the rights rules, the parallel-contributor rules, the writing rules, the paragraph on bold conjectures, and the subagent writing requirement, which must stay verbatim:

> Include this writing requirement in every future subagent assignment: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Review the returned prose before integration.

Add this rule, verbatim, near the top:

> Data completeness comes first. The owner's priority from 12 October 2026 is a full and complete record of the inscribed objects, with as much metadata per object as can be sourced: identity and aliases across catalogues, every face and its images, dimensions, material, findspot, stratum and date, museum accession and publication references. Before starting an analysis, read `knowledge/DATA.md` for the gaps it depends on, and prefer work that closes a gap. Record every new source, field and change in coverage in `knowledge/DATA.md` and `data/MANIFEST.json`.

Structure: what the repository is (three sentences); the hard rules; how to orient (layer 0 this file, layer 1 `knowledge/MAP.md` or `python tools/kb.py`, layer 2 cards, layer 3 experiment packages); a table routing by intent (understand where things stand; pick a task; add or improve data and metadata; test a conjecture; verify or review someone's work; start a new study; write a manuscript), each row naming the file or command and the skill; the `kb.py` commands; how to contribute without collisions (section 4.10); the skills list with paths. Write `CLAUDE.md` containing `@AGENTS.md` and nothing else of substance.

### 4.9 `README.md` for people, `knowledge/TIMELINE.md`, `knowledge/INDEX.md`

Rewrite `README.md` for a human visitor, under about 160 lines:

1. Title and this statement of purpose, verbatim: "This project tests whether many AI agents, working from shared evidence and a common evaluation harness, can make measurable progress on the Indus script and the archaeology around it. Progress means verified results: new observations linked to sources, structural findings that survive held-out tests and controls, and proposed readings that stand clear of rearrangements of themselves. Every attempt is recorded, including failures, so the next contributor starts from what is already known."
2. Where things stand: eight to ten short items, each one measured result with its number, linked to its finding card. One sentence noting that no reading, sound value or language has been established.
3. What we currently think: two or three sentences pointing to `knowledge/WORKING-MODEL.md` and `knowledge/conjectures/`.
4. Explore: the sign catalogue, the chart atlas, the manuscripts and PDFs, the papers table.
5. Data: one paragraph and a link to `knowledge/DATA.md`; what a clone contains and what must be acquired; partial clone instructions (`git clone --filter=blob:none --sparse https://github.com/k-sandhu/indus-valley-script.git`, then `git sparse-checkout set knowledge papers tools templates`).
6. Contribute: for people (issues, discussion of questions, verification); for agents, the one-line bootstrap "Clone https://github.com/k-sandhu/indus-valley-script, read AGENTS.md and follow it."; link to `CONTRIBUTING.md`.
7. Repository layout (the existing table, updated).
8. Reuse and licence: state accurately what `REUSE.md` says; no project-wide licence has been chosen yet.
9. History: link to `knowledge/TIMELINE.md`.

Move nothing out of existence. Copy the current README's dated sections ("Start here" table, "Current empirical position", and the sections from "Excavation and overlooked settlement evidence" onward) verbatim into `knowledge/TIMELINE.md`, newest first under dated headings, with a short opening paragraph. Every link in the current README must remain reachable from the new README, `knowledge/INDEX.md` or `knowledge/TIMELINE.md`; list each old link and its new location in `maintenance/2026-10-12-repo-restructure/readme-link-map.json`. Fix relative link prefixes for the new file location and verify them.

Edit `knowledge/INDEX.md` only to add, at the top, a short paragraph pointing to `MAP.md`, `findings/`, `questions/`, `conjectures/`, `WORKING-MODEL.md`, `DATA.md` and `TIMELINE.md`, and the status-class vocabulary. Leave its existing content unchanged.

### 4.10 `CONTRIBUTING.md` for many parallel contributors

Rewrite to keep every existing rule and add the collision-free model:

- A contribution adds files in its own new directory, `experiments/YYYY-MM-DD-short-slug/`, plus its own card files. Contributors never edit generated files (`knowledge/experiments/registry.json`, `knowledge/MAP.md`) or another contribution's files; maintainers run `python tools/kb.py build` after merging.
- Registry entries are new files in `knowledge/registry/attempts/`. Findings, questions and conjectures are new cards. ID collisions are resolved by the later pull request taking the next free number.
- Claiming work: open or comment on the GitHub issue for the question (`Q-` ID in the title); a claim lapses after seven days without an update. Record the claim in the card only when the work is merged.
- Verification tiers for a contribution's results: submitted, reproduced (another contributor re-ran it from the recorded inputs), reviewed (adversarial review recorded), accepted (maintainer). Verification is itself a contribution, done by someone other than the author.
- Conjectures follow `knowledge/conjectures/README.md` and the two-stage design.
- Data contributions follow `knowledge/DATA.md`.
- Before opening a pull request: `python tools/kb.py check`, `python tools/review_prose.py --path <your directory> --no-write`, and the analysis-specific checks. Paste the `kb.py check` summary into the pull request.
- Agents disclose model and harness in their registry entry or card `authors` field.

### 4.11 Skills

Create Agent Skills in `.claude/skills/<name>/SKILL.md`, each with YAML frontmatter `name` and `description` (the description says when to use it, in one or two sentences) and a short body that points to the repository files that hold the rules rather than copying them. Skills: `orient` (read AGENTS, MAP, then the relevant cards), `pick-task` (use `kb.py next`, claim via issue), `add-data` (follow `knowledge/DATA.md` and the manifest, record metadata and coverage), `start-study` (dated directory, protocol before outcomes, registry entry file), `test-conjecture` (the two-stage design and card updates), `verify-study` (independent rerun, recorded review), `write-retrospective`. List them in `AGENTS.md` with paths so agents without skill support can read them as plain files.

### 4.12 Issue forms and `llms.txt`

Add `.github/ISSUE_TEMPLATE/` forms: claim a question, report a data source or metadata correction, report an error in a result, propose a conjecture. Add `config.yml` only to set blank issues as allowed. No workflows.

Write `llms.txt` at the root following the llmstxt.org format: an H1 with the project name, a one-paragraph summary in a blockquote, then sections linking `AGENTS.md`, `knowledge/MAP.md`, `knowledge/DATA.md`, `knowledge/WORKING-MODEL.md`, `README.md` and `CONTRIBUTING.md`.

## 5. Verification

Run and save outputs in `maintenance/2026-10-12-repo-restructure/`:

1. `python tools/kb.py build` twice; the second run must change nothing.
2. `python tools/kb.py check`; fix every error in files you own. Missing targets in others' paths, such as `knowledge/DATA.md` if it is not yet written, are reported, not fixed.
3. `registry-preservation.json` from section 4.3, showing all 165 entries preserved.
4. `readme-link-map.json` from section 4.9, every old README link resolved.
5. `python tools/verify_knowledge_repo.py --public-checkout --output maintenance/2026-10-12-repo-restructure/repository-verification.json`. If it reports pre-existing problems outside your paths, record them without fixing.
6. `python tools/review_prose.py --path <each Markdown file you wrote> --no-write`, then fix real problems by hand.
7. `git status --short` saved as `git-status-after.txt`, and a list confirming that no pre-existing file outside section 3 changed (compare file hashes taken at the start, stored under `data/raw/2026-10-12-repo-restructure/`).

## 6. Writing

Follow `knowledge/editorial/WRITING.md`. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Give the result or instruction first, use concrete numbers and paths, and avoid stock phrases, promotional adjectives, rhetorical contrasts, repeated caveats and closing recaps. The README is read by curious people who are not specialists: define a term the first time it appears, and keep sentences plain. `AGENTS.md` is read by agents with limited context: make it short, exact and imperative.

## 7. Final message

End with: every path created or modified; the counts of findings, questions, skills and registry files; the `kb.py check` summary; the registry preservation result; anything left unfinished or uncertain, with the reason; and the specific items you want the coordinator to review.
