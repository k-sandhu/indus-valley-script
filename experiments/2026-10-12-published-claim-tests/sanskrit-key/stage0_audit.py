"""Stage 0: reproduce the key's skeletons and compare them with the published readings.

Outputs (tracked, aggregate): stage0/summary.json
Outputs (local, per inscription): data/raw/.../sanskrit-key/stage0_rows.jsonl
"""
import csv
import json
import os
import re
from collections import Counter

from common import (GLOSSING_CSV, HERE, INSCRIPTIONS_CSV, KEY_CSV, RAW, app_transliteration,
                    load_key, resolve_values, sha256, slp1_skeleton)


def edit_ops(a: str, b: str):
    """Levenshtein distance with the substitution pairs of one optimal alignment."""
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    ops = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            if a[i - 1] != b[j - 1]:
                ops.append(("sub", a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            ops.append(("del", a[i - 1], ""))
            i -= 1
        else:
            ops.append(("ins", "", b[j - 1]))
            j -= 1
    return d[n][m], ops


def main():
    key = load_key()
    values = resolve_values(key)
    skel = {s: slp1_skeleton(v) for s, v in values.items()}

    with open(INSCRIPTIONS_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_id = {r["id"]: r for r in rows}

    out_rows = []
    counts = Counter()
    sub_pairs = Counter()
    op_kinds = Counter()
    missing_signs = Counter()
    for r in rows:
        reading = (r.get("sanskrit") or "").strip()
        if not reading:
            counts["no_reading"] += 1
            continue
        if reading.startswith("ref:"):
            counts["reference_to_other_reading"] += 1
            continue
        if re.search(r"[\U00012000-\U0001254F]", r.get("translation") or ""):
            counts["cuneiform_entry"] += 1
            continue
        codes = re.findall(r"\d+", r["text"])[::-1]
        codes = [c for c in codes if c not in ("999",)]
        if any(c not in skel for c in codes):
            for c in codes:
                if c not in skel:
                    missing_signs[c] += 1
            counts["sign_missing_from_key"] += 1
            continue
        if "000" in codes:
            counts["contains_unknown_sign"] += 1
            continue
        key_skel = "".join(skel[c] for c in codes)
        read_skel = slp1_skeleton(reading)
        dist, ops = edit_ops(key_skel, read_skel)
        counts["compared"] += 1
        counts["exact"] += dist == 0
        for kind, a, b in ops:
            op_kinds[kind] += 1
            if kind == "sub":
                sub_pairs[f"{a}>{b}"] += 1
            elif kind == "del":
                sub_pairs[f"{a}>-"] += 1
            else:
                sub_pairs[f"->{b}"] += 1
        out_rows.append({
            "id": r["id"], "complete": r["complete"], "length": len(codes),
            "key_skeleton": key_skel, "reading": reading, "reading_skeleton": read_skel,
            "distance": dist, "app_transliteration": app_transliteration(codes, values),
        })

    # glossing: lemma counts and skeleton lengths
    with open(GLOSSING_CSV, encoding="utf-8") as f:
        gl = list(csv.DictReader(f))
    lemmas_per_id = Counter(g["id"] for g in gl)
    lemma_len = Counter(len(slp1_skeleton(g["form"])) for g in gl)
    by_text_len = {}
    for rid, k in lemmas_per_id.items():
        rr = next((x for x in out_rows if x["id"] == rid), None)
        if rr is None:
            continue
        L = len(rr["reading_skeleton"])
        by_text_len.setdefault(L, []).append(k)
    lemma_profile = {str(L): {"texts": len(v), "max_lemmas": max(v), "mean_lemmas": round(sum(v) / len(v), 3)}
                     for L, v in sorted(by_text_len.items())}

    compared = counts["compared"]
    dists = Counter(x["distance"] for x in out_rows)
    complete_rows = [x for x in out_rows if x["complete"] == "Y"]
    summary = {
        "inputs": {
            "inscriptions_csv_sha256": sha256(INSCRIPTIONS_CSV),
            "xlits_csv_sha256": sha256(KEY_CSV),
            "glossing_csv_sha256": sha256(GLOSSING_CSV),
        },
        "key": {
            "rows": len(key),
            "signs_with_nonempty_skeleton": sum(1 for s, v in skel.items() if v and s not in ("000", "999")),
            "signs_with_empty_skeleton": sorted(s for s, v in skel.items() if not v and s not in ("000", "999")),
            "skeleton_value_counts": Counter(v for s, v in skel.items() if s not in ("000", "999")).most_common(),
        },
        "record_counts": dict(counts),
        "missing_signs": dict(missing_signs),
        "distance_distribution": {str(k): v for k, v in sorted(dists.items())},
        "exact_share": round(counts["exact"] / compared, 4) if compared else None,
        "exact_share_complete_records": round(sum(x["distance"] == 0 for x in complete_rows) / len(complete_rows), 4),
        "complete_records_compared": len(complete_rows),
        "mean_distance_per_key_consonant": round(
            sum(x["distance"] for x in out_rows) / max(1, sum(len(x["key_skeleton"]) for x in out_rows)), 4),
        "edit_operation_counts": dict(op_kinds),
        "top_departures": sub_pairs.most_common(30),
        "glossing": {
            "rows": len(gl),
            "inscriptions_glossed": len(lemmas_per_id),
            "lemma_skeleton_length_distribution": {str(k): v for k, v in sorted(lemma_len.items())},
            "lemmas_per_text_by_reading_skeleton_length": lemma_profile,
        },
    }
    os.makedirs(os.path.join(HERE, "stage0"), exist_ok=True)
    with open(os.path.join(HERE, "stage0", "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    local = os.path.join(RAW, "sanskrit-key")
    os.makedirs(local, exist_ok=True)
    with open(os.path.join(local, "stage0_rows.jsonl"), "w", encoding="utf-8") as f:
        for x in out_rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(json.dumps({k: summary[k] for k in ("record_counts", "distance_distribution", "exact_share",
                                              "exact_share_complete_records", "mean_distance_per_key_consonant",
                                              "edit_operation_counts", "top_departures")}, ensure_ascii=False))
    print(json.dumps(summary["glossing"], ensure_ascii=False))
    print("empty skeleton signs:", summary["key"]["signs_with_empty_skeleton"][:80])
    print("value counts:", summary["key"]["skeleton_value_counts"][:40])


if __name__ == "__main__":
    main()
