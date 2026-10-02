# Shared quality changes the law, with little separation in the nested score

The fixed nested statistic gives similar rejection rates for broad and quality-conditioned vector references in this experiment. At nominal 5%, broad references reject 12 of 300 populations, or 4.0%, and quality-conditioned references reject nine, or 3.0%. Their paired difference is one percentage point, interval −1 to 3 points. The mean p-values are .5123 and .5141. All 29,700 broad references change the quality-specific vector margins; all 29,700 quality references preserve them. [Frozen main endpoint](main/results.json), [full independent audit](verification_main.json).

Twenty objects supply two faces and three slots each. Every site has five low-error and five high-error objects, with supplied replacement rates .025 and .60 shared across each object's slots. Latent slots are independent with the same distribution in both quality classes. The fitting model uses `(site,type)` for both references and ignores the extra quality field. The score's zero extension below five components and observed-abstention rule were fixed before generation. No observed or reference table used that guard in the completed study.

| Nominal threshold | Broad vector rejection | Quality-conditioned rejection | Paired broad-minus-quality interval |
|---|---:|---:|---:|
| 1% | 0/300, 0.000% | 2/300, 0.667% | −1.667 to 0.000 points |
| 5% | 12/300, 4.000% | 9/300, 3.000% | −1.000 to 3.000 points |
| 10% | 28/300, 9.333% | 25/300, 8.333% | −1.667 to 3.667 points |

At 5%, the marginal Wilson intervals are 2.303–6.860% and 1.586–5.602%. Paired intervals use 20,000 population bootstrap draws. The full audit reconstructs every population, all 59,400 reference proposals, metadata/margins, independent components/fold loads and p-values. It replays sixteen fits, including quality relabeling. Observed components range from sixteen to twenty; broad reference components thirteen to twenty and quality reference components fourteen to twenty. The run took 1,599.17 seconds, followed by a 59.28-second audit.

The [exact sampler example](exact/results.json) identifies the difference between the laws. Given broad counts, six columns have unequal rational probabilities under the supplied generator. Adding the quality-specific counts leaves four uniform columns and sixty-four uniform three-slot tables. [Independent verification](verification_exact.json) checks the weights and all 20,000 stored sampler draws.

The supplied channel also makes different information available in one face and in an ordered face pair. Maximum adjacent single-face event covariance is .0006072704; the corresponding ordered-vector maximum is .0057955982. [Exact moments](analytic-moments/results.json), [independent latent-pair sums](analytic-moments/verification.json), [methods](METHODS.md). A separate [post-outcome agreement diagnostic](agreement-diagnostic/README.md) uses 1,000 fresh populations. Its broad and quality references reject 94.2% versus 1.0% at 5%; exact conditional tails give 95.0% versus .8%. Its full independent audit passed. The completed nested endpoint remains the comparison for its stated prediction statistic.

[PROTOCOL.md](PROTOCOL.md) and [MAIN_BUDGET.md](MAIN_BUDGET.md) preserve the prospective main design and its prior-outcome exposure. [RETROSPECTIVE.md](RETROSPECTIVE.md) records source reuse, runtime differences, checks and the planned score-sensitivity follow-up.
