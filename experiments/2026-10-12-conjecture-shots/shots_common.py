"""Shared split and sealed loader for the October 12 conjecture shots.

The corpus is divided once into a discovery half and a confirmation half. A shot may
explore the discovery half freely. It may read the confirmation half only after its
PREDICTIONS.md exists and its SHA-256 is recorded in PREDICTIONS.sha256; every
confirmation read is appended to that shot's confirmation-access.jsonl. The guard is a
procedural record kept by the code, not a cryptographic barrier.
"""
from pathlib import Path
import collections
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
PACKAGE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-12-conjecture-shots"
SEED = "2026-10-12-conjecture-shots"
EXPECTED_FACES_SHA256 = None  # filled from split-summary.json after the split is written


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_faces():
    with open(FACES, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


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


def components(rows):
    """Close object families over CISI aliases and identical complete texts.

    Identical complete texts of length three or more are joined for every object type.
    Identical two-sign texts are joined among seals only: on Harappa tablets they chain
    multi-faced objects into one 500-family component, which would put most tablets in
    one half. Two-sign tablet duplicates can therefore fall in both halves.
    """
    uf = UnionFind()
    for r in rows:
        fam = "F:" + r["object_family_id"]
        uf.find(fam)
        cisi = r.get("source_cisi")
        if cisi and cisi not in ("-", ""):
            uf.union(fam, "C:" + cisi)
        if r["complete_observed"] and not r["has_unknown_sign"]:
            text = "T:" + "-".join(r["signs_reading_rtl"])
            if r["length"] >= 3 or (r["length"] == 2 and r["object_type"].startswith("SEAL")):
                uf.union(fam, text)
    comp_of_family = {}
    members = collections.defaultdict(set)
    for r in rows:
        c = uf.find("F:" + r["object_family_id"])
        members[c].add(r["object_family_id"])
    for c, fams in members.items():
        key = min(fams, key=lambda s: (len(s), s))
        half = int(hashlib.sha256(f"{SEED}:{key}".encode()).hexdigest(), 16) % 2
        for fam in fams:
            comp_of_family[fam] = {"component": key, "half": "discovery" if half == 0 else "confirmation"}
    return comp_of_family


def write_split():
    rows = read_faces()
    comp = components(rows)
    RAW.mkdir(parents=True, exist_ok=True)
    split_path = RAW / "split.json"
    if split_path.exists():
        raise SystemExit("split.json exists; the split is frozen")
    split_path.write_text(json.dumps(comp, indent=1, sort_keys=True), encoding="utf-8")
    by = collections.Counter()
    for r in rows:
        c = comp[r["object_family_id"]]
        by[(c["half"], r["site"] if r["site"] in ("Mohenjo-daro", "Harappa", "Dholavira", "Kalibangan", "Lothal", "Chanhu-daro") else "other",
            r["object_type"].split(":")[0])] += 1
    fam_half = collections.Counter(v["half"] for v in comp.values())
    comp_sizes = collections.Counter(v["component"] for v in comp.values())
    summary = {
        "seed": SEED,
        "faces_sha256": sha256(FACES),
        "split_sha256": sha256(split_path),
        "faces": len(rows),
        "families_by_half": dict(fam_half),
        "components": len(comp_sizes),
        "largest_components_families": sorted(comp_sizes.values(), reverse=True)[:10],
        "faces_by_half_site_type": [
            {"half": h, "site": s, "type": t, "faces": n} for (h, s, t), n in sorted(by.items())
        ],
        "rule": components.__doc__.strip(),
    }
    (PACKAGE / "split-summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


def load_split():
    return json.loads((RAW / "split.json").read_text(encoding="utf-8"))


def load_half(half, shot_dir=None, strip=()):
    """Return faces of one half with 'half' and 'component' added.

    Confirmation reads require shot_dir with a frozen PREDICTIONS.md. Fields named in
    strip are removed from each face and from its metadata, for shots that withhold
    variables from construction.
    """
    summary = json.loads((PACKAGE / "split-summary.json").read_text(encoding="utf-8"))
    if sha256(FACES) != summary["faces_sha256"] or sha256(RAW / "split.json") != summary["split_sha256"]:
        raise SystemExit("input or split hash changed")
    if half not in ("discovery", "confirmation"):
        raise ValueError(half)
    if half == "confirmation":
        if shot_dir is None:
            raise SystemExit("confirmation reads need a shot directory")
        shot_dir = Path(shot_dir)
        pred, rec = shot_dir / "PREDICTIONS.md", shot_dir / "PREDICTIONS.sha256"
        if not pred.exists() or not rec.exists():
            raise SystemExit("freeze PREDICTIONS.md and PREDICTIONS.sha256 before reading the confirmation half")
        recorded = rec.read_text(encoding="utf-8").split()[0]
        if recorded != sha256(pred):
            raise SystemExit("PREDICTIONS.md changed after freezing; write a dated amendment instead")
        with open(shot_dir / "confirmation-access.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                 "predictions_sha256": recorded}) + "\n")
    split = load_split()
    out = []
    for r in read_faces():
        c = split[r["object_family_id"]]
        if c["half"] != half:
            continue
        r = dict(r, half=c["half"], component=c["component"])
        if strip:
            r["metadata"] = {k: v for k, v in r["metadata"].items() if k not in strip}
            for k in strip:
                r.pop(k, None)
        out.append(r)
    return out


if __name__ == "__main__":
    s = write_split()
    print(json.dumps({k: s[k] for k in ("faces", "families_by_half", "components", "largest_components_families")}, indent=1))
