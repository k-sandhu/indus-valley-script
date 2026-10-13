# Meaning-map calibration

This task asks whether a sign-to-label map predicts declared object variables better than rearrangements of its label records within frequency and position bands. Objects in one closure component share their measurement. Predictions contrast per-sign effect sizes, so a high-frequency sign does not win merely by having more observations. The joint score sums standardized directional contrasts and calibrates that sum on the same rearrangements, preserving correlations between predictions.

```text
python -m bench meaning-map --synthetic --power-trials 100 --out experiments/NEW-DATE-my-study/meaning-synthetic.json
python -m bench meaning-map --objects data/raw/my-study/confirmation.jsonl --map data/raw/my-study/map.json --predictions data/raw/my-study/predictions.json --discovery data/raw/my-study/discovery.jsonl --permutations 9999 --power-trials 100 --power-effects 0,.25,.5,1 --out experiments/NEW-DATE-my-study/meaning.json
```

Object rows carry `id` or `component`, `signs`, and `properties`. The component comes from the shots loader or a documented closure over physical aliases and complete texts. A map is `{"S1": "official", "S2": "name"}` or an object whose sign records carry fields such as `label`, `official`, `band` and `position_band`. A declared `band` moves all label fields together among signs in that band; otherwise the harness uses a log2 frequency band and the supplied position band. Freeze construction bands on discovery before evaluating confirmation.

A predictions file is a list or `{"predictions": [...]}`. Each item has `id`, `variable`, `positive`, `negative`, `direction` (1 or −1), `measure`, `criterion` and `min_units`. For example:

```json
{"predictions": [{"id": "larger_official", "variable": "size", "positive": "official", "negative": "name", "direction": 1, "measure": "mean", "criterion": "rank", "min_units": 8}]}
```

Selectors may be label values or field tests such as `{"official": true}`. Measures are numeric `mean`, categorical `share` with a declared `value`, or bias-corrected categorical `concentration`. Optional `controls` residualize numeric means within declared object strata. Concentration uses the first-order multinomial KL bias correction; historical Shot B reproduction separately imports its original simulation-based correction. Site tests require `site_policy: "exclude_mohenjo"`. Predictions sharing objects use one joint credence rule in the shot freeze.

The default pass requires every declared measure to be computable, joint within-band p ≤ 0.05, and an influence rule for every prediction. `criterion: "rank"` ranks eligible per-sign effects before the contrast; `"loo"` requires the directional contrast to remain positive after every component deletion. `"none"` supplies a descriptive historical mean comparison and cannot grant a new claim pass. Individual p-values use a Bonferroni threshold for the declared set; the joint score has its own rearrangement distribution. An undefined rearrangement makes the test uncomputable, which prevents selecting only convenient null draws.

Output gives eligibility, component and joint scores, distances, p-values, influence results, split-half Pearson/Spearman reliability and variance across five re-splits. `--discovery` identifies the population used for these pre-freeze diagnostics. If omitted, reliability is explicitly measured on the evaluated population. Power mode plants outcomes on the supplied discovery incidence matrix: every sign sharing an object shares its response. Numeric effects are in response-noise SD; share effects are log odds. Concentration mixes a sign-specific category with the original background, at probability `1-exp(-effect*label_share)`. This exposes dilution by shared signs. Predictions sharing one variable need a separately specified joint generative law; the generic planting command requires one planting per variable. Selftest also records nominal-rate and large-effect results under its stated independent normal law.

Real runs need object variables joined to local sign observations. [DATA.md](../../knowledge/DATA.md) records the dimension, motif and context gaps. Use `python tools/fetch_data.py --show lipi` for source pins and [REPRODUCING.md](../../REPRODUCING.md) for normalized local inputs. The [Shot B scorer](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/confirm.py), [frozen result](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json) and [review rules](../../experiments/2026-10-12-conjecture-shots/REVIEW-RESPONSE.md) are the source methods. The October 13 reproduction recovers S = −0.5666586683810659, distance −0.4355708637004734 SD and p = 0.6701329867013298 using the frozen historical mean criterion.
