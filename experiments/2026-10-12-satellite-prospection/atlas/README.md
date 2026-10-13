# Local satellite atlas

The atlas consumes the coordinator's versioned geographic export. It displays actual processed Sentinel or terrain PNGs, supplied feature geometry and local Natural Earth country/coastline data. The initial view selects B01 at its raster footprint. An overview shows all labelled study blocks.

## Reproduction

Acquire the pinned licensed runtime and public-domain geographic context once:

    python experiments/2026-10-12-satellite-prospection/atlas/acquire_leaflet.py
    python experiments/2026-10-12-satellite-prospection/atlas/acquire_natural_earth.py

Build from the completed export, choosing a new viewer version each time:

    python experiments/2026-10-12-satellite-prospection/atlas/build_atlas.py --input experiments/2026-10-12-satellite-prospection/exports/atlas-data-v1.json --out experiments/2026-10-12-satellite-prospection/atlas/viewer-v1

The builder refuses an existing output directory. It validates PNG hashes and dimensions, geographic/display bounds, status values and unique IDs before copying assets. Images are already warped to EPSG:3857; the atlas preserves their bytes and does not repeat that transform. The input export, processed display metadata, source attribution and file hashes are included in the viewer record.

Open the generated index.html to use local imagery and evidence offline. For optional OSM labels, serve the viewer directory with a local HTTP server and enable the online basemap switch. Its README gives the command. No OSM tile archive or background tile downloader is included.

## Viewing and checks

Known archaeology, published candidates, screening leads, rejected features and controls have separate symbols. Evidence panels retain dates, source and observation IDs, coordinate uncertainty, explanations and next tests. A source link is enabled when an actual URL is supplied. The image caption identifies acquisition dates, source item IDs, native pixel size, attribution and limits. Supplied channel/context geometry is a separate selectable layer.

Browser QA uses local assets with the online basemap disabled. Screenshots, snapshots, console and request records are saved under atlas/qa/. These inspect the actual viewer after a completed export is available. They do not authenticate an archaeological interpretation.

License and source handling are documented in [map data and licenses](../research/map-data-and-licenses.md). Leaflet's full BSD-2-Clause notice and Natural Earth's public-domain source record accompany the local vendor assets. No external deployment or publication is part of this atlas build.
