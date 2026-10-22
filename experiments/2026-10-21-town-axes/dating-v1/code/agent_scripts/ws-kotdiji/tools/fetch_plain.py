"""Same as dating-v1/code/fetch_sources.py 'url' mode, but with a plain (non-browser) User-Agent,
for hosts (HAL) that serve a bot-check page to browser user agents without JavaScript."""
import datetime, hashlib, json, pathlib, sys, time
import requests
ROOT = pathlib.Path(r"C:\Users\sandh\OneDrive\Projects\indus_valley_script")
RAW = ROOT / "data" / "raw" / "2026-10-21-town-axes" / "dating"
UA = {"User-Agent": "curl/8.0"}
def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def save(subdir, name, url):
    d = RAW / subdir; d.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=UA, timeout=300); r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    ext = ".pdf" if r.content[:4] == b"%PDF" else (".html" if "html" in ctype else ".bin")
    path = d / (name + ext); path.write_bytes(r.content)
    sha = hashlib.sha256(r.content).hexdigest()
    rec = {"name": name, "file": str(path.relative_to(ROOT)).replace("\\", "/"), "url": url, "final_url": r.url,
           "landing": None, "doi": None, "retrieved_utc": now(), "sha256": sha, "bytes": len(r.content),
           "content_type": ctype, "user_agent": UA["User-Agent"]}
    if ext == ".pdf":
        import fitz
        doc = fitz.open(path)
        (d / (name + ".txt")).write_text("\n".join("=== page %d ===\n%s" % (p.number + 1, p.get_text()) for p in doc), encoding="utf-8")
        rec["pages"] = doc.page_count
    with open(d / "acquisitions.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    print(name, ext, len(r.content), sha[:12], rec.get("pages"))
if __name__ == "__main__":
    subdir, rest = sys.argv[1], sys.argv[2:]
    for name, url in zip(rest[0::2], rest[1::2]):
        try: save(subdir, name, url)
        except Exception as e: print("FAILED", name, url, repr(e))
        time.sleep(1.5)
