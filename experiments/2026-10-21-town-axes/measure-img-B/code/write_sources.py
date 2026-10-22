"""Write sources.json for role img-B: every service, lookup and imagery mosaic we used.

Usage: python experiments/2026-10-21-town-axes/measure-img-B/code/write_sources.py
"""
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tiles  # noqa: E402

HERE = Path(__file__).resolve().parent
ROLE = HERE.parent


def utc(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    towns = {}
    for f in sorted((ROLE / "towns").glob("*.json")):
        t = json.loads(f.read_text(encoding="utf-8"))
        for s in t["sources"]:
            towns.setdefault(s["file"], []).append({"town": t["town"], "source_id": s["id"], "imagery_date": s.get("imagery_date"),
                                                   "role": s.get("role_in_measurement")})
    mosaics = []
    pat = re.compile(r"(?P<name>.+?)(?:_wb(?P<rel>\d+))?_z(?P<z>\d+)_x(?P<x0>\d+)-(?P<x1>\d+)_y(?P<y0>\d+)-(?P<y1>\d+)\.png$")
    rel_dates = dict(tiles.wb_releases())
    for p in sorted((tiles.RAW / "mosaics").glob("*.png")):
        m = pat.match(p.name)
        rp = str(p.relative_to(tiles.ROOT)).replace("\\", "/")
        rec = {"file": rp, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size,
               "mosaicked_utc": utc(p.stat().st_mtime)}
        if m:
            rel = m.group("rel")
            rec.update({"zoom": int(m.group("z")), "tile_x": [int(m.group("x0")), int(m.group("x1"))],
                        "tile_y": [int(m.group("y0")), int(m.group("y1"))],
                        "service": "Esri World Imagery Wayback release " + rel + f" (published {rel_dates.get(rel)})" if rel else "Esri World Imagery (current)",
                        "tile_url_template": tiles.WB_TILE_URL.replace("{rel}", rel) if rel else tiles.TILE_URL})
        rec["used_by"] = towns.get(rp, [])
        rec["purpose"] = "measured or inspected in a town file" if rec["used_by"] else "inspected only (overview or location search)"
        mosaics.append(rec)
    identify = []
    for p in sorted((tiles.RAW / "identify").glob("*.json")):
        d = json.loads(p.read_text())
        top = (d.get("results") or [{}])[0].get("attributes", {})
        identify.append({"file": str(p.relative_to(tiles.ROOT)).replace("\\", "/"), "retrieved_utc": d.get("_retrieved_utc"),
                         "url": d.get("_url"), "date": top.get("DATE (YYYYMMDD)"), "source": top.get("SOURCE"),
                         "source_info": top.get("SOURCE_INFO"), "sensor": top.get("DESCRIPTION"),
                         "resolution_m": top.get("RESOLUTION (M)"), "max_level": top.get("MaxMapLevel")})
    wbcfg = tiles.RAW / "wayback" / "waybackconfig.json"
    out = {
        "role": "img-B",
        "written_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "attribution": tiles.ATTRIBUTION,
        "rights": "Esri World Imagery tiles and the mosaics and inspection crops made from them are third-party material; they are kept only under data/raw/2026-10-21-town-axes/img-B/, which Git ignores, and are not copied into the experiment directory.",
        "services": [
            {"id": "esri-world-imagery", "kind": "imagery tile service", "url": tiles.TILE_URL,
             "attribution": tiles.ATTRIBUTION, "projection": "Web Mercator (EPSG:3857), 256 px tiles, north up",
             "accessed_utc": "2026-10-21", "note": "Zoom 18 is the highest level with real detail at every site we examined; the identify service reports MaxMapLevel 18 for every imagery block we hit."},
            {"id": "esri-world-imagery-identify", "kind": "imagery metadata", "url": tiles.IDENTIFY_URL,
             "note": "Point query returning the imagery block, sensor, resolution and acquisition date; one cached response per town under identify/."},
            {"id": "esri-wayback", "kind": "archived imagery releases", "config_url": tiles.WB_CONFIG_URL,
             "config_file": str(wbcfg.relative_to(tiles.ROOT)).replace("\\", "/"),
             "config_sha256": hashlib.sha256(wbcfg.read_bytes()).hexdigest(), "config_retrieved_utc": utc(wbcfg.stat().st_mtime),
             "tile_url_template": tiles.WB_TILE_URL, "tilemap_url_template": tiles.WB_TILEMAP_URL,
             "metadata": "each release's metadataLayerUrl (World_Imagery_Metadata_<year>_r<nn>/MapServer, layers 4 to 6) queried at the town's point for SRC_DATE, SRC_DESC and SRC_RES",
             "attribution": tiles.ATTRIBUTION,
             "note": "Used where the current release shows the architecture poorly (Lothal, Harappa) and to search for visible remains at backfilled or overgrown sites."},
            {"id": "osm-nominatim", "kind": "gazetteer", "url": "https://nominatim.openstreetmap.org/search",
             "accessed_utc": "2026-10-21", "note": "Coordinates of archaeological-site nodes for Surkotada, Rakhigarhi (RGR-1, RGR-2), Kotada Bhadli and Bhirrana, and of villages near other sites. Data (c) OpenStreetMap contributors, ODbL."},
            {"id": "wikidata", "kind": "gazetteer", "url": "https://www.wikidata.org/wiki/Special:EntityData/{QID}.json",
             "accessed_utc": "2026-10-21", "note": "Coordinates (P625) of Chanhu-daro (Q1062208), Juni Kuran (Q63358276), Sutkagen Dor (Q2369920) and Nausharo (Q2039702). CC0."},
            {"id": "wikipedia", "kind": "gazetteer", "accessed_utc": "2026-10-21",
             "pages": ["https://en.wikipedia.org/wiki/Surkotada", "https://en.wikipedia.org/wiki/Banawali",
                       "https://en.wikipedia.org/wiki/Kanmer", "https://en.wikipedia.org/wiki/Chanhudaro",
                       "https://en.wikipedia.org/wiki/Shikarpur,_Gujarat"],
             "note": "Published site coordinates read from the article infoboxes; Chanhudaro gives none."},
        ],
        "identify_responses": identify,
        "mosaics": mosaics,
    }
    (ROLE / "sources.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(mosaics), "mosaics,", len(identify), "identify responses")


if __name__ == "__main__":
    main()
