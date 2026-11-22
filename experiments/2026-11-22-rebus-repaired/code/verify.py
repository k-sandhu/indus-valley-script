"""Independent verification and synthetic sanity checks for REBUS-REPAIRED-2026-11-22.

Does NOT import run_tamil_repaired.py, run_sanskrit_control.py, or lexical_inputs.py.
Recomputes exact Sangam token counts, Tamil Lexicon / Winslow / Monier-Williams compound
indices, real hits on the 38 blind and 12 published pairs, and verifies sign-level joint
random-key mechanics on synthetic planted and unplanted lexicons.

Run from repository root after the main scripts:
    python experiments/2026-11-22-rebus-repaired/code/verify.py
"""

import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
RESULTS = PKG / "results-v1"
TEMPLATES_PATH = ROOT / "experiments" / "2026-10-22-rebus-blind-templates" / "templates-v1.json"
TL_PATH = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1" / "tamil-lex-entries.jsonl"
SANGAM_DIR = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "sangam"
WINSLOW_PATH = ROOT / "data" / "raw" / "2026-10-24-lexical-extraction-extension" / "run-v1" / "winslow-entries.jsonl"
MW_PATH = ROOT / "data" / "raw" / "2026-10-12-decipherment-claim-tests" / "mw" / "mw.txt"

VOWELS = set("aeiouāīūēō")
LONG = {"ā": "a", "ī": "i", "ū": "u", "ē": "e", "ō": "o", "ṝ": "ṛ", "ḹ": "ḷ"}
SANDHI_TA = {"ṇ": ["ḷ"], "ṉ": ["l"], "ṅ": ["m"], "ñ": ["m"], "n": ["m"], "ṭ": ["ḷ"], "ṟ": ["l"]}

SLP1_MAP = {
    "a": "a", "A": "ā", "i": "i", "I": "ī", "u": "u", "U": "ū",
    "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ", "e": "e", "E": "ai", "o": "o", "O": "au",
    "M": "ṃ", "H": "ḥ",
    "k": "k", "K": "kh", "g": "g", "G": "gh", "N": "ṅ",
    "c": "c", "C": "ch", "j": "j", "J": "jh", "Y": "ñ",
    "w": "ṭ", "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ",
    "t": "t", "T": "th", "d": "d", "D": "dh", "n": "n",
    "p": "p", "P": "ph", "b": "b", "B": "bh", "m": "m",
    "y": "y", "r": "r", "l": "l", "v": "v",
    "S": "ś", "z": "ṣ", "s": "s", "h": "h", "L": "ḷ",
}
SLP1_CONS = set("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL")


def indep_seg(form):
    s = unicodedata.normalize("NFC", form.lower())
    s = s.replace("r̤", "ḻ").replace("ṁ", "ṃ").replace("ŭ", "u").replace("ů", "u").replace("ĕ", "e").replace("ŏ", "o")
    s = re.sub(r"[^a-zāīūēōṛṝḷḹṃḥśṣṅñṭḍṇḻḷṟṉḵ]", "", s)
    out = []
    i = 0
    while i < len(s):
        if s[i:i + 2] in ("ai", "au") or (i + 1 < len(s) and s[i + 1] == "h" and s[i] in "kgcjṭḍtdpb"):
            out.append(s[i:i + 2])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return out


def indep_norm(form, t1=False):
    toks = [LONG.get(t, t) for t in indep_seg(form)]
    out = []
    for t in toks:
        if not out or out[-1] != t:
            out.append(t)
    if t1:
        if len(out) >= 4 and out[-1] == "m" and (out[-2] in ("ai", "au") or out[-2] in VOWELS):
            out.pop()
        if len(out) >= 3 and (out[-1] in ("ai", "au") or out[-1] in VOWELS):
            out.pop()
    return tuple(out)


def ta_sandhi(m):
    s = {m}
    if m.endswith("a"):
        s |= {m + "m", m + "ṉ"}
    for alt in SANDHI_TA.get(m[-1:], ()):
        s.add(m[:-1] + alt)
    return s


def skt_sandhi(m):
    s = {m}
    if not m:
        return s
    last = m[-1]
    if last in ("a", "i", "A", "I"):
        s.add(m + "n")
    if last == "o":
        s.add(m[:-1] + "as")
    if last in ("r", "H", "S", "z"):
        s.add(m[:-1] + "s")
    if last in ("w", "q", "R"):
        s |= {m[:-1] + "z", m[:-1] + "w", m[:-1] + "q"}
    if last == "d":
        s.add(m[:-1] + "t")
    if last == "g":
        s |= {m[:-1] + "k", m[:-1] + "c"}
    if last == "k":
        s.add(m[:-1] + "c")
    if last == "b":
        s.add(m[:-1] + "p")
    if last == "j":
        s.add(m[:-1] + "c")
    if last in ("M", "n"):
        s.add(m[:-1] + "m")
    if len(m) >= 2 and last == "y" and m[-2] in SLP1_CONS:
        s.add(m[:-1] + "i")
    if len(m) >= 2 and last == "v" and m[-2] in SLP1_CONS:
        s.add(m[:-1] + "u")
    return s


def check_sangam():
    counts = Counter()
    total_lm = 0
    total_raw_block = 0
    for p in sorted(SANGAM_DIR.glob("pmuni*.html")):
        txt = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
        total_raw_block += len(re.findall(r"[\u0b80-\u0bff]+", txt))
        txt = unicodedata.normalize("NFC", txt)
        buf = []
        for ch in txt:
            if "\u0b80" <= ch <= "\u0bff" and unicodedata.category(ch)[0] in ("L", "M"):
                buf.append(ch)
            elif buf:
                tok = "".join(buf)
                counts[tok] += 1
                total_lm += 1
                buf = []
        if buf:
            tok = "".join(buf)
            counts[tok] += 1
            total_lm += 1
    return {
        "total_tokens_lm": total_lm,
        "total_tokens_raw_block": total_raw_block,
        "exact_ka": counts["கா"],
        "exact_aa": counts["ஆ"],
        "exact_aru": counts["அறு"],
        "exact_arru": counts["அற்று"],
    }


def count_tamil_hits(entries, spec):
    c2 = [e for e in entries if len(e["members"]) == 2 and all(len(x) >= 1 for x in e["members"])]
    by_f = defaultdict(list)
    by_l = defaultdict(list)
    for k, e in enumerate(c2):
        for st in {indep_norm(b, True) for b in ta_sandhi(e["members"][0])}:
            by_f[st].append(k)
        by_l[indep_norm(e["members"][1], True)].append(k)

    def holds(f1, f2):
        for a in f1:
            t1 = indep_norm(a, False)
            st1 = indep_norm(a, True)
            for b in f2:
                t2 = indep_norm(b, False)
                st2 = indep_norm(b, True)
                if any(t1 in {indep_norm(x, False) for x in ta_sandhi(c2[k]["members"][0])} for k in by_l.get(st2, ())):
                    return True
                if any(t2 == indep_norm(c2[k]["members"][1], False) for k in by_f.get(st1, ())):
                    return True
        return False

    idents = spec["identifications"]
    blind = sum(holds(idents[t["first"]]["words"], idents[t["second"]]["words"]) for t in spec["templates"])
    pub = sum(holds(idents[t["first"]]["words"], idents[t["second"]]["words"]) for t in spec["published_templates"])
    return len(c2), blind, pub


def check_mw(spec, skt_res):
    # Unit checks for <srs/> and —˚ parsing
    srs_map = {"A": ("a", "a"), "I": ("i", "i"), "U": ("u", "u"), "F": ("f", "f"),
               "e": ("a", "i"), "o": ("a", "u"), "E": ("a", "e"), "O": ("a", "o")}

    def sp_srs(txt):
        a, b = txt.split("<srs/>", 1)
        a = re.sub(r"[^a-zA-Z]", "", a)
        b = re.sub(r"[^a-zA-Z]", "", b)
        if not a or not b:
            return None
        if a.endswith(("ar", "Ar")) and len(a) >= 3:
            return a[:-2] + "a", "f" + b
        if a[-1] in srs_map:
            v1, v2 = srs_map[a[-1]]
            return a[:-1] + v1, v2 + b
        return None

    unit_checks = {
        "em_ring_srs_amrtatman": sp_srs("a-mf—˚tA<srs/>tman".replace("—˚", "")) == ("amfta", "atman"),
        "srs_amaradri": sp_srs("amarA<srs/>dri") == ("amara", "adri"),
        "srs_guna_o": sp_srs("nAdo<srs/>panizad") == ("nAda", "upanizad"),
        "sandhi_zaz": "zaz" in skt_sandhi("zaw") and "zaz" in skt_sandhi("zaq") and "zaz" in skt_sandhi("zaR"),
        "sandhi_saptan": "saptan" in skt_sandhi("sapta"),
        "sandhi_dvi": "dvi" in skt_sandhi("dvy"),
    }

    head_re = re.compile(r"<k1>([^<]+)<k2>([^<]+)(?:<h>[^<]+)?<e>([^<\s]+)")
    s_re = re.compile(r"<s>([^<]*(?:<srs/>[^<]*)*)</s>")
    seen = set()
    c2 = []
    with open(MW_PATH, encoding="utf-8") as f:
        hdr = ""
        body_parts = []
        for line in f:
            if line.startswith("<L>"):
                hdr = line.strip()
                body_parts = []
            elif line.startswith("<LEND>"):
                m = head_re.search(hdr)
                if not m or m.group(3) != "3":
                    continue
                k1, k2 = m.group(1), m.group(2)
                body = " ".join(body_parts)
                hs = body.split("¦", 1)[0]
                sm = s_re.search(hs)
                ss = sm.group(1) if sm else ""
                pair = None
                if "—˚" in ss and ss.count("<srs/>") == 1:
                    pair = sp_srs(ss.replace("—˚", ""))
                elif k2.count("—") == 1:
                    r1, r2 = k2.split("—", 1)
                    m1 = re.sub(r"[^a-zA-Z]", "", r1)
                    r2c = re.sub(r"^[Mmnrs]-", "", re.sub(r"[/^\\°˚]", "", r2))
                    m2 = re.sub(r"[^a-zA-Z]", "", r2c)
                    if m1 and m2:
                        pair = (m1, m2)
                elif "—" not in k2 and ss.count("<srs/>") == 1:
                    pair = sp_srs(ss)
                if pair and pair[0] and pair[1]:
                    key = (re.sub(r"[^a-zA-Z]", "", k1), pair[0], pair[1])
                    if key not in seen:
                        seen.add(key)
                        c2.append(pair)
            else:
                body_parts.append(line.strip())

    def skt_n(w, t1=False):
        iast = "".join(SLP1_MAP.get(c, "") for c in w)
        return indep_norm(iast, t1)

    by_f = defaultdict(list)
    by_l = defaultdict(list)
    for k, (m1, m2) in enumerate(c2):
        for st in {skt_n(b, True) for b in skt_sandhi(m1)}:
            by_f[st].append(k)
        by_l[skt_n(m2, True)].append(k)

    def holds(f1, f2):
        for a in f1:
            t1, st1 = skt_n(a, False), skt_n(a, True)
            for b in f2:
                t2, st2 = skt_n(b, False), skt_n(b, True)
                if any(t1 in {skt_n(x, False) for x in skt_sandhi(c2[k][0])} for k in by_l.get(st2, ())):
                    return True
                if any(t2 == skt_n(c2[k][1], False) for k in by_f.get(st1, ())):
                    return True
        return False

    hit_checks = {}
    for mp_name in ("primary_single", "multiplicity_matched", "primary_antara", "multiplicity_antara"):
        mp = skt_res["mappings_slp1"][mp_name]
        bh = sum(holds(mp[t["first"]], mp[t["second"]]) for t in spec["templates"])
        ph = sum(holds(mp[t["first"]], mp[t["second"]]) for t in spec["published_templates"])
        exp_b = skt_res["results"][mp_name]["blind_T0s_K50"]["hits"]
        exp_p = skt_res["results"][mp_name]["published_T0s_K50"]["hits"]
        hit_checks[mp_name] = {
            "blind_recomputed": bh, "blind_reported": exp_b, "blind_match": bh == exp_b,
            "published_recomputed": ph, "published_reported": exp_p, "published_match": ph == exp_p,
        }
    return {
        "unit_checks": unit_checks,
        "compound_count_recomputed": len(c2),
        "compound_count_reported": skt_res["lexicon_primary"]["two_member_compounds"],
        "compound_count_match": len(c2) == skt_res["lexicon_primary"]["two_member_compounds"],
        "hit_checks": hit_checks,
    }


def synthetic_joint_key_check():
    """Verify planted vs unplanted keys and shared-sign variance amplification in joint draws."""
    rng = np.random.default_rng(12345)
    vocab = [f"w{i}" for i in range(120)]
    signs = [f"S{i}" for i in range(10)]
    # 30 templates reusing a hub sign S0 heavily (like BULLHEAD in real templates)
    templates = [("S0", f"S{i}") for i in range(1, 10)] + [(f"S{i}", "S0") for i in range(1, 10)]
    templates += [(f"S{i}", f"S{(i % 9) + 1}") for i in range(1, 10)] + [("S1", "S3"), ("S2", "S4"), ("S5", "S7")]

    # Background random compounds (~10% density)
    bg = set()
    for a in vocab:
        for b in vocab:
            if a != b and rng.random() < 0.10:
                bg.add((a, b))
    planted_key = {s: f"w{i}" for i, s in enumerate(signs)}
    # Plant 15 extra true compounds for the planted key
    planted_bg = set(bg)
    for a, b in templates[:15]:
        planted_bg.add((planted_key[a], planted_key[b]))

    def run_draws(comp_set, key_map):
        real_hits = sum((key_map[a], key_map[b]) in comp_set for a, b in templates)
        pools = {s: [w for w in vocab if w != key_map[s]][:50] for s in signs}
        # Joint sign-level draws (10,000)
        joint = []
        for _ in range(10000):
            rk = {s: pools[s][rng.integers(50)] for s in signs}
            joint.append(sum((rk[a], rk[b]) in comp_set for a, b in templates))
        # Independent per-template draws (ignoring shared signs)
        indep = []
        for _ in range(10000):
            indep.append(sum((pools[a][rng.integers(50)], pools[b][rng.integers(50)]) in comp_set for a, b in templates))
        j_arr, i_arr = np.asarray(joint, float), np.asarray(indep, float)
        return {
            "real_hits": int(real_hits),
            "joint_mean": float(j_arr.mean()),
            "joint_ratio": float(real_hits / j_arr.mean()),
            "joint_p": float((j_arr >= real_hits).mean()),
            "joint_var": float(j_arr.var()),
            "indep_var": float(i_arr.var()),
        }

    planted = run_draws(planted_bg, planted_key)
    # Test 20 independent unplanted keys to check null calibration without single-draw Poisson noise
    unplanted_ratios = []
    unplanted_ps = []
    for k_idx in range(20):
        uk = {s: vocab[rng.integers(len(vocab))] for s in signs}
        res_u = run_draws(bg, uk)
        unplanted_ratios.append(res_u["joint_ratio"])
        unplanted_ps.append(res_u["joint_p"])
    unplanted = {
        "keys_tested": 20,
        "mean_ratio": float(np.mean(unplanted_ratios)),
        "mean_p": float(np.mean(unplanted_ps)),
        "share_p_below_005": float(np.mean([p < 0.05 for p in unplanted_ps])),
    }
    return {
        "planted": planted,
        "unplanted": unplanted,
        "planted_detected": planted["joint_ratio"] > 3.0 and planted["joint_p"] < 0.001,
        "variance_amplification_ok": planted["joint_var"] > planted["indep_var"],
        "unplanted_null_ok": 0.7 <= unplanted["mean_ratio"] <= 1.3 and unplanted["share_p_below_005"] <= 0.15,
    }


def main():
    spec = json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))
    tl_res = json.loads((RESULTS / "tamil_repaired.json").read_text(encoding="utf-8"))
    w_res = json.loads((RESULTS / "winslow_reextracted.json").read_text(encoding="utf-8"))
    skt_res = json.loads((RESULTS / "sanskrit_control.json").read_text(encoding="utf-8"))

    sangam = check_sangam()
    sangam_ok = (
        sangam["total_tokens_lm"] == 162436
        and sangam["total_tokens_raw_block"] == 162399
        and sangam["exact_ka"] == 9
        and sangam["exact_aa"] == 24
        and sangam["total_tokens_lm"] == tl_res["sangam_summary"]["total_tokens"]
        and sangam["exact_ka"] == tl_res["sangam_summary"]["exact_ka"]
        and sangam["exact_aa"] == tl_res["sangam_summary"]["exact_aa"]
    )

    tl_entries = [json.loads(line) for line in TL_PATH.open(encoding="utf-8")]
    aru_exact_count = sum(1 for e in tl_entries if len(e["members"]) == 1 and e["translit"].casefold() == "aṟu")
    tl_c2, tl_blind, tl_pub = count_tamil_hits(tl_entries, spec)
    tl_ok = (
        aru_exact_count == 0
        and tl_c2 == 56154
        and tl_c2 == tl_res["lexicon_summary"]["two_member_compounds"]
        and tl_blind == tl_res["modes"]["exact_freq_prod"]["primary_sign_marginal"]["parpola_hits"]
        and tl_pub == tl_res["modes"]["exact_freq_prod"]["published_shape_C"]["parpola_hits"]
    )

    w_records = [json.loads(line) for line in WINSLOW_PATH.open(encoding="utf-8")]
    jamin_guarded = [r["winslow_guarded_members"] for r in w_records if r.get("translit") == "jamīṉ" or r.get("head") == "ஜமீன்"]
    w_raw_entries = [dict(r, members=r["winslow_guarded_members"]) for r in w_records]
    w_ass_entries = [dict(r, members=r["members"]) for r in w_records]
    wr_c2, wr_blind, wr_pub = count_tamil_hits(w_raw_entries, spec)
    wa_c2, wa_blind, wa_pub = count_tamil_hits(w_ass_entries, spec)
    winslow_ok = (
        wr_c2 == 18421
        and wa_c2 == 25653
        and wr_c2 == w_res["raw_guarded"]["lexicon_summary"]["two_member_compounds"]
        and wa_c2 == w_res["lexicon_assisted"]["lexicon_summary"]["two_member_compounds"]
        and wr_blind == w_res["raw_guarded"]["modes"]["exact_freq_prod"]["primary_sign_marginal"]["parpola_hits"]
        and wr_pub == w_res["raw_guarded"]["modes"]["exact_freq_prod"]["published_shape_C"]["parpola_hits"]
        and wa_blind == w_res["lexicon_assisted"]["modes"]["exact_freq_prod"]["primary_sign_marginal"]["parpola_hits"]
        and wa_pub == w_res["lexicon_assisted"]["modes"]["exact_freq_prod"]["published_shape_C"]["parpola_hits"]
        and all(len(m) != 2 for m in jamin_guarded)
    )

    mw_check = check_mw(spec, skt_res)
    mw_ok = (
        all(mw_check["unit_checks"].values())
        and mw_check["compound_count_match"]
        and all(v["blind_match"] and v["published_match"] for v in mw_check["hit_checks"].values())
    )

    synth = synthetic_joint_key_check()
    synth_ok = synth["planted_detected"] and synth["unplanted_null_ok"]

    all_pass = sangam_ok and tl_ok and winslow_ok and mw_ok and synth_ok
    report = {
        "schema_version": "1.0",
        "task": "rebus-repaired/verification",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "all_passed": all_pass,
        "sangam_check": {"passed": sangam_ok, "counts": sangam},
        "tamil_lexicon_check": {
            "passed": tl_ok, "aru_exact_one_member_records": aru_exact_count,
            "two_member_compounds": tl_c2, "blind_hits": tl_blind, "published_hits": tl_pub,
        },
        "winslow_check": {
            "passed": winslow_ok,
            "raw_guarded": {"two_member_compounds": wr_c2, "blind_hits": wr_blind, "published_hits": wr_pub},
            "lexicon_assisted": {"two_member_compounds": wa_c2, "blind_hits": wa_blind, "published_hits": wa_pub},
            "jamin_suppressed_in_guarded": all(len(m) != 2 for m in jamin_guarded),
        },
        "monier_williams_check": {"passed": mw_ok, **mw_check},
        "synthetic_joint_key_check": {"passed": synth_ok, **synth},
    }
    out_path = PKG / "verification-v1.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"all_passed": all_pass, "sangam_ok": sangam_ok, "tl_ok": tl_ok,
                      "winslow_ok": winslow_ok, "mw_ok": mw_ok, "synth_ok": synth_ok}, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
