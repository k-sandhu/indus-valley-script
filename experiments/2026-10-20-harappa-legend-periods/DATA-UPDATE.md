# Proposed data and ledger updates

For the maintainer to fold into [knowledge/DATA.md](../../knowledge/DATA.md), [bench/spent.json](../../bench/spent.json) and the question cards after review. This package acquired no new source. It derived chronology fields for Harappa's seals from the Lipi export, documented the export's mapping of Vats's strata to HARP periods, and spent one new statistic family on one population.

## Spending ledger

Add this package's split to `bench/spent.json`. The entry below is the one the loader wrote to the package ledger ([shots/spent-ledger.json](shots/spent-ledger.json)), with the single confirmation read:

```json
"b8110b8a92b0895e1406696944459d541c53f45dd8a305dc89f5328b3a68fbcc": {
  "seed": "2026-10-20-harappa-legend-periods",
  "input_sha256": "198241fec78823834baa4faca8487a94e37b6352648dd088e3de418f9c66a05a",
  "assignment_sha256": "71205ceca280a034d6e044b9aed9fd608bde0cc0febc78d4e5247995f4ca7fac",
  "spent_families": ["harappa_period_sequence"],
  "reads": ["(copy the single read from shots/spent-ledger.json)"],
  "synthetic": false
}
```

The input is a derived file of the 175 Harappa seal families from Vats's Mound F with a stratum, so a later split of the full Lipi input will not inherit this entry automatically. Both halves were read after the freeze, and the whole population is spent for `harappa_period_sequence`. The 109 discovery families (Vats's stratified seals from Mounds AB and D and Areas G, H and J, and HARP's period-labelled seals) were examined for the same family. The 30 Mound F seals with an export period but no stratum were read by no test and remain unexamined for it. A later test of legends against period at Harappa needs seals outside the Lipi export, such as the CISI 3.1 numbers the project does not hold ([Q-1008](../../knowledge/questions/Q-1008-acquire-cisi-3-1.md)), or a different object class: Vats's 471 stratified non-seal faces from Mound F (tablets for the most part) have not been tested against stratum order.

The ledger copy was taken from the working-tree `bench/spent.json` on 20 October (SHA-256 `0d8f863a…`), which already held the fish-context package's uncommitted entry.

## Derived fields

[build_inputs.py](build_inputs.py) gives each of Harappa's 428 seal families a chronology record: the label source (Vats stratum for 242, HARP period for 36, an export period without either for 36, none for 114), the mound read from the `area-section` prefix, the trench cell, the stratum as a number, the export's period label and its order, Vats's printed depth in feet (parsed for 289 families) and the CISI H-number. The records stay local in `data/raw/2026-10-20-harappa-legend-periods/` with the legends; counts are in [inputs/inputs-summary.json](inputs/inputs-summary.json).

## The export's stratum-to-period mapping, for Q-1021

The export assigns a HARP period to every Vats stratum by mound. Over all Harappa faces with a stratum (837 faces), the assignment is one label per mound and stratum:

| Mound | VII | VI | V | IV | III | II | I |
|---|---|---|---|---|---|---|---|
| F | 3B-1 | 3B/C | 3B/C | 3C-1 | 3C-2 | 3C-3 | 3C-4 |
| AB | 3B-2 | 3B/C | 3C-1 | 3C-2 | 3C-3 | 3C-4 | 4 |
| J | | | | | 3C-1 | 3C-3 | 4 |
| G | | | | | 3C-4 | 4 | 4 |
| H | | | | | 4 | 5A | 5B |
| D | | | | none | none | none | none |

The held files do not say who made this assignment or on what basis. Vats (1940, *Excavations at Harappa*, vol. I, pp. 9–10) gives his own scheme: Mound F Strata I–III Late, IV–VII Intermediate, VIII Early; Mound AB Strata I–IV Late and V–VI Intermediate, with the Late strata of AB contemporary with those of F and AB's Stratum I possibly later. The export's offset of one stratum between F and AB (F Stratum IV and AB Stratum V are both 3C-1) agrees with Vats's statement. We propose that [Q-1021](../../knowledge/questions/Q-1021-chronology-calendar-ranges.md) record the table above as the export's mapping, with its source still to be found (Kenoyer and Meadow, or the ICIT documentation, are the likely places), and Vats's own scheme beside it.

For [Q-1022](../../knowledge/questions/Q-1022-depth-normalization.md): Vats's printed depths parse for 289 of 428 Harappa seal families. Within Mound F the stratum follows the depth closely (Stratum VII seals lie about 20 ft down, most Stratum I seals less than 3 ft), so a seal's stratum and its depth within a trench give nearly the same order; this package's results hold with either ([confirmation-v1/results.json](confirmation-v1/results.json), `sensitivity.depth_within_frame`).

## Coverage

No coverage figure in DATA.md changes. A proposed line for the chronology section: "On 20 October Vats's Mound F stratified seals (175 families, Strata VII–I, which the export maps to HARP 3B-1 through 3C-4) were tested for change in their legends ([Harappa legend-periods package](REPORT.md)); the export's mapping of Vats's strata to HARP periods is tabulated in that package's DATA-UPDATE.md, source undocumented."

## A record line for C-0006

C-0006 belongs to the stratigraphy package, so we did not edit it. A record line the maintainer may add: "20 October 2026: at Harappa, Vats's Mound F seals from 3B/C to late 3C keep the closing stock (0.85 early, 0.80 late) while legend length, sign inventory and variant choice change (p = 0.003, 0.0016, 0.0001; [Harappa legend-periods report](../../experiments/2026-10-20-harappa-legend-periods/REPORT.md)). The contrast between a fixed closing and a changing remainder returns at Harappa, with the change in the body of the legend rather than its opening sign (p = 0.39). C-0006's status is unchanged; its frozen test was at Mohenjo-daro."
