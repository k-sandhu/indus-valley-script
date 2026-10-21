"""Independent recomputation of the Mound F population and three frozen statistics.

Written after the read and importing none of the package's modules. It rebuilds the
frames, strata and clock from the confirmation file, the closing-stock shares of the
early and late thirds (P1, P2), the length correlation (P5) and the sign-inventory
statistic (P6), each with its own permutation test within frames (1,999 draws by
default, or the number given after the output path).

    python -P experiments/2026-10-20-harappa-legend-periods/verify_independent.py OUT_JSON [DRAWS]
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
CONFIRMATION = ROOT / "data/raw/2026-10-20-harappa-legend-periods/confirmation-mound-f-vats.jsonl"
STOCK = {"740", "520", "090", "400", "151", "156", "527", "617", "621", "226", "892", "407", "405", "154", "595"}


def midranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5 if sxx > 0 and syy > 0 else 0.0


def permute_within(units, rng):
    groups = defaultdict(list)
    for i, r in enumerate(units):
        groups[r["frame"]].append(i)
    u = [r["u"] for r in units]
    out = list(u)
    for idx in groups.values():
        vals = [u[i] for i in idx]
        rng.shuffle(vals)
        for i, v in zip(idx, vals):
            out[i] = v
    return out


def main():
    out_path = Path(sys.argv[1])
    draws = int(sys.argv[2]) if len(sys.argv) > 2 else 1999
    if out_path.exists():
        raise SystemExit("output exists")
    rows = [json.loads(line) for line in CONFIRMATION.read_text(encoding="utf-8").splitlines() if line.strip()]
    cells = Counter(r["metadata"]["chron_frame_cell"] for r in rows)
    for r in rows:
        c = r["metadata"]["chron_frame_cell"]
        r["frame"] = c if cells[c] >= 15 else "rest"
    sizes = Counter(r["frame"] for r in rows)
    rows = [r for r in rows if sizes[r["frame"]] >= 5]
    ranks = midranks([-r["metadata"]["chron_stratum"] for r in rows])
    for r, k in zip(rows, ranks):
        r["u"] = (k - 0.5) / len(rows)

    def merged(select):
        groups = defaultdict(list)
        for r in rows:
            v = select(r)
            if v is None:
                continue
            clean = r["complete_observed"] and not r["has_blank_space"] and not r["has_unknown_sign"]
            key = (r["frame"], tuple(r["signs_reading_rtl"])) if clean else (r["frame"], r["object_family_id"])
            groups[key].append((r, v))
        out = []
        for key, members in groups.items():
            us = sorted(m[0]["u"] for m in members)
            mid = len(us) // 2
            med = us[mid] if len(us) % 2 else (us[mid - 1] + us[mid]) / 2
            out.append({"frame": key[0], "u": med, "value": members[0][1], "signs": members[0][0]["signs_reading_rtl"]})
        return out

    def closing(r):
        code = r["text_code_visual_ltr"].strip()
        vis = r["signs_visual_ltr"]
        if not r["single_line"] or "/" in code or not code.startswith("+") or not vis or vis[0] == "000":
            return None
        complete = r["complete_observed"] and not r["has_blank_space"]
        if complete and r["length"] < 2:
            return None
        return vis[0]

    def length(r):
        return r["length"] if r["complete_observed"] and not r["has_blank_space"] else None

    close = merged(closing)
    early = [x["value"] in STOCK for x in close if x["u"] < 1 / 3]
    late = [x["value"] in STOCK for x in close if x["u"] >= 2 / 3]
    rng = random.Random(4)

    # P5: within-frame rank of length against u
    lens = merged(length)
    lr = [0.0] * len(lens)
    by_frame = defaultdict(list)
    for i, x in enumerate(lens):
        by_frame[x["frame"]].append(i)
    for idx in by_frame.values():
        rk = midranks([lens[i]["value"] for i in idx])
        for i, k in zip(idx, rk):
            lr[i] = (k - 0.5) / len(idx)
    obs5 = pearson(lr, [x["u"] for x in lens])
    null5 = [pearson(lr, permute_within(lens, rng)) for _ in range(draws)]
    p5 = (1 + sum(abs(v) >= abs(obs5) - 1e-12 for v in null5)) / (draws + 1)

    # P6: inventory over all legends
    allleg = merged(lambda r: True)
    counts = Counter(s for x in allleg for s in set(x["signs"]) - {"000"})
    keep = sorted(s for s, n in counts.items() if n >= 8)

    def inventory(u):
        mean = sum(u) / len(u)
        var = sum((v - mean) ** 2 for v in u) / len(u)
        total = 0.0
        for s in keep:
            us = [v for v, x in zip(u, allleg) if s in x["signs"]]
            total += len(us) * (sum(us) / len(us) - mean) ** 2
        return total / var
    obs6 = inventory([x["u"] for x in allleg])
    null6 = [inventory(permute_within(allleg, rng)) for _ in range(draws)]
    p6 = (1 + sum(v >= obs6 - 1e-12 for v in null6)) / (draws + 1)

    record = {"seals_in_frames": len(rows), "frames": dict(sorted(Counter(r["frame"] for r in rows).items())),
              "strata": dict(sorted(Counter(r["metadata"]["chron_stratum"] for r in rows).items())),
              "closing_units": len(close), "early_units": len(early), "late_units": len(late),
              "early_stock_share": sum(early) / len(early), "late_stock_share": sum(late) / len(late),
              "late_minus_early": sum(late) / len(late) - sum(early) / len(early),
              "P5_length_units": len(lens), "P5_r": obs5, "P5_p_two_sided": p5, "draws": draws,
              "mean_length_by_third": [sum(x["value"] for x in lens if lo <= x["u"] < hi) / max(1, sum(lo <= x["u"] < hi for x in lens))
                                       for lo, hi in ((0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.01))],
              "P6_units": len(allleg), "P6_signs": len(keep), "P6_statistic": obs6, "P6_p": p6}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1))


if __name__ == "__main__":
    main()
