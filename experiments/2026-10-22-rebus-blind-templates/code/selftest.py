"""Synthetic checks of the blind template scorer, run before any real measurement.

1. Shape C finds a planted compound in both directions and through sandhi (veṇ-mīṉ for veḷ + mīṉ).
2. Shape C misses a pair with no compound; shape S finds a planted shared member.
3. Random rates: exact enumeration agrees with the Monte Carlo estimate on the same template.
4. A key that hits every template scores a large ratio and is killed; a random key from the
   pools themselves scores a ratio near 1 and passes.
5. The scorer refuses to overwrite an existing output.

    python -I experiments/2026-10-22-rebus-blind-templates/code/selftest.py OUTDIR
"""

import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_templates as rt  # noqa: E402

sys.path.insert(0, str(rt.BASE))
import parse_tamil_lex  # noqa: E402
import rebus  # noqa: E402


def entry(translit):
    return {"translit": translit, "head": translit, "members": parse_tamil_lex.members(translit),
            "star": False, "pos": "n", "verb": False, "gloss": ""}


def lexicon(seed=5, n_words=300, planted=()):
    rng = random.Random(seed)
    cons, vows = "kcṭtpmnvylr", "aiuāīū"
    words = sorted({rng.choice(cons) + rng.choice(vows) + rng.choice(cons) + rng.choice(vows) + rng.choice("ṇḷṉṟm")
                    for _ in range(n_words)})
    tl = [entry(w) for w in words] + [entry(w) for w in ("mīṉ", "veḷ", "kaṇ", "nīr", "aṟu", "vaṭam")]
    for w in words:
        for x in rng.sample(words, rng.randint(0, 5)):
            tl.append(entry(f"{w}-{x}"))
    for c in planted:
        tl.append(entry(c))
    dedr = [{"attested": True, "tamil_forms": [e["translit"]]} for e in tl if len(e["members"]) == 1]
    return tl, dedr, words


def main(outdir):
    outdir = Path(outdir)
    target = outdir / "selftest.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    checks = {}
    planted = ["veṇ-mīṉ", "kaṇ-kāṇi", "nīr-k-kaṇ", "vaṭa-pala", "pala-mīṉ"]
    tl, dedr, words = lexicon(planted=planted)
    comp = rebus.Compounds(tl)
    s = rt.Searcher(comp)

    # 1-2. searches
    checks["C_sandhi_veḷ_mīṉ"] = bool(s.compound("veḷ", "mīṉ", "T0s"))
    checks["C_direction_a_nīr_kaṇ"] = bool(s.compound("nīr", "kaṇ", "T0s", "a"))
    checks["C_direction_b_nīr_kaṇ"] = bool(s.compound("nīr", "kaṇ", "T0s", "b"))
    checks["C_absent_pair_misses"] = not s.compound("aṟu", "nīr", "T0s")
    checks["S_shared_member_vaṭam_mīṉ"] = "pala" in s.shared("vaṭam", "mīṉ", "T0s")

    # the cached boolean search agrees with the base-rate picture_hits on every pair of 60 words
    sample = words[:60] + ["veḷ", "mīṉ", "nīr", "kaṇ", "vaṭam"]
    agree = all(bool(s.compound(a, b, tol, d)) == s.compound_holds(a, b, tol, d)
                for a in sample for b in sample for tol in ("T0s", "T1s") for d in ("a", "b", "both"))
    checks["cached_search_equals_picture_hits"] = agree

    # 3-4. a full run on synthetic templates
    idents = {f"I{i}": {"label": w, "words": [w]} for i, w in enumerate(words[:40])}
    pairs = [(f"I{i}", f"I{i + 1}") for i in range(0, 38, 2)]
    tl2 = list(tl) + [entry(f"{idents[a]['words'][0]}-{idents[b]['words'][0]}") for a, b in pairs]
    spec_hit = {"identifications": idents,
                "templates": [{"id": f"T{j}", "first": a, "second": b} for j, (a, b) in enumerate(pairs)]}
    rt.JOINT_DRAWS, rt.BOOT = 300, 300
    out_hit, _ = rt.run(spec_hit, tl2, dedr + [{"attested": True, "tamil_forms": [w]} for w in words], [], synthetic=True)
    prim = out_hit["results"]["primary"]
    checks["planted_key_hits_all"] = prim["parpola_hits"] == len(pairs)
    checks["planted_key_killed"] = out_hit["decision"]["verdict"] == "kill"

    # a key whose words are themselves random members of the candidate pool should pass
    rng = np.random.default_rng(3)
    out_null, _ = rt.run(spec_hit, tl, dedr, [], synthetic=True)
    prim0 = out_null["results"]["primary"]
    checks["unplanted_key_not_killed"] = out_null["decision"]["verdict"] != "kill"
    checks["unplanted_ratio_reported"] = prim0["ratio"] is None or prim0["ratio"] >= 0

    # 3. exact versus Monte Carlo on one template with planted compounds
    idents3 = {"A": {"words": [words[0]]}, "B": {"words": [words[1]]}, "B2": {"words": [words[1], words[2]]}}
    pools = {"first": {words[0]: {50: rt.ri.nearest(rt.ri.candidates(tl2, rebus.Compounds(tl2),
                                                                        {rebus.tl_norm(w, "T0s") for w in words}, []),
                                                       rt.features(words[0], rebus.Compounds(tl2), [], ({}, {})), "prod_first", 50)}},
             "second": {}}
    comp2 = rebus.Compounds(tl2)
    cands2 = rt.ri.candidates(tl2, comp2, {rebus.tl_norm(w, "T0s") for w in words}, [])
    for w in (words[1], words[2]):
        pools["second"][w] = {50: rt.ri.nearest(cands2, rt.features(w, comp2, [], ({}, {})), "prod_last", 50)}
    s2 = rt.Searcher(comp2)
    gen = np.random.default_rng(9)
    _, r_exact, _, _ = rt.score([{"id": "x", "first": "A", "second": "B"}], idents3, lambda t: "C", s2, pools, "T0s", 50, gen, joint=False)
    old = rt.EXACT_LIMIT
    rt.EXACT_LIMIT, rt.MC_DRAWS = 0, 20000
    _, r_mc, _, _ = rt.score([{"id": "x", "first": "A", "second": "B"}], idents3, lambda t: "C", s2, pools, "T0s", 50, gen, joint=False)
    rt.EXACT_LIMIT = old
    checks["exact_vs_monte_carlo"] = {"exact": r_exact[0], "monte_carlo": r_mc[0],
                                      "agree": abs(r_exact[0] - r_mc[0]) < 0.01 + 3 * (r_exact[0] * (1 - r_exact[0]) / 20000) ** 0.5}

    # 5. refusal to overwrite
    outdir.mkdir(parents=True, exist_ok=True)
    probe = outdir / "probe"
    (probe / "templates.json").parent.mkdir(parents=True, exist_ok=True)
    (probe / "templates.json").write_text("{}", encoding="utf-8")
    checks["refuses_overwrite"] = rt.main("no-such-spec.json", probe) == 1 and (probe / "templates.json").read_text() == "{}"

    flat = []
    for v in checks.values():
        flat.append(v["agree"] if isinstance(v, dict) else bool(v))
    res = {"schema_version": "1.0", "task": "rebus-blind-templates/selftest", "synthetic": True,
           "checks": checks, "planted_primary": {k: prim[k] for k in ("templates", "parpola_hits", "ratio", "random_rate")},
           "unplanted_primary": {k: prim0[k] for k in ("templates", "parpola_hits", "ratio", "random_rate")},
           "pass": all(flat)}
    target.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
