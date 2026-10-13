# Exact renewal examples

11 October 2026. Invented finite constructions, with no archaeological calibration.

The examples distinguish service that works at present from service that can continue under stated laws. The frozen [protocol](coordinator/MODEL-PROTOCOL.md), [implementation](coordinator/renewal_model.py) and [results](coordinator/run-v1/results.json) contain every state, action, horizon and policy. An independent implementation reproduced them in [5,218 checks](review/model-checks-v1/checks.json).

## States, timing and information

Two essential services, A and B, each have remaining asset life 0, 1 or 2. A third coordinate, `k`, records a skill or instructor resource with remaining life 0 through 3. The state is safe when both assets have positive life; skill can already be exhausted while those assets still operate. There are 36 states and 16 safe states.

At each period, a controller can choose to renew A, renew B and train, each at cost one from a shared period budget. Nonempty actions require `k>0` at the start; taking no action remains allowed. An unrenewed asset loses one life unit; renewal sets it to 2. Skill either remains unchanged or loses one unit, according to the declared world; training sets it to 3. An optional shock then subtracts one further unit from its targeted assets. A teacher present at the start can therefore complete training in that period even if ordinary aging would have removed the last unit.

The controller observes the full state and chooses before observing the current shock. Safety is checked at period boundaries. These laws omit within-period outages, repair lead times, imports, demographic change and distributed decision making. The separate accounting controls include imported delivery. A period has no historical duration.

The four supports are no shock, an optional shock to A, an optional shock jointly to A and B, and all combinations of optional single-unit shocks. They specify possible events without assigning frequencies. The possible calculation asks for an action and some favorable shock at each step. The robust calculation asks for an action that succeeds under every supported shock. Exact backward iteration gives horizons 0–12 and the infinite fixed point for each of 32 combinations of budget, skill aging and shock support.

## Results that distinguish the hypotheses

The primary starting state is `(2,2,3)`. “Indefinite” below refers to its membership in the infinite set under the declared law. Counts are states in that set, not communities or estimated survival rates.

| Period budget | Skill aging | Shock support | Robust infinite-state count | Primary outcome |
|---:|---|---|---:|---|
| 0 | Either | None | 0 | One safe transition, then failure |
| 1 | None | None | 9 | Indefinite |
| 1 | One unit per period | None | 0 | Three safe transitions, then failure |
| 2 | One unit per period | None | 11 | Indefinite |
| 2 | One unit per period | Optional shock to A | 10 | Indefinite |
| 2 | One unit per period | Optional joint shock to A and B | 0 | Three safe transitions under the worst supported sequence |
| 3 | One unit per period | Optional joint shock to A and B | 12 | Indefinite |

At budget 1, alternating repair of A and B can maintain both assets when skill does not age. When skill also ages, the same repair demands leave too little capacity to train before it disappears. One feasible three-transition path is `(2,2,3) → (2,1,2) → (1,2,1) → (2,1,0)`. At the end both assets operate, but no further renewal is available and the next transition fails.

Budget 2 can accommodate training in the no-shock world. The saved policy initially takes `(2,2,3) → (1,1,2) → (2,2,1) → (1,1,3)`. It renews both assets before their deadline, then trains while their remaining service covers that period. The policy later avoids entering `(1,1,1)`, because that state requires both repairs and training together for indefinite persistence. Average renewal work, `1/2 + 1/2 + 1/3 = 4/3` actions per period, therefore does not establish feasibility from every currently safe state at budget 2.

When a joint shock can occur every period, both assets must be renewed every period to remain positive. Budget 2 is exhausted by those repairs, so aging skill eventually expires. Budget 3 can renew both and train together. This proof follows directly from the transition law; it supplies no estimate of ancient work budgets or the frequency of destructive events. In the budget-2, aging-skill worlds with joint shocks, possible indefinite survival still has 11 states because the favorable calculation can repeatedly choose no shock.

## Shared inputs and bounded deliveries

Two further constructions keep separate questions separate. In the dependency example, both services have two apparent providers. When all four providers require the same upstream input, failure of that one input stops both services. When each provider has a different input, the minimum number of component failures causing any service loss is two. The program enumerates all 32 and 256 failure sets respectively. These are structural cut sets under stipulated graphs.

Seven accounting controls use invented, commensurable delivered quantities. With minimum demand 8, initial usable delivery bounded by 2 and imports bounded by 1, at least 5 additional units must come from outside those baseline bounds. Six controls yield an uninformative nonnegative lower bound of zero: shorter demand, larger initial stock, unknown import or initial-output ceilings, sufficient other supply, or unresolved minimum occupation. The result counts additional delivered units rather than repair acts or political institutions. [THEORY.md](THEORY.md) defines the archaeological denominator and the limits of that inference.

## Review sensitivities

The independent reviewer fixed two alternative laws before calculating their results. If a shock removes two asset units, it destroys a newly renewed asset completely. Every robust infinite set becomes empty for supports containing nonzero shocks, even at budget 3. The favorable calculation can retain a no-shock history, so its infinite sets remain unchanged.

If work requires skill surviving ordinary aging, the reviewer finds 56 fewer state memberships across 14 world/mode infinite sets. The budget-1, aging-skill, no-shock primary horizon falls from three to two transitions. The sums count memberships across model worlds. Neither variant changes the frozen baseline.

The [review](review/REVIEW.md) also supplies six exact counterexamples. They show why horizon, joint resource competition, observation timing, voluntary implementation, distribution among residents and external supply belong in the theory. All six declared counterexample assertions passed. Numerical consistency of a construction and historical applicability are separate evidential tasks; the prospective studies below address the latter.

## Repair and learning as one operation

The reviewer identified a resource-accounting issue while reading the manuscript: an apprentice can learn during repair, so the work may produce both renewed service and competence. We requested a separate exploratory law, frozen after baseline outcomes in [CO-PRODUCTION-PROTOCOL.md](review/CO-PRODUCTION-PROTOCOL.md). When training accompanies at least one asset renewal, this law assigns it zero incremental resource cost; training alone still costs one. State transitions, eligibility, information and shock laws otherwise stay as in the aging-skill baseline.

The new [enumeration](review/co-production-v1/results.json) covers 16 worlds. At budget 1 with no shocks, the robust infinite set rises from 0 to 9 states and the primary state becomes indefinitely viable. At budget 2, counts change from 11 to 12 without shocks, 10 to 12 with focal shocks and 0 to 12 with common or full shock support. Its primary state becomes indefinitely viable in all four supports. Budget 3 is unchanged. Every baseline finite and infinite set is contained in the new set; 13 world/mode infinite sets gain 76 memberships and none lose any.

This result sharpens the hypothesis. Replacement knowledge can be reproduced through the operation which also sustains service under the shared-operation law. A historical test must measure whether learning occurs during work, its duration and its incremental resource demands. The calculation does not estimate those costs or establish that learning is instantaneous. The reviewer records 1,133 checks, and a second implementation written by the coordinator after the result reproduces all sets and policy transitions in [1,968 checks](coordinator/co-production-checks-v1/checks.json), without importing reviewer functions.

## Reproduce the constructions

From the repository root, select fresh output directories. Each program refuses an existing endpoint:

```powershell
C:\Python313\python.exe experiments/2026-10-11-societal-persistence/coordinator/renewal_model.py --out experiments/2026-10-11-societal-persistence/coordinator/run-reproduction
```

The [review README](review/README.md) gives commands for the independent checker and counterexample enumerator. Their protocols freeze the laws and scope before calculation. The numerical constructions use the Python standard library and require no downloaded archaeological corpus. Source-reading records separately depend on ignored local witnesses.
