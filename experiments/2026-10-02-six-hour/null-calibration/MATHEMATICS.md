# The conditional laws behind the calibration study

The reference is valid when the observed corpus and its fitted reference corpora have the same conditional distribution. The fitting statistic can include grouping, fold allocation and tuning; the matching distribution is the part that needs justification. This note derives that distribution for the three synthetic laws declared in [the main protocol](MAIN_PROTOCOL.md).

## Ordinary fixed-margin columns

Let a cell c contain one exact length, slot and metadata stratum. Its n labeled rows have code counts `m(c,v)`. Under independent categorical draws with common slot probabilities within that cell, the probability of a particular assignment is

`∏v p(c,v)^m(c,v)`.

That expression is constant over assignments with those counts. Conditioning on every cell's count vector therefore makes each compatible labeled corpus equally likely. Cells combine independently under the specified synthetic law.

A uniform permutation of the n labeled entries produces the same law. A given distinct column assignment has `∏v m(c,v)!` generating permutations out of `n!`; this multiplicity is identical for every assignment. The number of distinct complete tables is

`|Ω| = ∏cells n(c)! / ∏v m(c,v)!`.

The original `shuffle_positions` helper samples labeled entry permutations independently in those cells. Its use of duplicate sign values creates repeated representations of a table, with equal multiplicity. It does not weight one distinct table more heavily because that table has more repeated complete strings.

In the exact binary example, each of three columns contains three zeros and three ones among six labeled rows. Each column has twenty distinct arrangements and each table has `(3! 3!)³ = 46,656` labeled generating permutations. There are 8,000 tables, and `8,000 × 46,656 = (6!)³`. Each table's probability is exactly 1/8,000.

## Conditioning on whole-string uniqueness

Let U denote the subset of Ω in which all complete row strings differ. If the observed synthetic dataset is drawn from the independent-slot law conditional on U, it is uniform on Ω∩U after conditioning on the column margins.

A proposal Y uniform on Ω is accepted exactly when Y∈U. For any accepted table y,

`P(Y=y | Y∈U) = (1/|Ω|) / (|Ω∩U|/|Ω|) = 1/|Ω∩U|`.

The waiting time to acceptance changes computational cost. Its distribution does not favor one accepted table over another. Independent proposal streams produce independent accepted tables from the same conditional space. The code preserves proposal counts and accepted seeds so the implementation can be checked against this argument.

The six-row binary example has eight possible distinct complete strings. Choosing six with balanced columns requires the two omitted strings to be bitwise complements. There are four complementary pairs to omit and 6! arrangements of each remaining set over labeled rows. Thus `|Ω∩U| = 4 × 6! = 2,880`, acceptance probability is 2,880/8,000 = .36, and every accepted table has probability 1/2,880. This subset need not itself be a permutation group; direct conditional sampling supplies its reference law.

The exact computation evaluates an integer adjacency statistic over both spaces and the unchanged nested statistic over the entire unique subset. This checks the sampler and tied-tail counting in a space where their probabilities can be enumerated.

## Physical copies change the supported tables

For the copy process, one latent object's independent-slot string is observed twice on a fixed artifact. Conditional on latent column counts, the object-level tables are uniform. Copying each object expands those tables into a restricted record-level space in which each declared pair remains identical.

Permuting record columns independently preserves record-level sign totals but usually creates unequal signs within a copy pair. Those new tables have positive mass under the record-wise reference and zero mass under the specified copy-generating law. Recomputing physical/text groups makes the statistic appropriate to each proposed table; it does not change which table law generated those proposals.

The matched block reference permutes columns among latent objects within their strata and then copies their changed strings back to both records. It preserves every fixed copy pair and has the same uniform object-level conditional law as the observation.

The exact four-object example has two zeros and two ones in each latent column. Its three-column block space has `choose(4,2)³ = 216` tables. The expanded eight-record column margins contain four zeros and four ones, giving `choose(8,4)³ = 343,000` ordinary record tables. Exactly 216 preserve all specified pairs, so the ordinary reference's probability of staying in the copy-supported space is 216/343,000, about .000630. This space count explains why a separate matched reference is necessary for this process. The main Monte Carlo experiment measures the resulting rejection rates using enough objects to fit the original nested routine.

## Exact and Monte Carlo p-values

For a statistic T on a finite uniform conditional space S, the tied-tail p-value is

`p_exact(x) = #{y∈S: T(y) ≥ T(x)} / |S|`.

Order the distinct statistic values from greatest to least. Every tied group receives the cumulative fraction through the end of that group. The observations with p≤α occupy at most an α fraction of S. Ties can make that fraction smaller. This argument permits an arbitrary fixed fitting algorithm in T, including training-only selection and data-dependent grouping.

With B independent uniform reference tables and an observed table from the same law, their B+1 statistics are exchangeable. Count the observed statistic itself among scores at least as large as it. The result is

`p_MC = (1 + #{reference scores ≥ observed score})/(B+1)`.

Conservative tied ranks give rejection probability at most α under that matching conditional law. The references must follow the same conditional law as the observation; adding one to the count supplies no replacement for that requirement. [Hemerik and Goeman](https://pmc.ncbi.nlm.nih.gov/articles/PMC6405018/) explain the conditional Monte Carlo formulation. [Phipson and Smyth](https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf) discuss finite random-reference p-values and the effect of omitting the observed score.

The main study uses B=99, making its smallest p-value .01. At the .05 threshold, rejection requires at most four reference exceedances. This resolution differs from the original thousand-reference Indus runs; the algorithm, grouping and model-selection rules are retained.

## Fitting domain and measured uncertainty

The original routine needs nonempty outer folds and enough training groups for the three inner folds. Some tables in the tiny ordinary enumeration have too few distinct strings/components for that requirement. Their space probabilities remain counted, and the integer statistic remains defined, but they receive no invented nested score. The tiny unique space has six distinct artifact/text groups throughout and supports the full nested enumeration. Main-run fitting failures halt the process and preserve the failed dataset.

The empirical rejection rate is measured across independently generated datasets from each declared law. Its Wilson interval describes uncertainty in that finite simulation rate. The rank argument requires a matching conditional law and a statistic defined on its reference space. The archaeological observation and selection process supplies its own exchangeability assumptions. Paired copy-reference comparisons use the same observed datasets and retain both reference outcomes.
