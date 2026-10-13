"""Draw the verification samples of face-image links, make contact sheets, and score them.

Usage (from the repository root):
    python -P experiments/2026-10-13-image-index-and-units/verify.py draw
    python -P experiments/2026-10-13-image-index-and-units/verify.py score

draw: reads run-2026-10-13/images/face-image-links.csv and draws three samples with the
seed '2026-10-13-image-index-and-units' (Amendment 1): S1, 60 links at random; S2, 20 links
with side rule 'ordinal' (objects with several faces) and relation face-side; S3, 15 links
whose join is not a plain file-name key (several-key crops, corrected prefixes, aliases,
name corrections, captions read on volume/page files). Writes verification-sample.csv
(identifiers, side, kind, the face's sign count) and local contact sheets that show the
whole crop with its printed caption. Refuses to redraw if the sample file exists.

score: reads verification-verdicts.csv (one row per sample item, written by the reader
after viewing the sheets) and writes verification-results.json with precision and Wilson
95% intervals per sample and criterion.
"""
import csv
import json
import math
import pathlib
import random
import sys

sys.dont_write_bytecode = True

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from contact_sheet import sheet  # noqa: E402

LINKS = HERE / "run-2026-10-13/images-v1-ordinal-rule/face-image-links.csv"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
SAMPLE = HERE / "verification-sample.csv"
VERDICTS = HERE / "verification-verdicts.csv"
RESULTS = HERE / "verification-results.json"
RAW = ROOT / "data/raw/2026-10-13-image-index-and-units/verify"
SEED = "2026-10-13-image-index-and-units"


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def draw():
    if SAMPLE.exists():
        sys.exit("sample exists; it is drawn once")
    links = list(csv.DictReader(LINKS.open(encoding="utf-8")))
    length = {}
    for line in FACES.open(encoding="utf-8"):
        f = json.loads(line)
        length[f["record_id"]] = f["length"]
    rng = random.Random(SEED)
    s1 = rng.sample(links, 60)
    used = {(l["record_id"], l["file"]) for l in s1}
    pool2 = [l for l in links if l["side_rule"] == "ordinal" and l["relation"] == "face-side" and (l["record_id"], l["file"]) not in used]
    s2 = rng.sample(pool2, 20)
    used |= {(l["record_id"], l["file"]) for l in s2}
    special = lambda l: l["flags"] and any(t in l["flags"] for t in ("several-keys", "prefix_corrected", "alias:", "corrected-by-visual-reading", "caption-read-visually"))
    pool3 = [l for l in links if special(l) and (l["record_id"], l["file"]) not in used]
    s3 = rng.sample(pool3, 15)
    rows = []
    for stratum, lst in (("S1", s1), ("S2", s2), ("S3", s3)):
        for i, l in enumerate(lst, 1):
            rows.append({"sample_id": f"{stratum}-{i:02d}", "stratum": stratum, "record_id": l["record_id"],
                         "object_family_id": l["object_family_id"], "key": l["key"], "file": l["file"],
                         "kind": l["kind"], "sides": l["sides"], "presumed_side": l["presumed_side"],
                         "side_rule": l["side_rule"], "relation": l["relation"], "face_sign_count": length[l["record_id"]],
                         "flags": l["flags"]})
    with SAMPLE.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    RAW.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(rows), 12):
        chunk = rows[i:i + 12]
        labels = [f"{r['sample_id']} {r['key']} {r['sides'] or '-'} {r['kind'][:3]} {r['relation']} n={r['face_sign_count']}" for r in chunk]
        sheet([r["file"] for r in chunk], RAW / f"sheet-{i // 12 + 1:02d}.png", cols=3, cell=520, labels="short", numbers=labels)
    print(len(rows), "items;", (len(rows) + 11) // 12, "sheets in", RAW)


def score():
    sample = {r["sample_id"]: r for r in csv.DictReader(SAMPLE.open(encoding="utf-8"))}
    verdicts = list(csv.DictReader(VERDICTS.open(encoding="utf-8")))
    out = {"criteria": {
        "identity": "the printed caption in the crop names the linked key (or, without a legible caption, the crop is the object named and nothing contradicts it)",
        "kind": "object photograph or impression as stated",
        "side": "the side relation stated in the link holds",
        "full": "identity, kind and side all hold, and for a face-side link the visible text is consistent with the face's recorded sign count"},
        "samples": {}}
    for stratum in ("S1", "S2", "S3"):
        rows = [v for v in verdicts if sample[v["sample_id"]]["stratum"] == stratum]
        res = {"n": len(rows)}
        for crit in ("identity", "kind", "side", "full"):
            judged = [v for v in rows if v[crit] in ("yes", "no")]
            k = sum(1 for v in judged if v[crit] == "yes")
            res[crit] = {"judged": len(judged), "correct": k, "precision": round(k / len(judged), 4) if judged else None,
                         "wilson95": wilson(k, len(judged))}
        res["errors"] = [{"sample_id": v["sample_id"], "file": sample[v["sample_id"]]["file"], "key": sample[v["sample_id"]]["key"],
                          "note": v["note"]} for v in rows if "no" in (v["identity"], v["kind"], v["side"], v["full"])]
        out["samples"][stratum] = res
    RESULTS.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"draw": draw, "score": score}[sys.argv[1]]()
