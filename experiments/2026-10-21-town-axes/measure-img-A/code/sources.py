"""Write sources.json for the img-A role from the local acquisition records.

Every mosaic we stitched has a JSON record next to it in data/raw/.../img-A/mosaics/
(tile range, zoom, retrieval time, SHA-256); every imagery-metadata query has a
record in data/raw/.../img-A/meta/. This script gathers them, marks which mosaics
carry measured lines, and adds the gazetteer and web sources we used to locate sites.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "data" / "raw" / "2026-10-21-town-axes" / "img-A"
ATTR = "Source: Esri, Vantor, Earthstar Geographics, and the GIS User Community"


def main():
    measured, inspected = {}, {}
    for p in sorted((HERE / "picks").glob("*.json")):
        P = json.loads(p.read_text())
        used = {ln["mosaic"] for ln in P.get("lines", [])}
        for key, m in P["mosaics"].items():
            (measured if key in used else inspected).setdefault(m, []).append(P["town"])
    mosaics = []
    for j in sorted((RAW / "mosaics").glob("*.json")):
        r = json.loads(j.read_text())
        f = r["file"]
        use = "measured" if f in measured else ("inspected" if f in inspected else "overview for locating the site")
        mosaics.append({
            "file": f, "sha256": r["sha256"], "town": r["slug"], "use": use,
            "service": r["tile_url"], "attribution": ATTR,
            "zoom": r["zoom"], "tile_x": r["tile_x"], "tile_y": r["tile_y"], "n_tiles": r["n_tiles"],
            "n_placeholder_tiles": r.get("n_placeholder_tiles"),
            "origin_global_px": r["origin_global_px"], "size_px": r["size_px"],
            "retrieved_utc": r["made_utc"], "local_only": True,
        })
    meta = []
    for j in sorted((RAW / "meta").glob("*.json")):
        r = json.loads(j.read_text())
        if "results" in r and isinstance(r["results"], list):
            for res in r["results"]:
                if res["layerId"] != 0:
                    continue
                at = res["attributes"]
                meta.append({"record": str(j.relative_to(ROOT)).replace("\\", "/"), "query_utc": r["query_utc"],
                             "point_lat_lon": [r["lat"], r["lon"]],
                             "service": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/identify",
                             "imagery_source": at.get("SOURCE"), "product": at.get("SOURCE_INFO"),
                             "sensor": at.get("DESCRIPTION"), "acquisition_date": at.get("DATE (YYYYMMDD)"),
                             "source_resolution_m": at.get("RESOLUTION (M)"), "accuracy_m": at.get("ACCURACY (M)"),
                             "levels": [at.get("MinMapLevel"), at.get("MaxMapLevel")],
                             "release": at.get("ReleaseName")})
    gazetteers = [
        {"id": "nominatim", "service": "https://nominatim.openstreetmap.org/search",
         "record": "data/raw/2026-10-21-town-axes/img-A/meta/nominatim_sites.json",
         "use": "first-hit positions of site names; OpenStreetMap contributors, ODbL", "queried_utc": "2026-10-21"},
        {"id": "wikipedia-coordinates", "service": "https://en.wikipedia.org/w/api.php (prop=coordinates)",
         "record": "data/raw/2026-10-21-town-axes/img-A/meta/wikipedia_coords.json",
         "use": "published site positions", "queried_utc": "2026-10-21"},
        {"id": "wikidata-coordinates", "service": "https://www.wikidata.org/w/api.php (wbgetentities, P625)",
         "record": "data/raw/2026-10-21-town-axes/img-A/meta/wikidata_coords.json",
         "use": "published site positions where Wikipedia had none", "queried_utc": "2026-10-21"},
    ]
    web = [
        {"url": "https://en.wikipedia.org/wiki/Surkotada", "use": "site position 23.6304 N, 70.8407 E", "retrieved": "2026-10-21"},
        {"url": "https://en.wikipedia.org/wiki/Banawali", "use": "site position 29.59833 N, 75.39194 E", "retrieved": "2026-10-21"},
        {"url": "https://en.wikipedia.org/wiki/Chanhudaro", "use": "description of the three mounds (no coordinates on the page)", "retrieved": "2026-10-21"},
        {"url": "https://en.wikipedia.org/wiki/Kanmer", "use": "site position 23 deg 25 min 4.44 s N, 70 deg 51 min 48.24 s E (via search result)", "retrieved": "2026-10-21"},
        {"url": "https://en.wikipedia.org/wiki/Shikarpur,_Gujarat", "use": "site position 23 deg 14 min 15 s N, 70 deg 40 min 39 s E (via search result)", "retrieved": "2026-10-21"},
        {"url": "https://journals.ed.ac.uk/lithicstudies/article/download/764/1564", "use": "Shikarpur lithic assemblage paper (Journal of Lithic Studies), same position for the Valamio Timbo mound (via search result)", "retrieved": "2026-10-21"},
    ]
    out = {"role": "img-A", "attribution_for_imagery": ATTR,
           "note": "Imagery files are third-party material kept only under data/raw/2026-10-21-town-axes/img-A/, which Git ignores.",
           "imagery_mosaics": mosaics, "imagery_metadata_queries": meta,
           "gazetteers": gazetteers, "web_pages": web}
    (HERE / "sources.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(mosaics), "mosaics,", len(meta), "metadata records")


if __name__ == "__main__":
    main()
