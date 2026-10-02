# Adjacent agreement reveals the shared-quality mechanism

On 1,000 fresh populations, the integer agreement statistic rejects 94.2% at nominal 5% with broad vector references and 1.0% with quality-conditioned references. Exact conditional tails give 95.0% and .8%. The Monte Carlo paired difference is 93.2 percentage points, interval 91.6–94.7. [Frozen endpoint](main/results.json), [full independent audit](verification.json).

For each object, count one when its two faces agree at both slots zero and one, and another when they agree at both slots one and two. Sum over twenty objects. The score ranges from zero to forty and reads observed signs and fixed object pairs. Quality enters the reference grouping; latent signs and quality labels supply no score value. The [protocol](PROTOCOL.md) was written after the nested comparison's small result and before these fresh populations. It is a post-outcome score-sensitivity experiment.

| Nominal threshold | Broad, 99-draw tail | Quality, 99-draw tail | Broad, exact tail | Quality, exact tail |
|---|---:|---:|---:|---:|
| 1% | 79.0% | 0.0% | 84.8% | 0.0% |
| 5% | 94.2% | 1.0% | 95.0% | 0.8% |
| 10% | 97.2% | 2.2% | 97.6% | 2.1% |

The supplied generator's expected score is 18.9712. Its average broad-reference conditional mean is expected to be 13.5058, a difference of 5.4654. In the fresh run, observed score mean is 18.855, broad conditional mean 13.4469 and quality conditional mean 18.8614. Broad shuffling distributes high- and low-agreement vectors across the fixed quality classes separately at each slot. Quality shuffling retains those class-specific counts and the agreement concentration within each object's class.

With n objects in a reference cell and agreement counts a0,a1,a2, the conditional score mean is `(a0*a1+a1*a2)/n`. The row-state dynamic program stores exact score multiplicities for every column-count triple at n=5 and n=10. A separate hypergeometric-intersection calculation verifies all 1,547 distributions: condition on the middle column, count its overlaps with the independently arranged outer columns, then convolve those two overlap counts. The complete object's-cell distributions are convolved for each of the 2,000 exact population tails. [Integer tables](main/binary_dp.json).

The matched integer tails are conservative because many column-count configurations make the score constant or leave a few tied values. Inclusive ties remain counted. The earlier [nested score study](../README.md) continues to show 4% versus 3% at 5%, interval −1 to 3 points. Together these results distinguish the observed sensitivity of two declared statistics to the same known sampler-law difference.

The audit independently generated all 1,000 populations, replayed every one of 198,000 reference tables, checked 199,000 integer scores, all margins/metadata, every exact and Monte Carlo tail, all cell distributions and paired intervals. All reference streams are distinct. Main runtime was 71.42 seconds; the independent audit took 96.27 seconds. [Work record](RETROSPECTIVE.md).
