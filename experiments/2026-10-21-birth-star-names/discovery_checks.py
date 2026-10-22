"""Exploratory checks on the discovery half chosen after discovery-v1 and the Brahmi calibration.

1. Are fish runs more closed than runs of other sign families of similar frequency?
2. Is the fish-run profile the same at different sites?
3. Is the fish-run type independent of the sign that follows it?
4. Does the fish-run profile fall inside the Brahmi asterism range at matched size?
5. How common are fish runs in name position per legend, beside the Brahmi asterism share?
All reads use bench.shots.load_half(..., "discovery", "birthstar").
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from bench import shots  # noqa: E402
from bench.common import sha256  # noqa: E402
import birthstar as bs  # noqa: E402
import score_fresh as sf  # noqa: E402


def family_runs(legs, base):
    out = defaultdict(list)
    for lg in legs:
        seq, n, i = lg["seq"], len(lg["seq"]), 0
        while i < n:
            b = base.get(seq[i])
            if b in ("B001", "B031") or b is None:
                i += 1
                continue
            j = i
            while j < n and base.get(seq[j]) == b:
                j += 1
            if j < n:
                out[b].append("+".join(seq[i:j]))
            i = j
    return out


def rarefied(tokens, n, rng, draws=999):
    arr = np.array(tokens, dtype=object)
    res = defaultdict(list)
    for _ in range(draws):
        st = bs.stats(list(rng.choice(arr, size=n, replace=False)))
        for k in ("S", "chao1", "normalised_entropy", "top_share"):
            if st.get(k) is not None:
                res[k].append(st[k])
    return {k: float(np.median(v)) for k, v in res.items()}


def mutual_information(pairs):
    n = len(pairs)
    ca, cb, cab = Counter(a for a, _ in pairs), Counter(b for _, b in pairs), Counter(pairs)
    return float(sum(v / n * np.log((v / n) / ((ca[a] / n) * (cb[b] / n))) for (a, b), v in cab.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--calibration", default=str(HERE / "calibration-v1/calibration.json"))
    args = ap.parse_args()
    out_dir = HERE / args.out
    out_dir.mkdir(parents=False, exist_ok=False)
    rows, event = shots.load_half(HERE / "round.json", "discovery", "birthstar")
    table = bs.coding()
    fish, strokes = bs.families(table)
    legs = bs.legends(rows)
    base = {c: r["base"] for c, r in table.items()}
    rng = np.random.default_rng(20261021)
    res = {"access": event, "script_sha256": sha256(__file__), "library_sha256": sha256(HERE / "birthstar.py"),
           "scorer_sha256": sha256(HERE / "score_fresh.py"), "calibration_sha256": sha256(args.calibration)}

    runs = family_runs(legs, base)
    fishN = len(runs["B220"])
    fam = {}
    for b, toks in sorted(runs.items(), key=lambda kv: -len(kv[1])):
        if len(toks) < 60:
            continue
        n = min(len(toks), fishN)
        fam[b] = {"codes_in_family": sum(1 for c in base if base[c] == b), "name_position_runs": len(toks),
                  "compared_at": n, "family": rarefied(toks, n, rng), "fish": rarefied(runs["B220"], n, rng)}
    res["family_closure"] = fam

    t0_by_site = defaultdict(list)
    nxt = []
    for lg in legs:
        for u in bs.units(lg["seq"], fish, strokes):
            if u["kind"] == "fish" and not u["final"]:
                t0_by_site[lg["site"]].append(u["T0"])
                nxt.append((u["T0"], lg["seq"][u["end"] + 1]))
    t0_all = [t for v in t0_by_site.values() for t in v]
    top4 = [k for k, _ in sorted(Counter(t0_all).items(), key=lambda kv: (-kv[1], kv[0]))[:4]]
    res["site_profiles"] = {s: {"runs": len(v), "top4_coverage": sum(t in top4 for t in v) / len(v),
                                "commonest": Counter(v).most_common(5)}
                            for s, v in sorted(t0_by_site.items(), key=lambda kv: -len(kv[1])) if len(v) >= 5}
    keep_a = [t for t, _ in Counter(a for a, _ in nxt).most_common(5)]
    keep_b = [t for t, _ in Counter(b for _, b in nxt).most_common(8)]
    pairs = [(a if a in keep_a else "other", b if b in keep_b else "other") for a, b in nxt]
    obs = mutual_information(pairs)
    a_, b_ = [a for a, _ in pairs], [b for _, b in pairs]
    null = [mutual_information(list(zip(a_, rng.permutation(b_)))) for _ in range(4999)]
    res["next_sign_independence"] = {"pairs": len(pairs), "mutual_information_nats": obs,
                                     "permutation_p": (1 + sum(x >= obs for x in null)) / 5000,
                                     "rows": keep_a + ["other"], "columns": keep_b + ["other"]}

    cal = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
    prof = {}
    for variant in ("strict", "broad"):
        counts = cal["variants"][variant]["asterism_counts"]
        profile, ranges, n_star = sf.profile_check(t0_all, counts)
        prof[variant] = {"n_compared": n_star, "fish_T0_profile": profile, "brahmi_95_range": ranges,
                         "inside": {k: ranges[k][0] <= profile[k] <= ranges[k][1] for k in ranges},
                         "fish_T0_richness_at_n": rarefied(t0_all, n_star, rng),
                         "brahmi_richness": {k: cal["variants"][variant]["asterism_elements"]["stats"][k] for k in ("S", "chao1")}}
    res["brahmi_profile_check"] = prof

    with_fish = sum(any(u["kind"] == "fish" and not u["final"] for u in bs.units(lg["seq"], fish, strokes)) for lg in legs)
    res["prevalence"] = {"legends": len(legs), "legends_with_name_position_fish_run": with_fish,
                         "share": with_fish / len(legs), "wilson95": bs.wilson(with_fish, len(legs)),
                         "brahmi_asterism_share_strict": cal["variants"]["strict"]["share_wilson95"],
                         "brahmi_asterism_share_broad": cal["variants"]["broad"]["share_wilson95"]}
    with (out_dir / "checks.json").open("x", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=str)
    print(json.dumps({k: res[k] for k in ("next_sign_independence", "brahmi_profile_check", "prevalence")}, indent=1, default=str))


if __name__ == "__main__":
    main()
