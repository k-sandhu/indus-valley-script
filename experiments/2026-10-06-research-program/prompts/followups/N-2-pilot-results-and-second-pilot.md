# Follow-up for package N from the coordinator: record the pilot and prepare a second one

The coordinator ran your pilot exactly as `PILOT.md` describes. Twelve Claude Sonnet 5.5 subagents read the six column batches, one fresh session per role and batch, and five Sonnet adjudicators settled the 31 disputed targets. All returns validated. The coordinator then ran `score_pilot.py` (initial and final) and `merge.py` with the commands in `PILOT.md`. The outputs are in `pilot/scored-initial-v1/`, `pilot/scored-final-v1/` and `pilot/merge-summary-v1.json`. The coordinator's account, with the control misses, dispute types, token ledger and full-run projection, is `pilot/PILOT-RESULTS.md`, with `pilot/coordinator-task-ledger-v1.jsonl` and `pilot/coordinator-cost-projection-v1.json`. The raw returns are under `data/raw/2026-10-08-helsinki1979-row-verification/returns-v2/`. Claude Code reports only a combined token total per task, so the returns keep `usage` null and the coordinator ledger holds the totals.

Two later results bear on the next run. Package M's v3 crop rebuild is frozen and evaluated (`experiments/2026-10-07-helsinki1979-digitization/README.md`, `REPORT.md`, `REVIEW-V3.md`), and its full-edition proposals are in `data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-v3/full-v2/proposals.jsonl` in the format of M's `OPTION-B-INTERFACE.md`. Package P (`experiments/2026-10-08-chart-reference-audit/`) corrected the chart reference to v2.1. Its `RECOMMENDED-USE.md` says how your reader charts should take that up.

Add a dated amendment to `PROTOCOL.md`, then:

1. **Record the pilot.** Write the pilot results into `README.md`, `REPORT.md`, `RETROSPECTIVE.md` and `registry-entry.json`, using the scorer outputs and the coordinator's files. Keep the frozen readings and scores unchanged. State the screening outcome (failed on the 95% all-fields control criterion, 16/18 per role before adjudication, 18/18 after). Include the dispute analysis, the 66 rows whose only open values are candidate sets, the cost measurements and the projection's assumptions.
2. **Prepare a second pilot, but do not run it.** It should test whether clearer conventions and better inputs cut adjudication without losing accuracy:
   - Amend the reader and adjudicator instructions. Coincident stroke pairs (8/764, 9/765, 10/766, 543/769, 501/768 and any others P lists) always stay as sets. The hatched cells 596 and 454 are `hatched_span`. Codes come from the printed chart labels in v2.1.
   - Build a new reader-chart version with v2.1 labels and a confidence notice.
   - Use v3 proposals.
   - Let the protocol choose between proposal-assisted Reader 1 and two blind readers. The pilot showed no speed gain from proposals.
   - Choose one or two fresh pages by a seeded rule. Exclude every page used in any evaluation, development set or the first pilot, and every v3 blind page.
   - Keep hidden controls. Use controls from the v3 adjudicated reference only if the protocol explains how they avoid the vocabulary change, or draw them from the v2 reference.

   Write the packets under a new dated raw directory. Put a `PILOT-2.md` beside `PILOT.md` with the exact commands, and the success criteria in the protocol before any reading exists.
3. Make sure `score_pilot.py` and `merge.py` can take a coordinator usage ledger of combined token totals, so cost is computed from measured values instead of nulls. Leave the frozen first-pilot outputs unchanged, and write any rerun to new paths.

Do not write inside packages M, O or P. Keep raw renders local. Follow `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Finish with a short report of what changed and the second pilot's design.
