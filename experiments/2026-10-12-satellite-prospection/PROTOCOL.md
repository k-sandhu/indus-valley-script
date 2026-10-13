# Satellite, terrain and former-channel screening

Recorded 12 October 2026 before new raster acquisition or candidate extraction. This study extends the reviewed October 11 settlement paper. The user requests actual imagery, terrain and palaeochannel investigation, specific possible locations, real-map overlays and another Claude Code Opus 5.5 review. Work is unattended, with no questions or external publication.

## Initial choice and outputs

Begin with the Cholistan/Ganweriwala regions P01/P02, Harappa–Old Beas/interfluve regions P08/P09, and western Kutch P12. These combine published archaeological context with different visibility and formation processes. Availability of authenticated coordinates, cloud-free scenes and local geomorphic information will determine bounded study blocks. Kirthar piedmont P18 is a reserve region if one initial region cannot support meaningful screening. Record block selection and its timing before candidate results.

Acquire actual multispectral Sentinel-2 Level-2A scenes and a documented approximately 30-metre elevation surface. Record collection, platform, item, acquisition time, processing baseline, radiometric scale/offset, pixel resolution, projection, bounds, masks, cloud fraction, asset URL and local hashes. Use at least two usable dates per selected block when available. Cloud-free scene metadata alone is insufficient: per-pixel quality within a block is required. Preserve native and reprojected transforms.

Search for published palaeochannel vectors or georeferenced supplementary data. If only a map figure is obtainable, any traced feature must be labelled as an approximate digitization with a documented transformation and positional error. Image-derived drainage or moisture traces are separate observations and do not inherit a palaeochannel age. A channel near occupation may predate it, postdate it or have been inactive during it.

Produce a reproducible screening report, observation and candidate registers, exact raster-analysis outputs, GeoJSON/KML, a real geographic map atlas and annotated image panels. Known archaeology, published unconfirmed proposals, newly screened unmatched leads, controls and rejected features must have distinct status. A search lead is not a discovery or an authenticated Indus settlement. Record the accessible comparison inventories and incomplete match coverage.

## Screening and comparison rules

Keep visible-mound or surface-anomaly screening separate from buried-surface prospects. Ten-metre optical pixels cannot directly authenticate walls or date occupation. A 30-metre DSM includes surface objects and has vertical uncertainty that can exceed a low mound's relief. Report native pixel support, apparent footprint and coordinate uncertainty; avoid interpreting resampled pixels as additional resolution.

An exploratory spectral/morphological detector may identify review targets, with parameters and rejected results retained. Inspect target patches alongside adjacent landform controls, seasonal imagery, modern roads/buildings/canals and dune or salt signatures. Record each target's raw contrast and control distribution without a discovery-probability interpretation. Known-site patches are calibration examples and cannot supply an independent detector performance estimate. Candidate selection and later refinements are exploratory.

Measure projected footprint and local relief with documented mask/annulus definitions. Exclude cloud, shadow, saturation and nodata. Keep terrain as a corroborating or unresolved descriptor rather than a substitute for dating. Do not multiply dependent optical and terrain descriptions into independent evidence. Compare seasonal consistency and land-use explanations. Inspect whether a proposed location falls on a dated, habitable surface only when actual local chronology supports that judgment.

Every shortlisted point or polygon must link to acquired scene IDs, actual image panels, terrain output, former-channel source or an explicit missing-data status, accessible-record matching, a rival explanation and a next discriminating test. Demote targets whose visible signature is adequately explained by current construction, canal spoil, dune morphology or other natural surfaces. No target can be forced into a shortlist merely to satisfy a desired count.

## Maps, rights and review

Overlay georeferenced imagery and target geometry on real maps with geographic basemap attribution. Show acquisition dates, source labels, layer bounds, latitude/longitude and a scale. Distinguish current waterways, published former-channel interpretations and newly traced surface features. A live basemap is navigation context, not independent archaeological evidence. Match map polygons to raster transforms and retain a georeferencing check.

Downloaded sources and raw rasters stay in ignored local data by default. Verify dataset-specific license terms before packaging transformed imagery or terrain panels. Do not cache or bulk-download standard OSM tiles. No deployment, repository visibility change, CI/CD or recurring automation is authorized.

Freeze the complete draft, candidate register and analysis manifest before a fresh actual `claude-opus-5-5` CLI review. Supply the sources, processing choices, candidate/control observations and map checks; identify whether the reviewer can inspect images or is limited to text. Address material findings in a new endpoint. Preserve failed acquisitions, selection refinements, rejected targets and frozen prior study files. Record externally observable outcomes and repairs in the research memory.

Follow the repository writing rules: maximize reader comprehension, explain ideas in connected prose, keep necessary shared assumptions together, and avoid repeated corrective warnings. Coordinate contributors through distinct file ownership.

## Source-availability refinement, 12 October 2026

After acquiring the first three blocks but before viewing or extracting candidate outcomes in a fourth, the current publisher supplement for Singh2017 became available. It supplies actual sediment-core positions at Kalibangan and Pilibanga. Add a14km-square block centered on the published Kalibangan reference, retaining the initial blocks. This provides a local comparison with measured former-channel stratigraphy. The table's UTM zone is absent; zone43N/WGS84 conversion is inferred from the published regional location and must remain labelled. The positions form a sampling transect, not a river polygon. Connecting them cannot manufacture a palaeochannel centerline.
