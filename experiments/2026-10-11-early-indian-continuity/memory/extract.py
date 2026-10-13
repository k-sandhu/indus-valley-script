"""Preserve plain-text derivatives and parent hashes locally; extraction is not reading-depth evidence."""
from pathlib import Path
import argparse
import hashlib
import json
from bs4 import BeautifulSoup
import fitz

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[2]
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/memory"


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="extract-v1")
    args = parser.parse_args()
    if Path(args.out).name != args.out:
        raise ValueError("Use a fresh directory name")
    out = RAW / args.out
    out.mkdir(parents=True, exist_ok=False)
    records = []
    for source in sorted(RAW.glob("acquisition-v*/*")):
        if source.name in {"acquisition.json"} or source.suffix not in {".html", ".pdf", ".json"}:
            continue
        record = {"source_path": source.relative_to(ROOT).as_posix(),
                  "parent_sha256": digest(source)}
        stem = source.parent.name + "-" + source.stem
        if source.suffix == ".html":
            soup = BeautifulSoup(source.read_bytes(), "html.parser")
            record["html_title"] = soup.title.get_text(" ", strip=True) if soup.title else None
            for item in soup(["script", "style"]):
                item.decompose()
            target = out / (stem + ".txt")
            target.write_text(soup.get_text("\n", strip=True), encoding="utf-8")
            record["transformation"] = "BeautifulSoup Unicode-aware text extraction; script/style excluded; no scripts executed"
        elif source.suffix == ".pdf":
            if not source.read_bytes().startswith(b"%PDF-"):
                record.update(status="not-a-pdf", transformation="signature check only")
                records.append(record)
                continue
            doc = fitz.open(source)
            target = out / (stem + ".json")
            pages = [{"pdf_page": page.number+1, "text": page.get_text()} for page in doc]
            target.write_text(json.dumps(pages, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            record.update(page_count=len(doc), transformation="PyMuPDF text-layer extraction; no OCR or text correction")
        else:
            text = json.loads(source.read_text(encoding="utf-8"))
            target = out / (stem + ".txt")
            target.write_text("\n".join(k+"\t"+v for k,v in text.items()), encoding="utf-8")
            record["transformation"] = "JSON segment identifiers and values retained in source order"
        record.update(path=target.relative_to(ROOT).as_posix(), sha256=digest(target),
                      bytes=target.stat().st_size, status="extracted", disposition="local-only")
        records.append(record)
    (out/"manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"derivatives": len(records), "pdfs": sum('page_count' in r for r in records)}))


if __name__ == "__main__":
    main()
