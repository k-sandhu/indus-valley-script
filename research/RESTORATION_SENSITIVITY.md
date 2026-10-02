# Restoration sensitivities

Created at the timestamp preserved in the final manifest, after the original restoration benchmark and before these additional outputs. These are exploratory robustness checks.

1. Give each whole text equal total weight, rather than each masked slot. Preserve all physical aliases and the same outer folds. Report both estimates; longer texts contribute more slots to the original endpoint.
2. Repeat nested restoration after only the three independently specified catalogue-compatible merges:861->817,405->390,706->705. Merge before uniqueness filtering and grouping. These are compatibility sensitivities, not proof that the fine glyphs are allographs.
3. Leave Mohenjo-daro, Harappa, and Lothal out separately. Use unique text representatives for the reported test, but define forbidden training components using ALL raw records from the held-out site. This prevents texts found at multiple sites from leaking through a retained representative with another site's metadata. Fit and select smoothing only within the retained training material. Report this stronger population definition and the size of its exclusions.

No real damaged text will be accepted merely because the model ranks a glyph highly. Candidate restoration requires an independently verified one-sign slot and surviving graphic evidence. An erased span coded000 is insufficient.
