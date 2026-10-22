# Scoring and comparison

score_frozen.py implements the frozen target choice and P0 through P3. compare.py compares bearings, layout dates and astronomical predictions. calibrate.py supplies an IntCal20 annual calendar distribution and the distribution of the oldest determination in a phase. Every JSON contains schema_version 1.0, task, synthetic and provenance, with input and code SHA-256 hashes. Existing output paths are rejected.

The settlement CSV header is:

    slug,part,role,lat,lon,theta_deg,sigma_theta_deg,D_year,sigma_D_years

There is one row per town, with the part that supplied its primary bearing and date. Do not turn several walls or alternative parts into independent towns. The three discovery slugs are mohenjo-daro, harappa and kalibangan; the other towns have role confirmation. Coordinates are decimal WGS84 degrees. theta is positive clockwise in degrees. D is an astronomical year: 2500 BCE is -2499. The standard deviations are in degrees and years. Missing or non-finite required numbers and duplicate slugs are rejected.

Optional columns thetac_<target> and rate_<target> supply a predicted deviation and a rate in degrees per year. Both values must be present for a target-row pair to bypass the predictor. The nine target identifiers are alcyone, aldebaran, procyon, equinox_set, equinox_rise, june_set, june_rise, december_set and december_rise. Without supplied values, each script uses astronomy/predict.py at that row's coordinates and date and builds a horizon when necessary. Supplied values are the caller's responsibility and must correspond to the chosen sensitivity variant.

Run from the repository root with the isolated environment:

    $astroPython = 'data/raw/2026-10-21-town-orientations-verification/venv-astro/Scripts/python.exe'
    & $astroPython -I experiments/2026-10-21-town-orientations-verification/analysis/score_frozen.py path/to/settlements.csv --output experiments/2026-10-21-town-orientations-verification/astro-v1/score-v1.json

Add --fixed-target alcyone to use a supplied frozen target. The result still reports the discovery choice the table would make and the discovery failure flag. Add --extinction k020, --extinction k045 or --extinction none for the extinction variants, and --horizon flat for the horizon variant. The default seed is 20261021; --seed changes it. The primary counts are fixed at 200,000 permutations when there are more than nine towns, 20,000 town bootstrap resamples, and 20,000 power simulations with 2,000 random permutations per simulation.

P0 uses the upper tail of Pearson's positive association with chronological year. For nine or fewer towns it enumerates all n! permutations, including the observed arrangement, and divides the count by n!. The random test uses (count+1)/(draws+1). It also requires positive Spearman rho and a positive Pearson coefficient after each town is removed. It is undecided with fewer than eight towns. We report P0 and the fitted slope for the confirmation towns as well as for the full table. Slope intervals use paired bootstrap resampling of towns; resamples with a single distinct date have no slope and are counted separately.

P1 compares the fitted slope interval with the weighted least-squares slope of the Alcyone predictions at the observed dates. Both fits use weights 1/(sigmaTheta squared + 1 degree squared). The mean local Alcyone rate is a separate output. P2 excludes predicted Aldebaran deviations within 0.5 degrees of zero and needs eight remaining towns. P3 uses the selected target on confirmation towns, the cardinal model and the discovery towns' weighted constant offset. Each model's error denominator uses its own rate; the cardinal and constant models have zero rate. The leave-one-out output gives the full ordering and whether the selected target still beats both alternatives.

Power adds independent normal date, bearing and intrinsic errors to the Alcyone model. It evaluates every sampled date directly with the vector version of our astronomy, using the actual town coordinates and sensitivity options. It does not substitute the supplied theta and rate columns for the Alcyone function between dates. The synthetic selftest instead supplies an explicitly synthetic linear model. There are 2,000 independent random permutations inside each simulation, also when the observed P0 would enumerate all permutations.

D1 checks 7.2 degrees against Mohenjo-daro's measured deviation plus or minus two standard deviations. For the 1..2 degree interval it reports both intersection with that measurement interval and full containment; intersection is the compatibility interpretation. The output keeps this choice explicit because an interval is not a single orientation.

For two settlement tables:

    & $astroPython -I experiments/2026-10-21-town-orientations-verification/analysis/compare.py path/to/first.csv path/to/second.csv --output experiments/2026-10-21-town-orientations-verification/astro-v1/comparison-v1.json

The sign of every difference is first minus second. The script lists unmatched towns, computes bearings and dates on the common slugs, and calculates or accepts astronomical predictions for each table. Its settlement astronomy comparison uses only rows with matching coordinates and dates, and lists the other slugs. It reports undecided when no same-coordinate, same-date astronomy pairs remain. Astronomy predictions must be evaluated at the same coordinates and dates before interpreting a difference as a difference between implementations.

You can also compare two long astronomy tables directly:

    & $astroPython -I experiments/2026-10-21-town-orientations-verification/analysis/compare.py --astro-first path/to/first-theta.csv --astro-second path/to/second-theta.csv --output experiments/2026-10-21-town-orientations-verification/astro-v1/astronomy-comparison-v1.json

A long astronomy CSV has slug, lat, lon, year, target and theta_base, or theta_deg in place of theta_base. A wide CSV can use D_year and the optional thetac_<target> columns. Both astronomy tables must have identical slug, coordinate, date and target keys. The script reports each target's largest absolute difference and the 0.10 degree rule. Fewer than all nine targets leave the overall result undecided unless an observed target already disagrees.

An adapter for another study should only map names and units into the common header. Write it after that study's report is released. Use csv.DictReader on its documented table, build one dictionary per town, and use csv.DictWriter with the header above. For example, a source field called layout_bce maps to D_year = 1-float(layout_bce), and an orientation standard deviation already in degrees maps directly to sigma_theta_deg. A gon value maps to degrees by multiplying by 0.9. Preserve the selected part and source uncertainties, assign discovery roles by the three specified slugs, and copy optional model fields only when their coordinate, epoch and variant definitions agree. Record the source file and adapter hashes with the adapted table. We have not opened or adapted the other study's files.

For a single radiocarbon determination:

    & $astroPython -I experiments/2026-10-21-town-orientations-verification/analysis/calibrate.py --bp 4000 --sigma 30 --output experiments/2026-10-21-town-orientations-verification/astro-v1/calibration-example-v1.json

For several determinations, pass --determinations path/to/determinations.json, containing a JSON list of objects with BP and sigma_BP. The calendar prior is uniform over the curve's 0..55,000 cal BP domain. The likelihood adds laboratory and interpolated curve variance in quadrature. The output includes each annual probability, the median in cal BP and astronomical years, and for a phase the probability distribution and median of the oldest age. The phase calculation multiplies independent cumulative distributions of calendar BP, then differences that product. It also reports the oldest individual median. Shared calibration-curve covariance and archaeological phase boundaries are not modelled.

Run all synthetic checks with analysis/selftest.py --output followed by a new JSON path. Each analysis script also has --selftest --output. astro-v1/selftest-analysis-v3.json is the current combined result; v1 preserves the checks before compare.py gained automatic prediction, and v2 precedes the attribution encoding repair. The tests use synthetic settlement values and the downloaded calibration curve. They do not inspect measurements or dates from either study. integration-analysis-v1.json also exercises the real astronomical function in the full 20,000-simulation power calculation on explicitly synthetic town deviations and dates.
