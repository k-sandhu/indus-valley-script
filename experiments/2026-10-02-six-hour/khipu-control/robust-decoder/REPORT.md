# Recovery with incorrect memberships

Exact maximum consensus recovered 281 of 300 simulated decoders after two child swaps, compared with one under the all-relations solver. It also retained fifteen ambiguous answers and accepted four wrong vectors. After two missing memberships, it recovered 285, retained fourteen ambiguities and accepted one wrong vector. Every final wrong accepted answer failed the fresh relation check and the fresh count check. [Aggregate scores](main-v1/aggregate.json), [independent verification](main-v1/verification.json), [protocol](PROTOCOL.md).

## What the fitting rule observes

These are fresh generated decimal accounts, with 300 seeds in each of five conditions. Each world has eight training accounts, eight withheld accounts and three withheld counted objects. Mark features describe units, tens and hundreds positions. A separate counted one-unit object fixes the first value to one. The fitter chooses the other two values from the entire strictly positive domain and receives only the training equations. It receives no value bag, base, integer restriction, condition label or error count. Inputs, evaluator keys, sealed inferences and later scores are saved separately.

Each equation becomes a line in the two remaining values. The rule enumerates positive intersections, feasible line families and the positive plane. It keeps every solution set with the largest number of satisfied accounts. Its primary gate accepts a unique point only when at least three quarters of the observed accounts support it. A second, predeclared gate requires half. An all-relations comparator requires every equation. Prefix evaluation continues after an early answer. The [methods and exact candidate class](METHODS.md) describe the families and thresholds.

## Final outcomes

Each entry below covers 300 worlds. A unique decoder is correct when it equals the generator's values `(1,10,100)`.

| Observation condition | All relations: correct / wrong / ambiguous / rejected | Three-quarter consensus: correct / wrong / ambiguous / rejected | Half consensus: correct / wrong / ambiguous / rejected |
|---|---|---|---|
| Complete | 299 / 0 / 1 / 0 | 299 / 0 / 1 / 0 | 299 / 0 / 1 / 0 |
| Two child swaps | 1 / 0 / 0 / 299 | 281 / 4 / 15 / 0 | 281 / 4 / 15 / 0 |
| Four child swaps | 0 / 0 / 0 / 300 | 1 / 1 / 1 / 297 | 200 / 16 / 84 / 0 |
| Two missing memberships | 0 / 0 / 0 / 300 | 285 / 1 / 14 / 0 | 285 / 1 / 14 / 0 |
| Ownership quantities | 0 / 0 / 0 / 300 | 0 / 0 / 0 / 300 | 0 / 1 / 0 / 299 |

One two-swap world exchanged children with equal quantities and retained all eight true equations. Two four-swap worlds retained six true equations because one exchanged pair had equal quantities. Three incomplete worlds removed a zero-quantity child in one account and therefore had one actual violation. The table keeps these accidental agreements; [violation counts](main-v1/aggregate.json) distinguish intended operations from actual equation errors.

The three-quarter gate rejects most four-swap worlds because four correct relations fall below its six-vote requirement. The half gate accepts 200 correct and sixteen wrong vectors while preserving eighty-four ambiguities. With ownership quantities, the same permissive gate falsely accepts one vector. These are fixed decision rules with observed outcomes, rather than probability statements about a majority of correct archaeological observations.

## A wrong answer with seven votes

World 20261010174 has six correct relations and two corrupted memberships. Five correct accounts repeat `-10u - 9t + h = 0`. The remaining correct account supplies `-10t + h = 0`. Together with the count `u=1`, they identify `(1,10,100)`.

The two corrupted rows are `u - 11t + h = 0` and `-11u + 2t = 0`. They intersect the repeated carry equation at `(1,11/2,119/2)`. This wrong vector satisfies seven accounts: the five repeated carries and both corrupted accounts. The true vector satisfies six. Maximum consensus selects the wrong point and discards the one correct equation that supplied a different ratio. All three values in the wrong vector increase with positional tier.

The fresh relation residuals are `(9,0,0,0,-9/2,9/2,0,0)`. The three independent count residuals are `(-18,-9/2,-162)`. The [compact exact case](maximum-consensus-failure.json) retains the acquired equations, supports and these checks. It shows how repeated constraints and correlated membership errors can give a false answer the larger consensus.

## Ambiguity and early answers

At the final prefix, the best consensus set contains a continuous family in two two-swap worlds, twelve four-swap worlds and eight incomplete worlds. Other ambiguities contain several isolated points. The complete-data ambiguity preserves a line after all eight accounts. All of these sets remain in the output. The true vector belongs to the best set in 295 two-swap worlds, 283 four-swap worlds and 299 incomplete worlds. Some ambiguous sets therefore also exclude the true decoder.

The three-quarter policy accepts a wrong vector at some prefix in 62 two-swap worlds and 52 incomplete worlds. Later observations recover the correct vector in fifty and forty-eight of those worlds, respectively; other histories end in a wrong vector or an ambiguous set. Under ownership quantities, thirty-six worlds have an early wrong unique point and all are rejected by the final gate. [Saved trajectories](main-v1/aggregate.json) preserve those transitions. The final performance table describes the full eight-account endpoint.

## Checks, reuse and next observations

Independent verification enumerated all 256 subsets per world with rational row reduction, covering 384,768 feasibility states including three constructed diagnostics. It checked 162,220 subset witnesses, 28,646 arrangement witnesses, every optimal-set classification and 573,061 withheld residuals. Projection checks reconstructed every corruption operation and every equation from object features. Static checks found no evaluator or file access in the tested fitting functions.

The [aggregate review](main-v1/aggregate-review.json) separately reconstructed all score tables and trajectories, and checked every saved line interval, line witness, pair calculation and point candidate. The [source review](source-review.json) records the primary article's page coordinates and the later preprint's version.

The calculation adapts the established consensus approach of [Fischler and Bolles, 1981, printed pages 383-385](https://www.sri.com/wp-content/uploads/2021/12/ransac-publication.pdf). Exhaustive fitting is practical here because the counted unit leaves only two free values. Our contribution is the saved experiment, its positive-family handling and its verified success and failure cases in this observation design.

A useful follow-up would observe a whole collection whose total survives reassignment among its children, then test that aggregate relation separately from uncertain local memberships. Such a checksum could constrain a decoder that wins local votes by discarding the only independent correct ratio. Its physical completeness and commodity assumptions would need to be supplied as part of that new observation design.
