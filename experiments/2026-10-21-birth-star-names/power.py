"""Power of the frozen fresh-data rules (P2-P4) under the claim and under rival models.

Fresh fish runs are simulated at the sample sizes the fresh pool may reach. The claim model
draws from the discovery run distribution with its Good-Turing unseen mass; rivals change one
feature at a time: an open vocabulary, a site-specific profile, a near-monopoly and a flat class
of 27 names.
"""
import argparse
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import birthstar as bs  # noqa: E402
import score_fresh as sf  # noqa: E402


def model_claim(counts):
    n = sum(counts.values())
    f1 = sum(v == 1 for v in counts.values())
    unseen = f1 / n
    types = list(counts)
    p = np.array([counts[t] for t in types], float) / n * (1 - unseen)
    return types, p, unseen


def draw(types, p, unseen, n, rng, tag):
    out = []
    for _ in range(n):
        if rng.random() < unseen:
            out.append(f"{tag}-new-{rng.integers(1_000_000)}")
        else:
            out.append(types[rng.choice(len(types), p=p / p.sum())])
    return out


def models(counts, top4):
    types, p, unseen = model_claim(counts)
    local_p = np.array([pi * (0.4 / 0.667) if t in top4 else pi * (0.6 / 0.333) for t, pi in zip(types, p)])
    mono_p = np.array([0.7 if t == types[0] else 0.3 * pi / (p.sum() - p[0]) for t, pi in zip(types, p)])
    ranked = sorted(types, key=lambda t: -counts[t])
    flat = ranked[:27]
    return {
        "claim_discovery_profile": (types, p, unseen),
        "open_vocabulary_novelty_0.30": (types, p, 0.30),
        "site_specific_top4_share_0.40": (types, local_p, unseen),
        "near_monopoly_top_0.70": (types, mono_p, unseen),
        "flat_over_27_discovery_runs": (flat, np.ones(len(flat)) / len(flat), 0.0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", default=str(HERE / "frozen-reference.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--trials", type=int, default=400)
    args = ap.parse_args()
    ref = json.loads(Path(args.reference).read_text(encoding="utf-8"))
    counts, top4 = ref["discovery_T0_counts"], ref["discovery_T0_top4"]
    inventory = set(ref["discovery_T0_inventory"])
    rng = np.random.default_rng(20261021)
    out = {"trials": args.trials, "reference_sha256": sf.sha256(args.reference), "results": {}}
    for n in (40, 60, 100, 150):
        n_star = min(n, sum(ref["brahmi_asterism_counts"].values()))
        ranges = {k: sf.reference_range(ref["brahmi_asterism_counts"], n_star, k) for k in sf.PROFILE_KEYS}
        for name, (types, p, unseen) in models(counts, top4).items():
            passes = {"P2": 0, "P3": 0, "P4": 0, "all": 0}
            for _ in range(args.trials):
                toks = draw(types, p, unseen, n, rng, name)
                p2 = sum(t not in inventory for t in toks) / n <= 0.15
                if n > n_star:
                    arr = np.array(toks, dtype=object)
                    sub = [bs.stats(list(rng.choice(arr, size=n_star, replace=False))) for _ in range(99)]
                    st = {k: float(np.median([s[k] for s in sub])) for k in sf.PROFILE_KEYS}
                else:
                    st = bs.stats(toks)
                p3 = all(st[k] is not None and ranges[k][0] <= st[k] <= ranges[k][1] for k in ranges)
                cov = sum(t in top4 for t in toks) / n
                p4 = 0.50 <= cov <= 0.85
                passes["P2"] += p2
                passes["P3"] += p3
                passes["P4"] += p4
                passes["all"] += p2 and p3 and p4
            out["results"].setdefault(str(n), {})[name] = {k: v / args.trials for k, v in passes.items()}
        out["results"][str(n)]["brahmi_ranges"] = ranges
    with open(args.out, "x", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["results"], indent=1))


if __name__ == "__main__":
    main()
