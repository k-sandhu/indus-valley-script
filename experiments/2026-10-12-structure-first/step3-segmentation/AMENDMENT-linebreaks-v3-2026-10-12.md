# Amendment after verification and review: line counts, boustrophedon faces and segmenter agreement

Recorded 12 October 2026 after the verifier (`../verification/VERIFICATION.md`) and the adversarial review (`../review/REVIEW.md`, findings 8 and 13). Runs `run-linebreaks-2026-10-12/` and `-v2/` are unchanged.

The earlier runs added line windows inside the loop over adjacent line pairs, so each interior line of the four three-line faces was counted twice. Run `run-linebreaks-2026-10-12-v3/` counts every line once. It also excludes the three faces the catalogue marks as boustrophedon, because their line directions alternate and the catalogue does not say which line runs which way; all three were ties in the earlier runs. Ties are now reported beside the decided faces.

The protocol required each segmenter's agreement with line breaks, and neither step 3 script computed it. The review computed it by running the frozen segmenters on the clean texts plus the joined multi-line faces in each line order (review run `step3-segmenter-breaks`). That result is reported in the step 3 report as a protocol output computed in review.
