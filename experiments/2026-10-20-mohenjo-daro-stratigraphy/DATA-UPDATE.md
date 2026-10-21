# Proposed data and ledger updates

For the maintainer to fold into [knowledge/DATA.md](../../knowledge/DATA.md), [bench/spent.json](../../bench/spent.json) and the question cards after review. This package acquired no new source; it derived fields from the 13 October join of the Mackay and Marshall tables and spent one new statistic family on two populations.

## Spending ledger

Add this package's split to `bench/spent.json`. The entry below is the one the loader wrote to the package ledger ([shots/spent-ledger.json](shots/spent-ledger.json)), with one confirmation read logged:

```json
"555e464fb746baef932842a97b1123e8de9cad574c27513a5e9c3ee8bd45d58e": {
  "seed": "2026-10-20-mohenjo-daro-stratigraphy",
  "input_sha256": "ea956d7de4daa7ada65bc02041b07c953afc80a52802718d126b97f2ca5df02d",
  "assignment_sha256": "a047a1c87478680d9d3ceb94dac2283074ba168d45d3df9314165791e185926b",
  "spent_families": ["stratigraphic_level"],
  "reads": ["(copy the single read from shots/spent-ledger.json)"],
  "synthetic": false
}
```

The input is a derived file of the 483 Mohenjo-daro objects joined to Marshall's 1931 table, so a later split of the full Lipi input will not inherit this entry automatically. Both halves of the split were read after the freeze, and the whole Marshall population is spent for `stratigraphic_level`. Mackay's DK-area population (625 seals with a level) was the discovery population and is examined for the same family. A later test of legend against level at Mohenjo-daro needs seals outside both tables, such as CISI 3.1 objects from later excavations with published levels.

We suggest a note in `bench/shots/README.md` that a package may give the loader a derived input holding only its confirmation population, and read both halves after the freeze, when its partition is not a random one. The access log then records every read of that population.

## Derived fields

[build_inputs.py](build_inputs.py) gives each joined seal a numeric height in feet with its datum, from the tracked join table: Mackay's level against the DK datum (SD bench-mark levels plus 2.2 ft) for 639 seals, and minus Marshall's depth below the modern surface for 440 seals. Marshall's printed depth parses as feet and inches for 451 of 492 joined rows; 33 rows print no depth, 7 print "surface" and one prints "B.P.". The derived file also assigns each Marshall seal a depth stratum (area with the export's section where the cell holds at least 15 seals) and a within-stratum height rank. These values stay local in `data/raw/2026-10-20-mohenjo-daro-stratigraphy/` with the legends; the counts are in [inputs/inputs-summary.json](inputs/inputs-summary.json).

For [Q-1022](../../knowledge/questions/Q-1022-depth-normalization.md): the Marshall depths are now parsed for the joined rows, and the rule for comparing them is the section, since depth below the modern surface is not comparable across sections. The bottom and top thirds of Marshall's sections lie at medians of 6 ft and 2.3 ft below the surface, against 10.9 ft between the medians of DK-G's thirds, which bounds how much time a within-section comparison can span. A conversion to metres against one datum for the whole city would need the surface heights of Marshall's sections, which no held source gives.

## Coverage

No coverage figure in DATA.md changes. The proposed line for the 13 October section: "On 20 October the joined levels were used for the first legend-against-level test at Mohenjo-daro ([stratigraphy package](../experiments/2026-10-20-mohenjo-daro-stratigraphy/REPORT.md)); Marshall's depths parse for 451 of 492 joined rows and are comparable only within an excavated section."
