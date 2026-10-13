"""Preserve selected-page text and one figure-page rendering as local derivatives."""
import hashlib
import json
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/2026-10-12-transmission-hypothesis/coordinator/population-v1"
PDF = RAW / "narasimhan2019-author.pdf"
PAGES = [1, 2, 6, 8, 9, 12, 13]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    text_path = RAW / "selected-pages-v1.json"
    image_path = RAW / "pdf-page9-v1.png"
    out = RAW / "derivatives-v1.json"
    if any(path.exists() for path in [text_path, image_path, out]):
        raise SystemExit("Derivative endpoint exists; no overwrite.")
    doc = fitz.open(PDF)
    parent = digest(PDF)
    with text_path.open("x", encoding="utf-8") as stream:
        json.dump({"parent_sha256": parent, "pdf_pages_one_based": PAGES,
                   "pages": [{"pdf_page": number, "text": doc[number-1].get_text()}
                             for number in PAGES]}, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    doc[8].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(image_path)
    with out.open("x", encoding="utf-8") as stream:
        json.dump({"parent_path": PDF.relative_to(ROOT).as_posix(), "parent_sha256": parent,
                   "pdf_page_count": len(doc), "derivatives": [
                       {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                        "bytes": path.stat().st_size, "parent_sha256": parent,
                        "redistribution": "local-only"} for path in [text_path, image_path]]},
                  stream, indent=2)
        stream.write("\n")
    print(json.dumps({"pdf_pages": len(doc), "selected": PAGES, "rendered": 9}))


if __name__ == "__main__":
    main()
