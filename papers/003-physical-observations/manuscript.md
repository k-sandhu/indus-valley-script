# Physical observations in numerical decoding: constraints, acquisition and a khipu control

Private working manuscript, 2 October 2026. Authorship, affiliations and venue are pending. Computational analysis and writing used AI assistance. The linked protocols, outputs and source records form the review package.

## Abstract

A proposed numerical reading must connect marks to independently observed quantities or relations. We study how physical membership, positional addresses and counts constrain unknown positive symbol values. In a six-label simulation, twelve complete whole–part observations identified relative values in all 24 generated collections; one count fixed scale. A subsequent acquisition experiment recovered absolute values in 23 of 24 complete-data worlds using an information/rank policy, compared with 15 under random selection. Inaccurate exact counts could identify a wrong scale that passed every withheld whole–part relation. A known-system control reproduced 16 of 20 columns in the published Puruchuco khipu account alignment. Generated decimal accounts identified the remaining positional values in 299 of 300 complete worlds after a counted unit fixed the first value. With unreliable local membership, a separate complete-inventory constraint increased recovery from 133 to 190 of 200 four-swap worlds and reduced accepted errors from nine to one. Incorrect completeness produced fifteen accepted errors. One wrong decoder passed eight fresh relations of rank one but failed independent counts. We provide exact solution certificates, preserved failures and an observation table for applying these methods to unfamiliar numerical records.

## 1. The observation that makes a reading testable

Suppose an unfamiliar object carries a mark beside three smaller objects. A proposed reading may assign a quantity to the mark. If the smaller objects demonstrably belong to the marked parent, their measured quantities can constrain the proposal. Repeated whole–part relations constrain relative values, while an independent count can establish absolute scale. The task is to identify which observations provide those constraints and which alternatives remain compatible.

This question is relevant to Indus numerical proposals because short stroke groups, vessel marks and multi-face tablets invite arithmetic interpretations. The project's earlier audit of a published two-equation proposal found several positive integer solutions under its unrestricted premises. Additional chosen ranges selected one system. The source review also found that the proposed external bangle count lacked an authenticated inscription-specific join. [Exact audit](../../research/methods/NUMERICAL_CONSTRAINT_AUDIT.md), [source premises](../../research/literature/metrology/numerical_source_premises.json). That result motivates acquiring a relation whose origin and units can be checked separately from the proposed reading.

Known numerical systems provide controls. Urton's study of khipu archives documents duplicate accounts and identity labels. The Khipu Field Guide publishes an explicit Puruchuco account comparison, with its partitions, values and discrepancies. Those records allow us to test how representation affects an already specified relation. [Urton 2005 author manuscript](https://dash.harvard.edu/server/api/core/bitstreams/7312037e-6b09-6bd4-e053-0100007fdf3b/content), [published field-guide calculation](https://khipufieldguide.com/notebook/appendix/notebooks/12%20-%20Replicating%20Purucucho.html).

We supply an additive quantity hypothesis and ask whether the available observations identify its positive values. The study combines generated controls, a published-source replication and a collection design. The generated answer keys establish numerical correctness; primary artifact sources supply acquisition targets.

## 2. Methods

### 2.1 Physical membership and scale

The first simulation generates 24 collections with six concealed positive values. Label frequencies are balanced across the text-only observation pool. A complete assembly contributes an equation: its parent's value equals the sum of the labelled child values. Twelve training assemblies and eight withheld assemblies are generated per collection. One independently counted object supplies an absolute measurement. The solver receives label identities, membership and the count, while the answer key remains in a separate saved input. [PHYS-01 protocol and current endpoint](../../experiments/2026-10-02-six-hour/physical-information/README.md).

Let `v` contain the unknown positive values and let `A` record parent-minus-child coefficients. Complete relations give `A v = 0`. Five independent rows can identify one positive relative ray for six labels. A count intersects that ray at a scale. Incomplete groups contribute inequalities, `parent ≥ visible children`, when the missingness is declared. Exact fractions preserve ranks, solutions and counterexamples.

We distinguish unrestricted positive values from a finite diagnostic that supplies the six-value bag. That diagnostic has a stronger prior and can select a mapping before the unrestricted relations identify it. Controls scramble membership, treat incomplete groups as complete, or give labels an ownership purpose with independently assigned object quantities. A corrected endpoint repairs an ownership-count error found while preparing the separated input interface. The initial output and correction remain available.

### 2.2 Choosing observations

A fresh acquisition experiment gives each policy public action descriptors, costs and a budget of 24 units. The descriptors disclose completeness and a bounded child-count menu. An inspection reveals a whole–part relation; a count measures a named object. Unopened responses and hidden quantities remain outside the selector. The surviving positive set is represented by equalities, inequalities and measured intervals. Exact optimization certificates support classification and planning calculations. [PHYS-02 protocol and methods](../../experiments/2026-10-02-six-hour/physical-acquisition/METHODS.md).

The original policies choose by information/rank, at random or by the cheapest available action. They run on 24 worlds for each of five conditions: complete groups, incomplete groups, valid count intervals, counts with insufficient reported uncertainty, and ownership labels. Success requires the correct absolute vector; relative identification and remaining scale intervals are recorded separately. Policies continue to the budget boundary, so the first identification cost differs from total expenditure.

A post-outcome refinement addresses interval measurements. The first information rule assigned no value to an interval when the existing range was narrower than the interval width. A shifted interval could still trim that range. A separately specified overlap rule uses `w/(w+2r)`, where `w` is current range width and `r` the measurement radius. It was tested on 24 fresh interval worlds with all four policies. Its assumptions and original failed rule remain in separate endpoints.

### 2.3 Puruchuco representation control

The Open Khipu Repository was pinned to commit `4039ca51f4de661d80d0160596309c983a62a9c7`. Six original Puruchuco accounts join to stable database identifiers. CM009 is a field-guide reconstruction from an earlier thesis and remains a separate witness. Every selected pendant attachment-position field and every selected knot-cluster total field is zero. The reference values therefore come from the guide's published calculation, with source coordinates and hashes. [KHI-01 source audit](../../experiments/2026-10-02-six-hour/khipu-control/SOURCE_AUDIT.md).

The fixed predictor adds UR068 pendant ranges 14–33, 34–53 and 54–73 by column, then compares the twenty results with UR067 pendants 13–32. Source review exposed the target values before the protocol was frozen. This part is a reference replication with a programmatically isolated predictor and evaluator. It keeps the published alignment and all four mismatches.

Controls preserve an ordered flat list with known width, reverse selected rows' column order, apply all 400 relative cyclic shifts, perform 10,000 within-row shuffles, or allocate the sixty-value bag into three equal rows 10,000 times. Whole-row permutations are an additive invariance check. Each control preserves the lower total, so column-wise error provides the useful distinction. [KHI-01 methods](../../experiments/2026-10-02-six-hour/khipu-control/METHODS.md).

### 2.4 Hidden positional values

A separate simulation generates 300 worlds for each of three account conditions. Each world has eight accounts with three leaf quantities. Complete-account parents store their sum; ownership parents have independent quantities. Quantities have three digit positions, whose true values are 1, 10 and 100. The solver receives positional digit counts, physical membership and a counted one-unit object. That object's feature vector `(1,0,0)` fixes the first positional value at one. Account relations constrain the two remaining values. The solver receives no known value bag.

For each account, the parent's feature vector minus the summed children's feature vectors supplies a linear equation. Exact row reduction and strict positivity classify each prefix as uniquely positive, ambiguous or infeasible. The evaluator checks unique decoders against all 32 generated quantities. Representations retain membership, reorder siblings, omit membership, collapse positions or scramble children across parents. Incomplete accounts lose one child's membership in four accounts; ownership records assign parent quantities independently. A protocol supplement specified prefix evaluation before execution. [KHI-01 simulation and verification](../../experiments/2026-10-02-six-hour/khipu-control/endpoints/main-v1/aggregate.json).

### 2.5 Uncertain membership and collective inventories

A fresh 300-seed experiment replaces all-equation fitting with maximum consensus among the eight local account relations. With the first positional value fixed, the positive domain has two free values. Exact intersections and line families retain every tied optimum. The primary support gate requires six of eight accounts; a secondary gate requires four. Conditions include two or four swapped assignments, missing associations and independent ownership values. Held-out account relations and independent counts evaluate each accepted decoder. The protocols and all earlier-prefix outcomes are saved. [KHI-03 methods](../../experiments/2026-10-02-six-hour/khipu-control/robust-decoder/METHODS.md).

KHI-04 then generates 200 fresh base seeds under seven observation conditions. All visible local account rows enter the support vote as equalities, including rows with missing associations. An independent inventory associates all eight parents with the pooled child collection. The proposed operation uses the same quantity type, units and event; parent marks describe contents pooled without loss or exchange. For a complete collection it gives a binding equality; a declared partial collection gives an inequality. Swapping local members preserves the complete collective equality. All parent and pooled-child marks are available before the first local prefix, with no assigned inventory-acquisition cost. The collective relation enters as a hard constraint and adds no local support vote. Two scale views are retained: normalized first value one represents a positive ray, while an independent unit-feature count fixes that world's absolute scale. The same 75% and 50% support gates are applied. [Collective protocol and observation availability](../../experiments/2026-10-02-six-hour/khipu-control/conservation-check/METHODS.md).

### 2.6 Select validation rows before opening targets

A post-outcome follow-up reuses KHI-04's sealed worlds and final candidate sets. Each world offers eight held-out account coefficient rows and three count-feature rows. The selector receives those rows, observation types, budget and any available unit-anchor coefficient row. Measured targets, decoder candidates, world condition and true values remain outside selection. Account-first, count-first and greedy coefficient-rank policies use budgets zero through three. Uniform-random subsets are enumerated exactly. Each check costs one abstract unit; acquisition effort and measurement uncertainty are absent. Validation intersects the original optimum points, rays and positive families with selected measured equations and retains the original support gate. [KHI-05 protocol and input separation](../../experiments/2026-10-02-six-hour/khipu-control/validation-design/METHODS.md).

## 3. Results

### 3.1 Relations determine ratios; counts determine scale

Twelve complete assemblies identify the correct positive relative vector in all 24 six-label collections. One count then identifies every absolute vector. At three assemblies, the finite value-bag diagnostic already selects one assignment in 12 collections, while no unrestricted positive relative vector is unique. At eight assemblies, the finite diagnostic is unique in all 24, while the unrestricted model identifies 23. [PHYS-01 corrected results](../../experiments/2026-10-02-six-hour/physical-information/main-corrected-anchor/results.json).

With six incomplete groups entered as inequalities, 17 collections retain a unique relative ray. Seven admit a second positive integer assignment after the count. For collection 20261015, both `(6,8,1,2,4,3)` and `(12,8,2,4,8,2)` satisfy every acquired constraint and the measured value eight on label `g1`. Withheld complete assemblies reject the alternative. [Exact integer witnesses](../../experiments/2026-10-02-six-hour/physical-information/integer-ambiguity-certificates.json).

Five short-prefix controls produce an incorrect positive relative ray: two scrambled collections and three incomplete collections treated as complete. Each fails at least one of the eight withheld relations; their failure counts are six, five, six, six and eight. A unique solution under an acquired subset can therefore be followed into a separate empirical check.

### 3.2 Observation choice changes recovery cost

| Condition | Information/rank: correct absolute vectors | Random | Cheapest |
|---|---:|---:|---:|
| Complete groups and exact counts | 23/24 | 15/24 | 0/24 |
| Incomplete groups and exact counts | 22/24 | 17/24 | 1/24 |
| Valid count intervals | 1/24 | 1/24 | 0/24 |
| Counts with insufficient uncertainty | 0/24 | 0/24 | 0/24 |
| Ownership labels | 0/24 | 0/24 | 0/24 |

Information/rank identifies quantities earlier than random in all 15 common complete-data successes, saving a mean 6.47 cost units. Across 17 common incomplete-data successes, it saves 9.82 units on average; it is faster in 16 and slower in one. One complete world has no available count, so its identified ratios retain unfixed scale. Opening all available evidence after the frozen run distinguishes one irreducibly ambiguous incomplete world from another that needs acquisition beyond the original budget. [Main acquisition analysis](../../experiments/2026-10-02-six-hour/physical-acquisition/main-analysis/analysis.json).

Valid intervals usually leave a scale interval. The refined overlap policy recovers six absolute vectors in 24 fresh worlds, compared with zero for each other policy on those same worlds. It retains correct ratios in all 24. Its final range is narrower in 15 worlds and tied in nine compared with information/rank. On those same fresh worlds, mean width relative to true scale is `47/192` for information/rank and `1765/10368` for overlap; median widths are `1/6` and `1/12`. Eighteen overlap-policy worlds retain intervals. [Fresh refinement analysis](../../experiments/2026-10-02-six-hour/physical-acquisition/precision-analysis/analysis.json).

### 3.3 The check must measure the unresolved quantity

Under insufficient count uncertainty, information/rank produces a wrong unique absolute vector in 21 of 24 worlds. In world 2026103200 it infers `(6,3,8,1,2,4)` while the true values are `(12,6,16,2,4,8)`. All ten withheld whole–part relations have zero residual. Two withheld counts have residuals minus two and minus eight. Conservation checks preserve a common rescaling; independent counts address that remaining degree of freedom. [Saved case](../../experiments/2026-10-02-six-hour/physical-acquisition/main/undercovered_counts-2026103200-information_rank.json).

This result guides verification design. A proposal inferred from ratios needs a scale-sensitive target. A proposal inferred from one measured count needs an independent count whose uncertainty is justified. The observation's mathematical relation to the remaining alternatives determines its ability to reject them.

### 3.4 Coordinate correspondence in a known account relation

The published khipu alignment matches 16 of 20 columns, with total absolute error 16. The lower records sum to 3,498 and the upper row to 3,482. Ordered flattening with known start and width preserves the prediction exactly. The reference alignment is the unique minimum-error result among 400 relative cyclic shifts. The best of 10,000 within-row shuffles has error 738; the best of 10,000 bag allocations has error 828. [Source aggregates](../../experiments/2026-10-02-six-hour/khipu-control/source-aggregate.json).

The scalar total difference remains 16 under every allocation, so it cannot distinguish the controls. The column-wise comparison measures the correspondence that the source's physical/account partition supplies.

### 3.5 Relation diversity in positional values

At eight complete accounts, 299 of 300 worlds identify the correct positional values. The remaining world has seven nonzero equations proportional to `−10u−9t+h=0` and one zero equation. The count fixes `u=1`. Both `(1,2,28)` and `(1,10,100)` satisfy the observed accounts. Repeating that carry relation leaves the free value unresolved.

Sibling permutations preserve every prefix. Removing membership leaves all 300 worlds ambiguous. Collapsing positions or scrambling membership rejects all 300 complete worlds by the eighth relation. Under full assumed membership, 97 incomplete worlds and 47 ownership worlds produce an incorrect unique decoder at some earlier prefix, then fail later. [KHI-01 numerical report](../../experiments/2026-10-02-six-hour/khipu-control/REPORT.md).

### 3.6 Consensus with uncertain associations

With two swapped assignments, the 75% consensus rule gives 281 correct, four wrong and fifteen ambiguous outcomes in 300 worlds; requiring every equation gives one correct outcome and 299 rejections. With four swaps, the 50% gate gives 200 correct, sixteen wrong and 84 ambiguous outcomes. The 75% gate rejects 297 worlds and accepts one correct, one wrong and one ambiguous set. Each final accepted wrong vector fails the independent checks. In one two-swap world, five true accounts repeat `-10u -9t +h = 0`; two corrupted accounts select `(1,11/2,119/2)` with seven votes, while the true vector has six. The saved exact geometry explains how a majority of individually correct relations can still identify a wrong point when their independent rank is low. [Frozen consensus report](../../experiments/2026-10-02-six-hour/khipu-control/robust-decoder/REPORT.md).

### 3.7 An independently recorded complete pool

In the fresh 200-seed collective experiment, two swapped assignments give 189 correct, two wrong and nine ambiguous outcomes under local consensus. Enforcing the complete-pool equality gives 197 correct, zero wrong and three ambiguous outcomes. For four swaps under the 50% gate, the corresponding counts are 133/9/58 and 190/1/9. With two missing local associations but a complete global inventory, correct recovery rises from 188 to 198. A declared partial pool gives 189 correct outcomes; treating that partial pool as complete gives fifteen accepted wrong points under the 50% gate and rejects every world under the 75% gate. [Collective results](../../experiments/2026-10-02-six-hour/khipu-control/conservation-check/REPORT.md).

At the final prefix, the correct complete-pool equation is the sum of the eight local equations. Its value comes from the independently recorded validity of the pooled relation when particular local associations are unreliable. Maximum consensus may discard some local equations while the collective relation remains binding. All comparisons reuse the same seed's quantities and have 200 independent base seeds.

One wrong baseline vector `(1,4/3,22)` passes all eight fresh account relations in world `20261020124-four_swapped`. Those equations have rank one and repeat the same carry relation. Three held-out count-feature rows have rank three and reject the vector, even if its scale is allowed to vary. In the counted view, a unit count of six gives `(6,8,132)` and count residuals `-4056`, `-1716` and `-3484`. The complete collective equation also rejects this point. This example makes the remaining validation requirement explicit: acquire measurements that separate the surviving values and scale. [Exact selected-case arithmetic](../../experiments/2026-10-02-six-hour/khipu-control/conservation-check/selected-case-arithmetic.json).

### 3.8 Validation choice and the remaining scale

The four-swap local-consensus population has nine wrong final rays. Three account-first checks leave one compatible. Greedy rank rejects all nine with two checks when the unit value has already been counted, or three without that anchor. Count-first needs fewer: one anchored count rejects all nine, while two unanchored counts do so. One unanchored count leaves all nine compatible because each wrong ray can adopt a different scale. The exact uniform-random expected counts remaining after three checks are .606 with the anchor and 2.024 without it. [Validation report and exact fractions](../../experiments/2026-10-02-six-hour/khipu-control/validation-design/REPORT.md).

Validation also filters tied optimum sets. Counted-view count-first with one check or greedy rank with two produces 190 correct absolute points and ten rejections from the original local-consensus sets. From the collective sets, either policy produces 199 correct points and rejects one. Unanchored count-first with two checks or greedy rank with three gives the same 199 collective recoveries. These are fixed-population post-outcome comparisons.

In the rank-one example, the first unanchored count selects the wrong absolute vector `(645/23,860/23,14190/23)` on the previously accepted ray. It fits `6v +8w = 5160`, as does the true vector `(6,60,600)`. A second count, `6u +6v +3w = 2196`, gives the wrong vector a residual of `1092/23` and rejects it. The saved intermediate point explains why scale identification alone can leave wrong ratios. Coefficient rank describes the selected rows; the original candidate constraints determine how many further measurements are needed.

## 4. Implications for collecting unfamiliar numerical records

The required observation table follows from these results. Each proposed relation needs a physical parent, its actual associated members, completeness, source coordinates, mark features and the basis for treating the relation as additive. A numerical reading also needs a measurement tied to an identified object and its units. An unresolved positive family shows which additional observation could distinguish the surviving values.

| Field to acquire | Record | Constraint it supplies |
|---|---|---|
| Physical identity | Registration, accession, source edition and exact figure/page | Joins observations to the same object and preserves aliases |
| Grouping and orientation | Parent, associated members, face adjacency, physical end and positional address | Defines which features participate in each relation |
| Completeness | Missing member, damaged area, recovery basis and surviving extent | Determines whether an equality, inequality or censored observation is appropriate |
| Graphic features | Counts, height/tier, form alternatives and image coordinates | Supplies coefficients and retains ambiguous alternatives |
| Quantity relation | Observed operation, its units and source basis | Gives the equation independently of assigned symbol values |
| Independent measurement | Named measured object, method, units and uncertainty | Fixes scale or separates remaining value assignments |
| Provenance | Original witness, copied descriptions and shared reconstruction | Identifies dependent observations and measurement errors |
| Reserved check | A separately acquired relation or scale-sensitive count | Tests the inferred values against information withheld during fitting |

The official Louvre record for Susa envelope SB 1940 describes three round pastilles and three rods inside, and three circular and three elongated exterior marks. That balanced mixture supplies one class-count row. It admits both a direct and a swapped two-class assignment in the project's design calculation. Unequal mixtures or individually associated imprint geometry would add distinguishing information. [Official accession](https://collections.louvre.fr/ark:/53355/cl010175973), [source-linked design calculation](../../experiments/2026-10-02-six-hour/physical-acquisition/susa-design-calculation.json). The accession and its documented contents provide a specific object for collecting those additional measurements.

For Indus objects, the current Harappa frame restores registrations and excavation keys for 22 incised tablets, and the Lothal audit links seal impressions with contact textures and support forms. Those records supply object provenance and operation hypotheses. A next numerical test needs an independently observed whole–part or measured-quantity relation attached to such an identified object. Acquisition should preserve original images and physical orientation before coding its features. [Harappa frame](../../experiments/2026-10-02-six-hour/harappa-object-frame/README.md), [Lothal frame](../../experiments/2026-10-02-six-hour/lothal-physical-use/README.md).

## 5. Verification, scope and availability

The simulations assume positive commensurate values, stable features and additive relations. Missingness is supplied when inequalities are used. The acquisition policy sees public costs and uncertainty descriptors. Base collections or base seeds are the independent units; prefixes, representations, policies and reused condition views share them. Point estimates describe these bounded designs. Mixed commodities, uncertain graphic identity and nonadditive functions require new models and controls.

PHYS-01 was checked by exact enumeration, rank over two prime fields and residual tests across 840 records. PHYS-02 arithmetic review checked 3,801 main states and 35,312 distinct saved certificates; the refinement review checked 993 states and 9,766 certificates. KHI-01 independent scalar sums checked 20,411 source predictions. Exact Gram determinants, row-space and witness checks covered all 36,000 simulation states, with 512 states independently checked by linear programming. The largest uncertainty in application is the observed relation and measurement model, which these arithmetic checks hold fixed.

KHI-03 checks all 12,000 prefixes and 384,768 exact subset states, retaining candidate and positivity witnesses. KHI-04 checks 11,200 prefixes, 716,820 subset states and 238,623 held-out residuals. A repaired static checker preserves its initial false flag beside unchanged fitting and scoring hashes. KHI-05 checks 33,600 deterministic validation records and independently classifies 59,856 random-subset intersections of ambiguous optimum sets. [Consensus verification](../../experiments/2026-10-02-six-hour/khipu-control/robust-decoder/main-v1/verification.json), [collective verification](../../experiments/2026-10-02-six-hour/khipu-control/conservation-check/verification-v2/verification.json), [validation reviews](../../experiments/2026-10-02-six-hour/khipu-control/validation-design/additional-review/verification.json).

Code, protocols, summaries, generated worlds, certificates and retrospectives are in the private project repository. Acquired database, source pages, manuscript and detailed source-derived vectors remain local with acquisition manifests and hashes. Frozen endpoints and post-outcome refinements have separate directories. [Claim-evidence map](claim-evidence-map.md), [reproduction and source package](methods.md).
