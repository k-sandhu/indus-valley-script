"""Experiment B: Deciding Sanskrit cross-language control on the exact 38 blind pairs and 12 published pairs.

Uses the frozen 16-sign Sanskrit picture-to-word mapping declared in PROTOCOL.md (Section 3.1)
and scores attested two-member compounds in Cologne Monier-Williams
(data/raw/2026-10-12-decipherment-claim-tests/mw/mw.txt) against productivity-matched random
Sanskrit simplex nouns, with 10,000 sign-level dependent random-key draws.

Run from repository root:
    python experiments/2026-11-22-rebus-repaired/code/run_sanskrit_control.py
"""

import functools
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE_CODE = ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "code"
sys.path.insert(0, str(BASE_CODE))
import rebus  # noqa: E402

PKG = Path(__file__).resolve().parents[1]
TEMPLATES_PATH = ROOT / "experiments" / "2026-10-22-rebus-blind-templates" / "templates-v1.json"
MW_PATH = ROOT / "data" / "raw" / "2026-10-12-decipherment-claim-tests" / "mw" / "mw.txt"
LOCAL_OUT = ROOT / "data" / "raw" / "2026-11-22-rebus-repaired" / "results-v1"
REPO_OUT = PKG / "results-v1"

SEED = 20261122
K_MAIN = 50
K_SENS = (25, 100)
EXACT_LIMIT = 2500
MC_DRAWS = 5000
JOINT_DRAWS = 10000
BOOT = 2000

# Frozen Sanskrit picture-to-word mappings (PROTOCOL.md Section 3.1, SLP1 forms)
SANSKRIT_PRIMARY = {
    "FISH": ["matsya"],
    "ONE": ["eka"],
    "TWO": ["dvi"],
    "SIX": ["zaz"],
    "SEVEN": ["saptan"],
    "FIG": ["vawa"],
    "SPINDLE": ["tarku"],
    "CIRCLES": ["valaya"],
    "SQUIRREL": ["kalandaka"],
    "TWOLONG": ["reKA"],
    "CRAB": ["karkawa"],
    "EYE": ["akzi"],
    "WATER": ["jala"],
    "HINDLEG": ["pAda"],
    "BULLHEAD": ["go"],
    "YOKE": ["yuga"],
}

SANSKRIT_MULTIPLICITY = {
    "FISH": ["matsya"],
    "ONE": ["eka", "ekaka"],
    "TWO": ["dvi", "dvA"],
    "SIX": ["zaz"],
    "SEVEN": ["saptan"],
    "FIG": ["vawa"],
    "SPINDLE": ["tarku"],
    "CIRCLES": ["valaya"],
    "SQUIRREL": ["kalandaka", "romaSI"],
    "TWOLONG": ["reKA"],
    "CRAB": ["karkawa"],
    "EYE": ["akzi"],
    "WATER": ["jala"],
    "HINDLEG": ["pAda", "jaNGA"],
    "BULLHEAD": ["go", "vfza", "ukzan"],
    "YOKE": ["yuga", "Dur", "vIvaDa"],
}

SANSKRIT_PRIMARY_ANTARA = dict(SANSKRIT_PRIMARY, TWOLONG=["antara"])
SANSKRIT_MULTIPLICITY_ANTARA = dict(SANSKRIT_MULTIPLICITY, TWOLONG=["antara"])

# ---------------------------------------------------------------- SLP1 -> IAST & Sanskrit normalization

SLP1_TO_IAST = {
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
SLP1_VOWELS = set("aAiIuUfFxXeEoO")
SLP1_CONSONANTS = set("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL")
DERIV_SUFFIXES = {"tA", "tva", "maya", "vat", "mat", "tara", "tama", "ika", "ka"}


def slp1_to_iast(s):
    return "".join(SLP1_TO_IAST.get(ch, "") for ch in s)


def clean_slp1(s):
    return re.sub(r"[^a-zA-Z]", "", s)


def skt_sandhi_bases(m1):
    """Symmetric reversal of general Sanskrit first-member compound sandhi (SLP1)."""
    out = {m1}
    if not m1:
        return out
    last = m1[-1]
    # -n stem truncation in compounds (rAja- < rAjan, sapta- < saptan, ukza- < ukzan)
    if last in ("a", "i", "A", "I"):
        out.add(m1 + "n")
    # -as / -is / -us visarga and r-sandhi (mano- < manas, jyotir- < jyotis)
    if last == "o":
        out.add(m1[:-1] + "as")
    if last in ("r", "H", "S", "z"):
        out.add(m1[:-1] + "s")
    # Final stop voicing / retroflex / nasal assimilation (zaw/zaq/zaR < zaz, ab < ap, vAg < vAc)
    if last in ("w", "q", "R"):
        out.add(m1[:-1] + "z")
        out.add(m1[:-1] + "w")
        out.add(m1[:-1] + "q")
    if last == "d":
        out.add(m1[:-1] + "t")
    if last == "g":
        out.add(m1[:-1] + "k")
        out.add(m1[:-1] + "c")
    if last == "k":
        out.add(m1[:-1] + "c")
    if last == "b":
        out.add(m1[:-1] + "p")
    if last == "j":
        out.add(m1[:-1] + "c")
    if last in ("M", "n"):
        out.add(m1[:-1] + "m")
    # Yan glide sandhi (Panini 6.1.77): C + y -> C + i (dvy- < dvi), C + v -> C + u
    if len(m1) >= 2 and last == "y" and m1[-2] in SLP1_CONSONANTS:
        out.add(m1[:-1] + "i")
    if len(m1) >= 2 and last == "v" and m1[-2] in SLP1_CONSONANTS:
        out.add(m1[:-1] + "u")
    return out


@functools.lru_cache(maxsize=None)
def skt_norm(slp1_form, tol):
    iast = slp1_to_iast(slp1_form)
    toks = rebus.normalise(rebus.seg_indic(iast), ["L"])
    return rebus.stem(toks) if tol == "T1s" else toks


# ---------------------------------------------------------------- Monier-Williams parser

SRS_SPLIT = {
    "A": ("a", "a"),
    "I": ("i", "i"),
    "U": ("u", "u"),
    "F": ("f", "f"),
    "e": ("a", "i"),
    "o": ("a", "u"),
    "E": ("a", "e"),
    "O": ("a", "o"),
}


def split_srs(span_text):
    """Split a headword span containing a single <srs/> into (m1, m2) in SLP1."""
    parts = span_text.split("<srs/>")
    if len(parts) != 2:
        return None
    left = clean_slp1(parts[0])
    right = clean_slp1(parts[1])
    if not left or not right:
        return None
    if left.endswith(("ar", "Ar")) and len(left) >= 3:
        return left[:-2] + "a", "f" + right
    v = left[-1]
    if v in SRS_SPLIT:
        v1, v2 = SRS_SPLIT[v]
        return left[:-1] + v1, v2 + right
    return None


def strip_connector(m2_raw):
    """Strip leading single-letter sandhi connector like M- or m- on raw second member."""
    m2_s = re.sub(r"[/^\\°˚]", "", m2_raw)
    m2_s = re.sub(r"^[Mmnrs]-", "", m2_s)
    return clean_slp1(m2_s)


def parse_mw(mw_path, include_hyphen=False):
    """Parse Monier-Williams into two-member compounds (<e>3) and simplex nominal candidates (<e>1, <e>2)."""
    compounds_seen = set()
    compounds = []
    simplex_heads = {}
    parse_stats = defaultdict(int)

    head_re = re.compile(r"<k1>([^<]+)<k2>([^<]+)(?:<h>[^<]+)?<e>([^<\s]+)")
    lex_re = re.compile(r'<info lex="([^"]+)"')
    s_tag_re = re.compile(r"<s>([^<]*(?:<srs/>[^<]*)*)</s>")

    with open(mw_path, encoding="utf-8") as f:
        hdr = ""
        body_parts = []
        for line in f:
            if line.startswith("<L>"):
                hdr = line.strip()
                body_parts = []
            elif line.startswith("<LEND>"):
                body = " ".join(body_parts)
                m = head_re.search(hdr)
                if not m:
                    continue
                k1, k2, ev = m.groups()
                # Simplex candidates: <e>1 or <e>2 (and their sub-senses inherit k1/lex)
                if ev[0] in ("1", "2") and "—" not in k2 and "<info verb=" not in body:
                    lm = lex_re.search(body)
                    if lm:
                        lex_tokens = [tok.split("#")[0] for tok in lm.group(1).split(":")]
                        if any(t in ("m", "f", "n") for t in lex_tokens):
                            k1_c = clean_slp1(k1)
                            if k1_c:
                                simplex_heads.setdefault(k1_c, {"k1": k1_c, "iast": slp1_to_iast(k1_c)})

                # Two-member compounds: main <e>3 entries only
                if ev == "3":
                    parse_stats["e3_total"] += 1
                    head_section = body.split("¦", 1)[0]
                    s_match = s_tag_re.search(head_section)
                    s_span = s_match.group(1) if s_match else ""
                    pair = None
                    kind = None

                    if "—˚" in s_span and s_span.count("<srs/>") == 1:
                        pair = split_srs(s_span.replace("—˚", ""))
                        kind = "em_ring_srs"
                    elif k2.count("—") == 1:
                        raw1, raw2 = k2.split("—", 1)
                        m1 = clean_slp1(raw1)
                        m2 = strip_connector(raw2)
                        if m1 and m2:
                            pair = (m1, m2)
                            kind = "em_dash"
                    elif "—" not in k2 and s_span.count("<srs/>") == 1:
                        pair = split_srs(s_span)
                        kind = "srs_only"
                    elif include_hyphen and "—" not in k2 and "<srs/>" not in s_span and k2.count("-") == 1:
                        if "<info verb=" not in body and "√" not in head_section:
                            raw1, raw2 = k2.split("-", 1)
                            m1 = clean_slp1(raw1)
                            m2 = clean_slp1(raw2)
                            if m1 and m2 and m2 not in DERIV_SUFFIXES and len(m1) >= 2 and len(m2) >= 2:
                                pair = (m1, m2)
                                kind = "hyphen_nominal"

                    if pair and len(pair[0]) >= 1 and len(pair[1]) >= 1:
                        key = (clean_slp1(k1), pair[0], pair[1])
                        if key not in compounds_seen:
                            compounds_seen.add(key)
                            compounds.append({"k1": key[0], "members": [pair[0], pair[1]], "kind": kind})
                            parse_stats[f"extracted_{kind}"] += 1
                    else:
                        parse_stats["e3_skipped"] += 1
            else:
                body_parts.append(line.strip())

    return compounds, list(simplex_heads.values()), dict(parse_stats)


class SktCompounds:
    def __init__(self, compounds):
        self.c2 = compounds
        self.first = defaultdict(list)
        self.last = defaultdict(list)
        for idx, e in enumerate(self.c2):
            m1, m2 = e["members"]
            for st in {skt_norm(b, "T1s") for b in skt_sandhi_bases(m1)}:
                self.first[st].append(idx)
            self.last[skt_norm(m2, "T1s")].append(idx)

    def anchor(self, word):
        return skt_norm(word, "T1s")

    def prod_first(self, word):
        return len(self.first.get(self.anchor(word), ()))

    def prod_last(self, word):
        return len(self.last.get(self.anchor(word), ()))

    def A(self, w1):
        return [self.c2[k] for k in self.first.get(self.anchor(w1), ())]

    def B(self, w2):
        return [self.c2[k] for k in self.last.get(self.anchor(w2), ())]


class SktSearcher:
    def __init__(self, comp):
        self.comp = comp
        self.cache = {}

    def _firsts(self, w2, tol):
        key = ("F", w2, tol)
        if key not in self.cache:
            self.cache[key] = {skt_norm(b, tol) for e in self.comp.B(w2) for b in skt_sandhi_bases(e["members"][0])}
        return self.cache[key]

    def _seconds(self, w1, tol):
        key = ("L", w1, tol)
        if key not in self.cache:
            self.cache[key] = {skt_norm(e["members"][1], tol) for e in self.comp.A(w1)}
        return self.cache[key]

    def compound_holds(self, w1, w2, tol, direction="both"):
        if direction in ("both", "a") and skt_norm(w1, tol) in self._firsts(w2, tol):
            return True
        if direction in ("both", "b") and skt_norm(w2, tol) in self._seconds(w1, tol):
            return True
        return False

    def shared_holds(self, w1, w2, tol):
        key = ("SB", w1, w2, tol)
        if key not in self.cache:
            a_secs = self._seconds(w1, tol)
            b_firsts = self._firsts(w2, tol)
            if not a_secs or not b_firsts:
                self.cache[key] = False
            else:
                excl = {skt_norm(b, tol) for w in (w1, w2) for b in skt_sandhi_bases(w)}
                self.cache[key] = bool((a_secs & b_firsts) - excl)
        return self.cache[key]

    def compound(self, w1, w2, tol, direction="both"):
        hits = []
        t1, t2 = skt_norm(w1, tol), skt_norm(w2, tol)
        if direction in ("both", "a"):
            for e in self.comp.B(w2):
                if t1 in {skt_norm(b, tol) for b in skt_sandhi_bases(e["members"][0])}:
                    hits.append(f"{slp1_to_iast(e['members'][0])}-{slp1_to_iast(e['members'][1])} ({e['k1']})")
        if direction in ("both", "b"):
            for e in self.comp.A(w1):
                if t2 == skt_norm(e["members"][1], tol):
                    hits.append(f"{slp1_to_iast(e['members'][0])}-{slp1_to_iast(e['members'][1])} ({e['k1']})")
        return sorted(set(hits))

    def holds(self, shape, f1, f2, tol, direction="both"):
        for a in f1:
            for b in f2:
                ok = self.compound_holds(a, b, tol, direction) if shape == "C" else self.shared_holds(a, b, tol)
                if ok:
                    return True
        return False


def build_skt_candidates(simplex_heads, comp):
    seen = {}
    for h in simplex_heads:
        w = h["k1"]
        st = comp.anchor(w)
        if not st or st in seen:
            continue
        seen[st] = {
            "word": w,
            "iast": h["iast"],
            "stem": "".join(st),
            "prod_first": comp.prod_first(w),
            "prod_last": comp.prod_last(w),
        }
    return list(seen.values())


def nearest_sign(cands, feat, k):
    pool = [c for c in cands if c["stem"] != feat["stem"]]
    lp1 = np.array([math.log1p(c["prod_first"]) for c in pool], dtype=float)
    lp2 = np.array([math.log1p(c["prod_last"]) for c in pool], dtype=float)
    sp1 = lp1.std() or 1.0
    sp2 = lp2.std() or 1.0
    d = np.sqrt(((lp1 - math.log1p(feat["prod_first"])) / sp1) ** 2 + ((lp2 - math.log1p(feat["prod_last"])) / sp2) ** 2)
    order = sorted(range(len(pool)), key=lambda i: (d[i], pool[i]["word"]))
    return [dict(pool[i], distance=float(d[i])) for i in order[:k]]


def nearest_slot(cands, feat, prod_key, k):
    pool = [c for c in cands if c["stem"] != feat["stem"]]
    lp = np.array([math.log1p(c[prod_key]) for c in pool], dtype=float)
    sp = lp.std() or 1.0
    d = np.abs(lp - math.log1p(feat[prod_key])) / sp
    order = sorted(range(len(pool)), key=lambda i: (d[i], pool[i]["word"]))
    return [dict(pool[i], distance=float(d[i])) for i in order[:k]]


def summarise(h, r, rng, joint_sign_counts=None, joint_slot_counts=None):
    h_arr, r_arr = np.asarray(h, float), np.asarray(r, float)
    n, H, R = len(h_arr), float(h_arr.sum()), float(r_arr.sum())
    ratio = H / R if R > 0 else None
    idx = rng.integers(0, n, (BOOT, n))
    rs, hs = r_arr[idx].sum(1), h_arr[idx].sum(1)
    ok = rs > 0
    boots = hs[ok] / rs[ok]
    ci = [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))] if ok.any() else [None, None]
    loo = [(H - h_arr[i]) / (R - r_arr[i]) if R - r_arr[i] > 0 else None for i in range(n)]
    loo_vals = [x for x in loo if x is not None]
    out = {
        "templates": n,
        "hits": int(H),
        "rate": H / n if n else None,
        "rate_ci95_wilson": rebus.wilson(int(H), n),
        "expected_random_hits_marginal": R,
        "random_rate_marginal": R / n if n else None,
        "ratio_marginal": ratio,
        "ratio_ci95_bootstrap_over_templates": ci,
        "leave_one_out_min": min(loo_vals) if loo_vals else None,
        "leave_one_out_max": max(loo_vals) if loo_vals else None,
    }
    if joint_sign_counts is not None:
        jc = np.asarray(joint_sign_counts, dtype=float)
        jm = float(jc.mean())
        out["joint_sign_level"] = {
            "draws": int(len(jc)),
            "expected_random_hits": jm,
            "random_rate": jm / n if n else None,
            "ratio": (H / jm) if jm > 0 else None,
            "sd_hits": float(jc.std(ddof=0)),
            "p_random_key_at_least_hits": float((jc >= H).mean()),
            "hits_distribution": {str(int(v)): int((jc == v).sum()) for v in sorted(set(jc.tolist()))},
        }
    if joint_slot_counts is not None:
        jc = np.asarray(joint_slot_counts, dtype=float)
        jm = float(jc.mean())
        out["joint_slot_level"] = {
            "draws": int(len(jc)),
            "expected_random_hits": jm,
            "random_rate": jm / n if n else None,
            "ratio": (H / jm) if jm > 0 else None,
            "sd_hits": float(jc.std(ddof=0)),
            "p_random_key_at_least_hits": float((jc >= H).mean()),
            "hits_distribution": {str(int(v)): int((jc == v).sum()) for v in sorted(set(jc.tolist()))},
        }
    return out


def score_set(templates, mapping, shape, srch, slot_pools, sign_pools, tol, k, rng,
              run_joint=True, direction="both", marginal_mode="sign"):
    real, rates, rows = [], [], []
    for t in templates:
        f1 = mapping[t["first"]]
        f2 = mapping[t["second"]]
        h = srch.holds(shape, f1, f2, tol, direction)
        if marginal_mode == "sign":
            p1 = [[c["word"] for c in sign_pools[w][k]] for w in f1]
            p2 = [[c["word"] for c in sign_pools[w][k]] for w in f2]
        else:
            p1 = [[c["word"] for c in slot_pools["first"][w][k]] for w in f1]
            p2 = [[c["word"] for c in slot_pools["second"][w][k]] for w in f2]
        if len(p1) == 1 and len(p2) == 1 and len(p1[0]) * len(p2[0]) <= EXACT_LIMIT:
            hits = sum(srch.holds(shape, [a], [b], tol, direction) for a in p1[0] for b in p2[0])
            r, method = hits / (len(p1[0]) * len(p2[0])), "exact"
        else:
            hits = 0
            for _ in range(MC_DRAWS):
                a = [p[rng.integers(len(p))] for p in p1]
                b = [p[rng.integers(len(p))] for p in p2]
                hits += srch.holds(shape, a, b, tol, direction)
            r, method = hits / MC_DRAWS, f"monte-carlo-{MC_DRAWS}"
        real.append(int(h))
        rates.append(r)
        rows.append({
            "id": t["id"], "first": t["first"], "second": t["second"], "shape": shape,
            "holds": bool(h), "random_rate": r, "random_rate_method": method,
        })

    joint_sign = None
    joint_slot = None
    if run_joint:
        signs = sorted({t["first"] for t in templates} | {t["second"] for t in templates})
        sign_word_pools = {s: [[c["word"] for c in sign_pools[w][k]] for w in mapping[s]] for s in signs}
        joint_sign = []
        for _ in range(JOINT_DRAWS):
            key = {s: [p[rng.integers(len(p))] for p in sign_word_pools[s]] for s in signs}
            joint_sign.append(sum(srch.holds(shape, key[t["first"]], key[t["second"]], tol, direction) for t in templates))

        slots = sorted({(t["first"], "first") for t in templates} | {(t["second"], "second") for t in templates})
        slot_word_pools = {(s, sl): [[c["word"] for c in slot_pools[sl][w][k]] for w in mapping[s]] for s, sl in slots}
        joint_slot = []
        for _ in range(JOINT_DRAWS):
            key = {(s, sl): [p[rng.integers(len(p))] for p in slot_word_pools[(s, sl)]] for s, sl in slots}
            joint_slot.append(sum(srch.holds(shape, key[(t["first"], "first")], key[(t["second"], "second")], tol, direction) for t in templates))

    return real, rates, rows, joint_sign, joint_slot


def run_suite(comp, cands, spec, mappings, include_full_sens=True):
    rng = np.random.default_rng(SEED)
    srch = SktSearcher(comp)
    groups = {
        "primary": spec["templates"],
        "gapped": spec["gapped_templates"],
        "published": spec["published_templates"],
    }
    no_bullhead = [t for t in groups["primary"] if t["first"] != "BULLHEAD" and t["second"] != "BULLHEAD"]

    all_words = sorted({w for mp in mappings.values() for ws in mp.values() for w in ws})
    feats = {
        w: {
            "word_slp1": w, "word_iast": slp1_to_iast(w), "stem": "".join(comp.anchor(w)),
            "prod_first": comp.prod_first(w), "prod_last": comp.prod_last(w),
        }
        for w in all_words
    }
    sign_pools = {w: {kk: nearest_sign(cands, feats[w], kk) for kk in (K_MAIN,) + K_SENS} for w in all_words}
    slot_pools = {
        "first": {w: {kk: nearest_slot(cands, feats[w], "prod_first", kk) for kk in (K_MAIN,) + K_SENS} for w in all_words},
        "second": {w: {kk: nearest_slot(cands, feats[w], "prod_last", kk) for kk in (K_MAIN,) + K_SENS} for w in all_words},
    }

    results = {}
    details = {}
    for map_name, mp in mappings.items():
        plan = [
            ("blind_T0s_K50", groups["primary"], "C", "T0s", K_MAIN, True, "both", "sign"),
            ("blind_T0s_K50_slot", groups["primary"], "C", "T0s", K_MAIN, False, "both", "slot"),
            ("blind_T1s_K50", groups["primary"], "C", "T1s", K_MAIN, True, "both", "sign"),
            ("published_T0s_K50", groups["published"], "C", "T0s", K_MAIN, True, "both", "sign"),
        ]
        if include_full_sens and map_name in ("primary_single", "multiplicity_matched"):
            plan += [
                ("blind_T0s_K25", groups["primary"], "C", "T0s", 25, True, "both", "sign"),
                ("blind_T0s_K100", groups["primary"], "C", "T0s", 100, True, "both", "sign"),
                ("blind_T0s_direction_a", groups["primary"], "C", "T0s", K_MAIN, True, "a", "sign"),
                ("blind_T0s_no_bullhead_26", no_bullhead, "C", "T0s", K_MAIN, True, "both", "sign"),
                ("gapped_shape_S_T0s", groups["gapped"], "S", "T0s", K_MAIN, True, "both", "sign"),
            ]
        m_res = {}
        m_det = {}
        for name, ts, shape, tol, k, run_joint, direction, marg_mode in plan:
            real, rates, rows, j_sign, j_slot = score_set(
                ts, mp, shape, srch, slot_pools, sign_pools, tol, k, rng,
                run_joint=run_joint, direction=direction, marginal_mode=marg_mode,
            )
            s = summarise(real, rates, rng, j_sign, j_slot)
            s.update({"tolerance": tol, "pool_size": k, "direction": direction, "marginal_pool_type": marg_mode})
            if name in ("blind_T0s_K50", "published_T0s_K50"):
                s["per_template"] = rows
            m_res[name] = s
            if shape == "C" and name in ("blind_T0s_K50", "blind_T1s_K50", "published_T0s_K50"):
                det = {}
                for r in rows:
                    if not r["holds"]:
                        continue
                    found = {}
                    for a in mp[r["first"]]:
                        for b in mp[r["second"]]:
                            x = srch.compound(a, b, tol, direction)
                            if x:
                                found[f"{slp1_to_iast(a)} | {slp1_to_iast(b)}"] = x
                    det[r["id"]] = found
                m_det[name] = det
        results[map_name] = m_res
        details[map_name] = m_det
    return feats, results, details


def main():
    REPO_OUT.mkdir(parents=True, exist_ok=True)
    LOCAL_OUT.mkdir(parents=True, exist_ok=True)
    spec = json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))

    print("Parsing Monier-Williams (primary: em-dash + <srs/>)...")
    mw_c2, mw_simplex, mw_stats = parse_mw(MW_PATH, include_hyphen=False)
    comp = SktCompounds(mw_c2)
    cands = build_skt_candidates(mw_simplex, comp)
    print(f"MW primary: {len(mw_c2)} two-member compounds, {len(cands)} simplex candidates, stats={mw_stats}")

    mappings = {
        "primary_single": SANSKRIT_PRIMARY,
        "multiplicity_matched": SANSKRIT_MULTIPLICITY,
        "primary_antara": SANSKRIT_PRIMARY_ANTARA,
        "multiplicity_antara": SANSKRIT_MULTIPLICITY_ANTARA,
    }
    feats, res_primary, det_primary = run_suite(comp, cands, spec, mappings, include_full_sens=True)

    print("Parsing Monier-Williams sensitivity (+ nominal hyphenated <e>3)...")
    mw_c2_hy, mw_simplex_hy, mw_stats_hy = parse_mw(MW_PATH, include_hyphen=True)
    comp_hy = SktCompounds(mw_c2_hy)
    cands_hy = build_skt_candidates(mw_simplex_hy, comp_hy)
    _, res_hy, _ = run_suite(
        comp_hy, cands_hy, spec,
        {"primary_single": SANSKRIT_PRIMARY, "multiplicity_matched": SANSKRIT_MULTIPLICITY},
        include_full_sens=False,
    )

    out = {
        "schema_version": "1.0",
        "task": "rebus-repaired/sanskrit-control",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "seed": SEED, "k_main": K_MAIN, "k_sensitivity": list(K_SENS),
            "exact_limit": EXACT_LIMIT, "mc_draws": MC_DRAWS, "joint_draws": JOINT_DRAWS, "bootstrap": BOOT,
        },
        "provenance": {
            "templates": {"path": TEMPLATES_PATH.relative_to(ROOT).as_posix(), "sha256": rebus.sha256(TEMPLATES_PATH)},
            "mw": {"path": MW_PATH.relative_to(ROOT).as_posix(), "sha256": rebus.sha256(MW_PATH)},
        },
        "mappings_slp1": mappings,
        "mappings_iast": {k: {s: [slp1_to_iast(w) for w in ws] for s, ws in mp.items()} for k, mp in mappings.items()},
        "lexicon_primary": {
            "two_member_compounds": len(mw_c2),
            "simplex_candidates": len(cands),
            "parse_stats": mw_stats,
        },
        "word_features": feats,
        "results": res_primary,
        "sensitivity_mw_plus_hyphen": {
            "two_member_compounds": len(mw_c2_hy),
            "simplex_candidates": len(cands_hy),
            "parse_stats": mw_stats_hy,
            "results": res_hy,
        },
    }

    det_path = LOCAL_OUT / "sanskrit-control-detail.json"
    det_path.write_text(json.dumps(det_primary, ensure_ascii=False, indent=1), encoding="utf-8")
    out["local_detail"] = {"path": det_path.relative_to(ROOT).as_posix(), "sha256": rebus.sha256(det_path)}
    (REPO_OUT / "sanskrit_control.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n=== SANSKRIT CROSS-LANGUAGE CONTROL (MW primary) ===")
    for mp_name in ("primary_single", "multiplicity_matched", "primary_antara", "multiplicity_antara"):
        b = res_primary[mp_name]["blind_T0s_K50"]
        b1 = res_primary[mp_name]["blind_T1s_K50"]
        p = res_primary[mp_name]["published_T0s_K50"]
        print(f"  [{mp_name}] T0s blind={b['hits']}/38 | sign-joint exp={b['joint_sign_level']['expected_random_hits']:.2f} "
              f"ratio={b['joint_sign_level']['ratio']:.2f} p={b['joint_sign_level']['p_random_key_at_least_hits']:.4f} | "
              f"T1s blind={b1['hits']}/38 ratio={b1['joint_sign_level']['ratio']:.2f} p={b1['joint_sign_level']['p_random_key_at_least_hits']:.4f} | "
              f"pub={p['hits']}/12 ratio={p['joint_sign_level']['ratio']:.2f}")
    print("\n=== SANSKRIT SENSITIVITY (+ hyphenated <e>3) ===")
    for mp_name in ("primary_single", "multiplicity_matched"):
        b = res_hy[mp_name]["blind_T0s_K50"]
        print(f"  [{mp_name}] T0s blind={b['hits']}/38 | sign-joint exp={b['joint_sign_level']['expected_random_hits']:.2f} "
              f"ratio={b['joint_sign_level']['ratio']:.2f} p={b['joint_sign_level']['p_random_key_at_least_hits']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
