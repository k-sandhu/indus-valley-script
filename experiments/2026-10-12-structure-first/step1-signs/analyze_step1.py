"""Step 1: sign-list granularity, coder agreement and the grouping prediction test.

Usage: python -X utf8 analyze_step1.py --out <run_dir> [--coder2 <tsv>] [--nulls 200]

Implements PROTOCOL.md step 1. Every model predicts the original Wells codes, so
held-out bits per sign are comparable across groupings.
"""
import argparse
import collections
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402

LAMBDAS = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
D = 0.75
DELTA = 0.5


# ------------------------------------------------------------------ profiles
def profile(texts, label):
    tok = collections.Counter(label[s] for t in texts for s in t)
    n = sum(tok.values())
    k = len(tok)
    top30 = sum(v for _, v in tok.most_common(30)) / n
    ent = -sum(v / n * math.log2(v / n) for v in tok.values())
    return {"types": k, "tokens": n, "once_share": sum(v == 1 for v in tok.values()) / k,
            "le2_share": sum(v <= 2 for v in tok.values()) / k, "top30_token_share": top30,
            "unigram_entropy_bits": ent}


# ------------------------------------------------------------------ models
class Data:
    def __init__(self, texts, folds, vocab):
        self.vocab = vocab
        self.idx = {c: i for i, c in enumerate(vocab)}
        self.V = len(vocab)
        self.START = self.V
        prev, cur, tf, comp = [], [], [], []
        for t, f, cp in zip(texts, folds, range(len(texts))):
            p = self.START
            for s in t:
                i = self.idx[s]
                prev.append(p)
                cur.append(i)
                tf.append(f)
                comp.append(cp)
                p = i
        self.prev = np.array(prev)
        self.cur = np.array(cur)
        self.fold = np.array(tf)
        self.text_id = np.array(comp)


def kn_probs(prev_tr, cur_tr, prev_te, cur_te, V):
    S = V + 1
    C = np.zeros((S, V))
    np.add.at(C, (prev_tr, cur_tr), 1)
    cv = C.sum(1)
    n1v = (C > 0).sum(1)
    n1w = (C > 0).sum(0)
    pcont = (n1w + DELTA) / ((C > 0).sum() + DELTA * V)
    c = C[prev_te, cur_te]
    denom = cv[prev_te]
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(denom > 0,
                     np.maximum(c - D, 0) / np.where(denom > 0, denom, 1)
                     + D * n1v[prev_te] / np.where(denom > 0, denom, 1) * pcont[cur_te],
                     pcont[cur_te])
    return p


def unigram_probs(cur_tr, cur_te, V):
    n = np.bincount(cur_tr, minlength=V).astype(float)
    return (n[cur_te] + DELTA) / (n.sum() + DELTA * V)


def class_probs(prev_tr, cur_tr, prev_te, cur_te, cls, ncls):
    """cls: array length V+1 mapping code index (and START) to class index; START has its own class."""
    cp_tr, cc_tr = cls[prev_tr], cls[cur_tr]
    M = np.zeros((ncls, ncls))
    np.add.at(M, (cp_tr, cc_tr), 1)
    row = M.sum(1)
    target_classes = np.unique(cls[:-1])
    nt = len(target_classes)
    p_cc = (M[cls[prev_te], cls[cur_te]] + 0.5) / (row[cls[prev_te]] + 0.5 * nt)
    V = len(cls) - 1
    nw = np.bincount(cur_tr, minlength=V).astype(float)
    nc = np.bincount(cls[:-1], weights=nw, minlength=ncls)
    size = np.bincount(cls[:-1], minlength=ncls).astype(float)
    p_wc = (nw[cur_te] + 0.5) / (nc[cls[cur_te]] + 0.5 * size[cls[cur_te]])
    return p_cc * p_wc


def inner_folds(data, train_mask):
    ids = data.text_id[train_mask]
    out = np.array([int(hashlib.sha256(f"{common.SEED + 7}:{i}".encode()).hexdigest(), 16) % 3 for i in ids])
    return out


class Evaluator:
    """Precomputes Kneser-Ney probabilities for all outer and inner splits."""

    def __init__(self, data, comp_of_text):
        self.d = data
        # inner fold assignment by component, not by text
        self.splits = []
        comp_arr = np.array([comp_of_text[t] for t in data.text_id])
        for k in range(5):
            tr = data.fold != k
            te = data.fold == k
            inner = np.array([int(hashlib.sha256(f"{common.SEED + 7}:{c}".encode()).hexdigest(), 16) % 3
                              for c in comp_arr[tr]])
            pt, ct = data.prev[tr], data.cur[tr]
            outer = {"pt": pt, "ct": ct, "pe": data.prev[te], "ce": data.cur[te]}
            outer["kn"] = kn_probs(pt, ct, outer["pe"], outer["ce"], data.V)
            outer["uni"] = unigram_probs(ct, outer["ce"], data.V)
            ins = []
            for j in range(3):
                a, b = inner != j, inner == j
                s = {"pt": pt[a], "ct": ct[a], "pe": pt[b], "ce": ct[b]}
                s["kn"] = kn_probs(s["pt"], s["ct"], s["pe"], s["ce"], data.V)
                ins.append(s)
            outer["inner"] = ins
            self.splits.append(outer)
        self.n = sum(len(s["ce"]) for s in self.splits)
        self.base_bits = -sum(np.log2(s["kn"]).sum() for s in self.splits) / self.n
        self.uni_bits = -sum(np.log2(s["uni"]).sum() for s in self.splits) / self.n

    def evaluate(self, cls, ncls, keep_tokens=False):
        total = 0.0
        lams = []
        per_tok = []
        for s in self.splits:
            inner_loss = np.zeros(len(LAMBDAS))
            for t in s["inner"]:
                pc = class_probs(t["pt"], t["ct"], t["pe"], t["ce"], cls, ncls)
                for i, lam in enumerate(LAMBDAS):
                    inner_loss[i] -= np.log2(lam * t["kn"] + (1 - lam) * pc).sum()
            lam = LAMBDAS[int(np.argmin(inner_loss))]
            lams.append(lam)
            pc = class_probs(s["pt"], s["ct"], s["pe"], s["ce"], cls, ncls)
            p = lam * s["kn"] + (1 - lam) * pc
            total -= np.log2(p).sum()
            if keep_tokens:
                per_tok.append(-np.log2(p))
        bits = total / self.n
        return bits, lams, (np.concatenate(per_tok) if keep_tokens else None)


def class_array(data, mapping):
    labels = [mapping[c] for c in data.vocab]
    uniq = {l: i for i, l in enumerate(sorted(set(labels)))}
    cls = np.array([uniq[l] for l in labels] + [len(uniq)])
    return cls, len(uniq) + 1


# ------------------------------------------------------------------ agreement
def ari(a, b, w=None):
    """Adjusted Rand index between two labelings, optionally weighted by w (token counts)."""
    if w is None:
        w = [1.0] * len(a)
    tab = collections.Counter()
    ra, rb = collections.Counter(), collections.Counter()
    for x, y, ww in zip(a, b, w):
        tab[(x, y)] += ww
        ra[x] += ww
        rb[y] += ww
    n = sum(w)
    comb = lambda v: v * (v - 1) / 2.0
    sij = sum(comb(v) for v in tab.values())
    sa = sum(comb(v) for v in ra.values())
    sb = sum(comb(v) for v in rb.values())
    exp = sa * sb / comb(n)
    mx = (sa + sb) / 2
    return (sij - exp) / (mx - exp) if mx != exp else float("nan")


def kappa(x, y):
    n = len(x)
    po = sum(a == b for a, b in zip(x, y)) / n
    px, py = sum(x) / n, sum(y) / n
    pe = px * py + (1 - px) * (1 - py)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


# ------------------------------------------------------------------ descriptive
def substitution_frames(texts):
    buckets = collections.defaultdict(collections.Counter)
    for t in set(texts):
        if len(t) < 3:
            continue
        for i in range(len(t)):
            buckets[(len(t), i, t[:i], t[i + 1:])][t[i]] += 1
    pairs = 0
    for c in buckets.values():
        k = len(c)
        pairs += k * (k - 1) // 2
    return pairs


def granularity(texts, folds, label):
    rec = [tuple(label[s] for s in t) for t in texts]
    vocab = sorted({s for t in rec for s in t})
    d = Data(rec, folds, vocab)
    bits_kn = bits_uni = 0.0
    n = 0
    for k in range(5):
        tr, te = d.fold != k, d.fold == k
        kn = kn_probs(d.prev[tr], d.cur[tr], d.prev[te], d.cur[te], d.V)
        un = unigram_probs(d.cur[tr], d.cur[te], d.V)
        bits_kn -= np.log2(kn).sum()
        bits_uni -= np.log2(un).sum()
        n += te.sum()
    return {"types": len(vocab), "bigram_bits": bits_kn / n, "unigram_bits": bits_uni / n,
            "bigram_gain_bits": (bits_uni - bits_kn) / n, "substitution_frame_pairs": substitution_frames(rec)}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--coder2")
    ap.add_argument("--nulls", type=int, default=200)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)

    items = common.load_clean()
    texts = [d["text"] for d in items]
    folds = [d["fold"] for d in items]
    comp_names = sorted({d["component"] for d in items})
    comp_idx = {c: i for i, c in enumerate(comp_names)}
    comp_of_text = [comp_idx[d["component"]] for d in items]

    coding_path = common.PROG / "step1-signs/sign_components_v1.tsv"
    coding = common.load_coding(coding_path)
    corpus_codes = sorted({s for t in texts for s in t})
    missing = [c for c in corpus_codes if c not in coding]
    vocab = sorted(set(coding) | set(corpus_codes))
    inv = common.inventories(coding, vocab)
    modsig = common.modifier_signature(coding, vocab)
    tok = collections.Counter(s for t in texts for s in t)

    summary = {"protocol_sha256": common.sha256(common.PROG / "PROTOCOL.md"),
               "coding_sha256": common.sha256(coding_path),
               "clean_sha256": common.sha256(common.CLEAN),
               "distinct_texts": len(texts), "tokens": sum(tok.values()), "attested_codes": len(corpus_codes),
               "codes_missing_from_coding": missing, "vocabulary": len(vocab),
               "fold_sizes_texts": collections.Counter(folds), "components": len(comp_names)}

    summary["profiles"] = {k: profile(texts, inv[k]) for k in ("W", "V", "P", "M", "B")}

    groupings = {"B_coder1": inv["B"], "V": inv["V"], "P": inv["P"], "M": inv["M"], "modifier_signature": modsig}
    coder2 = None
    if args.coder2:
        coder2 = common.load_coding(args.coder2)
        b2 = {c: (coder2[c]["base"] if c in coder2 else "W" + c) for c in vocab}
        groupings["B_coder2"] = b2
        att = corpus_codes
        a1 = [inv["B"][c] for c in att]
        a2 = [b2[c] for c in att]
        agree = {"codes_compared": len(att),
                 "codes_missing_in_coder2": [c for c in att if c not in coder2],
                 "ari_unweighted": ari(a1, a2), "ari_token_weighted": ari(a1, a2, [tok[c] for c in att]),
                 "coder1_families_attested": len(set(a1)), "coder2_families_attested": len(set(a2)),
                 "modifier_kappa": {}}
        vocab_mods = ["encl", "dots", "inner", "side", "top", "cap", "bar", "hatch", "double", "hold", "pole",
                      "yoke", "X", "variant"]
        both = [c for c in att if c in coder2]
        for m in vocab_mods:
            x = [m in coding[c]["mods"] for c in both]
            y = [m in coder2[c]["mods"] for c in both]
            agree["modifier_kappa"][m] = {"kappa": kappa(x, y), "coder1_n": sum(x), "coder2_n": sum(y)}
        summary["coder_agreement"] = agree

    data = Data(texts, folds, vocab)
    ev = Evaluator(data, comp_of_text)
    summary["baseline"] = {"kn_bits_per_sign": ev.base_bits, "unigram_bits_per_sign": ev.uni_bits,
                           "held_out_tokens": int(ev.n)}

    # training-frequency strata for each held-out token
    strata = np.zeros(ev.n, dtype=int)
    pos = 0
    for k, s in enumerate(ev.splits):
        nw = np.bincount(s["ct"], minlength=data.V)
        f = nw[s["ce"]]
        strata[pos:pos + len(f)] = np.select([f == 0, f <= 2, f <= 9], [0, 1, 2], 3)
        pos += len(f)
    base_tok = np.concatenate([-np.log2(s["kn"]) for s in ev.splits])
    names = ["seen0", "seen1-2", "seen3-9", "seen10+"]

    rng = np.random.default_rng(common.SEED + 1)
    results = {}
    for g, mapping in groupings.items():
        cls, ncls = class_array(data, mapping)
        bits, lams, per_tok = ev.evaluate(cls, ncls, keep_tokens=True)
        gain = ev.base_bits - bits
        null = []
        labels = cls[:-1].copy()
        for r in range(args.nulls):
            perm = rng.permutation(labels)
            rc = np.concatenate([perm, [cls[-1]]])
            b, _, _ = ev.evaluate(rc, ncls)
            null.append(ev.base_bits - b)
        null = np.array(null)
        strat = {}
        for i, nm in enumerate(names):
            m = strata == i
            strat[nm] = {"tokens": int(m.sum()), "baseline_bits": float(base_tok[m].mean()) if m.any() else None,
                         "class_bits": float(per_tok[m].mean()) if m.any() else None}
        sizes = collections.Counter(collections.Counter(mapping[c] for c in vocab).values())
        results[g] = {"groups": len(set(mapping[c] for c in vocab)),
                      "non_singleton_groups": sum(1 for v in collections.Counter(mapping[c] for c in vocab).values() if v > 1),
                      "bits_per_sign": bits, "gain_bits": gain, "lambda_by_fold": lams,
                      "null_mean": float(null.mean()), "null_p95": float(np.quantile(null, 0.95)),
                      "null_max": float(null.max()),
                      "p_value": float((1 + (null >= gain).sum()) / (1 + len(null))),
                      "passes": bool(gain > 0 and gain > np.quantile(null, 0.95)),
                      "by_training_frequency": strat}
        print(g, json.dumps({k: results[g][k] for k in ("gain_bits", "null_p95", "p_value", "passes")}), flush=True)
    summary["grouping_tests"] = results

    # modifier productivity among attested codes
    prod = {}
    for c in corpus_codes:
        row = coding.get(c)
        if not row:
            continue
        for m in row["mods"]:
            d = prod.setdefault(m, {"bases": set(), "codes": 0, "tokens": 0})
            d["bases"].add(row["base"])
            d["codes"] += 1
            d["tokens"] += tok[c]
    summary["modifier_productivity"] = {m: {"bases": len(v["bases"]), "codes": v["codes"], "tokens": v["tokens"]}
                                        for m, v in sorted(prod.items(), key=lambda x: -len(x[1]["bases"]))}
    fam = collections.Counter()
    famtok = collections.Counter()
    for c in corpus_codes:
        fam[inv["B"][c]] += 1
        famtok[inv["B"][c]] += tok[c]
    summary["largest_families"] = [{"base": b, "attested_codes": n, "tokens": famtok[b]} for b, n in fam.most_common(15)]
    summary["granularity"] = {k: granularity(texts, folds, inv[k]) for k in ("W", "V", "P", "M", "B")}

    # decision
    passing = [g for g in ("B_coder1", "B_coder2", "V", "P", "M", "modifier_signature")
               if g in results and results[g]["passes"]]
    coarse_order = ["B_coder1", "B_coder2", "modifier_signature", "P", "M", "V"]
    adopted = next((g for g in coarse_order if g in passing), None)
    summary["decision"] = {"passing_groupings": passing, "adopted_feature_layer": adopted,
                           "rule": "Coarsest grouping whose gain is positive and above its random-partition 95th percentile; W codes stay the unit."}

    def default(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, set):
            return sorted(o)
        raise TypeError(type(o))

    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=default) + "\n", encoding="utf-8")
    print(json.dumps(summary["decision"]))


if __name__ == "__main__":
    main()
