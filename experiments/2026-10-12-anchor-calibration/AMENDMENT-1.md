# Amendment 1: corrected R1 bound, per-family resolution and supplementary values

12 October 2026, written after the frozen outputs and an independent read-only review of the package were seen and before the computations below were run. The frozen outputs (`roles/summary.json`, `lexical/summary.json`, `positional/summary.json`, `verification.json` and the first diagnostic) stay unchanged.

## Changes

**R1 bound.** The review found that the version-1 `R1Annealer` never filled its per-family containing-string counts, so its five-string condition counted strings gained since the start rather than strings containing a member. Its best map does have 47 families meeting the rule when evaluated directly, so 47 is an achieved value, but the search followed a wrong objective. `roles.py` now fills the counts at initialization; the run version is kept as `history/roles-v1.py`. Four new restarts of 1,000,000 proposals from rearranged starts (spawn key 4) give the corrected bound in `roles/amendment-r1-bound.json`. The R1 permutation result does not depend on the bound.

**Per-family resolution.** Protocol rules 1 and 3 together require a Benjamini–Hochberg q of at most 0.01 across the 53 constrained families. With 1,000 draws the smallest p is 1/1,001, so q ≤ 0.01 is reachable only if at least six families sit at that floor. Under the frozen design no family meets the rule (smallest q = 0.026). A further 10,000 within-stratum draws (spawn key 5) give per-family p and q at finer resolution in `roles/amendment-resolution.json`. This is a post-outcome resolution extension; the frozen per-family results remain the protocol outcome.

**Supplementary values.** The report cited values that no saved output contained: the final-z rankings that name W520, W407 and W405; the 655 of 891 strings ending in W740; the L2 window counts when the *gaṇa* anchor lands on W002; and the closure component that makes the halves uneven. `diagnostics-supplement.json` records them.

**Verification.** `verify.py` read the first lexical engine check instead of the second. The run version is kept as `history/verify-v1.py` with its output `verification.json`; the corrected script writes `verification-v2.json` and also checks the amendment outputs.

**Wording.** The report states that no family meets the adjusted rule, that 21 families lies 0.4 standard deviations above the rearrangement mean of 19.9, that the half-H1 fit keeps the published roles and member counts, that the role-refit z values use rearrangements of the refitted map, and that the stratum p values are unadjusted.

## Outcomes

The corrected annealer reaches 47 families in all four restarts, the same value as version 1, so the bound and the 4% share of achievable gain stand ([corrected bound](roles/amendment-r1-bound.json)).

Under the frozen 1,000 draws no family meets q ≤ 0.01. In the 10,000-draw extension, bound stalks has no draw at or above its excess (p = 0.0001) and carrier/yoke one (p = 0.0002); both have q = 0.0053. Fish shapes has p = 0.0037 and q = 0.065, flag panel p = 0.0095 and q = 0.126. The headline statistics move little: families meeting the two-split rule p = 0.43, code-level count 0.0041, total excess 0.024 and whole-string compatibility 0.0071, against 0.012 under the frozen draws ([resolution extension](roles/amendment-resolution.json)). The frozen values remain the protocol outcomes.

The supplementary file records that W740 ends 655 of the 891 strings containing it, that one closure component of 237 strings lies in H1 and makes the halves uneven (816 and 728 components), that the 208 L2 draws placing the *gaṇa* value on W002 average 728 new-anchor windows against 308 otherwise, and the final-z rankings by stratum ([supplement](diagnostics-supplement.json)). [`verification-v2.json`](verification-v2.json) passes.
