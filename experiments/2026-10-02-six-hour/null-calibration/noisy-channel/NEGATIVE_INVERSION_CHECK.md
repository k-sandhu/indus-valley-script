# Exact absence probabilities for the known channel

Written before fitting the stored main populations, October 2, 2026. A cell contains ten objects and twenty observed face signs. Its empirical mean marginal has increments of 1/20. At the known ε=.1, direct inversion subtracts `t=1/70` and divides by a positive attenuation. A component is therefore negative exactly when its category is absent from both faces of every object in the cell.

For a subset S of categories, write `s=|S|` and `pS=Σx∈S p(x)`. The probability that neither face falls in S is

`qS = pS[(8−s)t]² + (1−pS)[1−st]²`.

The ten independent objects give absence probability `qS^10`. Summing singleton absence probabilities gives the expected number of negative components. Inclusion/exclusion over all 256 subsets gives the probability that every category appears: `C=ΣS (−1)^s qS^10`. Each of the six cells has a permutation of the same p and follows the generator's independent slot/object law. Thus the expected number of affected cells is `6(1−C)`, and the probability that a population has an affected cell is `1−C^6`. Save these quantities with rational arithmetic. Verify the all-categories coverage probability by a separate ten-step dynamic program on the observed category-set bitmask, using the exact ordered-pair probabilities.

This check isolates the finite-sample inversion failure at a known channel rate. The estimated-rate inversion remains an empirical endpoint because its shared agreement estimate couples the six cells. These calculations add no population, tuning or model selection.
