"""EXPLORATORY, after the confirmation outcome: class-level summaries of the frozen per-sign effects.

Reads only confirmation/results.json (written by the single frozen run) and
GLOSS-MAP.json; it does not read the confirmation half again. Writes
confirmation/exploratory_class_summary.json. Nothing here changes the frozen result.
"""
import collections
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
res = json.loads((HERE / "confirmation" / "results.json").read_text(encoding="utf-8"))
gm = {x["code"]: x for x in json.loads((HERE / "GLOSS-MAP.json").read_text(encoding="utf-8"))["signs"]}
eff = res["per_sign_effects"]

out = {"label": "exploratory, post-outcome", "class_means": {}, "top_site_concentrated": [], "openers": {}, "stock": {}}
for var, e in eff.items():
    by = collections.defaultdict(list)
    for s, v in e.items():
        by[gm[s]["class"]].append(v)
    out["class_means"][var] = {k: {"signs": len(v), "mean": float(np.mean(v))} for k, v in sorted(by.items())}
out["top_site_concentrated"] = [{"code": s, "class": gm[s]["class"], "effect": v}
                                for s, v in sorted(eff["site"].items(), key=lambda kv: -kv[1])[:12]]
for s in ("817", "861", "820", "920", "692"):
    out["openers"][s] = {k: eff[k].get(s) for k in ("site", "size", "unicorn", "harappa")}
out["stock"] = {s: {"stock": gm[s]["stock"], "harappa_excess": v} for s, v in eff["harappa"].items() if gm[s]["stock"]}
out["period_categories"] = res["diagnostics"]["period"].get("categories")
(HERE / "confirmation" / "exploratory_class_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out["class_means"], indent=1))
