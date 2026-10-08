# Package P: audit the 1979 sign-chart reference against the printed chart

Owned directory: `experiments/2026-10-08-chart-reference-audit/`. Local raw directory: `data/raw/2026-10-08-chart-reference-audit/`. Python with PyMuPDF (`fitz`), NumPy and Pillow is available; the CUDA environment is `C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe`.

## Why

The project's numeric reference for the sign chart of Koskenniemi and Parpola's *Corpus of Texts in the Indus Script* (1979; CC BY 4.0; `research/corpus/primary/koskenniemi_parpola1979.pdf`, chart on PDF pages 20–21) is `research/chart_reference/manual_numeric_reference.json`, with cell crops in `output/chart_atlas/cells/` (named `p<page>_c<column>_r<row>.png`). Its codes were read by AI models without expert certification, and 16 lower-code ambiguities were retained. It feeds package M's recognizer templates and position-chart cards, the blind references, package N's reader charts, and the `chart_reference` configuration of the public dataset candidate in `experiments/2026-10-08-hf-public-release/release/`.

The option-B verification pilot (package N, `experiments/2026-10-08-helsinki1979-row-verification/`) found a reading error. Two independent adjudicators and a reader reported that the three-tick U card is labelled 206 although the chart prints 208 for it. The coordinator checked the crops. `p21_c6_r1.png` prints class 327 with code 208, but the reference records 206 with high confidence. `p21_c5_r34.png` prints class 326 with the two-tick U, and the reference records 205 with alternatives 206 and 208. `p21_c5_r32.png` prints class 325 with code 205 for the one-tick U. The adjudicators also resolved the underlined comb card `p20_c4_r21` (reference 465 with alternatives 485 and 486) as 486. They argued from the printed digits and from the fact that 465 and 485 label other cells. Their returns are in `data/raw/2026-10-08-helsinki1979-row-verification/returns-v2/adjudicator/`, and the reader returns are beside them in `reader-1/` and `reader-2/`. Read them for their chart observations only.

## Task

Write `PROTOCOL.md` first, then:

1. **Re-read every printed code.** Render chart pages 20–21 from the PDF at a high resolution, at least 6 pixels per point, and read the printed class number and sign code of every one of the 687 cells from the image. Do not use the PDF text layer for values; it is OCR noise. Use the printed class sequence, which increases down each column, and the code sequence as consistency checks. Also check that no code labels two different drawings. Record each cell's reading, confidence and the visible evidence for any digit that is hard to read. Save renders and zoomed digit crops under the raw directory.
2. **Compare with the reference.** List every cell where your reading differs from `code` or from `alternatives`, every retained ambiguity you can now settle, and every one you cannot. For each, give the evidence: digit shapes, uniqueness of codes, class sequence, and the shape of the drawing. Treat the coordinator's observations above as hypotheses to test, not as facts.
3. **Write a corrected reference** as a new file, `chart-reference-v2.json` in the owned directory, with the same schema as the original plus a `change_log` per changed cell. Leave the original file and `output/chart_atlas/` unchanged. Mark the result "Exploratory" until a reviewer and, ideally, an expert confirm it.
4. **Measure the impact** without changing any frozen output:
   - which units in the v1 60-row and v2 80-row benchmark references and in package M's v3 blind packet cards would carry a different code under v2;
   - which recognizer templates or position-chart cards in package M use an affected label (list paths, do not edit);
   - which rows of the public release's `chart_reference`, benchmark tables and scorer expectations change;
   - whether package N's reader charts carry the affected labels.
   Recommend how each consumer should take up v2: for example, a new chart snapshot for a future pipeline version, a documented label mapping used as a sensitivity analysis in a new scoring run, and a new release version.
5. Write `README.md`, `REPORT.md`, `RETROSPECTIVE.md` and `registry-entry.json` as for other packages.

Do not write inside packages M, N or O or into `research/chart_reference/` or `output/`. Keep raw renders local. Do not claim decipherment or assign sounds or meanings; this package concerns only the edition's printed numbering. Follow `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.
