"""Synthetic checks of the rebus base-rate code, run before any real measurement.

1. Parpola's own pairs: which tolerance each of his matches needs.
2. Segmentation of each transcription system.
3. Planted homophones and polysemy in a synthetic lexicon.
4. Inventory scaling on a synthetic language with aspiration and voicing contrasts.
5. A planted interlock in synthetic compounds, and its absence.
6. Calibration of the shared-member null: in a synthetic compound lexicon whose
   members are distinct random strings, the rate at which two words share a member
   must equal the exact hypergeometric value.
7. The full interlock pipeline on a synthetic Tamil Lexicon with one planted interlock.

    python -I experiments/2026-10-21-rebus-base-rate/code/selftest.py OUTDIR
"""

import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parse_tamil_lex  # noqa: E402
import rebus  # noqa: E402
import run_interlocks  # noqa: E402

PKG = rebus.ROOT / "experiments" / "2026-10-21-rebus-base-rate"


def eq(a, b, tol):
    if tol == "T0":
        return rebus.tl_norm(a, "T0s") == rebus.tl_norm(b, "T0s")
    if tol == "T0+sandhi":
        return bool({rebus.tl_norm(x, "T0s") for x in rebus.sandhi_bases(a)} & {rebus.tl_norm(x, "T0s") for x in rebus.sandhi_bases(b)})
    return rebus.tl_norm(a, "T1s") == rebus.tl_norm(b, "T1s")


def weakest(a, b):
    for tol in ("T0", "T0+sandhi", "T1"):
        if eq(a, b, tol):
            return tol
    return None


def synthetic_entry(translit, gloss="", star=False, pos="n"):
    return {"translit": translit, "head": "", "members": parse_tamil_lex.members(translit),
            "star": star, "pos": pos, "verb": False, "gloss": gloss}


def main(outdir):
    outdir = Path(outdir)
    target = outdir / "selftest.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    checks = {}

    # 1. Parpola's pairs (2010, pp. 15-28)
    pairs = [("mīṉ", "mīṉ", "fish / star"), ("muruku", "muruku", "youth / ear-ring"),
             ("katir", "katir", "spindle / to shine"), ("piḷḷai", "piḷḷai", "squirrel / child"),
             ("vēḷ", "veḷ", "Murukan / white"), ("veṇ", "vēḷ", "veṇ-mīṉ / Muruka-vēḷ"),
             ("veḷi", "veḷ", "space / white"), ("veḷḷi", "vēḷ", "veḷḷi-mīṉ / Muruka-vēḷ"),
             ("vaṭam", "vaṭa", "banyan / north"), ("muruka", "muruku", "Muruka-vēḷ / muruku")]
    checks["parpola_pairs"] = [{"a": a, "b": b, "meanings": m, "weakest_tolerance": weakest(a, b)} for a, b, m in pairs]
    expected = ["T0", "T0", "T0", "T0", "T0", "T0+sandhi", "T1", "T1", "T0+sandhi", "T1"]
    checks["parpola_pairs_pass"] = [c["weakest_tolerance"] for c in checks["parpola_pairs"]] == expected

    # 2. segmentation
    seg = {
        "dedr_r_underdot": rebus.seg_indic("akakkār̤") == ["a", "k", "a", "k", "k", "ā", "ḻ"],
        "cdial_accent_anusvara": rebus.seg_indic("áṁśa") == ["a", "ṃ", "ś", "a"],
        "aspirate_digraph": rebus.seg_indic("bhāga") == ["bh", "ā", "g", "a"],
        "diphthong": rebus.seg_indic("piḷḷai") == ["p", "i", "ḷ", "ḷ", "ai"],
        "munda_length": rebus.normalise(rebus.seg_ipa("da:ʔ"), ["L"]) == ("d", "a", "ʔ"),
        "sumerian": rebus.seg_sumerian("ŋeštug") == ["ŋ", "e", "š", "t", "u", "g"],
        "gemination_free": rebus.normalise(rebus.seg_indic("veḷḷi"), ["L"]) == ("v", "e", "ḷ", "i"),
        "stem_m": rebus.stem(rebus.normalise(rebus.seg_indic("vaṭam"), ["L"])) == ("v", "a", "ṭ"),
        "stem_keeps_root_nasal": rebus.stem(rebus.normalise(rebus.seg_indic("mīṉ"), ["L"])) == ("m", "i", "ṉ"),
        "stem_keeps_final_y": rebus.stem(rebus.normalise(rebus.seg_indic("nāy"), ["L"])) == ("n", "a", "y"),
    }
    checks["segmentation"] = seg

    # 3. planted homophones
    pics = [{"id": "p1", "key": "arrow"}, {"id": "p2", "key": "fish"}, {"id": "p3", "key": "tree"}]
    names = [{"id": "n1", "key": "life", "class": "quality"}, {"id": "n2", "key": "star", "class": "celestial"}]
    lex = [
        {"id": "a", "forms": [tuple(rebus.seg_indic("ti"))], "items": {"arrow"}, "attested": True, "weight": 3},
        {"id": "b", "forms": [tuple(rebus.seg_indic("tī"))], "items": {"life"}, "attested": True, "weight": 2},
        {"id": "c", "forms": [tuple(rebus.seg_indic("mīn"))], "items": {"fish", "star"}, "attested": True, "weight": 5},
        {"id": "d", "forms": [tuple(rebus.seg_indic("maram"))], "items": {"tree"}, "attested": True, "weight": 5},
        {"id": "e", "forms": [tuple(rebus.seg_indic("maram"))], "items": {"star"}, "attested": False, "weight": 1},
    ]
    idx = rebus.concept_index(lex, pics + names)
    P, M, any_m, hom_m, _ = rebus.pair_matrix(idx, pics, names, lambda f: rebus.normalise(f, ["L"]))
    got_any = {(P[i], M[j]) for i in range(len(P)) for j in range(len(M)) if any_m[i][j]}
    got_hom = {(P[i], M[j]) for i in range(len(P)) for j in range(len(M)) if hom_m[i][j]}
    checks["planted_homophones"] = {"any": sorted(got_any), "homonym": sorted(got_hom),
                                    "pass": got_any == {("p1", "n1"), ("p2", "n2")} and got_hom == {("p1", "n1")}}

    # 4. inventory scaling
    rich = [rebus.seg_indic(w) for w in ["bhaga", "phala", "gadha", "kata", "ghaṭa", "daṇḍa", "thala", "bandha"] * 5]
    target_c = rebus.collision([rebus.normalise(f, ["L", "A", "V"]) for f in rich])
    steps, trail = rebus.scale_steps(rich, target_c)
    checks["inventory_scaling"] = {"steps": "".join(steps), "pass": steps == ["L", "A", "V"], "trail": trail}

    # 5. planted interlock
    ents = [synthetic_entry(t) for t in ["kalu-vēḷ", "kalu-tōṭu", "veṇ-pāṉ", "maram-pāṉ", "kalu", "pāṉ"]]
    comp = rebus.Compounds(ents)
    sh = run_interlocks.i1(comp, "kalu", "pāṉ", "T0s")
    ents2 = [synthetic_entry(t) for t in ["kalu-tōṭu", "veṇ-pāṉ", "maram-pāṉ"]]
    sh2 = run_interlocks.i1(rebus.Compounds(ents2), "kalu", "pāṉ", "T0s")
    checks["planted_interlock"] = {"shared": sh, "absent_case": sh2, "pass": list(sh) == ["veḷ"] and not sh2}

    # 6. null calibration against the hypergeometric value
    rng = random.Random(7)
    cons, vows = "kcṭtpmnyrlv", "aiuo"
    vocab = set()
    while len(vocab) < 300:
        w = "".join(rng.choice(cons) + rng.choice(vows) for _ in range(2)) + rng.choice(cons) + rng.choice("iuo")
        vocab.add(w)
    vocab = sorted(vocab)
    stems = {rebus.tl_norm(w, "T1s") for w in vocab}
    nA, nB = 6, 9
    entries = []
    # anchors are distinct words absent from the member vocabulary
    anchors1 = ["tū%saṟ" % c for c in "kcṭtpmnyrl"]
    anchors2 = ["vē%siḷ" % c for c in "kcṭtpmnyrl"]
    for a in anchors1:
        for x in rng.sample(vocab, nA):
            entries.append(synthetic_entry(f"{a}-{x}"))
    for b in anchors2:
        for x in rng.sample(vocab, nB):
            entries.append(synthetic_entry(f"{x}-{b}"))
    comp6 = rebus.Compounds(entries)
    hits = sum(bool(run_interlocks.i1(comp6, a, b, "T0s")) for a in anchors1 for b in anchors2)
    V = len(vocab)
    exact = 1 - math.comb(V - nA, nB) / math.comb(V, nB)
    rate = hits / (len(anchors1) * len(anchors2))
    # repeat over many synthetic draws to compare with the exact value
    total, n = 0, 0
    for rep in range(30):
        entries = []
        for a in anchors1:
            for x in rng.sample(vocab, nA):
                entries.append(synthetic_entry(f"{a}-{x}"))
        for b in anchors2:
            for x in rng.sample(vocab, nB):
                entries.append(synthetic_entry(f"{x}-{b}"))
        c = rebus.Compounds(entries)
        total += sum(bool(run_interlocks.i1(c, a, b, "T0s")) for a in anchors1 for b in anchors2)
        n += len(anchors1) * len(anchors2)
    se = math.sqrt(exact * (1 - exact) / n)
    checks["null_calibration"] = {"vocabulary": V, "distinct_T1_stems": len(stems), "nA": nA, "nB": nB,
                                  "exact_rate": exact, "observed_rate": total / n, "pairs": n,
                                  "z": (total / n - exact) / se, "pass": abs(total / n - exact) < 4 * se}

    # 7. full pipeline on a synthetic Tamil Lexicon
    rng7 = random.Random(11)
    words = sorted({"".join(rng7.choice(cons) + rng7.choice(vows) for _ in range(2)) + rng7.choice("ṇḷṉṟ")
                    for _ in range(400)})
    tl = [synthetic_entry(w) for w in words]
    tl += [synthetic_entry("muruku"), synthetic_entry("mīṉ"), synthetic_entry("kaṭavuḷ"),
           synthetic_entry("muruka-vēḷ", "Skanda"), synthetic_entry("veṇ-mīṉ", "Venus, the planet"),
           synthetic_entry("vaṭa-mīṉ", "Alcor, a star"), synthetic_entry("aṟu-mīṉ", "the Pleiades")]
    for w in words:
        for x in rng7.sample(words, rng7.randint(0, 6)):
            tl.append(synthetic_entry(f"{w}-{x}"))
    for x in rng7.sample(words, 20):
        tl.append(synthetic_entry(f"{x}-mīṉ", "a fish"))
    for x in rng7.sample(words, 5):
        tl.append(synthetic_entry(f"muruka-{x}", "a name of Skanda"))
    for x in rng7.sample(words, 8):
        tl.append(synthetic_entry(f"{x}-kaṭavuḷ", "a deity"))
    for e in tl:
        e["head"] = e["translit"]
    dedr = [{"attested": True, "items": {"banyan"}, "tamil_forms": ["vaṭam"], "forms": [], "id": "x1"},
            {"attested": True, "items": {"squirrel"}, "tamil_forms": ["aṇil"], "forms": [], "id": "x2"},
            {"attested": True, "items": {"spindle"}, "tamil_forms": ["katir"], "forms": [], "id": "x3"}]
    dedr += [{"attested": True, "items": {f"thing{i}"}, "tamil_forms": [w], "forms": [], "id": f"w{i}"}
             for i, w in enumerate(words + ["muruku", "mīṉ", "kaṭavuḷ"])]
    syn_pools = {"picture": [{"id": f"c{i}", "key": f"thing{i}"} for i in range(60)]}
    tokens = sorted(words * 3)
    saved = (run_interlocks.DRAWS, run_interlocks.BOOT)
    run_interlocks.DRAWS, run_interlocks.BOOT = 500, 200
    syn = run_interlocks.run(outdir, tl, dedr, tokens, {}, syn_pools, synthetic=True)
    run_interlocks.DRAWS, run_interlocks.BOOT = saved
    checks["pipeline"] = {"real_I1_T0s": syn["real"]["I1_T0s"]["shared"], "real_I2_T0s": syn["real"]["I2_T0s"],
                          "I1_null_rate_T0s": syn["null"]["I1_T0s"]["K50"]["rate"],
                          "pass": "veḷ" in syn["real"]["I1_T0s"]["shared"] and syn["real"]["I2_T0s"] == ["vaṭa-mīṉ"]}

    passed = all(v["pass"] if isinstance(v, dict) and "pass" in v else True for v in checks.values()) \
        and checks["parpola_pairs_pass"] and all(seg.values())
    out = {"schema_version": "1.0", "task": "rebus-base-rate/selftest", "synthetic": True,
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "provenance": {"code": {p.name: rebus.sha256(p) for p in sorted((PKG / "code").glob("*.py"))}},
           "checks": checks, "pass": passed}
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=list), encoding="utf-8")
    print(json.dumps({k: (v.get("pass", v) if isinstance(v, dict) else v) for k, v in checks.items()
                      if k != "parpola_pairs"}, ensure_ascii=False))
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
