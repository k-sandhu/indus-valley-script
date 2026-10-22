"""Independent arithmetic checks of the calibration, the frozen reference and the joint rule.

Written separately from birthstar.py and calibrate.py; standard library only.
"""
import csv
from collections import Counter
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RAW = HERE.parents[1] / "data/raw/2026-10-21-birth-star-names/luders-v1"


def chao1(counts):
    s = len(counts)
    f1 = sum(1 for v in counts.values() if v == 1)
    f2 = sum(1 for v in counts.values() if v == 2)
    return s + f1 * (f1 - 1) / (2 * (f2 + 1))


def hnorm(counts):
    n = sum(counts.values())
    h = -sum(v / n * math.log(v / n) for v in counts.values())
    return h / math.log(len(counts))


def main():
    checks = []
    cal = json.loads((HERE / "calibration-v1/calibration.json").read_text(encoding="utf-8"))
    with (RAW / "marking-resolved.csv").open(encoding="utf-8") as f:
        res = list(csv.DictReader(f))
    personal = [r for r in res if r["personal_name"] == "yes"]
    for variant in ("strict", "broad"):
        ast = Counter(r["asterism"] for r in personal if r["asterism"] and (variant == "broad" or r["strength"] == "strict"))
        block = cal["variants"][variant]
        st = block["asterism_elements"]["stats"]
        checks.append((f"{variant}: occurrences", sum(ast.values()) == block["asterism_rows"]))
        checks.append((f"{variant}: share", abs(sum(ast.values()) / len(personal) - block["share"]) < 1e-12))
        checks.append((f"{variant}: distinct", len(ast) == block["distinct_asterisms"]))
        checks.append((f"{variant}: chao1", abs(chao1(ast) - st["chao1"]) < 1e-9))
        checks.append((f"{variant}: normalised entropy", abs(hnorm(ast) - st["normalised_entropy"]) < 1e-9))
        checks.append((f"{variant}: top share", abs(max(ast.values()) / sum(ast.values()) - st["top_share"]) < 1e-12))
    checks.append(("personal denominator 757", len(personal) == 757 == cal["personal_name_rows"]))
    ref = json.loads((HERE / "frozen-reference.json").read_text(encoding="utf-8"))
    inv = json.loads((HERE / "discovery-v1/inventories.json").read_text(encoding="utf-8"))["T0"]
    checks.append(("reference inventory equals discovery T0", sorted(inv) == ref["discovery_T0_inventory"] and len(inv) == 33))
    top4 = sorted(inv, key=lambda k: (-inv[k], k))[:4]
    checks.append(("top four runs", top4 == ref["discovery_T0_top4"] == ["220", "240", "235", "233"]))
    checks.append(("top-four coverage 0.667", abs(sum(inv[k] for k in top4) / sum(inv.values()) - 164 / 246) < 1e-12))
    checks.append(("T0 chao1 38.6", abs(chao1(Counter(inv)) - 38.625) < 1e-9))
    checks.append(("T0 Good-Turing novelty", abs(sum(1 for v in inv.values() if v == 1) / sum(inv.values()) - 10 / 246) < 1e-12))
    checks.append(("broad reference counts", ref["brahmi_asterism_counts"] == cal["variants"]["broad"]["asterism_counts"]))
    t1 = json.loads((HERE / "discovery-v1/inventories.json").read_text(encoding="utf-8"))["T1"]
    checks.append(("T1 chao1 186", abs(chao1(Counter(t1)) - 186.0) < 1e-9 and len(t1) == 60))
    sys.path.insert(0, str(HERE))
    import score_fresh as sf
    def p(p2, p3, p4, p1=False, p5=False):
        return sf.joint({"P2_closure": {"pass": p2}, "P3_brahmi_profile": {"pass": p3}, "P4_stable_dominant_runs": {"pass": p4},
                         "P1_literal_N1": {"pass": p1}, "P5_literal_N3": {"pass": p5}})
    checks.append(("joint rule", (p(False, True, True), p(True, True, True), p(True, True, False), p(True, False, False),
                                  p(True, True, True, True, True), p(False, True, True, True, True)) == (0.005, 0.06, 0.03, 0.01, 0.1, 0.005)))
    out = {"checks": [{"check": c, "pass": bool(ok)} for c, ok in checks], "all_pass": all(ok for _, ok in checks)}
    with (HERE / "verification-v1.json").open("x", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
