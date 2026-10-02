"""Acquire public Tell Jokha source witnesses without replacing saved material."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ("frenez2023-author", "https://www.academia.edu/108938835/Indus_Valley_Early_Commercial_Connections_with_Central_and_Western_Asia", ".html"),
    ("frenez2023-figure3", "https://www.harappa.com/sites/default/files/styles/max_2600x2600/public/images/trade-image.jpg.webp?itok=xTbDLrJf", ".webp"),
    ("harappa-source-page", "https://www.harappa.com/content/indus-valley-early-commercial-connections-central-and-western-asia", ".html"),
]

def main():
    target = ROOT / "experiments/2026-10-02-six-hour/tell-jokha-contact/source-manifest.json"
    if target.exists():
        raise RuntimeError("Source manifest already exists.")
    destination = ROOT / "data/six-hour/tell-jokha/contact-witnesses"
    destination.mkdir(parents=True, exist_ok=True)
    entries = []
    for identity, url, suffix in SOURCES:
        path = destination / (identity + suffix)
        if path.exists():
            raise RuntimeError("Refusing to replace source: " + str(path))
        response = requests.get(url, timeout=60)
        entry = {"id": identity, "url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                 "status": response.status_code, "final_url": response.url,
                 "content_type": response.headers.get("content-type"),
                 "rights": "Unresolved redistribution rights; witness local-only"}
        if response.status_code == 200:
            path.write_bytes(response.content)
            entry.update({"path": path.relative_to(ROOT).as_posix(), "bytes": len(response.content),
                          "sha256": hashlib.sha256(response.content).hexdigest()})
            if suffix == ".webp":
                with Image.open(path) as image:
                    entry["image_size"] = list(image.size)
            else:
                soup = BeautifulSoup(response.content, "html.parser")
                for element in soup(["script", "style"]):
                    element.decompose()
                text_path = path.with_suffix(".txt")
                text_path.write_text(soup.get_text("\n", strip=True), encoding="utf-8")
                entry["extracted_text"] = {"path": text_path.relative_to(ROOT).as_posix(),
                                          "sha256": hashlib.sha256(text_path.read_bytes()).hexdigest()}
        entries.append(entry)
    target.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{k: x.get(k) for k in ["id", "status", "bytes", "image_size"]} for x in entries]))

if __name__ == "__main__":
    main()
