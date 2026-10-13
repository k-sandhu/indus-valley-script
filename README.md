# Indus Valley script research knowledge base

This project tests whether many AI agents, working from shared evidence and a common evaluation harness, can make measurable progress on the Indus script and the archaeology around it. Progress means verified results: new observations linked to sources, structural findings that survive held-out tests and controls, and proposed readings that stand clear of rearrangements of themselves. Every attempt is recorded, including failures, so the next contributor starts from what is already known.

## Where things stand

A held-out test scores cases withheld while a model is fitted. Each linked card defines its score, population and chance control; a p-value measures how unusual the result is under that control.

- Across 19 catalogue ranges, 166 of 493 identifiers are absent from the held export’s keys. [Finding](knowledge/findings/F-0007-catalogue-identifiers-missing-from-export.md)
- The reviewed census joins 68 of 114 inspected original museum records to corpus families. [Finding](knowledge/findings/F-0008-museum-joins-are-a-lower-bound.md)
- Previous-sign information improves held-out prediction by 0.848 bits per noninitial sign in the selected unique texts. [Finding](knowledge/findings/F-0001-sequential-prediction-on-unique-texts.md)
- Second-order context recovers the highest-ranked graphic in 37.27% of 8,009 artificial known-slot masks, against first order’s 34.59%. [Finding](knowledge/findings/F-0002-second-order-known-slot-restoration.md)
- Missing-count prediction fails its comparator: 46.30% recovery against 51.07% for always guessing one. [Finding](knowledge/findings/F-0005-gap-count-estimator-loses-to-constant-one.md)
- Graphic base families improve prediction by 0.0219 bits per sign against size-matched random groups (p = 0.005). [Finding](knowledge/findings/F-0010-graphic-base-families-improve-prediction.md)
- Lines recur more than crossing windows on 23 catalogue-divided faces, less on 4, with 42 ties (p = 0.0003). [Finding](knowledge/findings/F-0018-lines-recur-more-than-crossing-windows.md)
- Stroke groups take 3.61 values per following item, against 4.53–5.15 for size-matched Ur III counts. [Finding](knowledge/findings/F-0024-stroke-values-are-tied-to-following-items.md)
- None of 445 eligible seals with six or more signs shares its complete text with another seal. [Finding](knowledge/findings/F-0027-long-seal-texts-do-not-repeat.md)
- Of 16 sealings or tags with texts matching eligible seals, 13 match only seals found elsewhere. [Finding](knowledge/findings/F-0030-sealings-match-seals-from-other-cities.md)

No reading, sound value or language has been established.

## What we currently think

The [working model](knowledge/WORKING-MODEL.md) states the project’s current ideas about seal legends, offices, affiliations and tablet tiers. [Conjecture cards](knowledge/conjectures/) give each claim a credence, predictions and a kill condition, and record how tests change it.

The first two [conjecture shots](experiments/2026-10-12-conjecture-shots/REVIEW-RESPONSE.md), on 12–13 October, each explored one half of the corpus and made one frozen prediction about the other half. A full working reading of 118 signs failed to predict where seals were found or how large they were. Legends closing in a small set of signs sat on larger seals, a pass that an adversarial review traced to three large seals ending in sign 820. A [plate check](experiments/2026-10-13-plate-checks/README.md) of the published photographs found that the Lothal sealings and the Mohenjo-daro seal M-895 carry the same four-sign legend from two different seals.

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

Scripts run manually. The project has no CI/CD workflow or recurring automation; the [project website](https://k-sandhu.github.io/indus-valley-script/) is generated from the repository with `tools/build_site.py` and served by GitHub Pages from the `gh-pages` branch. Discussion takes place in [GitHub Discussions](https://github.com/k-sandhu/indus-valley-script/discussions).

## Reuse and licence

Code written for the project is released under the [Unlicense](LICENSES/Unlicense.txt), and the project's prose, data, cards and documentation under [CC0 1.0](LICENSES/CC0-1.0.txt); material derived from the 1979 Helsinki edition keeps [CC BY 4.0](LICENSES/CC-BY-4.0.txt) and its attribution ([LICENSE](LICENSE)). Contributions are accepted under the same terms. Third-party material keeps its own terms. [REUSE.md](REUSE.md), [third-party notices](THIRD_PARTY_NOTICES.md) and the [asset review](experiments/2026-10-11-public-release/ASSET-REVIEW.md) describe the current package and excluded sources. Manuscripts remain AI-assisted research drafts.

## History

The [research timeline](knowledge/TIMELINE.md) preserves the earlier README’s research summaries and navigation links. The [knowledge index](knowledge/INDEX.md) and [retrospectives](knowledge/retrospectives/README.md) retain the detailed record of results, failures and repairs.
