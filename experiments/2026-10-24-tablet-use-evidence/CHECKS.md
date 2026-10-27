# Validation and reproduction

From the repository root, the completed commands were:

```text
pdftotext -layout research/literature/sources/meadow_kenoyer_2000_tiny_seals.pdf D:/projects/indus_valley_script/data/raw/2026-10-24-tablet-use-evidence/chapter-layout.txt
pdftoppm -f 14 -l 20 -r 110 -png research/literature/sources/meadow_kenoyer_2000_tiny_seals.pdf D:/projects/indus_valley_script/data/raw/2026-10-24-tablet-use-evidence/source
python experiments/2026-10-24-tablet-use-evidence/build.py
python experiments/2026-10-24-tablet-use-evidence/verify.py
python tools/review_prose.py --path experiments/2026-10-24-tablet-use-evidence --output experiments/2026-10-24-tablet-use-evidence/prose-review-v1.json
python tools/review_prose.py --path experiments/2026-10-24-tablet-use-evidence --output experiments/2026-10-24-tablet-use-evidence/prose-review-v2.json
```

All 76 author accounting and integrity checks pass in validation-v1.json. The initial prose scan flagged one formal word in REPORT.md. We replaced it; the second scan has zero flags. The frozen protocol and scientific outputs were unchanged. A final scan includes this checks note and the retrospective.

The builder and verifier refuse existing endpoints. To reproduce the preserved run, use a separate copy of the owned package with new output names or a fresh directory and supply the held source and the October 2 join ledger. Do not erase this run to reuse the filenames. The builder reads no corpus inscription payload or confirmation cohort. No bench scorer is applicable to this physical-source field audit.

The source manifest identifies the PDF, extracted text, render coordinates and two local record files. We viewed PDF pages 14, 16, 17, 18, 19 and 20; page 15 was rendered but not displayed during this audit. The source's mould examinations remain reported observations, not new microscope work by the project.
