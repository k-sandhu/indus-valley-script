# Indus excavation and overlooked settlement evidence

The [reviewed paper](../../papers/005-settlement-survey-gaps/manuscript.md) answers the excavation, size and discovery-potential questions through a structured narrative review and descriptive calculations. The [printable export](../../output/pdf/indus_settlement_survey_gaps_2026-10-11.pdf) has 33 pages. The study was completed on 11 October 2026, with 72 source records, 69 cited references, 50 acquired local witnesses and 21 editorial regions of interest.

Historical inventories support the familiar approximately 100-of-1,000 account, while a recent review counts 142 excavated Early and Mature sites through 2024. Their populations and dates differ. Published area estimates also measure different units: Ganweriwala's legacy, ground-survey and visible-mound estimates are 81.5, 66.7 and approximately 33 hectares. Repeat investigations document local recording omissions, missing cartographic features, unconfirmed remote candidates and finer mound units. These distinct observations cannot identify a current regional excavation fraction, undiscovered-site total or artifact yield.

The agenda compares sites affected by later cities, alluvium, farming, piedmont sediment, caves, landslides and coastal change. Each proposed region has sources, a rival explanation, a comparison unit and a decision that could demote its premise. A concordance of records and survey effort precedes field tasks. The buried-surface pilot is an unrun 24-block workload, with block-level inference and adequate-observation requirements. No new field location, imagery analysis, field access or calibrated discovery probability was established.

## Current files

| Purpose | Current endpoint |
|---|---|
| Paper and reader guide | [manuscript](../../papers/005-settlement-survey-gaps/manuscript.md), [methods](../../papers/005-settlement-survey-gaps/methods.md), [paper README](../../papers/005-settlement-survey-gaps/README.md) |
| Final sources and reading depth | [sources-v6.json](sources-v6.json), [final search/access record](SEARCH-AND-ACCESS-FINAL.md) |
| Regions, comparisons and rules | [candidates-v5.json](candidates-v5.json), [GeoJSON](map-v5/survey-windows.geojson), [offline viewer](map-v5/survey-hypotheses.html) |
| Claim-to-observation and output joins | [claims-v3.json](claims-v3.json) |
| Numerical results | [run-v3 manifest](run-v3/manifest.json), [verification](run-v3/verification.json) |
| Inline conversions | [seven rows](run-v3-inline-arithmetic/arithmetic.json), [17 implementation checks](run-v3-inline-arithmetic/verification.json) |
| Current pilot | [PILOT-DESIGN-v4.md](PILOT-DESIGN-v4.md) |
| Original charts | [figures-v3](figures-v3/manifest.json); [layout-corrected observation diagram](figures-v4/manifest.json) |
| Commissioned review response | [response-to-reviewers.md](review/response-to-reviewers.md) |
| Final checks and preservation | [final verification](review/final-verification-v2.json), [PDF inspection](review/pdf-inspection.json), [package manifest](final-manifest.json) |
| Research memory | [retrospective](../../knowledge/retrospectives/2026-10-11-settlement-prospection.md), [registry](../../knowledge/experiments/registry.json) |

The register's A/B/C evidence classes describe the next question. Information, preservation-evidence and feasibility levels are separate editorial assessments by the AI-assisted drafting process. P2 documents known archaeological survival somewhere in a region, including other periods; it does not predict target-parcel survival. All feasibility is F0, unverified. Rectangles overlap, and a shared-frame rule selects any eligible cell once. They are indexing regions, not completed sampling frames or terrain predictions.

## Preserved history and review

[PROTOCOL.md](PROTOCOL.md) records the initial questions and user scope additions. The first complete 9,199-word [draft](review/draft-v1.md) and [manifest](review/draft-v1-manifest.json) were frozen before review. Sources v1–v5, candidate registers v1–v4, runs v1–v2, maps v1–v4 and earlier manuscripts remain preserved. The final substantive text was assembled as revised-v4; [revised-v5](review/revised-v5.md) changes only the observation-diagram path for print layout. The canonical paper matches that frozen revision. The v1–v3 pilot documents are superseded by v4.

Commissioned Codex passes covered source attribution, the first manuscript, mountain/cave integration, statistical design and numerical outputs. The [first manuscript audit](review/codex-adversarial-review.md) recorded 23 passes and one geographic failure. The corrected P18 box contains the official Ghazi Shah and Kai coordinates. The [source/region audit](review/final-source-region-audit.md) preserves 127 passes and two clarifications in its original log; successor registers resolve the sentence locator and consistent documentary preservation criterion.

Two actual Claude Code CLI reviews used canonical model `claude-opus-5-5`: [pass 1](review/claude-opus55-v1/review.md) and [pass 2](review/claude-opus55-v2/review.md). They used supplied authored packets with tools disabled. The second verdict was ready after targeted corrections, which are recorded in the response. Retained CLI JSON and invocation records establish the model and completed results. The first wrapper failed during local metadata handling after saving its successful review; recovered metadata leaves unavailable timing/exit fields explicit. The second invocation records exit code 0. These are commissioned AI-model passes, not archaeological peer review.

## Manual reproduction

Numerical aggregates use Python's standard library; original plot generation additionally uses the version in [requirements.txt](requirements.txt). The preserved run used Python 3.13.5 and matplotlib 3.11.2. Run each command from the repository root, with fresh output names. Existing endpoints are deliberately refused.

```powershell
python -X utf8 experiments/2026-10-11-settlement-prospection/analysis.py --output experiments/2026-10-11-settlement-prospection/replay-results-new --figures experiments/2026-10-11-settlement-prospection/replay-figures-new --source-register experiments/2026-10-11-settlement-prospection/sources-v2.json
```

The analysis reads the two preserved October 8 selected metadata files and the authored v2 source register. Its inscription-oriented metadata results remain supplementary and do not estimate settlement coverage. Source-reported numerical constants are curated in the script. The [final comparison](review/final-register-numeric-comparison.json) confirms all 32 consumed metadata fields across v2/v4/v5 against recorded run metadata; final package checks extend this through v6. Changes to reading depth and observations did not replace numerical inputs. Ordinary replay supplies no amendment argument and asserts no retrospective amendment history.

To reuse the preserved figure bytes while replaying calculations, use an existing hashed figure manifest:

```powershell
python -X utf8 experiments/2026-10-11-settlement-prospection/analysis.py --output experiments/2026-10-11-settlement-prospection/replay-data-only-new --figures experiments/2026-10-11-settlement-prospection/figures-v3 --reuse-figures --source-register experiments/2026-10-11-settlement-prospection/sources-v2.json
```

The figure reuse mode checks every recorded file hash. Fresh plotting may produce different file hashes across font/library versions while retaining the numerical results. The final diagram's border repair has its own script and manifest; it uses unchanged synthetic examples from run-v3:

```powershell
python -X utf8 experiments/2026-10-11-settlement-prospection/render_chain_layout.py --input experiments/2026-10-11-settlement-prospection/run-v3/synthetic-scenarios.json --output experiments/2026-10-11-settlement-prospection/replay-chain-new
```

The inline arithmetic and editorial map can likewise be recreated in new directories:

```powershell
python -X utf8 experiments/2026-10-11-settlement-prospection/run-v3-inline-arithmetic/calculate.py --output experiments/2026-10-11-settlement-prospection/replay-inline-new
python -X utf8 experiments/2026-10-11-settlement-prospection/make_map.py --input experiments/2026-10-11-settlement-prospection/candidates-v5.json --output experiments/2026-10-11-settlement-prospection/replay-map-new --source-register experiments/2026-10-11-settlement-prospection/sources-v6.json
```

PDF reproduction uses [presentation-requirements.txt](presentation-requirements.txt), Georgia fonts and Poppler for page inspection:

```powershell
python -X utf8 experiments/2026-10-11-settlement-prospection/render_paper.py --input papers/005-settlement-survey-gaps/manuscript.md --output tmp/pdfs/replay-paper-new.pdf
python -X utf8 experiments/2026-10-11-settlement-prospection/inspect_export.py --pdf tmp/pdfs/replay-paper-new.pdf --output tmp/pdfs/replay-paper-qa-new
```

The supplied `finalize_export.py` records this session's actual inspection and refuses replacing the final PDF; it is not a substitute for visually reviewing a new export. The final manuscript has three empirical/coordinate figures and one constructed observation diagram. Earlier synthetic fragment-yield examples remain supplementary. No national archaeological total is inferred from them.

## Sources and unresolved work

Raw acquired files remain local in ignored `data/raw/2026-10-11-settlement-prospection/`. Authored notes, pointers, hashes, original figures and aggregate outputs form this package. No complete downloaded paper, source image or inscription sequence is redistributed here. [ASSET-REVIEW.md](ASSET-REVIEW.md) records that boundary.

The next substantive change requires accessible project-level coordinates and footprints, record reconciliation, local chronology or a partner's preservation/detection calibration. The reviewed aggregates alone cannot support a fitted settlement-size model, a complete missing-site count, an artifact forecast or a marine discovery claim. The exact historical inventory lineage and several source supplements remain unresolved. This run added no CI/CD, scheduled task, external publication or field intervention.
