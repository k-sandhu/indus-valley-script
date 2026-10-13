# Atlas interface

The coordinator supplies exports/atlas-data-v1.json. Later exports use the same schema. The builder consumes that export and creates a new versioned viewer directory; it does not modify analysis, candidate or report files.

The export contains study_blocks, overlays and a GeoJSON feature_collection. Study blocks carry ID, name, region IDs, longitude/latitude bounds, native EPSG and scene IDs. Each overlay carries ID, block ID, kind, local path, longitude/latitude bounds, EPSG:3857 display bounds, date, source item IDs, native pixel size, attribution, limits and SHA-256. Overlay kinds are rgb, false_colour, ndvi and terrain.

Feature properties carry ID, name, status, block ID, observation IDs, explanation, source IDs, dates, coordinate uncertainty and the next test. Allowed statuses are known, published_candidate, screening_lead, rejected, control and context. The atlas preserves point, polygon and line geometries. Evidence text is rendered safely as text. Source URLs are linked only when supplied in the export.

The viewer opens on B01 at its raster-covered scale and provides an overview of all labelled study blocks, a block selector, local raster selection, opacity, status filters, coordinate-uncertainty display, and supplied channel or landscape-context layers. A local Natural Earth country/coastline layer supplies genuine regional geography. Local rasters are visible by default. OSM is optional and initially disabled. No remote satellite widget is used as evidence.

Candidate popups and the evidence panel identify status, observations, explanation, dates, coordinate uncertainty, sources and the next test. Raster captions show fixed acquisition dates, scene IDs, native pixel size, attribution and limits. Plain geographic links and a local image/evidence list remain available if the mapping library fails.

Geographic QA checks asset hashes, PNG dimensions, projection metadata and supplied bounds. Browser QA uses local assets and keeps OSM disabled. A build fails on a missing image, inconsistent hash, unsupported status, duplicate ID or incompatible projection rather than silently substituting data.
