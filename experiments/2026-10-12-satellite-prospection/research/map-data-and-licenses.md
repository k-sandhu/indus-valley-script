# Map data, display and licenses

Reviewed 12 October 2026. This atlas displays the study's processed satellite rasters and supplied geographic records locally. It does not acquire imagery through a live web-map widget. Each image retains its observation date, source item IDs, native pixel size, transformation description, bounds and file hash. The study coordinator supplies these fields and the processed rasters; the atlas validates their display metadata.

## Leaflet

The viewer uses a local copy of Leaflet 1.9.4. Its [versioned license](https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/LICENSE) is BSD 2-Clause. The local vendor directory retains the copyright notice, conditions and disclaimer, together with acquisition URLs, dates, byte counts and SHA-256 hashes. The atlas's own code and data records have separate provenance. The [versioned image-overlay implementation](https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/src/layer/ImageOverlay.js) and [tile-layer implementation](https://raw.githubusercontent.com/Leaflet/Leaflet/v1.9.4/src/layer/tile/TileLayer.js) were checked because the current public reference now documents a different API generation.

## OpenStreetMap

OpenStreetMap supplies geographic context when the reader enables its online basemap. Its [copyright page](https://www.openstreetmap.org/copyright) identifies the data as ODbL and requires contributor attribution. The viewer displays a visible linked credit on the map. It neither extracts OSM objects into the screening dataset nor packages OSM tiles.

The [standard raster tile policy](https://operations.osmfoundation.org/policies/tiles/) permits interactive viewport requests and prohibits bulk fetching, prefetch archives and offline tile packages. Browser requests must retain a valid Referer and ordinary HTTP caching. The viewer requests tiles only after explicit opt-in over HTTP or HTTPS, uses the documented HTTPS endpoint, and relies on the browser cache. File-view mode and automated QA keep the layer disabled. No service worker, tile downloader or background tile scan is included.

Local satellite images, evidence records, the Leaflet library and Natural Earth geographic context remain usable without a network connection. OSM labels require an online connection and a local HTTP view. This distinction is stated in the viewer and its README. A missing online basemap does not change the supplied raster georeferencing.

## Natural Earth geographic context

The atlas includes real country and coastline geometry from the [Natural Earth vector repository](https://github.com/nvkelso/natural-earth-vector), at a recorded commit. Its [official terms](https://www.naturalearthdata.com/about/terms-of-use/) place the map data in the public domain. Acquisition records retain each source URL, retrieval time, byte count and hash. The viewer credits Natural Earth and labels its 1:110 million scale. This coarse geographic layer gives the study blocks regional context; individual screening features are displayed on the supplied satellite rasters.

## Sentinel imagery

The [Copernicus Data Space terms](https://dataspace.copernicus.eu/terms-and-conditions) distinguish open Sentinel data from other portal content. The [Sentinel legal notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice) governs reuse of the data. Processed Sentinel overlays carry the prescribed modified-data credit with their actual acquisition year, as explained by the [official citation guidance](https://documentation.dataspace.copernicus.eu/FAQ.html). Scene identifiers, processing steps and acquisition witnesses belong to the coordinator's dataset record. The atlas copies only the processed overlay assets supplied for this run.

Each terrain or channel layer retains its own supplied attribution and limits. Its source is not inferred from appearance. A layer category without supplied data is marked unavailable. Copernicus credit is applied to Sentinel imagery, rather than assigned to unrelated assets.

## Geographic display

The agreed export schema supplies image PNGs already warped to EPSG:3857, the display projection used with the OSM basemap. The atlas does not reproject those images again. Metadata provide both their exact display bounds in metres and corresponding longitude/latitude bounds. The build checks those bounds against each other and records image dimensions and hashes. GeoJSON coordinates remain longitude then latitude; Leaflet receives latitude then longitude through its GeoJSON interface or explicit bounds conversion.

Raster pixel size is distinguished from coordinate uncertainty and archaeological extent. Known sites, published candidates, screening leads, rejected features, controls and landscape context retain separate status labels. A screening polygon is displayed as the supplied anomaly footprint, with its evidence and proposed follow-up; the viewer does not convert it to a settlement boundary or assign a cultural date.

## Verification and source handling

The viewer is built from a versioned export into a new atlas directory. The build preserves the input export, checks local assets and writes a manifest. Browser QA inspects the local viewer with OSM disabled, including evidence popups, layer switching, raster visibility and fallback geographic links. Network records distinguish local requests from remote requests. The atlas and license note are maintained locally; external publication is outside this assignment.
