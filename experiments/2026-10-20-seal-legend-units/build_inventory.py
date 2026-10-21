"""Freeze the line-trained model, the unit inventory and the closing stock (PROTOCOL section 5).

Usage: python -P experiments/2026-10-20-seal-legend-units/build_inventory.py --version v1

Local outputs (sign sequences derived from the Lipi export) go to
data/raw/2026-10-20-seal-legend-units/frozen-<version>/; the tracked FROZEN-<version>.json holds
their hashes and aggregate counts.
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legend_units as U  # noqa: E402

MIN_UNIT_COMPONENTS = 2
MIN_CLOSING_COMPONENTS = 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    args = ap.parse_args()
    raw = U.RAW / f"frozen-{args.version}"
    raw.mkdir(parents=True, exist_ok=False)
    texts, faces, excluded, _ = U.load_inputs()
    H = U.held_components(texts)
    build = [d for d in texts if d["component"] not in H]
    held = [d for d in texts if d["component"] in H and U.is_seal(d) and len(d["text"]) >= 3]
    faces = [f for f in faces if f["component"] not in H]
    stats = U.Stats((d["text"], d["component"]) for d in build)

    obs, lab = [], []
    for f in faces:
        with stats.without(f["component"]):
            orders = [(f["order"], 1.0)] if f["order"] else [("forward", 0.5), ("reverse", 0.5)]
            for o, w in orders:
                t = f[o]["text"]
                X = stats.text_features(t)
                Z = [U.layout(len(t), i) for i in range(1, len(t))]
                for c in f[o]["cuts"]:
                    obs.append((X, Z, c - 1, w))
                lab.append((X, {c - 1 for c in f[o]["cuts"]}, w))
    model = U.BreakModel().fit(obs)
    model.choose_threshold([(model.unit_scores(X), chosen, w) for X, chosen, w in lab])

    seg = []
    for d in build:
        with stats.without(d["component"]):
            cuts = model.cuts(stats.text_features(d["text"])) if len(d["text"]) > 1 else []
        seg.append({"text": list(d["text"]), "component": d["component"], "seal": U.is_seal(d), "cuts": cuts})

    unit_comps, unit_texts = collections.defaultdict(set), collections.Counter()
    final_comps, final_texts = collections.defaultdict(set), collections.Counter()
    for s in seg:
        t = tuple(s["text"])
        cuts = [0] + s["cuts"] + [len(t)]
        units = [t[a:b] for a, b in zip(cuts, cuts[1:])]
        for u in set(units):
            if len(u) > 1:
                unit_comps[u].add(s["component"])
                unit_texts[u] += 1
        if s["seal"] and len(t) >= 3:
            final_comps[units[-1]].add(s["component"])
            final_texts[units[-1]] += 1
    inventory = sorted((u for u, c in unit_comps.items() if len(c) >= MIN_UNIT_COMPONENTS),
                       key=lambda u: (-len(unit_comps[u]), u))
    stock = sorted((u for u, c in final_comps.items() if len(c) >= MIN_CLOSING_COMPONENTS),
                   key=lambda u: (-len(final_comps[u]), u))
    inv_rows = [{"unit": list(u), "components": len(unit_comps[u]), "texts": unit_texts[u]} for u in inventory]
    stock_rows = [{"unit": list(u), "final_components": len(final_comps[u]), "final_texts": final_texts[u]}
                  for u in stock]
    U.write_json(raw / "model.json", model.to_json())
    U.write_json(raw / "inventory.json", {"version": args.version, "rule": f"units of 2+ signs produced in texts of >= {MIN_UNIT_COMPONENTS} components of B; single signs are always units", "units": inv_rows})
    U.write_json(raw / "closing-stock.json", {"version": args.version, "rule": f"final units of B seal legends of 3+ signs, final in >= {MIN_CLOSING_COMPONENTS} components", "units": stock_rows})
    U.write_jsonl(raw / "build-segmentation.jsonl", seg)
    U.write_jsonl(raw / "held-legends.jsonl", [{"id": f"H{n:03d}", "text": list(d["text"])}
                                               for n, d in enumerate(sorted(held, key=lambda d: d["records"][0]))])
    U.write_jsonl(raw / "held-legends-key.jsonl", [{"id": f"H{n:03d}", "records": d["records"], "component": d["component"]}
                                                   for n, d in enumerate(sorted(held, key=lambda d: d["records"][0]))])

    seal_legends = [s for s in seg if s["seal"] and len(s["text"]) >= 3]
    stock_set = set(stock)
    covered = sum(U.closing_formula(tuple(s["text"]), stock_set) is not None for s in seal_legends)
    lens = collections.Counter(len(u) for u in inventory)
    cut_rate = sum(len(s["cuts"]) for s in seg) / sum(len(s["text"]) - 1 for s in seg)
    frozen = {"version": args.version, "protocol_sha256": U.sha256(U.PKG / "PROTOCOL.md"),
              "inputs": {"faces_file_sha256": U.sha256(U.FACES), "clean_file_sha256": U.sha256(U.CLEAN),
                         "audit_files": {p.name: U.sha256(p) for p in sorted(U.AUDIT.glob("verdicts-*.tsv"))}},
              "local_files": {p.name: U.sha256(p) for p in sorted(raw.iterdir())},
              "code": {name: U.sha256(U.PKG / name) for name in ("legend_units.py", "build_inventory.py", "RULES.md")},
              "training": {"faces": len(faces), "choices": len(obs), "with_plate_order": sum(bool(f["order"]) for f in faces),
                           "excluded": excluded},
              "model": {"features": U.FEATURES, "w_unit": model.w_unit.tolist(), "w_layout": model.w_layout.tolist(),
                        "tau": model.tau, "train_j": model.train_j, "converged": model.converged},
              "build_corpus": {"texts": len(build), "seal_legends_3plus": len(seal_legends), "cut_rate": cut_rate,
                               "mean_unit_length": sum(len(s["text"]) for s in seg) / sum(len(s["cuts"]) + 1 for s in seg)},
              "inventory": {"units_2plus": len(inventory), "by_length": dict(sorted(lens.items()))},
              "closing_stock": {"units": len(stock), "by_length": dict(sorted(collections.Counter(len(u) for u in stock).items())),
                                "b_seal_legends_with_stock_closing": covered,
                                "b_share_with_stock_closing": covered / len(seal_legends)},
              "held_set": {"components": len(H), "seal_legends_3plus": len(held)}}
    U.write_json(U.PKG / f"FROZEN-{args.version}.json", frozen)
    print({k: frozen[k] for k in ("training", "build_corpus", "inventory", "closing_stock", "held_set")})


if __name__ == "__main__":
    main()
