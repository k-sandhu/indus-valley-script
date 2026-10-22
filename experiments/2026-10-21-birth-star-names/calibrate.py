"""Calibration on Lüders's Brahmi donor names (PROTOCOL.md, Part 1).

Reads the donor rows, the two markings and the resolved marking, measures agreement, and computes
the class statistics of asterism elements and of other name elements, with matched-size draws.
"""
import argparse
from collections import Counter
import csv
import difflib
import json
from pathlib import Path
import re
import sys
import unicodedata

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import birthstar as bs  # noqa: E402

SECOND = sorted(["datta", "data", "dina", "dinna", "dinaka", "mitra", "mita", "mitta", "miti", "raksita", "rakhita",
                 "palita", "pala", "gupta", "guta", "deva", "dev", "sena", "bhuti", "nandin", "nandi", "nanda", "sri",
                 "siri", "dasa", "dasi", "ghosa", "bala", "sarman", "varman", "yasas", "yasa", "giri", "sarma",
                 "bhadra", "bhaga", "datta"], key=len, reverse=True)
HONORIFIC = re.compile(r"^(?:ayya|aya|arya|aryya|bhadamta|bhadanta|bhayamta)")


def skeleton(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.split(r"\s+or\s+", s)[0]
    s = re.sub(r"[^a-z]", "", s)
    s = HONORIFIC.sub("", s) if len(s) > 6 else s
    return s.replace("sh", "s").replace("ch", "c")


def best_form(r):
    """Prefer a Sanskrit equivalent, choosing the scan whose reading looks least damaged."""
    cands = [r["sanskrit"], r["sanskrit_b"]]
    cands = [c for c in cands if len(skeleton(c)) >= 3]
    if not cands:
        cands = [c for c in (r["name"], r["name_b"]) if len(skeleton(c)) >= 3]
    if not cands:
        return ""
    return min(cands, key=lambda c: sum(not ch.isalpha() and ch not in " -" for ch in c))


def first_member(form):
    s = skeleton(form)
    for suf in SECOND:
        if s.endswith(suf) and len(s) - len(suf) >= 3:
            s = s[: -len(suf)]
            break
    s = re.sub(r"(?:ika|aka|ila|iya|ka|ki)$", "", s) if len(s) > 5 else s
    s = re.sub(r"[aiu]+$", "", s)
    return s


def cluster(tokens, threshold=0.85):
    """Merge OCR variants: each element joins the commonest earlier element within the similarity threshold."""
    counts = Counter(tokens)
    reps, mapping = [], {}
    for t, _ in counts.most_common():
        match = next((r for r in reps if difflib.SequenceMatcher(None, t, r).ratio() >= threshold), None)
        mapping[t] = match or t
        if not match:
            reps.append(t)
    return [mapping[t] for t in tokens]


def kappa(a, b):
    labels = sorted(set(a) | set(b))
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[l] * cb[l] for l in labels) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else None


def read(path):
    with Path(path).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def class_block(tokens, pool, draws, seed):
    st = bs.stats(tokens)
    out = {"stats": st}
    if st["N"] and len(pool) > st["N"]:
        out["matched_other_elements"] = bs.compare(st, bs.matched(pool, st["N"], draws, seed))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--marking-a", required=True)
    ap.add_argument("--marking-b", required=True)
    ap.add_argument("--resolved", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--draws", type=int, default=9999)
    ap.add_argument("--seed", type=int, default=20261021)
    args = ap.parse_args()
    rows = {r["row_id"]: r for r in read(args.rows)}
    ma = {r["row_id"]: r for r in read(args.marking_a)}
    mb = {r["row_id"]: r for r in read(args.marking_b)}
    res = {r["row_id"]: r for r in read(args.resolved)}
    ids = list(rows)
    agree = {
        "rows": len(ids),
        "marked_A": sum(bool(ma[i]["asterism"]) for i in ids),
        "marked_B": sum(bool(mb[i]["asterism"]) for i in ids),
        "kappa_asterism_vs_not": kappa([bool(ma[i]["asterism"]) for i in ids], [bool(mb[i]["asterism"]) for i in ids]),
        "kappa_label": kappa([ma[i]["asterism"] for i in ids], [mb[i]["asterism"] for i in ids]),
        "kappa_strict_label": kappa([ma[i]["asterism"] if ma[i]["strength"] == "strict" else "" for i in ids],
                                    [mb[i]["asterism"] if mb[i]["strength"] == "strict" else "" for i in ids]),
        "disagreements": sum(ma[i]["asterism"] != mb[i]["asterism"] for i in ids),
    }
    personal = [i for i in res if res[i].get("personal_name", "yes") == "yes"]
    for i in personal:
        rows.setdefault(i, {"name": "", "sanskrit": "", "name_b": "", "sanskrit_b": ""})
    out = {"agreement": agree, "donor_rows": len(ids), "personal_name_rows": len(personal), "variants": {}}
    for variant in ("strict", "broad"):
        keep = (lambda i: res[i]["asterism"] and res[i]["strength"] == "strict") if variant == "strict" else (lambda i: bool(res[i]["asterism"]))
        ast_ids = [i for i in personal if keep(i)]
        other_ids = [i for i in personal if not res[i]["asterism"]]
        ast_tokens = [res[i]["asterism"] for i in ast_ids]
        other_raw = [first_member(best_form(rows[i])) for i in other_ids]
        other_raw = [t for t in other_raw if t]
        other_clustered = cluster(other_raw)
        names_clustered = cluster([skeleton(best_form(rows[i])) for i in other_ids if skeleton(best_form(rows[i]))])
        k = len(ast_ids)
        block = {"asterism_rows": k, "share": k / len(personal), "share_wilson95": bs.wilson(k, len(personal)),
                 "distinct_asterisms": len(set(ast_tokens)), "asterism_counts": dict(Counter(ast_tokens).most_common()),
                 "normalised_entropy_over_25_labels": float(bs.stats(ast_tokens)["entropy_nats"] / np.log(25)) if ast_tokens else None,
                 "asterism_elements": class_block(ast_tokens, other_clustered, args.draws, args.seed),
                 "other_elements_clustered": {"stats": bs.stats(other_clustered)},
                 "other_elements_unclustered": {"stats": bs.stats(other_raw)},
                 "other_full_names_clustered": {"stats": bs.stats(names_clustered)},
                 "other_elements_top": dict(Counter(other_clustered).most_common(25))}
        curve = {}
        rng_seed = args.seed + 7
        for n in (15, 30, 45, 60, 90, 120, 240):
            entry = {}
            if n <= len(ast_tokens):
                entry["asterism"] = {key: bs.summarise(v) for key, v in bs.matched(ast_tokens, n, 999, rng_seed).items()}
            if n < len(other_clustered):
                entry["other_elements"] = {key: bs.summarise(v) for key, v in bs.matched(other_clustered, n, 999, rng_seed + 1).items()}
            if entry:
                curve[str(n)] = entry
        block["discrimination_curve"] = curve
        out["variants"][variant] = block
    out["inputs"] = {p: bs_sha(p) for p in (args.rows, args.marking_a, args.marking_b, args.resolved)}
    out["script_sha256"] = bs_sha(__file__)
    out["library_sha256"] = bs_sha(HERE / "birthstar.py")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "x", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"agreement": agree, "strict": {k: out["variants"]["strict"][k] for k in ("asterism_rows", "share", "distinct_asterisms", "asterism_counts")}}, indent=2))


def bs_sha(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
