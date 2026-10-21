"""Print the per-statistic table of a discrimination summary for the report.

Usage: python -I experiments/2026-10-21-head-direction-corpora/summarize_run.py --summary <summary.json> [--panel main|without_doubtful|sanskrit_only_ia]

Reads only the aggregate summary written by discriminate.py; writes nothing.
"""
import argparse
import json
import sys
from pathlib import Path

ORDER = ("ia-ganges", "ta-brahmi", "sux-ur3", "akk-sargonic")


def fmt(x):
    return "null" if x is None else f"{x:+.3f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True, type=Path)
    ap.add_argument("--panel", default="main")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    s = json.loads(args.summary.read_text(encoding="utf-8"))
    panel = s if args.panel == "main" else s["sensitivities"][args.panel]
    print("thresholds", s.get("entry_thresholds"), "exclusions", s.get("exclusions", {}).get("excluded_by_corpus_and_reason"))
    for stat, r in panel["statistics"].items():
        d = r["decision"]
        cells = []
        for c in ORDER:
            v = r["corpora"].get(c)
            cells.append(f"{c}: {fmt(v['median'])} [{fmt(v['p5'])}, {fmt(v['p95'])}] e={v['eligible']}" if v else f"{c}: out")
        sx = r.get("sux_sargonic", {})
        sxs = f"sux-sargonic: {fmt(sx.get('median'))}" if sx.get("status") == "reported" else f"sux-sargonic: {sx.get('status')}"
        print(f"{stat}: n={r['n']} testable={d['testable']} kept={d['kept']} dir={d['direction']} sep={d['separated_replicate_share']:.3f}")
        print("   " + " | ".join(cells) + " | " + sxs)
        if "shuffle_reference" in r:
            for c, ref in r["shuffle_reference"].items():
                print(f"   shuffle {c}: obs={fmt(ref['observed'])} mean={fmt(ref['shuffle_mean'])} [{fmt(ref['p2_5'])}, {fmt(ref['p97_5'])}] e={ref['eligible']}")
        sub = r.get("subcorpora", {})
        if sub.get("corpora"):
            print("   sub n=%s on-primary-side=%s: " % (sub.get("n"), sub.get("every_subcorpus_on_primary_side"))
                  + "; ".join(f"{c} {fmt(v['median'])}" for c, v in sub["corpora"].items()))


if __name__ == "__main__":
    main()
