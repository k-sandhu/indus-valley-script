"""Step 2: images and texts on copper and moulded/incised tablets, and transfer to seals.

Usage: python -X utf8 analyze_step2.py --out <run_dir> [--perms 10000]

Implements PROTOCOL.md step 2. An object's image class is the union of the image
labels recorded on its faces; its texts are its complete faces without unknown
signs, in reading order.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402

UNCLASSED = {"None", "-", "Othr", "Unknown", "", None}


def norm_label(s):
    if s in UNCLASSED:
        return None
    if s.startswith("Bull1"):
        return "Unicorn"
    if s.startswith("Goat"):
        return "Goat"
    if s in ("Bull", "Bull2", "Bull3"):
        return "ShortBull"
    return s


def objects(faces, types):
    fam = collections.defaultdict(lambda: {"labels": set(), "texts": set(), "site": None, "raw": set()})
    for f in faces:
        if f["metadata"].get("type") not in types:
            continue
        o = fam[f["object_family_id"]]
        o["site"] = f["site"]
        o["raw"].add(f["symbol"])
        lab = norm_label(f["symbol"])
        if lab:
            o["labels"].add(lab)
        if f["complete_observed"] and not f["has_unknown_sign"] and f["length"] > 0:
            o["texts"].add(tuple(f["signs_reading_rtl"]))
    return fam


def ngrams(t, ns=(2,)):
    out = set()
    for n in ns:
        for i in range(len(t) - n + 1):
            out.add(t[i:i + n])
    if not out and 1 in ns or (not out and len(t) == 1):
        out.add(t)
    return out


def test_2a(objs, rng, perms):
    """Share of texts on >=2 objects whose objects show a single class."""
    rows = [(oid, next(iter(o["labels"])), o["texts"]) for oid, o in objs.items() if len(o["labels"]) == 1 and o["texts"]]
    labels = np.array([r[1] for r in rows])
    text_objs = collections.defaultdict(list)
    for i, r in enumerate(rows):
        for t in r[2]:
            text_objs[t].append(i)
    multi = [v for v in text_objs.values() if len(set(v)) >= 2]

    def stat(lab):
        return sum(len({lab[i] for i in v}) == 1 for v in multi)

    obs = stat(labels)
    null = np.array([stat(rng.permutation(labels)) for _ in range(perms)])
    return {"objects_with_one_class_and_text": len(rows), "texts_on_2plus_objects": len(multi),
            "class_pure": int(obs), "null_mean": float(null.mean()),
            "p_value": float((1 + (null >= obs).sum()) / (1 + perms))}


def text_types(objs):
    """Distinct texts with their majority class among single-class objects."""
    tc = collections.defaultdict(collections.Counter)
    for o in objs.values():
        if len(o["labels"]) != 1:
            continue
        lab = next(iter(o["labels"]))
        for t in o["texts"]:
            tc[t][lab] += 1
    types = [(t, c.most_common(1)[0][0], len(c)) for t, c in tc.items()]
    return types


def test_2b(types, rng, perms):
    grams = [ngrams(t, (2,)) or {t} for t, _, _ in types]
    labs = np.array([l for _, l, _ in types])
    n = len(types)
    J = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            u = grams[i] | grams[j]
            J[i, j] = J[j, i] = len(grams[i] & grams[j]) / len(u) if u else 0.0
    iu = np.triu_indices(n, 1)
    vals = J[iu]

    def stat(lab):
        same = lab[iu[0]] == lab[iu[1]]
        if same.sum() == 0 or (~same).sum() == 0:
            return 0.0
        return vals[same].mean() - vals[~same].mean()

    obs = stat(labs)
    null = np.array([stat(rng.permutation(labs)) for _ in range(perms)])
    same = labs[iu[0]] == labs[iu[1]]
    return {"text_types": n, "within_mean_jaccard": float(vals[same].mean()) if same.any() else None,
            "between_mean_jaccard": float(vals[~same].mean()), "difference": float(obs),
            "null_mean": float(null.mean()), "p_value": float((1 + (null >= obs).sum()) / (1 + perms))}, J


def test_2c(types, J, rng, perms):
    labs = np.array([l for _, l, _ in types])
    n = len(labs)
    shared = np.array([[len(ngrams(types[i][0]) & ngrams(types[j][0])) if i != j else -1 for j in range(n)]
                       for i in range(n)])

    def predict(lab):
        freq = collections.Counter(lab)
        correct = 0
        for i in range(n):
            row = shared[i]
            best = row.max()
            if best <= 0:
                pred = max(freq, key=lambda c: (freq[c] - (lab[i] == c), c))
            else:
                cands = collections.Counter(lab[j] for j in np.where(row == best)[0])
                top = max(cands.values())
                tied = [c for c, v in cands.items() if v == top]
                pred = max(tied, key=lambda c: (freq[c] - (lab[i] == c), c))
            correct += pred == lab[i]
        return correct / n

    obs = predict(labs)
    maj = collections.Counter(labs).most_common(1)[0][1] / n
    null = np.array([predict(rng.permutation(labs)) for _ in range(perms)])
    return {"text_types": n, "accuracy": float(obs), "majority_rate": float(maj), "null_mean": float(null.mean()),
            "p_value": float((1 + (null >= obs).sum()) / (1 + perms)),
            "types_with_no_shared_bigram": int((shared.max(1) <= 0).sum())}


def test_2d(copper, seals, rng, perms):
    # copper class-specific bigrams and trigrams
    class_grams = collections.defaultdict(set)
    all_grams = collections.defaultdict(set)
    # Specificity is judged against other labelled copper classes only (PROTOCOL step 2d);
    # tablets whose image is unrecorded may belong to the same class and are not rivals.
    for o in copper.values():
        labs = o["labels"]
        if not labs:
            continue
        for t in o["texts"]:
            g = ngrams(t, (2, 3))
            for lab in labs:
                class_grams[lab] |= g
            for x in g:
                all_grams[x] |= labs
    specific = {lab: {g for g in gs if all_grams[g] == {lab}} for lab, gs in class_grams.items()}
    # distinct (text, animal) seal pairs with a recorded animal
    pairs = set()
    for o in seals.values():
        if len(o["labels"]) != 1:
            continue
        lab = next(iter(o["labels"]))
        for t in o["texts"]:
            pairs.add((t, lab))
    pairs = sorted(pairs)
    seal_labs = np.array([p[1] for p in pairs])
    shared_classes = sorted(c for c in specific if specific[c] and c in set(seal_labs))
    hit = {c: np.array([bool(ngrams(t, (2, 3)) & specific[c]) for t, _ in pairs]) for c in shared_classes}

    def stat(lab):
        return sum(int((hit[c] & (lab == c)).sum()) for c in shared_classes)

    obs = stat(seal_labs)
    null = np.array([stat(rng.permutation(seal_labs)) for _ in range(perms)])
    per = {}
    for c in shared_classes:
        a = int((hit[c] & (seal_labs == c)).sum())
        b = int((hit[c] & (seal_labs != c)).sum())
        cc = int((~hit[c] & (seal_labs == c)).sum())
        d = int((~hit[c] & (seal_labs != c)).sum())
        # Review response (finding 11): report the 2x2 counts and the expected matching hits
        # under the margins; an odds ratio is given only when every cell is nonzero.
        total = a + b + cc + d
        per[c] = {"specific_ngrams": len(specific[c]), "hits_matching": a, "hits_other": b,
                  "matching_seal_texts": a + cc, "other_seal_texts": b + d,
                  "expected_matching_hits": (a + b) * (a + cc) / total if total else None,
                  "odds_ratio": (a * d / (b * cc)) if min(a, b, cc, d) > 0 else None}
    return {"seal_text_animal_pairs": len(pairs), "shared_classes": shared_classes, "matching_hits": int(obs),
            "null_mean": float(null.mean()), "p_value": float((1 + (null >= obs).sum()) / (1 + perms)),
            "per_class": per,
            "copper_classes_without_specific_ngrams": sorted(c for c in specific if not specific[c])}


def describe(objs):
    lab = collections.Counter(next(iter(o["labels"])) if len(o["labels"]) == 1 else ("multi" if o["labels"] else "unclassed")
                              for o in objs.values())
    per_class_texts = collections.defaultdict(set)
    per_class_objs = collections.Counter()
    for o in objs.values():
        if len(o["labels"]) == 1:
            c = next(iter(o["labels"]))
            per_class_objs[c] += 1
            per_class_texts[c] |= o["texts"]
    return {"objects": len(objs), "objects_with_text": sum(bool(o["texts"]) for o in objs.values()),
            "class_counts": dict(lab.most_common()),
            "per_class": {c: {"objects": per_class_objs[c], "distinct_texts": len(per_class_texts[c])}
                          for c in sorted(per_class_objs, key=lambda c: -per_class_objs[c])}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--perms", type=int, default=10000)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    faces = common.read_jsonl(common.FACES)
    rng = np.random.default_rng(common.SEED + 2)
    summary = {"protocol_sha256": common.sha256(common.PROG / "PROTOCOL.md"),
               "faces_sha256": common.sha256(common.FACES), "label_normalization":
               "Bull1:* -> Unicorn; Goat:* -> Goat; Bull/Bull2/Bull3 -> ShortBull; None, -, Othr, Unknown unclassed"}
    copper = objects(faces, {"TAB:C"})
    seals = objects(faces, {"SEAL", "SEAL:S", "SEAL:R", "SEAL:C", "SEAL:CY"})
    for name, types in (("copper", {"TAB:C"}), ("bas_relief", {"TAB:B"}), ("incised", {"TAB:I"})):
        objs = objects(faces, types)
        res = {"describe": describe(objs), "2a": test_2a(objs, rng, args.perms)}
        tt = text_types(objs)
        if len({l for _, l, _ in tt}) >= 2:
            res["2b"], J = test_2b(tt, rng, args.perms)
            res["2c"] = test_2c(tt, J, rng, args.perms)
        summary[name] = res
        print(name, json.dumps({k: v for k, v in res.items() if k != "describe"}, default=str)[:600], flush=True)
    summary["2d_copper_to_seals"] = test_2d(copper, seals, rng, args.perms)
    print("2d", json.dumps(summary["2d_copper_to_seals"], default=str)[:900])
    # sensitivity: treat the copper 'Othr' bin as its own class for 2a-2c
    def objects_othr(faces):
        objs = objects(faces, {"TAB:C"})
        for f in faces:
            if f["metadata"].get("type") == "TAB:C" and f["symbol"] == "Othr":
                objs[f["object_family_id"]]["labels"].add("OthrBin")
        return objs
    oo = objects_othr(faces)
    tt = text_types(oo)
    sens = {"2a": test_2a(oo, rng, args.perms)}
    sens["2b"], J = test_2b(tt, rng, args.perms)
    sens["2c"] = test_2c(tt, J, rng, args.perms)
    summary["copper_sensitivity_othr_as_class"] = sens
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
