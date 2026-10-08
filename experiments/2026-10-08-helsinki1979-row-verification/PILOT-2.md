# Coordinator instructions for pilot 2, 8 October 2026

Pilot 2 is prepared and unrun. Two blind roles each receive four column packets on PDF152 and PDF162, with 144 target locators and twelve hidden controls per role. Every packet has 36 targets and three supplementary items. The [preparation](pilot-2/2026-10-08-v1/preparation.json) records the eight packet paths/hashes, v3 proposal pin, chart version and selection hash. The [dated protocol amendment](PROTOCOL.md) fixes the revised screen before any reading.

## Deliver only the permitted material

The local packet run is `data/raw/2026-10-08-helsinki1979-row-verification/pilot2-2026-10-08-v1/`. Its `reader-1/` and `reader-2/` roots contain revised instructions, complete v2.1 charts, original chart pages and four batches: `pdf152-c0`, `pdf152-c1`, `pdf162-c0`, `pdf162-c1`. Neither role receives proposals. `coordinator/` holds control answers, selection/exclusion reasons, filtered-control audit and selected original v3 proposals. Its contents must stay hidden. `adjudication/` currently holds revised instructions and a pending notice; actual dispute packets will be generated later.

Run eight fresh sessions, one per role and column. Give each session only its assigned batch, its role's `INSTRUCTIONS.md` and `charts/`. Use separate permitted input roots or access restrictions so sibling returns, coordinator files and the checkout are unavailable. Assign a unique helper root under `data/raw/2026-10-08-helsinki1979-row-verification/pilot2-helpers-2026-10-08-v1/<role>/<batch_id>/`. A session previously exposed to these references must disclose that exposure and be replaced for independent control measurement. Provider and model choice remain model independent.

The assignment is: “Follow INSTRUCTIONS.md. Read every item in the assigned packet and inventory its complete source column. Both roles are blind. Return the supplied JSON envelope with actual provider/model/version/run, UTC timing, elapsed seconds and available usage. Save only to your assigned helper/return location. Maximize reader comprehension; explain observations directly in connected prose, keep shared assumptions together, and avoid repeated corrective comparisons or warnings.” Readers preserve mandatory coincident sets and use `hatched_span` for 596/454. They inspect printed chart labels when needed and record cell identity beside uncertainty.

Freeze the eight initial returns at `data/raw/2026-10-08-helsinki1979-row-verification/pilot2-returns-2026-10-08-v1/<role>/<batch_id>.json`. Actual readings declare `Frozen evaluation`. Leave unknown input/cached/output categories null with a reason. Write measured task totals in a separate JSONL at the returns root, `coordinator-usage.jsonl`. Each record needs role, batch, matching run ID, `combined_tokens` or `subagent_total_tokens`, and its measurement source. Include `duration_ms` or `elapsed_seconds`, provider/model/version and packet/return hashes when available. Record task totals rather than an encompassing parent-session total, which would double count child tasks. No fabricated usage or price is needed.

## Validate, score and adjudicate

Run the following from the repository root. PowerShell variables name only N-owned paths. Repeated commands need fresh versioned output paths; scripts refuse existing outputs.

```powershell
$nPython = 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe'
$nCode = 'experiments/2026-10-08-helsinki1979-row-verification'
$nRaw = 'data/raw/2026-10-08-helsinki1979-row-verification'
$nRun = "$nRaw/pilot2-2026-10-08-v1"
$nReturns = "$nRaw/pilot2-returns-2026-10-08-v1"
$nAdj = "$nRaw/pilot2-adjudication-2026-10-08-v1"
$nUsage = "$nReturns/coordinator-usage.jsonl"
$nResult = "$nCode/pilot-2/2026-10-08-v1"

foreach ($nRole in @('reader-1','reader-2')) {
    foreach ($nBatch in @('pdf152-c0','pdf152-c1','pdf162-c0','pdf162-c1')) {
        & $nPython -B "$nCode/validate_return.py" --packet "$nRun/$nRole/$nBatch/packet.json" --return-file "$nReturns/$nRole/$nBatch.json" --out "$nResult/validation-$nRole-$nBatch-v1.json"
        if ($LASTEXITCODE -ne 0) { throw "Invalid return: $nRole $nBatch" }
    }
}

& $nPython -B "$nCode/score_pilot.py" --run $nRun --returns $nReturns --usage-ledger $nUsage --out "$nResult/scored-initial-v1" --full-rows 11702 --printed-columns 328 --workers-per-role 6 --total-concurrency 12
if ($LASTEXITCODE -ne 0) { throw 'Initial scoring failed' }

& $nPython -B "$nCode/adjudicate.py" --run $nRun --returns $nReturns --out $nAdj
if ($LASTEXITCODE -ne 0) { throw 'Adjudication preparation failed' }
```

The scorer reports initial role accuracy, target agreement, matching unresolved sets, adjudication load and complete-column inventories. It joins measured coordinator totals without changing the frozen returns. Reader or inventory differences, including control disagreements, enter adjudication. Give fresh adjudicators only `$nAdj/adjudicator/` and their assigned batch. The generator selects the new instructions, strips reader identities and randomizes A/B independently for each item. Both initial readers were blind; the labels identify neither model nor run. Each adjudicator must return a full row with `adjudication_basis` and preserve source ambiguity. Store those returns at `$nReturns/adjudicator/<batch_id>.json` and append their actual usage entries to a new frozen version of the ledger if the initial ledger has already been frozen. Set `$nUsage` to that complete ledger path before final scoring.

```powershell
& $nPython -B "$nCode/score_pilot.py" --run $nRun --returns $nReturns --adjudications $nAdj --usage-ledger $nUsage --out "$nResult/scored-final-v1" --full-rows 11702 --printed-columns 328 --workers-per-role 6 --total-concurrency 12
if ($LASTEXITCODE -ne 0) { throw 'Final scoring failed' }

& $nPython -B "$nCode/merge.py" --run $nRun --returns $nReturns --adjudications $nAdj --usage-ledger $nUsage --out "$nRaw/pilot2-merge-2026-10-08-v1" --summary-out "$nResult/merge-summary-v1.json"
if ($LASTEXITCODE -ne 0) { throw 'Merge failed' }
```

Check `metrics.json.revised_screening`, `final_control_accuracy`, `progress.invalid_returns`, `cost.measured_totals`, `cost.coordinator_ledger` and `cost.column_task_projection`. All twelve controls per role must be correct to reach 95%; the target queue must be at most 10%, so at most fourteen of 144 paired targets may require adjudication. The final controls must match twelve of twelve, every assigned return must validate, and source inventories must reconcile. Matching code sets remain candidate-only unresolved records and do not inflate the dispute count. Merge stages only resolved rows and imports none; L still requires reviewed object/surface concordance.

Combined task tokens support workload estimates. They do not supply a dollar price. The column projection uses 11,702 numbered occurrences, 328 columns and ideal total concurrency 12; change `--total-concurrency` for another scenario. The original row/page projection separately uses `--workers-per-role`. These settings affect planning outputs, not reader execution. Neither selected page has a proposed continuation, so continuation effort remains outside this pilot's direct coverage. Both pages come from the beginning-sorted section; compare results as a revised-workflow screen on these pages, without attributing a change to proposals, chart corrections or blinding separately.

## Regenerate and review without readings

```powershell
& $nPython -B "$nCode/prepare_pilot2.py" --out "$nRaw/pilot2-reviewer-repeat-v1" --summary-out "$nResult/reviewer-preparation-v1.json"
& $nPython -B "$nCode/check_followup.py" --raw-out "$nRaw/pilot2-reviewer-check-v1" --out "$nResult/reviewer-check-v1.json"
python -B tools/review_prose.py --path $nCode --no-write
```

Regeneration reads the pinned full v3 JSONL and filters two pages; it performs no inference or reading. Compare selected pages, control sample indices, all source-image/chart hashes and counts. Creation time, elapsed preparation time, code hashes and packet paths can differ. If M/P inputs change, preserve the old run and record a new protocol/version rather than treating changed inputs as a replay.
