# Agent entry point

This repository is a durable Indus research knowledge base with manuscripts and reusable code. It preserves observations, experiments, failed paths and working conjectures about the undeciphered script and its archaeology. Start here, then follow the map to the task and its evidence.

Data completeness comes first. Since 12 October 2026 our first priority has been a full record of every inscribed object, with as much metadata per object as can be sourced: identity and aliases across catalogues, every face and its images, dimensions, material, findspot, stratum and date, museum accession and publication references. Before starting an analysis, read `knowledge/DATA.md` for the gaps it depends on, and prefer work that closes a gap. Record every new source, field and change in coverage in your own experiment package; maintainers fold those records into `knowledge/DATA.md` and `data/MANIFEST.json` after merging.

## Local data storage

Read [LOCAL_STORAGE.md](LOCAL_STORAGE.md) before acquiring or restoring data. Bulk local inputs are stored at `D:\projects\indus_valley_script`; the C: checkout retains junctions and file links for historical paths. Write new raw inputs under the D: `data/raw/YYYY-MM-DD-slug/` tree, keep them local-only, and record logical and physical paths. Check the D: target before large writes.

## Hard rules

- The project has no CI/CD, and none should be added: no `.github/workflows`, deployment scaffolding or recurring automations. A maintainer builds the website by hand with `tools/build_site.py` and publishes it to the `gh-pages` branch.
- Read `README.md`, `knowledge/INDEX.md`, `knowledge/experiments/registry.json` and the relevant retrospective before conducting research. Use the registry to avoid rerunning an already failed or superseded path without new evidence. Later instructions from the person you are working for take precedence.
- Preserve existing plans, outputs and source witnesses. Write new runs to dated directories; never overwrite a frozen endpoint to improve its apparent result. Mark simulations, hypotheses and post-outcome refinements clearly. Claims must link to source observations and exact analysis outputs.
- Every submitted reading, sign key, meaning map or conjecture attaches the relevant versioned output from `python -m bench <task>`. Read `bench/README.md` when choosing the protocol. Use the shared shots loader for confirmation, freeze every registered participant before the first read, and check `bench/spent.json` for prior use of the statistic family. A new seed over examined objects does not establish freshness.
- Do not claim the script is deciphered, assign authenticated sounds/meanings, claim independent excavation evidence from alternate transcriptions, or advertise novelty/SOTA beyond verified support. Later cultural continuity, pictorial resemblance and alien-artifact analogies generate tests, not archaeological facts.
- Raw acquired corpora and unresolved-rights sources are local-only by default. Review `knowledge/provenance/REDISTRIBUTION.md` before tracking new third-party material. Do not change repository visibility or publish outside the repository unless a maintainer asks for it. Permission to work in a private copy of the repository already covers maintaining its research contents. Read `REUSE.md` and `LICENSE`: project code is under the Unlicense, other project material under CC0 1.0, Helsinki 1979 derivatives under CC BY 4.0, and third-party material keeps its own terms; contributions come under the same terms.
- Parallel contributors must own distinct files, report changed paths, accommodate others and not revert their changes. Document externally observable approaches, challenges, fixes and outcomes in a retrospective; do not invent an exhaustive internal reasoning transcript.
- Read `knowledge/editorial/WRITING.md` before writing or editing. The project does not accept AI-slop wording. Write in the project's own voice ("we", "the project") and state each rule or priority directly, without attributing it to an owner or user. Use concrete observations, methods and results; remove stock phrases, promotional adjectives, rhetorical contrast, repeated caveats and canned recaps. Preserve technical precision, exact source titles and the original wording of frozen evidence.

We want the project to be bold. State the project's own ideas at full strength in `knowledge/conjectures/` and `knowledge/WORKING-MODEL.md`: working readings, meanings, functions and integrated models belong there, written as plain claims with a credence, predictions that could fail and a kill condition. Test them with the two-stage design in `experiments/2026-10-12-conjecture-shots/DESIGN.md`: free exploration on a discovery half, then one frozen shot at the confirmation half. Aim for about a third of new runs to be long shots. End each report with the boldest reading its results support and the test that would decide it.

Include this writing requirement in every future subagent assignment: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Review the returned prose before integration.

## How to orient

Layer 0 is this file. Layer 1 is [knowledge/MAP.md](knowledge/MAP.md) or `python tools/kb.py`. Layer 2 is the finding, question, conjecture or registry card for the task. Layer 3 is its linked experiment package, with protocol, exact outputs and review.

| Intent | Read or run | Skill |
|---|---|---|
| Understand where things stand | [README](README.md), [findings](knowledge/findings/), [working model](knowledge/WORKING-MODEL.md) | orient |
| Pick a task | `python tools/kb.py next`; check the question's issue | pick-task |
| Add or improve data and metadata | [DATA](knowledge/DATA.md), [manifest](data/MANIFEST.json) | add-data |
| Test a conjecture | [conjecture rules](knowledge/conjectures/README.md), [design](experiments/2026-10-12-conjecture-shots/DESIGN.md) | test-conjecture |
| Verify or review someone's work | [REPRODUCING](REPRODUCING.md), the card's exact evidence | verify-study |
| Start a new study | [CONTRIBUTING](CONTRIBUTING.md), [experiment template](templates/EXPERIMENT.md), prior attempts | start-study |
| Evaluate a reading, key, map, restoration or segmentation | [bench](bench/README.md); `python -m bench <task> --help` | start-study, test-conjecture, verify-study |
| Write a manuscript | [writing rules](knowledge/editorial/WRITING.md), [papers](papers/), its methods and claim-evidence map | orient, write-retrospective |

## Commands

Run from repository root with Python 3.13. The CLI uses only the standard library.

```text
python tools/kb.py search <terms...> [--kind finding|question|conjecture|attempt|direction|retrospective|paper] [--json]
python tools/kb.py show <ID>
python tools/kb.py list [--kind ...] [--status ...] [--area ...] [--json]
python tools/kb.py next [--area ...] [--kind analysis|metadata|verification|tooling|literature|data-acquisition|fieldwork] [--data-access ...] [--difficulty ...]
python tools/kb.py new question|finding|conjecture|attempt --title "..." [--area ...] [--data]
python tools/kb.py build
python tools/kb.py check [--strict]
```

`new` creates a draft: complete its inputs and fields before submitting. `next` uses merged card claims; check GitHub issues for active work. General questions use Q-0001–Q-0999; data acquisition cards use Q-1001 onward, and `new question --data` takes the next of those. `check` lists generated files that need a rebuild as maintainer notes; `--strict` counts them as errors. [Vocabularies](knowledge/registry/VOCABULARY.md) define fields and [CONTRIBUTING](CONTRIBUTING.md) defines review tiers.

## Contribute without collisions

Own a new `experiments/YYYY-MM-DD-short-slug/` directory and your new card files. Add registry files in `knowledge/registry/attempts/`. Leave another contribution's files and generated `knowledge/experiments/registry.json` and `knowledge/MAP.md` to maintainers, who build after merging. Resolve an ID collision in the later pull request by taking the next free number.

Claim a question on its GitHub issue, with the Q-ID in the title. Claims lapse after seven days without an update; maintainers record merged claims in cards. Disclose an agent's model and harness in `authors`. Verification is another contributor's contribution, with its own dated record. Run the checks listed in [CONTRIBUTING](CONTRIBUTING.md) before a pull request.

## Repository skills

Agents without skill support can read these as ordinary files.

- [orient](.claude/skills/orient/SKILL.md): find the task and its evidence.
- [pick-task](.claude/skills/pick-task/SKILL.md): select and claim a question.
- [add-data](.claude/skills/add-data/SKILL.md): improve metadata and coverage.
- [start-study](.claude/skills/start-study/SKILL.md): record a protocol and attempt.
- [test-conjecture](.claude/skills/test-conjecture/SKILL.md): run a two-stage test.
- [verify-study](.claude/skills/verify-study/SKILL.md): reproduce or review independently.
- [write-retrospective](.claude/skills/write-retrospective/SKILL.md): preserve approaches and repairs.
