"""Post-outcome description, exploratory: written after the confirmation result was known.

Shares and means by third of height in both excavations, a Stouffer combination of the
one-sided drift tests of the two excavations, and the variant classes behind P6. None of
this changes a frozen outcome.

    python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/post_outcome.py OUT_DIR
"""
from collections import Counter, defaultdict
import copy
import json
import math
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
import score  # noqa: E402
import strat_stats as S  # noqa: E402

RAW = ROOT / "data/raw/2026-10-20-mohenjo-daro-stratigraphy"


def third(u):
    return 0 if u < 1 / 3 else (1 if u < 2 / 3 else 2)


def normal_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def describe(objects, frozen):
    stock, formulae = set(frozen["closing_stock"]), set(frozen["closing_formulae"])
    close = S.units(objects, "closing")
    pairs = S.units(objects, "closing_pair")
    legends = S.units(objects, "length", min_length=1)
    out = {}
    for name, rows, test in (("closing_stock_share", close, lambda r: r["value"] in stock),
                             ("sign_740_share", close, lambda r: r["value"] == "740"),
                             ("closing_formula_share", pairs, lambda r: r["value"] in formulae)):
        out[name] = [float(np.mean([test(r) for r in rows if third(r["u"]) == t])) for t in range(3)]
    out["mean_length"] = [float(np.mean([r["value"] for r in legends if third(r["u"]) == t])) for t in range(3)]
    out["rectangular_share"] = [float(np.mean([o["object_type"] == "SEAL:R" for o in objects if third(o["u"]) == t])) for t in range(3)]
    out["units_by_third"] = [sum(third(r["u"]) == t for r in close) for t in range(3)]
    out["closing_signs_bottom_third_top8"] = dict(Counter(r["value"] for r in close if third(r["u"]) == 0).most_common(8))
    return out


def variant_profile(objects):
    """For each variant class, mean height of each code (codes with at least 3 rows)."""
    rows = S.variant_tokens([{"stratum": r["stratum"], "u": r["u"], "object_family_id": r["families"][0],
                              "text": {"signs": r["signs"]}} for r in S.all_legends(objects)], S.load_variant_classes())
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[r["class"]][r["value"]].append(r["u"])
    return {c: {code: {"rows": len(v), "mean_u": float(np.mean(v))} for code, v in sorted(codes.items()) if len(v) >= 3}
            for c, codes in sorted(by.items()) if sum(len(v) >= 3 for v in codes.values()) >= 2}


def main():
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=False)
    frozen = json.loads((PACKAGE / "discovery-v2/frozen-parameters.json").read_text(encoding="utf-8"))
    mackay_rows = [json.loads(x) for x in (RAW / "discovery-mackay1938.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    marshall_rows = [json.loads(x) for x in (RAW / "confirmation-marshall1931.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    mackay, _ = score.prepare(copy.deepcopy(mackay_rows), areas={"DK"})
    marshall, _ = score.prepare(copy.deepcopy(marshall_rows))
    disc = json.loads((PACKAGE / "discovery-v2/exploration.json").read_text(encoding="utf-8"))["rehearsal_in_sample"]
    conf = json.loads((PACKAGE / "confirmation-v1/results.json").read_text(encoding="utf-8"))["results"]

    def z_of(res):
        if res.get("z") is not None:
            return res["z"]
        return None
    combined = {}
    for k in ("P4", "P6", "P7"):
        za, zb = z_of(disc[k]), z_of(conf[k])
        z = (za + zb) / math.sqrt(2)
        combined[k] = {"z_mackay": za, "z_marshall": zb, "stouffer_z": z, "one_sided_p": normal_sf(z)}
    record = {"status": "exploratory, post-outcome",
              "mackay_dk": describe(mackay, frozen), "marshall": describe(marshall, frozen),
              "stouffer_two_excavations": combined,
              "variant_profiles": {"mackay_dk": variant_profile(mackay), "marshall": variant_profile(marshall)}}
    (out_dir / "summary.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("mackay_dk", "marshall", "stouffer_two_excavations")}, indent=1))


if __name__ == "__main__":
    main()
