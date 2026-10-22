"""Download source PDFs for the dating study and log URL, retrieval time and SHA-256.

Usage:
  python -P code/fetch_sources.py doi <subdir> <name> <doi> [<name> <doi> ...]
  python -P code/fetch_sources.py url <subdir> <name> <url> [<name> <url> ...]

Files land in data/raw/2026-10-21-town-axes/dating/<subdir>/<name>.pdf (or the
served extension), with a text extraction <name>.txt made by PyMuPDF when the file
is a PDF. Every retrieval is appended to acquisitions.jsonl in the same subdir.
For a DOI on Cambridge Core the article page is fetched first and its PDF link
followed.
"""
import datetime
import hashlib
import json
import pathlib
import re
import sys
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[4]
RAW = ROOT / "data" / "raw" / "2026-10-21-town-axes" / "dating"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cambridge_pdf_url(doi):
    r = requests.get("https://doi.org/" + doi, headers=UA, timeout=90)
    r.raise_for_status()
    m = re.search(r'(/core/services/aop-cambridge-core/content/view/[^"\s]+?\.pdf/[^"\s]+?\.pdf)', r.text)
    if not m:
        m = re.search(r'(aop-cambridge-core/content/view/[^"\s]+?\.pdf/[^"\s]+?\.pdf)', r.text)
        if not m:
            raise RuntimeError("no PDF link on " + r.url)
        return "https://www.cambridge.org/core/services/" + m.group(1), r.url
    return "https://www.cambridge.org" + m.group(1), r.url


def save(subdir, name, url, landing=None, doi=None):
    d = RAW / subdir
    d.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=UA, timeout=180)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    if r.content[:4] == b"%PDF":
        ext = ".pdf"
    elif "html" in ctype:
        ext = ".html"
    elif "text/plain" in ctype or url.endswith(".txt"):
        ext = ".txt"  # name such files with a suffix (e.g. _djvu) so they do not collide with PDF extractions
    elif "json" in ctype:
        ext = ".json"
    else:
        ext = ".bin"
    path = d / (name + ext)
    path.write_bytes(r.content)
    sha = hashlib.sha256(r.content).hexdigest()
    rec = {"name": name, "file": str(path.relative_to(ROOT)).replace("\\", "/"), "url": url,
           "final_url": r.url, "landing": landing, "doi": doi, "retrieved_utc": now(),
           "sha256": sha, "bytes": len(r.content), "content_type": ctype}
    if ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(path)
            txt = []
            for p in doc:
                txt.append("=== page %d ===\n%s" % (p.number + 1, p.get_text()))
            (d / (name + ".txt")).write_text("\n".join(txt), encoding="utf-8")
            rec["pages"] = doc.page_count
        except Exception as e:  # noqa: BLE001
            rec["text_error"] = repr(e)
    with open(d / "acquisitions.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    print(name, ext, len(r.content), sha[:12], rec.get("pages"))
    return rec


def main():
    mode, subdir, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    for name, ref in zip(rest[0::2], rest[1::2]):
        try:
            if mode == "doi":
                pdf, landing = cambridge_pdf_url(ref)
                save(subdir, name, pdf, landing=landing, doi=ref)
            else:
                save(subdir, name, ref)
        except Exception as e:  # noqa: BLE001
            print("FAILED", name, ref, repr(e))
        time.sleep(1.5)


if __name__ == "__main__":
    main()
