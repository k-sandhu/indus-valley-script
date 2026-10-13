# Finite renewal examples: definitions fixed before calculation

11 October 2026. All quantities and transitions below are invented. This is a transparent application of established viability, scheduling, dependency and conservation ideas. It has no fitted archaeological parameters.

## A service-renewal system

State is `(a,b,k)`, with two remaining service lifetimes `a,b ∈ {0,1,2}` and one remaining skill/instructor lifetime `k ∈ {0,1,2,3}`. There are 36 states. The safe set is `K={a>0,b>0}`; it contains 16 states, including those whose instructor has disappeared but whose material stocks still work. Skill is an enabling capacity, not a third observed service.

An action selects any subset of renewing A, renewing B and training a successor. Each task costs one invented resource unit, with a per-period budget `B ∈ {0,1,2,3}`. Nonempty actions require `k>0` at the start. Training takes one period and succeeds under this declared law; no multi-period learning process is represented.

Both service lifetimes age by one. A chosen renewal then resets that lifetime to two. Skill ages by `δ ∈ {0,1}`; selected training then resets it to three. A declared asset shock follows renewal and subtracts a further unit from the affected lifetime. Values stop at zero. Instructor loss after this interval does not invalidate a task it completed during the interval. There is no recovery after leaving K in this persistence definition.

Four disturbance supports are examined: none `{(0,0)}`; focal `{(0,0),(1,0)}`; common `{(0,0),(1,1)}`; and full `{(0,0),(1,0),(0,1),(1,1)}`. They are sets of possible shocks without probabilities. They do not supply an empirical comparison of correlations at matched marginals. The shock is selected after the action, so a robust policy must withstand it without knowing which shock will occur.

All 32 combinations of budget, skill ageing and disturbance support will be reported. For each, compute both possible survival (`∃action ∃shock`) and robust survival (`∃action ∀shock`). These answer different questions. A controller can select actions jointly; distributed implementability, enforcement and conflict are not established by its existence.

`V0=K`. `Vh` contains safe states with a permitted action leading to `Vh−1` under the appropriate shock quantifier. Horizon h means h transitions plus the initial safe inspection, not h historical years. Report horizons 0 through 12. Compute the infinite greatest fixed point by descending iteration until unchanged; store every step and a policy witness where available. Report the primary starting state `(2,2,3)` in every world, including its exit horizon if finite. No policy is a reconstruction of Harappan behavior.

Compare permanent and ageing skill to show how a stock can operate without successful long-term replacement. Budget constraints can obstruct simultaneous renewal. Average renewal workload bounds are necessary under the declared persistent ageing law, but deadlines and state dependence can make such bounds insufficient. Finite-horizon survival need not require renewal when starting stock suffices.

## Explicit dependency alternatives

Use two services, each with two alternative providers. In one invented graph, every provider additionally requires the same input U. In the other graph, provider inputs U1–U4 are distinct. Enumerate component-failure sets and inclusion-minimal sets that disable at least one service, including the minimum cardinality.

This tests whether apparent provider multiplicity supplies independent operational routes. It is a structural comparison of stipulated dependencies, not a failure probability estimate, a measured Harappan supply network or a novel general theorem.

## Conditional inverse bounds

For consistently defined service units and an interval, additional renewal is bounded below by `max(0, minimum cumulative demand − maximum usable initial stock − maximum imports − maximum nonrenewal exogenous supply)`. Inventory and flow terms must not double-count the same service. If an upper bound on any supply term is unknown, report the uninformative nonnegative bound instead of inventing a local renewal requirement.

Report seven invented controls: short horizon covered by stock; longer demand exceeding known supply; large starting stock; unknown imports; unknown starting stock; known exogenous supply that closes the deficit; and unresolved occupation interval with zero minimum demand. These are ordinary accounting bounds. A positive bound requires some additional supply mechanism; it does not identify repair, construction, agriculture, polity, writing, belief, conscious historical knowledge or local self-sufficiency.

## Integrity and review

Freeze code and results in `run-v1/` using a refusing-overwrite CLI. Record protocol and code hashes. The independent reviewer should derive its own transition/predecessor logic or exhaustive witness check rather than import the coordinator's functions. Reproduce all worlds, finite horizons, fixed points, policy safety, dependency cuts and inverse bounds. Any correction after this run needs a preserved attempt and separately dated endpoint.
