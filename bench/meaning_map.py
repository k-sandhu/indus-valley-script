"""Test directional meaning-map predictions against within-band label rearrangements."""
from collections import Counter, defaultdict
import math
from pathlib import Path

import numpy as np
from scipy.special import expit
from scipy.stats import rankdata, spearmanr

from .common import (SHOT_SOURCE, digest, envelope, null_summary, permutation_indices,
                     positive_int, read_json, read_rows)


def normalize_map(obj):
    mapping = obj.get("map", obj)
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("Map must be a nonempty sign-to-label object")
    return {str(s): v if isinstance(v, dict) else {"label": v} for s, v in mapping.items()}


def matches(record, selector):
    if isinstance(selector, dict):
        return all(record.get(k) == v for k, v in selector.items())
    return record.get("label") == selector


def variable(row, field):
    return row.get("properties", row.get("metadata", {})).get(field, row.get(field))


def numeric(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (ValueError, TypeError):
        return None


def units(rows, prediction):
    by = defaultdict(list)
    field = prediction["variable"]
    for row in rows:
        if field == "site" and prediction.get("site_policy") != "exclude_mohenjo":
            raise ValueError("Site predictions require site_policy: exclude_mohenjo")
        if field == "site" and variable(row, "site") == "Mohenjo-daro":
            continue
        val = variable(row, field)
        if val is None or val in ("", "-", "?", "Unknown"):
            continue
        by[str(row.get("component", row.get("group", row.get("id", ""))))].append(row)
    if "" in by:
        raise ValueError("Meaning-map rows require id, group or component")
    out = []
    measure = prediction.get("measure", "mean")
    for component, members in by.items():
        signs = set(s for r in members for s in r.get("signs", r.get("signs_reading_rtl", [])))
        values = [variable(r, field) for r in members]
        if measure == "mean":
            nums = [numeric(v) for v in values]
            nums = [v for v in nums if v is not None]
            if not nums:
                continue
            value = float(np.mean(nums))
        elif measure in ("share", "concentration"):
            value = Counter(map(str, values)).most_common(1)[0][0]
        else:
            raise ValueError("measure must be mean, share or concentration")
        controls = tuple(str(variable(members[0], f)) for f in prediction.get("controls", []))
        out.append({"component": component, "value": value, "signs": signs, "controls": controls})
    if prediction.get("controls") and measure == "mean":
        means = defaultdict(list)
        for u in out:
            means[u["controls"]].append(u["value"])
        for u in out:
            u["value"] -= float(np.mean(means[u["controls"]]))
    return out


def effects(us, codes, prediction):
    minimum = prediction.get("min_units", 8)
    measure = prediction.get("measure", "mean")
    eff, counts = {}, {}
    vals = [u["value"] for u in us]
    if not vals:
        return eff, counts
    if measure == "mean":
        background = float(np.mean(vals))
    elif measure == "share":
        background = float(np.mean([str(v) == str(prediction["value"]) for v in vals]))
    else:
        cats = sorted(set(vals))
        p = np.array([vals.count(c) for c in cats], dtype=float) / len(vals)
    for s in codes:
        xs = [u["value"] for u in us if s in u["signs"]]
        counts[s] = len(xs)
        if len(xs) < minimum:
            continue
        if measure == "mean":
            eff[s] = float(np.mean(xs)) - background
        elif measure == "share":
            eff[s] = float(np.mean([str(v) == str(prediction["value"]) for v in xs])) - background
        else:
            obs = np.array([xs.count(c) for c in cats], dtype=float)
            q = obs / len(xs)
            positive = q > 0
            # Multinomial finite-sample correction for KL, in nats per unit.
            eff[s] = float(np.sum(q[positive] * np.log(q[positive] / p[positive]))) - (len(cats) - 1) / (2 * len(xs))
    return eff, counts


def contrast(eff, codes, records, prediction, perm):
    idx = [i for i, s in enumerate(codes) if s in eff]
    if not idx:
        return float("nan")
    values = np.array([eff[codes[i]] for i in idx])
    criterion = prediction.get("criterion", "rank")
    if criterion == "rank":
        values = rankdata(values) / len(values)
    elif criterion not in ("loo", "none"):
        raise ValueError("criterion must be rank, loo or none")
    pos = [k for k, i in enumerate(idx) if matches(records[perm[i]], prediction["positive"])]
    neg = [k for k, i in enumerate(idx) if matches(records[perm[i]], prediction["negative"])]
    if not pos or not neg:
        return float("nan")
    direction = prediction.get("direction", 1)
    if direction not in (1, -1):
        raise ValueError("direction must be 1 or -1")
    return float(direction * (np.mean(values[pos]) - np.mean(values[neg])))


def rearrange_effects(codes, mapping, bands, measures, predictions, draws, seed, alpha=.05):
    records = [mapping[s] for s in codes]
    ident = np.arange(len(codes))
    actual = [contrast(e, codes, records, p, ident) for e, p in zip(measures, predictions)]
    sims = [[] for _ in predictions]
    for perm in permutation_indices(bands, draws, seed):
        for i, (e, p) in enumerate(zip(measures, predictions)):
            sims[i].append(contrast(e, codes, records, p, perm))
    components = {p["id"]: null_summary(a, s, alpha / len(predictions))
                  for p, a, s in zip(predictions, actual, sims)}
    if all(v["computable"] for v in components.values()):
        znull = [(np.array(s) - np.mean(s)) / np.std(s) for s in sims]
        S = sum(v["distance_sd"] for v in components.values())
        joint = null_summary(S, np.sum(znull, axis=0), alpha)
    else:
        joint = {"computable": False, "pass": False, "reason": "All declared predictions must be computable"}
    return {"components": components, "primary": joint}


def reliability(us, codes, prediction, seed):
    halves = [[], []]
    for u in us:
        halves[int(digest([seed, u["component"]]), 16) % 2].append(u)
    es = [effects(h, codes, prediction)[0] for h in halves]
    common = sorted(set(es[0]) & set(es[1]))
    a, b = [np.array([e[s] for s in common]) for e in es]
    valid = len(common) >= 3 and np.std(a) > 0 and np.std(b) > 0
    return {"eligible_signs_both_halves": len(common), "units_by_half": list(map(len, halves)),
            "pearson": float(np.corrcoef(a, b)[0, 1]) if valid else None,
            "spearman": float(spearmanr(a, b).statistic) if valid else None,
            "computable": valid}


def evaluate(rows, mapping, predictions, draws=199, seed=20261013, alpha=.05, discovery=None):
    if not 0 < alpha < 1 or draws < 1:
        raise ValueError("Require 0 < alpha < 1 and positive permutation count")
    if not predictions or len({p["id"] for p in predictions}) != len(predictions):
        raise ValueError("Declare uniquely named predictions")
    codes = sorted(mapping)
    freq = Counter(s for r in rows for s in set(r.get("signs", r.get("signs_reading_rtl", []))))
    bands = [mapping[s].get("band", [int(math.log2(max(1, freq[s]))), mapping[s].get("position_band", "all")]) for s in codes]
    measures, sample_sizes, influence, reliabilities = [], {}, {}, {}
    for p in predictions:
        us = units(rows, p)
        e, n = effects(us, codes, p)
        measures.append(e)
        sample_sizes[p["id"]] = {"units": len(us), "eligible_signs": len(e),
                                  "min_sign_units": min((n[s] for s in e), default=0)}
        reliabilities[p["id"]] = reliability(units(discovery if discovery is not None else rows, p), codes, p, seed)
        if p.get("criterion", "rank") == "loo":
            values = []
            for u in us:
                remaining = [v for v in us if v["component"] != u["component"]]
                eff = effects(remaining, codes, p)[0]
                values.append(contrast(eff, codes, [mapping[s] for s in codes], p, np.arange(len(codes))))
            influence[p["id"]] = {"criterion": "leave one component out, direction remains positive",
                                    "minimum_contrast": min(values, default=float("nan")),
                                    "pass": bool(values) and all(np.isfinite(v) and v > 0 for v in values)}
        else:
            influence[p["id"]] = {"criterion": p.get("criterion", "rank"),
                                    "pass": p.get("criterion", "rank") == "rank"}
    result = rearrange_effects(codes, mapping, bands, measures, predictions, draws, seed, alpha)
    resplits = {}
    for p in predictions:
        us = units(discovery if discovery is not None else rows, p)
        values = []
        for offset in range(5):
            halves = [[], []]
            for u in us:
                halves[int(digest([seed + offset, u["component"]]), 16) % 2].append(u)
            for h in halves:
                e = effects(h, codes, p)[0]
                values.append(contrast(e, codes, [mapping[s] for s in codes], p, np.arange(len(codes))))
        finite = np.array([v for v in values if np.isfinite(v)])
        resplits[p["id"]] = {"re_splits": 5, "computable_half_contrasts": len(finite),
                              "mean": float(finite.mean()) if len(finite) else None,
                              "sd": float(finite.std()) if len(finite) else None}
    result.update({"seed": seed, "permutations": draws, "alpha": alpha,
                   "sample_sizes": sample_sizes, "reliability": reliabilities, "discovery_resplit_stability": resplits,
                   "reliability_population": "supplied discovery data" if discovery is not None else "evaluated population",
                   "influence": influence,
                   "pass": result["primary"]["pass"] and all(v["pass"] for v in influence.values()),
                   "pass_rule": "All declared measures computable; joint within-band p <= alpha; every prediction uses rank or passes component leave-one-out"})
    return result


def synthetic_data(effect, seed):
    rng = np.random.default_rng(seed)
    mapping = {f"S{i:03}": {"label": "official" if i % 2 else "name", "band": [0, 0]} for i in range(64)}
    rows = []
    for i, (s, m) in enumerate(mapping.items()):
        for j in range(24):
            rows.append({"id": f"U{i}-{j}", "signs": [s],
                         "properties": {"size": float(rng.normal() + effect * (m["label"] == "official"))}})
    preds = [{"id": "larger_official", "variable": "size", "positive": "official",
              "negative": "name", "direction": 1, "criterion": "rank", "min_units": 4}]
    return rows, mapping, preds


def power(effects_to_plant=(0., .25, .5, 1.5), trials=40, draws=199, seed=20261013):
    report = []
    for effect in effects_to_plant:
        passes = 0
        for trial in range(trials):
            rows, mapping, predictions = synthetic_data(effect, seed + 1000 + trial)
            passes += evaluate(rows, mapping, predictions, draws, seed + 2000 + trial)["pass"]
        from .restoration import wilson
        report.append({"planted_effect_sd": effect, "law": "Independent component values, normal noise SD 1, 24 units per sign",
                       **wilson(passes, trials)})
    return report


def power_on_design(rows, mapping, predictions, effects_to_plant, trials=40, draws=199, seed=20261013):
    """Plant responses on the submitted incidence matrix; signs on one object share its response."""
    import copy
    from .restoration import wilson
    if len({p["variable"] for p in predictions}) != len(predictions):
        raise ValueError("Predictions sharing a variable need a joint generative law; run one declared planting per variable")
    report = []
    for effect in effects_to_plant:
        passes = 0
        for trial in range(trials):
            rng = np.random.default_rng(seed + 1000 + trial)
            generated = copy.deepcopy(rows)
            for p in predictions:
                us = units(rows, p)
                responses = {}
                observed = [u["value"] for u in us]
                for u in us:
                    pos = sum(matches(mapping[s], p["positive"]) for s in u["signs"] if s in mapping)
                    neg = sum(matches(mapping[s], p["negative"]) for s in u["signs"] if s in mapping)
                    exposure = pos / (pos + neg) if pos + neg else 0.
                    shift = effect * p.get("direction", 1) * exposure
                    if p.get("measure", "mean") == "mean":
                        value = float(rng.normal() + shift)
                    elif p.get("measure") == "share":
                        background = np.mean([str(v) == str(p["value"]) for v in observed])
                        background = float(np.clip(background, .01, .99))
                        probability = float(expit(math.log(background / (1 - background)) + shift))
                        value = str(p["value"]) if rng.random() < probability else "__synthetic_other__"
                    else:
                        if effect < 0:
                            raise ValueError("Concentration planting strength must be nonnegative")
                        selected = [s for s in sorted(u["signs"]) if s in mapping
                                    and matches(mapping[s], p["positive"] if p.get("direction", 1) == 1 else p["negative"])]
                        eligible = pos + neg
                        share = len(selected) / eligible if eligible else 0.
                        if selected and rng.random() < 1 - math.exp(-effect * share):
                            categories = sorted(set(observed))
                            value = categories[int(digest(selected[0]), 16) % len(categories)]
                        else:
                            value = str(rng.choice(observed))
                    responses[u["component"]] = value
                for row in generated:
                    component = str(row.get("component", row.get("group", row.get("id", ""))))
                    if component in responses:
                        row.setdefault("properties", dict(row.get("metadata", {})))[p["variable"]] = responses[component]
            passes += evaluate(generated, mapping, predictions, draws, seed + 2000 + trial)["pass"]
        report.append({"effect": effect, "effect_scale": {p["id"]: {"mean": "response noise SD", "share": "log odds", "concentration": "category-mixture strength; mixture probability 1-exp(-effect*exposure)"}[p.get("measure", "mean")] for p in predictions},
                       "law": "Component outcomes depend on the mapped-label share; all signs on a component share its response. Concentration plants a sign-specific category mixed with the original background.",
                       **wilson(passes, trials)})
    return report


def configure(ap):
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--objects", type=Path)
    ap.add_argument("--map", type=Path)
    ap.add_argument("--predictions", type=Path)
    ap.add_argument("--discovery", type=Path, help="Separate discovery objects for pre-freeze reliability")
    ap.add_argument("--permutations", type=positive_int, default=199)
    ap.add_argument("--seed", type=int, default=20261013)
    ap.add_argument("--alpha", type=float, default=.05)
    ap.add_argument("--effect", type=float, default=1.5)
    ap.add_argument("--power-trials", type=int, default=0)
    ap.add_argument("--power-effects", default="0,.25,.5,1.5")


def run(args):
    sources = [SHOT_SOURCE + "/shot-b-reading/confirm.py", SHOT_SOURCE + "/REVIEW-RESPONSE.md"]
    if args.synthetic:
        rows, mapping, predictions = synthetic_data(args.effect, args.seed)
        discovery = synthetic_data(args.effect, args.seed + 1)[0]
    else:
        if not args.objects or not args.map or not args.predictions:
            raise ValueError("Supply --objects, --map and --predictions")
        rows, mapping = read_rows(args.objects), normalize_map(read_json(args.map))
        obj = read_json(args.predictions)
        predictions = obj["predictions"] if isinstance(obj, dict) else obj
        discovery = read_rows(args.discovery) if args.discovery else None
        sources += [args.objects, args.map, args.predictions] + ([args.discovery] if args.discovery else [])
    result = evaluate(rows, mapping, predictions, args.permutations, args.seed, args.alpha, discovery)
    if args.power_trials:
        if args.power_trials < 1:
            raise ValueError("Power trials must be positive")
        result["power"] = power_on_design(discovery if discovery is not None else rows, mapping, predictions,
                                            tuple(float(v) for v in args.power_effects.split(",")), args.power_trials, args.permutations, args.seed)
        result["power_scope"] = "Planted on the supplied discovery incidence matrix when available, with component-shared outcomes"
    return envelope("meaning-map", result, args.synthetic, sources)
