# Protocol: georeferencing buried Indus urban footprints beneath Harappa, Lakhanjo-Daro and Rupnagar

Status: frozen before spatial data acquisition, control-point registration and layer generation.
Date: 2026-11-23.
Scope: GitHub Issue #14, living-town archaeological footprint mapping and non-invasive survey prioritization.

## 1. Research objective and target settlements

We map the spatial relationship between documented Indus-period archaeological deposits and overlying modern settlements at three living towns:

1. **Harappa** (Sahiwal District, Punjab, Pakistan; approximate centre 30.630°N, 72.864°E). Kenoyer (1991, printed p. 57) states that modern Harappa town covers approximately one quarter of the total area of the ancient site.
2. **Lakhanjo-Daro** (Sindh Industrial and Trading Estate, Sukkur, Upper Sindh, Pakistan; approximate centre 27.724°N, 68.847°E). Published accounts (ul-Haq and Ali 2001: 29, quoted in Biagi and Vidale 2022: 5; Directorate of Antiquities, Government of Sindh 2022) describe mounds originally covering nearly 50 hectares across the industrial estate, now cut by factory plots, roads and utility trenches, with surviving lower Mature Harappan and craft-production contexts beneath disturbed upper strata.
3. **Rupnagar**, also published as Ropar or Rupar (Rupnagar District, Punjab, India; published ASI coordinate 30.9664°N, 76.5331°E). The Archaeological Survey of India report for 2011–2012 (Prabhakar, *Indian Archaeology 2011–2012 – A Review*, pp. 72–76) describes four mounds spanning roughly 12 hectares on the left bank of the Sutlej, with Nalagarh Kothi on the main elevation, the southern mound densely covered by modern Rupnagar, and a six-fold cultural sequence that the ASI Chandigarh Circle site card (item 146, p. 163) splits across a break between Period I (2000–1400 BCE) and Painted Grey Ware (1000–700 BCE).

Our goal is to produce audited, versioned GeoJSON polygons and priority tables separating documented archaeological areas, modern built-up and street footprints, concealed overlap zones, and prioritized open parcels and rescue-section corridors suitable for non-invasive geophysical survey or municipal trench watching.

## 2. Coordinate reference systems and metric accuracy rules

All tracked GeoJSON outputs use WGS 84 geographic coordinates (EPSG:4326, longitude first, latitude second, following RFC 7946). Every area, distance, buffer, topographic slope and registration fit is computed in a site-specific WGS 84 Universal Transverse Mercator (UTM) projection using exact Snyder/USGS Transverse Mercator formulas:

- **Harappa**: UTM Zone 43N (EPSG:32643; central meridian 75°E, scale factor 0.9996, false easting 500,000 m).
- **Lakhanjo-Daro (Sukkur)**: UTM Zone 42N (EPSG:32642; central meridian 69°E, scale factor 0.9996, false easting 500,000 m).
- **Rupnagar (Ropar)**: UTM Zone 43N (EPSG:32643; central meridian 75°E, scale factor 0.9996, false easting 500,000 m).

An independent verification script checks forward and inverse projection closure to better than 1 mm across every vertex, confirms valid simple polygon rings with counter-clockwise exterior winding and no self-intersections, and recomputes every reported area independently by planar shoelace integration in UTM metres and spherical excess on the WGS 84 authalic sphere.

## 3. Data sources and local storage policy

We inspect held repository inputs first and acquire only open, public geospatial datasets into the local bulk storage path `data/raw/2026-11-23-living-towns-footprints/` (physical path `D:\projects\indus_valley_script\data\raw\2026-11-23-living-towns-footprints\`). Every local and newly acquired input is recorded with its SHA-256 hash, byte size, logical path and physical path.

- **Held primary archaeological texts and plans**:
  - Harappa: Wheeler (1947), *Ancient India* 3, Plate XV (`data/raw/2026-10-21-town-axes/plan-B/renders/wheeler47_p0004_100dpi.png`) and its two audited control-point sets (`experiments/2026-10-21-plan-registration/control-R1/harappa__wheeler1947-pl15.json` and `control-R2/harappa__wheeler1947-pl15.json`); Kenoyer (1991), "Urban Process in the Indus Tradition: A Preliminary Model from Harappa", Figure 4.2 (`data/raw/2026-10-21-town-axes/dating/harappa/kenoyer1991urban.pdf`); Kenoyer (2008), "Indus Urbanism: New Perspectives on its Origin and Character", Figure 3 (`data/raw/2026-10-21-town-axes/dating/harappa/kenoyer2008urbanism.pdf`).
  - Lakhanjo-Daro: Biagi and Vidale (2022), *Asian Perspectives* 61(1), Figure 3 (`data/raw/2026-10-21-town-axes/dating/lakhanjo-daro/biagi2022lakhan.pdf`); Directorate of Antiquities, Government of Sindh (2022), "Lakhian jo Daro, SITE, Sukkur" (`data/raw/2026-10-11-settlement-prospection/SINDH2022.html`); Shar and Shah (2022), *Kalich Research Journal* 8 (`data/raw/2026-10-21-town-axes/dating/lakhanjo-daro/kalich2022lakhan.pdf`); site gazetteer (`experiments/2026-11-22-site-survey-gazetteer/gazetteer-v1.json`).
  - Rupnagar: Prabhakar (2015), "22. Excavation at Rupnagar, District Rupnagar", *Indian Archaeology 2011–2012 – A Review*, pp. 72–79 (`data/raw/2026-10-21-post-catalogue-finds/run1b/sources/iar-2011-12/iar-2011-12.pdf`); ASI Chandigarh Circle site card record (`experiments/2026-10-26-indus-living-atlas/living-towns/sources.json`, LT-S13); Rupnagar District Administration Archaeological Museum notice (`data/raw/2026-10-11-settlement-prospection/ANCHOR_ROPAR.html`).
- **Held terrain and land-cover rasters**:
  - Copernicus GLO-30 30 m DEM tiles: `N30_00_E072_00` (Harappa), `N27_00_E068_00` (Lakhanjo-Daro) and `N30_00_E076_00` (Rupnagar).
  - ESA WorldCover 2021 v200 (10 m, CC BY 4.0) for Harappa (`data/raw/2026-10-12-satellite-prospection/SPATIAL_CONTROL_20261012T053309958546Z_B02_WorldCover_N30E072.tif`).
  - Esri World Imagery mosaics for Harappa (zoom 16 and zoom 18 under `data/raw/2026-10-21-plan-registration/` and `data/raw/2026-10-21-town-axes/`).
- **Newly acquired open public geospatial layers** (stored locally only):
  - ESA WorldCover 2021 v200 10 m clipped windows for Lakhanjo-Daro (`N27E066` tile on AWS S3) and Rupnagar (`N30E075` tile on AWS S3).
  - Esri World Imagery zoom 17 and zoom 18 mosaics for Lakhanjo-Daro (Sukkur SITE) and Rupnagar (Ropar) for control-point picking and visual verification of open parcels and streets.
  - OpenStreetMap (Overpass API, ODbL) road, building, industrial, park and water geometries within each site's 2.4 km analysis box to support modern street-corridor delineation and cross-check WorldCover built-up masks.

## 4. Control-point registration and residual-error rules

We never fabricate trench coordinates, wall lines or excavation outlines that are not directly supported by a named published plan, coordinate or excavation datum. Where a published site extent has no scaled outline map, we encode it as an explicit bounded envelope with a stated positional uncertainty buffer rather than inventing precise sub-mound polygons.

### 4.1 Similarity registration model

Published plans and annotated satellite figures are registered to WGS 84 / UTM ground coordinates through a four-parameter planar similarity transform (isotropic scale $s$, rotation $\theta$, translation $t_x, t_y$) fitted by weighted least squares:

$$
Q_i = s \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix} P_i + \begin{pmatrix} t_x \\ t_y \end{pmatrix}
$$

Control points are weighted by inverse variance $w_i = 1 / \sigma_i^2$, where Class A sharp permanent features (conserved brick wall corners, road-centre intersections, permanent building corners) carry $\sigma_A = 3.0\text{ m}$ and Class B schematic or broad landmarks (walled excavation enclosures, drawn monument centres, generalized road bends) carry $\sigma_B = 6.0\text{ m}$.

Every registration must satisfy five acceptance criteria:

1. **Minimum redundancy**: at least $N \ge 5$ spatially distributed control points (giving at least 6 degrees of freedom), with target singular-value ratio $\sigma_{\min}/\sigma_{\max} \ge 0.15$ so points are not collinear.
2. **Planar RMSE bound**: root-mean-square residual across all control points $\text{RMSE} \le 12.0\text{ m}$ for archaeological site plans (Kenoyer 1991/2008, Wheeler 1947) and $\text{RMSE} \le 5.0\text{ m}$ for modern satellite-base figures (Biagi and Vidale 2022, Figure 3).
3. **Leave-one-out stability**: maximum leave-one-out prediction error across control points $\text{LOO}_{\max} \le 20.0\text{ m}$ for site plans and $\le 8.0\text{ m}$ for satellite figures.
4. **Scale consistency**: fitted ground metres per plan unit within $\pm 5\%$ of the printed scale bar or metric grid spacing.
5. **Orientation and handedness check**: reflected (mirror) fit $\chi^2_{\text{mirror}} > 10\,\chi^2$ to confirm non-inverted geometry.

### 4.2 Site-specific registration and uncertainty buffers

- **Harappa**: We anchor the HARP local metric grid (`E1400–E2800`, `N0800–N2000`) from Kenoyer (1991, Figure 4.2) and Kenoyer (2008, Figure 3) to Esri World Imagery z18/z16 using permanent conserved features spanning north to south and west to east (Mound F Great Granary, Mound F Workmen's Quarters, Mound AB Muslim Tomb, Mound AB central excavation enclosure, Harappa Museum, Rest House, Mughal Sarai and the Chichawatni–Sahiwal road geometry), cross-checked against Wheeler (1947, Plate XV) R1/R2 registrations. Registered HARP-grid features carry an explicit uncertainty buffer of $\max(10\text{ m}, 1.5 \times \text{RMSE})$.
- **Lakhanjo-Daro (Sukkur)**: We register Biagi and Vidale (2022, Figure 3) to Esri World Imagery z18 via sharp intersections along Roads 3, 7 and 8 in Sukkur SITE. Mound D / Trench C is placed from the registered Figure 3 black rectangle (checked against the printed coordinate `27°43'44"N, 68°50'55"E`) with an explicit $\pm 15\text{ m}$ uncertainty buffer reflecting the caption's statement of approximate location. Because no scaled plan of Mounds A, B and C or the 2013/2017 salvage trenches is locally held, the wider site zone is represented transparently as a **topographic-and-source-bounded envelope** constrained by the DOAM (`27.723889°N, 68.846431°E`) and Shar and Shah (2022; `27.724167°N, 68.847500°E`) main-mound coordinates, the registered Mound D anchor, and the elevated limestone terrace surface above the surrounding flood basin in Copernicus GLO-30, bounded to the ~50 ha extent reported by ul-Haq and Ali (2001: 29). We do not adopt the unauthenticated 300 ha claim, and we assign a $\pm 50\text{ m}$ envelope uncertainty buffer to this wider mound complex.
- **Rupnagar (Ropar)**: We locate the north-east corner of the pavement of **Nalagarh Kothi** on Esri World Imagery z18 (cross-checked against OpenStreetMap and the ASI site coordinate `30°57'59.04"N, 76°31'59.16"E`) as the published `(0, 0)` datum of Prabhakar (*IAR 2011–12*, p. 73). All 21 published 5 m × 5 m trenches (`N45E120` through `N50E145`, `S65W20` through `S70W5`, `N5E20` through `N5E30`, and `S20W175` through `N20W185`) are projected directly from this datum along true north and east. Because the report defines the datum corner on the pavement and does not publish a surveying azimuth error, trench polygons carry a $\pm 6\text{ m}$ datum-and-grid uncertainty buffer (plus a $\pm 3^\circ$ rotation sensitivity check). The wider ~12 ha four-mound footprint (*IAR 2011–12*, p. 72) is mapped from the Copernicus GLO-30 elevated mound mass rising above the Sutlej terrace, partitioned into the protected northern/central/western mound zones and the densely built southern mound under modern Rupnagar, with a $\pm 25\text{ m}$ margin uncertainty buffer. No unmapped 1953–55 RPR-1/RPR-2 trench polygons are fabricated.

## 5. Four-layer geometric architecture

Each target site GeoJSON (`<site>-windows-v1.geojson`) separates features into four explicit layers via the `layer` property:

1. **`layer_1_published_archaeology`**: Published archaeological mounds, walled sectors, excavation zones and source-bounded mound envelopes. Every polygon records `evidence_grade` (`registered_plan`, `datum_grid_trench` or `topographic_source_envelope`), `source_citation`, `positional_uncertainty_m` and `area_ha`.
2. **`layer_2_modern_footprint`**: Modern built-up, industrial and street footprints within each site's analysis frame, derived deterministically by vectorizing ESA WorldCover 2021 class 50 (Built-up) polygons at 10 m resolution and tagging major road and industrial zones verified on Esri World Imagery and OpenStreetMap.
3. **`layer_3_concealed_overlap`**: Exact geometric overlap between Layer 1 and Layer 2, computed on a 2 m metric rasterization grid inside each site's UTM frame (and vectorized into GeoJSON polygons) to yield exact concealed area in hectares, percentage of the archaeological footprint concealed, and lower/upper area bounds under inward/outward positional uncertainty perturbation ($\pm u$).
4. **`layer_4_survey_windows`**: Candidate unbuilt open parcels (`window_type = "geophysical_open_parcel"`) and road or utility rights-of-way (`window_type = "rescue_corridor"`) delineated on Esri World Imagery, ESA WorldCover 2021 and OpenStreetMap within 400 m of Layer 1 or Layer 3, evaluated for non-invasive geophysical survey (ground-penetrating radar, fluxgate gradiometry, electrical resistivity tomography) or municipal salvage section recording.

## 6. Priority scoring and explicit demotion rules

Every Layer 4 candidate window is scored deterministically from 0 to 100 points across three measured quantities computed directly from the held and acquired rasters and Layer 1 geometries:

1. **Surface clearance (0–40 points)**:
   - For `geophysical_open_parcel` windows: `40 × f_open_clean × min(1.0, area_ha / 0.50)`, where `f_open_clean` is the fraction of ESA WorldCover pixels in bare/sparse vegetation, grassland or cropland (classes 30, 40, 60) plus half weight for shrubland (class 20), excluding built-up (50), tree cover (10) and water (80).
   - For `rescue_corridor` windows: `35 × min(1.0, length_m / 300.0)` when the corridor follows an accessible public road or utility verge verified on imagery/OSM, capped at 35 points so open areal grids outrank narrow linear transects when clearance and proximity are equal.
2. **Topographic prominence (0–30 points)**:
   - Computed from Copernicus GLO-30 elevation relative to the local plain baseline $z_{\text{base}}$ (15th percentile elevation within a 1.5 km annulus around the site):
     $$\text{Score}_{\text{topo}} = 30 \times \text{clip}\left(\frac{\Delta z}{6.0\text{ m}}, 0, 1\right)$$
   - Higher relative elevation marks preserved stratified mound mass rather than low floodplain or cut fill.
3. **Proximity to known Harappan contexts (0–30 points)**:
   - Computed from shortest UTM Euclidean distance $d$ from the window polygon to the nearest verified Mature or Early Harappan deposit or walled sector:
     $$\text{Score}_{\text{prox}} = 30 \times \max\left(0, 1 - \frac{\max(0, d - 50\text{ m})}{350\text{ m}}\right)$$
   - Windows inside or within 50 m of verified Harappan contexts receive the full 30 points; windows beyond 400 m receive 0 points.

### Explicit demotion rules

Six hard rules are evaluated automatically for every candidate window before assigning final priority tiers (Tier 1: score $\ge 70$ and no hard demotion; Tier 2: score $50\text{–}69$ or soft-demoted by one tier; Tier 3: score $< 50$ or hard-demoted):

- **D1 (Standing structure cover)**: Any `geophysical_open_parcel` with ESA WorldCover built-up fraction $> 0.70$ fails open-parcel clearance and is hard-demoted to Tier 3 (must be surveyed only as a `rescue_corridor` if a roadway exists).
- **D2 (Dense tree canopy)**: Any `geophysical_open_parcel` with ESA WorldCover tree-cover fraction $> 0.60$ is soft-demoted by one tier and tagged `gpr_obstructed_canopy` (magnetometry or canopy-gap transects required instead of continuous wheeled GPR).
- **D3 (Waterlogging or topographic sink)**: Any window with ESA WorldCover water fraction $> 0.15$ or mean elevation $\Delta z < -1.0\text{ m}$ below the local plain baseline is hard-demoted to Tier 3 (`water_or_sink_attenuation`).
- **D4 (Ferrous industrial clutter or municipal dumping)**: Any window situated inside an active metal-working industrial yard or documented garbage-capped/heavily bulldozed zone (such as Lakhanjo-Daro's eastern mound per Directorate of Antiquities 2022) is tagged `ferrous_clutter_or_disturbed_topsoil`, soft-demoted by one tier for magnetometry/GPR, and reassigned to deep ERT or salvage coring/trench watching.
- **D5 (Active religious, cemetery or conserved monument space)**: Active graveyards, shrines or conserved standing brick monuments are hard-demoted to Tier 3 (`heritage_or_sacred_restricted`) and excluded from invasive testing.
- **D6 (Minimum surveyable scale or excessive distance)**: Any `geophysical_open_parcel` smaller than $0.10\text{ ha}$ or any window more than $400\text{ m}$ from verified Harappan deposits is hard-demoted to Tier 3 (`below_scale_or_distance_threshold`).

## 7. Verification criteria

Independent verification (`code/verify.py`) reads the generated GeoJSON files, CSV table, summary JSON and local input hashes, and passes only if all checks succeed:

1. All local and acquired raw inputs exist and match their recorded SHA-256 checksums.
2. UTM forward/inverse projection closure error is $< 10^{-3}\text{ m}$ across all feature vertices.
3. Every plan/figure registration passes the residual RMSE, leave-one-out, scale-consistency, singular-value and mirror-reflection thresholds of Section 4.1.
4. Every GeoJSON polygon has closed rings, valid counter-clockwise exterior orientation, zero self-intersections, and exact layer tags.
5. Independent planar UTM area and spherical WGS 84 area recomputations agree with recorded `area_ha` values within $0.5\%$ (planar) and $1.0\%$ (spherical).
6. Layer 3 concealed overlap area lies within `[0, area(Layer 1)]`, matches the independent raster intersection to within $0.5\%$, and uncertainty bounds are strictly monotonic (`lower <= nominal <= upper`).
7. All Layer 4 scores and demotion flags match an independent recomputation from the raw WorldCover, DEM and distance inputs.
