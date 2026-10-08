# Helsinki 1979 row verification: first pilot recorded, second prepared

Pilot 1 **failed the 95% all-fields control screen**: each initial role matched **16/18 controls**, and the final adjudicated readings matched **18/18**. Readers agreed on **185/216 targets**; **31** required adjudication. The final merge has **150 singleton-resolved rows and 66 candidate-only rows**, with zero ledger imports. [Frozen initial metrics](pilot/scored-initial-v1/metrics.json), `control_accuracy`, `target_agreement`, `screening`; [final control replay](follow-up/2026-10-08-pilot2-v1/scored-final/metrics.json), `final_control_accuracy`; [frozen merge](pilot/merge-summary-v1.json), `dispositions`, `ledger_staging_rows`.

The seventeen Claude Sonnet 5.5 tasks used **6,218,955 measured combined tokens** and **23,373.822 summed seconds**. The coordinator's full-run projection has median **336.4 million tokens and 346.0 agent-hours**, with planning intervals **302.2–366.1 million** and **276.1–462.3 hours**. It assumes 328 column tasks per role, the observed disputed-column share and ideal concurrency. Billing remains unknown. [Measured aggregate](follow-up/2026-10-08-pilot2-v1/pilot1-record.json), `measured_combined_tokens`, `measured_agent_seconds`; [original projection](pilot/coordinator-cost-projection-v1.json), `method`, `full_run`.

**Pilot 2 is prepared and unrun**: two blind readers, PDF pages **152 and 162**, **144 targets**, four column batches and **12 distinct hidden controls per role**. It uses v3 crop geometry and keys, clarified coincident-pair/hatched-unit conventions, and new cards labelled from P's v2.1 reference. The cards preserve all 687 glyph panels and identify 33 medium-confidence labels. [Preparation](pilot-2/2026-10-08-v1/preparation.json), `selected_pages`, `target_detected_rows`, `columns`, `controls_per_role`, `chart_cells`; [instructions](PILOT-2.md). Both pages are beginning-sorted and contain no proposed continuations; the pilot's coverage and cost inference have that limit.

## Run and review

The coordinator should use [PILOT-2.md](PILOT-2.md), which gives exact delivery, validation, usage-ledger, scoring, adjudication and merge commands. Its success criteria were added to [PROTOCOL.md](PROTOCOL.md) before page selection. Both initial roles need 12/12 exact controls, all source inventories must reconcile, final controls must match 12/12, and at most fourteen of 144 targets may enter adjudication. Candidate sets remain open values. L still requires reviewed object/surface concordance.

Run these checks from the repository root with fresh output paths:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/prepare_pilot2.py --out data/raw/2026-10-08-helsinki1979-row-verification/pilot2-reviewer-repeat-v1 --summary-out experiments/2026-10-08-helsinki1979-row-verification/pilot-2/2026-10-08-v1/reviewer-preparation-v1.json

& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/check_followup.py --raw-out data/raw/2026-10-08-helsinki1979-row-verification/pilot2-reviewer-check-v1 --out experiments/2026-10-08-helsinki1979-row-verification/pilot-2/2026-10-08-v1/reviewer-check-v1.json

python -B tools/review_prose.py --path experiments/2026-10-08-helsinki1979-row-verification --no-write
```

`score_pilot.py` and `merge.py` accept `--usage-ledger`. They join combined tokens by role/batch/run, preserve null input/output categories and retain returned timing alongside coordinator task duration. The first-pilot replays in [follow-up/2026-10-08-pilot2-v1](follow-up/2026-10-08-pilot2-v1/) reproduce its accuracy and merge without changing frozen outputs. [Ledger contract](INPUT_CONTRACT.md) defines validation and projection fields. The existing Python environment supplies PyMuPDF and Pillow; generation reads v3 proposals without inference. Temporary locations remain under N's local raw directory, and no dependency was installed.

The final follow-up checks pass **62/62**, including all frozen input pins, measured-ledger conservation, invalid-ledger rejection, eight blind packet checks and 687 unchanged glyph panels. The initial check's **59/61** result is preserved beside its correction. [Final checks](follow-up/2026-10-08-pilot2-v1/checks-v3.json), `checks`, `passed`, `glyph_panels_compared`; [initial checks](follow-up/2026-10-08-pilot2-v1/checks-v1.json). Actual source readings in these software checks: **0**. The original workflow regression also passes **123/123** with the amended code. [Regression](follow-up/2026-10-08-pilot2-v1/regression-v4.json), `passed`, `total`.

## Evidence and files

[REPORT.md](REPORT.md) gives findings, dispute counts, timing comparisons and projection assumptions. [RETROSPECTIVE.md](RETROSPECTIVE.md) records preparation, the actual coordinator run and fixes. [sources.json](sources.json) pins source use; [registry-entry.json](registry-entry.json) proposes a Failed pilot entry for coordinator integration. [Follow-up path inventory](follow-up/2026-10-08-pilot2-v1/changed-paths.json) lists every new or changed path. Earlier [PILOT.md](PILOT.md), packets, readings, scores and pending outputs remain historical witnesses.

The hidden-control references and chart labels come from AI readings with shared conventions and no expert check. Agreement measures workflow convergence on target rows; full-edition verification remains unfinished. All source-derived rows, images, proposals and synthetic fixtures remain under `data/raw/2026-10-08-helsinki1979-row-verification/`. Source: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, University of Helsinki, [handle](http://hdl.handle.net/10138/342677), CC BY 4.0. Crops, card arrangement and label strips are recorded modifications.
