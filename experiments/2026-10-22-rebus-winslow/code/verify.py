"""Independent check of the frozen Winslow result.

The segmentation, length-free rule, stem rule and sandhi bases come from
experiments/2026-10-21-rebus-base-rate/code/verify.py, which reimplements them
without rebus.py. This script uses those functions, its own compound index,
replacement pools and shared-member search, and the members recorded in the
Winslow table, and compares each number with results-v1.

    python experiments/2026-10-22-rebus-winslow/code/verify.py RESULTS_DIR OUT_JSON
"""

import bisect
import importlib.util
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE_VERIFY = ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "code" / "verify.py"
spec = importlib.util.spec_from_file_location("base_verify", BASE_VERIFY)
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)

TABLE = ROOT / "data" / "raw" / "2026-10-22-rebus-winslow" / "derived-v1" / "winslow-entries.jsonl"


def main(results_dir, out_path):
    results_dir, out_path = Path(results_dir).resolve(), Path(out_path).resolve()
    if out_path.exists():
        print("refusing to overwrite", out_path)
        return 1
    inter = json.loads((results_dir / "interlocks.json").read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in TABLE.open(encoding="utf-8")]
    dedr = [json.loads(l) for l in (bv.DER / "dedr-entries.jsonl").open(encoding="utf-8")]
    checks = {}

    comps = [(r["members"][0], r["members"][1]) for r in rows if len(r["members"]) == 2]
    first, last = {}, {}
    for k, (a, b) in enumerate(comps):
        for st in {bv.t1(x) for x in bv.bases(a)}:
            first.setdefault(st, []).append(k)
        last.setdefault(bv.t1(b), []).append(k)

    def A(w):
        return [comps[k] for k in first.get(bv.t1(w), [])]

    def B(w):
        return [comps[k] for k in last.get(bv.t1(w), [])]

    def shared(w1, w2):
        excl = {bv.t0(x) for w in (w1, w2) for x in bv.bases(w)}
        na = {bv.t0(x[1]) for x in A(w1)}
        nb = {bv.t0(y) for x in B(w2) for y in bv.bases(x[0])}
        return (na & nb) - excl

    checks["two_member_compounds"] = {"verify": len(comps), "frozen": inter["lexicon"]["two_member_compounds"]}
    checks["A_B_sizes"] = {"verify": [len(A("muruku")), len(B("mīṉ"))], "frozen": [inter["real"]["A_size"], inter["real"]["B_size"]]}
    checks["real_I1_T0s"] = {"verify": sorted("".join(x) for x in shared("muruku", "mīṉ")),
                             "frozen": sorted(inter["real"]["I1_T0s"]["shared"].keys())}

    dedr_t0 = set()
    for r in dedr:
        if len(set(r["subgroups"])) >= 2:
            for g in r["groups"]:
                if g["lang"] == "Ta":
                    dedr_t0 |= {bv.t0(f) for f in g["forms"]}
    toks = []
    for p in sorted(bv.SANGAM.glob("pmuni*.html")):
        text = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
        toks.extend(re.findall(r"[஀-௿]+", text))
    toks.sort()
    signs = set(chr(c) for c in range(0x0BBE, 0x0BCE)) | {"ௗ"}

    def freq(head):
        h = re.sub(r"-.*$", "", head)
        while h and h[-1] in signs:
            h = h[:-1]
        if not h:
            return 0
        return bisect.bisect_left(toks, h + "\U0010ffff") - bisect.bisect_left(toks, h)

    cands = {}
    for r in rows:
        if len(r["members"]) != 1 or r["star"] or (r["pos"] or "") != "n" or r["verb"]:
            continue
        if bv.t0(r["translit"]) not in dedr_t0:
            continue
        st = bv.t1(r["translit"])
        if st not in cands:
            cands[st] = (r["translit"], len(first.get(st, [])), len(last.get(st, [])), freq(r["head"]))

    def real_feat(word):
        r = next(x for x in rows if x["translit"] == word and len(x["members"]) == 1)
        return (word, len(first.get(bv.t1(word), [])), len(last.get(bv.t1(word), [])), freq(r["head"]))

    def pool(word, which, k=50):
        rw = real_feat(word)
        items = [c for st, c in cands.items() if st != bv.t1(word)]
        lp = [math.log1p(c[which]) for c in items]
        lf = [math.log1p(c[3]) for c in items]

        def sd(v):
            m = sum(v) / len(v)
            return math.sqrt(sum((x - m) ** 2 for x in v) / len(v)) or 1.0
        sp, sf = sd(lp), sd(lf)
        d = [math.sqrt(((a - math.log1p(rw[which])) / sp) ** 2 + ((b - math.log1p(rw[3])) / sf) ** 2) for a, b in zip(lp, lf)]
        order = sorted(range(len(items)), key=lambda i: (d[i], items[i][0]))
        return [items[i] for i in order[:k]]

    checks["real_features"] = {"verify": {w: real_feat(w)[1:] for w in ("muruku", "mīṉ")},
                               "frozen": {w: [inter["real_features"][w][k] for k in ("prod_first", "prod_last", "freq")]
                                          for w in ("muruku", "mīṉ")}}
    p1, p2 = pool("muruku", 1), pool("mīṉ", 2)
    checks["pool_W1"] = {"verify_equals_frozen": [c[0] for c in p1] == [x["word"] for x in inter["replacement_pools"]["muruku"]],
                         "first_member_compounds_of_pool_words": sorted({c[1] for c in p1})}
    checks["pool_W2"] = {"verify_equals_frozen": [c[0] for c in p2] == [x["word"] for x in inter["replacement_pools"]["mīṉ"]]}
    hits = sum(bool(shared(a[0], b[0])) for a in p1 for b in p2)
    checks["I1_null_T0s_K50"] = {"verify": hits / (len(p1) * len(p2)), "frozen": inter["null"]["I1_T0s"]["K50"]["rate"]}

    def agree(c):
        if "verify_equals_frozen" in c:
            return c["verify_equals_frozen"]
        v, f = c["verify"], c["frozen"]
        if isinstance(v, dict):
            return {k: list(x) for k, x in v.items()} == {k: list(x) for k, x in f.items()}
        return v == f
    for c in checks.values():
        c["agree"] = agree(c)
    out = {"schema_version": "1.0", "task": "rebus-winslow/verification", "synthetic": False,
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "results": str((results_dir / "interlocks.json").relative_to(ROOT)).replace("\\", "/"),
           "base_verify_functions": {"path": str(BASE_VERIFY.relative_to(ROOT)).replace("\\", "/")},
           "checks": checks, "all_agree": all(c["agree"] for c in checks.values())}
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: c["agree"] for k, c in checks.items()} | {"all_agree": out["all_agree"]}))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(*sys.argv[1:]))
