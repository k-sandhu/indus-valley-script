# Astronomy and provisional predictions

The eleven CSV files in theta-c/ are provisional. They use the guessed coordinates in the assignment, not the independently measured town coordinates. Each file has 1,809 rows: nine targets at 201 Julian epochs from astronomical year -3499 to -1499, inclusive. A BCE label B becomes astronomical year 1-B. The epoch is TT with JD = 2451545.0 + 365.25(year-2000).

The target identifiers, in tie order, are alcyone, aldebaran, procyon, equinox_set, equinox_rise, june_set, june_rise, december_set and december_rise. All setting deviations are A-270 degrees and all rising deviations are A-90 degrees, including the solstitial targets. This follows the assignment's explicit definition. Rates are the central difference over D plus and minus 50 years, in degrees per year.

The base columns use k=0.30 and the DEM horizon. The other column pairs use k=0.20, k=0.45, no extinction, and a flat horizon with k=0.30. Each pair contains theta and its rate. The solar values retain the upper-limb and refraction definitions under every variant. Empty CSV numeric fields represent an unavailable value; JSON uses null. Each CSV has a provenance JSON beside it with its hash, input hashes and code hashes.

Run these commands from the repository root in PowerShell. Assign the interpreter once:

    $astroPython = 'data/raw/2026-10-21-town-orientations-verification/venv-astro/Scripts/python.exe'

One command regenerates a town at any measured coordinates. Choose a new output path; every writer refuses an existing output:

    & $astroPython -I experiments/2026-10-21-town-orientations-verification/astronomy/predict.py --table --slug mohenjo-daro --lat 27.324 --lon 68.136 --output experiments/2026-10-21-town-orientations-verification/astro-v1/rechecks/mohenjo-daro.csv

For measured coordinates replace lat and lon, and use a new directory such as astro-v1/theta-c-measured/. A new coordinate pair causes the program to download the required DEM tiles and cache a coordinate-labelled horizon. The caller can also import predict(target, lat, lon, year, extinction_variant, horizon_variant) from astronomy/predict.py. It returns theta and its rate. Library callers must call validation_gate() once before prediction.

For one target and epoch:

    & $astroPython -I experiments/2026-10-21-town-orientations-verification/astronomy/predict.py --target alcyone --lat 27.324 --lon 68.136 --year -2499 --extinction base --horizon dem --output experiments/2026-10-21-town-orientations-verification/astro-v1/example-alcyone-v1.json

The extinction options are base, k020, k045 and none. The horizon options are dem and flat. The function and CLI combine these choices. Horizon rays cover 45..135 and 225..315 degrees every 0.1 degree. Queries outside that azimuth coverage stop with an error.

Horizon files record the DEM surface height, the observer height, every tile hash, every apparent horizon altitude and the distance of the terrain sample that supplies it. We interpret H in the sea-level dip as DEM surface height plus 1.6 m above sea level. The effective radius is 6,371,000/(1-0.13) m. GLO-30 rays include 2,000 through 20,000 m every 30 m. GLO-90 rays include 20,000 through 249,950 m every 90 m and an additional endpoint at 250,000 m. Heights use bilinear interpolation; the edge of a tile uses its nearest boundary cell. Tiles absent from the AWS inventory are sea level. Missing downloads and nodata cells stop the run.

The terrain attribution is © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018 provided under COPERNICUS by the European Union and ESA. The Copernicus DEM licence applies to these derived profiles. Raw tiles and the licence witness remain local.

validation-v1.json records all numerical gates and their tolerances. validation-v1.md explains the results. stars-retrieved-v1.json records the independent SIMBAD measurements and bibcodes. Alcyone, Aldebaran and Procyon use van Leeuwen (2007) for coordinates, proper motion and parallax. The validation-only Thuban record retains Gaia coordinates because SIMBAD's TAP interface exposes only its preferred coordinate record; its Hipparcos 2007 proper motion and parallax were recovered from the measurement tables. This source exception is explicit in the star and validation records.

selftest-analysis-v1.json preserves the first analysis checks. selftest-analysis-v2.json checks the revision after compare.py gained automatic predictions for settlement CSVs, and selftest-analysis-v3.json is the current complete check after the attribution encoding repair. All are synthetic; they contain no measured settlement deviations or layout dates. RUN-NOTES.md records the implementation, repairs, source coverage and remaining limits. SOURCE-MANIFEST-v1.json records the local downloads.

To retrieve the source set on a fresh local copy:

    & $astroPython -I experiments/2026-10-21-town-orientations-verification/astronomy/sources.py
    & $astroPython -I experiments/2026-10-21-town-orientations-verification/astronomy/prepare_stars.py --output experiments/2026-10-21-town-orientations-verification/astro-v1/stars-retrieved-v1.json

On the existing run that output already exists, so the second command refuses to replace it. prepare_stars.py matches SIMBAD identifiers explicitly and checks the preferred astrometric bibcodes for the prediction stars. The preserved rechecks/stars-reassembled-v1.json has identical numerical star data.

Rebuild the environment with C:\Python313\python.exe -m venv data/raw/2026-10-21-town-orientations-verification/venv-astro, then install the versions in environment.txt. We used pip --isolated with the public PyPI index and disabled its cache. No environment or raw downloads should be tracked.

A fresh validation and analysis check use:

    & $astroPython -I experiments/2026-10-21-town-orientations-verification/astronomy/validate.py --output experiments/2026-10-21-town-orientations-verification/astro-v1/rechecks/validation-v1.json
    & $astroPython -I experiments/2026-10-21-town-orientations-verification/analysis/selftest.py --output experiments/2026-10-21-town-orientations-verification/astro-v1/rechecks/selftest-analysis-v1.json

These paths are also exclusive. Use another version after a recorded recheck exists.

COPERNICUS-ATTRIBUTION-v1.txt supplies the complete Unicode attribution for every frozen profile and derived table. attribution-correction-v1.json records the ASCII encoding repair; no numerical output was changed.
