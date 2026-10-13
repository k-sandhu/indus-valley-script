# Local satellite-screening atlas

Open index.html for the local imagery, feature evidence and geographic links. The Leaflet runtime, Natural Earth geography and supplied overlays are included locally. OSM starts disabled.

For the optional live geographic basemap, serve this directory over local HTTP. For example, run python -m http.server 8765 --bind 127.0.0.1 from this directory, open http://127.0.0.1:8765/, and enable the OSM switch. This is a local viewing server, not a deployment.

The viewer retains supplied archaeological status, observation IDs, scene dates, uncertainty, sources and follow-up tests. Screening polygons remain anomaly footprints. Library and basemap terms are recorded in THIRD-PARTY-NOTICES.md. No offline OSM tiles or remote satellite widgets are included.
