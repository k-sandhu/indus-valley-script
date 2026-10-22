# Measuring straight architectural features

We measure a line clockwise from true north, then fold its bearing to the nearest cardinal direction. The folded value is `theta_deg = ((bearing_deg + 45) % 90) - 45`; the endpoint -45 is mapped to +45, so the interval is (-45, +45]. Image columns increase to the right and rows increase downward. Integer image coordinates identify pixel centres. Endpoints are ordered: a plan arrow runs from its tail to its tip. Reversing an architectural line changes its bearing by 180 degrees and leaves its folded value unchanged.

Read `../MEASUREMENT-RULES.md` before choosing features. The tools refine the features you identify. They do not identify ancient architecture or decide which wall face belongs to a period. Record the publication and feature identification for every pick.

## Environment and output files

Run commands from the repository root. Set these PowerShell variables to shorten the examples:

```powershell
$py = 'data/raw/2026-10-21-town-orientations-verification/venv-infra/Scripts/python.exe'
$tool = 'experiments/2026-10-21-town-orientations-verification/tools'
```

Use `& $py -I` for every command that reads acquired files. Each program inserts only its trusted tools directory into the module path. Keep source PDFs and rasters unchanged. Renders and picks go in your own raw directory; your town records and summary go in your own measurement directory. JSON outputs and renders refuse an existing destination. Choose a new filename for a revision.

The source indexes are `../infra-v1/sites-located-v1.json`, `imagery-manifest-v1.json` and `plan-library-v1.json`. Coordinates in the first index are starting points. Locate the mounds yourself and record how. Check `../infra-v1/validation-v1/summary.json` for the validation status and empirical errors before measuring.

## 1. Render imagery

Select a composite path from the imagery manifest. Give latitude and longitude, a square crop width in metres and a display layer:

```powershell
& $py -I "$tool/render_image.py" <composite.tif> <my-raw/crop.png> --point <latitude> <longitude> --size 2000 --layer RGB --upsample 4 --grid 100
```

Layers are `RGB` (B04, B03, B02), `NIR` (B08, B04, B03), `SWIR` (B12, B11, B04) and `brightness` (the mean of B02, B03, B04 and B08). `--percentiles 2 98` sets the display stretch. `--edge` applies an unsharp mask to the display. Integer enlargement uses nearest-neighbour pixels. The display has a labelled UTM grid, a true-north arrow and a scale bar. The north arrow accounts for the difference between UTM grid north and true north.

The file `<crop.png>.json` records a 3 by 3 affine matrix, `pixel_to_utm`, the EPSG code, the source path and SHA-256, and the display settings. Do not resize or crop the PNG after rendering. The measurement tool reads the original raster, so the stretch, grid and display enhancement do not enter the line fit.

## 2. Render a plan

Select a library entry and inspect its north evidence and scale. PDF page numbers are one-based. A PDF region is `[left, top, right, bottom]` in unrotated MuPDF page points, with 72 points per inch. Image regions use source pixels.

```powershell
& $py -I "$tool/render_plan.py" <source.pdf> <my-raw/plan.png> --page 12 --dpi 300 --grid 200
& $py -I "$tool/render_plan.py" <source.pdf> <my-raw/plan-detail.png> --page 12 --dpi 300 --region 30 40 540 700 --grid 100
```

The labelled grid gives PNG pixel coordinates. The sidecar records the source hash, page, resolution, region and `pixel_to_source` matrix. PDFs with a nonzero page-rotation flag are rejected because silently mixing rotated page coordinates would make picks ambiguous. Export that page to an unrotated source image and record the transformation before using it. A scanned picture rotated within a PDF page is supported.

## 3. Pick and refine lines

Create a picks JSON. Corridor widths and manual pick uncertainties use pixels in the rendered PNG, including any enlargement. A corridor should contain one identifiable feature. Choose `edge` for a brightness boundary, `ridge` for a bright centre and `trough` for a dark centre. A line can use `mode: "manual"` when a profile fit is unsuitable; supply a positive one-standard-deviation `pick_sigma_px` for each endpoint.

```json
{
  "source_id": "imagery",
  "band": 7,
  "lines": [
    {
      "id": "wall-01",
      "part": "named excavation area",
      "kind": "wall",
      "identification": "Publication, figure and explanation of the identified wall face",
      "system": "system-1",
      "endpoints_px": [[120, 530], [152, 180]],
      "corridor_half_width_px": 12,
      "feature": "edge",
      "mode": "fit"
    }
  ]
}
```

`band` is a one-based raster band number. Composites use B02, B03, B04, B08, B11, B12 and brightness in that order. Scene windows contain only the first six; choose a band explicitly when measuring a scene. A single-band raster uses band 1.

```powershell
& $py -I "$tool/measure_lines.py" <my-picks.json> <my-raw/crop.png.json> <my-lines.json>
```

The fit samples perpendicular profiles in native source pixels. It smooths each profile over one native pixel, finds the strongest gradient or brightness extremum within the corridor, and interpolates the peak between samples. Deterministic RANSAC finds a consensus; total least squares refines it. Profiles are spaced about three native pixels apart where the length permits. The output includes refined PNG and native endpoints, profile and inlier counts, perpendicular residual RMS, length and angular error. Inspect fits with low inlier counts or peaks near a corridor boundary. A failed fit needs revised picks, a documented manual measurement or an unmeasurable reason.

For imagery, the tool transforms the fitted ends to WGS84 and uses the circular mean of the forward geodesic azimuth and the backward azimuth minus 180 degrees. This returns true bearings even away from a UTM central meridian.

### Plans: north arrow and scale picks

A plan picks file adds `north` and `scale`:

```json
{
  "source_id": "plan-01",
  "north": {
    "class": "true",
    "evidence": "Exact north label and its location, or report citation and page",
    "survey_year": null,
    "line": {
      "endpoints_px": [[800, 320], [800, 120]],
      "feature": "trough",
      "corridor_half_width_px": 5,
      "mode": "manual",
      "pick_sigma_px": 1
    }
  },
  "scale": {"endpoints_px": [[100, 900], [500, 900]], "length_m": 100},
  "lines": []
}
```

Copy architectural lines into `lines` using the imagery example's fields. Pick the straight arrow shaft and exclude a broad arrowhead from a fitted shaft segment. A manual arrow pick can use the actual tail and tip. Scale picks identify two marks whose separation is known; they need not span the whole bar.

North classes are `true`, `magnetic`, `grid` and `unspecified`. An arrow marked only `N` is unspecified. A magnetic needle symbol is magnetic. Keep the evidence for that classification. For a magnetic arrow with a survey year of at least 1900, add `location: [latitude, longitude]` and `igrf_coefficients: "data/raw/2026-10-21-town-orientations-verification/infra/igrf/igrf14coeffs.txt"`. The tool accepts IGRF-14 years through 2030. It adds east-positive declination to the raw relative bearing and keeps `bearing_raw_deg`, `declination_deg` and `bearing_deg`. Missing prerequisites leave the correction unresolved. A grid or unspecified arrow also leaves the true reference unresolved; its relative bearing remains available with that status.

For each plan line, the arrow's angular error is added in quadrature to the line's error. Lengths use the two scale picks. Scale-pick error and paper deformation are not part of the angular fit error.

## 4. Register a plan, when suitable controls exist

Pick at least two corresponding points, preferably three or more separated across the plan. UTM coordinates come from the imagery sidecar, not a commercial map. Supply one common EPSG code:

```json
{
  "epsg": 32642,
  "control_sigma_m": 10,
  "controls": [
    {"plan_px": [100, 200], "utm": [600000, 3000000]},
    {"plan_px": [800, 700], "utm": [600700, 2999500]},
    {"plan_px": [500, 100], "utm": [600400, 3000100]}
  ]
}
```

```powershell
& $py -I "$tool/register_plan.py" <controls.json> <registration.json>
```

The similarity has a uniform scale, rotation and translation, accounting for downward plan rows. The output reports metric residuals, covariance error, leave-one-out rotations and a jackknife rotation error, and true north as a unit vector in plan pixels. Rotation is positive counterclockwise in a conventional x-right, y-up frame. Two controls fit exactly and provide no residual estimate of error; without `control_sigma_m` their rotation error is null. Registration is a separate observation and does not silently replace the measured north arrow.

## 5. Group systems and write a town record

Use one source ID for the imagery and a separate source ID for each plan source. Give every line a system label and a named town part. Copy line results into a town input file, retaining all refinement fields. The required town schema is:

```json
{
  "schema_version": 1,
  "slug": "town-slug",
  "measurer": "A or B",
  "located_point": {"latitude": 0, "longitude": 0, "method": "How we located the mounds"},
  "sources": [
    {"id": "imagery", "kind": "imagery", "scene_ids": [], "scene_datetimes": [], "manifest_path": "..."},
    {"id": "plan-01", "kind": "plan", "citation": "...", "pdf_page": 1, "printed_page": "...", "figure": "...", "north_class": "unspecified", "north_evidence": "...", "survey_year": null}
  ],
  "lines": [],
  "registrations": [],
  "notes": "Judgements and any preferred alternative system",
  "unmeasurable_reason": null
}
```

Each line requires `source_id`, `id`, `part`, `kind`, `identification`, `system`, picked `endpoints_px`, `length_m`, `bearing_deg`, `theta_deg` and `sigma_deg`. Include `endpoints_utm` and `epsg` for imagery or `endpoints_plan_m` for plans so the distance check is possible. Keep each plan's north record and the full measured arrow result in its source entry or in the linked measurement result. A town with no lines still gets a file and a concrete `unmeasurable_reason`.

```powershell
& $py -I "$tool/systems.py" <town-input.json> <my-measurement/towns/town-slug.json> --summary <my-measurement/summary.csv>
```

For each system the tool checks that every line has another system line within 200 m, using shortest segment distances, and that the numeric folded deviations span at most 6 degrees. It also reports disconnected neighbour groups and mixed town parts for review. A singleton fails the neighbour condition. Systems are never combined across sources.

For lengths L, deviations theta and line errors sigma, the system mean is `sum(L * theta) / sum(L)`. The weighted standard deviation is the population quantity `sqrt(sum(L * (theta - mean)^2) / sum(L))`. The standard error is the largest of that standard deviation divided by sqrt(n), `sqrt(sum(L^2 * sigma^2)) / sum(L)`, and 0.3 degrees. These are the measurement rules' formulas. A shared arrow error can correlate plan lines; the formula is retained exactly and its assumptions should be considered when interpreting a source.

The main system within each source has the greatest total length, with line count breaking a length tie. An exact remaining tie is reported and resolved by lexical system ID for a reproducible output. The main system is retained even when its conditions have warnings. A preferred alternative and its reason belong in `notes`.

The town output adds `systems` (line IDs, n, total length, weighted deviation, three error terms and warnings) and `main_system_by_source`. The CSV has one row per source's main system, or one row for an unmeasurable town. Its columns are `schema_version,town,source_id,main_system,n,total_length_m,theta_deg,se_deg,conditions_pass,unmeasurable_reason`. Appending a town already in the CSV is rejected.

## Error and validation scope

`sigma_fit_deg` is the line-direction error conditional on the selected feature and inlier set. The tool limits the independent profile count to length divided by three source pixels. `sigma_deg` also has a floor equivalent to two independent endpoint errors of 0.1 native pixel; manual mode uses the stated endpoint uncertainty. `residual_rms_px` describes perpendicular scatter in native source pixels. It is not an error in metres or degrees. Plan `sigma_deg` includes the measured arrow error. No tool error covers a misidentified feature, a wrong north class, survey error, paper distortion or scene registration bias.

Empirical precision, rejection counts and the ratio between residuals and stated errors are recorded in `../infra-v1/validation-v1/summary.json`. Treat a small conditional fit error cautiously when those reference tests show larger residuals. Preserve the stated sigma in the town record. Do not shrink it or substitute an empirical multiplier without recording a separate field and explanation.

To repeat the synthetic checks, choose fresh output and work paths:

```powershell
& $py -I "$tool/selftest.py" --output <new-selftest.json> --work <new-raw-work-directory> --coefficients data/raw/2026-10-21-town-orientations-verification/infra/igrf/igrf14coeffs.txt
```

The selftest identifies its simulated inputs, seed, code hashes, checks and overall pass flag. It refuses to overwrite either an existing output or a working directory. The IGRF reference comparison is run by `reference_checks.py`; `runway_validation.py` acquires and measures modern runway edges with automatic reference-based picks. Those programs are infrastructure validation tools.


## Completed infrastructure validation, 21 October 2026

The source indexes are in `../infra-v1/sites-located-v1.json`, `../infra-v1/imagery-manifest-v1.json` and `../infra-v1/plan-library-v1.json`. The plan library gives one-based PDF pages and printed pages. It stores no page renders; render the listed page and select its indicated figure or panel. Read `../infra-v1/coordinate-source-review-resume-v2.json` for the conflicting Gola Dhoro longitudes before locating that mound.

`../infra-v1/selftest-v1.json` passed all 28 checks on 1,620 synthetic imagery cases, rotated plan arrows, magnetic correction, system formulas and similarity registration. All profile fits returned results. Working files occupied 657,594 bytes and were deleted after the run. The final checks retain the original RMS thresholds. Two implementation repairs increased the minimum number of candidate profiles on short segments to twelve while keeping the cap on independent samples, and centred control coordinates before fitting a similarity.

`../infra-v1/validation-v1/summary.json` and its README report 14 full runway edges and 662 segment fits with no fitting failures. Across seven runways, the mean signed residual is -0.041015 degrees and RMS is 0.137144 degrees. Segment RMS is 4.272758, 1.764927, 0.988215 and 0.746483 degrees for 100, 200, 300 and 400 m. The overall RMS of residual divided by stated sigma is 1.492410. The three runways with precise reference coordinates give a full-runway RMS of 0.020421 degrees and a segment ratio of 1.292660. Four other references carry coordinate-precision flags. Hisar has an official resolved reference but no held imagery and contributes no fit.

`../infra-v1/igrf-validation-v1.json` compares the three BGS reference cases; all pass, with a maximum absolute discrepancy of 0.000315 degrees. The coefficient source and hash are in `../infra-v1/igrf-coefficients-source.json`.

The conditional fit errors are smaller than observed residuals on average, especially for short features. Preserve the tool's sigma and use the validation as a separate calibration record. A long runway's RMS does not describe the precision of a 100 m feature.

For held-imagery validation without any acquisition, use:

```powershell
& $py -I "$tool/runway_validation.py" experiments/2026-10-21-town-orientations-verification/infra-v1/sites-located-v1.json data/raw/2026-10-21-town-orientations-verification/infra <new-summary.json> --official-references experiments/2026-10-21-town-orientations-verification/infra-v1/official-runway-references-v2.json --imagery-manifest experiments/2026-10-21-town-orientations-verification/infra-v1/imagery-manifest-v1.json --work <new-raw-runway-work-directory>
```

Give `--work` a fresh owned raw directory for automatic-pick outputs on a repeat; source imagery stays in the held raw directory. JSON outputs refuse an existing destination. `../infra-v1/storage-verification-v1.json` and `../infra-v1/recompression-v1.json` preserve the original raster audit and replacement hashes. All retained first-run TIFF bands were checked against their original pixel hashes after DEFLATE compression with horizontal predictor 2. Acquisition requires 1.5 GB free at its start, stops below 1.2 GB, and reserves 250 MB for disk writes.


The final coverage is 33 located towns with eight coordinate flags, 193 Sentinel-2 scenes in 33 composites, and 26 indexed plans for 18 towns. Landsat was not obtained. `../infra-v1/coverage-v1.csv` gives every town's counts. The canonical imagery manifest includes the three earlier offline composites as archived records. `../infra-v1/verification-v1.json` records 575 manifest-file checks and full reads of all 557 retained TIFFs. `../infra-v1/asset-inventory-v1.json`, `../infra-v1/source-inventory-v1.json`, `../infra-v1/deletions-v1.csv` and `../infra-v1/RUN-NOTES.md` give the final inventories and source limits.

Use `../infra-v1/imagery-manifest-v1.json` for current source records. Fifty-two legacy raster capture times are explicitly unavailable and 45 old STAC response times are approximate; their satellite observation timestamps are known. `../infra-v1/provenance-reconciliation-v1.json` records these metadata limits. For scene validity use the SCL records and acquisition checks; a zero scaled reflectance can be valid.
