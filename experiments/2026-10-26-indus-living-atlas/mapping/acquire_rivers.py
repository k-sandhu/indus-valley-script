"""Acquire pinned public-domain modern river context to the checked local store."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parents[1]
PHYSICAL = Path("D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/mapping")
LOGICAL = "data/raw/2026-10-26-indus-living-atlas/mapping"
PIN = "ca96624a56bd078437bca8184e78163e5039ad19"
URL = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{PIN}/geojson/ne_50m_rivers_lake_centerlines.geojson"


def main():
    if not PHYSICAL.parent.parent.parent.exists() or (ROOT / "data/raw").resolve() != Path("D:/projects/indus_valley_script/data/raw"):
        raise RuntimeError("The required D: store or data/raw junction is unavailable.")
    record_path = PACKAGE / "mapping/river-acquisition-v2.json"
    if record_path.exists():
        record = json.loads(record_path.read_text(encoding="utf-8"))
        path = Path(record["physical_path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("The preserved river input differs from its recorded hash.")
        print("Existing pinned river input verified.")
        return
    request = Request(URL, headers={"User-Agent": "IndusLivingAtlas/1.0 (public-domain river context)"})
    with urlopen(request, timeout=45) as response:
        content = response.read()
    data = json.loads(content)
    if data.get("type") != "FeatureCollection":
        raise ValueError("The response is not river GeoJSON.")
    PHYSICAL.mkdir(parents=True, exist_ok=True)
    target = PHYSICAL / "ne_50m_rivers_lake_centerlines.geojson"
    if target.exists():
        raise FileExistsError("An unregistered river witness already exists; inspect it before proceeding.")
    target.write_bytes(content)
    record = {"source_title": "Rivers, Lake Centerlines", "authors": "Natural Earth", "url": URL,
              "source_page": "https://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-rivers-lake-centerlines/",
              "commit": PIN, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
              "logical_path": f"{LOGICAL}/{target.name}", "physical_path": target.as_posix(),
              "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(),
              "feature_count": len(data["features"]), "rights_status": "explicit-license", "license": "Public domain",
              "terms_url": "https://www.naturalearthdata.com/about/terms-of-use/",
              "scope": "Small-scale contemporary drainage context. No Bronze Age channel position is inferred.",
              "transformation": "The atlas retains line geometry and name only; no archaeological annotation is added."}
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"bytes": len(content), "features": len(data["features"]), "sha256": record["sha256"]}))


if __name__ == "__main__":
    main()
