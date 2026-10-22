"""Synthetic checks of the Winslow parser and run, made before the real run.

1. Transliteration of Tamil script into the DSAL romanisation.
2. The junction rule on hand-made sub-entries: first-member and second-member
   compounds, sandhi doubling, glides, the preference for a consonant-initial
   second member, and derivatives that must not split.
3. parse_page on a synthetic page in Winslow's DSAL markup.
4. Compatibility with the frozen Compounds class: veṇ-mīṉ and muruka-vēḷ, split
   by our rule, meet in veḷ through rebus.sandhi_bases.
5. The full run wrapper on a synthetic Winslow table with one planted interlock,
   with reduced draw counts.

    python -I experiments/2026-10-22-rebus-winslow/code/selftest.py OUTDIR
"""

import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parse_winslow as pw  # noqa: E402
import run_winslow  # noqa: E402
from run_winslow import rebus, run_interlocks  # noqa: E402

PKG = run_winslow.PKG


def main(outdir):
    outdir = Path(outdir)
    target = outdir / "selftest.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    checks = {}

    # 1. transliteration
    tr = {"மீன்": "mīṉ", "முருகக்கடவுள்": "murukakkaṭavuḷ", "வெண்மீன்": "veṇmīṉ", "கைக்கிளை": "kaikkiḷai",
          "அஃது": "aḵtu", "சாழையகத்தி": "cāḻaiyakatti", "கௌரி": "kauri", "பொன்": "poṉ", "ஷண்முகன்": "ṣaṇmukaṉ"}
    checks["transliteration"] = {"cases": {k: pw.translit(k) for k in tr},
                                 "pass": all(pw.translit(k) == v for k, v in tr.items())}

    # 2. junction rule
    words = pw.Words(["mīṉ", "eṇṇey", "koṭi", "añcaṉam", "kalikkam", "akatti", "cāḻai", "kaṭavuḷ", "aṟu", "veḷ",
                      "maram", "kāl", "kal", "aṟai", "kaḷam", "ati", "mati", "kālam", "akai", "vakai", "kutirai",
                      "ōṭṭam", "kali", "pū", "āṭu", "kuṭṭi", "ēṇṇey"])
    cases = [
        ("mīṉeṇṇey", ["mīṉ"], ["mīṉ", "eṇṇey"], "first"),
        ("añcaṉakkalikkam", ["añcaṉam"], ["añcaṉa", "kalikkam"], "first"),
        ("cāḻaiyakatti", ["akatti"], ["cāḻai", "akatti"], "second"),
        ("aṟukkaṭavuḷ", ["kaṭavuḷ"], ["aṟu", "kaṭavuḷ"], "second"),
        ("veṇmīṉ", ["mīṉ"], ["veṇ", "mīṉ"], "second"),
        ("veṇmīṉ", ["veḷ"], ["veṇ", "mīṉ"], "first"),
        ("kallaṟai", ["kal"], ["kall", "aṟai"], "first"),
        ("kaḷamati", ["kaḷam"], ["kaḷa", "mati"], "first"),
        ("kālavakai", ["kālam"], ["kāla", "vakai"], "first"),
        ("kutiraiyōṭṭam", ["kutirai"], ["kutirai", "ōṭṭam"], "first"),
        ("āṭṭukkuṭṭi", ["āṭu"], ["āṭṭu", "kuṭṭi"], "first"),
        ("mīṉeṇṇey", ["mīṉ"], ["mīṉ", "eṇṇey"], "first"),
        ("kalippu", ["kali"], None, None),
        ("marakkalam", ["mīṉ"], None, None),
    ]
    got = []
    for s, roots, members, rule in cases:
        m, r = pw.segment(s, roots, words)
        got.append({"s": s, "roots": roots, "got": m, "rule": r, "ok": m == members and r == rule})
    checks["junction_rule"] = {"cases": got, "pass": all(g["ok"] for g in got)}

    # 3. parse_page on Winslow markup
    page = """<div>
<span class="new_p">*<hw><tam><b>மீன்</b> <b>mīṉ</b></tam></hw>, <i><pos>s.</pos></i> A fish, <tam>மச்சம்</tam>. 2. A star. <i>(c.)</i> <p2><tam>மீனெண்ணெய்</tam>, <i><pos>s.</pos></i> Fish oil.</p2> <p2><tam>வெண்மீன்</tam>–<tam>வெள்ளிமீன்</tam>, <i><pos>s.</pos></i> Venus.</p2> <p2><tam>மீன்பிடித்தல்</tam>. Fishing.</p2></span>
</div>
<div>
<hw><tam><b>அகப்பகை</b> <b>akappakai</b></tam></hw>, <i><pos>s.</pos></i> [<i>ex</i> <tam>அகம்</tam>, inside, <i>et</i> <tam>பகை</tam>.] Secret enmity.</span>
</div>
<div>
<hw><tam><b>அடங்கு</b> <b>aṭaṅku</b></tam></hw>, <tam>கிறேன்</tam>, <i>v. n.</i> To obey.</span>
</div>
<div>
<hw><tam><b>வெள்ளி</b> <b>veḷḷi</b></tam></hw>, <i><pos>s.</pos></i> Silver.</span>
</div>
<div>
<hw><tam><b>எண்ணெய்</b> <b>eṇṇey</b></tam></hw>, <i><pos>s.</pos></i> Oil.</span>
</div>
<div>
<hw><tam><b>வெள்</b> <b>veḷ</b></tam></hw>, <i><pos>s.</pos></i> White.</span>
</div>
<div>
<hw><tam><b>பகை</b> <b>pakai</b></tam></hw>, <i><pos>s.</pos></i> Enmity.</span>
</div>"""
    recs = pw.build([(1, page)])
    by = {r["head"]: r for r in recs}
    p3 = {
        "principal_noun": by["மீன்"]["pos"] == "n" and by["மீன்"]["asterisk"] and by["மீன்"]["members"] == ["mīṉ"],
        "first_member_sub": by["மீனெண்ணெய்"]["members"] == ["mīṉ", "eṇṇey"],
        "alternate_forms_split": by["வெண்மீன்"]["members"] == ["veṇ", "mīṉ"] and by["வெள்ளிமீன்"]["members"] == ["veḷḷi", "mīṉ"],
        "sentence_without_pos_unsplit": by["மீன்பிடித்தல்"]["members"] == [],
        "etymology_compound": by["அகப்பகை"]["members"] == ["aka", "pakai"] and by["அகப்பகை"]["seg"] == "ety",
        "verb_label": by["அடங்கு"]["verb"] and by["அடங்கு"]["pos"] == "v. n.",
    }
    checks["parse_page"] = {"cases": p3, "pass": all(p3.values())}

    # 4. compatibility with the frozen Compounds class
    ents = [{"translit": "-".join(m), "members": m, "head": "", "star": False, "pos": "n", "verb": False, "gloss": ""}
            for m in (["veṇ", "mīṉ"], ["muruka", "vēḷ"], ["muruka", "kaṭavuḷ"], ["maram", "mīṉ"])]
    sh = run_interlocks.i1(rebus.Compounds(ents), "muruku", "mīṉ", "T0s")
    checks["compounds_compatibility"] = {"shared": sorted(sh), "pass": sorted(sh) == ["veḷ"]}

    # 5. full wrapper on a synthetic Winslow table
    rng = random.Random(13)
    cons, vows = "kcṭtpmnyrlv", "aiuo"
    ws = sorted({"".join(rng.choice(cons) + rng.choice(vows) for _ in range(2)) + rng.choice("ṇḷṉṟ") for _ in range(400)})

    def ent(members, gloss=""):
        return {"page": 1, "kind": "sub" if len(members) == 2 else "principal", "head": "-".join(members),
                "translit": "-".join(members), "members": members, "seg": "first" if len(members) == 2 else None,
                "star": False, "pos": "n", "verb": False, "gloss": gloss}
    tl = [ent([w]) for w in ws + ["muruku", "mīṉ", "kaṭavuḷ"]]
    tl += [ent(["muruka", "vēḷ"], "Skanda"), ent(["veṇ", "mīṉ"], "Venus"), ent(["vaṭa", "mīṉ"], "Alcor, a star")]
    for w in ws:
        for x in rng.sample(ws, rng.randint(0, 6)):
            tl.append(ent([w, x]))
    for x in rng.sample(ws, 20):
        tl.append(ent([x, "mīṉ"], "a fish"))
    for x in rng.sample(ws, 5):
        tl.append(ent(["muruka", x], "a name of Skanda"))
    for x in rng.sample(ws, 8):
        tl.append(ent([x, "kaṭavuḷ"], "a deity"))
    dedr = [{"attested": True, "items": {"banyan"}, "tamil_forms": ["vaṭam"], "forms": [], "id": "x1"},
            {"attested": True, "items": {"squirrel"}, "tamil_forms": ["aṇil"], "forms": [], "id": "x2"},
            {"attested": True, "items": {"spindle"}, "tamil_forms": ["katir"], "forms": [], "id": "x3"}]
    dedr += [{"attested": True, "items": {f"thing{i}"}, "tamil_forms": [w], "forms": [], "id": f"w{i}"}
             for i, w in enumerate(ws + ["muruku", "mīṉ", "kaṭavuḷ"])]
    syn_pools = {"picture": [{"id": f"c{i}", "key": f"thing{i}"} for i in range(60)]}
    saved = (run_interlocks.DRAWS, run_interlocks.BOOT)
    run_interlocks.DRAWS, run_interlocks.BOOT = 500, 200
    syn = run_winslow.evaluate(tl, dedr, sorted(ws * 3), {}, syn_pools, outdir / "pipeline")
    run_interlocks.DRAWS, run_interlocks.BOOT = saved
    checks["pipeline"] = {"real_I1_T0s": syn["real"]["I1_T0s"]["shared"], "real_I2_T0s": syn["real"]["I2_T0s"],
                          "P2_rate": syn["decision"]["P2_rate"], "P2_pass": syn["decision"]["P2_pass"],
                          "compound_lists_removed": not any(k in syn["real"] for k in run_winslow.DETAIL_KEYS),
                          "pass": "veḷ" in syn["real"]["I1_T0s"]["shared"] and syn["real"]["I2_T0s"] == ["vaṭa-mīṉ"]
                          and not any(k in syn["real"] for k in run_winslow.DETAIL_KEYS)}

    passed = all(v["pass"] for v in checks.values())
    out = {"schema_version": "1.0", "task": "rebus-winslow/selftest", "synthetic": True,
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "provenance": {"code": {p.name: rebus.sha256(p) for p in sorted((PKG / "code").glob("*.py"))},
                          "reused_code": {n: rebus.sha256(run_winslow.BASE_CODE / n)
                                          for n in ("rebus.py", "run_interlocks.py", "parse_tamil_lex.py")}},
           "checks": checks, "pass": passed}
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=list), encoding="utf-8")
    print(json.dumps({k: v["pass"] for k, v in checks.items()}, ensure_ascii=False))
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
