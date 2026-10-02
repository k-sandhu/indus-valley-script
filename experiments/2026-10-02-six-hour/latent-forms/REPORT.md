# Learning a form mixture from reference records

The fitted mixture recovers all 24 large-reference mappings at zero and .35 shared mass, matching the supplied-form diagnostic on those records. The earlier two-model reference selector recovered 22 in each case. The new selector, which also considers mixture prediction on reference folds, chooses the mixture in every large-reference case at these two mass levels and likewise recovers all 24 maps.

These outcomes use the preserved common-length benchmark: twelve twenty-symbol systems, three shared-mass variants, two reference sizes and two form-mixture conditions. Training has 640 encoded records and testing has 400. The model receives a supplied component count of three, six-slot records and the common symbol inventory. It learns component profiles from reference symbols without reading the generated record labels, role pools or mapping answer. The same-record reuse is a post-outcome comparison with the frozen methods. [Protocol](PROTOCOL.md), [benchmark](../overlapping-forms/REPORT.md).

| Reference records | Shared mass | Fixed slot | Fixed graph | Earlier selector | Fixed mixture | New selector | Supplied labels |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 40 | 0 | 9/24 | 13/24 | 8/24 | 12/24 | 12/24 | 14/24 |
| 40 | .35 | 2/24 | 2/24 | 2/24 | 4/24 | 3/24 | 4/24 |
| 40 | .70 | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 |
| 400 | 0 | 21/24 | 22/24 | 22/24 | 24/24 | 24/24 | 24/24 |
| 400 | .35 | 22/24 | 16/24 | 22/24 | 24/24 | 24/24 | 24/24 |
| 400 | .70 | 16/24 | 9/24 | 16/24 | 18/24 | 16/24 | 19/24 |

Each denominator contains twelve systems and their two mixture conditions. The earlier selector chooses between graph and ordinary slot prediction; the new selector adds the fitted mixture. Supplied labels provide an additional observed conditioning field. [Independent aggregates](review-v1/verification.json).

Across both reference sizes and mixture conditions, the new selector improves complete recovery over the earlier selector by 12.50 percentage points at zero shared mass, with a twelve-system 95% percentile interval of 0.00–25.00. At .35 mass the improvement is 6.25 points, interval 0.00–12.50. At .70 mass complete recovery is unchanged. The fixed mixture recovers 82 of all 144 conditions; the new selector recovers 79, the earlier selector 70 and the supplied-label diagnostic 85. [Paired comparisons](review-v1/paired-comparisons.json).

Three coincident mixture components would produce a slot pseudocount of three under this fitting rule. A separate closed-form control tests that smoothing. At 400 reference records it recovers 21, 22 and 17 maps for mass 0, .35 and .70, respectively, while the learned mixture recovers 24, 24 and 18. The mixture's median reference-CV gains over that control are 1,669.37 and 530.80 bits at zero and .35 mass. At .70 the median difference is −36.48 bits. Adding the control to a four-model reference selector preserves all complete-map counts of the three-model selector. [Control protocol](COLLAPSED_PROTOCOL.md), [control results](collapsed-v1/verification.json), [reference scores](collapsed-v1/reference-choices.json).

The fitted profiles remain different from each other in every condition. At high shared mass those differences coexist with poorer reference prediction than the collapsed control, which explains the selector's preference for ordinary slot prediction. Component separation alone supplies no recovery criterion; the saved CV scores decide the operational model choice. [Continuous component distances](review-v1/component-separation.json).

The independent review certifies every one of 4,433 mapping assignment subproblems and verifies actual likelihood ascent and the EM lower bound at every update. Among 62 failed fixed-mixture maps, 56 score above the true map and six score below it. The latter six expose search misses under the current nonlinear objective. There are no distinct retained mapping candidates within 1e-8 of the selected score. The full initial and intermediate candidates remain available in the result package. [Objective diagnostics](review-v1/objective-diagnostics.json), [dual bounds](review-v1/assignment-duals.json).

The result supplies a way to use an unavailable form label through a fitted reference mixture, under a supplied component count. The next independent control can vary that count and estimate encoded-population mixture weights as form frequencies change. Additional starts can target the six observed search misses in a separate optimization experiment. Archaeological use would require an acquired reference and a documented inventory correspondence; the numerical result here concerns the preserved generated records.
