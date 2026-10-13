"""Locality, whole-text reuse and motif concordance of identical Indus seal texts (PROTOCOL.md)."""
import hashlib
import json
import math
import os
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FACES = os.path.join(ROOT, "data", "normalized", "lipi_observed_faces.jsonl")
LOCAL = os.path.join(ROOT, "data", "raw", "2026-10-12-seal-text-identity")
SEED = 20261012
N_PERM = 10000
FOREIGN = {"Altyn Depe", "Failaka", "Hajar", "Ra's al-Junayz", "Kish", "Luristan", "Nippur", "Qala'at al-Bahrain",
           "Shortughai", "Susa", "Tell Umma", "Tello", "Tepe Yahya", "Ur", "Gonur Depe", "Salut", "Girsu",
           "Karzakan", "Saar", "Janabiyah", "Kalba", "Dilmun"}
NO_MOTIF = {"None", "-", "", None}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def text_id(t):
    return hashlib.sha1("-".join(t).encode()).hexdigest()[:10]


def load():
    with open(FACES, encoding="utf-8") as f:
        faces = [json.loads(l) for l in f]
    return faces


def legible(f, min_len):
    return (f["complete_observed"] and f["single_line"] and not f["has_unknown_sign"]
            and len(f["signs_reading_rtl"]) >= min_len and "000" not in f["signs_reading_rtl"])


def eligible_seals(faces):
    by_fam = {}
    for f in faces:
        if not f["object_type"].startswith("SEAL") or not legible(f, 2):
            continue
        if f["site"] in FOREIGN or f["site"] in ("Unknown", "", None):
            continue
        fam = f["object_family_id"]
        if fam not in by_fam or float(f["record_id"]) < float(by_fam[fam]["record_id"]):
            by_fam[fam] = f
    seals = sorted(by_fam.values(), key=lambda f: float(f["record_id"]))
    return seals


def motif(f):
    m = f.get("symbol")
    if m in NO_MOTIF:
        return None
    m = m.split(":")[0]
    return None if m in NO_MOTIF else m


# ----------------------------------------------------------------------------- S1 / S2 / S4 helpers

def groups_by_text(seals):
    g = defaultdict(list)
    for i, f in enumerate(seals):
        g[tuple(f["signs_reading_rtl"])].append(i)
    return {t: idx for t, idx in g.items() if len(idx) >= 2}


def same_label_stats(groups, labels):
    """Text-weighted mean share of same-label pairs, and pair-weighted share."""
    shares, same_tot, pair_tot = [], 0, 0
    for idx in groups:
        lab = labels[idx]
        k = len(lab)
        pairs = k * (k - 1) // 2
        _, cnt = np.unique(lab, return_counts=True)
        same = int((cnt * (cnt - 1) // 2).sum())
        shares.append(same / pairs)
        same_tot += same
        pair_tot += pairs
    return float(np.mean(shares)), same_tot / pair_tot


def permutation_test(groups, labels, rng, n=N_PERM, strata=None):
    obs_t, obs_p = same_label_stats(groups, labels)
    null_t, null_p = np.empty(n), np.empty(n)
    for r in range(n):
        if strata is None:
            perm = labels[rng.permutation(len(labels))]
        else:
            perm = labels.copy()
            for s in np.unique(strata):
                pos = np.where(strata == s)[0]
                perm[pos] = labels[pos][rng.permutation(len(pos))]
        null_t[r], null_p[r] = same_label_stats(groups, perm)
    def summ(obs, null):
        return {"observed": obs, "null_mean": float(null.mean()), "null_q025": float(np.quantile(null, 0.025)),
                "null_q975": float(np.quantile(null, 0.975)), "p_one_sided": float((1 + (null >= obs).sum()) / (n + 1)),
                "ratio_to_null_mean": obs / float(null.mean()) if null.mean() > 0 else None}
    return {"text_weighted": summ(obs_t, null_t), "pair_weighted": summ(obs_p, null_p), "texts": len(groups),
            "pairs": int(sum(len(i) * (len(i) - 1) // 2 for i in groups))}


# ----------------------------------------------------------------------------- S3

def kn_bigram(texts, vocab):
    """Interpolated Kneser-Ney bigram over vocab + END, with START context. Returns s, T, e."""
    V = len(vocab)
    vid = {v: i for i, v in enumerate(vocab)}
    START, END = V, V  # START as a context row index V; END as an outcome column index V
    counts = np.zeros((V + 1, V + 1))
    for t in texts:
        prev = START
        for x in t:
            counts[prev, vid[x]] += 1
            prev = vid[x]
        counts[prev, END] += 1
    n1 = (counts == 1).sum()
    n2 = (counts == 2).sum()
    D = n1 / (n1 + 2 * n2)
    cont = (counts > 0).sum(axis=0).astype(float)  # distinct left contexts per outcome
    p_cont = cont / cont.sum()
    P = np.zeros_like(counts)
    for v in range(V + 1):
        c = counts[v].sum()
        if c == 0:
            P[v] = p_cont
        else:
            types = (counts[v] > 0).sum()
            P[v] = np.maximum(counts[v] - D, 0) / c + D * types / c * p_cont
    s = P[START, :V]
    T = P[:V, :V]
    e = P[:V, END]
    return s, T, e, D


def coincidence_by_length(s, T, e, max_len):
    """For each L: P(L) and sum over texts of length L of P(text)^2."""
    out = {}
    a = s.copy()          # forward mass over last symbol, length 1
    a2 = s ** 2
    T2 = T ** 2
    e2 = e ** 2
    for L in range(1, max_len + 1):
        pL = float(a @ e)
        s2 = float(a2 @ e2)
        out[L] = (pL, s2)
        a = a @ T
        a2 = a2 @ T2
    return out


def main():
    os.makedirs(LOCAL, exist_ok=True)
    rng = np.random.default_rng(SEED)
    faces = load()
    seals = eligible_seals(faces)
    sites = np.array([f["site"] for f in seals])
    groups = groups_by_text(seals)
    gl = list(groups.values())
    out = {"input_sha256": sha256(FACES), "eligible_seal_objects": len(seals),
           "sites": Counter(sites.tolist()).most_common(), "shared_texts": len(gl),
           "seal_objects_in_shared_texts": int(sum(len(i) for i in gl))}

    # S1
    out["S1_all"] = permutation_test(gl, sites, rng)
    for name, cond in (("len2", lambda L: L == 2), ("len3", lambda L: L == 3), ("len4plus", lambda L: L >= 4)):
        sub = [i for t, i in groups.items() if cond(len(t))]
        out[f"S1_{name}"] = permutation_test(sub, sites, rng) if sub else None
    cross = [(t, i) for t, i in groups.items() if len(set(sites[i])) > 1]
    out["shared_texts_spanning_sites"] = {"all": len(cross),
                                          "len4plus": sum(1 for t, _ in cross if len(t) >= 4)}

    # S2
    mh = np.isin(sites, ["Mohenjo-daro", "Harappa"])
    mh_idx = np.where(mh)[0]
    remap = {old: new for new, old in enumerate(mh_idx)}
    gl_mh = [[remap[i] for i in idx if i in remap] for idx in gl]
    gl_mh = [g for g in gl_mh if len(g) >= 2]
    out["S2_mohenjo_harappa"] = permutation_test(gl_mh, sites[mh_idx], rng)
    per = np.array([seals[i]["metadata"].get("period") for i in range(len(seals))])
    md = np.where((sites == "Mohenjo-daro") & np.isin(per, ["Early", "Intermediate", "Late"]))[0]
    remap = {old: new for new, old in enumerate(md)}
    gl_md = [[remap[i] for i in idx if i in remap] for idx in gl]
    gl_md = [g for g in gl_md if len(g) >= 2]
    out["S2_mohenjo_period_agreement"] = permutation_test(gl_md, per[md], rng) if gl_md else None

    # S3
    legible_texts = sorted({tuple(f["signs_reading_rtl"]) for f in faces if legible(f, 1)})
    vocab = sorted({x for t in legible_texts for x in t})
    s, T, e, D = kn_bigram(legible_texts, vocab)
    lens = Counter(len(f["signs_reading_rtl"]) for f in seals)
    coinc = coincidence_by_length(s, T, e, max(lens))
    obs_pairs = Counter()
    for t, idx in groups.items():
        k = len(idx)
        obs_pairs[len(t)] += k * (k - 1) // 2
    rows = {}
    for L in sorted(lens):
        n = lens[L]
        pL, s2 = coinc[L]
        expected = math.comb(n, 2) * s2 / pL ** 2
        rows[str(L)] = {"seals": n, "observed_identical_pairs": obs_pairs[L], "expected_pairs_model": expected,
                        "ratio": obs_pairs[L] / expected if expected > 0 else None}
    exp4 = sum(r["expected_pairs_model"] for L, r in rows.items() if int(L) >= 4)
    obs4 = sum(r["observed_identical_pairs"] for L, r in rows.items() if int(L) >= 4)
    out["S3_whole_text_reuse"] = {"model": "interpolated Kneser-Ney bigram, distinct legible texts of all object types",
                                  "training_texts": len(legible_texts), "discount": D, "by_length": rows,
                                  "len4plus": {"observed": obs4, "expected": exp4, "ratio": obs4 / exp4 if exp4 else None}}

    # S4
    mot = np.array([motif(f) or "" for f in seals])
    has = np.where(mot != "")[0]
    remap = {old: new for new, old in enumerate(has)}
    gl_m = [[remap[i] for i in idx if i in remap] for idx in gl]
    gl_m = [g for g in gl_m if len(g) >= 2]
    out["S4_motif_concordance"] = permutation_test(gl_m, mot[has], rng, strata=sites[has]) if gl_m else None
    out["motif_counts"] = Counter(mot[has].tolist()).most_common()

    # S5
    seal_text_sites = defaultdict(list)
    for f in seals:
        seal_text_sites[tuple(f["signs_reading_rtl"])].append((f["site"], f["record_id"]))
    s5 = []
    for f in faces:
        if f["object_type"].startswith("TAG") and legible(f, 2):
            t = tuple(f["signs_reading_rtl"])
            if t in seal_text_sites:
                s5.append({"tag_record": f["record_id"], "tag_site": f["site"], "tag_type": f["object_type"],
                           "length": len(t), "text_id": text_id(t),
                           "seal_sites": Counter(s for s, _ in seal_text_sites[t]).most_common(),
                           "seal_records": [r for _, r in seal_text_sites[t]][:10]})
    out["S5_tags_matching_seals"] = {"count": len(s5),
                                     "other_site_matches": sum(1 for r in s5 if any(s != r["tag_site"] for s, _ in r["seal_sites"])),
                                     "rows": s5}

    # tracked group table without sequences; local table with sequences
    table = []
    for t, idx in sorted(groups.items(), key=lambda x: (-len(x[1]), x[0])):
        table.append({"text_id": text_id(t), "length": len(t), "objects": len(idx),
                      "sites": Counter(sites[idx].tolist()).most_common(),
                      "motifs": Counter(mot[idx].tolist()).most_common(),
                      "records": [seals[i]["record_id"] for i in idx]})
    os.makedirs(os.path.join(HERE, "run-2026-10-12"), exist_ok=True)
    with open(os.path.join(HERE, "run-2026-10-12", "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "run-2026-10-12", "shared-texts.json"), "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=1)
    with open(os.path.join(LOCAL, "shared-texts-with-sequences.json"), "w", encoding="utf-8") as f:
        json.dump([{**row, "signs": list(t)} for row, t in zip(table, sorted(groups, key=lambda x: (-len(groups[x]), x)))],
                  f, ensure_ascii=False, indent=1)
    brief = {k: out[k] for k in ("eligible_seal_objects", "shared_texts", "seal_objects_in_shared_texts",
                                 "shared_texts_spanning_sites")}
    print(json.dumps(brief))
    for k in ("S1_all", "S1_len2", "S1_len3", "S1_len4plus", "S2_mohenjo_harappa", "S2_mohenjo_period_agreement",
              "S4_motif_concordance"):
        v = out[k]
        if v:
            print(k, v["texts"], v["pairs"], {x: round(v["text_weighted"][x], 3) for x in ("observed", "null_mean", "null_q975", "p_one_sided")},
                  "pair", round(v["pair_weighted"]["observed"], 3), round(v["pair_weighted"]["null_mean"], 3))
    print("S3", json.dumps(out["S3_whole_text_reuse"]["len4plus"]),
          {L: (r["observed_identical_pairs"], round(r["expected_pairs_model"], 2)) for L, r in out["S3_whole_text_reuse"]["by_length"].items()})
    print("S5", out["S5_tags_matching_seals"]["count"], out["S5_tags_matching_seals"]["other_site_matches"])


if __name__ == "__main__":
    main()
