# Estimating undiscovered sites: what the data would need

Prepared 11 October 2026. These are proposed statistical methods and constructed checks. No Indus total was fitted, no new geographic analysis was performed, and the frozen manuscript and candidate register were not changed. The companion source register records five original or official statistical references and the actual reading depth.

## The two-list estimate is not a guaranteed floor

Suppose two searches cover the same target population. List A contains `nA` valid, distinct sites, list B contains `nB`, and `m` identities are securely matched between them. Under the elementary independence model, the usual two-list estimate is

\[
\widehat N=\frac{n_A n_B}{m},\qquad m>0.
\]

It estimates the unseen cell of a capture-history table. It does not identify that cell from the three observed counts alone. The [U.S. Census Bureau's 2020 PES Estimation Design](https://www2.census.gov/programs-surveys/decennial/coverage-measurement/pes/2020-pes-estimation-design.pdf), published 29 November 2022, §3.1–3.2, separates operational dependence from correlated inclusion probabilities caused by heterogeneity. Its discussion describes the usual downward effect of correlation bias and the role of stratification. Archaeological lists can share both problems: one team may reuse another inventory, and both methods may favor the same prominent mounds. Conversely, methods can favor different classes of sites.

The direction of a large-sample effect can be shown directly. Write `pA` and `pB` for the marginal inclusion probabilities and `pAB` for joint inclusion. In an idealized model with repeated independent site histories,

\[
\frac{\widehat N}{N}\longrightarrow\frac{p_Ap_B}{p_{AB}}.
\]

Positive dependence, `pAB > pA pB`, makes this limit smaller than one. This is an assumption-dependent limiting result, not a guarantee for an observed estimate.

Consider a **constructed population of ten sites**. Each site's probabilities for the four histories `(both, A only, B only, neither)` are `(0.2, 0.2, 0.2, 0.4)`. Thus `pA=pB=0.4` and `pAB=0.2>0.16`: detection is positively dependent. A possible realization is `(1, 3, 3, 3)`. Both lists then contain four sites, with one match. The observed union has seven sites, but the independence estimate is `4×4/1=16`, exceeding the true ten. All four cell probabilities are positive, so this realization has positive multinomial probability; the calculated probability is 0.01376256. A single such possible realization disproves a guaranteed lower bound.

There is a narrower algebraic statement that should not be confused with this result. If one imposes a nonnegative association constraint on the **realized, completed** four-cell table, writing `a` and `b` for its A-only and B-only counts and `u` for its unseen count, then `mu≥ab` implies `u≥ab/m`. That constraint gives a bound conditional on the imposed relationship. It cannot be verified from the observed cells, because `u` is missing, and a positively dependent stochastic detection model need not produce that constraint in every finite realization.

With correct matching and genuinely in-scope records, the observed union `nA+nB−m` is a defensible minimum count. Even that statement depends on resolving false positives, aliases and whether separate components belong to one archaeological site. Replace any characterization of the naive estimate as a “rough floor” with **“an independence-based estimate that can be biased downward when both searches favor the same detectable sites; it is not a guaranteed lower bound.”**

## Why a total is presently unidentified

A usable estimation frame would specify the same geographic footprint, archaeological period, site definition and reference date for every list. The population could be surviving occupations of a defined period in a catchment, or the subset accessible to a specified set of methods. “Every place ever occupied by Indus communities” is a different target: remains destroyed before observation cannot be recovered by statistical duplication of present inventories. The closed-population condition concerns a fixed target across the observation process. Later destruction, new exposure, changed site splitting and revised period assignment need explicit treatment.

The required observations are the joint, matched site histories within that frame, including known searches that did not detect a site. Counts drawn from different regional surveys or period definitions cannot supply these histories. A match error changes the denominator directly: missed matches reduce `m` and raise the naive estimate, while false matches raise `m` and lower it. Detection should therefore be modeled after identity and cultural attribution have been reconciled, with sensitivity analyses for unresolved records.

[Link 2003](https://doi.org/10.1111/j.0006-341X.2003.00129.x) demonstrates the deeper problem with unrestricted heterogeneous detection: substantially different population sizes can produce essentially indistinguishable observations under plausible alternative detection models. Its primary abstract was inspected, not its full derivation. In this application, allowing an arbitrary number of sites with zero probability of detection provides a direct exact example. Adding those sites changes the total without changing any observed history. Neither a second list nor an arbitrarily precise fit to visible sites identifies that number. Restricting analysis to sites detectable by the chosen methods defines a narrower estimand; it does not count deeply buried, destroyed or otherwise unreachable occupations.

## Multiple lists and discovery curves are possible next methods

[Fienberg 1972](https://doi.org/10.1093/biomet/59.3.591) develops multiple-recapture estimation by fitting log-linear models to the observed capture-history cells and projecting to the missing all-zero cell. With three or more genuinely distinct searches, this framework can represent some list relationships and permit model comparisons. Dependence structure, heterogeneity and exclusions still need substantive constraints. A fully unrestricted model leaves the missing cell unidentified. An archaeological implementation should report sensitivity to plausible list interactions and detection strata, alongside uncertainty in matching and period assignment. This is a proposed application of the method; the original publisher abstract and metadata were read.

A discovery curve needs a measure of search effort and a stable observation process. Record searched area, transect or person-hours, sensor and resolution, sediment-depth access, season and surface cover, together with verified new discoveries, repeated detections and negative searches. Calendar year alone combines effort changes, methods and shifting geography. An observed plateau can result from searching the same accessible surfaces repeatedly while other settings remain outside the observation process.

[Colwell, Mao and Chang 2004](https://doi.org/10.1890/03-0557), pp.2717–2719 and 2726, provides incidence-based rarefaction and extrapolation for comparable samples from one assemblage. Its model uses occurrence frequencies across repeated sampling units. The authors distinguish interpolation from predicting an ultimate asymptote and find their extrapolation substantially more useful over a limited extension of sampling. For an archaeological adaptation, a site must be capable of reappearing across comparable detection occasions. An inventory of unique sites from disjoint tiles does not, by itself, supply those repeated-detection frequencies. Different effort levels and spatial dependence require suitable strata or an explicit observation model before extrapolation.

[Chao and Jost 2012](https://doi.org/10.1890/11-1952.1), “Sample Coverage and the Species Accumulation Curve” and Discussion, provides a complementary way to compare sampling completeness. Coverage concerns the probability mass represented by already detected identities. It is not the fraction of all possible identities discovered: very rare or inaccessible classes can contribute little detectable mass while containing many sites. Their paper develops individual-based formulas; applying the concept to archaeological incidence requires an appropriate sampling model and units. A defensible initial aim is comparison of yield and completeness at equal effort or coverage within defined strata, followed by validation of modest predictions on a held-out survey effort. None of these methods licenses a civilization-wide total from the current aggregate counts.

## Suggested manuscript insertion

> Future estimation of undiscovered sites would require matched inventories within a common geographic and chronological frame, a consistent site definition and a fixed target population. Two-list capture–recapture estimates use the overlap between independently generated records; both shared research history and uneven visibility can violate independence. Positive dependence can make the independence estimate too low, but does not guarantee that a finite-sample estimate is a lower bound. The valid, deduplicated union supplies a minimum observed count. Multiple-list models can represent some detection relationships, while their estimates remain sensitive to the assumed dependence structure and to sites with negligible or zero detection probability. Effort-based discovery curves offer another proposed approach, using comparable searches and repeated detection histories to compare yield or completeness. Their immediate purpose would be to test predictions for additional survey effort in defined catchments. The present aggregate evidence supplies neither the matched histories nor the observation frame needed to fit a total. [Estimation sources E01–E05]

