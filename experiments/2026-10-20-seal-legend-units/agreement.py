"""Agreement between our rule implementation and an independent agent on the held set (PROTOCOL section 6).

Usage: python -P experiments/2026-10-20-seal-legend-units/agreement.py --version v1 --agent <agent jsonl> --out <json>

The agent file has one row per held legend: {"id": "H000", "cuts": [..], "closing": [..] or null}.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legend_units as U  # noqa: E402


def load_frozen(version):
    raw = U.RAW / f"frozen-{version}"
    inv = {tuple(r["unit"]) for r in U.json.loads((raw / "inventory.json").read_text(encoding="utf-8"))["units"]}
    stock = {tuple(r["unit"]) for r in U.json.loads((raw / "closing-stock.json").read_text(encoding="utf-8"))["units"]}
    model = U.BreakModel.from_json(U.json.loads((raw / "model.json").read_text(encoding="utf-8")))
    return raw, inv, stock, model


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else None


def compare(held, first, second):
    va, vb = [], []
    same_cuts = same_close = 0
    for h in held:
        L = len(h["text"])
        ca, cb = set(first[h["id"]]["cuts"]), set(second[h["id"]]["cuts"])
        va += [i in ca for i in range(1, L)]
        vb += [i in cb for i in range(1, L)]
        same_cuts += ca == cb
        a, b = first[h["id"]].get("closing"), second[h["id"]].get("closing")
        same_close += (tuple(a) if a else None) == (tuple(b) if b else None)
    return {"legends": len(held), "positions": len(va), "cut_rate_first": sum(va) / len(va),
            "cut_rate_second": sum(vb) / len(vb), "position_agreement": sum(x == y for x, y in zip(va, vb)) / len(va),
            "kappa": kappa(va, vb), "identical_segmentations": same_cuts / len(held),
            "identical_closing": same_close / len(held)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--agent", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--junction", action="store_true",
                    help="version 2 direct segmentation: threshold cuts plus the strongest boundary (AMENDMENT-1.md)")
    args = ap.parse_args()
    raw, inv, stock, model = load_frozen(args.version)
    held = U.read_jsonl(raw / "held-legends.jsonl")
    agent = {r["id"]: r for r in U.read_jsonl(args.agent)}
    if set(agent) != {h["id"] for h in held}:
        raise ValueError("The agent file must hold exactly one row per held legend")
    ours = {}
    for h in held:
        s = U.segment_by_rules(h["text"], inv, stock)
        ours[h["id"]] = {"id": h["id"], "cuts": s["cuts"], "closing": list(s["closing"]) if s["closing"] else None}
    texts, _, _, _ = U.load_inputs()
    H = U.held_components(texts)
    stats = U.Stats((d["text"], d["component"]) for d in texts if d["component"] not in H)
    direct = {}
    for h in held:
        X = stats.text_features(tuple(h["text"]))
        cuts = model.cuts(X)
        if args.junction:
            j = int(model.unit_scores(X).argmax()) + 1
            cuts = sorted(set(cuts) | {j})
            close = tuple(h["text"][j:]) if 1 <= len(h["text"]) - j <= 4 else None
            direct[h["id"]] = {"cuts": cuts, "closing": list(close) if close and close in stock else None}
        else:
            direct[h["id"]] = {"cuts": cuts}
    out_raw = raw / "agreement"
    out_raw.mkdir(exist_ok=True)
    ours_path = out_raw / f"ours-{args.out.stem}.jsonl"
    if not ours_path.exists():
        U.write_jsonl(ours_path, [ours[h["id"]] for h in held])
    result = {"version": args.version, "agent_file_sha256": U.sha256(args.agent),
              "rules_sha256": U.sha256(U.PKG / ("RULES.md" if args.version == "v1" else f"RULES-{args.version}.md")), "code_sha256": U.sha256(U.PKG / "legend_units.py"),
              "rules_vs_agent": compare(held, ours, agent),
              "rules_vs_model_direct": compare(held, ours, direct),
              "operational_rule": "kappa >= 0.80 and identical closing on >= 90% of legends"}
    r = result["rules_vs_agent"]
    result["operational"] = bool(r["kappa"] is not None and r["kappa"] >= 0.80 and r["identical_closing"] >= 0.90)
    U.write_json(args.out, result)
    print(U.json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
