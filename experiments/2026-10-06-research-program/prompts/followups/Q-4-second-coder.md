# Follow-up for package Q from the coordinator: integrate the independent second coding

The independent second coding of all 96 targets is complete. Two Claude Sonnet 5.5 subagents in fresh sessions each coded half from your blind packet alone: rows 1–48 and rows 49–96 in template order. The coordinator merged their returns without changing any row into `data/raw/2026-10-08-bonta-review/second-coder-v1/returns/coder2-merged.json`. The part files and their hashes are listed in its `parts`. Confidence counts are 66 high, 23 medium and 7 low, with none unmapped.

The coders raised three points about the instructions:
- `class` in `helsinki_candidates` is undefined; both coders used the chart cell's printed class number, the `rank` field.
- `INSTRUCTIONS.md` names the v1 template, while they used v2 as `ADDITIONAL-FORMS.md` directs.
- One coder notes that Mayig P-numbers equal chart classes up to P372 and run two higher from P375, and that chart cell 369 (class 43) has no Mayig class.

Both reported seeing only file and folder names outside their assignment. Their notes are in the part files. Check the third point against your own reference data.

Add a dated amendment to `PROTOCOL.md` registering the agreement measures and sensitivities before computing them. Then:

1. **Agreement.** Compare your frozen 96-target mapping with the second coding target by target. Report:
   - Mayig agreement as exact singleton match, candidate-set overlap and disjoint sets, with Cohen's kappa where it is meaningful;
   - the same for Wells and Helsinki candidates;
   - agreement split by confidence level and by target type (Table 18 drawing, caption form, field or anchor target).

   List every disagreement with both codings and a short visual note.
2. **Sensitivity instead of forced adjudication.** Rerun every mapping-dependent result under three mappings:
   - your mapping;
   - the second coder's mapping;
   - an agreed-only mapping that keeps targets whose Mayig sets overlap and drops the rest.

   The mapping-dependent results are the field test, the fish units, the lexical tests (all-caption, clear-origin and any held-out subset) and the reading joins. Report each result under all three, and say which conclusions survive all of them. Keep the earlier single-coder outputs frozen, and write new outputs to a new dated folder. If some disagreements change a conclusion, list them for a later adjudicator, and do not resolve them yourself.
3. **Status.** Results that hold under all three mappings can lose the "single-coder" qualifier. Label them as two AI coders without specialist review. Update `REPORT.md` (opening first, ranked by strength), `README.md`, `RETROSPECTIVE.md`, `registry-entry.json`, the claim ledger where a mapping changes a claim's test, and the file inventory.

Do not write to `knowledge/INDEX.md`, `knowledge/experiments/registry.json`, the first-pass directory or the other contributors' `research/literature/2026-10-08-bonta-*` directories. Do not claim or imply that any reading is established. Follow `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Finish with a short report: agreement figures, the results under the three mappings, and what changed.
