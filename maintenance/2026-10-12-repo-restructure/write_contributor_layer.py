"""Write the human entry page, focused repository skills and issue forms."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from write_navigation import put


def main():
    findings={p.name.split('-',2)[0]+'-'+p.name.split('-',2)[1]:p.relative_to(ROOT).as_posix() for p in (ROOT/'knowledge/findings').glob('F-*.md')}
    def f(identifier):return findings[identifier]
    text=f'''# Indus Valley script research knowledge base

This project tests whether many AI agents, working from shared evidence and a common evaluation harness, can make measurable progress on the Indus script and the archaeology around it. Progress means verified results: new observations linked to sources, structural findings that survive held-out tests and controls, and proposed readings that stand clear of rearrangements of themselves. Every attempt is recorded, including failures, so the next contributor starts from what is already known.

## Where things stand

A held-out test scores cases withheld while a model is fitted. Each linked card defines its score, population and chance control; a p-value measures how unusual the result is under that control.

- Across 19 catalogue ranges, 166 of 493 identifiers are absent from the held export’s keys. [Finding]({f('F-0007')})
- The reviewed census joins 68 of 114 inspected original museum records to corpus families. [Finding]({f('F-0008')})
- Previous-sign information improves held-out prediction by 0.848 bits per noninitial sign in the selected unique texts. [Finding]({f('F-0001')})
- Second-order context recovers the highest-ranked graphic in 37.27% of 8,009 artificial known-slot masks, against first order’s 34.59%. [Finding]({f('F-0002')})
- Missing-count prediction fails its comparator: 46.30% recovery against 51.07% for always guessing one. [Finding]({f('F-0005')})
- Graphic base families improve prediction by 0.0219 bits per sign against size-matched random groups (p = 0.005). [Finding]({f('F-0010')})
- Lines recur more than crossing windows on 23 catalogue-divided faces, less on 4, with 42 ties (p = 0.0003). [Finding]({f('F-0018')})
- Stroke groups take 3.61 values per following item, against 4.53–5.15 for size-matched Ur III counts. [Finding]({f('F-0024')})
- None of 445 eligible seals with six or more signs shares its complete text with another seal. [Finding]({f('F-0027')})
- Of 16 sealings or tags with texts matching eligible seals, 13 match only seals found elsewhere. [Finding]({f('F-0030')})

No reading, sound value or language has been established.

## What we currently think

The [working model](knowledge/WORKING-MODEL.md) states the project’s current ideas about seal legends, offices, affiliations and tablet tiers. [Conjecture cards](knowledge/conjectures/) give each claim a credence, predictions and a kill condition, and record how tests change it.

## Explore

Open the [reviewed sign catalogue](experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html) for sign hypotheses and examples, or the [687-cell chart atlas](output/chart_atlas/index.html) for source-linked chart cells and transcription uncertainty. The [repository map](knowledge/MAP.md) lists findings, questions, attempts, papers and retrospectives. The [original report PDF](output/pdf/indus_script_research_report.pdf) and [settlement paper PDF](output/pdf/indus_settlement_survey_gaps_2026-10-11.pdf) are retained alongside their methods.

| Manuscript draft | Subject |
|---|---|
| [001](papers/001-artifact-aware-prediction/manuscript.md) | Graphic prediction and artificial restoration |
| [002](papers/002-conditional-reference-laws/manuscript.md) | Reference laws for copies, selection and recording quality |
| [003](papers/003-physical-observations/manuscript.md) | Physical observations and numerical ambiguity |
| [004](papers/004-reference-model-selection/manuscript.md) | Reference choice before symbol mapping |
| [005](papers/005-settlement-survey-gaps/manuscript.md) | Excavation counts, survey gaps and overlooked settings |
| [006](papers/006-sanskrit-key-calibration/manuscript.md) | A published Sanskrit key and its rearrangement controls |

## Data

The first priority is a complete record of inscribed objects and their metadata: catalogue aliases, every face and image, dimensions, material, context, dating, accession and publication references. [DATA.md](knowledge/DATA.md) records held inputs and coverage gaps. A clone contains reviewed prose, code, protocols, aggregates, source pointers and selected attributed resources; acquired corpora, most photographs, downloaded witnesses and detailed corpus-derived audit tables must be acquired separately under their source terms. [REPRODUCING.md](REPRODUCING.md) gives pinned inputs and replay requirements; [rights records](knowledge/provenance/REDISTRIBUTION.md) describe what can be shared.

For a smaller initial checkout:

```text
git clone --filter=blob:none --sparse https://github.com/k-sandhu/indus-valley-script.git
cd indus-valley-script
git sparse-checkout set knowledge papers tools templates
```

This checkout supports browsing the knowledge layer. Add experiment directories and required inputs before inspecting their outputs or reproducing a study.

## Contribute

People can [open an issue](https://github.com/k-sandhu/indus-valley-script/issues/new/choose), discuss an [open question](knowledge/questions/) or independently verify a recorded result. Data and metadata corrections are especially useful. [CONTRIBUTING.md](CONTRIBUTING.md) explains claims, owned files, review tiers and pull-request checks.

For agents: Clone https://github.com/k-sandhu/indus-valley-script, read AGENTS.md and follow it.

## Repository layout

| Directory | Contents |
|---|---|
| `papers/` | Manuscript drafts, detailed methods and evidence maps |
| `knowledge/` | Findings, questions, conjectures, registry entries, directions and source caveats |
| `experiments/` | Dated protocols, outputs, reviews and retrospectives |
| `research/` | Preserved original plans, audits, source notes and experiments |
| `src/` | Reusable original and exploratory analysis code |
| `results/` | Preserved root outputs, including superseded endpoints |
| `output/` | Reports, chart atlas, summaries and verification manifests |
| `archive/` | Original README, import record and historical documentation |
| `tools/` | Manual knowledge-base, preservation and verification utilities |
| `data/` | Local inputs and acquisition records; bulk inputs excluded from Git |
| `templates/` | Experiment, finding, question and source-review templates |
| `.claude/skills/` | Short task guides linked from AGENTS.md |
| `.github/ISSUE_TEMPLATE/` | Question claims, data corrections, result errors and conjecture forms |

Scripts run manually. The project has no CI/CD, deployment configuration or recurring automation.

## Reuse and licence

No project-wide licence has been chosen. Public visibility does not license newly authored material for unrestricted reuse; source-specific licences and notices remain in force. [REUSE.md](REUSE.md), [third-party notices](THIRD_PARTY_NOTICES.md) and the [asset review](experiments/2026-10-11-public-release/ASSET-REVIEW.md) describe the current package and excluded sources. Manuscripts remain AI-assisted research drafts.

## History

The [research timeline](knowledge/TIMELINE.md) preserves the earlier README’s research summaries and navigation links. The [knowledge index](knowledge/INDEX.md) and [retrospectives](knowledge/retrospectives/README.md) retain the detailed record of results, failures and repairs.
'''
    put('README.md',text)
    skills={
        'orient':('Use when entering this repository or locating the evidence for a task.',
                  'Read [AGENTS.md](../../../AGENTS.md), then [MAP.md](../../../knowledge/MAP.md) or run `python tools/kb.py search <terms>`. Read the relevant cards and their linked experiment package. Before analysis, read [DATA.md](../../../knowledge/DATA.md) and the relevant retrospective; use the registry’s retry condition to decide whether new work is justified.'),
        'pick-task':('Use when selecting and claiming an open research or metadata question.',
                     'Run `python tools/kb.py next`, using area, data-access and difficulty filters. Read the card, its sources and prior attempts. Follow [CONTRIBUTING.md](../../../CONTRIBUTING.md) to claim through the question’s issue, with its Q-ID in the title; check recent updates because merged card claims can lag the issue. Work in distinct owned files.'),
        'add-data':('Use when improving object records, metadata, source joins or data coverage.',
                    'Read [DATA.md](../../../knowledge/DATA.md), [data/MANIFEST.json](../../../data/MANIFEST.json), [context-data-plan.md](../../../knowledge/directions/context-data-plan.md) and [redistribution rules](../../../knowledge/provenance/REDISTRIBUTION.md). Follow their source and coverage fields. Record the proposed additions and conflicts in your own dated package; maintainers integrate shared coverage records under [CONTRIBUTING.md](../../../CONTRIBUTING.md).'),
        'start-study':('Use when creating a new experiment or a changed retry of earlier work.',
                       'Search prior attempts and read their retry conditions and retrospectives. Follow [CONTRIBUTING.md](../../../CONTRIBUTING.md) and the [experiment template](../../../templates/EXPERIMENT.md): create a dated owned directory, record the protocol before outcomes, then add a file in [registry/attempts](../../../knowledge/registry/attempts/). Choose fields from [VOCABULARY.md](../../../knowledge/registry/VOCABULARY.md); preserve earlier endpoints and disclose model and harness.'),
        'test-conjecture':('Use when testing a claim about meaning or function in a conjecture card.',
                          'Read the relevant card, [conjecture rules](../../../knowledge/conjectures/README.md) and [two-stage design](../../../experiments/2026-10-12-conjecture-shots/DESIGN.md). Follow the discovery/confirmation split and frozen predictions there. Record every result in your owned package and propose the card’s credence and record update for maintainer integration. Keep the frozen outcome and kill condition visible.'),
        'verify-study':('Use when independently reproducing an outcome or recording an adversarial review.',
                        'Read [REPRODUCING.md](../../../REPRODUCING.md), the study’s protocol, input hashes and exact outputs. Reproduce or review in your own new dated package, stating which code and sources were reused. Follow the verification tiers in [CONTRIBUTING.md](../../../CONTRIBUTING.md); report discrepancies and required local inputs. Another contributor’s review remains a separate contribution.'),
        'write-retrospective':('Use when recording the observable approach, problems, repairs and outcome of a contribution.',
                               'Read [AGENTS.md](../../../AGENTS.md), [writing rules](../../../knowledge/editorial/WRITING.md) and the relevant [retrospective](../../../knowledge/retrospectives/README.md). Write the externally observable approach, challenge, fix and outcome in your owned experiment directory. Link exact commands, outputs and preserved failed endpoints, then add or propose navigation records under [CONTRIBUTING.md](../../../CONTRIBUTING.md).'),
    }
    for name,(description,body) in skills.items():
        put(f'.claude/skills/{name}/SKILL.md',f'---\nname: {name}\ndescription: {json.dumps(description)}\n---\n\n# {name.replace("-"," ").capitalize()}\n\n{body}')
    forms={
        'claim-question':('Claim a question','Claim work on a Q-ID and record your planned scope.','[Q-0000] Claim: ',[
            ('question','Question ID and card','Include the Q-ID and repository path.'),
            ('scope','Planned work and owned paths','Name the dated directory, inputs, deliverable and expected update date.'),
            ('contributors','Contributor or agent details','Agent: disclose model and harness. Human: give your contributor handle.')]),
        'data-correction':('Data source or metadata correction','Report a source, missing field or corrected object join.','Data: ',[
            ('objects','Objects, fields and existing records','Keep catalogue namespaces and aliases explicit. Include DATA gap or Q-ID if available.'),
            ('source','Source and exact locator','Give title, edition, URL and page/plate/registration. Describe access and rights; link to source records.'),
            ('change','Proposed change and coverage','State the observation, competing assertions, completeness and the coverage count affected. Keep unresolved-rights images and corpus text local.')]),
        'result-error':('Error in a result','Report a reproducible error in a measured finding or study.','Result error: ',[
            ('result','Finding or attempt ID and output','Give the F-ID or registry ID, path and JSON field or table.'),
            ('reproduction','Reproduction and expected outcome','Record command, input hashes, environment and the observed discrepancy.'),
            ('scope','Affected claim and proposed check','Identify the exact affected population and suggest an independent check. Preserve the original endpoint.')]),
        'propose-conjecture':('Propose a conjecture','State a testable meaning or function claim and deciding predictions.','Conjecture: ',[
            ('claim','Claim, area and credence','Write the claim plainly and give a probability from 0 to 1.'),
            ('basis','Evidence and earlier proposals','Link findings and prior proposals, with source scope.'),
            ('test','Predictions, pass rules and kill condition','Follow knowledge/conjectures/README.md and the two-stage design; include a prospective prediction.')]),
    }
    for name,(title,description,prefix,fields) in forms.items():
        lines=[f'name: {json.dumps(title)}',f'description: {json.dumps(description)}',f'title: {json.dumps(prefix)}','body:']
        lines+=['  - type: markdown','    attributes:', '      value: '+json.dumps("Read CONTRIBUTING.md and AGENTS.md. Replace Q-0000 in the issue title with the card's ID. Claims lapse after seven days without an update." if name=='claim-question' else 'Read CONTRIBUTING.md. Link source records and keep acquired images, sign sequences and third-party passages out of this issue.')]
        for field,label,hint in fields:
            lines += ['  - type: textarea',f'    id: {field}','    attributes:',f'      label: {json.dumps(label)}',f'      description: {json.dumps(hint)}','    validations:','      required: true']
        put(f'.github/ISSUE_TEMPLATE/{name}.yml','\n'.join(lines))
    put('.github/ISSUE_TEMPLATE/config.yml','blank_issues_enabled: true')
    print('Wrote human README,',len(skills),'skills and',len(forms),'issue forms')


if __name__=='__main__':main()
