# Open-data geospatial prospection pilot for buried alluvial surfaces and visible micro-relief (Issues 12 and 13)

## 1. Main results

Using 16 full 1-degree Copernicus DEM GLO-30 tiles (six reused from local storage and ten newly acquired into local bulk storage on D:) plus held Sentinel-2 Level-2A and ESA WorldCover 2021 v200 control rasters, we executed both predeclared terrain analyses from `PROTOCOL.md`.

In Analysis A (Issue 13), we classified 30,041 valid 1 km² alluvial cells across two shared frames into four preservation strata based on macro-scale Topographic Position Index (`TPI_5km`), Height Above Local Channel Floor (`HACF`), local slope and micro-relief roughness: 19,717 cells in the combined Harappa–Khanewal, Old Beas, Ganji Bar and East Multan–Tulamba frame (P08 and P09) and 10,324 cells in the Sirsa–Hanumangarh valley-flank frame (P06). Both frames recover the published regional geomorphology directly from 30 m elevation alone: Harappa, Tulamba and Kalibangan sit on elevated bar or valley-margin scarps (`S1` and `S2`, 4.1 to 7.8 m above the local channel floor), while the five Singh et al. (2017) sediment cores (`GS-7`, `GS-10`, `GS-11`, `GS-13`, `GS-14`) trace the exact cross-valley profile from northwest flank (`S2`) down into the incised palaeovalley fill (`S3`) and back up to Kalibangan (`S2`). Excluding 3 km buffers around all documented calibration anchors, we drew two cryptographically seeded 24-block pilot workloads (six blocks per stratum plus three ranked backups per stratum, with at least 5 km intra-stratum spacing) and locked eight spatially grouped held-out evaluation blocks in each frame (`SHA-256 = 8521d7367c9536a1440112493cf927f76665ea81be869cdc565b35b0e802781d` for P08 and P09; `SHA-256 = b8ce6e240db4ff7603cd8a546f4dd6bcd25cd5c96ab17c15c8a1a44eeb394a70` for P06).

In Analysis B (Issue 12), multi-scale 30 m micro-relief separates 12 documented archaeological coordinate records (11 distinct sites across P01 to P09) from 200 landform-matched random negative 1 km² control cells with statistically real but incomplete discrimination: multi-scale `TPI_max` inside a 500 m search disk reaches ROC AUC = 0.7221 (Cliff's delta = 0.4442, one-sided Mann–Whitney p = 0.00494), `TPI_300` reaches ROC AUC = 0.7096 (p = 0.00745) and annulus prominence reaches ROC AUC = 0.6850 (p = 0.01583). Prominent urban tells stand out sharply (Agroha Mound at 14.36 m `TPI_300`, Harappa at 9.37 m, Rakhigarhi at 7.23 m, Kalibangan at 7.11 m, Banawali at 5.04 m), whereas lower-relief rural or leveled settlements (Bhirrana at 1.77 m, Sothi at 1.83 m, Kunal at 1.91 m, Karanpura at 2.55 m) overlap heavily with background terrain noise. Cross-checking held ESA WorldCover 2021 v200 and Sentinel-2 layers explains why false positives remain high (21% to 48% across thresholds): on the cultivated Punjab plain around Harappa (block B02), 75.0% (63 of 84) of 2 m DEM rises contain at least 10% modern built-up cover, whereas around Ganweriwala in Cholistan (block B01) built-up contamination is 0.0% (0 of 66) and natural desert dunes supply the competing positive anomalies. We packaged 72 strictly unique blind-testable 1 km² field units (36 size-stratified compact-relief candidates and 36 landform-matched negative controls across P01, P02, P03, P04 and P05) with a concealed key locked at `SHA-256 = abbc468e5cb22a805194d161fb40d10ba9dd4a2de7109dd8f4bc4aec306b589d`.

An independent verification suite (`code/verify.py`) passed all five check groups (16 tile hashes and GeoTIFF headers, sub-millimetre WGS84 Transverse Mercator accuracy of 0.031 mm against `pyproj 3.8.0`, synthetic terrain invariance, Analysis A stratum and holdout integrity, and Analysis B statistical recomputation and blind-packet non-leakage).

## 2. Shared scope, definitions and data

Copernicus DEM GLO-30 is a digital surface model at 1 arcsecond posting (roughly 27 m east-west by 31 m north-south at 30 degrees north) that records ground elevation together with modern buildings, tree canopies and embankments. Resampling the mosaic bilinearly onto a 30 m Transverse Mercator grid aligns metric neighborhoods and integer 1 km² block boundaries without adding native spatial resolution. Terrain relief and 10 m optical reflectance describe surface geometry and land cover only; they establish neither archaeological origin, Harappan cultural affiliation nor calendar date. Every selected block and blind target therefore carries an explicit demotion rule tied to future coring, optically stimulated luminescence (OSL) dating or equal-effort ground survey by local heritage partners.

We define four recurring terrain quantities used throughout this report:

- **Topographic Position Index (`TPI`)** is local elevation minus a Gaussian-smoothed background elevation at a stated standard deviation $\sigma$. Positive `TPI_5km` ($\sigma = 5000\text{ m}$) marks elevated interfluve bars; negative `TPI_5km` marks incised valleys. Short-scale residuals (`TPI_150`, `TPI_300`, `TPI_600` and their pixelwise maximum `TPI_max`) isolate compact mound-sized rises after removing broad valley slope.
- **Height Above Local Channel Floor (`HACF`)** is pixel elevation minus the minimum terrain elevation within an equal-area 7.5 km neighborhood (computed after a 3 by 3 median filter to remove isolated pits). It estimates vertical relief above the nearest valley thalweg.
- **Annulus prominence** is peak elevation minus the median elevation inside a surrounding ring spanning from $\max(180\text{ m}, r_{\text{eq}} + 90\text{ m})$ out to 300 m beyond that inner radius, where $r_{\text{eq}}$ is the component's equal-area radius.
- **Cliff's delta** is the nonparametric effect size $2 \times \text{AUC} - 1$, ranging from $-1$ to $+1$, measuring how often a randomly chosen known site exceeds a randomly chosen negative control.

Full tile provenance, URLs, byte counts and SHA-256 hashes for all 16 Copernicus tiles appear in `outputs/dem_manifest.json` and `DATA-UPDATE.md`. Exact geographic bounds for regions P01 to P09 follow `papers/005-settlement-survey-gaps/manuscript.md` Appendix A, with P01 and P02 clipped to the published Orengo et al. (2020) study polygon (`SPATIAL_CONCORDANCE_ORENGO_SOURCE_AOI.geojson`).

## 3. Analysis A: Buried-surface preservation stratification and 24-block pilots

Both study frames exhibit the same four-part alluvial architecture predicted by Giosan et al. (2012) and Singh et al. (2017): narrow high-relief upland bars (`S1`, 6.2% to 6.4% of cells), broad transitional bar-margin slopes (`S2`, 65.1% to 76.0%), low-lying flat alluvial valley fills (`S3`, 14.7% to 18.0%) and narrow active or recent channel-floor scour belts (`S4`, 0.6% to 0.8%). In P06, the roughness exclusion filter (`std(TPI_240) > 2.0 m` or median slope `> 2.5 deg`) masks 902 cells (8.74%), cleanly removing the Thar Desert dune belt south of Kalibangan from the alluvial coring pool. In P08 and P09, 11,673 of the 19,717 cells lie inside the geographic overlap of the two editorial rectangles; each cell carries both labels and enters the sampling frame once.

| Frame | Valid 1 km² cells | S1 Older upland bar | S2 Covered bar margin | S3 Young alluvial cover | S4 Active channel scour | Calibration excluded (3 km) | High-relief or urban excluded | Unclassified residual |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P08 and P09 | 19,717 | 1,268 (6.43%) | 14,988 (76.02%) | 2,901 (14.71%) | 151 (0.77%) | 64 (0.32%) | 260 (1.32%) | 85 (0.43%) |
| P06 | 10,324 | 635 (6.15%) | 6,720 (65.09%) | 1,861 (18.03%) | 61 (0.59%) | 131 (1.27%) | 902 (8.74%) | 14 (0.14%) |

Checking where documented calibration anchors fall inside this automated classification confirms that the DEM strata track real archaeological and stratigraphic positions rather than arbitrary elevation quantiles:

| Anchor | Frame | Kind | Cell stratum | Median elevation (m) | Median `TPI_5km` (m) | Median `HACF` (m) |
|---|---|---|---|---:|---:|---:|
| Harappa (DOAM) | P08 and P09 | Archaeological site | `S1_older_upland_bar` | 164.69 | +1.672 | 7.598 |
| Harappa (Wikidata) | P08 and P09 | Archaeological site | `S2_covered_bar_margin` | 161.63 | -1.457 | 4.133 |
| Tulamba | P08 and P09 | Archaeological site | `S2_covered_bar_margin` | 145.61 | +0.593 | 7.602 |
| Kalibangan | P06 | Archaeological site | `S2_covered_bar_margin` | 179.44 | -0.002 | 7.752 |
| Sothi | P06 | Archaeological site | `S3_young_alluvial_cover` | 191.71 | -3.051 | 10.700 |
| Karanpura | P06 | Archaeological site | `S3_young_alluvial_cover` | 196.35 | -4.486 | 4.777 |
| Singh 2017 `GS-14` (NW flank) | P06 | Dated core | `S2_covered_bar_margin` | 177.88 | -0.332 | 6.195 |
| Singh 2017 `GS-13` (NW floor) | P06 | Dated core | `S3_young_alluvial_cover` | 177.32 | -1.220 | 5.629 |
| Singh 2017 `GS-7` (valley center) | P06 | Dated core | `S3_young_alluvial_cover` | 176.93 | -1.757 | 5.242 |
| Singh 2017 `GS-10` (valley axis) | P06 | Dated core | `S3_young_alluvial_cover` | 176.82 | -2.372 | 5.130 |
| Singh 2017 `GS-11` (SE flank) | P06 | Dated core | `S2_covered_bar_margin` | 180.50 | +1.030 | 8.816 |

The Singh et al. (2017) transect steps down from `S2` on the northwest valley margin (`GS-14`, 177.88 m) across the `S3` incised Ghaggar–Hakra valley fill (`GS-13`, `GS-7`, `GS-10`, bottoming at `TPI_5km = -2.372 m`) and back onto the `S2` southern flank beside Kalibangan (`GS-11`, 180.50 m). Meanwhile Sothi and Karanpura sit in `S3` valley-fill depressions south of the main Ghaggar channel, showing that target-age archaeology is not restricted to `S1` bars alone.

![Analysis A stratification and locked 24-block pilots](figures/analysis_a_stratification_maps.png)

In each frame, our deterministic draw (`code/analysis_a_preservation.py`) selected 24 primary pilot blocks (six per stratum, with 16 discovery blocks and 8 spatially grouped held-out evaluation blocks) plus 12 ranked backup replacements (three per stratum) in case local parcels prove inaccessible. Observed minimum intra-stratum separation exceeds the 5.0 km floor in both frames (19.03 km in P08 and P09; 7.07 km in P06), and every drawn block lies at least 5.42 km from all calibration anchors. Complete block geometries and attributes are saved in `outputs/analysis_a_p08_p09_pilot_blocks.{csv,geojson}`, `outputs/analysis_a_p06_pilot_blocks.{csv,geojson}` and `outputs/analysis_a_holdout_lock.json`.

| Frame | Draw seed SHA-256 (prefix) | Holdout side | Holdout blocks (8 locked) | Holdout commitment SHA-256 |
|---|---|---|---|---|
| P08 and P09 | `19c9bdb4ea820d03` | West half | `P08_P09-S1-03`, `S1-05`, `S2-05`, `S2-06`, `S3-01`, `S3-02`, `S4-03`, `S4-04` | `8521d7367c9536a1440112493cf927f76665ea81be869cdc565b35b0e802781d` |
| P06 | `7bc10e12cf2c6773` | East half | `P06-S1-01`, `S1-02`, `S2-01`, `S2-06`, `S3-04`, `S3-06`, `S4-01`, `S4-06` | `b8ce6e240db4ff7603cd8a546f4dd6bcd25cd5c96ab17c15c8a1a44eeb394a70` |

## 4. Analysis B: Micro-relief calibration, land-cover controls and blind field packet

Evaluating all 12 documented site records against 200 landform-matched random negative 1 km² cells (50 per corridor, stratified by `TPI_5km` quartiles and outside 3 km site exclusion buffers, or 5 km around both Ganweriwala coordinates) shows clear elevation excess at major tells alongside severe overlap with background relief at low-relief sites.

| Known site record | Corridor | Point `TPI_300` (m) | 500 m max `TPI_300` (m) | 500 m max `TPI_max` (m) | Annulus prominence (m) | Peak offset (m) | Compact mound pass |
|---|---|---:|---:|---:|---:|---:|:---:|
| Agroha Mound | P03 | +9.320 | 14.364 | 15.051 | 18.171 | 313.2 | Yes |
| Harappa | P08 | -4.030 | 9.368 | 10.674 | 11.686 | 468.6 | Yes |
| Rakhigarhi | P07 | +1.299 | 7.232 | 8.972 | 8.303 | 494.8 | Yes |
| Kalibangan | P06 | +3.225 | 7.105 | 8.122 | 9.558 | 94.9 | Yes |
| Banawali | P03 | +4.146 | 5.043 | 6.533 | 6.214 | 42.4 | Yes |
| Ganweriwala (DOAM) | P01 and P02 | -1.037 | 4.579 | 7.001 | 5.412 | 426.4 | No |
| Tulamba | P08 and P09 | +1.495 | 3.149 | 3.550 | 3.652 | 123.7 | Yes |
| Karanpura | P06 | -0.235 | 2.553 | 3.989 | 2.923 | 394.6 | No |
| Kunal | P03 | +0.070 | 1.914 | 2.132 | 3.480 | 450.0 | No |
| Sothi | P06 | -0.479 | 1.834 | 1.869 | 3.361 | 150.0 | Yes |
| Bhirrana | P03 | +0.500 | 1.772 | 2.416 | 2.134 | 189.7 | No |
| Ganweriwala (Gulzar) | P01 and P02 | -0.363 | 1.462 | 1.469 | 2.591 | 429.5 | Yes |

Two practical lessons emerge directly from this table. First, published gazetteer coordinates often miss the physical mound summit by 100 to 500 m: the Wikidata coordinate for Harappa falls in a low river-edge depression (`point TPI_300 = -4.030 m`) 469 m from the 9.37 m mound summit, and the DOAM Ganweriwala coordinate sits on flat ground (`-1.037 m`) 426 m from a 4.58 m rise, while the alternative Gulzar coordinate 13.7 km southwest shows only 1.46 m relief inside 500 m. Second, 30 m elevation separates the 12 site disks from the 200 matched negative disks (`TPI_max` median 4.77 m vs. 2.19 m, AUC = 0.7221, p = 0.00494; `TPI_300` median 3.86 m vs. 1.91 m, AUC = 0.7096, p = 0.00745), yet every threshold that recovers at least half of the known sites still fires on 20% to 51% of random background 500 m disks:

| Operating rule (500 m search disk) | Known-site recall (TP of 12) | Negative-control FPR (FP of 200) |
|---|---:|---:|
| `TPI_300 >= 2.0 m` | 8 of 12 (66.7%) | 96 of 200 (48.0%) |
| `TPI_300 >= 3.0 m` | 7 of 12 (58.3%) | 60 of 200 (30.0%) |
| `TPI_300 >= 4.0 m` | 6 of 12 (50.0%) | 42 of 200 (21.0%) |
| `TPI_max >= 3.5 m` | 8 of 12 (66.7%) | 55 of 200 (27.5%) |
| `TPI_max >= 5.0 m` | 6 of 12 (50.0%) | 40 of 200 (20.0%) |
| Annulus prominence `>= 3.0 m` | 9 of 12 (75.0%) | 102 of 200 (51.0%) |
| Compact-mound filter (0.5 to 40 ha, AR `<= 3.5`, C `>= 0.15`, exp `<= 4.5`, prom `>= 2.5 m`) | 8 of 12 (66.7%) | 74 of 200 (37.0%) |

The held ESA WorldCover 2021 v200 and Sentinel-2 cross-check (`outputs/analysis_b_summary.json`) diagnoses two distinct false-positive mechanisms across environments:

| Held control block | Environment | DEM peaks `>= 2.0 m` (`>= 0.54 ha`) | Modern built-up `>= 10%` | Cropland `>= 50%` | Bare non-built | Mean built fraction | Median peak NDVI |
|---|---|---:|---:|---:|---:|---:|---:|
| B01 (Ganweriwala, P01 and P02) | Cholistan desert | 66 | 0 (0.0%) | 0 | 66 | 0.000 | 0.133 |
| B02 (Harappa, P08) | Cultivated Punjab plain | 84 | 63 (75.0%) | 9 | 12 | 0.467 | 0.285 |
| B04 (Kalibangan, P06) | Valley and dune margin | 90 | 13 (14.4%) | 12 | 65 | 0.096 | 0.195 |

On the cultivated alluvial plain around Harappa, three-quarters of all 2 m DEM anomalies are modern villages, brick kilns and road or canal structures captured by the digital surface model. In Cholistan, modern built-up contamination drops to zero, leaving barchan and parabolic sand dunes as the primary non-archaeological mimic. Across the full corridors, our compact-mound filter extracts 8,274 compact rises in P01 and P02 (inside the Orengo polygon) and 6,937 in P03, P04, P05 and P07, confirming that 30 m DEM screening is a coarse pre-filter rather than a standalone mound detector: on cultivated plains it must be paired with ESA WorldCover built-up masking and historical Survey of India maps, and in Cholistan it must be paired with multitemporal spectral and radar soil-moisture indices.

![Analysis B calibration ROC and blind prospection packet](figures/analysis_b_calibration_and_candidates.png)

To enable an unbiased ground test of DEM micro-relief screening, we drew 36 size-stratified compact candidates outside all known-site exclusion buffers (18 inside P01 and P02 split evenly across small 0.5 to 5 ha, medium 5 to 20 ha and large 20 to 40 ha footprints; 18 across P03, P04 and P05, six per corridor) and paired them with 36 strictly unique landform-matched random negative 1 km² controls from the same corridors. All 72 units were cryptographically shuffled into `outputs/analysis_b_blind_field_packet.csv` and `outputs/analysis_b_blind_field_packet.geojson` (`BLIND-001` to `BLIND-072`), omitting candidate status and micro-relief scores while retaining each region's Appendix A demotion rule. The sealed key (`outputs/analysis_b_blind_key.csv` and `outputs/analysis_b_blind_key_lock.json`) is committed at `SHA-256 = abbc468e5cb22a805194d161fb40d10ba9dd4a2de7109dd8f4bc4aec306b589d`.

## 5. Boldest reading and deciding test

Our boldest supported reading is that the two regional survey gaps have fundamentally different physical causes that demand opposite field strategies: in the incised Punjab and Ghaggar–Hakra plains (P06, P08 and P09), most target-age settlement surfaces along bar margins and valley fills (`S2` and `S3`, accounting for 83% to 91% of eligible alluvial land) are concealed beneath young alluvium or masked by modern villages (75% of 2 m DEM rises in block B02), so surface relief alone misses rural settlements such as Bhirrana, Kunal and Sothi and only systematic stratigraphic coring can measure what survives; in Cholistan (P01 and P02), where modern built-up interference is zero, high-relief compact DEM anomalies inside the Orengo footprint still mix real unrecorded tells with natural dunes at roughly a 1-to-2 false-positive background rate unless filtered by multitemporal soil-moisture and radar signatures.

Two paired tests decide this reading directly. First, executing the locked 24-block coring and OSL pilots in P08–P09 and P06 (releasing the eight held-out blocks per frame only after locking the discovery-half preservation model) will establish whether `S2` covered bar margins and `S3` young alluvial fills actually preserve intact 2600–1900 BCE terrestrial horizons above or beneath Holocene scour; finding systematic truncation across adequate dated profiles in `S2` and `S3` demotes the buried-landscape premise for those units. Second, equal-effort blind ground checks of the 72 shuffled units in `analysis_b_blind_field_packet.geojson` (after adding a full-corridor ESA WorldCover built-up mask to pre-flag modern villages in P03 to P05) will measure exact positive predictive value by size class and corridor; if phase-supported archaeological recovery shows no excess in the 36 candidates over the 36 matched negative controls once the SHA-256 key is opened, pure 30 m micro-relief prospection is demoted as a standalone search filter.

## 6. Exact output and code links

- Protocol: `experiments/2026-11-22-geospatial-prospection-pilot/PROTOCOL.md`
- Data acquisition and storage record: `experiments/2026-11-22-geospatial-prospection-pilot/DATA-UPDATE.md`
- Retrospective: `experiments/2026-11-22-geospatial-prospection-pilot/RETROSPECTIVE.md`
- Code: `code/acquire_dem.py`, `code/geo_utils.py`, `code/analysis_a_preservation.py`, `code/analysis_b_microrelief.py`, `code/verify.py`
- Analysis A outputs: `outputs/dem_manifest.json`, `outputs/analysis_a_summary.json`, `outputs/analysis_a_holdout_lock.json`, `outputs/analysis_a_p08_p09_pilot_blocks.{csv,geojson}`, `outputs/analysis_a_p06_pilot_blocks.{csv,geojson}`, `figures/analysis_a_stratification_maps.png`
- Analysis B outputs: `outputs/analysis_b_summary.json`, `outputs/analysis_b_calibration_table.csv`, `outputs/analysis_b_blind_field_packet.{csv,geojson}`, `outputs/analysis_b_blind_key.csv`, `outputs/analysis_b_blind_key_lock.json`, `figures/analysis_b_calibration_and_candidates.png`
- Independent verification record: `outputs/verification.json` (5 of 5 checks passed)
