# Protocol: were the Harappan towns laid out on the stars?

Frozen on 21 October 2026, before the coordinating agent opened any measurement or dating output of this package and before any star or sun position was computed. The SHA-256 of this file is recorded in `PROTOCOL.sha256`. Changes after the freeze go into dated amendments; this file stays as written.

## The claim and where it comes from

Study 4 of the [direction note of 20 October](../../knowledge/directions/parpola-forward-2026-10-20.md) states the claim at full strength: Harappan builders aligned the main axes of new towns on the setting point of a bright star or star group, so a town's deviation from the cardinal directions records when it was laid out. Holger Wanzke proposed this for Mohenjo-daro in "Axis Systems and Orientation at Mohenjo-Daro" (*Interim Reports* vol. 2, 1987, printed pp. 33–44), choosing Aldebaran and noting that the theory needed exact orientations at other Harappan sites. The direction note pointed out that his own table of setting points puts the Pleiades close to the Mohenjo-daro axes at the city's foundation, and the Pleiades head the asterism list that Asko Parpola places in the Harappan calendar.

Before freezing we read Wanzke's paper on the scan held at `research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf` (printed page = PDF page index − 2 on this scan). His architectural tables (printed pp. 33–34) are in gon, 400 to the circle, with clockwise deviation positive (footnote 2, p. 38). They give a first axis system of "ca. 8 gon clockwise" (about 7.2°) for the main streets of the SD, L, HR, VS, Dales and DK-B and DK-G areas, topographical axes of 9.0–11.0 gon, and a second system oriented exactly to the cardinal points in the Moneer and DK-C areas. His Fig. 11 shows the first system's axes visibly turned clockwise, and his Fig. 9 marks "+9 gon" on the western horizon profile. The text of p. 37 instead says that the architectural axes "show a slight divergence from the cardinal points of 1° to 2° clockwise", and the match with Aldebaran in 2000–1600 BCE (setting −3.0 gon in 2500 BCE, +3.8 gon in 1500 BCE) is argued from that figure. The direction note's "1–2°" comes from p. 37 and its star values are Wanzke's gon values converted to degrees. Our measurements decide which figure describes the city; this protocol does not depend on either.

On p. 34 Wanzke also lists orientations taken from Jansen (1979) for other sites, in gon from north with unknown north reference: Harappa citadel 0 and streets −11 to +6, Surkotada town wall −16, Lothal "dock" wall +5.5 and Street 1 −4.4, Sutkagen-dor −2, Balakot +3.3 and −1, Kalibangan surrounding wall 0, exterior wall −2 and main street −13. The coordinating agent saw these values before writing this protocol. They are not used in scoring, and no measurer was given them.

## Data: the settlement-axis table

The table is built for every Harappan town with straight architecture that our measurers could measure, starting from the eleven towns named in the direction note (Mohenjo-daro, Harappa, Kalibangan, Lothal, Dholavira, Surkotada, Banawali, Rakhigarhi, Chanhu-daro, Kanmer, Shikarpur) and the optional towns in [towns-v1.json](towns-v1.json). Four agents measure every town without seeing each other's numbers or this protocol, under [MEASUREMENT-BRIEF.md](MEASUREMENT-BRIEF.md): img-A picks line endpoints on Esri World Imagery mosaics, img-B computes gradient-orientation peaks inside polygons drawn on the same service, and plan-A and plan-B measure published plans relative to their north arrows. A fifth agent records layout phases and their dating evidence under [DATING-BRIEF.md](DATING-BRIEF.md). The SHA-256 of the briefs and the town list are in `briefs.sha256`. None of these agents was told about stars, the sun or calendars.

The deviation θ of a line is its bearing from true north folded to the nearest cardinal direction, in (−45°, +45°], positive clockwise. A clockwise deviation θ turns the west end of an east–west street θ degrees north of west, toward the setting point of a star of small positive declination.

### Town deviation

For each measurer we take the main system that the measurer declares, with its length-weighted mean deviation and standard error. The town's deviation comes from the two imagery measurers, because Web Mercator imagery is referenced to true north by construction.

1. Two systems lie in the same part of a town when their measured lines or polygons come within 200 m of each other. If img-A and img-B both declare a main system and the two lie in the same part (or one of them covers the whole town), the town deviation θ is the inverse-variance weighted mean of the two values. If they lie in different parts, we take for each part the sum of the total measured lengths that both measurers report in that part, choose the part with the larger sum, and combine the two measurers' systems for that part; a measurer with no system there contributes nothing.
2. If only one imagery measurer has a value, it is used alone.
3. If neither imagery measurer has a value, the town deviation comes from plan systems whose arrow is classified `true`, or `grid` with 0.5° added in quadrature to the error, combined in the same way. Plans with `magnetic` or `unspecified` arrows never enter the primary value.
4. The town error is σθ = max(propagated standard error, half the difference between the two combined values, 0.3°). The 0.3° floor covers imagery registration and the definition of a wall line.
5. Two imagery values differing by more than 3 combined standard errors and by more than 1.5° are flagged as discordant; the rule above still applies, and the flag is reported.

The table also keeps every other system, each plan value with its north reference, and for plans with a magnetic arrow and a stated or inferable survey year a declination-corrected value from the IGRF model (1900 onward), used only for the comparison of plans with imagery. A town enters scoring when it has a primary deviation and a layout date.

### Layout date

The date D of a town is the start of the layout phase of the part whose system gave the town deviation: the phase in which its exposed Harappan walls or street grid were first built. It is chosen in this order of evidence.

1. A published Bayesian model of the site's phases: the median of the start boundary of the layout phase, with σD equal to the width of its 95% range divided by 3.92.
2. A published synthesis or excavation report that states a calibrated calendar start for the layout phase on the basis of radiocarbon determinations from the site: the stated start, with σD equal to a quarter of the stated range for the start if one is given, otherwise 150 years.
3. An excavator's start date for the layout phase based on cross-dating without radiocarbon: the stated start, with σD = 200 years.

Where sources at the same level disagree, the most recent one is used and the disagreement is recorded. A town whose layout phase has no calendar start at any level is reported without a date and does not enter scoring. As a sensitivity check we calibrate the radiocarbon determinations of each layout phase with IntCal20 and take the median calendar age of the oldest determination; we also repeat the main statistic with the date of first occupation in place of the layout date.

## Astronomy

Each candidate target is turned into a predicted deviation θc(D, town): the direction, measured from the cardinal direction of the nearest arm of the grid, in which the target was last seen setting (or first seen rising) at the town's latitude and horizon in the year D.

**Targets.** The three stars named in the direction note set on the western horizon: the Pleiades represented by Alcyone (η Tauri, HIP 17702, V = 2.87), Aldebaran (α Tauri, HIP 21421, V = 0.86) and Procyon (α Canis Minoris, HIP 37279, V = 0.34). The sun contributes six targets: setting and rising at the equinoxes, at the June solstice and at the December solstice. The list of nine is fixed and its order (Alcyone, Aldebaran, Procyon, then the solar targets) breaks ties.

**Positions.** J2000 positions, proper motions, parallaxes and radial velocities come from SIMBAD (Hipparcos new reduction, van Leeuwen 2007, with the radial velocities SIMBAD lists), retrieved and hashed before use. Space motion to the epoch uses ERFA `pmsafe`; precession uses the long-term model of Vondrák, Capitaine and Wallace (2011, *Astronomy & Astrophysics* 534, A22) through ERFA `ltpb`, valid over ±200,000 years. Nutation, aberration and annual parallax are ignored, as they move these targets by less than 0.01°. Years BCE are astronomical years (2500 BCE = −2499), taken as Julian epochs. The sun's declination is +ε at the June solstice, −ε at the December solstice and 0 at the equinoxes, where ε is the mean obliquity from the same Vondrák model (the angle between the ecliptic pole from `ltpecl` and the equator pole from `ltpequ`).

**Horizon.** The horizon altitude for every azimuth from 45° to 135° and from 225° to 315°, at 0.1° steps, comes from the Copernicus DEM: GLO-30 out to 20 km and GLO-90 from 20 to 250 km, sampled every 30 m and 90 m along each ray. The observer stands 1.6 m above the DEM surface at the town coordinates used by the imagery measurers (their mean where both report). Terrain within 2 km is excluded, so the archaeological mound, the trees and buildings on it and the modern village do not count as horizon. The apparent elevation of a terrain point at distance d and height difference Δh is atan(Δh/d − d/(2R')), with R' = 6,371 km / (1 − 0.13) for terrestrial refraction. The apparent horizon at an azimuth is the largest of these elevations and of the sea-level dip of the observer. The sensitivity check uses a flat horizon at apparent altitude 0°.

**Refraction and extinction.** Astronomical refraction follows Bennett (1982) with a temperature of 20 °C and a pressure of 1010 hPa. A star is last seen setting at the apparent altitude hv = max(apparent horizon, e), where e is its extinction angle: the altitude at which m + k (X(e) − 1) equals the limiting magnitude 6.0 of a dark sky at the zenith, with k = 0.30 magnitudes per air mass and the air mass X of Kasten and Young (1989) evaluated at the apparent altitude. The checks repeat the score with k = 0.20 and k = 0.45, and with no extinction (hv equal to the apparent horizon). The sun is taken at the moment its upper limb touches the apparent horizon, with semi-diameter 0.267°.

**Azimuth and predicted deviation.** For declination δ, latitude φ and true altitude h = hv − R(hv), the azimuth from north satisfies cos A = (sin δ − sin φ sin h)/(cos φ cos h), taking the western solution for setting and the eastern for rising. Because the horizon varies with azimuth, the computation is iterated until the azimuth changes by less than 0.001°. The predicted deviation is the azimuth minus the nearest cardinal direction: 270° for the setting stars and the equinoctial sunset, 90° for the equinoctial sunrise. A positive value therefore means a clockwise grid in both cases, since turning a grid clockwise by θ moves its west arm θ north of west and its east arm θ south of east. For the solstitial sun, whose setting and rising points lie 25–30° from east and west at these latitudes, the deviation is taken from the same nearest cardinal direction and can therefore exceed 20°. The rate dθc/dD is computed numerically from θc at D ± 50 years.

**Validation gate.** Before the code touches the measured data, it must reproduce three checks: the mean obliquity in 2500 BCE within 0.02° of 23.97°; the minimum polar distance of Thuban (α Draconis) falling between 2900 and 2700 BCE; and a geometric setting azimuth for Aldebaran at Mohenjo-daro in 2500 and 1500 BCE that we compare with Wanzke's −3.0 and +3.8 gon and report. The comparison with Wanzke is reported, not gated, because his horizon and refraction assumptions are not stated.

## Stage 1: choosing the target on three towns

The target is chosen on Mohenjo-daro, Harappa and Kalibangan and frozen before any other town is scored. For each candidate c, over the discovery towns t with a deviation and a date,

χ²c = Σt (θt − θc(Dt, t))² / (σθ,t² + (dθc/dD · σD,t)² + σint²),

with an intrinsic builders' scatter σint = 1.0°. The chosen target c* is the one with the smallest χ²c; at least two discovery towns are needed. The stage writes `discovery-v1/choice.json` with every χ²c, the choice and the hashes of its inputs and code, and the SHA-256 of that file is written to `discovery-v1/choice.sha256` before stage 2 runs. If the smallest χ²c exceeds the 99th percentile of χ² with as many degrees of freedom as discovery towns, the choice is still carried forward and flagged as a failure on the discovery towns.

## Stage 2: the frozen predictions

Every prediction is computed once from the frozen inputs and reported whether it passes or fails. "All towns" means every town with a primary deviation and a layout date; "confirmation towns" are all of them except the three discovery towns.

**P0, the kill condition.** Across all towns, deviation rises with later layout date. The statistic is Pearson's r between θ and D (in astronomical years, so later is larger), with a one-sided permutation p-value from all permutations when n ≤ 9 and 200,000 random permutations otherwise. P0 passes when p < 0.05, Spearman's ρ is positive, and r stays positive when any single town is left out. It requires n ≥ 8; with fewer towns the claim is undecided. If P0 fails with n ≥ 8, deviation and founding date are uncorrelated across at least eight towns and the claim is dead as stated in the direction note. We repeat P0 on the confirmation towns alone and report the slope of θ on D by weighted least squares, with weights 1/(σθ² + σint²) and a 95% interval from 20,000 bootstrap resamples of towns, beside the 0.5° per century that the Pleiades and Aldebaran models both predict.

**P1, the Pleiades version.** Every town deviates clockwise, by about 0.5° more per century of later layout. P1 passes when at least 80% of all towns have θ > 0, no town has θ < −2σθ, and the 95% interval of the fitted slope contains the slope predicted by the Alcyone model at the towns' latitudes and excludes zero.

**P2, the Aldebaran version.** The deviation changes sign around 2050 BCE: anticlockwise in towns laid out earlier and clockwise in later ones. For each town the Aldebaran model gives a predicted sign. P2 passes when at least 80% of all towns whose predicted deviation differs from zero by more than 0.5° have θ of the predicted sign, with n ≥ 8 such towns.

**P3, the chosen target.** The target c* chosen in stage 1 predicts the confirmation towns better than two alternatives without stars: cardinal intent (θ = 0 for every town) and a constant offset equal to the weighted mean deviation of the discovery towns. The statistic is χ² over confirmation towns with the stage-1 error model. P3 passes when χ²c* is smaller than both alternatives' χ² and the χ² probability of χ²c* with as many degrees of freedom as confirmation towns exceeds 0.05. A leave-one-out check reports whether the ordering of the three χ² values survives the removal of any single confirmation town.

**Power.** Before P0 is computed, we simulate it 20,000 times with the towns' actual dates and errors, deviations drawn from the Alcyone model plus Gaussian errors (σθ, σD and σint), and report the probability that P0 passes. The simulation uses no measured deviation.

**Credence.** The conjecture enters at credence 0.10. The joint rule is: P0 failing with n ≥ 8 sets it to 0.02 and the status to dead; P0 passing with P3 passing sets it to 0.40; P0 passing with P3 failing sets it to 0.15; fewer than eight towns leaves it at 0.10 with the status open. P1 and P2 decide only which version of the claim survives: a version whose prediction fails is recorded as failed even if the general claim survives.

**D1, a descriptive check on Mohenjo-daro.** We report which of Wanzke's two figures, about 7.2° (8 gon) from his tables or 1–2° from his p. 37, lies within 2σθ of our Mohenjo-daro deviation. It has no pass rule.

## Sensitivity checks

These are reported with the result and do not change the pass rules: extinction coefficients 0.20 and 0.45 and no extinction; a flat horizon; IntCal20 dates and first-occupation dates in place of layout dates; every measured system of a town as a separate point with its own part's date where the dating gives one; img-A alone and img-B alone; and true-north plan values in place of imagery.

## Freshness and the bench

This test uses no inscriptions, so it spends nothing in the corpus and no split of the inscription corpus applies. No task of `python -m bench` scores settlement orientations; the scorer of this package follows the bench conventions (versioned JSON with `schema_version`, `task`, `synthetic` and `provenance`, input and code hashes, and refusal to overwrite existing outputs). The population is new: no earlier package measured town orientations, and `bench/spent.json` has no family for them. We propose the family `settlement_axis_orientation` for the ledger in the package record. The Mohenjo-daro orientation was examined by Wanzke, and the coordinating agent saw Jansen's 1979 values for six sites as listed above.

## Outputs

All outputs go to new dated directories and are never overwritten: `horizon-v1/`, `dates-v1/`, `table-v1/` (the settlement-axis table as JSON and CSV), `validation-v1/`, `discovery-v1/`, `confirmation-v1/` and `sensitivity-v1/`, each with the hashes of its inputs and code. A file `FREEZE.json` records the hashes of this protocol and of the code before stage 1 runs.
