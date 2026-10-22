# Protocol: true-north bearings of Harappan towns from registered plans

Frozen on 21 October 2026, before any control point was chosen and before any rotation was computed. The SHA-256 of this file is recorded in `PROTOCOL.sha256` and, with the hashes of the code, the plan list and the briefs, in `FREEZE.json`. Changes after the freeze go into dated amendments; this file stays as written.

## 1. Purpose

The [town-axes package](../2026-10-21-town-axes/REPORT.md) measured the axes of Harappan towns on satellite imagery, which is referenced to true north, and on excavators' plans, whose north arrows are almost never labelled true or magnetic and disagree with the imagery by several degrees. Only Mohenjo-daro, Harappa, Lothal and Dholavira have dated true-north values, so its frozen kill condition P0, which needs eight dated towns, was undecided. Its planning simulation gives P0 a power of 0.97 if eleven dated towns had true-north values with errors near 1°.

This package measures the true bearing of each plan's north arrow by registering the plan to current imagery. A registrar finds features that appear both on the plan and on Esri World Imagery, such as mound outlines, survey pillars, roads, canals and village edges, and records each feature's pixel position on the plan and on the imagery. We fit a similarity transform (rotation, uniform scale and translation) from plan pixels to Web Mercator. Web Mercator is conformal and its grid north is true north at every point, so the fitted rotation gives the true bearing of the plan's page axes and therefore of its drawn arrow. The plan-B measurements of the town-axes package, which give each wall line relative to its plan's arrow, then convert to true north.

## 2. Plans

The plans are listed in [plans-v1.json](plans-v1.json), written by `code/make_plans.py` from the plan-B town files with only the render file, publication, page, scale bar and published site coordinates of each plan. There are 21 plans of 12 towns.

| Role | Towns and plans (plan-B source ids) |
|---|---|
| Target | Kalibangan (iar1967-68-fig7, iar1968-69-fig), Banawali (iar1987-88-fig1, iar1983-84-fig4), Farmana (shinde2008-fig19), Surkotada (joshi1990-fig8, joshi1990-fig4), Kanmer (kharakwal-fig5), Chanhu-daro (mackay1943-pl4) |
| Validation | Dholavira (asi2020-vol5-drg9, asi2020-fig2.10, bisht2015-fig6.3, asi2020-fig2.11), Lothal (bisht2015-fig10.10a, rao1979-fig17, rao1979-fig18) |
| Optional | Harappa (wheeler1947-pl15), Rangpur (rao1963-fig8, rao1963-fig6), Rojdi (possehl1989-fig23), Gola Dhoro (iar1996-97-fig1) |

Rakhigarhi and Shikarpur have no plan with measured lines in the town-axes package. A search agent (section 3) looks for a published plan of either town that shows Harappan structures, a north arrow and features visible in the imagery; if it finds one, it measures the lines by plan-B's method, declares a main system, and registers the plan under the same rule. Its town files follow the plan-B schema and enter the computation through `register.py --extra-towns`.

## 3. Registrars and what they may see

Two registrars, R1 and R2, register every plan independently. Each registrar's work is split by region among three agents with the same brief: G1 (Kalibangan, Banawali, Farmana, Harappa), G2 (Surkotada, Kanmer, Dholavira) and G3 (Chanhu-daro, Lothal, Rangpur, Rojdi, Gola Dhoro). A seventh agent, S, does the search for Rakhigarhi and Shikarpur. All work under [REGISTRATION-BRIEF.md](REGISTRATION-BRIEF.md) or [SEARCH-BRIEF.md](SEARCH-BRIEF.md), whose hashes are in `FREEZE.json`.

The registrars are given the plan list, the tools in `code/cptools.py` and the brief. They are not given, and are told not to open, the town-axes measurement and result files (the plan-B and plan-A town files, the imagery measurements, the settlement-axis table, the report and its cards), this protocol, each other's output, or any statement of what the measurements are for. Their checking tool fits the frozen model and prints the scale, the residuals and the rotation error, but not the rotation. They may draw the plan's ink over the imagery with the fitted transform to see whether the features match.

The coordinating agent read the town-axes report, which states the plan deviations and the imagery deviations, before writing this protocol. For that reason the coordinator chooses no control points, edits no control file, and computes no rotation until the control files are hashed in `CONTROL-FREEZE.json`.

## 4. Control points

### Eligible features and their errors

A control point is a point that can be identified on the plan and in the imagery and whose position is unlikely to have changed between the survey and the image. Each point is assigned to a class with a one-sigma identification error per coordinate, in ground metres, for the pair of positions together.

| Class | Features | σ (m) |
|---|---|---|
| A | Sharp corners of permanent built features: standing masonry, a building or compound wall corner, a survey pillar or benchmark, a well head, a bridge abutment, the crossing of two metalled roads or of a road and a railway | 3 |
| B | Well-defined points on linear landscape features drawn on the plan: crossings and sharp bends of tracks, canals, drains or field embankments; corners of excavation cuts or spoil heaps that are still visible | 6 |
| C | Points on landforms and soft edges: corners, re-entrants or extremities of a mound outline or contour, breaks of slope, the edge of a village or a tank, a bend in the bank of a dry channel | 12 |
| P | A link between two plans: the same drawn feature (wall corner, trench corner, grid peg) on both | 2 |

Each point's error adds two picking terms of 1.5 pixels, one at the plan's scale-bar resolution and one at the imagery's ground resolution: σi² = σclass² + (1.5 px × plan m/px)² + (1.5 px × imagery m/px)².

A point placed on Harappan masonry that is exposed and visible as masonry in the imagery is flagged `exposed_masonry`. Mound edges formed over buried walls are landforms (class C) and are not flagged.

### Choice rule

1. For each plan the registrar first lists every feature on the plan that might be visible today, then looks for each in the imagery. Every class A or B point that can be identified with confidence is used. Class C points are added until there are at least five points if the plan allows, chosen to spread over the whole extent of the plan rather than to cluster.
2. At least three points are required. Points that all lie near one line do not count as three.
3. A point is chosen from what the plan and the imagery show. No point is chosen, moved or dropped on the basis of an orientation value; the registrars see none.
4. After a check with the tool, a point may be moved or removed only when the registrar can name an identification error (a different feature, a feature rebuilt or moved since the survey, a misread pixel). Every change is written in the control file's log with its reason; removing a point only because its residual is large is not allowed.
5. If the plan itself shows fewer than three features that survive in the imagery, the registrar may chain it through an auxiliary plan of the same site: a second plan (from the same or another publication) that shows both the measured structures and surviving features. The measured plan is linked to the auxiliary plan with class P points, and the auxiliary plan to the imagery as above. The auxiliary plan needs a scale bar, measured by the registrar.
6. Imagery is the current Esri World Imagery at zoom 17 to 19, or an older Esri Wayback release where it shows a feature better; the release is recorded with each mosaic. Sentinel-2, at 10 m, is too coarse for these features and is not used.
7. A plan with no three usable features is recorded as not registrable, with the features looked for and why each failed.

## 5. Fit and error model

The code is `code/regfit.py`, frozen with this protocol.

**Fit.** Plan pixels (x, y) with y downward become right-handed coordinates (x, −y). Imagery pixels become Web Mercator metres, centred on the points' centroid and multiplied by the cosine of its latitude, so that map units are ground metres. A plan-to-plan link uses the target plan's right-handed pixels. The four parameters of q = s R(φ) p + t are fitted by weighted least squares with weights 1/σi² on both coordinates. The rotation φ is counter-clockwise from the plan frame to the map frame, so a direction with page azimuth a (clockwise from page-up) has true bearing a − φ.

**Rotation error.** The prior error σprior comes from the parameter covariance with the stated σi. With N points there are 2N − 4 degrees of freedom; when χ² per degree of freedom exceeds 1, the prior error is multiplied by its square root. With N ≥ 4 we also compute the jackknife error of the N leave-one-out rotations. The registration error σφ is the larger of the scaled prior error and the jackknife error. For a chain of links the rotations add and the errors add in quadrature.

**Acceptance.** A link is accepted when all of these hold: N ≥ 3; the ratio of the smaller to the larger singular value of the centred target points is at least 0.10; χ² per degree of freedom is at most 9; the plan fits better than its mirror image; and, where the plan has a scale bar, the fitted metres per pixel lie within 15% of the scale bar's. A registration with σφ above 5° is accepted but uninformative and is not used. A chain is accepted when every link is.

**Synthetic check.** Before any control point was chosen, `code/selftest.py` checked the sign conventions end to end and the coverage of σφ on synthetic registrations; the result is `selftest-v1/selftest.json`. The coverage of the stated one- and two-sigma intervals was at or above the nominal 68% and 95% in every configuration tried, so the error model is not tuned further.

**Two registrars.** For each plan the accepted, informative registrations are combined by inverse-variance weighting, with σφ equal to the larger of the propagated error and half the difference between the two rotations. Two registrations are flagged discordant when they differ by more than three combined sigmas and by more than 2°; the combination rule still applies and the flag is reported.

## 6. True-north deviations

**Arrow bearing.** With the plan-B page azimuth a_arrow of a plan's north arrow, the arrow's true bearing is α = a_arrow − φ, with error σφ.

**Systems.** Each plan-B system on a registered plan, with deviation θsys relative to the arrow and standard error se, has true-north deviation θtrue = fold(θsys + α) in (−45°, +45°], positive clockwise. Its error replaces the arrow term of plan-B's standard error by the registration error: σtrue² = max(se² − σarrow², 0) + σφ², where σarrow² is the sum of the squares of plan-B's arrow picking and drafting terms, with a floor of 0.3°.

**Town value.** A town's true-north deviation is its plan-B main system (the system that plan-B declared main, before this package existed) converted on its own plan. If that plan is not registered, it is the registered system with the largest total length whose part is the same as the main system's part on another plan of the town. Otherwise the town has no value. Kalibangan's citadel (KLB-1) and lower town (KLB-2) are both reported; the town value follows plan-B's main system.

## 7. Validation

**Primary rule.** At Dholavira and Lothal the town-axes imagery measurers found the castle at −5.50 ± 1.50° and the dock at −1.88 ± 0.30°. For each of the two towns we compare the registered town value (section 6) with the imagery value. For this comparison the registration uses only the control points not flagged `exposed_masonry`, so that it rests on the same kinds of features as the registrations of backfilled towns; if fewer than three such points exist or that registration is not accepted, all points are used and the comparison is labelled. The validation passes when |θreg − θimg| ≤ 2 √(σreg² + σimg²) at both towns.

If it passes, the registered values are offered for scoring. If it fails at either town, the table is still reported with the failure, and the report does not offer the values for scoring until the cause is found and a new protocol tests it.

**Secondary checks, reported without a pass rule.** (a) Arrows of known kind: the Dholavira drawing whose north comes from a latitude-longitude graticule should have α = 0, and Mackay's Chanhu-daro arrow labelled "MAG. NORTH NOV 2ND 1935" should have α equal to the IGRF declination for 1935 used by the town-axes package (+0.886°); we report each difference with its error. (b) The castle systems of the four Dholavira plans and the plans of Lothal, converted to true north, should agree with each other within their errors although their arrows disagree. (c) The two registrars' rotations for each plan, and their discordance flags. (d) The registrations of the validation plans with all points, beside the ones without exposed masonry.

## 8. Counting dated towns

A dated town is one with a layout date in the town-axes exploratory table (`exploratory-v1/table.json`). The towns with true-north values are the four imagery towns and every target or optional town with a registered value. If eight or more dated towns have true-north values and the validation passes, the report says that the frozen P0 of the town-axes protocol can be scored on them, in a separate package with its own protocol. This package computes no correlation between deviation and date.

## 9. Sequence and outputs

1. Freeze: this protocol, `REGISTRATION-BRIEF.md`, `SEARCH-BRIEF.md`, `plans-v1.json` and the code are hashed in `FREEZE.json`; `selftest-v1/selftest.json` is written.
2. The registrars write one control file per plan to `control-R1/` and `control-R2/` (and the search agent to `control-S/` with town files in `measure-S/towns/`), following the format in the brief.
3. When all agents have finished, the coordinator hashes every control and town file into `CONTROL-FREEZE.json`, before running any rotation.
4. `code/register.py` runs once and writes `registration-v1/results.json` and `registration-v1/towns.csv`; it refuses to overwrite an existing output.

Plans, mosaics, crops and overlays are third-party material and stay under `data/raw/2026-10-21-plan-registration/`, which Git ignores.

## 10. Bench and freshness

No task of `python -m bench` scores plan registration or orientation, and this package tests no claim. It measures inputs for the town-axes P0, which spends the proposed family `settlement_axis_orientation` when it is scored. The outputs follow the bench conventions: versioned JSON with `schema_version`, `task`, `synthetic` and `provenance`, input and code hashes, and refusal to overwrite.
