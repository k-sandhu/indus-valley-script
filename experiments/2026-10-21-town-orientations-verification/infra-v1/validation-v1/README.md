# Modern runway validation

We measured two long edges on each of 7 paved runways, using the held Sentinel-2 composites and automatic picks seeded from published thresholds. All 14 full edges and all 662 segments returned fits. The execution and coverage checks passed. The selftest in `../selftest-v1.json` separately passed 28 checks across 1,620 synthetic cases.

A runway residual is the mean signed residual of its two full edges against the reference true bearing. Positive values are clockwise. Ahmedabad and Kandla use the AAI eAIP true bearings and thresholds checked in the held AD 2.12 tables. Faisalabad uses OurAirports thresholds. Moenjodaro, Sukkur, Bhuj and Bathinda have float32-style coordinate tails and doubtful source precision; their residuals remain in the full aggregate and carry those flags. The separate precise-reference aggregate contains OPFA, VAAH and VAKE. Hisar's official 3,000 m record resolves the obsolete threshold discrepancy, but no held imagery was available, so it contributes no measurements.

| Runway | Residual (degrees) | Reference |
|---|---:|---|
| OPFA 03R/21L | -0.029683 | OurAirports |
| OPMJ 08/26 | -0.056447 | OurAirports; precision flagged |
| OPSK 14/32 | -0.343383 | OurAirports; precision flagged |
| VAAH 05/23 | 0.019082 | AAI eAIP |
| VABJ 05/23 | 0.089365 | OurAirports; precision flagged |
| VAKE 05/23 | -0.002429 | AAI eAIP |
| VIBT 13/31 | 0.036390 | OurAirports; precision flagged |
| VIHR 12/30 | Unmeasured | No held imagery |

Across seven runways the mean residual is -0.041015 degrees and RMS is 0.137144 degrees. For the three precise-reference runways the mean is -0.004343 degrees and RMS is 0.020421 degrees.

| Segment length (m) | Fits | RMS (degrees) | RMS of residual / stated sigma |
|---:|---:|---:|---:|
| 100 | 326 | 4.272758 | 1.502224 |
| 200 | 158 | 1.764927 | 1.477963 |
| 300 | 102 | 0.988215 | 1.424405 |
| 400 | 76 | 0.746483 | 1.567373 |

Across all segments the RMS of residual divided by stated sigma is 1.492410; the precise-reference subset gives 1.292660. Conditional line-fit errors understate the observed residuals on average. Keep the reported sigma and the empirical calibration as separate fields. Short 100 m segments have substantially larger errors than full runways.

Segments do not overlap within an edge and a length family. Opposite edges share imagery; the four length families overlap. These observations calibrate measurement error and do not form independent archaeological samples. No archaeological feature was measured.


Inputs are in `../imagery-manifest-v1.json` and `../official-runway-references-v2.json`. Automatic picks are local under `data/raw/2026-10-21-town-orientations-verification/infra/validation/runways-final-v1/`. `summary.json` retains every fit, failure count, reference warning and code hash.

The final pass recomputes threshold-derived distances, centres and eligibility after applying official reference overrides. It uses a fresh automatic-pick directory. `summary-first-pass.json` preserves the first pass; every aggregate is identical between passes.

The tools recover modern runway directions with an RMS of 0.137 degrees across these seven runways; 100 m segments have an RMS of 4.273 degrees. A repeat on additional runways with surveyed thresholds would decide how well this calibration transfers to new imagery.
