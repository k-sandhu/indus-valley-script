# Review brief: Indus Valley script research repository

You are an outside reviewer of this repository, working read-only. The repository is a research knowledge base on the undeciphered Indus script (c. 2600–1900 BCE). Most of its work is done by AI agents (Claude Code, Codex) working from shared evidence, with one maintainer. It holds manuscripts, experiment packages, a card-based knowledge layer (findings, questions, conjectures, directions, retrospectives, registry), a statistical benchmark harness (`bench/`), a stdlib-only CLI (`tools/kb.py`) and a hand-built website (`tools/build_site.py`, published to `gh-pages`). Since 12 October 2026 the first priority is a complete record of every inscribed object with as much metadata as can be sourced (see `knowledge/DATA.md`). Today is 14 October 2026; the project started on 1 October 2026, so everything here was built in two weeks.

## Facts we measured before writing this brief

- 19,835 tracked files (`git ls-files`). `experiments/` holds 17,745 of them in 57 dated directories. Then `research/` 761 (434 in `research/primary_index`), `output/` 705 (689 in `output/chart_atlas`), `knowledge/` 346 (185 registry, 69 questions, 35 findings, 18 retrospectives, 14 directions, 7 conjectures), `src/` 141 (89 in `src/six_hour`), `results/` 35, `papers/` 20 (6 manuscripts), `bench/` 17, `site/` 15, `tools/` 11, `archive/` 3.
- Top-level documents: `AGENTS.md` (agent entry point and hard rules), `CLAUDE.md` (points to AGENTS.md), `README.md`, `PLAN.md` (the original 1 October plan), `CONTRIBUTING.md`, `REPRODUCING.md`, `REUSE.md`, `THIRD_PARTY_NOTICES.md`, `llms.txt`, `CITATION.cff`.
- A restructure already ran on 12 October: `experiments/2026-10-12-repo-restructure/` (read its `PLAN.md` and `RETROSPECTIVE.md` before proposing another one).

## Constraints the project keeps, which your advice must respect or explicitly argue against

- No CI/CD, deployment scaffolding or recurring automations.
- Frozen experiment outputs are never overwritten; new runs go to new dated directories; failed paths stay on record. Claims link to exact outputs, so moving files breaks evidence links unless handled.
- Raw acquired corpora and unresolved-rights material are local-only and gitignored (`data/**` except `data/README.md` and `data/MANIFEST.json`, `tmp/`, `.vendor/`, most PDFs and images).
- Licences: code Unlicense, other project material CC0, Helsinki 1979 derivatives CC BY 4.0.
- The project never claims decipherment or authenticated sound values, but states its own conjectures boldly with credences, predictions and kill conditions, and tests them with a two-stage discovery/confirmation design (`experiments/2026-10-12-conjecture-shots/DESIGN.md`).

## Rules for this review

1. Do not create, modify, move or delete any file. Do not run `python tools/kb.py build`, `tools/build_site.py`, `register_experiment.py`, any `write_*` or `build_*` script, or anything else that writes. Read-only commands such as `git ls-files`, `git log`, `python tools/kb.py list|show|search|next|check` and file reads are fine.
2. Only read git-tracked files. Do not open anything under `data/` except `data/README.md` and `data/MANIFEST.json`, and do not open `tmp/`, `.vendor/` or gitignored files. They hold third-party material we may not share.
3. Start with `AGENTS.md`, `README.md`, `knowledge/MAP.md` (or `python tools/kb.py list`), then follow what your lens needs. Sample rather than read exhaustively: the experiments tree is large.
4. Ground every observation in a repo-relative path (with a line number where it helps). Separate what you observed from what you recommend. Where you estimate a number, say so.
5. Write for comprehension: explain each idea directly in connected prose, keep necessary shared assumptions together, and avoid repeated corrective comparisons or warnings that interrupt the argument. No stock phrases, promotional adjectives or canned recaps.

## Output

Your final answer is a single Markdown report, and nothing else, with these sections:

1. **Verdict**: three to six sentences on the state of the repository through your lens.
2. **Observations**: numbered, each with its evidence paths.
3. **Recommendations**: ranked by value for effort. For each: what to do, concrete steps (paths to move, merge, delete, create, or rules to change), what it costs or breaks (evidence links, registry, `kb.py`, site build, agent instructions), and how we would know it worked.
4. **Keep as is**: what is working and should not be touched.
5. **First week**: the five actions you would take first, in order.

