# Proposed question-card updates

## Q-0027 Check catalogue line divisions against the source plates

Status: `done` for the 75 divided faces with CISI 1 and 2 plate crops; the 43 faces without a crop (32 CISI 3 numbers, 11 without a CISI number) wait for CISI 3.1 and 3.2 or for excavation-report photographs.

Outcome note, 20 October 2026: Three independent readers counted the sign groups on every divided face with a crop. 65 divisions are confirmed, 10 unclear and none contradicted. The Lipi visual code lists a divided legend's lines in the reverse of the catalogue's reading order, and the export's `signs_reading_rtl` is its exact reversal on all 118 divided faces; the upper line is read first on 43 of the 46 faces placed with high or medium confidence, and the lower line first on H-60, H-97 and K-16. The second group is a wrapped line on 57 faces and set apart in the field on 7. Evidence: `experiments/2026-10-20-seal-legend-units/plate-audit/audit-table.csv`, `audit-summary.json`, `DATA-UPDATE.md`.

## Q-0028 Train a segmenter on the catalogue's line divisions

Status: `done`.

Outcome note, 20 October 2026: A conditional-logit model of where a scribe breaks a line, trained on the divisions with features from corpus statistics, found 79.4% of held-out divisions while cutting 7.7% of other positions on the 33 plate-ordered faces (J = 0.718, interval 0.586–0.838), against 0.348 for the saved Dirichlet-process segmenter; both pre-stated rules pass, and 200 label permutations never exceed 0.222. Trained the same way on Ur III seal legends, it beats cutting everywhere on word divisions (F1 0.618 against 0.557) with 91% precision and 47% recall. Its frozen units and closing stock of 49 formulae are applied by written rules on which an independent agent agreed completely, and four prospective predictions are hashed. Evidence: `experiments/2026-10-20-seal-legend-units/REPORT.md`, `run-2026-10-20/cv-summary.json`, `PREDICTIONS.md`.

Follow-on card (proposed): "Score the frozen closing-formula predictions on the CISI 3.1 seals", data access purchase-dependent (Q-1008), compute hours, with `score_prospective.py` as the only scorer and the transcription format in its docstring.
