# Audit of the second exploratory terrain screen

The terrain run retained 852 connected relative-height supports and selected 24 for visual review across four acquired blocks. It was introduced after the first colour detector's panels were inspected and rejected for contemporary fields, ridges, settlements and channel banks. This is a separate exploratory method. Its parameters were saved at 05:33:09 UTC on 12 October 2026 before extraction; the run completed at 05:35:29. The original colour code, inputs and outputs remain preserved.

[Parameters](../outputs-terrain-v1/parameters.json), [complete supports](../outputs-terrain-v1/all-terrain-supports.geojson), [review polygons](../outputs-terrain-v1/review-targets.geojson), [review table](../outputs-terrain-v1/review-targets.csv) and [block/context records](../outputs-terrain-v1/block-analysis.json) preserve the results. The program's 74 implementation checks pass. A separate [inspection capsule](../outputs-terrain-v1/inspection-checks.json) records ten passing post-run checks.

## Measurements and selection

The existing processed arrays contain a 30 m metric grid warped from approximately 1 arcsecond Copernicus DSM. The screen applies a one-cell Gaussian smoothing and subtracts an eight-cell, 240 m Gaussian background. Supports are eight-connected cells above a 1 m residual; six cells give the smallest retained area, 0.54 hectares. Peak residual and peak elevation above a surrounding-ring median must reach 2 m. Areas above 30 hectares, elongated or irregular supports, connection to an extensive lower-threshold height support, insufficient surrounding coverage and block-edge context receive explicit flags. The geometric rank is ring prominence multiplied by the square root of perimeter compactness and divided by the square root of axis ratio.

The surrounding ring begins beyond the support's equivalent radius plus 90 m, with a minimum inner radius of 180 m, and extends another 300 m. The reported prominence is a DSM peak minus that ring's elevation median. It differs from both the smoothed high-pass peak and a polygon-median contrast. The area is the detector's threshold support on 30 m cells. These definitions are stored with every support.

Five unsigned WorldCover 2021 v200 windows supply built, crop, tree and water fractions. Two source tiles meet in the Kutch block; they are mosaicked on their geographic grid before binary classes are averaged onto the DSM grid. This prevents separately normalized tile averages from double-counting seam cells. Built fraction above 10%, proximity within 60 m to substantially built cells, water fraction above 10% and incomplete coverage screen review eligibility. Cropland is a descriptor and rival-control stratum, so a cropped location can remain eligible for inspection. Each block has an upper review budget of six, with 500 m separation between selected peaks.

| Block | Retained supports | Passing the rules | Selected for review |
|---|---:|---:|---:|
| B01 Ganweriwala reference surroundings | 207 | 16 | 6 |
| B02 Harappa countryside | 208 | 13 | 6 |
| B03 western Kutch catchment | 211 | 63 | 6 |
| B04 Kalibangan–Pilibanga | 226 | 42 | 6 |
| Total | 852 | 134 | 24 |

B01's WorldCover cropland fraction is approximately 0.15%, whereas the coordinator's contemporary optical inspection identified agricultural patterns among first-detector targets. The older classification cannot replace current image review. Compact natural hills can also pass the height rules: B03's leading support has 49.79 m peak-minus-ring prominence. Its numerical rank does not settle the formation process.

## Reference evidence and rival controls

The input supplies source-linked reference points rather than authenticated site-footprint polygons. Eight point records preserve existing census coordinates and the four block selection references. Two reference pairs coincide almost exactly, and the Kalibangan block-selection point differs from the finer prior census point. Every record reports 200 m, 500 m and 1,000 m context windows, nearby supports and land-cover fractions. These windows are sampling descriptions. They do not replace archaeological site boundaries.

The strongest B04 support, B04-T0136 at 74.130979 E, 29.474253 N, has an 11.70-hectare support and 9.42 m peak-minus-ring prominence. Its peak is 167 m from the existing Kalibangan census reference. It should enter the known-site/context comparison before any unmatched interpretation. Harappa's nearest retained support is B02-T0197, 250 m from its point; it is preserved with its screening flags. Ganweriwala's nearest support lies approximately 1.07 km from the selected point, which leaves the footprint/identity concordance unresolved in this measurement alone.

The block records contain 32 points drawn with a fixed seed and 18 selected built-land, cropland or extensive-height rival examples. Some rival examples overlap review targets because their purpose is to expose alternative explanations rather than supply confirmed archaeological absence. Four-date panels accompany the 24 selected features and additional rival examples. The coordinator owns final visual and contextual classifications.

## Preservation and practical limits

All 852 geographic polygons are valid, cover their recorded peaks and reproduce their cell-based metric area within the inspection tolerance. All 47 manifest-listed outputs match their hashes, as do the code, input arrays and earlier colour endpoints. Five acquired WorldCover clips and four local derived arrays remain in ignored files prefixed `SPATIAL_CONTROL_`. The output manifest carries the Sentinel, WorldCover and Copernicus DSM notices.

The DSM is a surface model with acquisition dates and vertical errors documented in the data-methods audit; buildings, vegetation, natural slopes and edited terrain affect these descriptors. The 2 m screen threshold is an exploratory geometry choice, with no calibrated local false-positive rate. Threshold supports do not date occupation or supply settlement areas. The scene panels use raw-reflectance display clips without a second SCL-mask application, while optical values remain outside the rank. The coordinator's clean renderer and multi-season inspection make the final optical-quality decisions.

The installed Shapely release emitted deprecation warnings for its older transform interface. The computations completed and their geometry checks passed. A replay can suppress these console warnings with `-W ignore::DeprecationWarning` while preserving the numerical method. Existing output directories are refused; any replay or parameter refinement needs a new endpoint. The original manifest remains unchanged, and the separate inspection capsule records this later audit.
