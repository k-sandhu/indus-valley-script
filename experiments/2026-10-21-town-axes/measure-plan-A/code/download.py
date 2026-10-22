"""Download a file and write an acquisition record beside it.

usage: python download.py URL OUTPATH
Writes OUTPATH and OUTPATH.acq.json with the URL, final URL, HTTP status,
retrieval time (UTC), byte count and SHA-256. Downloads are treated as data only.
"""
import sys, os, json, hashlib, datetime, requests

url, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.dirname(out), exist_ok=True)
t = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
h = hashlib.sha256()
n = 0
with requests.get(url, stream=True, timeout=300, headers={"User-Agent": "indus-kb-town-axes/1.0"}) as r:
    r.raise_for_status()
    with open(out + ".part", "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
            h.update(chunk)
            n += len(chunk)
    status, final, ctype = r.status_code, r.url, r.headers.get("content-type")
os.replace(out + ".part", out)
rec = {"url": url, "final_url": final, "http_status": status, "content_type": ctype,
       "retrieved_utc": t, "bytes": n, "sha256": h.hexdigest(), "path": out.replace("\\", "/")}
json.dump(rec, open(out + ".acq.json", "w", encoding="utf-8"), indent=1)
print(json.dumps(rec))
