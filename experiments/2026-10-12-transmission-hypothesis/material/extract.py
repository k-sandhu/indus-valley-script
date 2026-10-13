"""Preserve reproducible text derivatives; outputs are local-only source witnesses."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from bs4 import BeautifulSoup
import fitz


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("inputs", type=Path, nargs="+")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    manifest = []
    for i, path in enumerate(args.inputs):
        raw = path.read_bytes()
        if raw.startswith(b"%PDF"):
            doc = fitz.open(path)
            text = "\n".join(f"\n===== PDF PAGE {j + 1} =====\n" + page.get_text() for j, page in enumerate(doc))
            method = "PyMuPDF page.get_text, one-based PDF page markers"
        elif path.suffix == ".xml":
            soup = BeautifulSoup(raw, "xml")
            text = soup.get_text("\n", strip=True)
            method = "BeautifulSoup XML get_text with newlines; table reading requires original XML or PDF"
        else:
            soup = BeautifulSoup(raw, "html.parser")
            if "pdfcoffee" in path.name or "report-mirror" in path.name:
                candidates = soup.select("p.d-block.text-justify")
                text = max((x.get_text("\n", strip=True) for x in candidates), key=len)
                method = "Longest p.d-block.text-justify citation-preview node; primary report transcription only"
            else:
                text = soup.get_text("\n", strip=True)
                method = "BeautifulSoup HTML get_text with newlines; access challenges retained"
        name = f"{i+1:02d}-{path.stem}.txt"
        target = args.output_dir / name
        target.write_text(text, encoding="utf-8")
        manifest.append({"input_path": path.as_posix(), "input_sha256": digest(path), "output_path": target.as_posix(), "output_sha256": digest(target), "characters": len(text), "method": method, "redistribution": "local-only source derivative"})
        print(name, len(text))
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
