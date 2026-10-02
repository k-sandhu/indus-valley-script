# Main calibration figure

[calibration.svg](main/calibration.svg) shows the completed independent, unique, copied-object and imperfect-face studies. PNG and PDF copies use the same data and layout. The eighteen plotted values and intervals are in [points.csv](main/points.csv), with exact endpoint/audit/source hashes in [figure.json](main/figure.json). The PNG was visually checked after rendering.

Bars are the original case-specific 95% Wilson intervals across 1,000 populations. Each separately reported reference case has distinct seeds across its populations. In the copied-object comparison, cross-method seed sharing joins 500 pairs of trials. The pre-outcome amendment retains these marginal intervals and uses the linked clusters for uncertainty in the paired difference. At nominal 5%, that difference is 10.5 percentage points, interval 8.5–12.6. [Amendment](../PAIRED_UNCERTAINTY_AMENDMENT.md), [actual overlap and paired calculation](../paired_seed_audit.json).

The renderer requires Matplotlib 3.11.2 and checks the completed full audits before generating a new endpoint. Its local environment is ignored by version control. Preserve this first figure and use a new output directory if any data, layout or interval definition changes.
