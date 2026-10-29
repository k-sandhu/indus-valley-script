# Retrospective: navigation and tooling fixes, 15 October 2026

Claude Opus 5.5 in Claude Code applied five fixes from the 14 October outside review, from a brief written by the session that ran the review. The outcome is a 198-line map built from a fixed directory list, three new `kb.py` behaviours, one ownership rule for coverage records, a corrected citation licence and labels on the four frozen directories. Nothing was committed.

## Approach

We read the review's README and reports A and B, then `AGENTS.md`, `CONTRIBUTING.md`, `knowledge/editorial/WRITING.md` and the whole of `tools/kb.py`, and saved the map and the `kb.py check` output before editing. Before relying on the reports we confirmed that `tools/build_site.py` imports `kb.py` from Git and uses only `index_items()`, `frontmatter()` and `heading()`, none of which changed, and that nothing else calls `map_document()` or `check()`. Each `kb.py` behaviour was tested by creating cards from the CLI, running `check` in both modes and deleting the cards, with the transcript kept in [dry-run.txt](dry-run.txt).

## Problems and repairs

The brief asked us to mark `PLAN.md` in place. Its hash is recorded in two evidence manifests that `verify_knowledge_repo.py --verify-import` checks, so any edit would register as changed evidence, which the brief's own rule against editing frozen evidence forbids. We left the file unchanged, marked it from the map, and recorded the choice for the maintainer.

The contradiction about coverage records appeared in three places, the two the review cited and section 6 of `knowledge/DATA.md`. Changing `AGENTS.md` alone would have left `CONTRIBUTING.md` contradicting itself, so all three were aligned.

The first version of the shorter map came to 201 lines. Joining the three header sentences into one paragraph and dropping a redundant introductory sentence brought it to 198 without removing any entry.

A repository-wide `grep` for links into the map timed out on the 19,848-file tree; restricting the search to `tools/`, `knowledge/`, `.claude/` and the top-level documents answered it in seconds.

`verify_knowledge_repo.py` fails with 55 errors: 54 broken links in packages from 11 to 13 October and the tracked `data/MANIFEST.json`. We checked that none involves a file changed here and recorded them in the README; they are left for a separate repair.

## Outcome

`kb.py check` and `kb.py check --strict` pass after a build, the map lists no local directory, and the full import hash check finds no changed or missing evidence file. The [README](README.md) lists each change with its files and the remaining maintainer decisions.
