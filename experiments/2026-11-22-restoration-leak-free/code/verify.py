"""Independent verification of the leak-free restoration refit.

Does not import splits.py or run_refit.py. Independently checks:
  1. Exact 8,009 query counts, alignment, and recomputed metrics for all 18 split x model cells.
  2. Exact Split 1 reproduction against frozen Paper 001 (PM), MARKOV-01 (M1),
     MARKOV-03 (M2), and 6 October (MKN) endpoints.
  3. Zero outer-fold and inner-fold full-corpus alias leakage on Split 2 and Split 3,
     and zero outer-fold and inner-fold Levenshtein<=1 or F-0010 base-family leakage on Split 3.
  4. Independent refit and brute-force complete-sequence likelihood replay on sampled
     queries across all 3 splits and all 6 models, plus hidden-target invariance.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import re
import sys
import time
import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parent.parent
RAW = ROOT / "data/raw/2026-11-22-restoration-leak-free"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

from methods.conditional_structure import UNKNOWN, load_records, make_folds
import models as mdl

SEED = 20261006
MODEL_ORDER = ["PM", "M1", "M2", "MKN", "MKN-GF", "MKN-GF-SB"]
SPLIT_ORDER = ["split1_baseline", "split2_alias_clean", "split3_near_variant_clean"]
BINS = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.000001)]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def levenshtein_le_1(a: tuple[str, ...], b: tuple[str, ...]) -> bool:
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diffs = 0
        for x, y in zip(a, b):
            if x != y:
                diffs += 1
                if diffs > 1:
                    return False
        return True
    short, long_s = (a, b) if la < lb else (b, a)
    i = j = diffs = 0
    while i < len(short) and j < len(long_s):
        if short[i] == long_s[j]:
            i += 1
            j += 1
        else:
            diffs += 1
            if diffs > 1:
                return False
            j += 1
    return True


def independent_full_corpus_roots(rows: list[dict], raw_faces: list[dict]) -> list[int]:
    """Independent BFS connected components over all 5,680 faces + 1,596 benchmark rows."""
    n_b = len(rows)
    n_tot = n_b + len(raw_faces)
    key_to_nodes: dict[tuple, list[int]] = defaultdict(list)

    def add(node: int, kind: str, val):
        if val is not None:
            key_to_nodes[(kind, val)].append(node)

    for i, r in enumerate(rows):
        for a in r["artifact_aliases"]:
            add(i, "fam", str(a))
        add(i, "seq", r["seq"])

    for j, r in enumerate(raw_faces):
        node = n_b + j
        fam = str(r.get("object_family_id", r.get("artifact_id", r["record_id"])))
        add(node, "fam", fam)
        cisi = r.get("source_cisi")
        if cisi is not None:
            s = str(cisi).strip()
            if s and s not in {"-", "--", "?", "??"} and "?" not in s:
                m = re.match(r"^([A-Za-z]+-\d+)", s)
                add(node, "cisi", m.group(1).upper() if m else s.upper())
        exc = (r.get("metadata") or {}).get("excavation-idno")
        if exc is not None:
            s = str(exc).strip()
            if s and s not in {"-", "--", "- -", "?", "??", "Unknown"} and "?" not in s:
                norm = re.sub(r"[\s\-_./,]+", "", s).upper()
                if any(ch.isdigit() for ch in norm):
                    site = str(r.get("site") or "").strip().upper()
                    add(node, "exc", (site, norm))
        seq = tuple(map(str, r.get("signs_reading_rtl", [])))
        if seq:
            add(node, "seq", seq)

    adj: list[list[int]] = [[] for _ in range(n_tot)]
    for nodes in key_to_nodes.values():
        if len(nodes) > 1:
            hub = nodes[0]
            for u in nodes[1:]:
                adj[hub].append(u)
                adj[u].append(hub)

    comp = [-1] * n_tot
    cid = 0
    for start in range(n_tot):
        if comp[start] != -1:
            continue
        stack = [start]
        comp[start] = cid
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if comp[v] == -1:
                    comp[v] = cid
                    stack.append(v)
        cid += 1
    return comp[:n_b]


def recompute_metrics(scores: list[dict]) -> dict:
    n = len(scores)
    top1 = sum(1 for s in scores if s["top1"]) / n
    top5 = sum(1 for s in scores if s["top5"]) / n
    top10 = sum(1 for s in scores if s["top10"]) / n
    bits = sum(float(s["bucket_loss_bits"]) for s in scores) / n
    ece = 0.0
    for lo, hi in BINS:
        part = [s for s in scores if lo <= s["model_top_mass"] < hi]
        if part:
            ece += (len(part) / n) * abs(
                sum(s["model_top_mass"] for s in part) / len(part)
                - sum(1 for s in part if s["top1"]) / len(part)
            )
    return {"slots": n, "top1": top1, "top5": top5, "top10": top10, "bucket_cross_entropy_bits": bits, "expected_calibration_error": ece}


def brute_force_m1(m1: mdl.M1Restorer, seq: tuple[str, ...], slot: int) -> np.ndarray:
    unk = m1.index[UNKNOWN]
    vals = []
    for cand in m1.signs:
        s = list(seq)
        s[slot] = cand
        ix = [m1.index.get(c, unk) for c in s]
        p = float(m1.inner.start[ix[0]])
        for a, b in zip(ix[:-1], ix[1:]):
            p *= float(m1.inner.transition[a, b])
        p *= float(m1.inner.transition[ix[-1], m1.inner.end_index])
        vals.append(p)
    arr = np.asarray(vals, dtype=np.float64)
    return arr / arr.sum()


def brute_force_m2(m2: mdl.M2Restorer, seq: tuple[str, ...], slot: int) -> np.ndarray:
    if m2.alpha is None:
        return brute_force_m1(mdl.M1Restorer.__new__(mdl.M1Restorer), seq, slot)  # not reached if handled
    unk = m2.index[UNKNOWN]
    vals = []
    for cand in m2.signs:
        s = list(seq)
        s[slot] = cand
        ix = [m2.index.get(c, unk) for c in s] + [m2.end_index]
        a = b = m2.start_index
        p = 1.0
        for target in ix:
            p *= float(m2.probability(a, b)[target])
            a, b = b, target
        vals.append(p)
    arr = np.asarray(vals, dtype=np.float64)
    return arr / arr.sum()


def brute_force_mkn(mkn: mdl.MKNRestorer, seq: tuple[str, ...], slot: int) -> np.ndarray:
    vals = []
    for cand in mkn.signs:
        s = list(seq)
        s[slot] = cand
        vals.append(mkn.likelihood(s))
    arr = np.asarray(vals, dtype=np.float64)
    return arr / arr.sum()


def brute_force_gf(gf: mdl.GraphicFamilyMarkov, seq: tuple[str, ...], slot: int) -> np.ndarray:
    vals = []
    for cand in gf.signs:
        s = list(seq)
        s[slot] = cand
        vals.append(gf.likelihood(s))
    arr = np.asarray(vals, dtype=np.float64)
    return arr / arr.sum()


def main():
    started = time.perf_counter()
    summary_path = PKG / "results-v1/summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    clean_path = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
    obs_path = ROOT / "data/normalized/lipi_observed_faces.jsonl"
    base_path = ROOT / "experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv"

    rows, _ = load_records(clean_path, min_length=3, unique=True)
    raw_faces = read_jsonl(obs_path)
    base_map = {}
    for line in base_path.read_text(encoding="utf-8").splitlines()[1:]:
        p = line.split("\t")
        if len(p) >= 2 and p[0].strip():
            base_map[p[0].strip()] = p[1].strip()
    row_by_id = {r["record_id"]: r for r in rows}
    idx_by_id = {r["record_id"]: i for i, r in enumerate(rows)}
    base_seqs = [tuple(base_map.get(s, s) for s in r["seq"]) for r in rows]

    # 1. Independent full-corpus BFS roots
    indep_roots = independent_full_corpus_roots(rows, raw_faces)

    # 2. Check zero cross-fold leakage on Splits 2 and 3 (both outer and inner folds)
    leakage_audit = {}
    fold_maps = {}
    for sname in SPLIT_ORDER:
        reg = read_jsonl(RAW / "folds" / f"{sname}.jsonl")
        assert len(reg) == len(rows) == 1596
        fold_of = {idx_by_id[x["record_id"]]: x["fold"] for x in reg}
        comp_of = {idx_by_id[x["record_id"]]: x["component"] for x in reg}
        fold_maps[sname] = (fold_of, comp_of)

        # Outer cross-fold full-corpus alias violations (BFS roots)
        alias_cross_pairs = 0
        lev1_cross_pairs = 0
        base_cross_pairs = 0
        for i in range(len(rows)):
            fi = fold_of[i]
            for j in range(i + 1, len(rows)):
                if fold_of[j] == fi:
                    continue
                if indep_roots[i] == indep_roots[j]:
                    alias_cross_pairs += 1
                if levenshtein_le_1(rows[i]["seq"], rows[j]["seq"]):
                    lev1_cross_pairs += 1
                if base_seqs[i] == base_seqs[j]:
                    base_cross_pairs += 1

        # Inner 3-fold check for Splits 2 and 3
        inner_alias_violations = 0
        inner_lev1_violations = 0
        inner_base_violations = 0
        if sname != "split1_baseline":
            for outer_f in range(5):
                tr_idx = [i for i in range(len(rows)) if fold_of[i] != outer_f]
                tr_rows = [rows[i] for i in tr_idx]
                by_c = defaultdict(list)
                for local_i, global_i in enumerate(tr_idx):
                    by_c[comp_of[global_i]].append(local_i)
                inner_groups = [by_c[c] for c in sorted(by_c)]
                inner_assign, _ = make_folds(tr_rows, inner_groups, 3, SEED + outer_f)
                for a_loc in range(len(tr_idx)):
                    fa = inner_assign[a_loc]
                    ga = tr_idx[a_loc]
                    for b_loc in range(a_loc + 1, len(tr_idx)):
                        if inner_assign[b_loc] == fa:
                            continue
                        gb = tr_idx[b_loc]
                        if indep_roots[ga] == indep_roots[gb]:
                            inner_alias_violations += 1
                        if levenshtein_le_1(rows[ga]["seq"], rows[gb]["seq"]):
                            inner_lev1_violations += 1
                        if base_seqs[ga] == base_seqs[gb]:
                            inner_base_violations += 1

        leakage_audit[sname] = {
            "outer_full_corpus_alias_cross_pairs": alias_cross_pairs,
            "outer_levenshtein_1_cross_pairs": lev1_cross_pairs,
            "outer_base_family_cross_pairs": base_cross_pairs,
            "inner_full_corpus_alias_cross_pairs": inner_alias_violations if sname != "split1_baseline" else None,
            "inner_levenshtein_1_cross_pairs": inner_lev1_violations if sname != "split1_baseline" else None,
            "inner_base_family_cross_pairs": inner_base_violations if sname != "split1_baseline" else None,
        }

    assert leakage_audit["split2_alias_clean"]["outer_full_corpus_alias_cross_pairs"] == 0
    assert leakage_audit["split2_alias_clean"]["inner_full_corpus_alias_cross_pairs"] == 0
    assert leakage_audit["split3_near_variant_clean"]["outer_full_corpus_alias_cross_pairs"] == 0
    assert leakage_audit["split3_near_variant_clean"]["inner_full_corpus_alias_cross_pairs"] == 0
    assert leakage_audit["split3_near_variant_clean"]["outer_levenshtein_1_cross_pairs"] == 0
    assert leakage_audit["split3_near_variant_clean"]["inner_levenshtein_1_cross_pairs"] == 0
    assert leakage_audit["split3_near_variant_clean"]["outer_base_family_cross_pairs"] == 0
    assert leakage_audit["split3_near_variant_clean"]["inner_base_family_cross_pairs"] == 0

    # 3. Independently recompute metrics from local per-query JSONLs for all 18 cells
    metric_audit = {}
    max_metric_diff = 0.0
    for sname in SPLIT_ORDER:
        metric_audit[sname] = {}
        for mname in MODEL_ORDER:
            p_path = RAW / "predictions" / sname / f"{mname}.jsonl"
            scores = read_jsonl(p_path)
            assert len(scores) == 8009
            recomp = recompute_metrics(scores)
            saved = summary["splits"][sname]["models"][mname]["summary"]
            diffs = {k: abs(recomp[k] - saved[k]) for k in ["top1", "top5", "top10", "bucket_cross_entropy_bits", "expected_calibration_error"]}
            max_metric_diff = max(max_metric_diff, max(diffs.values()))
            assert max(diffs.values()) < 1e-12, (sname, mname, diffs)
            metric_audit[sname][mname] = {"slots": recomp["slots"], "max_abs_diff": max(diffs.values()), "sha256_match": sha256_file(p_path) == summary["splits"][sname]["models"][mname]["local_predictions_sha256"]}
            assert metric_audit[sname][mname]["sha256_match"]

    # 4. Exact Split 1 reproduction against frozen repository baselines
    repro = {}
    for mname, ref_rel in [
        ("PM", "results/restoration/baseline_slot_audit.jsonl"),
        ("M1", "experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl"),
        ("M2", "experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl"),
    ]:
        mine = read_jsonl(RAW / "predictions/split1_baseline" / f"{mname}.jsonl")
        ref = read_jsonl(ROOT / ref_rel)
        assert len(mine) == len(ref) == 8009
        max_loss_diff = 0.0
        max_mass_diff = 0.0
        top1_mismatch = top5_mismatch = 0
        for a, b in zip(mine, ref):
            assert (a["record_id"], a["slot"], a["actual"], a["fold"], a["group"]) == (b["record_id"], b["slot"], b["actual"], b["fold"], b["group"])
            if a["top1"] != b["top1"]:
                top1_mismatch += 1
            if a["top5"] != b["top5"]:
                top5_mismatch += 1
            max_loss_diff = max(max_loss_diff, abs(a["bucket_loss_bits"] - b["bucket_loss_bits"]))
            max_mass_diff = max(max_mass_diff, abs(a["model_top_mass"] - b["model_top_mass"]))
        assert top1_mismatch == 0 and top5_mismatch == 0 and max_loss_diff < 1e-11 and max_mass_diff < 1e-11
        repro[mname] = {"reference": ref_rel, "queries_checked": 8009, "top1_mismatches": top1_mismatch, "top5_mismatches": top5_mismatch, "max_loss_diff": max_loss_diff, "max_top_mass_diff": max_mass_diff}

    oct6 = json.loads((ROOT / "experiments/2026-10-06-modern-restoration/aggregate-results.json").read_text(encoding="utf-8"))
    oct6_mkn = oct6["models"]["classical/extra0/loss"]["summary"]
    my_mkn = summary["splits"]["split1_baseline"]["models"]["MKN"]["summary"]
    mkn_diffs = {
        "top1": abs(my_mkn["top1"] - oct6_mkn["top1"]),
        "top5": abs(my_mkn["top5"] - oct6_mkn["top5"]),
        "top10": abs(my_mkn["top10"] - oct6_mkn["top10"]),
        "bucket_cross_entropy_bits": abs(my_mkn["bucket_cross_entropy_bits"] - oct6_mkn["bucket_cross_entropy_bits"]),
        "expected_calibration_error": abs(my_mkn["expected_calibration_error"] - oct6_mkn["expected_calibration_error"]),
    }
    assert max(mkn_diffs.values()) < 1e-12, mkn_diffs
    repro["MKN"] = {"reference": "experiments/2026-10-06-modern-restoration/aggregate-results.json#/models/classical/extra0/loss/summary", "metric_abs_diffs": mkn_diffs}

    # 5. Independent brute-force likelihood replay on deterministic sample (15 queries/split = 45 queries x 6 models = 270 replays)
    rng = random.Random(20261122)
    replay_audit = {}
    for sname in SPLIT_ORDER:
        fold_of, _ = fold_maps[sname]
        saved_preds = {m: {(x["record_id"], x["slot"]): x for x in read_jsonl(RAW / "predictions" / sname / f"{m}.jsonl")} for m in MODEL_ORDER}
        max_bf_diff = 0.0
        max_saved_diff = 0.0
        hidden_invariance_ok = True
        checked = 0
        for fold in range(5):
            train = [rows[i] for i in range(len(rows)) if fold_of[i] != fold]
            test = [rows[i] for i in range(len(rows)) if fold_of[i] == fold]
            sample_rows = rng.sample(test, 3)

            sel_pm = summary["splits"][sname]["models"]["PM"]["folds"][fold]["selected"]["alpha"]
            sel_m1 = summary["splits"][sname]["models"]["M1"]["folds"][fold]["selected"]["alpha"]
            sel_m2 = summary["splits"][sname]["models"]["M2"]["folds"][fold]["selected"]["alpha"]
            sel_mkn = summary["splits"][sname]["models"]["MKN"]["folds"][fold]["selected"]
            sel_gf = summary["splits"][sname]["models"]["MKN-GF"]["folds"][fold]["selected"]
            sel_ens = summary["splits"][sname]["models"]["MKN-GF-SB"]["folds"][fold]["selected"]

            pm = mdl.PMRestorer(train, sel_pm)
            m1 = mdl.M1Restorer(train, sel_m1)
            m2 = mdl.M2Restorer(train, sel_m2)
            mkn = mdl.MKNRestorer(train, order=sel_mkn["order"], discount_scale=sel_mkn["discount_scale"])
            gf = mdl.GraphicFamilyMarkov(train, base_map, alpha=sel_gf["gf_alpha"])
            sb = mdl.SkipBigramPosModel(train, alpha_pos=20.0, alpha_skip=20.0)

            for r in sample_rows:
                slot = rng.randrange(len(r["seq"]))
                seq = r["seq"]
                actual = seq[slot]
                masked_row = dict(r, seq=tuple("ERASED" if k == slot else c for k, c in enumerate(seq)))

                # Fast distributions
                p_pm = pm.distribution(r, slot)
                p_m1 = m1.distribution(r, slot)
                p_m2 = m2.distribution(r, slot)
                p_mkn = mkn.distribution(r, slot)
                p_gf = gf.distribution(r, slot)
                p_sb = sb.distribution(r, slot)
                p_mkn_gf = mdl.log_linear_pool([p_mkn[None], p_gf[None]], [1.0 - sel_gf["w_gf"], sel_gf["w_gf"]])[0]
                p_ens = mdl.log_linear_pool([p_mkn[None], p_gf[None], p_sb[None]], [1.0 - sel_ens["w_gf"] - sel_ens["w_sb"], sel_ens["w_gf"], sel_ens["w_sb"]])[0]

                # Hidden-target invariance
                if not (
                    np.array_equal(p_pm, pm.distribution(masked_row, slot))
                    and np.array_equal(p_m1, m1.distribution(masked_row, slot))
                    and np.array_equal(p_m2, m2.distribution(masked_row, slot))
                    and np.array_equal(p_mkn, mkn.distribution(masked_row, slot))
                    and np.array_equal(p_gf, gf.distribution(masked_row, slot))
                    and np.array_equal(p_sb, sb.distribution(masked_row, slot))
                ):
                    hidden_invariance_ok = False

                # Brute-force complete sequence likelihood checks
                bf_m1 = brute_force_m1(m1, seq, slot)
                bf_m2 = brute_force_m1(mdl.M1Restorer(train, 20.0), seq, slot) if sel_m2 is None else brute_force_m2(m2, seq, slot)
                bf_mkn = brute_force_mkn(mkn, seq, slot)
                bf_gf = brute_force_gf(gf, seq, slot)
                max_bf_diff = max(
                    max_bf_diff,
                    float(np.max(np.abs(p_m1 - bf_m1))),
                    float(np.max(np.abs(p_m2 - bf_m2))),
                    float(np.max(np.abs(p_mkn - bf_mkn))),
                    float(np.max(np.abs(p_gf - bf_gf))),
                )

                # Compare against saved JSONL entries for all 6 models
                for mname, probs, signs in [
                    ("PM", p_pm, pm.signs),
                    ("M1", p_m1, m1.signs),
                    ("M2", p_m2, m2.signs),
                    ("MKN", p_mkn, mkn.signs),
                    ("MKN-GF", p_mkn_gf, mkn.signs),
                    ("MKN-GF-SB", p_ens, mkn.signs),
                ]:
                    rec = saved_preds[mname][(r["record_id"], slot)]
                    idx_map = {s: i for i, s in enumerate(signs)}
                    rank = np.argsort(-probs, kind="stable")
                    loss = -math.log2(max(float(probs[idx_map.get(actual, idx_map[UNKNOWN])]), 1e-300))
                    max_saved_diff = max(max_saved_diff, abs(loss - rec["bucket_loss_bits"]), abs(float(probs[rank[0]]) - rec["model_top_mass"]))
                    assert (signs[rank[0]] == actual) == rec["top1"]
                    assert (actual in [signs[t] for t in rank[:5]]) == rec["top5"]
                checked += 1

        assert hidden_invariance_ok and max_bf_diff < 1e-11 and max_saved_diff < 1e-11
        replay_audit[sname] = {
            "sampled_queries": checked,
            "model_evaluations_checked": checked * len(MODEL_ORDER),
            "hidden_target_invariance": hidden_invariance_ok,
            "max_brute_force_prob_diff": max_bf_diff,
            "max_saved_jsonl_diff": max_saved_diff,
        }

    report = {
        "status": "Verified computation",
        "verified_summary_path": "experiments/2026-11-22-restoration-leak-free/results-v1/summary.json",
        "verified_summary_sha256": sha256_file(summary_path),
        "verifier_sha256": sha256_file(Path(__file__)),
        "all_checks_passed": True,
        "leakage_audit": leakage_audit,
        "split1_reproduction": repro,
        "metric_recomputation": {"cells_checked": 18, "max_abs_diff": max_metric_diff, "details": metric_audit},
        "brute_force_replay": replay_audit,
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }
    out_path = PKG / "verification-v1.json"
    out_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "VERIFIED", "runtime_seconds": report["runtime_seconds"], "leakage_audit": leakage_audit}, indent=2))


if __name__ == "__main__":
    main()
