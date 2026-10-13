"""Capture bounded chronological/control witnesses locally, never in tracked outputs."""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path

import fitz
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/raw/2026-10-11-early-indian-continuity/review"
PLAN = [
    ("kenoyer2006", "https://www.harappa.com/sites/default/files/pdf/Kenoyer2006_The%20Origin%2C%20Context%20and%20Function%20of%20the%20Indus%20Sc.pdf"),
    ("giosan2012", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3387054/"),
    ("witzel1997", "https://michaelwitzel.org/wp-content/uploads/2014/06/canon.pdf"),
    ("jamison2014-2-15", "https://vedisk.sites.ku.dk/files/2021/09/Jamison-Brereton-s.-2-15.pdf"),
    ("jamison2014-13-22", "https://vedisk.sites.ku.dk/files/2021/09/13-22-Stephanie_W_Jamison_Joel_P_Brereton_The.pdf"),
    ("allon2021", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8789374/"),
    ("wiles2006", "https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/19/66/78/06/2019667806/2019667806.pdf"),
    ("haoma-rituals", "https://www.iranicaonline.org/articles/haoma-ii/"),
    ("avesta-survey", "https://www.iranicaonline.org/articles/avesta-holy-book/"),
    ("indo-iranian-religion", "https://www.iranicaonline.org/articles/indo-iranian-religion/"),
    ("loc-gandhara", "https://guides.loc.gov/south-asian-manuscripts/gandhara"),
    ("lmu-gandhara", "https://www.en.gandhara.indologie.uni-muenchen.de/"),
]


def capture(item):
    source_id, url = item
    observed = dt.datetime.now(dt.timezone.utc).isoformat()
    r = requests.get(url, timeout=45)
    r.raise_for_status()
    is_pdf = r.content.startswith(b"%PDF")
    suffix = ".pdf" if is_pdf else ".html"
    path = OUT / (source_id + suffix)
    if path.exists():
        raise FileExistsError(f"Frozen witness already exists: {path}")
    path.write_bytes(r.content)
    rec = {
        "source_id": source_id, "url": url, "final_url": r.url,
        "retrieved_utc": observed, "status_code": r.status_code,
        "content_type": r.headers.get("content-type"),
        "local_path": path.relative_to(ROOT).as_posix(),
        "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest(),
        "rights_status": "rights-unverified", "raw_handling": "local-only",
    }
    if is_pdf:
        doc = fitz.open(stream=r.content, filetype="pdf")
        rec["page_count"] = len(doc)
        text = "\n".join(f"[PDF PAGE {i + 1}]\n{p.get_text()}" for i, p in enumerate(doc))
    else:
        soup = BeautifulSoup(r.content, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        rec["html_title"] = soup.title.get_text() if soup.title else None
    tpath = OUT / (source_id + ".txt")
    tpath.write_text(text, encoding="utf-8")
    rec["extraction"] = {"path": tpath.relative_to(ROOT).as_posix(), "parent_sha256": rec["sha256"], "sha256": hashlib.sha256(tpath.read_bytes()).hexdigest(), "method": "PyMuPDF get_text" if is_pdf else "BeautifulSoup text; script/style/nav/header/footer removed"}
    return rec


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "capture-v1.json"
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(capture, item): item for item in PLAN}
        for job in concurrent.futures.as_completed(jobs):
            try:
                results.append(job.result())
            except Exception as e:
                source_id, url = jobs[job]
                results.append({"source_id": source_id, "url": url, "error": str(e)})
    results.sort(key=lambda r: r["source_id"])
    manifest_path.write_text(json.dumps({"sources": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps([{k: r.get(k) for k in ("source_id", "bytes", "page_count", "error")} for r in results], ensure_ascii=True))


if __name__ == "__main__":
    main()
