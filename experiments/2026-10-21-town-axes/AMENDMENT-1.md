# Amendment 1: a secondary analysis on plans whose north is not stated

Written on 21 October 2026 after the four measurers and the dating researcher had finished their files and before the coordinating agent read any bearing, deviation or error value from them. Its SHA-256 is recorded in `AMENDMENT-1.sha256`. [PROTOCOL.md](PROTOCOL.md) is unchanged, and its primary analysis is run and reported exactly as frozen.

## What we knew when writing it

The coordinator had read only two facts from the measurement files: which towns have at least one measured system for each measurer, and how each plan's north arrow is classified. Imagery gave measurable architecture at five towns: Mohenjo-daro, Harappa, Lothal and Dholavira for both imagery measurers, and Sutkagen-dor for img-A only. Kalibangan, Banawali, Rakhigarhi, Chanhu-daro, Kanmer, Shikarpur, Surkotada and the other optional towns are backfilled, overgrown or not found in the imagery. Almost every published plan carries an arrow that does not say whether it points to true or magnetic north; the plans of Chanhu-daro are labelled magnetic, and one Dholavira plan is labelled true.

Under the frozen rules the primary deviation therefore exists for at most six towns, Kalibangan has none, and P0 needs eight. The frozen result will be "undecided", and the claim's credence stays at 0.10. The plans contain much more information than that verdict uses, so we add one secondary analysis, declared here before any value is seen and reported as exploratory.

## The secondary analysis

**Plan-north error.** For every town that has both a primary (imagery) deviation and a plan measurement, we take each plan measurer's declared main system and compute Δ = θplan − θimagery, with the plan value as measured relative to its own arrow (magnetic plans corrected with IGRF where a survey year is known). The plan-north error is summarised by the mean of Δ (bias) and its root mean square, sΔ. If fewer than three towns supply a difference, sΔ is set to 3°.

**Plan-based town deviation.** A town with no primary deviation takes the inverse-variance mean of the plan measurers' declared main systems, whatever their north label, with error σθ² = max(propagated standard error, half the difference between the two plan values, 0.3°)² + sΔ². No bias correction is applied; the bias is reported. Towns with a primary deviation keep it.

**Layout date.** The frozen date rule applies unchanged. For a plan-based town the part is the one named by the plan measurers' declared main systems; where the two name different parts, or the name does not match a part in the dating record, the part is the earliest walled or gridded part that the dating record describes. This choice is made from the part names alone and recorded in `dates-v1/dates.json`.

**Statistics.** Stage 1 and stage 2 run unchanged on this extended table, with outputs in `exploratory-v1/`: the target is chosen on Mohenjo-daro, Harappa and Kalibangan, and P0 to P3, the power simulation and D1 follow the protocol's definitions and pass rules.

**Credence.** The exploratory result cannot make the claim dead or strengthened in the protocol's sense, because its towns depend on plans whose north was not stated. If the exploratory P0 fails with at least eight towns, the credence falls to 0.04 and the status becomes weakened; if it passes, the credence rises to 0.15 and the status stays open, pending true-north measurements of the plan-only towns. P1, P2 and P3 are reported for the record.
