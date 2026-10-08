# 1979 chart-reference audit

Status: Exploratory. The audit reads all 687 printed chart cells and proposes eight primary-code corrections, one class-number correction and removal of all 16 retained lower-code ambiguities. Twenty-one numeric row records change. The resulting code list has no duplicates and covers every class from 1 to 401 in nondecreasing order. These numbers are in [comparison.json](comparison.json), field `summary`; the complete proposed reference is [chart-reference-v2.json](chart-reference-v2.json).

The evidence is a single AI visual reader's transcription of the printed chart. Independent reviewer and expert confirmation remain pending. Code 333 at `p21_c4_r22` retains medium confidence because its ink is worn. The audit supports the new v3 hypotheses 506 to 508, 206 to 208 and 285 to 286, and retains 360 at `20:4:13`. A final larger-crop check corrected this audit's own preliminary 571 decision to 671. [REPORT.md](REPORT.md) gives the digit evidence and [RETROSPECTIVE.md](RETROSPECTIVE.md) records the interruptions and correction.

[impact.json](impact.json) lists each changed consumer location and field. Explicit cell joins change 11 units in eight rows of the v1 60-row reference and eight units in seven rows of the v3 80-row adjudicated reference. The v2 80-row adjudicated reference has zero directly joined changes; 18 units have affected candidate labels without matching cell locations. These remain identity-review candidates. The public release has 21 affected chart rows and 65 v1 / 88 v2 stored prediction alternatives requiring code or rank updates. Package N's inspected chart cards are byte-identical copies of M's v2 cards. No replacement scores were computed.

## Reproduce from the repository root

Use the existing local PDF and atlas metadata listed in [sources.json](sources.json). The scripts require PyMuPDF, Pillow and PyArrow. They set writable library temporary paths within this package's raw directory and write only the two owned roots. The observed environment already provides these dependencies.

```powershell
$auditPython = 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe'
& $auditPython -B experiments/2026-10-08-chart-reference-audit/audit.py render
& $auditPython -B experiments/2026-10-08-chart-reference-audit/audit.py review
& $auditPython -B experiments/2026-10-08-chart-reference-audit/extra-crops.py
& $auditPython -B experiments/2026-10-08-chart-reference-audit/audit.py compare
& $auditPython -B experiments/2026-10-08-chart-reference-audit/impact.py
& $auditPython -B experiments/2026-10-08-chart-reference-audit/verify.py
& $auditPython -B tools/review_prose.py --path experiments/2026-10-08-chart-reference-audit --no-write
```

For a quick mechanical replay, run the last four commands after `extra-crops.py`. The scripts reproduce the saved observations and joins; a fresh visual reading requires looking at the chart images. [visual-readings.json](visual-readings.json) preserves the first pass and [reinspection-decisions.json](reinspection-decisions.json) records subsequent decisions. [cell-observations.json](cell-observations.json), `rows[*]`, gives each final class, code, confidence, crop and evidence note.

## Files and local witnesses

The owned code is [audit.py](audit.py), [extra-crops.py](extra-crops.py), [impact.py](impact.py) and [verify.py](verify.py). The remaining records are this README, [PROTOCOL.md](PROTOCOL.md), [REPORT.md](REPORT.md), [RETROSPECTIVE.md](RETROSPECTIVE.md), [sources.json](sources.json), [registry-entry.json](registry-entry.json), the numeric and impact JSON files linked above, [consumer-input-integrity.json](consumer-input-integrity.json), [verification.json](verification.json) and [file-inventory.json](file-inventory.json). The registry proposal has not been inserted into the shared registry.

All new source pixels and extracted benchmark records remain in [the local raw directory](../../data/raw/2026-10-08-chart-reference-audit/). It contains two full-page 6x renders, 687 cell crops at 8x, 40 first-pass sheets, 56 full-cell crops at 16x with seven review sheets, 19 distinct digit crops at 24x with five comparison sheets, acquisition/render manifests, three extracted release JSON files, a five-file preliminary-output history, and the prose-scan record. The exact file paths and hashes are enumerated in [file-inventory.json](file-inventory.json); the inventory excludes its own hash.

The reviewer should rerun `compare`, `impact.py` and `verify.py`, inspect all 21 changed numeric rows and the 16 resolved ambiguities, compare the disputed 360, 698 and 671 digits with their documented neighbors, and sample unchanged cells from both pages. Review the 18 v2 and 31 v3 units flagged without matching candidate-cell identities before any consumer migration. [verification.json](verification.json) records mechanical checks; source-number decisions remain Exploratory.
