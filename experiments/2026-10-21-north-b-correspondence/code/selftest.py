"""Synthetic entries with known answers for dedr_parts.py and count.py.

Each case reproduces a page-format trap named in PROTOCOL.md, step 2. The forms are
invented strings in DEDR's transcription, not dictionary entries.

    python -I experiments/2026-10-21-north-b-correspondence/code/selftest.py --out <path>
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import count  # noqa: E402
import dedr_parts as dp  # noqa: E402


def page(*entries):
    return "".join(f'<div>\n<span class="new_p"><number>{n}</number> {body}</span>\n</div>' for n, body in entries)


def lines_of(rec, letter=""):
    part = next(p for p in rec["parts"] if p["letter"] == letter)
    return [(ln["lang"], [(f["form"], f["initial_class"], f["doubt"], f["borrowed"]) for f in ln["forms"]]) for ln in part["lines"]]


CHECKS = []


def check(name, got, want):
    CHECKS.append({"case": name, "ok": got == want, "got": repr(got), "want": repr(want)})


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # 1. label after a grammatical label in one italic run; 12. label with ';' and without '.'
    rec = dp.parse_entry("1", '<b><i>Ta.</i> malar</b> to open. <b><i>(tr.). Malt.</i> balre</b> to open. '
                              '<b><i>Kur</i> malkh</b> id.', 1)
    check("label after grammatical label", lines_of(rec),
          [("Tamil", [("malar", "m", False, False)]), ("Malto", [("balre", "b", False, False)]),
           ("Kurukh", [("malkh", "m", False, False)])])

    # 2. bold cross-reference with a label does not start a line or add a form
    rec = dp.parse_entry("2", '<b><i>Ta.</i> vaṭi</b> to drip. <b><i>Kur.</i> baṛ-</b> to drip. Cf. 37 <b>Ta. maṭi</b>.', 1)
    check("bold cross-reference", lines_of(rec),
          [("Tamil", [("vaṭi", "v", False, False)]), ("Kurukh", [("baṛ-", "b", False, False)])])

    # 3. doubtful label; 8. a gloss ending in a question mark does not mark the next line
    rec = dp.parse_entry("3", '<b><i>Ta.</i> māṉ</b> who? <b><i>Ma.</i> māṉ</b> id. ? <b><i>Kur.</i> bānō</b> id. '
                              '<b><i>Malt.</i> ?bano</b> id.', 1)
    check("doubt marks", lines_of(rec),
          [("Tamil", [("māṉ", "m", False, False)]), ("Malayalam", [("māṉ", "m", False, False)]),
           ("Kurukh", [("bānō", "b", True, False)]), ("Malto", [("bano", "b", True, False)])])

    # 4. borrowed form, and 'borrowed' in a line
    rec = dp.parse_entry("4", '<b><i>Ta.</i> maṉ</b> honour. <b><i>Kur.</i> bān, mān</b> honour (&lt; IA). '
                              '<b><i>Malt.</i> mane</b> house; borrowed from Kur.', 1)
    check("borrowed forms", lines_of(rec),
          [("Tamil", [("maṉ", "m", False, False)]),
           ("Kurukh", [("bān", "b", False, False), ("mān", "m", False, True)]),
           ("Malto", [("mane", "m", False, True)])])

    # 5. lettered sub-entries in separate spans; 14. plain-text marker before an italic label
    body = ('<b><i>(a) Ta.</i> veḷ</b> white. <b><i>Kur.</i> bel</b> white.</span><span class="new_p">'
            '<b><i>(b) Ta.</i> mīṉ</b> fish. <b><i>Malt.</i> mínu</b> fish. (c) <i>Ta.</i> <b>mūcu</b> to cover. '
            '<b><i>Kur.</i> mūc-</b> id.')
    rec = dp.parse_entry("5", body, 1)
    check("lettered parts", [p["letter"] for p in rec["parts"]], ["a", "b", "c"])
    check("part a", lines_of(rec, "a"), [("Tamil", [("veḷ", "v", False, False)]), ("Kurukh", [("bel", "b", False, False)])])
    check("part b", lines_of(rec, "b"), [("Tamil", [("mīṉ", "m", False, False)]), ("Malto", [("mínu", "m", False, False)])])
    check("part c", lines_of(rec, "c"), [("Tamil", [("mūcu", "m", False, False)]), ("Kurukh", [("mūc-", "m", False, False)])])

    # 7. comparison notes after ' / ' are cut
    rec = dp.parse_entry("7", '<b><i>Ta.</i> miṭai</b> to weave. <b><i>Kur.</i> miṭ-</b> id. / Cf. Skt. <b>mṛ-</b>; '
                              '<b><i>Malt.</i> biṭe</b> id. DED 1.', 1)
    check("comparison cut", (lines_of(rec), rec["parts"][0]["cut"]),
          ([("Tamil", [("miṭai", "m", False, False)]), ("Kurukh", [("miṭ-", "m", False, False)])], True))

    # 9. optional initial letter; 13. Latin name before a label in one italic run
    rec = dp.parse_entry("9", '<b><i>Ta.</i> (v)iṇ</b> sky. <i>Shorea robusta. Malt.</i> <b>bīnde</b> sky.', 1)
    check("optional letter and Latin name", lines_of(rec),
          [("Tamil", [("viṇ", "v", False, False)]), ("Malto", [("bīnde", "b", False, False)])])

    # 10, 11. vowel classes, nasal flag, accents and bh
    vc = {w: dp.vowel_context(w) for w in ["mīṉ", "bínḍke", "mūnd", "veḷ", "mai", "bhal", "mrag", "bīnkō", "ēru", "me·n"]}
    check("vowel context", vc, {"mīṉ": ("long front", True), "bínḍke": ("short front", True), "mūnd": ("long back", True),
                                "veḷ": ("short front", False), "mai": ("diphthong", False), "bhal": ("short back", False),
                                "mrag": ("none", False), "bīnkō": ("long front", True), "ēru": ("none", False),
                                "me·n": ("long front", True)})
    check("bh flag", dp.initial_class("bhal"), ("b", True))
    check("accent removed from initial", dp.initial_class("bínḍke"), ("b", False))

    # 6. repeated prints: the longest is used and shorter prints are prefixes
    short = '<b><i>(a) Ta.</i> mal</b> to fold.'
    long_ = short + '</span><span class="new_p"><b><i>(b) Ta.</i> maṭi</b> fold. <b><i>Kur.</i> baṛ-</b> to fold.'
    pg = page(("6", short), ("6", long_), ("8", '<b><i>Ta.</i> vāy</b> mouth. <b><i>Kur.</i> bāy</b> mouth.'))
    recs, fails = dp.build([(1, pg, hashlib.sha256(pg.encode()).hexdigest())])
    check("repeated print", ([r["entry"] for r in recs], recs[0]["n_prints"], [p["letter"] for p in recs[0]["parts"]], fails),
          (["6", "8"], 2, ["a", "b"], []))

    # 15. labels DSAL set in plain type: a line after a gloss end, a citation after "Cf. 52"
    rec = dp.parse_entry("15", '<b><i>Ta.</i> māy</b> to yawn. <b><i>Kur.</i> bāynā</b> to yawn. Malt. <b>báye</b> id. '
                               'Br. <b>bāy</b> id. Cf. 52 Kur. <b>mīknā</b>.', 1)
    check("plain-type lines and citation", lines_of(rec),
          [("Tamil", [("māy", "m", False, False)]), ("Kurukh", [("bāynā", "b", False, False)]),
           ("Malto", [("báye", "b", False, False)]), ("Brahui", [("bāy", "b", False, False)])])
    # 16. a botanical authority "R. Br." before an italic label is not Brahui
    rec = dp.parse_entry("16", '<b><i>Ta.</i> kāval</b> a tree, S. nobilis R. Br. <b><i>Ma.</i> kāvaḷ</b> id.', 1)
    check("R. Br. is not a label", [ln["lang"] for ln in rec["parts"][0]["lines"]], ["Tamil", "Malayalam"])
    # 17. a plain label that moves backwards in DEDR's order cites another entry
    rec = dp.parse_entry("17", '<b><i>Kur.</i> mal</b> hill. <b><i>Malt.</i> male</b> hill. Ta. <b>malai</b> mountain.', 1)
    check("plain label out of order", lines_of(rec),
          [("Kurukh", [("mal", "m", False, False)]), ("Malto", [("male", "m", False, False)])])
    # 18. an italic label after "Cf." and an entry number cites another entry
    rec = dp.parse_entry("18", '<b><i>Ta.</i> vaḷ</b> sharp. <b><i>Kur.</i> bal</b> id. Cf. 12 <i>Malt.</i> <b>mal</b>.', 1)
    check("italic citation", lines_of(rec),
          [("Tamil", [("vaḷ", "v", False, False)]), ("Kurukh", [("bal", "b", False, False)])])
    # 19. a print that is not a prefix of the longest print is a different entry under the same number
    pg = page(("20", '<b><i>Ta.</i> vali</b> to pull. <b><i>Kur.</i> balnā</b> id.'),
              ("20", '<b><i>Ta.</i> viku</b> to be tight. <b><i>Ma.</i> viku</b> id. <b><i>Kur.</i> bik-</b> id.'))
    recs, fails = dp.build([(1, pg, "x")])
    check("misnumbered print", ([r["entry"] for r in recs], [r["misnumbered_print"] for r in recs], fails),
          (["20", "20/2"], [False, True], ["20"]))

    # counting: pass rule on a synthetic dictionary
    synth = page(
        ("4876", '<b><i>Ta.</i> miṉ</b> to shine. <b><i>Kur.</i> bīnkō</b> star. <b><i>Malt.</i> bínḍke</b> star.'),
        ("10", '<b><i>Ta.</i> māl</b> big. <b><i>Kur.</i> bāl</b> big.'),
        ("11", '<b><i>Ta.</i> mīḷ</b> return. ? <b><i>Kur.</i> bīl-</b> return. <b><i>Malt.</i> mīle</b> id.'),
        ("12", '<b><i>Ta.</i> vaḷ</b> sharp. <b><i>Malt.</i> bal</b> sharp.'),
        ("13", '<b><i>Ta.</i> mūṉṟu</b> three. <b><i>Kur.</i> mūnd</b> three.'),
    )
    recs, _ = dp.build([(1, synth, "x")])
    res = count.run(recs)
    check("pass rule: one undoubted entry is unresolved", (res["pass_rule"]["entries_counted_for_pass"], res["pass_rule"]["outcome"]),
          (["10"], "unresolved"))
    check("doubtful case listed", [(c["entry"], c["doubtful"]) for c in res["cases"]["tamil_m_northern_b"]],
          [("4876", False), ("4876", False), ("10", False), ("11", True)])
    synth2 = synth + page(("14", '<b><i>Ta.</i> mōr</b> buttermilk. <b><i>Malt.</i> bōre</b> id.'))
    recs, _ = dp.build([(1, synth2, "x")])
    res2 = count.run(recs)
    check("pass rule: two entries pass", (res2["pass_rule"]["entries_counted_for_pass"], res2["pass_rule"]["outcome"]),
          (["10", "14"], "pass"))
    synth3 = page(
        ("4876", '<b><i>Ta.</i> miṉ</b> to shine. <b><i>Kur.</i> bīnkō</b> star.'),
        ("12", '<b><i>Ta.</i> vaḷ</b> sharp. <b><i>Malt.</i> bal</b> sharp.'),
        ("13", '<b><i>Ta.</i> mūṉṟu</b> three. <b><i>Kur.</i> mūnd</b> three.'),
    )
    recs, _ = dp.build([(1, synth3, "x")])
    res3 = count.run(recs)
    check("pass rule: failure", res3["pass_rule"]["outcome"], "failure")
    check("primary table", res3["primary"]["first_undoubted_form"]["without_4876"]["m"]["pooled"], {"m": 1, "b": 0, "v": 0, "other": 0})

    ok = all(c["ok"] for c in CHECKS)
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"all_passed": ok, "n_checks": len(CHECKS), "checks": CHECKS}, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8", newline="\n")
    for c in CHECKS:
        if not c["ok"]:
            print("FAIL", c["case"], "got", c["got"], "want", c["want"])
    print(json.dumps({"all_passed": ok, "n_checks": len(CHECKS)}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
