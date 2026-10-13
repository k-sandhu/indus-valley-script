"""Acquire the pinned Leaflet runtime and preserve its explicit license."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

VERSION = "1.9.4"
BASE = f"https://cdn.jsdelivr.net/npm/leaflet@{VERSION}/dist/"
FILES = [
    "leaflet.js", "leaflet.js.map", "leaflet.css",
    "images/layers.png", "images/layers-2x.png",
    "images/marker-icon.png", "images/marker-icon-2x.png", "images/marker-shadow.png",
]
LICENSE_URL = f"https://raw.githubusercontent.com/Leaflet/Leaflet/v{VERSION}/LICENSE"


def main() -> None:
    destination = Path(__file__).resolve().parent / "vendor" / f"leaflet-{VERSION}"
    manifest_path = destination / "acquisition.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in manifest["files"]:
            content = (destination / record["path"]).read_bytes()
            if hashlib.sha256(content).hexdigest() != record["sha256"]:
                raise ValueError(f"Existing vendor asset changed: {record['path']}")
        print(f"Existing pinned runtime verified: {destination}")
        return
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for relative, url in [(name, BASE + name) for name in FILES] + [("LICENSE", LICENSE_URL)]:
        request = Request(url, headers={"User-Agent": "IndusLocalAtlas/1.0 (pinned-library-acquisition)"})
        with urlopen(request, timeout=60) as response:
            content = response.read()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != content:
            raise FileExistsError(f"Refusing to replace a different vendor asset: {target}")
        target.write_bytes(content)
        records.append({
            "path": relative, "url": url, "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        })
    license_text = (destination / "LICENSE").read_text(encoding="utf-8")
    if "BSD 2-Clause License" not in license_text or "Volodymyr Agafonkin" not in license_text:
        raise ValueError("The acquired Leaflet license did not match the expected notice.")
    manifest = {
        "component": "Leaflet", "version": VERSION,
        "rights_status": "explicit-license", "license": "BSD-2-Clause",
        "license_url": LICENSE_URL,
        "scope": "Unmodified pinned Leaflet distribution files; full license retained.",
        "files": records,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Acquired {len(records)} pinned files with license: {destination}")


if __name__ == "__main__":
    main()
