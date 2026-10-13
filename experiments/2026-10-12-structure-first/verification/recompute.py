"""Independent recomputation of selected structure-first headline numbers.

Written from the verification assignment's definitions without reading the
step scripts, common.py or segmenters.py. Writes my_values.json next to this
file. Run from anywhere with: python -X utf8 recompute.py
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "2026-10-12-structure-first"
CLEAN = ROOT / "data" / "normalized" / "lipi_clean_rtl_singleline.jsonl"
FACES = ROOT / "data" / "normalized" / "lipi_observed_faces.jsonl"
CODER1 = EXP / "step1-signs" / "sign_components_v1.tsv"
CODER2 = EXP / "step1-signs" / "second-coder" / "components_coder2.tsv"
BRONZE = ROOT / "data" / "raw" / "2026-10-12-bronze-age-comparison" / "normalized-v4" / "records.jsonl"
OUT = Path(__file__).resolve().parent / "my_values.json"


def read_jsonl(path):
    with open(path, encoding="utf8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def read_coding(path):
    rows = {}
    with open(path, encoding="utf8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            parts += [""] * (len(header) - len(parts))
            rec = dict(zip(header, parts))
            rows[rec["code"].strip()] = rec
    return rows


def comb2(x):
    x = np.asarray(x, dtype=float)
    return x * (x - 1) / 2.0


def ari_from_table(table):
    """Adjusted Rand index from a contingency table (rows x cols of counts or weights)."""
    table = np.asarray(table, dtype=float)
    n = table.sum()
    sum_ij = comb2(table).sum()
    sum_a = comb2(table.sum(axis=1)).sum()
    sum_b = comb2(table.sum(axis=0)).sum()
    total = comb2(n)
    expected = sum_a * sum_b / total
    max_index = 0.5 * (sum_a + sum_b)
    return float((sum_ij - expected) / (max_index - expected))


def contingency(labels_a, labels_b, weights):
    ua = sorted(set(labels_a))
    ub = sorted(set(labels_b))
    ia = {v: i for i, v in enumerate(ua)}
    ib = {v: i for i, v in enumerate(ub)}
    t = np.zeros((len(ua), len(ub)))
    for a, b, w in zip(labels_a, labels_b, weights):
        t[ia[a], ib[b]] += w
    return t


def entropy_bits(counter):
    c = np.array(list(counter.values()), dtype=float)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def binom_two_sided(k, n):
    """Exact two-sided sign test p for k successes of n at p = 0.5 (doubling the smaller tail)."""
    if n == 0:
        return 1.0
    tail = min(k, n - k)
    s = sum(math.comb(n, i) for i in range(0, tail + 1))
    return float(min(1.0, 2 * s / 2 ** n))


def contains(seq, sub):
    n, m = len(seq), len(sub)
    if m == 0 or m > n:
        return False
    for i in range(n - m + 1):
        if seq[i:i + m] == sub:
            return True
    return False


# ---------------------------------------------------------------- shared frames
clean_rows = [r for r in read_jsonl(CLEAN) if r["clean_rtl_singleline"] and not r["has_unknown_sign"]]
text_families = defaultdict(set)
for r in clean_rows:
    text_families[tuple(r["signs_reading_rtl"])].add(str(r["object_family_id"]))
texts = sorted(text_families)
n_tokens = sum(len(t) for t in texts)

faces = read_jsonl(FACES)
c1 = read_coding(CODER1)
c2 = read_coding(CODER2)

out = {"frame": {"distinct_texts": len(texts), "signs": n_tokens, "faces": len(faces)}}

# ---------------------------------------------------------------- check 1: profiles
code_counts = Counter(s for t in texts for s in t)
missing = sorted(c for c in code_counts if c not in c1)
base_counts = Counter()
for code, n in code_counts.items():
    base_counts[c1[code]["base"]] += n


def profile(counts):
    types = len(counts)
    once = sum(1 for v in counts.values() if v == 1)
    total = sum(counts.values())
    top30 = sum(v for _, v in counts.most_common(30))
    return {"types": types, "share_types_once": once / types, "top30_token_share": top30 / total}


out["check1_profiles"] = {"W": profile(code_counts), "B": profile(base_counts), "codes_missing_from_coder1": missing}

# ---------------------------------------------------------------- check 2: coder ARI
attested = sorted(code_counts)
la = [c1[c]["base"] for c in attested]
lb = [c2[c]["base"] for c in attested]
out["check2_coder_ari"] = {
    "attested_codes": len(attested),
    "codes_missing_from_coder2": [c for c in attested if c not in c2],
    "ari_unweighted": ari_from_table(contingency(la, lb, [1] * len(attested))),
    "ari_token_weighted": ari_from_table(contingency(la, lb, [code_counts[c] for c in attested])),
}

# ---------------------------------------------------------------- step 2 helpers
NO_LABEL = {"None", "-", "Othr", "Unknown", "", None}


def norm_symbol(sym):
    if sym in NO_LABEL:
        return None
    if sym.startswith("Bull1"):
        return "Unicorn"
    if sym.startswith("Goat"):
        return "Goat"
    if sym in ("Bull", "Bull2", "Bull3"):
        return "ShortBull"
    return sym


def face_text(f):
    if f["complete_observed"] and not f["has_unknown_sign"] and f["length"] > 0:
        return tuple(f["signs_reading_rtl"])
    return None


def objects_of(type_ok):
    objs = defaultdict(lambda: {"classes": set(), "texts": set(), "raw_symbols": set()})
    for f in faces:
        if not type_ok(f["metadata"]["type"]):
            continue
        o = objs[str(f["object_family_id"])]
        o["raw_symbols"].add(f["symbol"])
        cls = norm_symbol(f["symbol"])
        if cls is not None:
            o["classes"].add(cls)
        t = face_text(f)
        if t is not None:
            o["texts"].add(t)
    return objs


# ---------------------------------------------------------------- check 3: copper 2a
copper = objects_of(lambda t: t == "TAB:C")
single = {k: o for k, o in copper.items() if len(o["classes"]) == 1 and o["texts"]}
text_objs = defaultdict(list)
for k, o in single.items():
    for t in o["texts"]:
        text_objs[t].append(k)
shared = {t: ks for t, ks in text_objs.items() if len(ks) >= 2}
consistent = sum(1 for t, ks in shared.items() if len({next(iter(single[k]["classes"])) for k in ks}) == 1)
out["check3_copper_2a"] = {
    "copper_objects": len(copper),
    "copper_objects_multi_class": sum(1 for o in copper.values() if len(o["classes"]) > 1),
    "single_class_objects_with_text": len(single),
    "shared_texts": len(shared),
    "shared_texts_one_class": consistent,
    "share_one_class": consistent / len(shared) if shared else None,
}

# ---------------------------------------------------------------- check 4: 2d hits


def ngrams(t):
    if len(t) == 1:
        return {t}
    g = set()
    for n in (2, 3):
        for i in range(len(t) - n + 1):
            g.add(t[i:i + n])
    return g


copper_class_texts = defaultdict(set)
for o in copper.values():
    if len(o["classes"]) == 1:
        copper_class_texts[next(iter(o["classes"]))] |= o["texts"]
class_grams = {c: set().union(*[ngrams(t) for t in ts]) if ts else set() for c, ts in copper_class_texts.items()}
specific = {}
for c, g in class_grams.items():
    others = set().union(*[class_grams[d] for d in class_grams if d != c]) if len(class_grams) > 1 else set()
    specific[c] = g - others

SEAL_TYPES = {"SEAL", "SEAL:S", "SEAL:R", "SEAL:C", "SEAL:CY"}
seals = objects_of(lambda t: t in SEAL_TYPES)
pairs = set()
for o in seals.values():
    if len(o["classes"]) == 1:
        cls = next(iter(o["classes"]))
        for t in o["texts"]:
            pairs.add((t, cls))
seal_classes = {c for _, c in pairs}

hits_by_class = {}
hits_by_class_substring = {}
for c in sorted(specific):
    if c not in seal_classes or not specific[c]:
        continue
    sp = specific[c]
    hits_by_class[c] = sum(1 for t, k in pairs if k == c and (ngrams(t) & sp))
    hits_by_class_substring[c] = sum(1 for t, k in pairs if k == c and any(contains(t, g) for g in sp))

out["check4_2d"] = {
    "copper_classes": {c: {"texts": len(copper_class_texts[c]), "specific_ngrams": len(specific[c])} for c in sorted(specific)},
    "seal_classes": sorted(seal_classes),
    "pairs": len(pairs),
    "hits_by_class": hits_by_class,
    "hits_total": sum(hits_by_class.values()),
    "hits_total_substring_variant": sum(hits_by_class_substring.values()),
}

# ---------------------------------------------------------------- check 5: line breaks


def found_elsewhere(window, fam):
    for t, fams in text_families.items():
        if fams == {fam}:
            continue
        if contains(t, window):
            return True
    return False


def straddle_windows(x, y, lengths):
    seq = x + y
    j = len(x)
    wins = []
    for L in lengths:
        if L < 2 or L > len(seq):
            continue
        for s in range(max(0, j - L + 1), min(j - 1, len(seq) - L) + 1):
            wins.append(seq[s:s + L])
    return wins


def run_linebreaks(lengths_as_set=True, interior_lines_twice=False):
    """interior_lines_twice reproduces, for diagnosis only, counting each line once per adjacent pair."""
    per_face = []
    for f in faces:
        code = f["text_code_visual_ltr"]
        if "/" not in code:
            continue
        if "[" in code or "]" in code or "000" in code:
            continue
        fam = str(f["object_family_id"])
        lines = []
        for part in code.split("/"):
            signs = tuple(s.strip("+").strip() for s in part.split("-"))
            signs = tuple(s for s in signs if s)
            if f["direction"] != "L/R":
                signs = signs[::-1]
            lines.append(signs)
        line_wins = [ln for ln in lines if len(ln) >= 2]
        if interior_lines_twice:
            line_wins = [ln for a, b in zip(lines, lines[1:]) for ln in (a, b) if len(ln) >= 2]
        fwd, bwd = [], []
        for a, b in zip(lines, lines[1:]):
            lens = [len(a), len(b)]
            if lengths_as_set:
                lens = sorted(set(lens))
            fwd += straddle_windows(a, b, lens)
            bwd += straddle_windows(b, a, lens)
        if not line_wins or not (fwd or bwd):
            continue
        lf = [found_elsewhere(w, fam) for w in line_wins]
        ff = [found_elsewhere(w, fam) for w in fwd]
        bf = [found_elsewhere(w, fam) for w in bwd]
        line_rate = sum(lf) / len(lf)
        n_lines = len(lines)
        pooled = (sum(ff) + sum(bf)) / (len(ff) + len(bf))
        order_rates = [sum(x) / len(x) for x in (ff, bf) if x]
        per_face.append({"record_id": f["record_id"], "line_rate": line_rate, "pooled": pooled, "better": max(order_rates),
                         "lines": n_lines, "line_windows": len(lf), "line_found": sum(lf), "straddle_windows": len(ff) + len(bf), "straddle_found": sum(ff) + sum(bf)})
    gt = sum(1 for r in per_face if r["line_rate"] > r["better"])
    lt = sum(1 for r in per_face if r["line_rate"] < r["better"])
    gt_p = sum(1 for r in per_face if r["line_rate"] > r["pooled"])
    lt_p = sum(1 for r in per_face if r["line_rate"] < r["pooled"])
    return {
        "faces_used": len(per_face),
        "line_gt_better": gt,
        "line_lt_better": lt,
        "sign_test_p_better": binom_two_sided(gt, gt + lt),
        "line_gt_pooled": gt_p,
        "line_lt_pooled": lt_p,
        "sign_test_p_pooled": binom_two_sided(gt_p, gt_p + lt_p),
        "mean_line_rate": float(np.mean([r["line_rate"] for r in per_face])),
        "mean_pooled_rate": float(np.mean([r["pooled"] for r in per_face])),
        "mean_better_rate": float(np.mean([r["better"] for r in per_face])),
        "pooled_line_rate": sum(r["line_found"] for r in per_face) / sum(r["line_windows"] for r in per_face),
        "pooled_straddle_rate": sum(r["straddle_found"] for r in per_face) / sum(r["straddle_windows"] for r in per_face),
        "line_windows": sum(r["line_windows"] for r in per_face),
        "faces_three_plus_lines": sum(1 for r in per_face if r["lines"] >= 3),
    }


out["check5_linebreaks"] = run_linebreaks(True)
out["check5_linebreaks_variant_duplicate_lengths"] = run_linebreaks(False)
out["check5_diagnostic_interior_lines_twice"] = run_linebreaks(True, interior_lines_twice=True)

# ---------------------------------------------------------------- check 6: numerals
numeral_value = {code: rec["count"].strip() for code, rec in c1.items()
                 if rec["base"] in ("B001", "B031") and rec["count"].strip()}
item_values = defaultdict(Counter)
num_tokens = 0
for t in texts:
    for i, s in enumerate(t):
        if s not in numeral_value:
            continue
        nxt = t[i + 1] if i + 1 < len(t) else "</s>"
        if nxt in numeral_value:
            continue
        item_values[nxt][numeral_value[s]] += 1
        num_tokens += 1
qual = {k: v for k, v in item_values.items() if sum(v.values()) >= 5}
out["check6_numerals"] = {
    "numeral_codes": len(numeral_value),
    "tokens": num_tokens,
    "items_ge5": len(qual),
    "mean_distinct_values": float(np.mean([len(v) for v in qual.values()])),
    "token_weighted_top_share": sum(max(v.values()) for v in qual.values()) / sum(sum(v.values()) for v in qual.values()),
    "mean_item_top_share_unweighted": float(np.mean([max(v.values()) / sum(v.values()) for v in qual.values()])),
}

# ---------------------------------------------------------------- check 7: edge asymmetry


def edge_asym(seqs):
    seqs = [s for s in seqs if len(s) >= 2]
    k = len({u for s in seqs for u in s})
    h_first = entropy_bits(Counter(s[0] for s in seqs)) / math.log2(k)
    h_last = entropy_bits(Counter(s[-1] for s in seqs)) / math.log2(k)
    return {"texts": len(seqs), "inventory": k, "h_first_norm": h_first, "h_last_norm": h_last, "asymmetry": h_first - h_last}


bronze = read_jsonl(BRONZE)
sum_seals = set()
skipped = 0
for r in bronze:
    if r["corpus"] != "sumerian" or r["kind"] != "seal":
        continue
    if any(len(w) == 0 for w in r["word_units"]):
        skipped += 1
        continue
    sum_seals.add(tuple(u for w in r["word_units"] for u in w))
sum_res = edge_asym(sorted(sum_seals))
sum_res["records_skipped_empty_unit"] = skipped
out["check7_edge_asymmetry"] = {"ivs": edge_asym(texts), "sumerian_seal": sum_res}

OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf8")
print(json.dumps(out, indent=2, ensure_ascii=False))
