"""Measurement 1: how often a picturable noun and a name meaning have homophones, per language.

For every pair (picture concept, name concept) whose two concepts both have at
least one attested word in a lexicon, the pair counts as a homophone pair when
some word for the picture and some word for the name share a normalised form.
We report the rate over all words (Parpola's practice: any attested word may be
used), the rate with one word per concept, the homonym rate (two different
lexemes) and the chance that two random lexemes share a form. Intervals come
from a bootstrap that resamples picture concepts and name concepts.

    python -I experiments/2026-10-21-rebus-base-rate/code/run_homophones.py OUTDIR
"""

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebus  # noqa: E402

PKG = rebus.ROOT / "experiments" / "2026-10-21-rebus-base-rate"
SEED = 20261021
BOOT = 2000


def bootstrap(any_m, rng):
    a = np.array(any_m, dtype=bool)
    if a.size == 0:
        return [None, None]
    nP, nM = a.shape
    vals = []
    for _ in range(BOOT):
        ip = rng.integers(0, nP, nP)
        im = rng.integers(0, nM, nM)
        vals.append(a[np.ix_(ip, im)].mean())
    return [float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))]


def word_collision(lex, norm):
    forms = [norm(e["forms"][0]) for e in lex if e["attested"]]
    c = Counter(forms)
    n = len(forms)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) if n > 1 else None, n


def main(outdir):
    outdir = Path(outdir)
    target = outdir / "homophones.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    pools = json.loads((PKG / "pools-v1.json").read_text(encoding="utf-8"))
    pics, names = pools["picture"], pools["name"]

    bur, bur_rep = rebus.load_burushaski()
    lexicons = {
        "dravidian-dedr": rebus.load_dedr(),
        "dravidian-dedr-wordlevel": rebus.load_dedr(strict=True),
        "indoaryan-cdial": rebus.load_cdial(),
        "sumerian-epsd2": rebus.load_epsd2(),
        "munda-rau2019": rebus.load_munda(),
        "burushaski-backstrom": bur,
    }
    # inventory scaling: target is Tamil-headed DEDR forms under the stated rule
    tamil_forms = [f for e in lexicons["dravidian-dedr"] if e["attested"] and e["head_lang"] == "Ta" for f in e["forms"]]
    target_c = rebus.collision([rebus.normalise(f, ["L"]) for f in tamil_forms])
    rng = np.random.default_rng(SEED)
    result = {"schema_version": "1.0", "task": "rebus-base-rate/homophones", "synthetic": False,
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "provenance": {
                  "code": {p.name: rebus.sha256(p) for p in sorted((PKG / "code").glob("*.py"))},
                  "inputs": {str(p.relative_to(rebus.ROOT)).replace("\\", "/"): rebus.sha256(p) for p in [
                      rebus.DER / "dedr-entries.jsonl", rebus.DER / "cdial-entries.jsonl",
                      rebus.DER / "epsd2-lemmas.jsonl",
                      rebus.SRC / "munda" / "pMunda_cognate_set_2019-08-29.csv",
                      rebus.SRC / "backstrom" / "backstromnorthernpakistan-v1.1.zip",
                      PKG / "pools-v1.json"]},
                  "seed": SEED, "bootstrap_replicates": BOOT, "burushaski_representative_variety": bur_rep},
              "target_collision_tamil_T0": target_c, "languages": {}}

    for name, lex in lexicons.items():
        att = [e for e in lex if e["attested"]]
        token_forms = [f for e in att for f in e["forms"]]
        steps, trail = rebus.scale_steps(token_forms, target_c)
        if name.startswith("dravidian"):
            steps, trail = ["L"], trail[:1]
        idx = rebus.concept_index(lex, pics + names)
        lang = {"lexemes": len(lex), "attested_lexemes": len(att), "scaled_steps": "".join(steps),
                "collision_trail": trail, "tolerances": {}}
        lang["concepts_found"] = {"picture": sum(1 for c in pics if c["id"] in idx),
                                  "name": sum(1 for c in names if c["id"] in idx)}
        lang["mean_words_per_found_concept"] = {
            k: (sum(len(idx[c["id"]]) for c in pool if c["id"] in idx) / max(1, lang["concepts_found"][k]))
            for k, pool in (("picture", pics), ("name", names))}
        tols = {"T0": lambda f: rebus.normalise(f, ["L"]),
                "T0s": lambda f, s=tuple(steps): rebus.normalise(f, s),
                "T1s": lambda f, s=tuple(steps): rebus.stem(rebus.normalise(f, s))}
        for tname, norm in tols.items():
            P, M, any_m, hom_m, examples = rebus.pair_matrix(idx, pics, names, norm)
            n_pairs = len(P) * len(M)
            k_any = sum(map(sum, any_m))
            k_hom = sum(map(sum, hom_m))
            P1, M1, any1, _, ex1 = rebus.pair_matrix(idx, pics, names, norm, one_per_concept=True)
            k1 = sum(map(sum, any1))
            wc, wn = word_collision(lex, norm)
            by_class = {}
            for cls in ("deity", "celestial", "colour", "direction", "kinship", "quality"):
                cols = [j for j, m in enumerate(M) if next(c for c in names if c["id"] == m)["class"] == cls]
                tot = len(P) * len(cols)
                by_class[cls] = {"pairs": tot, "any": sum(any_m[i][j] for i in range(len(P)) for j in cols),
                                 "rate": (sum(any_m[i][j] for i in range(len(P)) for j in cols) / tot) if tot else None}
            lang["tolerances"][tname] = {
                "evaluable_pairs": n_pairs, "pairs_any": k_any, "rate_any": k_any / n_pairs if n_pairs else None,
                "rate_any_ci95_bootstrap": bootstrap(any_m, rng),
                "pairs_homonym": k_hom, "rate_homonym": k_hom / n_pairs if n_pairs else None,
                "rate_homonym_ci95_bootstrap": bootstrap(hom_m, rng),
                "one_word_per_concept": {"pairs": len(P1) * len(M1), "pairs_any": k1,
                                         "rate": k1 / (len(P1) * len(M1)) if P1 and M1 else None},
                "word_pair_collision": wc, "word_pair_collision_n": wn, "by_name_class": by_class,
                "example_pairs": examples[:40],
            }
        result["languages"][name] = lang
        print(name, {t: (v["rate_any"], v["rate_homonym"]) for t, v in lang["tolerances"].items()}, flush=True)

    # the prediction compares Dravidian with the other languages under T0s, all words
    ref = result["languages"]["dravidian-dedr"]["tolerances"]["T0s"]["rate_any"]
    others = {k: v["tolerances"]["T0s"]["rate_any"] for k, v in result["languages"].items()
              if not k.startswith("dravidian") and v["tolerances"]["T0s"]["rate_any"] is not None}
    full = {k: v for k, v in others.items() if k in ("indoaryan-cdial", "sumerian-epsd2")}
    med = float(np.median(list(full.values()))) if full else None
    result["prediction_single_homophone"] = {
        "rule": "pass if the Dravidian rate (T0s, all words) lies between 0.5 and 2 times the median rate of the full dictionaries (Indo-Aryan CDIAL, Sumerian ePSD2)",
        "dravidian": ref, "others": others, "median_full_dictionaries": med,
        "ratio": (ref / med) if med else None,
        "pass": (med is not None and 0.5 <= ref / med <= 2.0) if med else None,
    }
    # word-level examples are derived from the dictionaries and stay local
    detail = {}
    for name, lang in result["languages"].items():
        for tname, t in lang["tolerances"].items():
            detail[f"{name}/{tname}"] = t.pop("example_pairs")
    local = rebus.RAW / "results-v1" / (outdir.name + "-homophones-detail.json")
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text(json.dumps(detail, ensure_ascii=False, indent=1), encoding="utf-8")
    result["local_detail"] = {"path": str(local.relative_to(rebus.ROOT)).replace("\\", "/"), "sha256": rebus.sha256(local)}
    target.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(result["prediction_single_homophone"], ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
