# Proposed changes to knowledge/DATA.md from the Q-0009 pilot

All numbers come from [README.md](README.md) and [results.json](run-2026-10-15/results.json) of this package. No new source, acquisition or rights status is introduced; the change concerns how one existing field is counted. Paths inside the proposed text are written from the repository root in code spans, so that the maintainer can turn them into links relative to `knowledge/DATA.md` without the link check failing on this file.

## Units paragraph (line 7)

Replace "`None` in the motif fields is an asserted absence and counts as usable." with:

> `None` in the motif fields was counted as an asserted absence on 12 October. A photograph check on 15 October confirmed this for rectangular seals and not for square seals, where `None` and `-` also mark faces too broken or worn to show a motif (`experiments/2026-10-15-route-test-metadata/README.md`); seal motif coverage is given under both rules in section 2.

## Section 2, "Fields not in the table" (line 95)

After "motif (`symbol`, including asserted absence) 89.4%", add:

> On seals, counting `None` as an absence only on rectangular seals, as the 15 October photograph check supports, gives 2,013 of 2,239 seal objects (89.9%) a usable motif value instead of 2,110 (94.2%); the other 97 seal objects marked `None` and all 129 with a placeholder are unknown. `None` on tablets, tags, sealings and pottery (2,161 faces) has not been checked against photographs.

## Section 4, `motif` row (target object record table)

Replace the coverage cell "89.4% incl. asserted absence" with:

> 89.4% incl. asserted absence; on seals 89.9% when `None` counts only on rectangular seals (Q-0009 pilot, 15 October)

## Section 5, ranking table

No change in rank. Q-0009 is a general card (section 5's last paragraph); the pilot's next step, a second reading of all square-seal `None` and `-` faces, is a few hours of held-source work and could be listed beside Q-1004 if maintainers want it ranked.

## Manifest

[manifest-additions.json](manifest-additions.json) adds one sentence to the `notes` of the `lipi` entry and the package to its `evidence` and `questions`.
