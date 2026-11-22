# Retrospective: Open-data geospatial prospection pilot (Issues 12 and 13)

Recorded on 22 November 2026 to document externally observable implementation choices, obstacles encountered, repairs made and verified outcomes for `experiments/2026-11-22-geospatial-prospection-pilot/`.

## 1. Environment and data reuse

Inspecting the active Python 3.13 environment showed `numpy`, `scipy`, `PIL`, `matplotlib`, `sklearn` and `requests` were installed, while compiled GDAL bindings (`rasterio`, `pyproj`, `shapely`, `geopandas`) were absent. Rather than adding third-party binary packages, we wrote a self-contained geospatial layer in `code/geo_utils.py` using Pillow for 32-bit float GeoTIFF reading and tag inspection, exact WGS84 Transverse Mercator ellipsoid equations (verified to 0.031 mm against the `pyproj 3.8.0` UTM Zone 43N core table in `SPATIAL_CONCORDANCE_SINGH_CORES_DERIVED.json`), and vectorized NumPy ray-casting for polygon clipping.

Before downloading any external raster, we inventoried `data/raw/2026-10-12-satellite-prospection/`, `data/raw/2026-10-21-town-orientations-verification/astro/dem/` and `data/raw/2026-10-24-q1032-town-axis-register/dem/`. Six full 30 m Copernicus DEM tiles (`N29_00_E073_00` through `N29_00_E076_00`, `N30_00_E072_00` and `N30_00_E073_00`) were already held locally and reused without copying. We downloaded only the ten missing 1-degree tiles (421.5 MB total) from public AWS Open Data into local bulk storage under `D:\projects\indus_valley_script\data\raw\2026-11-22-geospatial-prospection-pilot\dem\30m\` via the `data/raw` junction, recording full SHA-256 hashes and `.source.json` sidecars.

## 2. Obstacles encountered and repairs

1. **Slow 2D minimum filter in Height Above Local Channel Floor (`HACF`)**: The first version of `compute_hacf` applied a non-separable 125-by-125 pixel circular `scipy.ndimage.minimum_filter` on the 120 m downsampled grid, which stalled runtime. We replaced it with an exact $O(N)$ two-pass separable 1D `minimum_filter1d` over an equal-area square neighborhood ($\text{half-width} = R\sqrt{\pi}/2$, matching the area of a 7.5 km disk). Runtime dropped to seconds while preserving exact step-height recovery on synthetic valley-and-bar tests (`verify.py` error 0.0000 m).
2. **Minor legend overlap in Analysis A map**: Visual inspection of the first `figures/analysis_a_stratification_maps.png` showed the bottom legend slightly overlapping the horizontal Easting axis labels. Adjusting `tight_layout(rect=[0.0, 0.13, 1.0, 0.94])` and re-running `analysis_a_preservation.py` cleared the overlap while reproducing identical stratum counts and identical holdout SHA-256 hashes.
3. **Accidentally dropped `roc_auc` key in `analysis_b_summary.json`**: A dictionary comprehension excluding `"roc_"` array fields (`roc_fpr`, `roc_tpr`) inadvertently omitted the scalar `roc_auc` field from `analysis_b_summary.json`. We narrowed the filter to exclude only `("roc_fpr", "roc_tpr")` so every scalar metric is persisted directly in JSON.
4. **Shared-frame overlap duplicates in the Analysis B blind packet**: Manual inspection of `outputs/analysis_b_blind_key.csv` revealed that three negative control cells lying inside the geographic overlap of P03 and P04 (or P03 and P05) had been drawn twice when looping separately over P03, P04 and P05, yielding 69 unique coordinates out of 72 rows. This violated the single-frame non-duplication rule in `papers/005-settlement-survey-gaps/manuscript.md` Section 2.3. We repaired `analysis_b_microrelief.py` to track used negative-control coordinates across corridors, added an explicit unique-coordinate guard to `code/verify.py`, re-ran Analysis B cleanly, and confirmed 72 strictly unique coordinates (36 candidates and 36 matched negative controls) with all five independent verification checks passing.

## 3. Final verified state

- All code and tracked outputs live strictly inside `experiments/2026-11-22-geospatial-prospection-pilot/`.
- All raw acquired DEM tiles live strictly inside `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/` on drive D:.
- Independent verification (`code/verify.py`) passes 5 of 5 check groups and writes `outputs/verification.json`.
- Prose audit (`python tools/review_prose.py --path experiments/2026-11-22-geospatial-prospection-pilot --no-write`) verifies compliance with `knowledge/editorial/WRITING.md`.
