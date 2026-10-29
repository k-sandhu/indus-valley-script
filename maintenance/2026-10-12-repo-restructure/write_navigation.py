"""Author the additive navigation documents; preserve old README sections."""
from pathlib import Path
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import kb


def put(name, text):
    path = ROOT/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip()+'\n', encoding='utf-8', newline='\n')


def main():
    index = (ROOT/'data/raw/2026-10-12-repo-restructure/INDEX-before.md').read_text(encoding='utf-8')
    definitions = index.split('## Status vocabulary\n\n',1)[1].split('\n\n',1)[0]
    areas = {
        'corpus': 'Transcriptions, sign inventories, sampling frames and the representation of inscribed records.',
        'data': 'Acquisition, metadata, joins and completeness of object, surface, image and source records.',
        'structure': 'Order, recurrence, boundaries, prediction and distributions of signs or units.',
        'seals': 'Seal legends, sealings, stamps, motifs and the physical use of seals.',
        'tablets': 'Inscribed tablets, their complete faces, production series and object relationships.',
        'numerals': 'Proposed numerical notation, quantities, metrology and arithmetic constraints.',
        'images': 'Photographs, drawings, graphic features, recognition and visual annotation.',
        'meaning': 'Semantic and functional hypotheses and their independent tests.',
        'language': 'Phonetic keys, lexical comparisons and proposed linguistic identifications.',
        'archaeology': 'Find contexts, strata, chronology, material evidence and settlement observations.',
        'comparative': 'Known writing systems, cultural transmission and cross-society comparisons.',
        'methods': 'Evaluation, inference, mathematical controls and reusable research procedures.',
    }
    vocab = '# Controlled vocabularies\n\nUse one area per item and one status class per attempt or finding. Preserve an attempt’s original free-text `status`.\n\n## Areas\n\n'
    vocab += '\n'.join(f'- `{key}`: {value}' for key,value in areas.items())
    vocab += '\n\n## Status classes\n\nThe seven definitions below are copied exactly from [INDEX.md](../INDEX.md). Their field values are `proposed`, `synthetic`, `exploratory`, `frozen-evaluation`, `failed`, `superseded` and `verified-computation`.\n\n'+definitions
    vocab += '\n\n**Source review** (`source-review`) means an audit, survey, census or literature review whose output is a source record rather than a computation. **Record** (`record`) means a coordination, release or preservation record.\n\nFor mixed work choose the class of the primary endpoint and explain that choice. The [status mapping](STATUS-MAPPING.md) records every existing decision. A checked simulation remains `synthetic`; a failed frozen evaluation can retain `frozen-evaluation` when preservation of the prespecified endpoint is the primary fact.\n\n## Questions and conjectures\n\nQuestion statuses: `open`, `claimed`, `done`, `dropped`. Task kinds: `analysis`, `data-acquisition`, `metadata`, `verification`, `literature`, `fieldwork`, `tooling`. Priority is an integer from 1 (highest) to 5. Data access: `none-needed`, `public`, `local-only`, `acquire`, `fieldwork`. Compute: `minutes`, `hours`, `days`. Difficulty: `starter`, `standard`, `expert`.\n\nConjecture statuses: `open`, `strengthened`, `weakened`, `dead`. Risk: `safe`, `stretch`, `long-shot`. Credence is a probability from 0 to 1; follow [the conjecture rules](../conjectures/README.md).\n\nVerification tiers describe contributor review separately from status class: `submitted`, `reproduced`, `reviewed`, `accepted`.\n\n## Paths and frontmatter\n\nFrontmatter paths in `evidence` and `sources` are relative to repository root. Append `#/field/subfield` to JSON evidence to name a JSON Pointer; escape slash as `~1` in a field name. Body links are relative to the Markdown file. Use quoted scalars, flow lists, block lists of scalars or block lists of flow mappings. The CLI retains unsupported structures as raw strings and reports invalid required fields.\n'
    put('knowledge/registry/VOCABULARY.md',vocab)
    put('knowledge/registry/README.md','''# Registry records

Each attempt lives in `attempts/<ID>.json`. Copy an existing entry’s field structure or run `python tools/kb.py new attempt --title "Your question" --area data`, then complete its outcome, evidence, authors and retry condition. Read [VOCABULARY.md](VOCABULARY.md) before choosing its area and status class.

Original entries retain every field and a zero-based `registry_order`. New entries omit that field and sort after the originals by ID. `metadata.json` preserves the registry’s top-level schema and scope. Maintainers run `python tools/kb.py build` after merging entries; contributors do not hand-edit the [generated registry](../experiments/registry.json) or [map](../MAP.md).

The [status mapping](STATUS-MAPPING.md) records the classifications of the preserved entries. To find prior work use `python tools/kb.py search <terms>` and read the linked retrospective before starting a new run.
''')
    # Keep all existing INDEX bytes after the requested insertion.
    intro = ('The [repository map](MAP.md) lists the full navigation layer. Read [findings](findings/), '
             '[open questions](questions/), [conjectures](conjectures/), the [working model](WORKING-MODEL.md), '
             '[data coverage](DATA.md) and the [timeline](TIMELINE.md) for the next step. '
             'Attempts and findings use the [status-class vocabulary](registry/VOCABULARY.md).\n\n')
    # The saved INDEX is authoritative; an existing insertion is never duplicated.
    saved = (ROOT/'data/raw/2026-10-12-repo-restructure/INDEX-before.md').read_bytes()
    separator = b'\r\n\r\n' if b'\r\n' in saved else b'\n\n'
    first, rest = saved.split(separator,1)
    expected=first+separator+intro.replace('\n', '\r\n' if separator.startswith(b'\r') else '\n').encode('utf-8')+rest
    assert (ROOT/'knowledge/INDEX.md').read_bytes() in (saved,expected), 'INDEX changed since the snapshot; preserve and review it before insertion'
    (ROOT/'knowledge/INDEX.md').write_bytes(expected)
    put('knowledge/experiments/README.md','''# Experiment registry

Search the attempts with `python tools/kb.py search <terms> --kind attempt`, or browse [the map](../MAP.md). Each [entry file](../registry/attempts/) preserves its question, original status, outcome, challenge, remedy, evidence and retry condition. [Status classes and areas](../registry/VOCABULARY.md) make the entries comparable without replacing the original wording.

The [registry.json](registry.json) file is generated by `python tools/kb.py build` from `knowledge/registry/metadata.json` and the entry files. Existing entries retain `registry_order`; new entries omit it and sort by ID after the originals. Contributors add entry files in their own pull requests. Maintainers build the generated registry and map after merging.

`python tools/register_experiment.py <entry.json>` validates a supplied entry or list, creates new per-entry files and calls the build. It refuses conflicting existing entries. New entries need `status_class`, `area` and the original registry fields; agents also disclose model and harness in `authors`.

`tools/build_knowledge_registry.py` reconstructs the original root entries and methods index. It is preserved unchanged as a historical utility and is superseded for new entries. Running it can replace current classifications and navigation; use `tools/kb.py build` for current maintenance.

Preserved `registry-entry.json` and `registry-entries.json` files inside experiment packages are proposed or integrated records from those runs. Leave them in place. The per-entry registry is the source for current navigation.

Before repeating a study, read its `retry_when`, source package and relevant [retrospective](../retrospectives/README.md). Add a new dated endpoint for repairs and verification.
''')
    # Preserve whole original sections; only relative link prefixes change.
    old = (ROOT/'data/raw/2026-10-12-repo-restructure/README-before.md').read_text(encoding='utf-8')
    parts = re.split(r'(?=^## )',old,flags=re.M)
    sections = {p.splitlines()[0][3:]:p for p in parts[1:]}
    def relocate(text):
        return re.sub(r'(!?\[[^\]]*\]\()([^\s)]+)(\))',
                      lambda m:m[1]+(m[2] if re.match(r'^[a-zA-Z][\w+.-]*:',m[2]) or m[2].startswith('#') else '../'+m[2])+m[3],text)
    groups = [
        ('2026-10-12', ['Start here','Where identical seal texts are found','Structure before meaning','Tests of published decipherment and usage claims','Four Bronze Age documentary comparisons']),
        ('2026-10-11', ['Excavation and overlooked settlement evidence']),
        ('2026-10-02', ['Current empirical position','Repository organization','Research memory rule']),
    ]
    timeline = '# Research timeline\n\nThis preserves the README material present at the start of the 12 October restructure. Sections are grouped newest first by the dates of their research packages; the inherited Start here table is the navigation snapshot of 12 October. Wording and measurements are retained, with relative link prefixes adjusted for this directory.\n\n'
    for day,names in groups:
        timeline += '# '+day+'\n\n'
        for name in names:
            timeline += relocate(sections.pop(name)).rstrip()+'\n\n'
    assert not sections, sections
    timeline += '# Archived introduction\n\n'+relocate(parts[0].split('\n',1)[1]).strip()+'\n'
    put('knowledge/TIMELINE.md',timeline)
    put('CLAUDE.md','@AGENTS.md')
    put('AGENTS.md','''# Agent entry point

This repository is a durable Indus research knowledge base with manuscripts and reusable code. It preserves observations, experiments, failed paths and working conjectures about the undeciphered script and its archaeology. Start here, then follow the map to the task and its evidence.

Data completeness comes first. The owner's priority from 12 October 2026 is a full and complete record of the inscribed objects, with as much metadata per object as can be sourced: identity and aliases across catalogues, every face and its images, dimensions, material, findspot, stratum and date, museum accession and publication references. Before starting an analysis, read `knowledge/DATA.md` for the gaps it depends on, and prefer work that closes a gap. Record every new source, field and change in coverage in `knowledge/DATA.md` and `data/MANIFEST.json`.

## Hard rules

- The user wants no CI/CD. Do not add `.github/workflows`, deployment scaffolding or recurring automations.
- Read `README.md`, `knowledge/INDEX.md`, `knowledge/experiments/registry.json` and the relevant retrospective before conducting research. Use the registry to avoid rerunning an already failed or superseded path without new evidence. Respect the user's subsequent instructions.
- Preserve existing plans, outputs and source witnesses. Write new runs to dated directories; never overwrite a frozen endpoint to improve its apparent result. Mark simulations, hypotheses and post-outcome refinements clearly. Claims must link to source observations and exact analysis outputs.
- Do not claim the script is deciphered, assign authenticated sounds/meanings, claim independent excavation evidence from alternate transcriptions, or advertise novelty/SOTA beyond verified support. Later cultural continuity, pictorial resemblance and alien-artifact analogies generate tests, not archaeological facts.
- Raw acquired corpora and unresolved-rights sources are local-only by default. Review `knowledge/provenance/REDISTRIBUTION.md` before tracking new third-party material. Do not change repository visibility or publish externally without a user request. Explicit user authorization for a private repository already covers maintaining its research contents. Read `REUSE.md`; no project-wide licence has been chosen.
- Parallel contributors must own distinct files, report changed paths, accommodate others and not revert their changes. Document externally observable approaches, challenges, fixes and outcomes in a retrospective; do not invent an exhaustive internal reasoning transcript.
- Read `knowledge/editorial/WRITING.md` before writing or editing. The user explicitly rejects AI-slop wording. Use concrete observations, methods and results; remove stock phrases, promotional adjectives, rhetorical contrast, repeated caveats and canned recaps. Preserve technical precision, exact source titles and the original wording of frozen evidence.

The user wants the project to be bold. State the project's own ideas at full strength in `knowledge/conjectures/` and `knowledge/WORKING-MODEL.md`: working readings, meanings, functions and integrated models belong there, written as plain claims with a credence, predictions that could fail and a kill condition. Test them with the two-stage design in `experiments/2026-10-12-conjecture-shots/DESIGN.md`: free exploration on a discovery half, then one frozen shot at the confirmation half. Aim for about a third of new runs to be long shots. End each report with the boldest reading its results support and the test that would decide it.

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
| Write a manuscript | [writing rules](knowledge/editorial/WRITING.md), [papers](papers/), its methods and claim-evidence map | orient, write-retrospective |

## Commands

Run from repository root with Python 3.13. The CLI uses only the standard library.

```text
python tools/kb.py search <terms...> [--kind finding|question|conjecture|attempt|direction|retrospective|paper] [--json]
python tools/kb.py show <ID>
python tools/kb.py list [--kind ...] [--status ...] [--area ...] [--json]
python tools/kb.py next [--area ...] [--kind analysis|metadata|verification|tooling|literature|data-acquisition|fieldwork] [--data-access ...] [--difficulty ...]
python tools/kb.py new question|finding|attempt --title "..." [--area ...]
python tools/kb.py build
python tools/kb.py check
```

`new` creates a draft: complete its inputs and fields before submitting. `next` uses merged card claims; check GitHub issues for active work. General questions use Q-0001–Q-0999; data acquisition cards use Q-1001 onward. [Vocabularies](knowledge/registry/VOCABULARY.md) define fields and [CONTRIBUTING](CONTRIBUTING.md) defines review tiers.

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
''')
    put('CONTRIBUTING.md','''# Contributing research and data

This is a knowledge repository with manually run research code. It has no CI/CD or deployment configuration. Begin with [AGENTS.md](AGENTS.md), [data coverage](knowledge/DATA.md) and the [map](knowledge/MAP.md).

## Before starting

Read the [registry](knowledge/experiments/registry.json), the relevant [retrospective](knowledge/retrospectives/README.md) and the linked paper methods. State the new observation, model or corrected premise that makes the proposed run informative. The registry's `retry_when` field identifies useful reasons to revisit earlier failures.

Choose the next unused experiment ID and a new dated directory, `experiments/YYYY-MM-DD-short-slug/`. Copy the [experiment template](templates/EXPERIMENT.md), then record the target, inputs, selection rule, controls, outcomes and stopping conditions before outcomes. State whether the work is a proposal, simulation, source replication, exploratory refinement or frozen evaluation. Keep its graphic, functional, numerical or linguistic target explicit and use the [status classes](knowledge/registry/VOCABULARY.md).

Data contributions follow [knowledge/DATA.md](knowledge/DATA.md) and record sources, metadata fields and coverage changes in [data/MANIFEST.json](data/MANIFEST.json). Conjectures follow [their card rules](knowledge/conjectures/README.md) and the [two-stage design](experiments/2026-10-12-conjecture-shots/DESIGN.md).

## Files and claims for parallel work

A contribution adds files in its own new experiment directory plus its own card files. Contributors never edit generated [registry.json](knowledge/experiments/registry.json), [MAP.md](knowledge/MAP.md) or another contribution's files. Maintainers run `python tools/kb.py build` after merging. Propose any shared-document change in your own package so a maintainer can integrate it.

Registry entries are new files in [knowledge/registry/attempts/](knowledge/registry/attempts/). Findings, questions and conjectures are new cards; use [finding](templates/FINDING.md), [question](templates/QUESTION.md) and [conjecture](knowledge/conjectures/TEMPLATE.md) templates. A later pull request resolves an ID collision by taking the next free number. General question IDs are Q-0001–Q-0999; specific data acquisition cards use Q-1001 onward. Agents disclose model and harness in the registry entry or card `authors` field.

Claim work by opening or commenting on the GitHub issue for the question, with its Q-ID in the title. A claim lapses after seven days without an update. Record the claim in the card only when the work is merged; always check the issue before starting.

Assign each contributor distinct owned paths. Tell them that others share the workspace and that their implementation must accommodate those changes. Include this requirement in every assignment:

> Maximize reader comprehension. Explain the idea directly in connected prose, keep necessary shared assumptions together, and avoid repeated corrective comparisons or warnings that interrupt the argument. Read `knowledge/editorial/WRITING.md` before writing. Preserve exact source titles and frozen evidence wording.

The integrating contributor reviews returned prose, numbers, links and source scope. Describe the result early, followed by the method and evidence needed to assess it. Necessary limitations belong together with the affected claim or shared methods premises. Follow the verbatim subagent requirement in [AGENTS.md](AGENTS.md).

## During a run

1. Preserve source identity, physical-object aliases, all available faces and uncertain cases. Record how the analytical representation was made from the source observations.
2. Keep source observations, proposed interpretations and evaluator answers in distinct inputs. Describe exactly what the fitted model and any acquisition selector receive.
3. Save commands, seeds, code/helper snapshots, source hashes and environment versions. A copied helper needs its own hash in the run record.
4. Write each run or repair to a new endpoint. Retain earlier results and identify the defect or premise changed by the repair.
5. Check the computation with an appropriate independent implementation, exact certificate or source inspection. Report the independent unit and keep repeated conditions together when calculating uncertainty.
6. Record the observable approach, challenges, fixes and outcomes in a retrospective. Link each conclusion to exact outputs and source coordinates.

Raw acquired sources and detailed unresolved-rights derivatives remain local under the [redistribution record](knowledge/provenance/REDISTRIBUTION.md). Track our code, prose, protocols, generated controls, aggregate results and acquisition manifests. Review payload contents as well as extensions. [REUSE.md](REUSE.md) states the current licence and publication status.

## Verification and completion

Result verification has four tiers: **submitted** records the author's result; **reproduced** means another contributor reran it from recorded inputs; **reviewed** means an adversarial review is recorded; **accepted** is the maintainer's decision. Verification is itself a contribution, done by someone other than the author, in its own dated directory. These tiers are separate from a finding's status class.

Before opening a pull request run `python tools/kb.py check`, `python tools/review_prose.py --path <your directory> --no-write`, `python tools/verify_knowledge_repo.py --output <your new verification path>` and the analysis-specific checks. Paste the `kb.py check` summary into the pull request. New cards and entries make the generated files stale: report that drift in the summary and leave generation to maintainers. Fix card, evidence and link errors in your owned files. Maintainers rebuild after merging and check the combined tree.

Add registry and card records, and propose index and claim-evidence-map updates for maintainer integration. Give each failure a concrete retry input. Inspect the proposed Git payload before pushing completed private research contents.

Use the next unused numbered directory under [papers/](papers/) for a new manuscript. Keep its draft status, contribution, source access and exact evidence map visible. Future public release or external submission requires the user's decision and the recorded source-specific packaging review.
''')
    put('llms.txt','''# Indus Valley script research knowledge base

> A research knowledge base testing whether shared evidence and recorded evaluation can support measurable progress on the Indus script and its archaeology. It preserves source-linked observations, experiments, failures, manuscripts and testable conjectures. Complete objects and metadata are the first priority; acquired corpora remain local and no reading or language has been established.

## Agent entry

- [AGENTS.md](AGENTS.md): the starting rules and task routes.
- [Repository map](knowledge/MAP.md): generated inventory of cards, studies and papers.

## Evidence and working ideas

- [Data coverage](knowledge/DATA.md): held inputs, missing fields and acquisition priorities.
- [Working model](knowledge/WORKING-MODEL.md): current conjectures and deciding tests.

## People and contribution

- [README](README.md): purpose, measured results and exploration.
- [CONTRIBUTING](CONTRIBUTING.md): ownership, claims and independent verification.
''')
    print('Wrote navigation, vocabularies and preserved timeline')


if __name__ == '__main__':
    main()
