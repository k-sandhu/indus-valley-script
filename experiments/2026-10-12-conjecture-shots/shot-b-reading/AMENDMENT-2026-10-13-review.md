# Amendment after the adversarial review: the `class` field and CISI identifiers

Recorded 13 October 2026 by the coordinator from the [adversarial review](../review/REVIEW.md), finding M3. The frozen predictions, map and outcome are unchanged.

EXPLORATION.md, PREDICTIONS.md and RETROSPECTIVE.md describe the metadata field `class` as encoding the field animal. It does not. `class` is a text classification: the code UC occurs on 279 tablets and 145 pots as well as 189 seals, UC seals have a unicorn share of 0.339 against 0.554 for all seals, and the codes 2L and 3L mark two-line and three-line texts. Stripping it during construction was harmless.

The withheld-variable list did not strip `source_cisi` and `metadata.cisi`, whose prefixes name the site. No construction script uses them, and a leak through them could only have helped the map pass, so it did not affect the failure. Later shots that withhold site strip CISI identifiers and any record-order field that tracks site.

The review also found that 114 of 925 sized confirmation seal faces are fragments and 49 partly damaged, and that the size model has no site term. Both weaken P2; a later size test restricts to complete seals and includes site.
