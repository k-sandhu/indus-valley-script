# Adjudicator brief: deciding disagreements between two readings

Two readers transcribed each block of the CISI basic-data table independently. Where their readings of a cell differ, you decide what the page prints. Read [READER-BRIEF.md](READER-BRIEF.md) first: it defines the five columns, the line format and the bracket convention (`[a/b]` for two candidates, `[?]` and `[??]` for unreadable characters, `{ }` for brackets printed in the catalogue).

## Inputs

For each block you are assigned, the list of disagreements is `data/raw/2026-10-13-cisi-basic-data-full/assembled/compare/<block>.todo.json`. Each record gives the CISI number, the column (`col1` to `col5`, or `row` when an entry or a corrigenda line was read differently as a whole), the two readings `pass1` and `pass2`, and the strips where the entry probably appears. The strip list is an estimate from the entry's position: if the entry is not there, look in the neighbouring strips of the same block (`s01.png`, `s02.png`, …, and for blocks with tails also `t01.png`, `t02.png`, … in the same directory), or crop the full page render `data/raw/2026-10-13-cisi-basic-data-full/pages/<volume>-pdf<NNN>.png` (CISI 1: PDF = printed page + 36; CISI 2: PDF = printed page + 35). Crop and enlarge as much as you need with PIL, and save crops under `data/raw/2026-10-13-cisi-basic-data-full/crops-adjudication/`.

Work strip by strip: group the records of a block by the strip their entry is in, open each strip once, crop and enlarge the rows you need, and decide every record in that strip before moving on. Look at the printed cell itself every time; do not decide by majority, by plausibility or by the pattern of neighbouring entries. Do not open the local corpus (`data/normalized/`, `data/lipi/`), the older website export, the PDF's text layer, the pilot's readings or any other transcription.

## Decisions

Write one file per block, `data/raw/2026-10-13-cisi-basic-data-full/assembled/adjudication/<block>.adjudication.json`: a JSON list with one record per todo record, in the same order, each with these fields:

- `cisi` and `column`, copied from the todo record (for corrigenda, the `line-<n>` identifier).
- `pass1` and `pass2`, copied from the todo record.
- `outcome`, one of:
  - `first-pass-right`: the page prints what pass 1 wrote (`final` = pass 1);
  - `second-pass-right`: the page prints what pass 2 wrote (`final` = pass 2);
  - `both-wrong`: the page prints something else, which you write in `final`;
  - `undecidable`: the scan does not settle it; `final` is a bracketed reading that keeps every candidate the page allows and no other.
- `final`: the cell as printed, in the reader format. For a `row` record it is the whole five-cell line, or `absent` if no such entry is printed; for a corrigenda line it is the line's text.
- `note`: one short sentence on what decided it (for example "the third digit has the closed bowl of a 6 at 3x").

A reading that brackets the right answer among its candidates is not wrong, but when the page decides the cell, prefer the definite reading: if pass 1 bracketed a digit as `[3/5]`, pass 2 wrote a definite 3 there, and the page clearly prints a 3, the outcome is `second-pass-right`. When the passes differ only in spacing or punctuation that the page shows clearly, decide it like any other cell. Keep the printed text as printed, including evident misprints.

## Report

When every assigned block has its file, report back in plain connected prose (maximize reader comprehension; explain directly; keep shared assumptions together; avoid repeated corrective comparisons or warnings): the number of decisions per outcome, the cells you could not decide and why, any todo record whose entry you could not find on the page, any systematic difference between the two readers you noticed, and the paths you wrote. Do not paste cell values into the report beyond what is needed to describe a problem.
