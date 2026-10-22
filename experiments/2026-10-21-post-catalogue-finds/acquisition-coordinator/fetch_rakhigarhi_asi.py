"""Fetch the ASI edition of Nath, Excavations at Rakhigarhi (1997-98 to 1999-2000) with tools/fetch_data.py's fetch_http.

The Internet Archive copy read by run 2N is a draft dated 31 December 2014 without a seal
catalogue; run 1B found the ASI download 12 for the published edition. Usage: python -I -B fetch_rakhigarhi_asi.py <repo root>
"""
import importlib.util, json, pathlib, sys

root = pathlib.Path(sys.argv[1]).resolve()
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("fetch_data", root / "tools" / "fetch_data.py")
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

src = {
    "id": "rakhigarhi-nath-asi-2014",
    "title": "Excavations at Rakhigarhi (1997-98 to 1999-2000)",
    "kind": "excavation-report",
    "fetch": {"method": "http", "url": "https://asi.nic.in/admin/publications/ePublicationReportsDetails/download/12",
              "filename": "rakhigarhi-nath-asi-2014.pdf"},
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
