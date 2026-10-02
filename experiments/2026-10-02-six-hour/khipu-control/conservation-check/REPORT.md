# A complete pooled inventory helps resolve uncertain local membership

In this simulation, an independently observed complete inventory improved recovery when some objects had been assigned to the wrong local accounts. At the 50% support threshold, four swapped assignments gave 133 correct decoders, 9 wrong decoders and 58 ambiguous cases in 200 worlds. Enforcing the complete collection's conservation equation gave 190 correct, 1 wrong and 9 ambiguous cases on the same worlds. The remaining wrong answer satisfied the aggregate equation exactly. Its three independent count checks rejected it.

The experiment uses generated positional marks and account relations. Its two sources of physical evidence are separate: an inventory links the whole collection to its members, and a counted object fixes numerical scale. All shared premises, source exposure and observation availability are stated in [Methods](METHODS.md). The protocol was [frozen before generation](protocol-freeze.json), with a [pre-generation availability supplement](availability-protocol-freeze.json). The sealed outputs contain 1,400 worlds from 200 fresh base seeds, 11,200 account prefixes and 44,800 policy decisions. Conditions and policies reuse each seed's quantities, so each comparison has 200 independent base seeds.

## Final recovery

Each cell gives **correct / wrong / ambiguous / rejected** out of 200. A correct decoder here means the relative vector `(1,10,100)`. Ambiguity retains every tied point or continuous positive family. Rejection includes an empty positive domain or insufficient local support. The complete-inventory rule receives the aggregate observation as a hard constraint; it earns no extra support vote.

| Observation condition | Local consensus, 75% support | Collective constraint, 75% support |
|---|---:|---:|
| Complete local accounts and pool | 200 / 0 / 0 / 0 | 200 / 0 / 0 / 0 |
| Two swapped assignments | 189 / 2 / 9 / 0 | 197 / 0 / 3 / 0 |
| Four swapped assignments | 1 / 2 / 0 / 197 | 1 / 0 / 0 / 199 |
| Two missing local associations, complete pool | 188 / 0 / 12 / 0 | 198 / 0 / 2 / 0 |
| Two missing pool objects, declared partial | 188 / 0 / 12 / 0 | 189 / 0 / 11 / 0 |
| Two missing pool objects, declared complete | 188 / 0 / 12 / 0 | 0 / 0 / 0 / 200 |
| Independent ownership codes | 0 / 0 / 0 / 200 | 0 / 0 / 0 / 200 |

| Observation condition | Local consensus, 50% support | Collective constraint, 50% support |
|---|---:|---:|
| Complete local accounts and pool | 200 / 0 / 0 / 0 | 200 / 0 / 0 / 0 |
| Two swapped assignments | 189 / 2 / 9 / 0 | 197 / 0 / 3 / 0 |
| Four swapped assignments | 133 / 9 / 58 / 0 | 190 / 1 / 9 / 0 |
| Two missing local associations, complete pool | 188 / 0 / 12 / 0 | 198 / 0 / 2 / 0 |
| Two missing pool objects, declared partial | 188 / 0 / 12 / 0 | 189 / 0 / 11 / 0 |
| Two missing pool objects, declared complete | 188 / 0 / 12 / 0 | 0 / 15 / 1 / 184 |
| Independent ownership codes | 0 / 0 / 0 / 200 | 0 / 0 / 0 / 200 |

These counts come from the eight-account rows in [aggregate.json](main-v1/aggregate.json). The 75% threshold accepts very few four-swap worlds because it requires six supporting accounts. The 50% threshold allows the independently observed collection equation to distinguish more candidates, while preserving one accepted error. Both thresholds were specified before this experiment's worlds were generated.

A complete global pool also helps when two local associations are missing. The global inventory still includes both objects, so its equation supplies information lost from the local groups. Recovery rises from 188 to 198 under either threshold. When both objects are physically absent and this is declared, the supplied constraint becomes `parent total >= visible child total`. That inequality improves recovery by one world and leaves eleven ambiguous cases.

Incorrectly declaring a partial pool complete excludes the true decoder in all 200 worlds. At the 75% threshold, every world is rejected for insufficient local support. At the 50% threshold, fifteen wrong points are accepted. Before either gate, the constrained optimum has 125 unique wrong points and 75 ambiguous sets. The support threshold therefore matters even after an aggregate has been imposed.

The ownership control assigns parent values independently of the child quantities. Collective fitting finds an empty positive domain in 37 worlds and insufficient local support in the other 163, under both thresholds. These outcomes record the failure of the supplied additive function in this control.

## What the pooled observation contributes

For a complete pool, swapping members between parents leaves the collection equation unchanged. At the final prefix its coefficient row equals the sum of the eight local rows, so it adds no row rank to a correctly specified complete system. Its useful contribution is the independently observed validity of the whole-collection relation when particular local assignments are unreliable. Maximum consensus may discard some local rows; the collective constraint remains binding.

The whole inventory is available before the first local prefix. In complete worlds, collective fitting identifies the correct relative vector after one local account in 165 of 200 worlds; local consensus alone identifies none at that prefix. The inventory includes all eight parent marks and the pooled child marks. No acquisition costs were assigned, so these prefix results describe the information supplied by that observation. The experiment does not measure the inspection budget needed to acquire it.

## Exact failures and held-out measurements

The [selected-case arithmetic record](selected-case-arithmetic.json) extracts two post-outcome examples from unchanged sealed outputs. It recomputes their residuals and ranks independently.

In world `20261020097-four_swapped`, the complete aggregate is `-70u -63t +7h = 0`, seven times the recurring relation `-10u -9t +h = 0`. The wrong normalized vector `(1,5/6,35/2)` satisfies five local accounts and this aggregate. The true vector `(1,10,100)` satisfies four local accounts. The 50% collective rule accepts the wrong vector. The complete collection relation has retained the family `h = 10 +9t`, and a corrupted account chooses a wrong point within it. The eight fresh account relations have rank two and reject this point. With the observed unit count of two, the wrong absolute vector is `(2,5/3,35)`; the three count residuals are `-330`, `-660` and `-1540/3`.

In world `20261020124-four_swapped`, local consensus accepts `(1,4/3,22)` with five supporting accounts. All eight fresh account equations are multiples of `-10u -9t +h = 0`, or zero. Their rank is one, and every one accepts the wrong vector. The three held-out count-feature rows have rank three. With the observed unit count of six, the wrong absolute vector `(6,8,132)` gives count residuals `-4056`, `-1716` and `-3484`. Even allowing an unknown positive scale cannot make this ray fit all three counts. The complete aggregate `-80u -92t +10h = 0` has residual `52/3` at the wrong normalized vector. Collective fitting instead recovers `(1,10,100)` with four supporting local accounts.

Every final wrong accepted vector fails at least one of the three count checks. One final wrong baseline vector passes all eight held-out relation checks: the rank-one example above. All saved vectors, early errors and later replacements remain in [evaluated-prefixes.jsonl](main-v1/evaluated-prefixes.jsonl). Fresh objects can repeat the same algebraic pattern; rank and independently counted quantities determine whether they distinguish the remaining hypotheses.

## Scale and verification

Without a counted object, every accepted normalized vector represents all its positive multiples. No unmeasured run identifies an absolute vector. In the counted view, the observation `[1,0,0] -> s` fixes the first positional value. The remaining ratios come from the account and collection equations. Counted recovery totals equal the relative recovery totals in both tables because all worlds receive a correct scale observation.

The [independent verification](verification-v2/verification.json) reconstructs memberships and inventories, checks 716,820 subset-feasibility states, 251,013 subset positivity witnesses, 126,058 candidate witnesses, 238,623 held-out residuals and 43,386 scale-ambiguity witnesses. It also checks every aggregate summary and the frozen consensus baseline's code hash. A first static audit misclassified a locally bound comprehension variable named `key` as hidden answer-key access. The [repair record](verification-v2/AUDIT_REPAIR.json) preserves that audit and the corrected checker; fitting code, inferences and scores retain their original hashes. The [retrospective](RETROSPECTIVE.md) records this repair and the earlier diagnostic correction.
