# Coordinator instructions for the three-page pilot

Use the **v2 preparation of Package N**, which supplies Package M's **frozen v2 proposals**. The similar version names refer to different things: N v2 refines the packet/return contract before any readings; M's future v3 layout is still a separate input. Source pages are PDF53,83,170, with 216 detected target rows across six columns and 18 distinct reference controls per role. Each of the 12 packets contains 39 items. [Preparation](pilot/preparation-v2.json), `selected_pages`, `target_detected_rows`, `batches`.

## Hand the permitted folders to readers

The actual packet/image payloads are local:

- Reader 1: `data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2/reader-1/`.
- Reader 2: `data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2/reader-2/`.
- Coordinator only: the same run's `coordinator/`, including the control map, answers and selection exclusions.
- Adjudicator: a fresh directory produced by `adjudicate.py` after both initial returns are frozen.

Tracked [Reader 1 instructions](pilot/reader-1/INSTRUCTIONS.md), [Reader 2 instructions](pilot/reader-2/INSTRUCTIONS.md) and [adjudication instructions](pilot/adjudication/INSTRUCTIONS.md) are also copied into the delivery roots. The tracked `PACKETS.json` files list delivery paths and hashes without image or row payloads. Hand each reader its local delivery root only, with the shared charts and its assigned batch. Do not hand readers this guide, the coordinator directory, the checkout or earlier M references. The control rows are unlabelled within packets; their differing page context can suggest supplementary rows, so access separation is necessary and concealment remains imperfect.

Launch six separate tasks for each role, one for every batch ID: `pdf053-c0`, `pdf053-c1`, `pdf083-c0`, `pdf083-c1`, `pdf170-c0`, `pdf170-c1`. Use a fresh session for each task, a unique helper directory beneath N's local raw directory and no shared scratchpad. Reader 1 may use its proposal file; Reader 2 may use source images and charts only. Claude Sonnet, Codex or another reader can use the same JSON contract. Model diversity is a coordinator choice; separate sessions and input permissions must hold regardless of model.

The minimal assignment is: “Follow INSTRUCTIONS.md in your supplied role root. Read every item in batch `<batch_id>/packet.json`, inventory its complete source column, and return the JSON envelope from return-template.json. Save output only to your private helper/return location. Maximize reader comprehension; explain observations directly in connected prose, keep shared assumptions together, and avoid repeated corrective comparisons or warnings.” Record exact provider/model/version/run and task timing/usage. A reader with prior access to these references must disclose it and be replaced for independent control scoring. The tooling verifies hashes and declarations; task-level isolation still depends on the coordinator's execution environment.

## Collect, validate and score

Store the twelve completed JSON files at `data/raw/2026-10-08-helsinki1979-row-verification/returns-v2/<role>/<batch_id>.json`. Fill actual identity, UTC start/finish, elapsed seconds and available token/billing records. Set `evidence_status=Frozen evaluation`. `input_tokens` includes cached input; unknown values stay null with `unavailable_reason`. Finished returns are immutable inputs. Corrections go in a fresh returns root with a recorded reason, and any affected adjudication packets must be rebuilt.

All commands below run from the repository root. Every output must be a new path. Python needs NumPy, PyMuPDF and the existing M inference environment for regeneration; no model-specific API is required.

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/validate_return.py --packet data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2/reader-1/pdf053-c0/packet.json --return-file data/raw/2026-10-08-helsinki1979-row-verification/returns-v2/reader-1/pdf053-c0.json --out experiments/2026-10-08-helsinki1979-row-verification/pilot/validation-r1-pdf053-c0-v1.json

& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/score_pilot.py --run data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2 --returns data/raw/2026-10-08-helsinki1979-row-verification/returns-v2 --out experiments/2026-10-08-helsinki1979-row-verification/pilot/scored-initial-v1 --workers-per-role 1

& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/adjudicate.py --run data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2 --returns data/raw/2026-10-08-helsinki1979-row-verification/returns-v2 --out data/raw/2026-10-08-helsinki1979-row-verification/adjudication-pilot-v1
```

The scorer runs validation for every existing return; invalid files appear in `progress.invalid_returns`. `metrics.json` reports per-role and per-batch control accuracy, M-compatible code scoring, target agreement, unresolved matching candidates and adjudication load. `cost-ledger.json` records each actual task's model/run/hash/timing/usage. The generator for adjudication rejects invalid initial returns. Give the adjudicator only `adjudication-pilot-v1/adjudicator/`; its anonymous A/B mapping remains in `coordinator/`. The number of tasks/rows depends on real disagreements. A source-column mismatch escalates its target items and requires a full corrected inventory.

Store adjudicator returns at `returns-v2/adjudicator/<batch_id>.json`. Then run:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/score_pilot.py --run data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2 --returns data/raw/2026-10-08-helsinki1979-row-verification/returns-v2 --adjudications data/raw/2026-10-08-helsinki1979-row-verification/adjudication-pilot-v1 --out experiments/2026-10-08-helsinki1979-row-verification/pilot/scored-final-v1 --workers-per-role 1

& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' -B experiments/2026-10-08-helsinki1979-row-verification/merge.py --run data/raw/2026-10-08-helsinki1979-row-verification/pilot-2026-10-08-v2 --returns data/raw/2026-10-08-helsinki1979-row-verification/returns-v2 --adjudications data/raw/2026-10-08-helsinki1979-row-verification/adjudication-pilot-v1 --out data/raw/2026-10-08-helsinki1979-row-verification/pilot-merge-v1 --summary-out experiments/2026-10-08-helsinki1979-row-verification/pilot/merge-summary-v1.json
```

Resolved, completely covered rows receive an L-compatible staging row; unresolved candidates and locator collisions remain in `merged-records.json`. This invokes no ledger import. An occurrence-qualified physical-object/surface concordance remains necessary for L.

## Cost interpretation and decision

The default projection uses 11,369 provisional detections and one worker for each initial role and adjudication phase. It shows observed setup/control overhead per assigned row and per target row, initial serial task hours, an idealized parallel duration and intervals. Both initial role workloads must be complete before full initial-pass projection. Missing usage blocks that metric; total effort requires actual adjudicator timing. If a monetary rate card is needed, add `--rates <local-json-file>` using the exact contract in [INPUT_CONTRACT.md](INPUT_CONTRACT.md). Do not substitute guessed prices or synthetic fixture usage.

Stop full-run expansion when the [protocol](PROTOCOL.md) screening criteria fail: any wrong control number/classification/count, either role below 95% all-fields control accuracy, any wrong agreeing control pair, or incomplete source inventories. Actual affordability also requires task bills and adjudication effort. Eighteen successes out of eighteen controls give a Wilson lower bound of about 82.4%; three pages and reference controls cannot certify edition-wide accuracy. A convention repair needs a fresh validation sample and a dated amendment.

Package M v3 is not available in this preparation. Use the external-proposal adapter only after reviewing the new geometry and input mapping. Repeated controls in a full run monitor drift and can become familiar to readers; plan fresh controls and specialist sampling before treating their accuracy as a population estimate.
