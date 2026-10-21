"""Planted-effect power for the frozen predictions at the shape of Vats's Mound F.

Each synthetic population has the Mound F seal families' frame cells and strata, read
from the export's area-section and phase fields only (no legend, format or motif of a
Mound F seal is read). Every family receives the legend and format of a seal drawn with
replacement from the Harappa pool: every Harappa seal outside the confirmation
population, damaged legends included, so that the share of legends readable at each
position follows the pool. Effects are planted by stratum order, and then a fraction of
the seals in each frame exchange strata at random, which models residual, intrusive and
misassigned finds.

Two further scenarios ask what the tests would see if Mound F repeated an association
already observed: the discovery seals keep their own period rank, and Mackay's DK-G
seals keep their own height rank, each resampled into Mound F's shape.

    python -P experiments/2026-10-20-harappa-legend-periods/power.py FROZEN_JSON OUT_JSON [--quick]
"""
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import copy
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import period_stats as P  # noqa: E402
from period_stats import S  # noqa: E402
import period_score as Q  # noqa: E402
import build_inputs as B  # noqa: E402

ROOT = PACKAGE.parents[1]
DISCOVERY = ROOT / "data/raw/2026-10-20-harappa-legend-periods/discovery-harappa-labelled.jsonl"
MACKAY = ROOT / "data/raw/2026-10-20-mohenjo-daro-stratigraphy/discovery-mackay1938.jsonl"
DRAWS = 999
G = {}


def mound_f_frame():
    """(family, frame cell, stratum) for every Mound F seal family with a Vats stratum,
    from the export's metadata. Only area-section, phase, time and the CISI number are
    used, through build_inputs.chronology."""
    fam = defaultdict(list)
    for line in B.FACES.read_text(encoding="utf-8").splitlines():
        f = json.loads(line)
        if f["site"] == "Harappa" and f["object_type"].startswith("SEAL"):
            fam[f["object_family_id"]].append(f)
    frame = []
    for k, members in fam.items():
        chron = B.chronology(members[0])
        if chron["chron_mound"] == "F" and chron["chron_source"] == "vats_stratum":
            frame.append((k, chron))
    return sorted(frame, key=lambda x: int(x[0]))


def init(frozen_path):
    sys.path.insert(0, str(PACKAGE))
    import explore_discovery
    G["frozen"] = json.loads(Path(frozen_path).read_text(encoding="utf-8"))
    G["frame"] = mound_f_frame()
    G["pool"] = explore_discovery.harappa_pool()
    disc, _ = P.prepare(P.read_rows(DISCOVERY), "discovery")
    G["discovery"] = disc
    mackay = []
    for r in P.read_rows(MACKAY):
        m = r["metadata"]
        if r["object_type"].startswith("SEAL") and m.get("strat_area") == "DK" and m.get("strat_height_ft") is not None:
            o = dict(r)
            o["text"] = P.edge_text_fields(r)
            mackay.append(o)
    ranks = S.average_ranks([o["metadata"]["strat_height_ft"] for o in mackay])
    for o, rk in zip(mackay, ranks):
        o["u"] = (rk - 0.5) / len(mackay)
    G["mackay"] = mackay
    pool = G["pool"]
    opening = Counter(o["text"]["opening"] for o in pool if o["text"]["opening"] and not (o["text"]["length"] is not None and o["text"]["length"] < 2))
    G["top_openings"] = [s for s, _ in opening.most_common(10)]
    G["opening_weights"] = dict(opening)
    stock = set(G["frozen"]["closing_stock"])
    closing = Counter(o["text"]["closing"] for o in pool if o["text"]["closing"])
    G["stock_closings"] = [s for s, _ in closing.most_common() if s in stock][:6]
    G["closing_weights"] = dict(closing)
    other = Counter(o["text"]["closing"] for o in pool if o["text"]["closing"] and o["text"]["closing"] not in stock)
    G["other_closings"] = (list(other), np.array(list(other.values()), float) / sum(other.values()))
    nonfinal = Counter(s for o in pool for s in o["text"]["signs"][:-1] if s != "000")
    G["top_nonfinal"] = [s for s, _ in nonfinal.most_common(20)]
    G["nonfinal_weights"] = dict(nonfinal)
    classes = S.load_variant_classes()
    G["classes"] = classes
    counts = defaultdict(Counter)
    for o in pool:
        for s in o["text"]["signs"]:
            if s in classes:
                counts[classes[s]][s] += 1
    G["variant_pairs"] = {c: [s for s, _ in v.most_common(2)] for c, v in counts.items() if len(v) >= 2 and v.most_common(2)[1][1] >= 3}
    G["stock_share_pool"] = float(np.mean([o["text"]["closing"] in stock for o in pool if o["text"]["closing"] and not (o["text"]["length"] is not None and o["text"]["length"] < 2)]))


def synthetic(rng, source=None, keep_u=False):
    """One Mound F-shaped population. With keep_u, the drawn seals keep their own rank
    in their source sequence and are placed at the Mound F stratum of matching rank."""
    pool = source or G["pool"]
    objects = []
    for k, (fam, chron) in enumerate(G["frame"]):
        o = pool[rng.integers(0, len(pool))]
        new = {"object_family_id": f"syn-{k}", "object_type": o["object_type"], "symbol": o.get("symbol"),
               "text": copy.deepcopy(o["text"]), "metadata": dict(chron), "source_u": o.get("u")}
        objects.append(new)
    objects, _ = P.confirmation_frames(objects)
    P.add_clock(objects, "mound")
    if keep_u:
        # reassign strata within each frame so that seals with higher source rank sit higher
        groups = defaultdict(list)
        for o in objects:
            groups[o["stratum"]].append(o)
        for members in groups.values():
            strata = sorted(o["metadata"]["chron_stratum"] for o in members)[::-1]  # oldest first
            ranked = sorted(members, key=lambda o: (o["source_u"], rng.random()))
            for o, st in zip(ranked, strata):
                o["metadata"]["chron_stratum"] = st
        P.add_clock(objects, "mound")
    return objects


def mix(objects, fraction, rng):
    """Exchange strata among a random fraction of the seals in each frame."""
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
        strata = [members[i]["metadata"]["chron_stratum"] for i in chosen]
        for i, st in zip(chosen, rng.permutation(strata)):
            members[i]["metadata"]["chron_stratum"] = st
    return P.add_clock(objects, "mound")


def set_closing(t, sign):
    t["signs"][-1] = sign
    t["closing"] = sign
    if len(t["signs"]) >= 2 and "000" not in t["signs"][-2:]:
        t["closing_pair"] = "-".join(t["signs"][-2:])


def weighted(group, weights, rng):
    w = np.array([weights[s] for s in group], float)
    return group[rng.choice(len(group), p=w / w.sum())]


def plant(objects, kind, size, rng):
    if kind == "opening":
        tops = list(G["top_openings"])
        rng.shuffle(tops)
        early, late = tops[:5], tops[5:]
        for o in objects:
            t = o["text"]
            if t["opening"] is None or (t["length"] is not None and t["length"] < 2) or rng.random() >= size:
                continue
            s = weighted(early if o["u"] < 0.5 else late, G["opening_weights"], rng)
            t["signs"][0] = s
            t["opening"] = s
    elif kind == "closing_identity":
        tops = list(G["stock_closings"])
        rng.shuffle(tops)
        early, late = tops[:3], tops[3:]
        for o in objects:
            t = o["text"]
            if t["closing"] is None or t["closing"] not in set(G["frozen"]["closing_stock"]) or rng.random() >= size:
                continue
            set_closing(t, weighted(early if o["u"] < 0.5 else late, G["closing_weights"], rng))
    elif kind == "closing":
        stock = set(G["frozen"]["closing_stock"])
        names, p = G["other_closings"]
        q = size / G["stock_share_pool"]
        for o in objects:
            t = o["text"]
            if t["closing"] in stock and o["u"] < 0.5 and rng.random() < q:
                set_closing(t, names[rng.choice(len(names), p=p)])
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
    elif kind == "interior":
        tops = list(G["top_nonfinal"])
        rng.shuffle(tops)
        early, late = tops[:5], tops[5:10]
        for o in objects:
            t = o["text"]
            slots = [j for j in range(1, len(t["signs"]) - 1) if t["signs"][j] != "000"]
            if not slots or rng.random() >= size:
                continue
            j = slots[rng.integers(0, len(slots))]
            t["signs"][j] = weighted(early if o["u"] < 0.5 else late, G["nonfinal_weights"], rng)
    elif kind == "format":
        low, high = size
        for o in objects:
            o["object_type"] = "SEAL:R" if rng.random() < low + (high - low) * o["u"] else "SEAL:S"
    return objects


def raw(res):
    out = {}
    for k, v in res.items():
        out[k] = {"outcome": v.get("outcome"), "p": v.get("p"), "observed": v.get("observed"),
                  "interval90": v.get("interval90"), "interval95": v.get("interval95"), "perm_p": v.get("perm_p"),
                  "early_share": v.get("early_share"), "units": v.get("units") or v.get("early_units")}
    return out


def run_one(task):
    name, kind, size, fraction, only, rep, overrides = task
    rng = np.random.default_rng([20261021, rep, int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)])
    frozen = dict(G["frozen"], **(overrides or {}))
    if kind == "discovery":
        objects = synthetic(rng, source=G["discovery"], keep_u=True)
    elif kind == "mackay":
        objects = synthetic(rng, source=G["mackay"], keep_u=True)
    else:
        objects = plant(synthetic(rng), kind, size, rng)
    objects = mix(objects, fraction, rng)
    res = Q.score_predictions(objects, frozen, draws=DRAWS, boot=DRAWS, seed=int(rng.integers(1e9)), influence=False, only=set(only))
    return name, raw(res)


def scenarios(quick):
    all_p = ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "PC")
    drift_p = ("P3", "P4", "P5", "P6", "P7", "PC")
    if quick:
        out = [("null fixity", "none", 0, 0, ("P1", "P2"), 300, None)]
        for d in (0.1, 0.2, 0.3):
            out.append((f"closing stock diff={d}", "closing", d, 0, ("P1",), 150, None))
        for k in (3, 4, 5):
            for inv in (6, 8):
                o = {"min_category": k, "inventory_min_units": inv}
                out.append((f"null k={k} inv={inv}", "none", 0, 0, ("P3", "P6", "P7"), 200, o))
                out.append((f"opening rho=0.25 k={k} inv={inv}", "opening", 0.25, 0, ("P3", "P6"), 150, o))
                out.append((f"closing identity rho=0.5 k={k} inv={inv}", "closing_identity", 0.5, 0, ("P7",), 150, o))
                out.append((f"interior rho=0.5 k={k} inv={inv}", "interior", 0.5, 0, ("P6",), 150, o))
        return out
    out = [("null", "none", 0, 0, all_p, 400, None)]
    for d in (0.1, 0.2, 0.3):
        out.append((f"closing stock diff={d}", "closing", d, 0, ("P1", "P2"), 200, None))
    for f in (0, 0.25, 0.5):
        for rho in (0.15, 0.25, 0.35):
            out.append((f"opening rho={rho} mix={f}", "opening", rho, f, ("P3", "P6"), 200, None))
    for f in (0, 0.25):
        for rho in (0.25, 0.5):
            out.append((f"closing identity rho={rho} mix={f}", "closing_identity", rho, f, ("P1", "P7"), 200, None))
            out.append((f"variant rho={rho} mix={f}", "variant", rho, f, ("P4",), 200, None))
            out.append((f"interior rho={rho} mix={f}", "interior", rho, f, ("P6",), 200, None))
        for d in (0.5, 0.8, 1.2):
            out.append((f"length diff={d} mix={f}", "length", d, f, ("P5",), 200, None))
        for lo, hi in ((0.10, 0.25), (0.10, 0.30)):
            out.append((f"format {lo}-{hi} mix={f}", "format", (lo, hi), f, ("PC",), 200, None))
    for f in (0, 0.25):
        out.append((f"discovery association mix={f}", "discovery", 0, f, drift_p, 200, None))
        out.append((f"mackay DK-G association mix={f}", "mackay", 0, f, all_p, 200, None))
    return out


def summarise(rs, only, frozen):
    entry = {"replicates": len(rs)}
    for p in only:
        vals = [r[p] for r in rs if p in r]
        outcomes = Counter(v["outcome"] for v in vals)
        entry[p] = {"rates": {k: n / len(vals) for k, n in sorted(outcomes.items())}}
        if p == "P1":
            obs = np.array([v["observed"] for v in vals])
            entry[p]["mean_observed"] = float(obs.mean())
            entry[p]["sd_observed"] = float(obs.std())
            entry[p]["mean_interval90_width"] = float(np.mean([v["interval90"][1] - v["interval90"][0] for v in vals]))
            rules = {}
            for margin in (0.20, 0.25, 0.30):
                for fail_size in (0.15, 0.20):
                    fz = dict(frozen, equivalence_margin=margin, fail_size=fail_size)
                    c = Counter(Q.equivalence_outcome(v, fz) for v in vals)
                    rules[f"margin={margin} fail_size={fail_size}"] = {k: n / len(vals) for k, n in sorted(c.items())}
            entry[p]["rule_variants"] = rules
        if p == "P2":
            shares = np.array([v["early_share"] for v in vals if v["early_share"] is not None])
            entry[p]["early_share_mean"] = float(shares.mean())
            entry[p]["early_share_quantiles_05_10_50"] = [float(x) for x in np.quantile(shares, [0.05, 0.10, 0.5])]
            entry[p]["early_units_mean"] = float(np.mean([v["units"] for v in vals]))
        if p in Q.DRIFT or p == "PC":
            ps = np.array([v["p"] for v in vals])
            entry[p]["p_le_0.05"] = float(np.mean(ps <= 0.05))
            entry[p]["p_gt_0.10"] = float(np.mean(ps > 0.10))
            entry[p]["units_mean"] = float(np.mean([v["units"] for v in vals if v["units"] is not None]))
    return entry


def main():
    frozen_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    quick = "--quick" in sys.argv
    if out_path.exists():
        raise SystemExit("output exists")
    init(frozen_path)
    plan = scenarios(quick)
    tasks = [(n, k, s, f, o, rep, ov) for n, k, s, f, o, reps, ov in plan for rep in range(reps)]
    results = defaultdict(list)
    with ProcessPoolExecutor(max_workers=16, initializer=init, initargs=(str(frozen_path),)) as ex:
        for name, out in ex.map(run_one, tasks, chunksize=4):
            results[name].append(out)
    summary = {}
    for n, k, s, f, o, reps, ov in plan:
        entry = summarise(results[n], o, dict(G["frozen"], **(ov or {})))
        entry.update({"kind": k, "size": s, "mix_fraction": f, "overrides": ov})
        summary[n] = entry
    record = {"frame": dict(Counter(c["chron_frame_cell"] for _, c in G["frame"])),
              "strata": dict(Counter(c["chron_stratum"] for _, c in G["frame"])),
              "pool_families": len(G["pool"]), "draws": DRAWS,
              "stock_share_pool": G["stock_share_pool"],
              "frozen_parameters_sha256": hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
              "scenarios": summary,
              "notes": {
                  "null": "no planted effect; P1 rates give equivalence power under true fixity, drift-test rates of 'drift' give the false-positive rate",
                  "closing": "size = expected late-third minus early-third difference in closing-stock share",
                  "opening": "rho = share of legends whose opening is redrawn from five of the ten commonest pool openings by stratum (below or above the median rank)",
                  "closing_identity": "rho = share of stock-closing legends whose closing is redrawn from three of the six commonest stock closers by period; stock share unchanged",
                  "variant": "rho = probability that a token of a two-code variant class takes the low or high code by period",
                  "interior": "rho = share of legends with one interior sign redrawn from five of the twenty commonest non-final signs by period",
                  "length": "size = expected late-third minus early-third difference in mean legend length, in signs",
                  "format": "object type redrawn as rectangular with probability rising linearly in u between the two values",
                  "discovery": "discovery seals with their own period rank placed at Mound F strata of matching rank within each frame",
                  "mackay": "Mackay DK-G seals with their own height rank placed at Mound F strata of matching rank",
                  "mix": "fraction of seals per frame whose strata are exchanged at random after planting"}}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(P.jsonable(record), indent=2) + "\n", encoding="utf-8")
    brief = {}
    for n, v in summary.items():
        brief[n] = {p: (v[p]["rates"], v[p].get("p_le_0.05")) for p in v if p.startswith("P")}
    print(json.dumps(P.jsonable(brief), indent=1))


if __name__ == "__main__":
    main()
