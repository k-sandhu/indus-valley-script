# Main calibration study for the declared conditional references

Written after the timing pilot and before the main calibration outcomes, October 2, 2026. The pilot's nine datasets and 108 fitted references completed in 2.90 seconds. That timing supports a main study of **1,000 datasets in each of three synthetic families**, with **99 fitted reference draws per dataset/reference**. The physical-copy family has two paired references, giving 396,000 fitted reference corpora plus 3,000 observed fits. Pilot rejection counts are not used to select the main parameters or infer calibration.

## Known synthetic laws

Each dataset has forty three-sign records and two equally sized `(site,type)` strata. Eight codes have slot probabilities obtained by cyclically rotating [.20,.16,.14,.12,.11,.10,.09,.08] by `stratum + 2*slot`. Positions are independent within a generated latent string. The seed rules, every observed dataset and every reference proposal/accepted seed are saved.

1. **Independent records.** Forty independent strings, each on a distinct artifact. Independently shuffle each exact length/slot/stratum column using the original helper.
2. **Unique records.** Draw the same complete forty-row population until all complete strings are distinct. For its reference, reject original column-shuffle proposals whenever they produce repeated complete strings. This is the known independent-slot law conditional on whole-string uniqueness.
3. **Physical copies.** Draw twenty independent latent strings, ten in each stratum, and create two identical face records on each shared artifact. Test both record-wise column shuffling and a matched reference that shuffles columns among latent objects within their strata, then expands each object back to its two copies. The record-wise reference tests the reach of its exchangeability assumption; the block reference follows this synthetic generating law.

Conditioning an independent-slot law on its column counts makes every compatible labeled table equiprobable: the categorical probability product depends only on those counts. Adding complete-string uniqueness restricts that uniform space. The reference's column permutations are uniform on the ordinary fixed-margin space, and rejection leaves a uniform draw on its unique subset. The physical-copy law instead has support on tables with each specified copy pair identical; its matched reference preserves that support.

## Actual statistic and fitting procedure

Use unchanged snapshots of `conditional_structure.py`, `nested_conditional.py`, `nested_joint_null.py` and `nested_unique_conditioned.py`. Call the original full-procedure `fit` and nested cross-validation. Every observed/reference corpus rebuilds the transitive artifact/identical-string groups, reallocates five outer folds with seed 20261001, selects models in three training-only inner folds and evaluates noninitial held-out log score. The original grid remains 5/20/100/500/2000. Preserve selected baseline/dependent models for all five folds, scores, group counts, largest group and fold loads.

The statistic is the original dependent-minus-selected-independent gain in bits per noninitial sign. Count reference statistics greater than or equal to the observed value. Report `p = (1 + exceedances)/(1 + 99)`. The main p-value grid therefore begins at .01. It checks rejection rates at .01, .05 and .10; it does not reproduce the finer .001 resolution of the original thousand-reference runs. Uniform conditional draws with ties included support the plus-one rank calculation. [Phipson and Smyth](https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf) discuss finite random-reference p-values, and [Hemerik and Goeman](https://pmc.ncbi.nlm.nih.gov/articles/PMC6405018/) provide the conditional Monte Carlo formulation.

## Endpoints and uncertainty

Report every dataset's observed score and p-values, and rejection counts/rates with 95% Wilson intervals across the 1,000 independently generated datasets. At a 5% rate, that sample size gives an approximate interval width of 2.7 percentage points. The record and block references for a copy dataset share its observed score; preserve their paired disagreements as a further diagnostic. Report acceptance rates for uniqueness conditioning and changes in recomputed groups.

Do not select a preferred family, comparator, fitting seed or rejection threshold after outcomes. This reduced population studies the specified sampler/statistic combination; claims about the full archaeological corpus retain their original population and exchangeability assumptions.

## Exact and implementation checks

Alongside the main process, complete the small fixed-margin enumeration and its rejection-uniformity audit. Enumerate all 8,000 balanced six-row binary tables and their 2,880 unique-row subset. The integer adjacency statistic checks exact tied-tail p-values. Also evaluate the unchanged nested statistic across the entire unique subset, which has enough components for five outer folds. Record how many ordinary tiny tables have too few components for that same algorithm instead of assigning them a fabricated fit.

For four binary latent objects copied twice, count the matched block space and the much larger record-wise space, including the latter's probability of preserving all four copy pairs. Check marginal preservation and copy consistency on every main draw. Independently replay selected observed/reference fits and every trial's exceedance count, plus-one p-value and aggregate interval. Verify every source snapshot and completed endpoint. Preserve interrupted/failing trial records; a resumed process must use identical source hashes and parameters.

After the pilot, only output formatting was made compact and the Wilson endpoint for zero/all successes was set to exact 0/1. The pilot code snapshot remains preserved. These changes leave datasets, model selection, scores and rejection rules unchanged.
