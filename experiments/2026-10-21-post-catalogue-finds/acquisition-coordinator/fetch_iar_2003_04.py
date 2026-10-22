"""Fetch IAR 2003-04 from the ASI publication index with tools/fetch_data.py's fetch_http.

The Internet Archive copy used by run 1A (tdl.49427) has unusable OCR. The ASI index at
https://asi.nic.in/pages/Publications/indianArchaelogyReports lists the volume as
download 115. Usage: python -I -B fetch_iar_2003_04.py <repo root>
"""
import importlib.util, json, pathlib, sys

root = pathlib.Path(sys.argv[1]).resolve()
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("fetch_data", root / "tools" / "fetch_data.py")
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

src = {
    "id": "iar-2003-04-asi",
    "title": "Indian Archaeology 2003-04 - A Review",
    "kind": "annual-review",
    "fetch": {"method": "http", "url": "https://asi.nic.in/admin/publications/ePublicationReportsDetails/download/115",
              "filename": "iar-2003-04-asi.pdf"},
    "rights": {"status": "rights-unverified", "licence": None, "detail": "Archaeological Survey of India publication offered for download on the ASI website; no licence stated."},
    "questions": ["Q-1026"],
}
dest = root / "data/raw/2026-10-21-post-catalogue-finds/coordinator/sources" / src["id"]
status = fd.fetch_http(src, dest, False)
rec = json.loads((dest / "acquisition.json").read_text(encoding="utf-8"))
target = dest / src["fetch"]["filename"]
src["fetch"].update({"sha256": rec["sha256"], "bytes": rec["bytes"]})
rel = str(target.relative_to(root)).replace("\\", "/")
src.update({"status": "held", "location": "local-only", "local_paths": [rel], "hashes": {rel: rec["sha256"]}, "fetch_status": status})
out = root / "experiments/2026-10-21-post-catalogue-finds/acquisition-coordinator/manifest-proposals-coordinator.json"
data = json.loads(out.read_text(encoding="utf-8"))
data["sources"] = [s for s in data["sources"] if s["id"] != src["id"]] + [src]
out.write_text(json.dumps(data, indent=1), encoding="utf-8")
print(json.dumps({"id": src["id"], "bytes": rec["bytes"], "sha256": rec["sha256"], "status": status}))
