# Segmentation rules for seal legends, version 2

These rules cut an Indus seal legend into units and name its closing formula. They are frozen with the unit inventory and the closing stock of version 2, whose hashes are in [FROZEN-v2.json](FROZEN-v2.json), and they are applied unchanged to the held set of this package and to every fresh legend scored under [PREDICTIONS.md](PREDICTIONS.md). The lists were produced by a segmenter trained on the catalogue's line divisions ([PROTOCOL.md](PROTOCOL.md), section 5, as changed by [AMENDMENT-1.md](AMENDMENT-1.md)); the rules themselves need only the two lists and can be applied by hand. The rule text is that of version 1 ([RULES.md](RULES.md)); only the lists differ.

## What the rules take

A legend is a sequence of Wells sign numbers in reading order, the first sign read first. A multi-line legend is joined with its top line first. Two lists are needed, both kept locally in `data/raw/2026-10-20-seal-legend-units/frozen-v2/` because they are derived from the Lipi transcriptions:

- the **inventory** (`inventory.json`): every unit of two or more signs, each a sequence of sign numbers. Every single sign is also a unit, so a legend can always be cut.
- the **closing stock** (`closing-stock.json`): the closings, of one to four signs, that the segmenter found after the strongest boundary of seal legends in at least three unrelated groups of objects.

## Rule 1: the closing formula

Look at the final stretches of the legend: its last sign, its last two signs, its last three and its last four, stopping before the stretch would take in the whole legend. The closing formula is the longest of these stretches that appears, sign for sign and in the same order, in the closing stock. If none of them appears there, the legend has no stock closing, and Rule 2 is applied to the whole legend.

For example, if the stock holds both `740` and `176 740`, a legend ending `… 176 740` closes with `176 740`; a legend ending `… 342 740` closes with `740`, unless `342 740` is itself in the stock.

## Rule 2: cutting the opening into units

The opening is everything before the closing formula. Cut it into consecutive units, each either a single sign or a unit of the inventory of at most six signs, using as few units as possible. When two or more cuts use the same, smallest number of units, compare them from the end of the opening backwards: take the cut whose last unit is longer; if the last units are equally long, the one whose second-to-last unit is longer; and so on.

The legend's segmentation is the cuts of the opening followed by one cut between the opening and the closing formula. A legend with no stock closing is cut by Rule 2 alone, with no further cut.

## What to report

For each legend, report the positions of the cuts, counting a cut between the i-th and (i+1)-th sign as position i, and the closing formula (or "none"). A legend of three signs that closes with a two-sign formula from the stock, for instance, has one cut at position 1.
