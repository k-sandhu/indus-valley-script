# Package N: verifying every row of the 1979 Helsinki corpus (option B)

Owned directory: `experiments/2026-10-08-helsinki1979-row-verification/`. Local raw directory: `data/raw/2026-10-08-helsinki1979-row-verification/`. Python with PyMuPDF (`fitz`) is available; the CUDA environment is `C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe`.

## Purpose

The user chose to produce a verified transcription of Koskenniemi and Parpola's *Corpus of Texts in the Indus Script* (1979; CC BY 4.0; `research/corpus/primary/koskenniemi_parpola1979.pdf`) by having every printed row checked by two independent readers, with a third settling disagreements. Package M (`experiments/2026-10-07-helsinki1979-digitization/`) is rebuilding its cropping step (v3) and will produce proposals for every printed row; until then its v2 proposals are the latest. Read package M's `README.md`, `REPORT.md`, `REVIEW.md`, `repair/2026-10-07-v2/blind/CONVENTIONS.md`, the two v2 blind readings and the adjudication in `repair/2026-10-07-v2/blind/`, and the evaluation in `repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/`. The v2 readers took roughly 45–90 minutes and several hundred thousand tokens per 40 rows; a full run of about 11,369 rows twice is therefore a large cost, and this package's first job is to design a workflow that is accurate and affordable, and to measure it on a pilot before anyone commits to the full run.

## Workflow design

Write `PROTOCOL.md` first. Design the workflow so that:
- Reader 1 verifies and corrects the pipeline's proposal for a row (fast, but exposed to the proposal); reader 2 reads the row blind from the page without any proposal (slower, independent). Rows where both agree are accepted; any disagreement in number, classification, unit count or a unit's strict code goes to an adjudicator who sees both readings and the page but not which is the pipeline's. Consider batching a whole page or column per reading task to cut overhead, and say how the batch size affects accuracy.
- Readers follow `CONVENTIONS.md` and the same JSON row format, so outputs can be scored with package M's evaluator functions.
- A small hidden control set of already-adjudicated rows (from the v2 80-row reference) is mixed into each batch, unlabelled, to measure each reader's accuracy continuously.
- Every reading records the reader identity (model and run), timing and token cost if available, and the packet hash.
- The merge step produces one verified record per printed row with its provenance (agreed, adjudicated, or unresolved with candidate sets), keyed so that package L's ledger import interface can consume it later through a reviewed concordance.

## Build

Implement the tooling: packet generation per page or column (crops with context, the relevant chart cards, the proposals for reader 1 only), reader instructions for each role, validation of returned JSON, agreement computation, adjudication packets, merge, progress tracking and a cost ledger. Readers will be run by the coordinator as separate AI agents (Claude Sonnet and possibly Codex models); your tooling must not depend on which model reads.

## Pilot

Prepare pilot packets for three pages chosen by a seeded rule from pages not used in any evaluation sample or development set (about 200 printed rows), using package M's latest available proposals (v2 now; note that the full run will use v3). Put the packets and reader instructions where the coordinator can hand them to readers, under `pilot/`, with one folder per reader role and one for adjudication. Do not perform the readings yourself. Write `PILOT.md` explaining exactly what the coordinator should run, and a `score_pilot.py` that, once readings exist, computes per-role accuracy on the hidden controls, agreement rates, adjudication load, time and token cost per row, and a projection of the full run's cost and duration with intervals.

Update `README.md`, `RETROSPECTIVE.md` and `registry-entry.json`. Keep raw renders local and do not track replay copies of large outputs.
