"""Index of local Lipi families (provisional objects) for museum joins.

Reads data/normalized/lipi_observed_faces.jsonl (local-only) and the Lipi image index.
Usage as a module, or from the repository root for a quick look-up:
    python experiments/2026-10-13-museum-open-access/lipi_index.py cisi M-1727 L-29
    python experiments/2026-10-13-museum-open-access/lipi_index.py idno dk8528 ch2000
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
IMAGES = ROOT / "data/lipi/src/assets/data/seal_id_and_image_mapping.json"
PLACEHOLDERS = {"", "-", "--", "- -", "?", "??", "Unknown", "unknown", "0", "0.0"}


def norm(s):
    return re.sub(r"[^0-9a-z]", "", (s or "").casefold())


def usable(v):
    return v is not None and str(v).strip() not in PLACEHOLDERS


def load():
    fams = {}
    with open(FACES, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            f = fams.setdefault(r["object_family_id"], {"family": r["object_family_id"], "faces": [], "cisi": set(),
                                                        "idno": set(), "site": r["site"]})
            m = r["metadata"]
            f["faces"].append({"record_id": r["record_id"], "length": r["length"], "cisi": r["source_cisi"]})
            if usable(r["source_cisi"]):
                f["cisi"].add(r["source_cisi"].strip())
            if usable(m.get("excavation-idno")):
                f["idno"].add(m["excavation-idno"].strip())
            for k in ("type", "material", "symbol", "shape", "area-section", "block-house", "room-grid", "depth", "period",
                      "phase", "time"):
                f.setdefault(k, m.get(k))
            for k, mk in (("h_mm", "horizontal(mm)"), ("v_mm", "vertical(mm)"), ("t_mm", "thickness(mm)")):
                v = m.get(mk)
                if usable(v) and (f.get(k) in (None, "", "0")):
                    f[k] = v
                else:
                    f.setdefault(k, v)
    imgs = json.loads(IMAGES.read_text(encoding="utf-8"))
    for f in fams.values():
        f["images"] = sorted({x for c in f["cisi"] for x in imgs.get(c, [])})
        f["cisi_norm"] = {norm(c) for c in f["cisi"]}
        f["idno_norm"] = {norm(i) for i in f["idno"]}
        f["lengths"] = [x["length"] for x in f["faces"]]
    return fams


def by_cisi(fams):
    idx = {}
    for f in fams.values():
        for c in f["cisi_norm"]:
            idx.setdefault(c, []).append(f["family"])
    return idx


def idno_prefix(fams, key, site=None):
    k = norm(key)
    out = []
    for f in fams.values():
        if site and f["site"] != site:
            continue
        for i in f["idno_norm"]:
            if i.startswith(k):
                out.append((f["family"], i, i == k))
    return out


def brief(f):
    return {k: (sorted(v) if isinstance(v, set) else v) for k, v in f.items()
            if k in ("family", "site", "cisi", "idno", "type", "material", "symbol", "shape", "h_mm", "v_mm", "t_mm",
                     "lengths", "images", "area-section", "block-house", "room-grid", "depth")}


if __name__ == "__main__":
    fams = load()
    mode, keys = sys.argv[1], sys.argv[2:]
    if mode == "cisi":
        idx = by_cisi(fams)
        for k in keys:
            for fid in idx.get(norm(k), []):
                print(k, json.dumps(brief(fams[fid]), ensure_ascii=False))
            if not idx.get(norm(k)):
                print(k, "not found")
    elif mode == "idno":
        for k in keys:
            hits = idno_prefix(fams, k)
            print(k, len(hits), [(h, i, e) for h, i, e in hits][:12])
            for h, _, _ in hits[:6]:
                print("   ", json.dumps(brief(fams[h]), ensure_ascii=False))
