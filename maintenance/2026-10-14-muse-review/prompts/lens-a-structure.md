## Your lens: repository structure and code layout

Judge the physical layout of the repository: top-level directories, where code, data pointers, outputs, plans and reports live, and how a newcomer (human or agent) finds the evidence for a claim.

Questions to answer:

- How many places hold the same kind of thing? Compare `research/`, `results/`, `output/`, `src/`, `experiments/`, `archive/`, `papers/` and `site/`, and the loose top-level files such as `PLAN.md` and `llms.txt`. Which are legacy layers from the first days (for example the 1–2 October "six-hour" run in `src/six_hour` and `experiments/2026-10-02-six-hour`) that a newcomer still has to step around?
- Is reusable code separated from one-off experiment scripts? Look at `src/`, `src/methods`, `bench/`, `tools/` and the scripts inside experiment packages. What should be a library with tests, and what should stay frozen inside its package?
- Experiment packages hold many intermediate files (for example `maintenance/2026-10-12-repo-restructure/` and `experiments/2026-10-13-bench/`). Is there a standard package shape? What should a package contain at minimum, and what is noise?
- What is the cost of 19,835 tracked files for cloning, searching and agent context? Which large trees could leave Git history or move to a release asset without breaking evidence links?
- Propose a target top-level layout of at most about eight entries, with a migration path that keeps frozen evidence paths resolvable (for example redirect stubs, a path map in the registry, or moving only non-evidence material).
