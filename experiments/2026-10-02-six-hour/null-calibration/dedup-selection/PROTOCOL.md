# Selecting distinct strings from a larger independent population

Written before computing this endpoint, October 2, 2026. The declared unique-record null draws six independent strings conditional on all six being distinct. This experiment examines another observation process: draw seven independent strings, retain each distinct string once, and then condition on having six distinct strings with balanced three-zero/three-one columns. It tests whether that selection process induces the same conditional table law.

Use three independent binary slots with probabilities of one equal to .2, .3 and .4. The six retained strings form one of four balanced sets, each omitting a complementary pair from the eight possible strings. For each set S, enumerate all raw seven-draw occupancy vectors whose support is S. Each vector has one duplicated string. Sum its exact multinomial probability. After selection, randomize the retained strings' labels uniformly over all 6! arrangements, making the induced labeled-table law explicit.

The seven-draw probability of a support S is `(7!/2) × ∏x∈S q(x) × Σx∈S q(x)`. The six-string column margins fix the product term. The support mass therefore depends on the sum of its member-string probabilities. Verify this formula with the complete raw occupancy-vector enumeration and record exact rational masses for every support and labeled table.

Reuse the already frozen 2,880-table nested scores and integer adjacency scores. Verify their hashes and table identities; fit no new models. Evaluate the original uniform-unique tied-tail probabilities under this selected-support law. Report exact rejection probabilities at .01, .05, .10 and the additional coarse threshold .25, plus the largest probability departure over all attainable cutoffs. Also evaluate tails under the matched selected-support law and check their conservative rejection property over every attainable cutoff.

This is a separate synthetic selection experiment. Its known seven-draw process is a testable example of deduplication after sampling. The archaeological unique weighting retains its declared selected-population reference and source assumptions.
