"""Build the seal findspot maps: where identical seal texts, near copies and matching sealings were found.

Population and grouping are those of experiments/2026-10-12-seal-text-identity (imported, not copied):
complete, legible, single-line seal texts of at least two signs from South Asian sites, one face per
object family. Site coordinates come from experiments/2026-10-08-site-map-and-overview/data/map-data.json.

Writes
  run-2026-10-20/site-links.json      tracked aggregates: site counts, site-pair links, permutation references
  data/raw/2026-10-20-seal-findspot-maps/seal-findspots.html   local page with record-level values and images
  data/raw/2026-10-20-seal-findspot-maps/records.json          the record-level table embedded in that page

Record-level values (sign sequences, catalogue numbers, findspots) derive from the Lipi export, which has no
licence at the pinned commit, so they stay local (knowledge/provenance/REDISTRIBUTION.md).
"""
import hashlib
import importlib.util
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IDENTITY = ROOT / "experiments/2026-10-12-seal-text-identity/analysis.py"
MAPDATA = ROOT / "experiments/2026-10-08-site-map-and-overview/data/map-data.json"
LINKS = ROOT / "experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv"
TEMPLATE = HERE / "template.html"
OUT = HERE / "run-2026-10-20"
LOCAL = ROOT / "data/raw/2026-10-20-seal-findspot-maps"
IMAGE_PREFIX = "../../lipi/public/seal_images/"  # relative to LOCAL
SEED = 20261020
N_PERM = 5000

MOTIF_LABELS = {
    "Bull1": "unicorn", "Gaur": "short-horned bull (gaur)", "Zebu": "zebu", "Elep": "elephant",
    "Rhin": "rhinoceros", "Buff": "water buffalo", "Tigr": "tiger", "Goat": "goat",
    "CompBull": "composite bull", "Comp": "composite animal", "Scene": "scene", "Mult": "multi-headed animal",
    "Htgr": "horned tiger", "Gavi": "gharial", "Phyt": "plant", "Anth": "anthropomorph", "Ass": "ass",
    "Bull2": "two-horned bull", "Bull3": "bull (Bull3)", "Bull": "bull", "Bult": "bull (Bult)",
    "T-M-T": "T-M-T scene", "T-A-T": "T-A-T scene", "Othr": "other", "Misc": "other", "MISC": "other",
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def import_identity():
    spec = importlib.util.spec_from_file_location("seal_text_identity", IDENTITY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(name):
    return re.sub(r"[^a-z]", "", re.sub(r"\(.*?\)", "", name.lower()))


def site_index():
    sites = json.loads(MAPDATA.read_text(encoding="utf-8"))["sites"]
    idx = {}
    for s in sites:
        for n in [s["name"]] + s.get("alts", []):
            idx.setdefault(norm(n), s)
    return idx


def place(name, idx):
    hit = idx.get(norm(name)) or idx.get(norm(name.split("(")[0]))
    if not hit or hit.get("lat") is None:
        return None
    return {"name": name, "lat": hit["lat"], "lon": hit["lon"], "coord_kind": hit.get("coord_kind"),
            "region": hit.get("region")}


def usable(v):
    return v not in (None, "", "-", "--", "- -", "?", "??", "Unknown", "0", 0)


def images_by_record():
    import csv
    out = defaultdict(list)
    with LINKS.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["record_id"]].append(row["file"])
    return out


def record(f, ident, imgs, role):
    md = f["metadata"]
    code = ident.motif(f)
    size = [md.get("horizontal(mm)"), md.get("vertical(mm)")]
    size = [float(x) for x in size if usable(x)]
    return {
        "id": f["record_id"], "cisi": f.get("source_cisi") or md.get("cisi"), "site": f["site"],
        "type": f["object_type"], "role": role,
        "motif_code": code, "motif": MOTIF_LABELS.get(code, code) if code else None,
        "signs": f["signs_reading_rtl"],
        "size_mm": size if len(size) == 2 else None,
        "material": md.get("material") if usable(md.get("material")) else None,
        "findspot": " / ".join(v for v in (md.get("area-section"), md.get("block-house"), md.get("room-grid")) if usable(v)) or None,
        "depth": md.get("depth") if usable(md.get("depth")) else None,
        "period": " ".join(v for v in (md.get("period"), md.get("phase")) if usable(v)) or None,
        "images": [IMAGE_PREFIX + x for x in imgs.get(f["record_id"], [])[:3]],
    }


def length_class(n):
    return "2" if n == 2 else "3" if n == 3 else "4+"


def pair_key(a, b):
    return " | ".join(sorted((a, b)))


def link_counts(groups_sites):
    """groups_sites: list of (length_class, [site per seal]). Count texts linking each site pair, and texts
    with two or more copies at one site."""
    cross, same = Counter(), Counter()
    for lc, sites in groups_sites:
        uniq = sorted(set(sites))
        for a, b in combinations(uniq, 2):
            cross[(lc, pair_key(a, b))] += 1
        for s, k in Counter(sites).items():
            if k >= 2:
                same[(lc, s)] += 1
    return cross, same


def main():
    ident = import_identity()
    faces = ident.load()
    seals = ident.eligible_seals(faces)
    groups = ident.groups_by_text(seals)
    assert len(seals) == 1430 and len(groups) == 65 and sum(len(v) for v in groups.values()) == 174, \
        "population differs from the 12 October seal-text identity study"
    idx = site_index()
    imgs = images_by_record()

    # matching sealings and tags (S5 of the identity study)
    seal_text = defaultdict(list)
    for i, f in enumerate(seals):
        seal_text[tuple(f["signs_reading_rtl"])].append(i)
    tags = [f for f in faces if f["object_type"].startswith("TAG") and ident.legible(f, 2)
            and tuple(f["signs_reading_rtl"]) in seal_text]
    assert len(tags) == 16

    # texts shown: recurring seal texts plus seal texts that a sealing matches
    shown = {t: list(i) for t, i in groups.items()}
    for f in tags:
        t = tuple(f["signs_reading_rtl"])
        shown.setdefault(t, list(seal_text[t]))
    by_len = defaultdict(list)
    for t in seal_text:
        by_len[len(t)].append(t)

    texts, records = [], {}
    for t, members in shown.items():
        tid = ident.text_id(t)
        seal_ids = []
        for i in members:
            r = record(seals[i], ident, imgs, "seal")
            records[r["id"]] = r
            seal_ids.append(r["id"])
        tag_ids = []
        for f in tags:
            if tuple(f["signs_reading_rtl"]) == t:
                r = record(f, ident, imgs, "sealing")
                records[r["id"]] = r
                tag_ids.append(r["id"])
        near_ids = []
        if len(t) >= 3:
            for k in by_len[len(t)]:
                if k != t and sum(x != y for x, y in zip(k, t)) == 1:
                    for i in seal_text[k]:
                        r = record(seals[i], ident, imgs, "near")
                        r["differs_at"] = [j for j, (x, y) in enumerate(zip(k, t)) if x != y][0]
                        records.setdefault(r["id"], r)
                        near_ids.append(r["id"])
        sites = Counter(records[i]["site"] for i in seal_ids)
        texts.append({"id": tid, "signs": list(t), "length": len(t), "length_class": length_class(len(t)),
                      "seals": seal_ids, "sealings": tag_ids, "near": near_ids,
                      "sites": sites.most_common(),
                      "motifs": Counter(records[i]["motif"] or "none recorded" for i in seal_ids).most_common()})
    texts.sort(key=lambda x: (-len(x["sites"]), -len(x["seals"]), -x["length"]))

    # site table
    site_seals = Counter(f["site"] for f in seals)
    all_sites = set(site_seals) | {f["site"] for f in tags}
    placed = {s: place(s, idx) for s in sorted(all_sites)}
    unplaced = sorted(s for s, p in placed.items() if p is None)
    site_rows = []
    for s, p in placed.items():
        if p is None:
            continue
        p = dict(p)
        p["eligible_seals"] = site_seals.get(s, 0)
        p["seals_in_recurring_texts"] = sum(1 for t in texts if t["id"] in {ident.text_id(k) for k in groups}
                                            for i in t["seals"] if records[i]["site"] == s)
        site_rows.append(p)

    # observed links and a permutation reference: site labels shuffled across all 1,430 eligible seals,
    # text groups held fixed, so each site keeps its number of seals.
    labels = np.array([f["site"] for f in seals])
    gl = [(length_class(len(t)), list(i)) for t, i in groups.items()]

    def counts_with_pooled(lab):
        c, s = link_counts([(lc, lab[i].tolist()) for lc, i in gl])
        for counter in (c, s):
            for (lc, k), v in list(counter.items()):
                counter[("all", k)] += v
        return c, s

    obs_cross, obs_same = counts_with_pooled(labels)
    sims_c, sims_s = defaultdict(lambda: np.zeros(N_PERM)), defaultdict(lambda: np.zeros(N_PERM))
    rng = np.random.default_rng(SEED)
    for r in range(N_PERM):
        c, s = counts_with_pooled(labels[rng.permutation(len(labels))])
        for k, v in c.items():
            sims_c[k][r] = v
        for k, v in s.items():
            sims_s[k][r] = v

    def summarise(obs, sims):
        rows = []
        for k in set(obs) | set(sims):
            v = sims[k] if k in sims else np.zeros(N_PERM)
            o = obs.get(k, 0)
            if o == 0 and v.mean() < 0.5:
                continue
            rows.append({"length_class": k[0], "key": k[1], "observed": o, "expected": round(float(v.mean()), 2),
                         "q025": round(float(np.quantile(v, 0.025)), 1), "q975": round(float(np.quantile(v, 0.975)), 1),
                         "p_ge": round(float((1 + (v >= o).sum()) / (N_PERM + 1)), 4),
                         "p_le": round(float((1 + (v <= o).sum()) / (N_PERM + 1)), 4)})
        order = {"all": 0, "2": 1, "3": 2, "4+": 3}
        return sorted(rows, key=lambda r: (order[r["length_class"]], -r["observed"], -r["expected"]))

    cross_rows = summarise(obs_cross, sims_c)
    same_rows = summarise(obs_same, sims_s)

    sealing_links = Counter()
    for f in tags:
        for i in seal_text[tuple(f["signs_reading_rtl"])]:
            sealing_links[(f["site"], seals[i]["site"])] += 1

    aggregates = {
        "schema_version": "1.0", "status_class": "exploratory",
        "inputs": {"faces_sha256": sha256(ident.FACES), "map_data_sha256": sha256(MAPDATA),
                   "identity_analysis_sha256": sha256(IDENTITY)},
        "population": {"eligible_seals": len(seals), "recurring_texts": len(groups),
                       "seals_in_recurring_texts": sum(len(v) for v in groups.values()),
                       "texts_shown": len(texts), "matching_sealings": len(tags),
                       "unplaced_sites": unplaced},
        "permutation": {"seed": SEED, "draws": N_PERM,
                        "rule": "site labels shuffled across all eligible seals; text groups fixed"},
        "sites": site_rows,
        "cross_site_links": cross_rows,
        "same_site_repeats": same_rows,
        "sealing_links": [{"sealing_site": a, "seal_site": b, "seal_copies": v} for (a, b), v in sealing_links.most_common()],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "site-links.json").write_text(json.dumps(aggregates, indent=1, ensure_ascii=False), encoding="utf-8")

    LOCAL.mkdir(parents=True, exist_ok=True)
    payload = {"aggregates": aggregates, "texts": texts, "records": records}
    (LOCAL / "records.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(payload, ensure_ascii=False))
    (LOCAL / "seal-findspots.html").write_text(html, encoding="utf-8")
    print(json.dumps(aggregates["population"], indent=1))
    print("top cross-site pairs (all lengths):")
    for r in cross_rows[:8]:
        print(" ", r)
    print("same-site repeats (all lengths):")
    for r in [r for r in same_rows if r["length_class"] == "all"][:8]:
        print(" ", r)


if __name__ == "__main__":
    main()
