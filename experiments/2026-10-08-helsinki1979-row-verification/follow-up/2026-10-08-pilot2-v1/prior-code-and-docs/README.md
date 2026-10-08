# Package N: Helsinki 1979 verification workflow

The pilot is prepared for **216 detected target rows on PDF53,83,170**, with six column batches per role and 18 distinct hidden reference controls per role. Each of the 12 packets contains 39 items. Tooling has passed **123/123 synthetic and integrity checks**. No source readings were performed: pilot reader accuracy, agreement, adjudication burden and cost remain **Proposed**. [Preparation fields](pilot/preparation-v2.json), `selected_pages`, `target_detected_rows`, `role_packets`; [checks](verification/synthetic-check-v3.json), `passed`, `total`, `source_readings_performed`.

Reader 1 checks and corrects Package M's frozen v2 proposals. Reader 2 reads independently from images and the full positional chart. Both inventory the complete column, recover missed numbered rows and attach fully transcribed continuation lines. Anonymous adjudication settles disagreements, and merge preserves unresolved candidates and source occurrence provenance. The current real-data merge stages **0 rows** and leaves **216 pending records** because no reader returns exist. [Pending merge](pilot/pending-merge-v2.json), `dispositions`, `ledger_staging_rows`; [pending metrics](pilot/pending-2026-10-08-v2/metrics.json), `reader_evaluation_status`, `target_agreement`, `cost`.

Use [PILOT.md](PILOT.md) to hand separate local role folders to the coordinator's readers and run validation, scoring, adjudication and merge. The actual image/row/proposal/control payloads stay under `data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2/`. Tracked role packet manifests and instructions are under [pilot/](pilot/). N's earlier prepared v1 and pending outputs are preserved; N v2 is the current handoff. Both use M's endpoint v2; M's future v3 proposals require a new pinned run.

## Reproduce and review

Run from the repository root using fresh output paths:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/generate_packets.py --out data/raw/2026-10-08-helsinki1979-row-verification/reviewer-packet-repeat-v1 --summary-out experiments/2026-10-08-helsinki1979-row-verification/verification/reviewer-preparation-v1.json

& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/check_workflow.py --run data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2 --raw-out data/raw/2026-10-08-helsinki1979-row-verification/reviewer-synthetic-v1 --summary-out experiments/2026-10-08-helsinki1979-row-verification/verification/reviewer-checks-v1.json

python -B tools/review_prose.py --path experiments/2026-10-08-helsinki1979-row-verification --no-write
```

The existing environment supplies PyMuPDF, NumPy, OpenCV, SciPy, PyTorch, Pillow and jsonschema. Regeneration reuses M's frozen PDF/chart/weights/digits/calibration and available Tesseract. Scoring, validation and merge need no model inference. The generator redirects M's scratch constant in memory into N's raw directory and disables bytecode writes; it leaves M's algorithm and source files unchanged. `TMP`, `TEMP` and `MPLCONFIGDIR` point to N's local raw `tmp/`. No dependency was installed.

Regeneration must preserve page selection 53/83/170, 216 detections, six columns, 18 controls and identical source images. Timing, creation timestamps and code hashes change with the new preparation; compare source/selection/asset hashes and task counts separately. The complete exclusions are in the coordinator-only selection manifest and its hash is in the tracked preparation. Verify role folders contain no hidden-control answers and Reader 2 receives no proposal file. The check script's synthetic billing/accuracy outputs remain local and explicitly marked Synthetic.

## Evidence and remaining work

[Protocol and pre-reading amendment](PROTOCOL.md), [findings and limitations](REPORT.md), [retrospective](RETROSPECTIVE.md), [input contract](INPUT_CONTRACT.md), [source register](sources.json), [registry proposal](registry-entry.json), [all created paths](file-manifest.json).

The full run's cost remains unmeasured until the coordinator supplies real task usage and adjudicator effort. Three pages give a planning sample; hidden controls share M's chart/reference conventions and may be identifiable as supplementary pages. V3 integration and reviewed occurrence/object/surface concordances remain unverified. No full-corpus verification or Package L import was run.

Source images and numerical witnesses derive from Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, University of Helsinki, [institutional record](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [handle](http://hdl.handle.net/10138/342677), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Raster cropping, card arrangement, proposal generation and numerical verification are recorded modifications. All source-derived payloads remain local under this package's requested handling.
