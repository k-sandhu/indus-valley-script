# Prepared verification pilot and software checks

The package supplies a complete handoff for separate readers: **216 target locators across PDF pages 53,83,170, six column batches and 18 distinct controls per role**. Its **123/123** software checks pass. No reader accuracy or affordable full-run cost has yet been measured. [Preparation](pilot/preparation-v2.json), `selected_pages`, `target_detected_rows`, `columns`, `controls_per_role`; [checks](verification/synthetic-check-v3.json), `passed`, `total`, `source_readings_performed`.

## Selection and prepared material

The seeded selection excluded 120 of the 159 corpus pages because they appeared in prior samples, count evaluations or development outputs. Eligible section lists contained 5 numbered, 18 end-sorted and 16 beginning-sorted pages. `random.Random(20261008).choice` selected 53,83,170 from those ascending lists, in section order. Each chosen page yielded 72 v2 detections and two columns. These are detector counts; the separate readers must establish the source counts and continuation coverage. [Preparation](pilot/preparation-v2.json), `eligible_page_counts`, `excluded_pages`, `pages`; local `coordinator/selection.json`, `excluded_pages`, `dependency_hashes`.

| Quantity | Prepared v2 value | Exact evidence |
|---|---:|---|
| Detected target locators | 216 | `preparation-v2.json.target_detected_rows` |
| Column batches per role | 6 | `preparation-v2.json.columns` |
| Controls per role, unique within pilot | 18 | `preparation-v2.json.controls_per_role`, `distinct_controls` |
| Assigned items per role | 234 | Sum of six `batches.assigned_rows` for one role |
| Reader packets | 12 | `preparation-v2.json.role_packets` |
| Local prepared bytes | 36,526,470 | `preparation-v2.json.local_bytes`, at freeze before later score diagnostics |
| Packet preparation | 137.1 seconds | `preparation-v2.json.preparation_seconds` |
| Valid actual reader tasks | 0/12 | `pending-2026-10-08-v2/progress.json.valid_reader_tasks`, `expected_reader_tasks` |
| Actual staged ledger rows/imports | 0/0 | `pending-merge-v2.json.ledger_staging_rows`, `real_ledger_imports` |

The packets include full-page and column context, individual row context and exact proposal boxes, original chart/instruction pages and all 12 positional card sheets. Reader 1 alone receives proposals. Images/row payloads, reference controls and synthetic returns are local. Tracked files contain our code, instructions, aggregate results and source/hash manifests. [Generator](generate_packets.py), `make`; [input contract](INPUT_CONTRACT.md).

## Why the workflow checks complete source columns

M's repaired 80-row evaluation accepted 44 crops, matched 59 counts, 62 numbers and 55 classification strings, and passed only one of five criteria. Its random-page reference recovered 1,242/1,286 rows, with misses clustered on two pages. The original 11,369 detections therefore cannot define the complete source universe. The new return contract requires actual source ordinals, missing-row additions, observed page-column counts and complete attached continuation readings. Unmatched columns or ordinal collisions block a complete merge. [M metrics](../2026-10-07-helsinki1979-digitization/repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json), `summary`, `source_row_recall`, `negative_result_criteria`; [coverage implementation](workflow.py), `inventory_complete`; [merge](merge.py), `merge`.

Agreement requires exact strict-code sets and all specified row fields. Matching multi-code sets remain unresolved. An adjudicator sees both readings in randomized A/B order and the source, with role/model and proposal-confidence fields removed. Returned free text can still reveal how a reader worked; role instructions require source observations without proposal comparisons. The execution environment must isolate sessions and input folders; hashes cannot prove blindness. [Adjudication](adjudicate.py), `anonymous`, `prepare`; [protocol](PROTOCOL.md), Roles and row representation, Validation, agreement and adjudication.

## What was checked

The final 123 checks audit all 12 packet hashes, control-label absence, identical role source items, proposal isolation, return validation mutations, ambiguous-set handling, field disagreement routing, anonymous packet generation, candidate/provenance merge, missing-column and duplicate-ordinal blocking, timing/cost arithmetic and L's row schema. Constructed fixtures create one disagreement among 216 fake target rows, then exercise one anonymous adjudication and stage 216 synthetic rows. A second fixture keeps one matching ambiguous code set unresolved and stages the other 215 source-covered rows. Those values test software behavior; their accuracy and costs are simulated inputs, stored in a separate local synthetic directory. All fixture staging rows carry `synthetic=true`. No real ledger import occurs. [Check record](verification/synthetic-check-v3.json), `tests`, `fixture_status`, `source_readings_performed`; [check script](check_workflow.py).

Visual QA inspected a column image, a row-context image and a positional chart card for readability, source context and original chart-cell position. It did not produce annotations or a reference reading. The checked source/asset hashes and preserved chart snapshot support image provenance; sampling three images does not establish every row's cropping correctness. Readers judge each exact box and recover its full source row from context.

## Accuracy and cost still to measure

The current pending score has zero paired targets, null agreement and adjudication rates, no measured task usage and no monetary projection. Pending merge retains 216 unresolved locator records and stages zero. [Pending metrics](pilot/pending-2026-10-08-v2/metrics.json), `target_agreement`, `adjudication_load`, `cost`; [merge](pilot/pending-merge-v2.json), `dispositions`.

Controls comprise one ambiguous and two singleton reference rows per column, sampled without replacement within the pilot. This mixes convention-sensitive rows into every task but changes the reference mixture relative to the full edition. Both roles use the same existing chart and adjudication, so correlated convention errors can survive independent sessions. Full-page context can reveal that a row is supplementary, and previous reader exposure can compromise its control value. Even 18/18 control successes give a Wilson 95% interval of about 82.4–100%; the pilot is a screening and workload measurement. [Protocol](PROTOCOL.md), Selection fixed before outcomes, Pilot metrics, cost and decision.

Once complete returns exist, the scorer reports per-role/per-batch control accuracy, M-compatible candidate scoring, exact target agreement and adjudication load. Timing and token/billing totals include setup and controls; missing categories stay unknown. Initial-pass time/cost projections resample the three sampled pages. Total planning intervals also resample measured adjudication tasks and draw a disagreement rate; Wilson endpoints remain a separate sensitivity. The 11,369 denominator is a provisional workload scenario that omits unknown missed source rows. Parallel duration assumes equal workers per role and does not measure scaling efficiency. [Scorer](score_pilot.py), `costs`; [contract](INPUT_CONTRACT.md), usage fields.

The page sample has no randomized batch-size comparator, so it cannot establish an accuracy benefit from column batching. Future v3 proposals, full-run control refresh, human/specialist review and occurrence/object/surface concordances remain outside this completed preparation. The supplied external-proposal mode accepts a documented M-compatible adapter; a real v3 input was unavailable and has not been validated. [PILOT.md](PILOT.md) gives execution commands and decision criteria.
