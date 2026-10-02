# What changed during the acquisition experiment

The earlier [physical-information experiment](../physical-information/README.md) showed that physical membership could identify relative quantities and that a separately counted object could set scale. This task asked which observation should be obtained next when access costs and missing evidence matter. The resulting code treats the surviving positive quantity set as the object of acquisition, so an ambiguous case remains a set of possible assignments.

## Design and first execution

The [protocol](PROTOCOL.md) was written before running. New worlds varied both the label quantities and their common unit, with new seeds for pilot and main runs. A concealed generator family supplied valid physical worlds. The planner received public label names, physical group-size bounds, visible fragments, availability and costs. It inferred unrestricted positive rational quantities and received no generator values, family or finite value bag.

The first complete-data pilot, [pilot-complete-v1](pilot-complete-v1/results.json), recovered all four relative vectors under information/rank but acquired no absolute solution. Random acquisition found all four. The count score had included the artificial `sum(values)=1` normalization among observed equalities. After ratios were fixed, that matrix appeared full rank and every scale count received zero score. The [repair](PILOT_REPAIR_01.md) separated acquired equality rows from the gauge before rerunning the same pilot seeds. The repaired pilot identified all four absolute solutions, at mean first cost 9.25, compared with 19.25 for random.

The repair also replaced repeated planning linear programs with exact substitution once a relative vector had been identified. Compatible homogeneous membership relations then have no remaining quantity-identification information. This reduced work per action without supplying unopened children. Original pilot results, source and protocol bytes were preserved.

Five repaired pilots exercised complete groups, incomplete groups, valid measurement intervals, undercovered counts and ownership labels. Each endpoint received exact certificate, action-boundary and object-measurement checks. The ownership implementation counts the actual named object bearing a badge; it avoids the earlier physical-information experiment's repaired mistake of substituting a label's original quantity after badge shuffling.

## Numerical and acquisition checks

SciPy 1.17.1 and NumPy 2.2.6 proposed numerical extrema. Fraction reconstruction and exact primal/dual checks supplied the accepted results. Separate verification rebuilt observation constraints, checked proof objectives, recomputed equality ranks and assessed uniqueness/evaluation flags. Strict positive feasibility and unbounded directions were retained explicitly. The main run completed 285,808 LP calls; the refinement completed 144,177. Their certificate digests and state proofs remain in the endpoints.

Public-input hashes record what was available before each action. Metamorphic tests changed concealed quantities, unopened responses and withheld answers while leaving the acquired observations intact. Choices and score traces stayed identical. The new interval branch additionally passed a width-one/radius-one calculation and tests after an acquired count. Evaluation reads the concealed answer after choices and supplies no value to the selector.

The main results expose two different sources of missing identification. Opening all available evidence after the run, with no cost cap, still leaves one incomplete world ambiguous. Another incomplete information/rank failure becomes identifiable with more acquisition. The complete world with no available count retains an unfixed scale under every amount of membership inspection. Those diagnostic responses were opened after the policy endpoint and never fed back into its choices.

## The interval policy that needed a second experiment

The valid-interval pilot identified an exact scale intersection once under random selection and never under information/rank. The original later-count score, `max(0,1−2r/w)`, treated every current range narrower than a reported interval as having no further acquisition benefit. Another interval's centre can shift its overlap and trim that range.

The [refinement protocol](PRECISION_REFINEMENT_PROTOCOL.md) derived `w/(w+2r)` from the mean overlap of the current range with uniformly located compatible intervals. It specified 24 fresh worlds, all four policies and the unchanged costs, availability and tie rules before execution. The refined policy reached six exact quantity vectors, while each original policy reached none on those worlds. It narrowed the final scale range in fifteen and tied in nine. Eighteen worlds still retained scale intervals. The new planning prior is visible in the protocol and remains a heuristic for coordinates before ratios have been identified.

The refinement only changes scores for nonzero-radius measurements. The main count-error control still documents wrong unique scales when uncertainty is understated. In one saved case, an inferred half-scale vector passed all ten withheld physical relations and failed both independently counted withheld objects. The main endpoint preserves 21 information/rank worlds with a wrong unique answer and fourteen random worlds that encountered one; three random runs later rejected theirs. Ownership controls rejected the quantity model throughout the final main comparison.

## Source collection and rendering

The first source search had located SB 1940 by scholarly figure caption. A second accession query, including the Louvre's English catalogue route, found its official notice and JSON identifier `cl010175973`. The notice supplies an inside/outside count relation and references the six individual catalogue entries Suse 223–225 and 330–332. This is a dated addition to the earlier source search record. Its raw notice and images' rights metadata remain local.

The BnF web reader returned HTTP 403. Direct HTTP retrieval succeeded, and the local HTML confirmed the accession-linked six-token caption. The Louvre and BnF notices use different shape names and give diameters 4.9 cm and 6 cm. The [source note](SOURCE_AND_MEASUREMENTS.md) keeps those fields separate and identifies the catalogue/conservation records needed for the next collection step. The equal class mixture on SB 1940 also produced a concrete design calculation: two positive cross-representation assignments satisfy its aggregate count row, while a hypothetical unequal-mixture row distinguishes them.

The cost figure uses Matplotlib. It was absent from both the ordinary Python and the bundled runtime. Plotting dependencies were installed into a temporary directory outside the project and used only by the rendering process; simulations retained NumPy 2.2.6. Figure manifests record Matplotlib 3.11.2 and rendering NumPy 2.5.3. Visual inspection found the first legend overlapping a curve; a second figure moved it to an empty region. Both figure versions and source snapshots remain available.

## Reuse and the next collection step

Reuse the certificate engine, observation representation and frozen world/action traces to compare another selector. A new selection rule needs its own protocol and seeds. The current score uses a bounded group-size menu and declared access costs; collecting those fields is part of a real archaeological pilot. The immediate Susa work is to retrieve the six token catalogue entries, trace the opening/conservation basis, reconcile the notice measurements and locate an accessioned envelope with unequal class counts. An Indus application begins with a documented physical relation and a quantity observation in a stated unit.

This record covers observable designs, execution problems, fixes and outcomes. The source/selector boundaries, retained positive alternatives and wrong unique answers are available for further inspection in the dated endpoints.
