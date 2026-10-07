# Current Proposed test designs, 7 October 2026

The complete definitions, data availability, nulls and support/rejection rules are in [the seven current designs](amendment-2026-10-07-review-corrections/TEST-DESIGNS.md). Numerical planning assumptions are Synthetic in [power-targets.json](amendment-2026-10-07-review-corrections/power-targets.json), rerunnable with `power_targets.py`. No archaeological test was run.

| Design | Required effective sample | Detectable effect / evaluation requirement |
|---|---|---|
| 1. Rare compounds | 300 route objects over three deposits/two sites; 1,000 controls | 1% to 5%; fixed-rate power 0.9350, joint route simulation at least 80% |
| 2. Matched shape features | 600 per group over independent inventories | 20% to 30%; approximate power 0.8887 |
| 3. Seriation | 12 assemblages × 30 objects, three sites | 0.10 bits/object; 1,000 simulations per model, at least 80% power; power not yet estimated |
| 4. Positional rules | 400 multi-mark objects per group/time slice, three intermediate slices | 10% to 20%; approximate power 0.8836, joint slice simulation required |
| 5. Kiln frequency | Batch-aware target to be simulated from reconstructed denominators | Ten-percentage-point decline; at least 80% power |
| 6. Hearth date | Registered sealing/feature/sample/calibration join | At least 95% calendar probability before or after 2800 BCE |
| 7. Contact conventions / paired blocks | 250 graphic objects per group / 60 held-out independent pairs | 10% to 25%, approximate power 0.9550 / 20% to 50%, exact power 0.9863 |

Design 3 compares contextual independence (`q_context = softmax(beta × covariates)`, hierarchical site effects, Dirichlet-multinomial sampling) with copying/mutation (`q_t = (1−rho) q_context,t + rho M_mu q_previous`) on a declared dated route. Both share complexity, medium, ware, production covariates and dispersion. The planning alternative uses rho 0.70, mutation 0.10 and concentration 50; hold out sites and temporal blocks. Its 360-object target must be power-checked before evaluation. [Full design 3](amendment-2026-10-07-review-corrections/TEST-DESIGNS.md), section 3.

Fixed-rate binomial and approximate two-group powers assume independent effective units and one-sided alpha 0.0025, allowing twenty Bonferroni-controlled tests per design. Clustering, estimated control rates, missingness and joint route constraints require simulation before interpreting a negative result. Only Kot Diji (95), Rangpur (222) and Rehman Dheri (190) are additive exact-count rows with at least thirty objects; the required normalized, dated deposit matrices and paired contact objects are missing. [Current evidence](amendment-2026-10-07-review-corrections/inputs-05/evidence-table.json); [targets](amendment-2026-10-07-review-corrections/power-targets.json).
