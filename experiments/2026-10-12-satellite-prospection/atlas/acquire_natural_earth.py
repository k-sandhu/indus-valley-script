"""Acquire genuine public-domain geographic context at a recorded commit."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

REPOSITORY = "nvkelso/natural-earth-vector"
TERMS = "https://www.naturalearthdata.com/about/terms-of-use/"
FILES = ["ne_110m_admin_0_countries.geojson", "ne_110m_coastline.geojson"]


def acquire(url):
    request = Request(url, headers={"User-Agent": "IndusLocalAtlas/1.0 (public-domain-map-acquisition)"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def main():
    directory = Path(__file__).resolve().parent / "vendor" / "natural-earth"
    manifest_file = directory / "acquisition.json"
    if manifest_file.exists():
        metadata = json.loads(manifest_file.read_text(encoding="utf-8"))
        for record in metadata["files"]:
            if hashlib.sha256((directory / record["path"]).read_bytes()).hexdigest() != record["sha256"]:
                raise ValueError("Existing Natural Earth source file changed.")
        print("Existing Natural Earth files verified.")
        return
    commit_url = f"https://api.github.com/repos/{REPOSITORY}/commits/master"
    commit = json.loads(acquire(commit_url))["sha"]
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    for name in FILES:
        url = f"https://raw.githubusercontent.com/{REPOSITORY}/{commit}/geojson/{name}"
        content = acquire(url)
        parsed = json.loads(content)
        if parsed.get("type") != "FeatureCollection":
            raise ValueError("Expected a genuine GeoJSON FeatureCollection.")
        path = directory / name
        if path.exists() and path.read_bytes() != content:
            raise FileExistsError("Refusing to replace an existing geographic source.")
        path.write_bytes(content)
        records.append({
            "path": name, "url": url, "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "feature_count": len(parsed["features"]),
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        })
    manifest = {
        "component": "Natural Earth 1:110 million countries and coastline",
        "repository": "https://github.com/" + REPOSITORY,
        "commit": commit, "commit_access_url": commit_url,
        "rights_status": "explicit-license", "license": "public domain",
        "terms_url": TERMS,
        "attribution": "Made with Natural Earth.",
        "scope": "Map data are public domain under the official terms; source files are unmodified.",
        "files": records,
    }
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (directory / "NOTICE.md").write_text(
        "# Natural Earth data notice\n\n"
        "Natural Earth map data are public domain. Source: https://github.com/nvkelso/natural-earth-vector\n"
        "Official terms: " + TERMS + "\n"
        "Credit: Made with Natural Earth. Source commit, URLs and hashes are in acquisition.json.\n"
        "This atlas uses the 1:110 million country and coastline geometry for broad geographic context.\n",
        encoding="utf-8",
    )
    print(json.dumps({"commit": commit, "files": [{"path": r["path"], "bytes": r["bytes"]} for r in records]}, indent=2))


if __name__ == "__main__":
    main()
