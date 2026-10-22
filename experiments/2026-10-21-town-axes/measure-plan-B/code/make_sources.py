"""Compile sources.json for the plan-B role from the town files and the download log.

Usage: python .../code/make_sources.py

Every source named in towns/*.json is listed once per file with the towns that use it, its
citation, figure locator, file path, SHA-256 of the file, the render or extracted image we
measured and its SHA-256, and an acquisition record: the URL, retrieval time and HTTP status
from data/raw/2026-10-21-town-axes/plan-B/downloads.json for files we downloaded, or the
repository path and data/MANIFEST.json entry for files already held locally. Files that were
downloaded and examined but not used for any town are listed under "examined_not_used".
"""
import glob
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROLE = os.path.dirname(HERE)
RAW = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


log = json.load(open(os.path.join(RAW, "downloads.json"), encoding="utf-8"))
by_file = {}
for r in log:
    if r.get("status") == 200 and os.path.exists(r["file"]):
        by_file[r["file"].replace("\\", "/")] = r
manifest = json.load(open(os.path.join("data", "MANIFEST.json"), encoding="utf-8"))
man_by_path = {}
for s in manifest["sources"]:
    for p in s.get("local_paths") or []:
        man_by_path[p.replace("\\", "/")] = s["id"]

entries = []
used_files = set()
for tf in sorted(glob.glob(os.path.join(ROLE, "towns", "*.json"))):
    t = json.load(open(tf, encoding="utf-8"))
    for s in t["sources"]:
        f = (s.get("file") or "").replace("\\", "/")
        used_files.add(f)
        e = {"source_id": s["id"], "town": t["town"], "measured": s.get("used", True) and t["measurable"],
             "citation": s.get("citation_or_service"), "locator": s.get("locator"), "file": f,
             "sha256": s.get("sha256") or (sha(f) if f and os.path.exists(f) else None),
             "pdf_page_index": s.get("pdf_page_index"), "printed_page": s.get("printed_page"),
             "render": s.get("render"), "render_sha256": s.get("render_sha256"),
             "north_reference": s.get("north_reference"), "north_label_text": s.get("north_label_text")}
        if s.get("reason_not_used"):
            e["reason_not_used"] = s["reason_not_used"]
        if f in by_file:
            r = by_file[f]
            e["acquisition"] = {"method": "downloaded by plan-B", "url": r["url"], "final_url": r["final_url"],
                                "retrieved_utc": r["retrieved_utc"], "http_status": r["status"],
                                "content_type": r["content_type"], "bytes": r["bytes"], "sha256_at_download": r["sha256"]}
        else:
            e["acquisition"] = {"method": "file already held in the repository (local-only raw data)",
                                "manifest_source_id": man_by_path.get(f)}
        entries.append(e)

unused = []
for f, r in sorted(by_file.items()):
    if f not in used_files:
        unused.append({"file": f, "url": r["url"], "retrieved_utc": r["retrieved_utc"], "sha256": r["sha256"],
                       "bytes": r["bytes"]})
removed = [r for r in log if not os.path.exists(r["file"])]
out = {"role": "plan-B", "description": "Every plan source used or examined by the plan-B measurer, with its acquisition record. Third-party files stay under data/raw/2026-10-21-town-axes/plan-B/ (Git-ignored).",
       "sources": entries, "examined_not_used": unused,
       "downloaded_then_deleted_for_disk_space": [{"file": r["file"], "url": r["url"], "retrieved_utc": r["retrieved_utc"], "sha256": r["sha256"], "bytes": r["bytes"], "status": r["status"]} for r in removed]}
with open(os.path.join(ROLE, "sources.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("sources", len(entries), "unused downloads", len(unused), "deleted", len(removed))
