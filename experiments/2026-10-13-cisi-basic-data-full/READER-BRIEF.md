# Reader brief: transcribing a block of CISI basic data

You are transcribing part of the "basic data" table of a printed catalogue of Indus inscribed objects, the *Corpus of Indus Seals and Inscriptions* (CISI). Volume 1 (Joshi and Parpola 1987) covers collections in India, volume 2 (Shah and Parpola 1991) collections in Pakistan. Each volume ends with a table that gives, for every object it illustrates, the catalogue number and four further columns. You will be given the images of one block, which is one half-column of one printed page, cut into strips from top to bottom. Neighbouring strips overlap by about two lines, so an entry near a cut appears twice; transcribe it once.

## The five columns

1. **CISI number**: a site prefix and a number, such as `M-nnnn`, `H-nnn`, `L-nn`, `K-nn` or `Rhd-nn`. When the pieces of a broken object carry different numbers, the entry is printed on several piece lines, with `(1)`, `(2)` after the CISI number or alone on the following lines.
2. **FC number**: a four-digit number from the Finnish concordance (Koskenniemi and Parpola). Keep leading zeros (`0nnn`).
3. **Excavation number or corresponding data**: an area code and number of forms such as `DK nnnn`, `DK-C nnnn`, `HR nnnn`, `VS nnnn`, `UPM/MD-nnn`, `L nnn`, `SD nnnn`, `B nnn` or `E nnnn`; `???` where the catalogue has no data. Volume 1 marks some numbers with `(o)` (written on the object) or `(t)` (from the excavation report's tabulation), and may give two numbers for one object; keep everything as printed.
4. **Museum and registration numbers**: of forms such as `MD nnn`, `MD nnn, 55.nn`, `L, P-nnnII`, `NMP 50.nnn`, `EXB nnnn`, `ASI 63.10.nnn`, `NMI nn` or `IM A nnnn`; several numbers are separated by commas or listed on continuation lines.
5. **Photograph sources**: forms such as `JL nnn; a: P nnn`, `AV nnn, a: P nnnn`, `HU nnn; a: Si.12 p.nn:nnn` or `a: FEM, pl. lxxxvi, nnn`.

## Output format

Write a plain UTF-8 text file. The first line is a comment:

```text
# <pass>, CISI <1 or 2> printed p. <page> (PDF <pdfpage>), block <block id>
```

Then one line per catalogue entry, in printed order, with the five columns separated by ` | ` (space, vertical bar, space). In these examples `n` stands for a digit:

```text
M-nnnn | nnnn | DK nnnn | MD nnn | JL nnn; a: P nnn
M-nnnn (1) // (2) | nnnn | HR nnnn | MD nnn // MD nnn | JL nnnn, // JL nnn; a: Si. 12:nnn
```

- Keep the printed text: spelling, punctuation, spacing of codes and abbreviations. Do not expand or normalize.
- A column that runs onto a continuation line of the same entry is joined with a single space.
- When an entry is printed as several piece lines, join the piece lines of each column with ` // ` in printed order, and write the piece markers in column 1 as printed (`M-nnnn (1) // (2)`). Leave a piece's cell empty if nothing is printed there.
- Leave a cell empty if the column is blank for that entry.
- Any character you cannot read with confidence goes in square brackets: `[3/5]` for two candidates (put the likelier first), `[?]` for an unreadable character, `[??]` for an unreadable stretch. If a whole number could be read two ways, write `[candidate_a/candidate_b]`. Bracket freely: a bracket is never an error, a confident wrong digit is.
- Square brackets printed in the catalogue itself are rare; if you meet one, write it as `{` `}` and say so in a comment line.
- Bold or italic type: ignore it unless the key on the page makes it meaningful; do not mark it.
- Lines that are not entries (page headings, the key, abbreviation lists, corrigenda) are not transcribed in a block file, except where your assignment says otherwise.
- If an entry continues from the previous block or onto the next, transcribe what is in your strips and add a comment line `# continues` or `# continued` after it.
- You may add comment lines starting with `#` anywhere, for example to note a damaged area of the scan.

## Rules

Read only the strip images you are given (and the full-page render, if your assignment names it, for orientation). Do not open any other file in `data/raw/2026-10-13-cisi-basic-data-full/` or in the CISI 2 pilot's directories, and do not consult the local corpus (`data/normalized/`, `data/lipi/`), the older website export, the PDF's text layer, any other transcription or the web. Nothing is filled from another source: the value of this reading is that it is independent. Zoom into a strip (crop and enlarge it) as often as you like.
