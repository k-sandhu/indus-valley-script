"""Build the object lists for the 13 October 2026 plate checks. No image is opened here.

Check 1 (conjecture C-0004): the Lothal sealings L-161 to L-170 and seal M-895.
Check 2 (Shot A rivals): every seal in Shot A's size population, both halves, one per
component, whose legend ends in 001, 595, 679 or 820, and a comparison set chosen by a
fixed rule from the same population.

Eligibility is Shot A's own code: seal_table.seal_table and rank_lib.size_text_population
and rank_lib.representative are imported read-only from the shot package, with the
component and half taken from the frozen split file. This script does not call
shots_common.load_half, so it appends nothing to Shot A's confirmation-access log.

Comparison rule, fixed before any image is viewed. High-set seals are processed in order
of (half, family identifier length, family identifier). For each, the candidates are
seals of the same population that end in any other sign, have at least one Lipi crop,
and are not already chosen. Level 1: same type, same site, same length. Level 2: same
type and site, length differing by one. Level 3: same type, same site class (Shot A's
six named sites or 'other'), same length. Within the first level that has candidates,
the candidate nearest in log face area is chosen; ties go to the lower SHA-256 of
'2026-10-13-plate-checks:' + family. If no candidate with a crop exists at any level,
the level-1 rule is applied without the crop requirement and the pair is marked as
having no comparison image.

Views for blinded inspection: for each seal, the impression of side A (file
'<cisi>_imp_a.jpg', otherwise the first file whose suffix starts with lowercase 'a') and
the object photograph of side A ('<cisi>_A.jpg', otherwise the first suffix starting
'A'). Seals without a CISI number have no Lipi crop.

Outputs
- experiments/2026-10-13-plate-checks/object-lists.json: identifiers, groups, sites,
  types, lengths, last-sign codes, sizes, crop file names. No full sign sequences.
- data/raw/2026-10-13-plate-checks/object-lists-with-sequences.json: the same rows with
  the catalogue reading-order sequences (local-only; Lipi has no licence).
"""
import hashlib
import json
import math
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHOT_A = ROOT / "experiments/2026-10-12-conjecture-shots/shot-a-rank"
sys.path.insert(0, str(SHOT_A))
from seal_table import seal_table  # noqa: E402
import rank_lib as L  # noqa: E402

FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
SPLIT = ROOT / "data/raw/2026-10-12-conjecture-shots/split.json"
CROPS = ROOT / "data/lipi/public/seal_images"
RAW = ROOT / "data/raw/2026-10-13-plate-checks"
HIGH = {"001", "595", "679", "820"}
SEED = "2026-10-13-plate-checks:"
CHECK1 = ["L-%d" % n for n in range(161, 171)] + ["M-895"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def crop_index():
    names = sorted(os.listdir(CROPS))
    def crops_for(cisi):
        if not cisi or cisi in ("-", "--"):
            return []
        pre = cisi + "_"
        return [n for n in names if n.startswith(pre) or ("_" + pre) in n]
    return crops_for


def view_crops(cisi, crops):
    if not crops:
        return {}
    suffix = {n: n[len(cisi) + 1:].rsplit(".", 1)[0] for n in crops if n.startswith(cisi + "_")}
    imp = [n for n in crops if suffix.get(n) == "imp_a"] or [n for n in crops if suffix.get(n, "")[:1] == "a"]
    obj = [n for n in crops if suffix.get(n) == "A"] or [n for n in crops if suffix.get(n, "")[:1] == "A"]
    out = {}
    if imp:
        out["impression"] = imp[0]
    if obj:
        out["object"] = obj[0]
    if not out:
        out["other"] = crops[0]
    return out


def photo_kind(cisi, name):
    rest = name[len(cisi) + 1:] if name.startswith(cisi + "_") else name
    rest = rest.rsplit(".", 1)[0]
    if rest.startswith("imp") or (rest[:1].islower()):
        return "impression"
    return "object"


def main():
    rows = [json.loads(l) for l in open(FACES, encoding="utf-8") if l.strip()]
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    for r in rows:
        c = split[r["object_family_id"]]
        r["half"], r["component"] = c["half"], c["component"]
    crops_for = crop_index()

    # Check 1 objects: catalogue rows, no eligibility filter.
    check1 = []
    for r in rows:
        if r.get("source_cisi") in CHECK1:
            m = r["metadata"]
            check1.append({
                "cisi": r["source_cisi"], "record_id": r["record_id"], "site": r["site"],
                "type": r["object_type"], "symbol": r.get("symbol"), "length": r["length"],
                "direction": r["direction"], "preservation": m.get("preservation"),
                "horizontal_mm": m.get("horizontal(mm)"), "vertical_mm": m.get("vertical(mm)"),
                "thickness_mm": m.get("thickness(mm)"), "excavation_idno": m.get("excavation-idno"),
                "lipi_crops": crops_for(r["source_cisi"]),
                "last_sign": r["signs_reading_rtl"][-1] if r["signs_reading_rtl"] else None,
                "_sequence_rtl": list(r["signs_reading_rtl"]),
            })
    check1.sort(key=lambda t: (t["cisi"][0], int(t["cisi"].split("-")[1])))

    # Check 2 population: Shot A rules, each half reduced separately, then pooled.
    rec_by_family = {}
    for r in rows:
        rec_by_family.setdefault(r["object_family_id"], []).append(r)
    pop = []
    for half in ("discovery", "confirmation"):
        table = seal_table([r for r in rows if r["half"] == half])
        sub = L.representative(L.size_text_population(table))
        for t in sub:
            t["half"] = half
        pop.extend(sub)
    direction = {r["record_id"]: r["direction"] for r in rows}
    for t in pop:
        t["direction"] = direction.get(t["record_id"])
        t["crops"] = crops_for(t["cisi"])
    high = sorted([t for t in pop if t["last"] in HIGH],
                  key=lambda t: (t["half"], len(t["family"]), t["family"]))
    others_all = [t for t in pop if t["last"] not in HIGH]

    def tie(t):
        return hashlib.sha256((SEED + t["family"]).encode()).hexdigest()

    used, pairs = set(), []
    for h in high:
        levels = [
            ("type+site+length", lambda c: c["type"] == h["type"] and c["site"] == h["site"] and c["length"] == h["length"]),
            ("type+site+length+-1", lambda c: c["type"] == h["type"] and c["site"] == h["site"] and abs(c["length"] - h["length"]) == 1),
            ("type+siteclass+length", lambda c: c["type"] == h["type"] and L.site6(c["site"]) == L.site6(h["site"]) and c["length"] == h["length"]),
        ]
        chosen, level = None, None
        for name, ok in levels:
            cands = [c for c in others_all if c["crops"] and c["family"] not in used and ok(c)]
            if cands:
                cands.sort(key=lambda c: (abs(c["log_area"] - h["log_area"]), tie(c)))
                chosen, level = cands[0], name
                break
        if chosen is None:
            cands = [c for c in others_all if c["family"] not in used and levels[0][1](c)]
            if cands:
                cands.sort(key=lambda c: (abs(c["log_area"] - h["log_area"]), tie(c)))
                chosen, level = cands[0], levels[0][0] + " (no crop available)"
        if chosen is not None:
            used.add(chosen["family"])
        pairs.append((h, chosen, level))

    def public(t, group, pair_id, level=None):
        return {"pair": pair_id, "group": group, "cisi": t["cisi"], "family": t["family"],
                "record_id": t["record_id"], "half": t["half"], "site": t["site"], "type": t["type"],
                "length": t["length"], "last_sign": t["last"], "direction": t["direction"],
                "h_mm": t["h"], "v_mm": t["v"], "log_area": round(t["log_area"], 4),
                "animal": t["animal"], "match_level": level, "lipi_crops": t["crops"],
                "view_crops": view_crops(t["cisi"], t["crops"])}

    check2 = []
    for i, (h, c, level) in enumerate(pairs, 1):
        pid = "P%02d" % i
        check2.append(public(h, "high", pid))
        if c is not None:
            check2.append(public(c, "comparison", pid, level))

    seqs = {t["family"]: t["signs"] for t in pop}
    out = {
        "written_by": "experiments/2026-10-13-plate-checks/build_lists.py",
        "inputs": {"faces_sha256": sha256(FACES), "split_sha256": sha256(SPLIT),
                   "seal_table_sha256": sha256(SHOT_A / "seal_table.py"),
                   "rank_lib_sha256": sha256(SHOT_A / "rank_lib.py")},
        "check2_population": {"seals": len(pop), "high_set": len(high),
                              "high_by_half": {hf: sum(1 for t in high if t["half"] == hf) for hf in ("discovery", "confirmation")},
                              "high_without_crop": sum(1 for t in high if not t["crops"]),
                              "unmatched": sum(1 for _, c, _ in pairs if c is None),
                              "match_levels": {lv: sum(1 for _, c, l in pairs if l == lv) for lv in {l for _, _, l in pairs}}},
        "check1": [{k: v for k, v in t.items() if not k.startswith("_")} for t in check1],
        "check2": check2,
    }
    (HERE / "object-lists.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    RAW.mkdir(parents=True, exist_ok=True)
    local = dict(out)
    local["check1"] = check1
    local["check2"] = [dict(t, sequence_rtl=seqs.get(t["family"])) for t in check2]
    (RAW / "object-lists-with-sequences.json").write_text(json.dumps(local, indent=1), encoding="utf-8")
    print(json.dumps(out["check2_population"], indent=1))


if __name__ == "__main__":
    main()
