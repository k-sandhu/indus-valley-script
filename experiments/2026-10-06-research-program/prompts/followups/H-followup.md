# Follow-up for package H from the coordinator

A Sonnet review is in `experiments/2026-10-06-resemblance-baseline/REVIEW.md`, with an independent recoding of 113 of 130 drawings and sensitivity checks in `review/`. It confirms your computations and the coarse-rule results, and finds that the strict-rule counts change under independent recoding (Indus 1–3 rather than 4, Tifinagh 8–9 rather than 10, Ogham 0–1), that descriptor agreement between the reviewer and your primary coding is 52/113 complete descriptors (46%) with orientation agreeing in 54%, and that six Tifinagh glyphs (U+2D3C, 2D3D, 2D3F, 2D45, 2D47, 2D49) and Tamil sign 10 were misread in the primary rows. Under every rule and coding the Tifinagh control matches at least as many drawings as the Indus subset.

Keep `run-v1` unchanged and add a dated amendment to `PROTOCOL.md`. Then:

1. Recode the misread rows from the source drawings, record each change with its reason, and produce an Exploratory `run-v2`. Report v1 and v2 side by side and the range across the three codings (primary, second pass, reviewer).
2. Define orientation and symmetry operationally so that two coders can apply them, or drop orientation from the strict rule, and say which you chose.
3. Rewrite the first paragraph of `REPORT.md` with size-matched numbers, paired uncertainty (for example the paired tests the review ran) and the stratified pattern by segment band, including the 4–6 segment band where the Indus subset leads.
4. Describe the synthetic null once, accurately, as within-inventory re-drawing, and state that the random-mark generator described in the prompt was not built; build it if you can within this pass.
5. Repair `sources.json` (damaged characters and dropped spaces), add the library MARC record identifying the 2025 PDF as an 8-page booklet, the 145-page edition (ISBN 9788197784255), The Week article URL, and the 2026 Volume I statements the review located (revised counts 551, 1,531 and 2,124, and B. B. Lal's 1962 figures of 89% and 85% at Volume I PDF p. 302).
6. Reconcile the T18 and I24 correction accounts between `README.md` and `RETROSPECTIVE.md`.

Make inter-coder reliability a stated result: a shape descriptor that coders apply consistently is a prerequisite for any resemblance rate. Update `README.md`, `RETROSPECTIVE.md` and `registry-entry.json`, and keep the wording neutral.
