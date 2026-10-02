# Correlated faces need their joint observation law

At a 5% threshold, scalar record-column shuffling rejected 110 of 1,000 populations from the declared independent-object generator. The ordered face-vector reference rejected 50. Their paired difference is 6.0 percentage points, with a 95% bootstrap interval of 4.3–7.7 points. [Main endpoint](main/results.json), [full independent audit](verification_main.json).

Each synthetic population has twenty latent objects, three independent slots, eight categories and two site strata. Each object supplies two observed faces. A face retains its latent category with probability .9 and otherwise chooses uniformly from the other seven categories. The face errors are independent conditional on the latent category. This creates correlated face records that often differ. The [protocol](PROTOCOL.md) fixes this law before the timing pilot; [MAIN_BUDGET.md](MAIN_BUDGET.md) records the pilot-based budget and the pre-main seed correction.

The matched reference permutes each object's ordered pair of observed signs within its slot and site cell. It preserves both the pair counts and the expanded record margins. The scalar reference fixes record margins alone. Every proposal then rebuilds physical/text components, allocates five outer folds and tunes the original models with three inner folds and grid 5/20/100/500/2000. Both references use 99 draws and the same inclusive plus-one rank calculation.

| Nominal threshold | Record-column rejections | 95% Wilson interval | Face-vector rejections | 95% Wilson interval | Paired record minus vector difference |
|---|---:|---:|---:|---:|---:|
| 1% | 25/1,000, 2.5% | 1.70–3.66% | 5/1,000, 0.5% | 0.21–1.17% | 2.0 points, interval 1.1–2.9 |
| 5% | 110/1,000, 11.0% | 9.21–13.09% | 50/1,000, 5.0% | 3.81–6.53% | 6.0 points, interval 4.3–7.7 |
| 10% | 196/1,000, 19.6% | 17.26–22.17% | 104/1,000, 10.4% | 8.66–12.45% | 9.2 points, interval 7.1–11.3 |

At 5%, 41 populations are rejected by both references, 69 by the record reference alone and nine by the vector reference alone. The paired intervals use 20,000 bootstrap resamples of the 1,000 independent populations, with seed 2,026,100,204. Reference seeds are unique within the main run and use namespaces disjoint from earlier studies. The 198,000 reference fits and 1,000 observed fits completed in 5,577.93 seconds.

The audit regenerated all populations and latent truth, replayed all reference proposals, checked every margin and metadata field, reconstructed groups and fold loads through independent graph traversal, verified all p-values and aggregates, and replayed fifteen complete fits. All 99,000 scalar references changed the ordered pair margins; every vector reference preserved them. Observed component counts ranged from fifteen to twenty; record references ranged from nine to twenty and vector references from thirteen to twenty.

The observed faces agreed at 48,821 of 60,000 slots and at 10,817 of 20,000 complete strings. Their replacement indicators marked 11,868 of 120,000 face signs. The [methods derivation](METHODS.md) gives slot agreement probability 142/175 and whole-string agreement probability `(142/175)^3` under the generator. Latent truth is retained for these source checks and is absent from model fitting.

The finite sampler audit counts all tables in two four-object examples and independently replays 200,000 sampled tables. [Exact sampler output](exact/results.json), [verification](verification_exact.json). The broader [domain-support witness](../domain-support/README.md) shows that the unextended fitting procedure can fail elsewhere in a legal face-vector conditional space. The main rejection counts describe the measured simulation grid; the sampler's conditional law and the statistic's domain are stated together in the methods.

[Related work](../RELATED-WORK.md) connects the reference to established block-permutation and repeated-measurement methods. The next archaeological measurements are the correspondence between faces, the number and source history of records per object, and the metadata profile in which comparable face vectors can be exchanged. A separate [known-channel recovery study](../noisy-channel/PROTOCOL.md) reuses these frozen simulated observations.
