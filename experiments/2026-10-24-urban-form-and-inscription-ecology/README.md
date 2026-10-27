# Indus towns through rebuilding

We compared twelve towns through their reported building sequences, materials, structures, locations and documentary contexts. The strongest recurring similarity is the persistence of shared streets, drains, entrances and boundaries while adjacent buildings and activities changed. Banawali supplies explicit clearance and replanning after earlier occupation; Kanmer and Farmana supply named additions within established layouts. These ordered changes provide a stronger comparison than one final plan for each town.

The register contains 287 source-qualified assertions, 134 quantity rows and 42 source-use records. It joins twelve core towns and one Harappa-hinterland relation, with 38 checked file paths representing 36 distinct held hashes. Counts preserve their excavation scope, reconstruction status and phase. The reference index identifies relevant assertions; completeness has not been assessed. We have not assembled a comparable census of buildings or documentary objects across the twelve towns.

## Read and view

The final illustrated book has 74 pages and 23 source-linked graphics. The 26-slide presentation includes 13 editable charts, 13 editable tables and source notes on every slide. The separate graphic atlas supplies all 23 figures in PNG and SVG, with captions, source coordinates and validation records. All large products remain local on D:.

| Product | Physical path |
|---|---|
| Illustrated study | `D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/book/run-v4/indus-towns-study-2026-10-24-v4.pdf` |
| Editable presentation | `D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/presentation/output/indus-urban-form-2026-10-24-v2.pptx` |
| Graphic atlas | `D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/visuals/run-v7/urban-form-visual-atlas-run-v7.zip` |
| Delivery bundle | `D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/delivery/run-v1/indus-town-study-package-2026-10-24.zip` |

Start with the [report](REPORT.md), then use the [town profiles](COMPARISON.md), [quantity register](quantities.csv) and [source-use bibliography](SOURCES.md) to follow a claim to its source. The full [assertion JSON](run-v3/observations.json) preserves structured quantities, uncertainty, original phases and missing reasons. The [methods](METHODS.md) explain modern spatial, construction and chronological approaches and which inputs each requires. The [prospective design](TEST-DESIGN.md) separates architectural observations from documentary labels and sets the conditions for a deciding test.

The towns are Mohenjo-daro, Harappa, Dholavira, Lothal, Chanhudaro, Kalibangan, Banawali, Rakhigarhi, Surkotada, Kanmer, Shikarpur and Farmana. Eleven continue Q-1032's case frame. Farmana adds a smaller settlement with unusually explicit named alterations. [DATA-UPDATE.md](DATA-UPDATE.md) records new fields, source acquisition, coverage changes and unchanged global object coverage. The prior town-axis measurements, north references and horizon assumptions remain in their original package.

## Claims and tests

The new conjectures state that common rules preserved shared routes through rebuilding, sealings recorded handovers between urban groups, and repeated Harappa tablets recorded obligations for shared works. Their initial credences are 0.55, 0.35 and 0.10. The last is the long shot. Each card credits predecessors, distinguishes rival explanations and supplies a kill condition. These are exploratory claims over examined evidence. [EXPOSURE.json](EXPOSURE.json) records the prior research and unchanged spent ledger; the attached shots benchmark checks the workflow on generated data only.

The documentary comparison distinguishes display, manufacture, fastening, use and discard. It includes scoped aggregates from all 225 printed Dholavira seal-context rows and sixteen pinned earlier outputs, including failed predictions. Detailed source extraction remains local-only. The new joins add no adjudicated physical objects to the global census.

## Reproduce and inspect

Run from the repository root with Python 3.13 and the local sources restored through [LOCAL_STORAGE.md](../../LOCAL_STORAGE.md). [ENVIRONMENT.json](ENVIRONMENT.json) records runtime versions. Use a new output directory for a new run; preserved endpoints reject replacement.

```powershell
python -X utf8 experiments/2026-10-24-urban-form-and-inscription-ecology/build_register.py --out experiments/2026-10-24-urban-form-and-inscription-ecology/reproduction-run-v1
python -X utf8 experiments/2026-10-24-urban-form-and-inscription-ecology/compare_enclosures.py --out experiments/2026-10-24-urban-form-and-inscription-ecology/reproduction-shapes-v1
python -X utf8 experiments/2026-10-24-urban-form-and-inscription-ecology/synthetic_diagnostics.py --out experiments/2026-10-24-urban-form-and-inscription-ecology/reproduction-synthetic-v1
python -X utf8 experiments/2026-10-24-urban-form-and-inscription-ecology/verify_study.py --out experiments/2026-10-24-urban-form-and-inscription-ecology/reproduction-validation-v1.json
```

[CHECKS.json](CHECKS.json) records the source, computation, product and repository checks. The [visual module](modules/visuals/README.md) and [presentation module](modules/presentation/README.md) give rebuild and native editing checks. The book builder uses the final figure manifest and requires a new D: output path and tag. The review responses and [retrospective](RETROSPECTIVE.md) preserve failed integration and graphic runs. [AUTHORSHIP-CORRECTION.md](AUTHORSHIP-CORRECTION.md) corrects an unsupported model-variant label in the preserved protocol and draft cards.

The strongest reading is that Indus towns maintained shared frameworks through substantial local rebuilding. Independently dated histories of the same routes, entrances and adjacent structures, joined to primary documentary contexts, can decide whether that persistence reflects common rules and whether writing adds a specific institutional explanation.
