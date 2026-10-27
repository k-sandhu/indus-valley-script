# Crop continuity after Harappan urban decline

An initial independent audit and descriptive reanalysis, completed 25 October 2026. Read the [report](REPORT.md) for the findings and [next-study design](NEXT-STUDY.md) for the proposed regional test. The [protocol](PROTOCOL.md) records prior exposure, scope and decision rules.

Current endpoint: [run-v2 summary](run-v2/summary.json), [52-check validation](run-v2/validation.json), [figure](run-v2/seasonal-comparison.svg). The [source manifest](source-manifest.json), [comparison register](comparison-data-register.json), [data update](DATA-UPDATE.md), [work record](RETROSPECTIVE.md) and [validation record](VALIDATION.md) preserve access, coverage and checks. Run-v1 and its original script remain available.

Run from the repository root with Python 3.13 and PyMuPDF, pdfplumber and matplotlib. Raw inputs and detailed tables are local-only. The analysis needs the 100-page accepted manuscript and supplement from the [Cambridge repository](https://api.repository.cam.ac.uk/server/api/core/bitstreams/4c711d77-f084-41ae-848f-141a31a2b855/content), stored as `petrie-bates-2017.pdf` in the raw directory. Verify its hash against the source manifest. Reuse existing inputs; a new acquisition must follow `LOCAL_STORAGE.md`.

```text
python experiments/2026-10-25-crop-continuity/audit.py --raw D:/projects/indus_valley_script/data/raw/2026-10-25-crop-continuity --out experiments/2026-10-25-crop-continuity/run-NEW
python experiments/2026-10-25-crop-continuity/validate.py --raw D:/projects/indus_valley_script/data/raw/2026-10-25-crop-continuity --summary experiments/2026-10-25-crop-continuity/run-NEW/summary.json --out experiments/2026-10-25-crop-continuity/run-NEW/validation.json
python experiments/2026-10-25-crop-continuity/plot.py --summary experiments/2026-10-25-crop-continuity/run-NEW/summary.json --out experiments/2026-10-25-crop-continuity/run-NEW/seasonal-comparison.svg
```

Outputs refuse overwrites. The focal paper's source facts are explicitly recorded in the script with their locators; its unacquired supplement is not a numerical input. Re-running the script checks our extraction and arithmetic, without re-identifying plants or recalibrating dates. Status: `source-review`, verification tier `submitted`.

Attribution: comparison table values originate in C. A. Petrie and J. Bates (2017), *‘Multi-cropping’, Intercropping and Adaptation to Variable Environments in Indus South Asia*, DOI [10.1007/s10963-017-9101-z](https://doi.org/10.1007/s10963-017-9101-z), under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). We extract selected columns, aggregate specified cereal groups and replot seasonal summaries. Original downloaded sources remain local; source-specific rights are recorded in the manifest.
