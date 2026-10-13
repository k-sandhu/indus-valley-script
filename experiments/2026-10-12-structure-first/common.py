"""Shared loaders for the structure-first program.

All sequences are in reading order. Distinct texts are the analysis unit; copies
on several objects and faces of one object share a component and never cross a
fold. See PROTOCOL.md, "Shared inputs and grouping".
"""
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROG = ROOT / "experiments/2026-10-12-structure-first"
RAW = ROOT / "data/raw/2026-10-12-structure-first"
CLEAN = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
SCHEMA = ROOT / "data/normalized/mayig_sign_schema.json"
BRONZE = ROOT / "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl"
SEED = 20261012


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


class UnionFind:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def load_clean():
    """Return distinct clean texts with their component and fold.

    Each item: dict(text=tuple, component=str, fold=int, records=[ids], families=[ids],
    sites=set, types=set, symbols=set).
    """
    rows = [r for r in read_jsonl(CLEAN) if r["clean_rtl_singleline"] and not r["has_unknown_sign"]]
    uf = UnionFind()
    for r in rows:
        t = "T:" + "-".join(r["signs_reading_rtl"])
        uf.union(t, "F:" + r["object_family_id"])
    by_text = collections.OrderedDict()
    for r in rows:
        t = tuple(r["signs_reading_rtl"])
        d = by_text.setdefault(t, {"text": t, "records": [], "families": set(), "sites": set(),
                                   "types": set(), "symbols": set()})
        d["records"].append(r["record_id"])
        d["families"].add(r["object_family_id"])
        d["sites"].add(r["site"])
        d["types"].add(r["object_type"])
        d["symbols"].add(r["symbol"])
    comps = collections.defaultdict(list)
    for t, d in by_text.items():
        d["component"] = uf.find("T:" + "-".join(t))
        comps[d["component"]].append(d)
    for c, items in comps.items():
        key = min(rid for d in items for rid in d["records"])
        h = int(hashlib.sha256(f"{SEED}:{key}".encode()).hexdigest(), 16)
        for d in items:
            d["fold"] = h % 5
    return list(by_text.values())


def load_coding(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            code = r["code"].strip().zfill(3)
            mods = [m.strip() for m in (r.get("mods") or "").split(";") if m.strip()]
            rows[code] = {"base": r["base"].strip(), "mods": mods, "count": (r.get("count") or "").strip(),
                          "confidence": (r.get("confidence") or "").strip()}
    return rows


def schema_maps():
    sch = json.loads(SCHEMA.read_text(encoding="utf-8"))["signs"]
    w2p, w2m = {}, {}
    for pid, s in sch.items():
        for w in s.get("wells_graphemes", []):
            code = w[1:].zfill(3)
            w2p[code] = pid
            ms = s.get("mahadevan_graphemes", [])
            if ms:
                w2m[code] = ms[0]
    return w2p, w2m


def inventories(coding, codes):
    """Map every code to a label under each inventory of PROTOCOL step 1."""
    w2p, w2m = schema_maps()
    inv = {"W": {}, "V": {}, "P": {}, "M": {}, "B": {}}
    for c in codes:
        row = coding.get(c)
        inv["W"][c] = c
        if row is None:
            for k in ("V", "P", "M", "B"):
                inv[k][c] = "W" + c
            continue
        mods = sorted(m for m in row["mods"] if m != "variant")
        inv["V"][c] = f"{row['base']}|{','.join(mods)}|{row['count']}"
        inv["P"][c] = w2p.get(c, "W" + c)
        inv["M"][c] = w2m.get(c, "W" + c)
        inv["B"][c] = row["base"]
    return inv


def modifier_signature(coding, codes):
    """Group codes by modifier set across bases; strokes and bare bases stay singleton."""
    out = {}
    for c in codes:
        row = coding.get(c)
        if row is None or row["base"] in ("B001", "B031"):
            out[c] = "S" + c
            continue
        mods = sorted(m for m in row["mods"] if m != "variant")
        out[c] = "MOD:" + ",".join(mods) if mods else "S" + c
    return out
