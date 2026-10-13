# Repair and training as a shared operation

This variant was requested after the baseline and its review were available. The [amendment protocol](CO-PRODUCTION-PROTOCOL.md) was fixed before the new calculation; the [new implementation](co_production.py) and [complete results](co-production-v1/results.json) leave all prior endpoints unchanged. Every quantity and operation remains invented.

The law now charges for selected asset renewals and charges one for training selected alone. When training accompanies repair, its incremental cost is zero. Training still resets skill within one period, as stipulated in the original model, and requires a teacher present at the start. The declared shared operation can therefore produce both a repaired asset and a successor skill resource. This tests an alternative task definition; it supplies no historical evidence for free or instantaneous learning.

The calculation covers all 16 combinations of budget and shock support with aging skill, both survival quantifiers, horizons 0–12 and infinite sets. Its 1,133 checks confirm that all original action choices remain available, all baseline finite and infinite state sets are contained in the new sets, and saved policy actions satisfy the new budget and quantifier. Thirteen world/mode infinite sets gain a total of 76 state memberships; none lose memberships.

| Budget | Shock support | Baseline robust infinite count | Shared-operation robust infinite count | Shared-operation primary outcome |
|---:|---|---:|---:|---|
| 0 | None | 0 | 0 | One safe transition |
| 0 | Focal, common or full | 0 | 0 | No safe transition |
| 1 | None | 0 | 9 | Indefinite |
| 1 | Focal | 0 | 0 | One safe transition |
| 1 | Common or full | 0 | 0 | No safe transition |
| 2 | None | 11 | 12 | Indefinite |
| 2 | Focal | 10 | 12 | Indefinite |
| 2 | Common | 0 | 12 | Indefinite |
| 2 | Full | 0 | 12 | Indefinite |
| 3 | Any of the four supports | 12 | 12 | Indefinite |

The primary state is `(2,2,3)`. Counts refer to invented state memberships. At budget 1 without shocks, a saved policy alternates asset repairs and trains every third transition during the repair: `(2,2,3) → (2,1,2) → (1,2,1) → (2,1,3)`. The third action renews A and trains at total cost 1. Unlike the separate-cost baseline, the repeated operation can retain both service and skill indefinitely.

At budget 2 under common or full shock support, both assets can be renewed and a successor trained together for cost 2. The original three-transition limit disappears. Budget 3 supplies no additional action under the changed cost law: a shared repair-and-training operation costs at most 2. The program checks that budgets 2 and 3 have identical action choices and finite/infinite sets.

Possible infinite counts are 0 at budget 0, 9 at budget 1 and 12 at budgets 2–3 for every support, because the no-shock sequence remains available. Robust counts still vanish at budget 1 under nonzero shocks: one shared repair operation cannot restore both assets when both must be renewed before the relevant shock. The shared-operation law also retains the original unit-shock survival margin. It has not been combined with the stronger-shock or post-aging-eligibility alternatives.

The variant removes part of the baseline's artificial deficit and sharpens the empirical question. Work requirements should be measured for actual operations and their multiple outputs. Repair, production and learning may share work, while teaching may also slow production or require another participant. A historical schedule must represent those effects before adding independent task minima. [The supplemental claim ledger](claims-co-production.json) links these results and their limits without changing the earlier source/claim pins.
