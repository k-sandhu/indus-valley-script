"""Build a local Leaflet atlas from the coordinator's versioned geographic export."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path

ATLAS = Path(__file__).resolve().parent
REPOSITORY = ATLAS.parents[2]
STATUSES = {"known", "published_candidate", "screening_lead", "rejected", "control", "context"}
KINDS = {"rgb", "false_colour", "ndvi", "terrain"}
GEOMETRIES = {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}
RADIUS = 6378137.0


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(values, label: str) -> list[float]:
    if not isinstance(values, list) or len(values) != 4:
        raise ValueError(f"{label}: expected [west, south, east, north]")
    if any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
        raise ValueError(f"{label}: bounds must be finite numbers")
    west, south, east, north = values
    if not (-180 <= west < east <= 180 and -85.05112878 <= south < north <= 85.05112878):
        raise ValueError(f"{label}: bounds exceed the supported map extent")
    return list(values)


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Overlay is not a PNG: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if width < 1 or height < 1:
        raise ValueError(f"Overlay has invalid dimensions: {path}")
    return width, height


def coordinates(values, label: str) -> None:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{label}: missing geometry coordinates")
    if isinstance(values[0], (int, float)):
        if len(values) < 2 or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
            raise ValueError(f"{label}: invalid coordinate")
        lon, lat = values[:2]
        if not (-180 <= lon <= 180 and -85.05112878 <= lat <= 85.05112878):
            raise ValueError(f"{label}: coordinate outside map range")
    else:
        for nested in values:
            coordinates(nested, label)


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--osm-tile-url", default="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
    args = parser.parse_args()
    source = args.input.resolve()
    output = args.out.resolve()
    if not output.is_relative_to(ATLAS) or output == ATLAS:
        raise ValueError("The viewer output must be a new directory inside atlas/.")
    if output.exists():
        raise FileExistsError("Preserve the existing viewer and choose a new versioned output directory.")
    if not args.osm_tile_url.startswith("https://") or any(t not in args.osm_tile_url for t in ("{z}", "{x}", "{y}")):
        raise ValueError("OSM tile configuration must use HTTPS and z/x/y placeholders.")
    input_content = source.read_bytes()
    input_hash = hashlib.sha256(input_content).hexdigest()
    data = json.loads(input_content.decode("utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("The atlas export must be an object.")
    blocks = data.get("study_blocks")
    overlays = data.get("overlays")
    collection = data.get("feature_collection")
    if not isinstance(blocks, list) or not blocks or not isinstance(overlays, list) or not overlays:
        raise ValueError("The export needs study_blocks and overlays arrays.")
    if not isinstance(collection, dict) or collection.get("type") != "FeatureCollection":
        raise ValueError("feature_collection must be GeoJSON FeatureCollection.")
    block_ids = set()
    for block in blocks:
        block_id = block.get("id")
        if not isinstance(block_id, str) or not block_id or block_id in block_ids:
            raise ValueError("Study block IDs must be nonempty and unique.")
        block_ids.add(block_id)
        bounds(block.get("bbox_lonlat"), f"Block {block_id}")
    overlay_ids = set()
    prepared = []
    for overlay in overlays:
        overlay_id = overlay.get("id")
        if not isinstance(overlay_id, str) or not overlay_id or overlay_id in overlay_ids:
            raise ValueError("Overlay IDs must be nonempty and unique.")
        overlay_ids.add(overlay_id)
        if overlay.get("block_id") not in block_ids or overlay.get("kind") not in KINDS:
            raise ValueError(f"Overlay {overlay_id}: unrecognized block or kind.")
        if overlay.get("display_crs") != "EPSG:3857":
            raise ValueError(f"Overlay {overlay_id}: expected an already warped EPSG:3857 PNG.")
        geographic = bounds(overlay.get("bounds_lonlat"), f"Overlay {overlay_id}")
        projected = overlay.get("bounds_display_m")
        if not isinstance(projected, list) or len(projected) != 4 or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in projected):
            raise ValueError(f"Overlay {overlay_id}: invalid display bounds.")
        xmin, ymin, xmax, ymax = projected
        if not (xmin < xmax and ymin < ymax):
            raise ValueError(f"Overlay {overlay_id}: inverted display bounds.")
        relative = overlay.get("path")
        if not isinstance(relative, str) or "://" in relative:
            raise ValueError(f"Overlay {overlay_id}: a local PNG path is required.")
        asset = (source.parent / relative).resolve()
        if not asset.is_file():
            raise FileNotFoundError(f"Overlay {overlay_id}: {asset}")
        expected = overlay.get("sha256")
        observed = digest(asset)
        if not isinstance(expected, str) or expected.lower() != observed:
            raise ValueError(f"Overlay {overlay_id}: supplied hash does not match the PNG.")
        width, height = png_dimensions(asset)
        west, south, east, north = geographic
        expected_projected = [
            RADIUS * math.radians(west),
            RADIUS * math.log(math.tan(math.pi / 4 + math.radians(south) / 2)),
            RADIUS * math.radians(east),
            RADIUS * math.log(math.tan(math.pi / 4 + math.radians(north) / 2)),
        ]
        pixel = max((xmax - xmin) / width, (ymax - ymin) / height)
        maximum_error = max(abs(a - b) for a, b in zip(projected, expected_projected))
        if maximum_error > max(0.01, pixel / 2):
            raise ValueError(f"Overlay {overlay_id}: geographic/display bounds differ by {maximum_error:.3f} m.")
        if not overlay.get("date") or not overlay.get("attribution") or not overlay.get("source_item_ids"):
            raise ValueError(f"Overlay {overlay_id}: date, source items and attribution are required.")
        prepared.append((overlay, asset, width, height, maximum_error))
    features = collection.get("features")
    if not isinstance(features, list):
        raise ValueError("GeoJSON features must be an array.")
    feature_ids = set()
    for feature in features:
        properties = feature.get("properties", {})
        feature_id = properties.get("id")
        if not isinstance(feature_id, str) or not feature_id or feature_id in feature_ids:
            raise ValueError("Feature IDs must be nonempty and unique.")
        feature_ids.add(feature_id)
        if properties.get("status") not in STATUSES:
            raise ValueError(f"Feature {feature_id}: unsupported status.")
        if properties.get("block_id") and properties["block_id"] not in block_ids:
            raise ValueError(f"Feature {feature_id}: unknown block.")
        geometry = feature.get("geometry", {})
        if geometry.get("type") not in GEOMETRIES:
            raise ValueError(f"Feature {feature_id}: unsupported geometry.")
        coordinates(geometry.get("coordinates"), f"Feature {feature_id}")
        uncertainty = properties.get("coordinate_uncertainty_m")
        if uncertainty is not None and (not isinstance(uncertainty, (int, float)) or not math.isfinite(uncertainty) or uncertainty < 0):
            raise ValueError(f"Feature {feature_id}: invalid coordinate uncertainty.")
    vendor = ATLAS / "vendor" / "leaflet-1.9.4"
    vendor_manifest = json.loads((vendor / "acquisition.json").read_text(encoding="utf-8"))
    for record in vendor_manifest["files"]:
        if digest(vendor / record["path"]) != record["sha256"]:
            raise ValueError(f"Vendored library changed: {record['path']}")
    natural_earth = ATLAS / "vendor" / "natural-earth"
    geography_manifest = json.loads((natural_earth / "acquisition.json").read_text(encoding="utf-8"))
    for record in geography_manifest["files"]:
        if digest(natural_earth / record["path"]) != record["sha256"]:
            raise ValueError(f"Natural Earth source changed: {record['path']}")
    geographic_data = {
        "countries": json.loads((natural_earth / "ne_110m_admin_0_countries.geojson").read_text(encoding="utf-8")),
        "coastline": json.loads((natural_earth / "ne_110m_coastline.geojson").read_text(encoding="utf-8")),
    }
    dataset_notice_path = ATLAS.parent / "THIRD-PARTY-NOTICES.md"
    dataset_notice = dataset_notice_path.read_bytes()
    if b"liability" not in dataset_notice or b"WorldDEM-30" not in dataset_notice:
        raise ValueError("The complete DEM source and liability notices are required.")
    prepared_panels = []
    for feature in features:
        properties = feature["properties"]
        relative = properties.get("panel_path")
        if not relative:
            continue
        panel = (REPOSITORY / relative).resolve()
        if not panel.is_file():
            panel = (source.parent / relative).resolve()
        if not panel.is_file() or digest(panel) != properties.get("panel_sha256"):
            raise ValueError(f"Evidence panel missing or changed: {properties['id']}")
        png_dimensions(panel)
        prepared_panels.append((properties, panel))
    output.mkdir(parents=True)
    asset_dir = output / "assets" / "overlays"
    asset_dir.mkdir(parents=True)
    panel_dir = output / "assets" / "panels"
    panel_dir.mkdir()
    shutil.copytree(vendor, output / "vendor" / "leaflet-1.9.4")
    shutil.copytree(natural_earth, output / "vendor" / "natural-earth")
    asset_records = []
    for index, (overlay, asset, width, height, maximum_error) in enumerate(prepared, start=1):
        destination = asset_dir / f"overlay-{index:03d}.png"
        shutil.copyfile(asset, destination)
        if digest(destination) != overlay["sha256"].lower():
            raise ValueError(f"Overlay changed while being copied: {overlay['id']}")
        original_path = overlay["path"]
        overlay["path"] = destination.relative_to(output).as_posix()
        overlay["input_path"] = original_path
        overlay["width"] = width
        overlay["height"] = height
        projected_bounds = overlay["bounds_display_m"]
        overlay["display_pixel_m"] = [
            (projected_bounds[2] - projected_bounds[0]) / width,
            (projected_bounds[3] - projected_bounds[1]) / height,
        ]
        asset_records.append({
            "id": overlay["id"], "input_path": str(asset), "viewer_path": overlay["path"],
            "bytes": destination.stat().st_size, "sha256": digest(destination),
            "width": width, "height": height, "display_crs": overlay["display_crs"],
            "display_pixel_m": overlay["display_pixel_m"],
            "bounds_lonlat": overlay["bounds_lonlat"], "bounds_display_m": overlay["bounds_display_m"],
            "maximum_bounds_error_m": maximum_error, "date": overlay["date"],
            "source_item_ids": overlay["source_item_ids"], "attribution": overlay["attribution"],
            "transformation": "Byte-identical copy of coordinator-supplied EPSG:3857 PNG; no atlas reprojection.",
        })
    panel_records = []
    for index, (properties, panel) in enumerate(prepared_panels, start=1):
        destination = panel_dir / f"panel-{index:03d}.png"
        shutil.copyfile(panel, destination)
        if digest(destination) != properties["panel_sha256"]:
            raise ValueError("A source evidence panel changed during copying.")
        properties["input_panel_path"] = properties["panel_path"]
        properties["panel_path"] = destination.relative_to(output).as_posix()
        panel_records.append({
            "feature_id": properties["id"], "source_path": str(panel),
            "viewer_path": properties["panel_path"], "bytes": destination.stat().st_size,
            "sha256": properties["panel_sha256"],
            "transformation": "Byte-identical copy of the coordinator's annotated evidence panel.",
        })
    data["viewer_config"] = {
        "built_utc": datetime.now(timezone.utc).isoformat(), "input_name": source.name,
        "input_sha256": input_hash, "osm_tile_url": args.osm_tile_url,
        "osm_initially_enabled": False, "projection": "EPSG:3857",
        "geojson_coordinates": "longitude, latitude",
    }
    for name in ["index.html", "app.js", "styles.css"]:
        shutil.copyfile(ATLAS / "templates" / name, output / name)
    (output / "input-export.json").write_bytes(input_content)
    (output / "atlas-data.json").write_text(json_text(data) + "\n", encoding="utf-8")
    serialized = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    (output / "atlas-data.js").write_text("window.ATLAS_DATA = " + serialized + ";\n", encoding="utf-8")
    geo_serialized = json.dumps(geographic_data, ensure_ascii=False).replace("<", "\\u003c")
    (output / "geography-data.js").write_text("window.ATLAS_GEOGRAPHY = " + geo_serialized + ";\n", encoding="utf-8")
    (output / "DATASET-THIRD-PARTY-NOTICES.md").write_bytes(dataset_notice)
    (output / "THIRD-PARTY-NOTICES.md").write_text(
        "# Atlas component notices\n\n"
        "Leaflet 1.9.4: BSD-2-Clause. The unmodified distribution, complete license and acquisition record are in vendor/leaflet-1.9.4/.\n\n"
        "Online map context: © OpenStreetMap contributors, ODbL; https://www.openstreetmap.org/copyright. "
        "No OSM tiles are packaged. Interactive use follows https://operations.osmfoundation.org/policies/tiles/.\n\n"
        "Natural Earth 1:110 million countries and coastline: public-domain map data. "
        "Made with Natural Earth. Official terms: https://www.naturalearthdata.com/about/terms-of-use/. "
        "Unmodified source geometry, source commit and hashes are in vendor/natural-earth/.\n\n"
        "Processed overlay attribution is retained per layer in atlas-data.json and the visible viewer captions. "
        "The coordinator's acquisition records govern source data and processing provenance.\n", encoding="utf-8",
    )
    with (output / "THIRD-PARTY-NOTICES.md").open("a", encoding="utf-8") as handle:
        handle.write("\nFull source, modification and liability notices for the DEM, Sentinel and WorldCover data "
                     "are preserved verbatim in [DATASET-THIRD-PARTY-NOTICES.md](DATASET-THIRD-PARTY-NOTICES.md).\n")
    (output / "README.md").write_text(
        "# Local satellite-screening atlas\n\n"
        "Open index.html for the local imagery, feature evidence and geographic links. "
        "The Leaflet runtime, Natural Earth geography and supplied overlays are included locally. OSM starts disabled.\n\n"
        "For the optional live geographic basemap, serve this directory over local HTTP. "
        "For example, run python -m http.server 8765 --bind 127.0.0.1 from this directory, "
        "open http://127.0.0.1:8765/, and enable the OSM switch. "
        "This is a local viewing server, not a deployment.\n\n"
        "The viewer retains supplied archaeological status, observation IDs, scene dates, uncertainty, sources and follow-up tests. "
        "Screening polygons remain anomaly footprints. Library and basemap terms are recorded in THIRD-PARTY-NOTICES.md. "
        "No offline OSM tiles or remote satellite widgets are included.\n", encoding="utf-8",
    )
    files = []
    for path in sorted(output.rglob("*")):
        if path.is_file():
            files.append({"path": path.relative_to(output).as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    manifest = {
        "status": "built-local-viewer; browser inspection recorded separately",
        "input": {"path": str(source), "bytes": len(input_content), "sha256": input_hash},
        "built_utc": data["viewer_config"]["built_utc"],
        "study_block_count": len(blocks), "overlay_count": len(overlays), "feature_count": len(features),
        "feature_status_counts": {status: sum(f["properties"]["status"] == status for f in features) for status in sorted(STATUSES)},
        "map_projection": "EPSG:3857",
        "geographic_context": {
            "source": "Natural Earth 1:110 million countries and coastline",
            "repository_commit": geography_manifest["commit"],
            "license": geography_manifest["license"],
            "terms_url": geography_manifest["terms_url"],
            "source_files": geography_manifest["files"],
            "transformation": "Unmodified geographic source geometry serialized into a local browser script.",
        },
        "display_georeferencing": "Supplied EPSG:3857 bounds checked against corresponding EPSG:4326 longitude/latitude bounds.",
        "osm": {"initially_enabled": False, "packaged_tiles": 0, "automated_tile_fetch": False},
        "overlays": asset_records, "evidence_panels": panel_records,
        "dataset_notice": {
            "source_path": str(dataset_notice_path), "viewer_path": "DATASET-THIRD-PARTY-NOTICES.md",
            "sha256": hashlib.sha256(dataset_notice).hexdigest(), "byte_identical": True,
        },
        "files": files,
        "scope": "Asset integrity and display metadata checks; archaeological interpretation remains in the study record.",
    }
    (output / "manifest.json").write_text(json_text(manifest) + "\n", encoding="utf-8")
    print(json.dumps({"viewer": str(output / "index.html"), "blocks": len(blocks), "overlays": len(overlays), "features": len(features)}, indent=2))


if __name__ == "__main__":
    main()
