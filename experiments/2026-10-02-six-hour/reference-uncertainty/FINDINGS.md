# Finite references and erroneous supplied identities

Integrating uncertainty in a small reference reduced confident wrong mappings in the constructed administrative systems. It changed exact recovery much less. Under a changed record-generating process, wrong mappings could still receive almost all the conditional mapping mass. A supplied wrong identity also produced confident answers because the search was restricted to maps that obeyed it.

The [declared grid](PROTOCOL.md) has 24 new generated systems, with twelve in each family. Each system contributes nested reference populations of 40, 400 and 4,000 records, encoded training populations of 40, 160 and 640 records, two process conditions and three identity conditions. Two likelihoods produce [2,592 saved trials](main/results.json). The [condition table](review/conditions.csv) retains all 216 conditions; every condition has twelve generated systems. Repeated sizes, models and anchor conditions share data within a system.

## Recovery and confidence

The rows below pool nine reference/training-size combinations. Their denominators are 108 condition trials from twelve systems, so they describe this grid's pattern rather than 108 independent replications. A confident wrong trial has an incorrect selected map and conditional mapping mass of at least 0.95.

| Administrative process | Supplied identities | Fixed-reference exact maps | Integrated-reference exact maps | Fixed-reference confident wrong maps | Integrated-reference confident wrong maps |
|---|---|---:|---:|---:|---:|
| Unchanged | None | 72/108 | 74/108 | 10/108 | 0/108 |
| Unchanged | Two correct | 87/108 | 84/108 | 9/108 | 0/108 |
| 35% mixture change | None | 30/108 | 28/108 | 29/108 | 9/108 |
| 35% mixture change | Two correct | 49/108 | 51/108 | 27/108 | 8/108 |

The stationary transition family was easier: both likelihoods recovered all 108 maps in each unchanged-process identity condition that allowed the truth. Both recovered 107/108 under the mixture change. The administrative generator has position-dependent roles, while both solvers use stationary transition statistics. More reference records therefore estimate a constrained approximation more precisely; they do not supply the missing position-dependent model.

The two procedures also predict held-out records differently. The fixed procedure retains its reference parameters. The integrated procedure updates with mapped encoded training counts before predicting the test records. That adaptation is part of the specified method, and helps explain why its held-out anchor penalties can be smaller.

## Testing a bad identity against further records

The erroneous condition asserts one correct identity and one exchanged identity. Its two destination identities remain compatible with a bijection, but the true map is excluded. Every selected map follows both supplied identities. The search contains 720 maps, compared with 40,320 in the unrestricted condition.

An independently sampled held-out population usually penalized the erroneous condition relative to the unrestricted search. [Every paired difference](review/wrong-anchor-heldout.csv) is preserved.

| Generator and process | Likelihood | Wrong-identity trials with worse held-out score | Mean added bits per sign |
|---|---|---:|---:|
| Transition, unchanged | Fixed | 108/108 | 0.8164 |
| Transition, unchanged | Integrated | 107/108 | 0.2643 |
| Transition, changed | Fixed | 108/108 | 0.5389 |
| Transition, changed | Integrated | 107/108 | 0.1747 |
| Administrative, unchanged | Fixed | 102/108 | 0.1597 |
| Administrative, unchanged | Integrated | 97/108 | 0.0581 |
| Administrative, changed | Fixed | 88/108 | 0.0709 |
| Administrative, changed | Integrated | 82/108 | 0.0228 |

Some erroneous identities improve the test score under the fitted approximation. In the changed administrative condition this happens in 20 fixed-reference trials and 26 integrated-reference trials. A predictive penalty is thus a useful diagnostic with a measurable miss rate. A physical identity observation should retain its independent object and measurement record, so that it can be reviewed alongside a statistical disagreement.

## What this adds to the solver design

Retain uncertain reference parameters, alternatives to each external identity and a separately acquired evaluation population. Report mapping mass together with model checks and anchor sensitivity. The present experiment supplies test cases in which these reports disagree in informative ways.

The benchmark supplies eight stable identities and a bijection, along with known generative families. It separates finite-reference uncertainty, process mismatch and an erroneous identity under those assumptions. A broader solver will need variable inventories, uncertain segmentation and independently observed relations between labels and objects.

Posterior concentration under model misspecification is established statistical work. Kleijn and van der Vaart's [2006 paper](https://arxiv.org/abs/math/0607023) studies concentration near models that minimize Kullback–Leibler divergence to the sampling law. The present contribution is the saved mapping benchmark and its diagnostics; that general phenomenon motivates the process checks.

## Verification and reproduction

[Eleven review checks](review/checks.json) pass. The review independently regenerates and scores a selected trial in each of the 216 conditions using sequential prediction or scalar transition sums. The largest held-out score discrepancy is `3.78e-14` bits per sign. Bijections, anchor compliance, recovery flags, trial accounting and the generator, protocol and program hashes also match.

```powershell
python src/six_hour/reference_uncertainty.py --output experiments/2026-10-02-six-hour/reference-uncertainty/repeat
```

Use a fresh output directory. The [pilot](pilot/results.json) remains separate from the main grid. Main generation took 151.8 seconds on the recorded local environment.
