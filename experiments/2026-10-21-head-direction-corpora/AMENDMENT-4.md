# Amendment 4: corpus sizes, exclusions and a second panel

Written 21 October 2026 (UTC) after every corpus was normalised and counted, and before any statistic of section 7 was computed on a comparison corpus. The counts below come from the grouping and eligibility code of `discriminate.py` and contain no statistic.

## What the counts show

After grouping by die, alias and identical sign sequence, and keeping complete or restored legends of at least two sign units with an object and a site, the four primary corpora hold these eligible legends at sign level: Indo-Aryan seals and sealings from Basarh and Bhita 245, Tamil-Brahmi seals, rings and coins 23 (16 seals and rings, so the coin substitute of section 4 applies), Ur III seal legends 3,044, and Old Akkadian legends in Akkadian 11. The Old Akkadian figure is small because of the record, not the selection. The CDLI catalogue lists 62 Akkadian-language seals and 31 Akkadian-language sealings of the period, and it gives a provenience for 210 of its 777 Old Akkadian seal entries of any language. Of the 72 Akkadian records that remain after the exclusions below, 27 lose their first or last signs to damage, 21 have no site, and 16 are complete with a site and at least two signs; grouping by die and identical legend leaves 11. At word level, only 30 Indo-Aryan legends have two or more words, because most Gupta legends are a single compound, and 7 Tamil-Brahmi legends do.

With the entry threshold of section 8 (25 legends), one head-final and one head-initial corpus enter at sign level, and the keep rule of section 9, which needs two of each, cannot be applied to any statistic. The frozen protocol therefore cannot keep or reject a statistic on these corpora. We record that outcome before running the code, and the run reports it.

## Exclusions

Twenty-five cuneiform records are composite editions, legends that CDLI reconstructs from several impressions and catalogues under one number without a physical object, and one is catalogued as a reproduction or cast. They leave before grouping, under section 4's rule that edited texts are not counted as objects. The list is `data/raw/2026-10-21-head-direction-corpora/review/exclusions.json` (local; its hash is in the run summary). The Tamil-Brahmi touchstone from Khuan Luk Pat, which Mahadevan places in his seal table, is excluded by the coordinator corrections of Amendment 3.

## A second panel at an entry threshold of 20

The threshold of 25 was set before the sizes were known. A threshold of 20 admits the Tamil-Brahmi corpus at sign level and changes nothing else, so we also run the full panel with `--minimum-legends 20` and report it beside the frozen run as a declared deviation. At 20 the Old Akkadian corpus still does not enter, so this panel cannot apply the keep rule either.

## What the runs report

Both runs compute every statistic on the corpora that enter, at the matched size of section 8, with the replicate spread, the within-legend shuffle reference for `S1`, the Sumerian legends of the Old Akkadian period where they are large enough, the sub-corpora and the two sensitivity runs. Those values describe the corpora. They are not a discrimination test, and no statistic is kept or rejected on them. Section 11's conditions for placing the Indus legends are unchanged, and the first of them, a kept statistic, is not met.

## Code changes

`discriminate.py` gained two options for these runs: `--exclusions`, which removes the listed records before grouping and reports their counts by corpus and reason, and `--minimum-legends`, the entry threshold, whose default stays 25. The cuneiform records of run B are passed through `adapt_cuneiform.py`, which changes their form and not their content: a record without words keeps one empty line, run B's `site_unknown_reason` is copied to the `site_reason` field the validator reads, and fifteen lacuna words without sign units, all in damaged Akkadian records that are not eligible, are removed.
