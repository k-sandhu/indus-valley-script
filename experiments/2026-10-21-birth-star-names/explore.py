"""Exploration of the birth-star predictions on the discovery half only (PROTOCOL.md, Part 2).

Every read goes through bench.shots.load_half(..., "discovery", "birthstar"). The confirmation
half is never requested. Outputs are aggregate counts and statistics.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from bench import shots  # noqa: E402
from bench.common import sha256  # noqa: E402
import birthstar as bs  # noqa: E402

SPLIT = HERE / "round.json"


def configuration(legs, fish, strokes, unit, include_final, draws, seed):
    f_tok, o_tok, i_tok = bs.collect(legs, fish, strokes, unit, include_final)
    fs, os_, is_ = bs.stats(f_tok), bs.stats(o_tok), bs.stats(i_tok)
    out = {"unit": unit, "include_final": include_final, "fish": fs, "opening_vocabulary": os_,
           "legend_initial": is_, "fish_share_of_name_position_units": fs["N"] / (fs["N"] + os_["N"]) if fs["N"] else None}
    if fs["N"] and os_["N"] > fs["N"]:
        out["matched_opening"] = bs.compare(fs, bs.matched(o_tok, fs["N"], draws, seed))
    if fs["N"] and is_["N"] > fs["N"]:
        out["matched_initial"] = bs.compare(fs, bs.matched(i_tok, fs["N"], draws, seed + 1))
    return out, Counter(f_tok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--draws", type=int, default=9999)
    ap.add_argument("--seed", type=int, default=20261021)
    args = ap.parse_args()
    out_dir = HERE / args.out
    out_dir.mkdir(parents=False, exist_ok=False)
    rows, event = shots.load_half(SPLIT, "discovery", "birthstar")
    table = bs.coding()
    fish, strokes = bs.families(table)
    legs = bs.legends(rows)
    results = {"access": event, "input_sha256": json.loads(SPLIT.read_text())["input_sha256"],
               "coding_sha256": sha256(bs.CODING), "script_sha256": sha256(__file__),
               "library_sha256": sha256(HERE / "birthstar.py"), "draws": args.draws, "seed": args.seed,
               "discovery_seal_legends": len(legs),
               "legends_with_fish": sum(any(s in fish for s in lg["seq"]) for lg in legs),
               "configurations": []}
    inventories = {}
    for unit in ("T1", "T3", "T0"):
        for include_final in (False, True):
            conf, inv = configuration(legs, fish, strokes, unit, include_final, args.draws, args.seed)
            results["configurations"].append(conf)
            inventories[f"{unit}{'_with_final' if include_final else ''}"] = dict(inv.most_common())
    # Position of fish compounds and their prefixes, primary unit.
    pos = Counter()
    prefixes = Counter()
    sign_counts = Counter()
    for lg in legs:
        for u in bs.units(lg["seq"], fish, strokes):
            if u["kind"] == "fish":
                pos["final" if u["final"] else "name_position"] += 1
                if not u["final"]:
                    prefixes[u["prefix"]] += 1
                    sign_counts.update(u["run"])
    results["fish_compound_positions"] = dict(pos)
    results["prefix_counts_name_position"] = dict(prefixes.most_common())
    results["fish_sign_counts_name_position"] = dict(sign_counts.most_common())
    results["modifier_pairs"] = bs.modifier_pairs(sign_counts, table)
    with (out_dir / "results.json").open("x", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    with (out_dir / "inventories.json").open("x", encoding="utf-8") as f:
        json.dump(inventories, f, indent=2)
    print(json.dumps({k: results[k] for k in ("discovery_seal_legends", "legends_with_fish", "fish_compound_positions")}, indent=2))


if __name__ == "__main__":
    main()
