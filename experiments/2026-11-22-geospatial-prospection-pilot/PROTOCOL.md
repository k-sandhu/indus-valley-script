# Geospatial prospection pilot protocol (Issues 12 and 13)

Recorded on 22 November 2026 before acquiring additional Copernicus DEM GLO-30 tiles or executing pixel-level analyses. This protocol translates the proposed survey agenda in `papers/005-settlement-survey-gaps/manuscript.md` (Section 2.3, Section 8.3 and Appendix A) and `experiments/2026-10-11-settlement-prospection/PILOT-DESIGN-v4.md` into two reproducible digital terrain analyses over public 30 m elevation surfaces and already-held satellite control layers.

We separate buried-surface preservation stratification (Analysis A, Issue 13) from visible micro-relief screening (Analysis B, Issue 12). Thirty-metre digital surface models (Copernicus DEM GLO-30) capture ground elevation plus surface structures such as buildings and trees; neither 30 m terrain relief nor 10 m optical imagery can confirm archaeological authenticity, Harappan cultural affiliation or calendar chronology. All derived blocks, anomalies and control units are sampling frames and blind-testable leads for future geoarchaeological coring, optically stimulated luminescence (OSL) dating and ground survey by local heritage partners.

## 1. Study regions and elevation inputs

We reuse all locally held full 1-degree Copernicus DEM GLO-30 GeoTIFF tiles under `data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/` and `data/raw/2026-10-24-q1032-town-axis-register/dem/GLO-30/` (`N29_00_E074_00`, `N29_00_E075_00`, `N29_00_E076_00` and `N30_00_E072_00`), together with the held Sentinel-2 Level-2A composites and ESA WorldCover 2021 v200 land-cover control arrays for blocks B01 (Ganweriwala), B02 (Harappa) and B04 (Kalibangan) under `data/raw/2026-10-12-satellite-prospection/`.

To complete continuous 30 m coverage across regions P01 to P09, we acquire the remaining 10 missing 1-degree Copernicus DEM GLO-30 tiles from the public AWS Open Data bucket (`https://copernicus-dem-30m.s3.amazonaws.com/`) into local-only storage at `data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/` (physical path `D:\projects\indus_valley_script\data\raw\2026-11-22-geospatial-prospection-pilot\dem\30m\`):

- Cholistan and Ganweriwala margins (P01 and P02, clipped to the published Orengo et al. 2020 study-area polygon in `SPATIAL_CONCORDANCE_ORENGO_SOURCE_AOI.geojson`): `N27_00_E070_00`, `N27_00_E071_00`, `N28_00_E070_00`, `N28_00_E071_00` and `N29_00_E071_00`. (The Orengo polygon lies east of 71.0 degrees longitude north of 29.0 degrees latitude, so `N29_00_E070_00` is not required for P01 clipped to that footprint.)
- Harappa–Khanewal, Old Beas, Ganji Bar and East Multan–Tulamba shared frame (P08 and P09, union `[71.3, 29.8, 73.0, 30.9]`): `N29_00_E071_00`, `N29_00_E072_00` and `N30_00_E071_00`, paired with held `N30_00_E072_00`.
- Sirsa–Hanumangarh valley flanks (P06, `[74.0, 29.1, 75.2, 29.9]`): fully covered by held `N29_00_E074_00` and `N29_00_E075_00`.
- Haryana–Punjab mound corridors (P03 `[75.3, 29.3, 76.2, 30.0]`, P04 `[75.8, 29.8, 76.3, 30.5]`, P05 `[74.7, 29.8, 75.5, 30.4]` and overlapping P07 `[75.7, 29.1, 76.2, 29.6]`): `N30_00_E074_00`, `N30_00_E075_00` and `N30_00_E076_00`, paired with held `N29_00_E074_00`, `N29_00_E075_00` and `N29_00_E076_00`.

Every acquired tile records its exact URL, HTTP status, retrieval timestamp, byte count, SHA-256 hash, license notice and both repository-relative and physical D: paths in a local acquisition manifest and in `DATA-UPDATE.md`. All coordinate projections use exact WGS84 Transverse Mercator equations (equatorial radius 6,378,137.0 m, inverse flattening 298.257223563, scale factor 0.9996, false easting 500,000 m), verified to sub-millimetre agreement against the eight UTM Zone 43N core coordinates from Singh et al. (2017) in `SPATIAL_CONCORDANCE_SINGH_CORES_DERIVED.json`.

## 2. Analysis A: 24-block buried-surface preservation stratification (Issue 13)

Analysis A implements `PILOT-DESIGN-v4.md` quantitatively on two shared frames:

1. **Frame P08–P09 (Harappa–Khanewal, Old Beas, Ganji Bar and East Multan–Tulamba)**: union `[71.3, 29.8, 73.0, 30.9]`, projected on Transverse Mercator centered at 72.0 degrees east. Every 1 km² cell carries all applicable region labels (`P08`, `P09` or both) and enters the frame once.
2. **Frame P06 (Sirsa–Hanumangarh valley flanks)**: `[74.0, 29.1, 75.2, 29.9]`, projected on UTM Zone 43N (central meridian 75.0 degrees east), directly aligned with the Kalibangan–Pilibanga sediment-core transect of Singh et al. (2017).

Because Indian and Pakistani fieldwork operates under distinct heritage permits, we produce a complete 24-block pilot workload (six blocks per stratum, eight held out) for P08–P09 and a companion 24-block workload for P06 under identical rules.

### 2.1 Pixel-level geomorphic fields

Each frame is resampled from the 1-arcsecond Copernicus DEM mosaic onto a 30 m metric grid by bilinear interpolation (native support remains approximately 27 m east-west by 31 m north-south; resampling adds no new spatial resolution). At every 30 m pixel we compute:

- **Elevation** $z$ (metres above EGM2008 geoid).
- **Local slope** $s$ (degrees) from the 3 by 3 central-difference gradient.
- **Macro-scale Topographic Position Index ($\text{TPI}_{5\text{km}}$)**: elevation minus a Gaussian-smoothed surface with $\sigma = 5000\text{ m}$ (about 167 pixels). Positive values identify elevated Pleistocene interfluve bars (such as the Ganji Bar in P08–P09 and flanking uplands in P06); negative values identify incised valleys and alluvial floodplains (Giosan et al. 2012; Singh et al. 2017).
- **Height Above Local Channel Floor (HACF)**: elevation minus the local minimum elevation within a 7.5 km radius after applying a 3 by 3 median filter to suppress isolated single-pixel sinks. A 7.5 km search radius spans the half-width of the incised Ravi, Old Beas and Ghaggar–Hakra valleys so valley-floor pixels sit near 0 to 2.5 m while elevated upland bars stand 4 to 12 m above the nearest thalweg.
- **Micro-relief residual ($\text{TPI}_{240\text{m}}$)**: elevation smoothed with $\sigma = 30\text{ m}$ minus elevation smoothed with $\sigma = 240\text{ m}$. Its standard deviation inside each 1 km² cell measures surface roughness from modern urban fabric, dune fields or dissected scarps.

### 2.2 Cell aggregation, calibration exclusions and preservation strata

Each frame is partitioned into integer-aligned 1 km by 1 km cells (33 by 33 pixel centers inside each cell, retaining only cells with at least 95% valid DEM coverage). Before drawing inference blocks, we separate a known-context calibration pool: every cell whose centroid lies within 3.0 km of documented archaeological anchors (`Harappa` and `Tulamba` in P08–P09; `Kalibangan`, `Sothi`, `Karanpura` and the five Singh et al. 2017 core localities `GS-7`, `GS-10`, `GS-11`, `GS-13` and `GS-14` in P06) is tagged as `calibration_excluded` and removed from the inference draw, while remaining recorded in a separate calibration table.

Cells with extreme urban or dune surface roughness ($\text{std}(\text{TPI}_{240\text{m}}) > 2.0\text{ m}$ or median slope $> 2.5^\circ$) are tagged `excluded_high_relief_or_urban` so modern town centres and active dune ridges do not contaminate alluvial preservation strata. Remaining eligible 1 km² cells are assigned in strict priority order to four mutually exclusive strata:

1. **`S4_active_channel_scour` (active or recent channel scour belts)**: cell median $\text{HACF} < 2.5\text{ m}$ and cell median $\text{TPI}_{5\text{km}} \le -1.0\text{ m}$ (or at least 25% of cell pixels have $\text{HACF} < 1.5\text{ m}$ and $\text{TPI}_{5\text{km}} \le -1.0\text{ m}$). Highest probability of Holocene scour and truncation of target-age surfaces.
2. **`S1_older_upland_bar` (older upland bars and stable interfluve surfaces)**: cell median $\text{TPI}_{5\text{km}} \ge +1.25\text{ m}$ and cell median $\text{HACF} \ge 4.5\text{ m}$ and cell median slope $\le 1.5^\circ$. Stable Pleistocene alluvium (Ganji Bar and valley-flank interfluves) where target-age surfaces lie near the surface or under thin cover.
3. **`S2_covered_bar_margin` (covered bar margins and valley-flank transitions)**: transitional belt where elevated bars descend into incised valleys, defined either by $-1.0\text{ m} < \text{median } \text{TPI}_{5\text{km}} < +1.25\text{ m}$ with $\text{median HACF} \ge 2.5\text{ m}$, or by a within-cell scarp transition where the 10th percentile of $\text{TPI}_{5\text{km}}$ is $\le -0.5\text{ m}$ and the 90th percentile is $\ge +0.5\text{ m}$. Primary stratum for testing younger alluvial cover over older bar margins.
4. **`S3_young_alluvial_cover` (young alluvial cover and leveled floodplain benches)**: remaining low-lying, flat valley-fill cells ($\text{median } \text{TPI}_{5\text{km}} \le -0.5\text{ m}$ or $\text{median HACF} < 4.5\text{ m}$, not meeting S4 scour criteria). Represents aggraded floodplain alluvium and leveled agricultural ground where target-age horizons may be buried below shallow auger depth.

If any cell falls outside S1 to S4 under these rules (for example, an elevated plateau with low HACF below 4.5 m), it is labelled `unclassified_residual` and counted explicitly in the stratum audit table.

### 2.3 Cryptographic draw and 8-block holdout lock

For each frame (`P08_P09` and `P06`), we derive a deterministic 256-bit seed from:

`seed_hex = SHA256("indus_valley_script:2026-11-22:issue13:v1:" + frame_id)`

and initialize NumPy's `PCG64` generator with `int(seed_hex, 16)`. Within each of the four strata, we randomly permute eligible cells and select six pilot blocks plus three ranked backup replacements sequentially, enforcing a minimum centroid separation of 5.0 km between any two selected blocks (including backups) in the same stratum so correlated landform units are not duplicated.

To preserve spatial coherence in the held-out evaluation split (`PILOT-DESIGN-v4.md`: "Eight of the 24 sampled blocks, two per stratum, are held aside only for prediction-model evaluation; correlated landform units stay together"), we lock two of the six selected blocks per stratum (eight total per 24-block pilot) by selecting the geographically easternmost-or-westernmost holdout zone via a second deterministic hash `SHA256("indus_valley_script:2026-11-22:issue13:holdout:v1:" + frame_id)`. Specifically, we split each frame along its median easting into two halves, assign one half as the held-out evaluation zone (or pick the two blocks in each stratum closest to the holdout half so every stratum contributes exactly two held-out blocks while keeping held-out units geographically grouped), and record the exact SHA-256 commitment hash of the canonical JSON list of the eight locked holdout blocks.

## 3. Analysis B: Micro-relief calibration and anomaly screening (Issue 12)

Analysis B calibrates a multi-scale Copernicus GLO-30 micro-relief detector across documented archaeological mounds versus matched random negative 1 km² control cells, then generates a blind-testable candidate and negative-control field packet for P01–P02 and P03–P05.

### 3.1 Multi-scale micro-relief metrics

Across three 30 m metric mosaics covering (1) Cholistan and Ganweriwala (P01–P02, clipped to Orengo et al. 2020 AOI, TM centered at 71.0 degrees east), (2) Haryana–Punjab mound corridors (P03, P04, P05 and overlapping P07, UTM Zone 43N centered at 75.0 degrees east), plus the P06 and P08–P09 mosaics from Analysis A, we compute:

- Smooth elevation $z_1 = \text{Gaussian}(z, \sigma = 30\text{ m})$.
- Multi-scale Topographic Position Index residuals:
  - $\text{TPI}_{150} = z_1 - \text{Gaussian}(z, \sigma = 150\text{ m})$
  - $\text{TPI}_{300} = z_1 - \text{Gaussian}(z, \sigma = 300\text{ m})$
  - $\text{TPI}_{600} = z_1 - \text{Gaussian}(z, \sigma = 600\text{ m})$
  - $\text{TPI}_{\max} = \max(\text{TPI}_{150}, \text{TPI}_{300}, \text{TPI}_{600})$.
- Connected components of pixels with $\text{TPI}_{300} > 1.0\text{ m}$ (8-connectivity), computing footprint area (ha), peak $\text{TPI}_{300}$ (m), peak $\text{TPI}_{\max}$ (m), principal-axis ratio $\sqrt{\lambda_1 / \lambda_2}$, pixel-boundary compactness $4\pi A / P^2$, low-support expansion ratio (area at $\text{TPI}_{300} > 0.5\text{ m}$ divided by area at $\text{TPI}_{300} > 1.0\text{ m}$), and **annulus prominence** $P_{\text{ann}}$ (peak elevation minus median elevation inside a ring from $\max(180\text{ m}, r_{\text{eq}} + 90\text{ m})$ to $+300\text{ m}$ beyond the inner radius, where $r_{\text{eq}} = \sqrt{A/\pi}$).

### 3.2 Known-site calibration versus matched random negative controls

We assemble 12 documented archaeological coordinate records (11 distinct localities, preserving both conflicting Ganweriwala coordinates separately per `concordance-sources.json`) inside our 30 m tiles:

- P01–P02: Ganweriwala DOAM (28.598889 N, 71.150000 E) and Ganweriwala Gulzar and Wikidata (28.500000 N, 71.066667 E).
- P06: Kalibangan (29.473889 N, 74.129722 E), Sothi (29.125500 N, 74.726400 E) and Karanpura (29.108056 N, 75.097222 E).
- P03 and P07: Agroha Mound (29.333083 N, 75.620633 E), Banawali (29.598316 N, 75.392133 E), Bhirrana (29.554167 N, 75.565278 E), Kunal (29.500000 N, 75.683333 E) and Rakhigarhi (29.293733 N, 76.114683 E).
- P08–P09: Harappa (30.633333 N, 72.866667 E) and Tulamba (30.525486 N, 72.239767 E).

Because historical gazetteer coordinates can be offset by 100 to 500 m from a mound's summit (for example, the DOAM Ganweriwala point sits on the plain edge beside a prominent mound; see `outputs-terrain-v1/block-analysis.json`), we measure for every known site both the exact-point TPI and the maximum $\text{TPI}_{300}$, $\text{TPI}_{\max}$ and annulus prominence within a 500 m search disk (area 0.785 km²), recording the offset distance in metres.

For an area-matched negative comparison, we draw 50 random 1 km² control cells per corridor (200 total across P01–P02, P03–P05/P07, P06 and P08–P09), stratified by macro-landform ($\text{TPI}_{5\text{km}}$ quartiles) and excluding a 3.0 km buffer around all documented sites (5.0 km around both Ganweriwala reference points in P01–P02). Within each negative control cell we measure the exact same metrics both over the full 1 km² cell and over an area-matched 500 m radius central disk. We report Mann–Whitney U p-values, Cliff's delta, ROC AUC, and true-positive recall versus false-positive rate across predeclared thresholds ($\text{TPI}_{300} \ge 2.0, 3.0, 4.0\text{ m}$ and compact-mound shape filters: footprint area 0.5 to 40 ha, axis ratio $\le 3.5$, compactness $\ge 0.15$, low-support expansion ratio $\le 4.5$, annulus prominence $\ge 2.5\text{ m}$).

Where our candidate and calibration footprints overlap the held high-resolution Sentinel-2 and ESA WorldCover 2021 v200 arrays in blocks B01 (Ganweriwala), B02 (Harappa) and B04 (Kalibangan), we cross-check built-up land fraction (`WorldCover class 50`), cropland fraction (`class 40`) and dry-season optical NDVI to quantify false positives driven by modern villages, brick kilns and canal embankments.

### 3.3 Blind-testable candidate and negative-control field packet

From all compact micro-relief anomalies meeting the locked geometric filter outside the known-site exclusion buffers, we draw a size-stratified candidate sample for field follow-up:

- **P01–P02 (Cholistan inside Orengo AOI)**: up to 18 candidates stratified across small (0.5–5 ha), medium (5–20 ha) and large (>20 ha) footprints (targeting 6 per size class, ranked by geometric score $P_{\text{ann}} \sqrt{\text{compactness}} / \sqrt{\text{axis\_ratio}}$ with a minimum 2.0 km spacing between shortlisted peaks), paired with 18 landform-matched random negative 1 km² control cells (total 36 units).
- **P03–P05 (Haryana–Punjab mound corridors)**: up to 18 candidates stratified across corridors P03, P04 and P05 (6 per corridor across small, medium and large footprints, minimum 2.0 km spacing), paired with 18 landform-matched random negative 1 km² control cells (total 36 units).

All 72 field units are shuffled with a deterministic SHA-256 seed (`indus_valley_script:2026-11-22:issue12:blind:v1`) into a blind-testable GeoJSON and CSV table (`BLIND-001` through `BLIND-072`) that omits candidate versus negative status, paired with a separate keyed lookup table and SHA-256 hash. Every unit carries its region-specific demotion rule from Paper 005 Appendix A (reclassify individual natural dune, embankment or later-period mounds; demote excess-candidate claims if equal-effort blind checks show no phase-supported excess over negative controls).

## 4. Verification and deliverables

An independent verification script (`code/verify.py`) will verify:
1. All raw DEM tile SHA-256 hashes and GeoTIFF dimensions and tags.
2. Sub-millimetre Transverse Mercator projection round-trip accuracy against Singh et al. (2017) UTM 43N points.
3. Exact reproducibility of the 24-block draws, stratum counts, exclusion buffers, 5 km spacing constraints and 8-block holdout SHA-256 commitments.
4. Independent recomputation of synthetic Gaussian hill TPI invariance, known-site vs. negative-control ROC AUC, recall and false-positive counts, and blind-packet key integrity.

All scripts, outputs, figures, `REPORT.md`, `DATA-UPDATE.md` and `RETROSPECTIVE.md` reside strictly inside `experiments/2026-11-22-geospatial-prospection-pilot/`.
