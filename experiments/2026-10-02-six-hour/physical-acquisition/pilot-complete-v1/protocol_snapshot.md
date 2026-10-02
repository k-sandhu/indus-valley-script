# Choosing the next physical observation

Written on 2 October 2026 before execution. This simulation extends [physical-information](../physical-information/README.md) from a fixed collection to a sequence of paid observations. Its question is which accessible inspection or count best reduces the quantity assignments still compatible with the evidence.

## Worlds, observations and costs

Generate new worlds independently of the preceding experiment. Each world has six randomly renamed quantity labels. The concealed values are a common unit, chosen from 1–3, times `{1, a, a+1, 2a, 3a, 4a}`, where `a` is independently 2 or 3. This construction supplies varied values and enough possible two-/three-child conservation relations. The selection algorithms receive neither these values nor this generator family.

Sample two complete assemblies as initial observations, eighteen further assemblies as possible inspections and ten complete assemblies as withheld relations. Draw assemblies without selecting their rank. Every parent and child has its own object identifier. Add unlinked objects until the six label frequencies are balanced. Each count action selects a named object by its observed label, before reading its physical quantity.

Each inspection has a public parent label, any already visible child labels, a complete/fragmentary record indicator, an availability flag and a cost drawn from 1, 2, 3 or 4. Count opportunities have their named object's observed label, availability and a cost drawn from 5, 6 or 8. Availability is drawn independently of quantity. Available inspections have probability 0.75; available count opportunities have probability 0.5. Preserve worlds with no available count. The paid budget is 24 units; the two initial relations and already visible fragment associations are supplied equally to all policies.

Run 24 seeds per condition. The main conditions are complete/exact counts, incomplete membership, noisy counts with valid intervals, undercovered count intervals, and ownership labels. Policies share a condition's world and action responses but use independent selection randomness. Use four separate pilot seeds to check execution; preserve any pilot and all repairs before the main endpoint.

## Hypothesis class and positive ambiguity

Infer six fixed positive commensurate quantities. Complete membership supplies `parent = sum(children)`. A known incomplete group supplies `parent ≥ sum(visible children)`. An independent count supplies either an equality or a closed interval. No value bag or upper bound on quantities is supplied.

Before any absolute count, fix `sum(values) = 1` only to represent relative vectors. Once an absolute count is observed, remove this gauge and use the count's units. Test strict positive feasibility and determine coordinate bounds. Record an empty positive set, a unique relative vector, a unique absolute vector, or surviving positive ambiguity. Exact equality rank alone is insufficient when inequalities and intervals constrain the set.

Linear programming finds candidate extrema and certificates. Convert the returned primal and dual quantities to fractions, then check feasibility, dual signs, stationarity and equality of the primal/dual objectives exactly. An infeasible model needs a certified phase-one relaxation; an unbounded range needs a feasible recession direction. Preserve certificate failures as failed executions. The duality calculation follows the standard linear-programming result in [Boyd and Vandenberghe](https://web.stanford.edu/~boyd/cvxbook/index.html); the numerical interface and marginal conventions are documented by [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html).

## Selection policies

**Information/rank rule.** Score an exact count by the independent equality direction it could add, divided by its cost. Score an interval count by the unresolved range it could restrict; acquiring the first absolute interval also fixes a scale range. When a relative vector is identified, a count's declared absolute precision can be compared in the common scale coordinate.

For an unopened assembly, the child labels are unknown. Enumerate all possible two-/three-child multisets consistent with its public visible fragments, using the six code names. This is a planning distribution over possible observations, not a quantity-value prior. Retain outcomes compatible with the present strict positive set. A complete relation earns one unit for a possible independent equality; an incomplete relation earns one-quarter unit when its inequality cuts the present set. Average over compatible outcomes and divide by cost. Use code/action order for ties. Store the compatible-outcome counts and exact scores. If all scores vanish, use the cost rule and mark the fallback.

**Random rule.** Choose uniformly among unacquired, available actions affordable within the remaining budget.

**Physical cost/availability rule.** Choose the cheapest available, affordable action. Break equal-cost ties by a complete record before a fragmentary one, then by action identifier. It receives the same observed metadata as the other rules.

The planner receives only public action descriptors, acquired observations, current constraints and a policy seed. Oracle responses, concealed values and withheld cases live in separate objects. Query an oracle only after recording the action choice. Instrument this boundary and check that modifying unopened responses while preserving planner inputs leaves the choice unchanged.

## Missingness, noise and controls

In the incomplete condition, mark 40% of candidate inspections fragmentary. Show one child initially; an inspection reveals all surviving children, with one true child still missing. Fit the surviving contents as an inequality. Complete records continue to supply equality.

For valid noisy counts, add an independent error from `{-1, 0, 1}` and report the observed value ±1, truncated below at zero. Every interval contains the actual count. For undercoverage, draw the error from `{-2, -1, 1, 2}` but declare a zero-width interval. Retain false unique answers and contradictions. This condition models a count treated as more exact than its observation warrants.

For ownership controls, shuffle labels globally over all object slots while preserving the balanced pool. Quantities remain properties of the individual physical objects. Every count is taken from the particular object bearing the observed badge. The quantity-vector model may be contradicted or may produce an accidental fit; preserve both outcomes.

## Assessment and records

Assess after every acquired observation. Record spent cost, action, response, equality rank, positive feasibility, coordinate ranges, uniqueness and any contradiction. Record the cost when a correct relative or absolute vector is first identified. Keep false unique results separate from correct ones.

The ten withheld complete relations test structural predictions. Add two independently counted withheld objects to test absolute quantities: homogeneous whole/part relations alone preserve every rescaling. Evaluation reads the answer key only after a planner choice. An ownership assignment passes only if it predicts these object-specific quantities and all withheld relations.

Compare policies by paired worlds, reporting identification counts, cost distributions, retained ambiguity, positive-model rejection, wrong uniqueness and withheld failures. The independent unit is the world. Save generated worlds, public inputs, hidden oracle responses, all policy traces, exact state certificates, code/protocol hashes and execution failures in separate pilot/main directories. Refuse to overwrite a result.

## Archaeological correspondence

The inspected [Susa sources](../physical-information/ARCHAEOLOGICAL_TARGET.md) suggest three distinct acquisition types: retrieve an accession-linked token membership record; document whether that record is complete; and obtain a separate physical count or measured quantity. The simulation's cost and availability values are constructed. A real pilot needs those fields from collection records, alongside the distinction between exterior seal imagery and contents-related marks.
