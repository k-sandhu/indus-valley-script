# Follow-up for package Q from the coordinator: the full manuscript PDF

The owner downloaded the second edition and placed it at `data/raw/2026-10-08-bonta-review/papers/A_Partial_Decipherment_of_the_Indus_Vall.pdf`. It has 259 pages and about 2,650 embedded images, which are the Indus sign drawings. Its SHA-256 is `12e8e6b1c427dbdc995e64991d5d0a676b8d397956f28379b046a230a5065f14`, it was produced by Ghostscript 9.26, and it is dated 3 June 2024. It is a third-party publication. Keep it, its renders and its image crops in the local raw directory, and put only identifiers, counts, short quotations and your own analysis in tracked files.

Your revised package stands, and all earlier outputs stay frozen. The PDF removes the main limit you recorded: missing glyphs. Add a dated amendment to `PROTOCOL.md` that registers every new calculation below, with its statistic, null model and decision rule, before you compute it. Then do the following.

1. **Verify the witness.** Confirm the PDF is the same edition as the page-text witness by comparing their text and segment structure, and record the mapping from form-feed segments to printed pages. Cite printed pages from now on.
2. **Sign catalogue.** Extract the image of every sign Bonta assigns a value to: Table 18 and the other value tables, ligatures and compounds, and the field and anchor figures. Build a local sign-image catalogue with page, table, entry, his proposed value and the crop path. Count distinct signs against his stated 55.
3. **Your mapping, frozen first.** Map each catalogued sign to this project's reference classes. Use the Mayig classes with their Wells candidates, as before. Where you can, also map it to the 1979 Helsinki chart cells in `experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json`, whose cell images are `output/chart_atlas/cells/`. Record the basis, candidate sets and confidence. Freeze this mapping with a hash before step 4.
4. **Blind second-coder packet.** The coordinator will have an independent reader map the same signs without seeing your mapping. Prepare a packet under `data/raw/2026-10-08-bonta-review/second-coder-v1/` containing:
   - the sign crops, with neutral IDs and without his values;
   - the reference images the coder needs (the chart cells and any sign-class images available locally);
   - instructions, and a return template in the same format as your mapping.

   Then continue. When the second coding arrives, the coordinator will ask you to measure agreement, adjudicate and rerun.
5. **Reading inventory.** Extract every reading in the paper as data: catalogue label (MH, ICIT or CISI), the sign sequence as catalogued sign IDs in the paper's order, his proposed reading and gloss, its field assignment, and whether he presents it as derivation, illustration or check. Join the readings to the local corpus through CISI or excavation identifiers, never through same-number ICIT joins. Report coverage and the readings that will not join.
6. **Field replication.** Write his field rules (P, M, C and T fields, juncture signs, and how terminal signs behave) as explicitly as the paper allows. Apply them to the local corpus with the mapped signs. Report how many texts segment cleanly under the rules, how many conflict with them and where.
7. **Full lexical test.** Repeat the permutation test over all identifiable readings, not only the six-role panel, using the same dictionary pin and his stated value variants.
   - Classify each value by how he says he derived it: metrology or M field, pictorial, dictionary search against contexts, or later extension. Report the test separately for readings that contain only values not derived from a dictionary search.
   - Where his narrative lets you separate the readings he used to derive a value from those he read afterwards, report a held-out test on the latter.
   - Count every reading attempted, including those he marks as unclear or failed.

   Report what remains of the excess over chance once circularity is removed.
8. **Validation audit.** Use the PDF's figures and text to identify which ICIT readings he presents as checks made after the values were fixed. Report their object overlap with the Mahadevan material.
9. **Ledger and report.** Add the newly identifiable claims and readings to the claim ledger, and update the concordance. Revise the opening of `REPORT.md` with the new results, ranked by strength, and update `README.md`, `RETROSPECTIVE.md`, `registry-entry.json` and the file inventory.

Results that rest on your single-coder mapping are Exploratory until the second coding is integrated; say so beside each one. Do not write to `knowledge/INDEX.md`, `knowledge/experiments/registry.json` or the first-pass directory. Do not claim or imply that any reading is established. Follow `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Finish with a short report: the sign count, the mapping coverage, the location and contents of the second-coder packet, the reading inventory size and coverage, and the main new results.
