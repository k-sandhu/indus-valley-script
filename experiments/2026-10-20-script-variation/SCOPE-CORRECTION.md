# Correction to the target-code rationale

The frozen protocol says that the cutoff at Wells code 200 excludes fish targets. That rationale is wrong. The fish study defines its family by graphic base B220 in `sign_components_v1.tsv`; these codes are above 200. The numeric cutoff excludes lower-coded targets but is not a fish exclusion. We preserve the frozen protocol and scoring code unchanged.

The code admitted 49 fish targets in the selected discovery observations and 47 in the selected confirmation observations. All are Wells 240 in Mayig compatibility class P062. That class failed the declared discovery support rule, which requires at least two different fine codes with three observations each. It therefore supplied **zero of the 306 primary scored targets**. None of the three strictly matched full-corpus frame pairs has a fish target either. The primary reported score remains the same; the report now states how its non-fish scope actually arose.

The broad selection and empty exact-frame endpoint did include those fish observations. This overlaps the fish study's objects, though its endpoints test different questions. The spending history already declares full-corpus and site exposure. We make no new freshness claim and do not relabel or recompute the frozen endpoint. The aggregate counts, exact B220 code list and source hashes are in `scope-audit-v1.json`.
