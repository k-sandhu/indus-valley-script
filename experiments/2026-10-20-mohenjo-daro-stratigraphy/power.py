"""Planted-effect power for the frozen predictions at the shape of Marshall's areas.

Each synthetic population has Marshall's depth strata, their sizes and their tied depth
values, taken from the tracked Mackay-Marshall join table and the export's section field;
no Marshall legend is read. Legends are drawn with replacement from Mackay's DK seals.
Effects are planted on the true height, and then a fraction of seals in every stratum
exchange heights at random, which models residual and intrusive finds.

    python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/power.py FROZEN_JSON OUT_JSON
"""
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import copy
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import strat_stats as S  # noqa: E402
import score  # noqa: E402

ROOT = PACKAGE.parents[1]
DISCOVERY = ROOT / "data/raw/2026-10-20-mohenjo-daro-stratigraphy/discovery-mackay1938.jsonl"
JOIN = ROOT / "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
DRAWS = 999
G = {}


def marshall_frame():
    """Strata and depth values of Marshall's seals: area and depth from the join table,
    section and object type from the export. No legend field is read."""
    sections, types = {}, {}
    for line in FACES.read_text(encoding="utf-8").splitlines():
        f = json.loads(line)
        sections.setdefault(f["object_family_id"], f["metadata"].get("area-section", ""))
        types.setdefault(f["object_family_id"], f["object_type"])
    fam_rows = defaultdict(list)
    for r in csv.DictReader(JOIN.open(encoding="utf-8")):
        if r["source"] == "marshall1931":
            fam_rows[r["lipi_family_id"]].append(r)
    frame = []
    for fam, rows in fam_rows.items():
        depths = set()
        for r in rows:
            m = re.fullmatch(r"(\d+) ft (\d+) in", r["level_ft"].strip())
            depths.add(int(m.group(1)) + int(m.group(2)) / 12 if m else None)
        if len(depths) != 1 or None in depths or not types[fam].startswith("SEAL"):
            continue
        frame.append({"object_family_id": fam, "object_type": types[fam],
                      "metadata": {"strat_source": "marshall1931", "strat_area": rows[0]["area"],
                                   "strat_section": sections[fam], "strat_height_ft": -depths.pop()}})
    kept, sizes = score.assign_strata(frame)
    strata = defaultdict(list)
    for o in kept:
        strata[o["metadata"]["strat_stratum"]].append(o["metadata"]["strat_height_ft"])
    return dict(strata), sizes


def init(frozen_path):
    rows = [json.loads(line) for line in DISCOVERY.read_text(encoding="utf-8").splitlines() if line.strip()]
    pool, _ = score.prepare(rows, areas={"DK"})
    G["pool"] = pool
    G["frozen"] = json.loads(Path(frozen_path).read_text(encoding="utf-8"))
    G["strata"], _ = marshall_frame()
    opening = Counter(o["text"]["opening"] for o in pool if o["text"]["opening"] and o["text"]["length"] and o["text"]["length"] >= 2)
    G["top_openings"] = [s for s, _ in opening.most_common(10)]
    G["opening_weights"] = dict(opening)
    stock = set(G["frozen"]["closing_stock"])
    other = Counter(o["text"]["closing"] for o in pool if o["text"]["closing"] and o["text"]["closing"] not in stock)
    G["other_closings"] = (list(other), np.array(list(other.values()), float) / sum(other.values()))
    classes = S.load_variant_classes()
    G["classes"] = classes
    counts = defaultdict(Counter)
    for o in pool:
        for s in o["text"]["signs"]:
            if s in classes:
                counts[classes[s]][s] += 1
    G["variant_pairs"] = {c: [s for s, _ in v.most_common(2)] for c, v in counts.items() if len(v) >= 2 and v.most_common(2)[1][1] >= 3}
    halves = np.random.default_rng(5).permutation(len(pool))
    G["half_a"] = [pool[i] for i in halves[: len(pool) // 2]]
    G["half_b"] = [pool[i] for i in halves[len(pool) // 2:]]
    sys.path.insert(0, str(PACKAGE))
    import explore_mackay
    G["scores_a"] = explore_mackay.nonfinal_scores(S.units(G["half_a"], "length", min_length=2))


def synthetic(rng, source=None, keep_heights=False):
    """One Marshall-shaped population. With keep_heights, Mackay seals keep their own
    height rank, re-ranked inside each synthetic stratum."""
    pool = source or G["pool"]
    objects = []
    for name, heights in G["strata"].items():
        picks = rng.integers(0, len(pool), len(heights))
        hs = rng.permutation(heights)
        for k, (i, h) in enumerate(zip(picks, hs)):
            o = pool[i]
            new = {"object_family_id": f"syn-{name}-{k}", "object_type": o["object_type"],
                   "text": copy.deepcopy(o["text"]),
                   "metadata": {"strat_source": "marshall1931", "strat_stratum": name,
                                "strat_height_ft": float(o["u"]) if keep_heights else float(h)}}
            objects.append(new)
    return S.add_height_rank(objects, stratum_key="strat_stratum")


def mix(objects, fraction, rng):
    """Exchange heights among a random fraction of seals in each stratum."""
    if fraction <= 0:
        return objects
    groups = defaultdict(list)
    for o in objects:
        groups[o["stratum"]].append(o)
    for members in groups.values():
        k = int(round(fraction * len(members)))
        if k < 2:
            continue
        chosen = rng.choice(len(members), k, replace=False)
        heights = [members[i]["metadata"]["strat_height_ft"] for i in chosen]
        for i, h in zip(chosen, rng.permutation(heights)):
            members[i]["metadata"]["strat_height_ft"] = h
    return S.add_height_rank(objects, stratum_key="strat_stratum")


def set_closing(t, sign):
    t["signs"][-1] = sign
    t["closing"] = sign
    if len(t["signs"]) >= 2 and "000" not in t["signs"][-2:]:
        t["closing_pair"] = "-".join(t["signs"][-2:])


def plant(objects, kind, size, rng):
    if kind == "opening":
        tops = list(G["top_openings"])
        rng.shuffle(tops)
        early, late = tops[:5], tops[5:]
        for o in objects:
            t = o["text"]
            if t["opening"] is None or t["length"] is None or t["length"] < 2 or rng.random() >= size:
                continue
            group = early if o["u"] < 0.5 else late
            w = np.array([G["opening_weights"][s] for s in group], float)
            s = group[rng.choice(len(group), p=w / w.sum())]
            t["signs"][0] = s
            t["opening"] = s
    elif kind == "length":
        lam = size / (2 / 3)
        for o in objects:
            t = o["text"]
            if t["length"] is None:
                continue
            extra = int(lam * o["u"]) + (rng.random() < (lam * o["u"]) % 1)
            if extra:
                t["signs"] = t["signs"][:1] + ["999"] * extra + t["signs"][1:]
                t["length"] += extra
    elif kind == "variant":
        flip = rng.random() < 0.5
        for o in objects:
            t = o["text"]
            for j, s in enumerate(t["signs"]):
                c = G["classes"].get(s)
                if c in G["variant_pairs"] and rng.random() < size:
                    a, b = G["variant_pairs"][c]
                    low, high = (a, b) if flip else (b, a)
                    t["signs"][j] = low if o["u"] < 0.5 else high
    elif kind == "closing":
        stock = set(G["frozen"]["closing_stock"])
        names, p = G["other_closings"]
        q = size / 0.73
        for o in objects:
            t = o["text"]
            if t["closing"] in stock and o["u"] < 0.5 and rng.random() < q:
                set_closing(t, names[rng.choice(len(names), p=p)])
    elif kind == "formula":
        formulae = set(G["frozen"]["closing_formulae"])
        q = size / 0.36
        for o in objects:
            t = o["text"]
            if t["closing_pair"] in formulae and o["u"] < 0.5 and rng.random() < q:
                t["signs"][-2] = "999"
                t["closing_pair"] = "999-" + t["signs"][-1]
    return objects


def opening_js_excess(objects, rng, draws=200):
    """Jensen-Shannon divergence (bits) of opening signs between the bottom and top
    thirds, minus its mean under height permutation: the size of a planted drift on the
    scale of the Harappa 3B-3C comparison (excess 0.033 bits)."""
    rows = S.units(objects, "opening")
    vals = [r["value"] for r in rows]
    u = np.array([r["u"] for r in rows])
    index = S.strata_index(rows)

    def js(v):
        lo, hi = Counter(x for x, y in zip(vals, v) if y < 1 / 3), Counter(x for x, y in zip(vals, v) if y >= 2 / 3)
        keys = sorted(set(lo) | set(hi))
        a = np.array([lo[k] for k in keys], float)
        b = np.array([hi[k] for k in keys], float)
        a, b = a / a.sum(), b / b.sum()
        m = (a + b) / 2

        def kl(p, q):
            nz = p > 0
            return float(np.sum(p[nz] * np.log2(p[nz] / q[nz])))
        return 0.5 * kl(a, m) + 0.5 * kl(b, m)
    obs = js(u)
    null = [js(S.permuted_u(u, index, rng)) for _ in range(draws)]
    return obs - float(np.mean(null))


def run_one(task):
    name, kind, size, fraction, only, rep = task
    rng = np.random.default_rng([20261020, rep, int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)])
    frozen = G["frozen"]
    if kind == "mackay":
        objects = synthetic(rng, keep_heights=True)
    elif kind == "mackay_transfer":
        objects = synthetic(rng, source=G["half_b"], keep_heights=True)
        frozen = dict(frozen, nonfinal_scores=G["scores_a"])
    else:
        objects = plant(synthetic(rng), kind, size, rng)
    objects = mix(objects, fraction, rng)
    res = score.score_predictions(objects, frozen, draws=DRAWS, boot=DRAWS, seed=int(rng.integers(1e9)), influence=False, only=set(only))
    out = {k: v["outcome"] for k, v in res.items()}
    if kind == "opening" and rep < 40:
        out["js_excess"] = opening_js_excess(objects, rng)
    return name, out


def main():
    frozen_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    if out_path.exists():
        raise SystemExit("output exists")
    init(frozen_path)
    strata, sizes = G["strata"], None
    _, sizes = marshall_frame()
    all_p = ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9")
    scenarios = [("null", "none", 0, 0, all_p, 300)]
    for f in (0, 0.25, 0.5):
        for rho in (0.15, 0.25, 0.35):
            scenarios.append((f"opening rho={rho} mix={f}", "opening", rho, f, ("P4", "P5"), 200))
        for d in (0.3, 0.5, 0.8):
            scenarios.append((f"length diff={d} mix={f}", "length", d, f, ("P7",), 200))
        for rho in (0.25, 0.5):
            scenarios.append((f"variant rho={rho} mix={f}", "variant", rho, f, ("P6",), 200))
    for d in (0.1, 0.2, 0.3):
        scenarios.append((f"closing stock diff={d}", "closing", d, 0, ("P1", "P2"), 200))
    scenarios.append(("closing formulae diff=0.2", "formula", 0.2, 0, ("P3",), 200))
    for f in (0, 0.25):
        scenarios.append((f"mackay heights mix={f}", "mackay", 0, f, ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P9"), 200))
        scenarios.append((f"mackay transfer half-B mix={f}", "mackay_transfer", 0, f, ("P8",), 200))
    tasks = [(n, k, s, f, o, rep) for n, k, s, f, o, reps in scenarios for rep in range(reps)]
    results = defaultdict(list)
    with ProcessPoolExecutor(max_workers=16, initializer=init, initargs=(str(frozen_path),)) as ex:
        for name, out in ex.map(run_one, tasks, chunksize=4):
            results[name].append(out)
    summary = {}
    for n, k, s, f, o, reps in scenarios:
        rs = results[n]
        entry = {"kind": k, "size": s, "mix_fraction": f, "replicates": len(rs)}
        for p in o:
            outcomes = Counter(r[p] for r in rs)
            entry[p] = {"pass_rate": outcomes["pass"] / len(rs), "outcomes": dict(outcomes)}
        js = [r["js_excess"] for r in rs if "js_excess" in r]
        if js:
            entry["opening_js_excess_bits_mean"] = float(np.mean(js))
        summary[n] = entry
    record = {"strata_seals_with_depth": sizes, "draws": DRAWS,
              "frozen_parameters_sha256": hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
              "scenarios": summary,
              "notes": {"null": "no planted effect; pass rates of P1-P3 are equivalence power under true fixity, of P4-P9 the false-positive rate",
                        "opening": "rho = share of legends whose opening is redrawn from five of the ten commonest Mackay openings by true height (below or above the median)",
                        "length": "size = expected difference in mean legend length between top and bottom thirds, in signs",
                        "variant": "rho = probability that a token of a two-code variant class takes the low or high code by true height",
                        "closing": "size = expected top-third minus bottom-third difference in closing-stock share; P1 should rarely pass at 0.2 and above",
                        "mackay": "Mackay seals with their own heights, re-ranked in Marshall-shaped strata: power if Marshall's areas repeat Mackay's DK-G sequence",
                        "mix": "fraction of seals per stratum whose heights are exchanged at random after planting (residual and intrusive finds)"}}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({n: {p: v[p]["pass_rate"] for p in v if p.startswith("P")} for n, v in summary.items()}, indent=1))


if __name__ == "__main__":
    main()
