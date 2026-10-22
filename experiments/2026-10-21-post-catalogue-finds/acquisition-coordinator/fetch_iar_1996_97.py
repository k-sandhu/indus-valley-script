"""Fetch the Internet Archive copy of IAR 1996-97 with tools/fetch_data.py's fetch_http.

The ASI mirror's 1996-1997 file holds the 1997-98 volume (run 1A), so this volume
was missing. Usage: python -I fetch_iar_1996_97.py <repo root>
"""
import hashlib, importlib.util, json, pathlib, sys, urllib.parse

root = pathlib.Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("fetch_data", root / "tools" / "fetch_data.py")
sys.dont_write_bytecode = True
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

ident = "indianarchaeology199697areview_534_b"
files = [
    ("iar-1996-97-archive", "Indian Archaeology 1996_97 A Review.pdf", 6805984, "f26914ff1f255faaf47328a7fc54ce0b", "5f8cadad28407967aee0c6165d52ed1707d6657a"),
    ("iar-1996-97-archive-djvu-xml", "Indian Archaeology 1996_97 A Review_djvu.xml", 7846937, "399e3333dfe90644c8ac4d404063e4e4", "9d72b9aeacaa3953a860ff6a42ed77d202529352"),
    ("iar-1996-97-archive-djvu-txt", "Indian Archaeology 1996_97 A Review_djvu.txt", 899411, "fcfcb44cf3b09eb5d0d36127163126ed", "3c18fec78398cbcba9ee3e3f6d08412e64e49539"),
]
proposals = []
for sid, name, size, md5, sha1 in files:
    src = {
        "id": sid,
        "title": "Indian Archaeology 1996-97 - A Review",
        "kind": "annual-review",
        "identifiers": [ident],
        "fetch": {"method": "http", "url": f"https://archive.org/download/{ident}/{urllib.parse.quote(name)}",
                  "filename": name.replace(" ", "_"), "bytes": size, "archive_md5": md5, "archive_sha1": sha1},
        "rights": {"status": "rights-unverified", "licence": None,
                   "detail": "Digital Library of India upload on the Internet Archive; the upload's licence tag does not establish the copyright status of the ASI publication."},
        "questions": ["Q-1026"],
    }
    dest = root / "data/raw/2026-10-21-post-catalogue-finds/coordinator/sources" / sid
    status = fd.fetch_http(src, dest, False)
    target = dest / src["fetch"]["filename"]
    data = target.read_bytes()
    rec = json.loads((dest / "acquisition.json").read_text(encoding="utf-8"))
    src["fetch"]["sha256"] = rec["sha256"]
    src.update({"status": "held", "location": "local-only",
                "local_paths": [str(target.relative_to(root)).replace("\\", "/")],
                "hashes": {str(target.relative_to(root)).replace("\\", "/"): rec["sha256"]},
                "md5_match": hashlib.md5(data).hexdigest() == md5, "sha1_match": hashlib.sha1(data).hexdigest() == sha1,
                "fetch_status": status})
    proposals.append(src)
out = root / "experiments/2026-10-21-post-catalogue-finds/acquisition-coordinator/manifest-proposals-coordinator.json"
out.write_text(json.dumps({"sources": proposals}, indent=1), encoding="utf-8")
print(json.dumps([{k: p[k] for k in ("id", "md5_match", "sha1_match", "fetch_status")} | {"sha256": p["fetch"]["sha256"]} for p in proposals], indent=1))
