# Source concordance for the satellite investigation

Checked on 12 October 2026. This contributor examined published coordinates and spatial-data access before interpreting any candidate imagery. The outputs are [known-locations.geojson](known-locations.geojson) and [concordance-sources.json](concordance-sources.json). The GeoJSON contains 17 point features representing six archaeological localities and eight geological cores; alternative references for Ganweriwala, Harappa and Kalibangan account for the extra points. It also contains one historical-map coverage polygon. These selected records provide context for the investigation. The underlying regional gazetteer remains incomplete, so a feature without a matching record cannot be designated a new discovery.

Source access is recorded at the level actually achieved: acquired primary page, indexed primary passage, or a preserved observation from an earlier commissioned research pass. Full PDFs were inspected for the Ganweriwala survey plan, the Kutch coordinate table, the Singh supplements and the Garcia-Molsosa availability statement. The current Harappa inventory was read through the web tool; a local HTML download failed. The Uesugi Harappa entry was reused through preserved metadata because its current primary download returned 503. The acquisition log retains successes and failures. A frozen source from an earlier experiment was never replaced to improve an access outcome.

The point coordinates below transcribe source references rather than surveyed settlement boundaries. The GeoJSON retains the full numerical conversion for reproducibility. Decimal places describe the arithmetic, while the assumed plotting buffers describe the limited geographical confidence. Those buffers are 100 m for the Kutch references and geological cores, 1,000 m for Harappa, 1,100 m for Kalibangan and 15,000 m for the conflicting Ganweriwala references. They are analyst choices rather than confidence intervals. In particular, the Ganweriwala buffer displays the discrepancy between sources and does not bound the true site position.

| Reference | Latitude N | Longitude E | Evidence and locator |
|---|---:|---:|---|
| Ganweriwala, government inventory | 28.598889 | 71.150000 | SPC01, Latitude/Longitude fields |
| Ganweriwala, Gulzar survey paper | 28.500000 | 71.066700 | SPC02, printed p. 36/PDF p. 2 |
| Harappa, government inventory | 30.626363 | 72.866035 | SPC03, Latitude/Longitude fields |
| Harappa, preserved Uesugi entry | 30.633333 | 72.866667 | SPC04, printed p. 96/PDF p. 2, citing Possehl 1999 p. 764 |
| Juna Khatiya, field table | 23.691308 | 68.956733 | SPC05, Table 1, printed p. 34/PDF p. 32, row 9 |
| Padta Bet, field table | 23.696453 | 68.973381 | SPC05, same table, row 13 |
| Dwajagadh, field table | 23.720469 | 68.977806 | SPC05, same table, row 14 |
| Kalibangan, Singh paper | 29.474167 | 74.130833 | SC15, Results: Sedimentary characteristics, first paragraph |
| Kalibangan, Nigam paper | 29.483333 | 74.133333 | SPC09, Puratattva 26, printed p. 7/PDF p. 20 |

## Archaeological identity and coordinate disagreements

The [government Ganweriwala inventory](https://doam.gov.pk/public/sites/7243) and [Gulzar’s survey paper](https://easaa.org/wp-content/uploads/2023/01/Sidra-Gulzar-3.pdf) place their references approximately 13.659 km apart. The latter reports a December 2015 surface survey and the use of handheld GPS benchmarks, but it does not list geographic coordinates for those benchmarks. Its Figure 2, printed p. 39/PDF p. 5, supplies a useful identity template: two north/south mounds and a diagonal track. The projected labels in that plan have no identified CRS or zone. This pass extracted the native plan image for comparison and made no speculative transformation of its grid. Precise identity in current imagery remains unresolved; the government's point is the declared frame reference, rather than an accepted calibration target.

The [current government Harappa entry](https://doam.gov.pk/public/sites/6579) is approximately 775 m from the preserved Uesugi coordinate. Its broad 3500–1800 BCE chronology is an inventory label. The older coordinate has one arc-minute precision. Both references identify the known multi-phase locality, but neither supplies its extent. Their agreement at locality scale does not validate a complete known-site layer around Harappa.

The primary Kutch coordinates come from Rajesh S. V. and Abhayan G. S., *Pre-Urban Harappan Phase in Gujarat: An Assessment*, [Social Orbit 6](https://farookcollege.ac.in/imgserver/uploads/attachments/social-orbit-2020_8eeb2f65-311e-4178-a0e4-2fae8a7aa901_0.pdf), 9–45. Table 1 was visually checked at printed p. 34/PDF p. 32. Its Padta Bet and Dwajagadh rows cite the team's 2019 survey and classify their pottery as Pre-Urban Harappan Sindh-type. This coordinate check does not independently date that material. Padta's 50 × 50 m table measure is a historical survey observation; a verified centroid or boundary for the later excavation was not obtained. The journal volume is labelled 2020 but cites a 2021 article, so its actual release date remains unverified.

An indexed passage from [Gadekar and colleagues’ 2021 Juna Khatiya paper](https://doi.org/10.2218/jls.5161), p. 4, §1.1, supplies 23°41′28.52″N, 68°57′23.96″E, approximately 9.85 m from the table point. The current publisher landing page was acquired, while the old PDF routes returned 404. The indexed coordinate is retained as an alternative inside the Juna record. A preserved file named `JUNAKHATIYA2021.pdf` proved to contain Kenoyer’s *The Integration and Diversity in the Indus Tradition (2600–1900 BCE): Comparing Cities, Towns and Villages*. It was rejected as a witness for the Gadekar passage, and left unchanged. Its identity and hash are recorded in the manifest.

An exact primary coordinate for the recently discussed Lakhapar habitation locality near Juna Khatiya was not obtained. Lakhapar is also a repeated toponym in Kutch. Substituting a village centre would create an unverified archaeological location, so this record has no geometry.

## Published geological coordinates and their scope

[Singh and colleagues’ 2017 paper](https://doi.org/10.1038/s41467-017-01643-9), source SC15, supplied an actual spatial table rather than a locality inferred from a map. All four supplementary files were acquired from the working `static-content.springer.com` host. The former `springer-cdn.com` route failed in this session. Supplementary Table 1, printed/PDF p. 53, was checked visually for all eight core positions and drill depths. The two accompanying spreadsheets contain detrital-grain isotope observations; they do not contain a channel vector layer.

The table prints “UTM Coordinates WGS84/NAD83” and omits the zone. Zone 43N was inferred from the named Indian localities, and WGS84 was chosen from the printed datum pair. The transformation used pyproj 3.8.0/PROJ 9.8.1, EPSG:32643 to EPSG:4326, with `always_xy=True`. The derived local witness retains those assumptions, the source hash and inverse-transform checks. Inverse errors below two nanometres demonstrate computational consistency only. The field positional accuracy is unreported, and all cores have an assumed 100 m plotting buffer.

| Core | Original easting | Original northing | Latitude N | Longitude E | Drill depth, m |
|---|---:|---:|---:|---:|---:|
| GS-7 | 412947 | 3261617 | 29.481028 | 74.102062 | 38.44 |
| GS-10 | 414628 | 3260754 | 29.473356 | 74.119466 | 39.02 |
| GS-11 | 415029 | 3259899 | 29.465667 | 74.123668 | 43.32 |
| GS-13 | 411152 | 3263962 | 29.502063 | 74.083358 | 42.32 |
| GS-14 | 409348 | 3265635 | 29.517031 | 74.064609 | 36.95 |
| SRH-5 | 639545 | 3390379 | 30.637917 | 76.456175 | 51.40 |
| KNL-1 | 563528 | 3280343 | 29.651439 | 75.656389 | 40.33 |
| MNK-6 | 589075 | 3297993 | 29.809140 | 75.921779 | 36.19 |

The five GS cores form a transect perpendicular to the former-channel axis near Kalibangan. Source Figure 4a distinguishes that satellite surface trace from the modern Ghaggar course and places the settlement above its southern edge. Figures 5 and 7 distinguish younger inset deposits in GS7/GS10 from older surrounding deposits; the wider subsurface fluvial belt extends beyond the surface trace at GS13/GS14. These relationships support geological context for block B04. A line joining the cores would represent a sampling transect rather than the course of a river. The upstream cores belong to separate source sections and do not transfer their dates to remote candidate features. The GeoJSON therefore marks every core as geological context and retains its sampled-landform description and SC15 interpretation link.

The parent added B04, centred on the coarse Nigam reference at 29.483333 N, 74.133333 E, as a source-availability refinement before viewing its pixels or extracting targets. This contributor did not inspect the candidate raster outputs. The acquired cores justify a local comparison with the published transect; they do not supply a dated polygon for the whole 14 km block.

## Candidate datasets and historical maps

The [Orengo and colleagues’ 2020 article](https://doi.org/10.1073/pnas.2005583117) reports 337 proposed Cholistan clusters, including the published unconfirmed Khundowala and Mulhiawala mounds. The [author code repository](https://github.com/horengo/Orengo_et_al_2020_PNAS), pinned to tree `44f65f47487446332a8307884af1c7022a96fe3b`, contains two scripts. It supplies a literal 47-vertex study-area polygon and named GEE training-asset references, but this pass retrieved no coordinate table or vector layer for the clusters. A local GeoJSON preserves the code's polygon with an explicit closure and records the difference between GEE geodesic edges and linear longitude/latitude edges. It describes study coverage. The exact Khundowala/Mulhiawala candidate points remain unlocated; a named hill or village was not substituted. Publisher/PMC supplement attempts returned challenges or failed; the Europe PMC supplement endpoint timed out. Those results establish this access gap rather than the permanent absence of a dataset.

[Garcia-Molsosa, Orengo and Petrie’s 2023 paper](https://doi.org/10.1186/s40494-023-00985-6), PDF p. 25, links analysis code and describes then-unreleased MAHSA data and commercially licensed TanDEM-X inputs. Its availability section supplies no ready-made palaeochannel GIS layer. The current situation differs: MAHSA's [5 February 2026 launch announcement](https://www.mahsa.arch.cam.ac.uk/news/explore-historic-maps-south-asia-mahsa-cambridge-university-library) reports 480 IIIF images and metadata for 1,245 historical maps. That announcement supports current map access, while the article's archaeological and channel layers remain unacquired in this pass.

A bounded, unauthenticated query of MAHSA's public search API identified [*Cutch No. 6*](https://databasemahsa.org/en/report/4b28eeb0-04a4-47db-a56c-b3329e6e272b), dated 1884, at scale 1:63,360, shelfmark `IOR/X/9884/1/6/1884`. Its catalogue polygon spans 68.5–69.0 E and 23.5–23.75 N, containing the Kutch references in **B03**. The selected factual footprint is included as `historic_map_coverage_only`, with date, scale, shelfmark and exact source locator. The returned tiles contain no scan or IIIF URL, and CUDL's collection page returned 403. Consequently, the layer cannot yet test individual historical land-use symbols or establish a channel course.

The raw query filename retains `MAHSA_MAPQUERY_B02.json` because this contributor initially used the wrong block label; its queried coordinates were the Kutch location. The manifest explicitly associates the unchanged response with B03. For B04, a query at 74.13 E, 29.48 N with a 1 km buffer returned zero records. An alternate Pilibanga text search also returned zero; Hanumangarh returned two sheets at 75–75.5 E and 28.75–29 N, outside B04, which were excluded. This bounded check does not exhaust portal coverage.

## Verification and handoff

The manifest records 12 sources and 26 local witnesses with byte lengths and SHA-256 hashes. All 26 matched at handoff. Each GeoJSON feature joins to a source ID; all point coordinates follow longitude/latitude order; all eight core buffers are 100 m; the historical-map polygon closes. Its eight original core grids were retained alongside the conversions. Three unlocated named records have no invented geometry. Derived images, table transcription, AOI extraction and the map-footprint extraction record their parent hashes and operations.

Raw PDFs, images, scripts and portal responses remain in the ignored local raw directory. Rights for the source code repository, journal scan and historical-map images were not established; the manifest distinguishes those assets from articles carrying explicit CC BY 4.0 licences. The tracked coordinate register and notes contain selected factual observations and authored interpretation. The remaining material gaps are precise Ganweriwala image identity, a full Cholistan candidate vector, the recent Lakhapar coordinate, and locally accessible historical scans or published channel geometry for these blocks.
