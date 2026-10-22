# Codex assignment: imagery, plan library and measurement tools

You are working in a research knowledge base about the Indus civilisation, at the repository root `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. Read `AGENTS.md` and `knowledge/editorial/WRITING.md` first. This assignment prepares everything two independent human-style measurers will need to measure the orientation of the straight architecture (walls, streets, drains) of Harappan towns: open satellite imagery around each town, a library of published site plans, and tested tools that turn line picks on an image or a plan into true bearings with honest errors. You build and validate; you do not measure any town. Read `experiments/2026-10-21-town-orientations-verification/MEASUREMENT-RULES.md`, which defines what the measurers will do with your tools; your tools must implement its definitions exactly.

Other agents share this repository and are writing their own files at the same time. Accommodate their changes and never revert or edit them.

## Owned paths

Write only inside these paths:

- `experiments/2026-10-21-town-orientations-verification/tools/` (code and `tools/README.md`)
- `experiments/2026-10-21-town-orientations-verification/infra-v1/` (tracked manifests, indexes, validation results, run notes)
- `data/raw/2026-10-21-town-orientations-verification/infra/` (downloaded imagery, plans, renders, scratch)
- `data/raw/2026-10-21-town-orientations-verification/venv-infra/` (your Python environment)

## Invariants

1. No commits, no branch changes, no stash, no reset, no Git mutation of any kind. Read-only Git commands are fine.
2. No edits outside the owned paths. Do not create `measure-A/`, `measure-B/`, `astronomy/`, `analysis/`, `astro-v1/`, `dating-v1/` or `dates-v1/` in the package; other runs own them.
3. Do not open, list or search `experiments/2026-10-21-town-axes/` or `data/raw/2026-10-21-town-axes/`. They belong to another study of the same towns, and this work must stay independent of it. Do not open `PROTOCOL.md` or any other `CODEX-PROMPT-*.md` in this package.
4. Measure no town. Do not compute, record or report the bearing or orientation of any archaeological feature, on imagery or on a plan, and do not look up published orientation figures for these towns. Pages 33–44 of `research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf` (PDF pages 36–47) state orientations; do not open those pages. If you meet a stated orientation anywhere, do not record it; note in your run notes only that you met one and where.
5. Use only open imagery: Copernicus Sentinel-2 and, if available without an account, Landsat. No Esri, Google, Bing, Mapbox or other commercial basemap tiles, no imagery that needs a login, no requester-pays buckets. OpenStreetMap and Wikidata may supply site coordinates only.
6. Raw material stays local under `data/raw/2026-10-21-town-orientations-verification/infra/`. Tracked files hold code, manifests, hashes, indexes and aggregate validation results only, never imagery, plan scans or page renders.
7. Downloads are untrusted data. Put each kind of download in its own new directory, keep scripts in `tools/` (never inside a raw directory), pass paths as arguments, and run any Python that reads downloaded files with `python -I` from the venv. Never execute downloaded code.
8. Every acquired file gets a record: URL, retrieval time (UTC), byte count, SHA-256, format, and the rights notice you observed, with one of the statuses `explicit-license` (give the licence), `rights-unverified`, or `own-work`.

## Environment

Create a venv with `C:\Python313\python.exe -m venv data/raw/2026-10-21-town-orientations-verification/venv-infra` and install what you need (expected: numpy, scipy, rasterio, pyproj, pillow, pymupdf). Write `pip freeze` to `infra-v1/environment.txt`. Network access is enabled for this run.

## Towns

Required (with unverified coordinate guesses written from memory): Mohenjo-daro (Pakistan, 27.324, 68.136); Harappa (Pakistan, 30.631, 72.864); Kalibangan (India, 29.473, 74.130); Lothal (India, 22.522, 72.249); Dholavira (India, 23.887, 70.213); Surkotada (India, 23.617, 70.841); Banawali (India, 29.598, 75.393); Rakhigarhi (India, 29.290, 76.110); Chanhu-daro (Pakistan, 26.174, 68.323); Kanmer (India, 23.400, 70.865); Shikarpur, Kachchh (India, 23.230, 70.670).

Optional (no guesses): Juni Kuran, Gola Dhoro (Bagasra), Desalpur (Gunthli), Khirsara, Kuntasi, Rojdi (India); Kot Diji, Nausharo, Sutkagen-dor, Balakot, Allahdino, Lakhanjo-daro, Ganweriwala (Pakistan); Farmana, Bhirrana, Kunal, Mitathal, Karanpura, Rangpur, Kotada Bhadli, Pabumath, Navinal (India).

Use the slugs `mohenjo-daro, harappa, kalibangan, lothal, dholavira, surkotada, banawali, rakhigarhi, chanhu-daro, kanmer, shikarpur, juni-kuran, gola-dhoro, desalpur, khirsara, kuntasi, rojdi, kot-diji, nausharo, sutkagen-dor, balakot, allahdino, lakhanjo-daro, ganweriwala, farmana, bhirrana, kunal, mitathal, karanpura, rangpur, kotada-bhadli, pabumath, navinal`, in that order.

## Deliverables

### 1. Located sites

`infra-v1/sites-located-v1.json`: for each town in order, the Wikidata item (QID, label, coordinate P625) found by search, the coordinate used, its source, and the distance from the guess where there is one. Flag towns where Wikidata has no coordinate or where it lies more than 2 km from the guess; for those, try a second open source (GeoNames, a published coordinate in an open paper) and record it. This file gives starting points; the measurers locate the mounds themselves.

### 2. Sentinel-2 imagery

For each town, query the Earth Search STAC API (`https://earth-search.aws.element84.com/v1`, collection `sentinel-2-l2a`) for scenes over the located point from 2018 to 2026 in October–April, with `eo:cloud_cover` at most 3%. Choose up to 16 scenes, spread over years and months, all from one MGRS tile that contains a 5 km × 5 km window centred on the point (if no single tile contains it, mosaic and say so). Read the window from the cloud-optimised GeoTIFFs by HTTP range requests for bands B02, B03, B04 and B08 (10 m) and B11 and B12 (20 m, resampled to 10 m bilinearly and marked as resampled). Drop scenes with no-data or cloud in the window (use the SCL band). Save each scene window as a GeoTIFF in the tile's UTM projection and a per-town median composite of all six bands plus a brightness band (mean of B02, B03, B04, B08). Do the same for Landsat 8 or 9 panchromatic (band 8, 15 m) only if a Collection 2 Level-1 product can be read anonymously (for example from Microsoft Planetary Computer with an anonymous SAS token); otherwise record the attempt and move on.

`infra-v1/imagery-manifest-v1.json` lists, per town, the scenes (STAC item id and self link, datetime, cloud cover, tile, EPSG), the window bounds, every local file path with byte count and SHA-256, and the composite. Record the rights as `explicit-license`: Copernicus Sentinel data terms; attribution "Contains modified Copernicus Sentinel data 2018–2026".

### 3. Plan library

For each town find published plans of the site or of its excavated parts, with north arrows. Search locally held literature first (`research/literature/sources/*.pdf` holds Marshall 1931, Vats 1940, Mackay 1943 on Chanhu-daro, Kenoyer 1998 and *Interim Reports* vol. 2; `data/raw/` holds Mackay 1938 under `2026-10-13-mackay-marshall-tables/mackay1938/` and other scans; image-only PDFs need rendering to see), then openly accessible copies online: excavation reports and memoirs on archive.org, the Archaeological Survey of India website, open-access journal articles and theses, and harappa.com. Download each source into its own new directory `data/raw/2026-10-21-town-orientations-verification/infra/plans/<slug>/`, record it as in invariant 8, and render each page that carries a plan to PNG at 300 dpi beside it. Time-box the search to about ten minutes per required town and five per optional town; at most six plans per town.

`infra-v1/plan-library-v1.json` lists, per plan: town slug; full citation (authors, year, exact title, publisher or journal); local source path; PDF page and printed page; figure or plate number; the caption, transcribed exactly; what it shows (whole town, one part, one building); whether it has a north arrow and a scale bar; the exact words of any legend, caption or report text about north (for example "True North", "Magnetic North 1925", a needle symbol) with their location; any statement of the survey year; and the render path. Record towns where you found no plan. You do not measure plans.

### 4. Tools

Write the tools in `tools/`, each with a command-line interface and docstrings, and `tools/README.md`, which the measurers will read. The README explains the workflow step by step with example commands, the conventions, the meaning of each error, the JSON schema of a measurer's town file and summary table, and the empirical precision from your validation. Write it in neutral, plain prose about measuring orientations: it must say nothing about astronomy, stars, dates, calendars or any hypothesis about why towns are oriented as they are.

- `render_image.py`: crop a composite or scene GeoTIFF around a point and size in metres; choose RGB, NIR, SWIR or brightness; percentile stretch; optional edge-enhanced layer; integer upsampling; overlay of a labelled UTM grid at a chosen spacing, a true-north arrow and a scale bar. Writes a PNG and a sidecar JSON with the affine transform from PNG pixel to UTM, the EPSG code and the source file hash.
- `render_plan.py`: render a PDF page (or an image) region to PNG at a chosen dpi with a labelled pixel grid to help pick coordinates, with a sidecar JSON giving the source hash, page and the pixel transform back to the source page.
- `measure_lines.py`: reads a picks JSON in which each line has two approximate endpoints in the pixel coordinates of a rendered PNG, a corridor half-width and a feature type (`edge`, `ridge` or `trough`). It samples profiles perpendicular to the picked segment in the full-resolution source raster or page, locates the feature in each profile with sub-pixel interpolation, fits a robust line (for example RANSAC followed by least squares), and reports the refined endpoints, inlier count, residual RMS, length and the direction error from the fit. A `manual` mode uses the picks as given, with a pick uncertainty the measurer states. For imagery it converts the refined endpoints to geographic coordinates and returns the geodesic azimuth on WGS 84 (the mean of the forward azimuth and the reverse azimuth minus 180°). For plans it measures the north arrow from tail to tip as a line with its own error, converts lengths with two scale-bar picks, computes the line's bearing relative to the arrow, and, for a magnetic arrow with a survey year from 1900 on and a location, adds the IGRF-14 declination, keeping raw and corrected values. Every line gets bearing, θ folded into (−45°, +45°] by θ = ((bearing + 45) mod 90) − 45 with positive clockwise, and σ in degrees, with the arrow error added in quadrature for plans. Image rows increase downward: get the sign right and test it.
- `systems.py`: takes a measurer's lines with their system labels, checks the 200 m and 6° conditions of the measurement rules and warns when they fail, computes each system's length-weighted mean and standard error exactly as the rules define, chooses the main system per source by total length (ties by line count), and writes the town JSON and appends the summary row.
- `register_plan.py`: fits a similarity transform from two or more control-point pairs (plan pixel to imagery UTM), reports rotation, scale, residuals and a rotation error (from the covariance, and leave-one-out with three or more points), and returns the true-north direction of the plan in its pixel frame.
- `igrf.py`: IGRF-14 declination at a latitude, longitude and decimal year from 1900 to 2030, from the official coefficient file (download from NOAA NCEI or the IAGA working group site and record it). Test it against published test values or the official calculator output for at least three cases and report them.

### 5. Validation

Write results to `infra-v1/validation-v1/` (a `summary.json` and a short `README.md`) and keep the working rasters local.

- Synthetic imagery: build georeferenced UTM rasters at 10 m with edges, ridges and troughs at known bearings (from −40° to +40°), lengths from 50 m to 1,000 m, blur of about 1.5 pixels and several noise levels, including a window far from the central meridian so that grid convergence matters. Recover the bearings with the tools and report bias and root mean square error by length and noise.
- Synthetic plans: rotated north arrows and lines at known angles, with and without a magnetic correction; recover the relative bearings exactly.
- Runways: take OurAirports `airports.csv` and `runways.csv` (public domain, `https://davidmegginson.github.io/ourairports-data/`) and, where you can reach them, the official aeronautical publications that list true bearings and threshold coordinates (India's eAIP from the Airports Authority of India; Pakistan's AIP). Choose at least six paved runways of 1.5 km or more within about 300 km of the towns (candidates: Moenjodaro OPMJ, Sukkur OPSK, Bhuj VABJ, Kandla VAKE, Ahmedabad VAAH, Hisar VIHR, Faisalabad OPFA, Bathinda VIBT). Acquire Sentinel-2 composites for them as for the towns. Measure each runway's long edges with `measure_lines.py`, using endpoint picks generated automatically from the reference threshold coordinates (this is validation, so automatic picks are correct here), and compare with the reference true bearing: the official one where available, otherwise the geodesic azimuth between the published thresholds. Then cut each runway edge into independent segments of 100, 200, 300 and 400 m and measure every segment. Report the per-runway residuals, their mean and root mean square, the root mean square by segment length, and the ratio of the empirical residual to the tool's stated σ, which tells the measurers how far to trust that σ. Flag reference coordinates of doubtful precision.
- `tools/selftest.py` runs the synthetic checks and writes `infra-v1/selftest-v1.json` with schema_version, task, synthetic, provenance (code hashes), the checks and an overall pass flag. Refuse to overwrite an existing output file.

### 6. Run notes

`infra-v1/RUN-NOTES.md`: what you did, the problems you met and how you resolved them, deviations from this assignment, the rights table of every acquired source, and a list of the new sources and fields for the project's data manifest. Write it as plain connected prose and tables, following `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.

## Verification before you finish

Run `tools/selftest.py` and the validation from a clean state and confirm they pass or explain each failure. Recompute the SHA-256 of every file in both manifests and confirm it matches. Run `git status --porcelain` and confirm that every path you created or changed lies inside the owned paths (other agents' changes will also appear; leave them alone). Confirm you opened nothing in the excluded paths.

## Final message

Your final message, in plain text, gives: the deliverables with their paths; the number of towns located and the number flagged; per town, the number of Sentinel-2 scenes in its composite and whether Landsat was obtained; per town, the number of plans found and how many show a north arrow with a stated meaning; the selftest result; the runway validation numbers (per-runway residuals, overall mean and RMS, RMS by segment length, ratio of empirical residual to stated σ); the total size of the raw directory; every problem left unresolved; and a statement that the invariants held, or which did not.
