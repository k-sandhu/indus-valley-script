Entry documentation cleanup is complete, with the findings guide still pending from the parallel contribution.

Changed entry documents:

- README.md: Added later object, town and conjecture results, the living atlas, and layout and storage guidance.
- AGENTS.md: Linked the findings guide and corrected the knowledge-base help command.
- CONTRIBUTING.md: Replaced repeated storage detail with a guide link.
- REPRODUCING.md: Added a portable storage guide pointer.
- llms.txt: Updated the navigation list.
- data/README.md and bench/README.md: Replaced workstation-specific detail with guide links.
- templates/EXPERIMENT.md: Kept local-input path fields and corrected coverage-record ownership.
- .claude/skills/add-data/SKILL.md and .claude/skills/start-study/SKILL.md: Kept the local-only acquisition rule and storage link.
- The orient, pick-task, test-conjecture, verify-study and write-retrospective skills: Removed the repeated storage paragraph.
- knowledge/registry/attempts/DOCUMENTATION-CLEANUP-2026-10-27.json: Added the submitted attempt record.
- experiments/2026-10-27-documentation-cleanup/: Added the report, retrospective, before-and-after notes, link checker, check outputs, changed-paths record and final message.

The command correction was `python tools/kb.py` to `python tools/kb.py --help`; the bare command fails because a subcommand is required. No pre-existing broken relative link was corrected. Three new links point to the parallel findings guide, which does not yet exist.

The README additions cite the object register in `experiments/2026-10-22-object-register/REPORT.md`, the H-1657 review in `experiments/2026-10-24-harappa-context-pass2-review/REPORT.md`, the image review in `experiments/2026-10-26-object-pilot-review/REPORT.md`, and the town register in `experiments/2026-10-24-q1032-town-axis-register/REPORT.md`. The later-test paragraph links its conjecture cards and the bench ledger.

Checks: `kb.py check` failed only on the three missing findings-guide links across 680 items, with zero warnings and two maintainer notes about generated files. The link checker found 194 resolving paths, three missing findings-guide links, and zero paths withheld for local links. The prose scan covered 18 files and reported 20 flags, all from existing slash compounds or file labels.

The coordinator should integrate the findings guide from the parallel run and rerun the link and knowledge-base checks. Maintainers can regenerate the map and registry after merging. No build, commit, push or branch change was made.