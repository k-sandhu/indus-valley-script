## Your lens: knowledge layer, process and rules

Judge the documentation, card system and rules that agents and contributors must follow: `AGENTS.md`, `CONTRIBUTING.md`, `knowledge/` (INDEX, MAP, DATA, WORKING-MODEL, TIMELINE, findings, questions, conjectures, directions, retrospectives, registry, editorial, provenance), `.claude/skills/`, `templates/`, `bench/README.md` and `bench/spent.json`, and `tools/kb.py`.

Questions to answer:

- How much must an agent read before doing useful work? Trace the mandatory reading path from `AGENTS.md` and estimate its length in words or tokens. Which rules are duplicated across files, which contradict each other, and which are no longer enforced by anything?
- Are there too many card kinds? Compare findings, questions, conjectures, directions, attempts/registry entries and retrospectives. Could any be merged, or turned into fields of another kind, without losing information?
- Is `knowledge/MAP.md` (603 lines) and the generated registry the right navigation layer, or would a smaller index plus `kb.py` queries serve better?
- Is the confirmation protocol (`bench/`, shots loader, `spent.json`, freezing participants, two-stage design) proportionate to the evidence it guards? Where does it slow honest work, and where is it still too weak (for example, how is the confirmation half protected from repeated reads by many agents)?
- What would a one-page contributor contract look like that keeps the project's guarantees (frozen evidence, provenance, no decipherment claims, bold but falsifiable conjectures) while cutting the reading load? Draft its outline.
